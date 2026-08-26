"""Turn corpus specifications into parsed EXFOR measurements.

The supplement's tables name a subentry *and* a scattering energy per row, while
``exfor_tools`` retrieves a whole entry at a time and unrolls it into one measurement
per energy. Retrieval here therefore proceeds entry by entry and then matches
measurements back to the rows that asked for them, so that every row is accounted for:
either it produced data or it appears in the coverage report with a reason.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from exfor_tools import ExforEntry
from exfor_tools.reaction import Reaction

from . import errors, munge
from .overrides import OVERRIDES, Override
from .spec import SECTORS, SpecRow

# The supplement quotes scattering energies inconsistently -- some to three decimals,
# some to one -- and EXFOR occasionally revises them, so rows are matched to
# measurements within a tolerance rather than exactly.
ENERGY_ABS_TOL_MEV = 0.05
ENERGY_REL_TOL = 0.01


def energy_matches(spec_energy: float, measured: float) -> bool:
    tol = max(ENERGY_ABS_TOL_MEV, ENERGY_REL_TOL * spec_energy)
    return abs(spec_energy - measured) <= tol


@dataclass
class RowOutcome:
    """What became of one row of a supplement corpus table."""

    row: SpecRow
    resolved: bool
    reason: str = ""
    subentry: str = ""
    energy: float | None = None
    n_points: int = 0


@dataclass
class SectorData:
    """Everything retrieved for one corpus-sector."""

    corpus: str
    sector: str
    quantities: tuple[str, ...]
    process: str
    measurements: dict[str, list] = field(default_factory=lambda: defaultdict(list))
    entries: dict[str, ExforEntry] = field(default_factory=dict)
    outcomes: list[RowOutcome] = field(default_factory=list)

    @property
    def n_measurements(self) -> int:
        return sum(len(v) for v in self.measurements.values())

    @property
    def n_points(self) -> int:
        return sum(m.rows for ms in self.measurements.values() for m in ms)

    @property
    def unresolved(self) -> list[RowOutcome]:
        return [o for o in self.outcomes if not o.resolved]

    @property
    def coverage(self) -> float:
        rows = [o for o in self.outcomes if o.row.in_exfor]
        if not rows:
            return 1.0
        return sum(o.resolved for o in rows) / len(rows)

    def all_measurements(self) -> list:
        return [m for ms in self.measurements.values() for m in ms]


def build_sector(
    rows: list[SpecRow],
    *,
    vocal: bool = False,
    min_num_pts: int = 1,
) -> SectorData:
    """Retrieve every data set a corpus-sector's table asks for.

    Rows are grouped by (target, entry); each group becomes one or more ``ExforEntry``
    queries, split when its subentries need different uncertainty columns. Measurements
    are then matched back to rows by subentry and energy.
    """
    corpus, sector = rows[0].corpus, rows[0].sector
    quantities, process = SECTORS[sector]
    data = SectorData(corpus=corpus, sector=sector, quantities=quantities, process=process)

    by_group: dict[tuple[tuple[int, int], str], list[SpecRow]] = defaultdict(list)
    for row in rows:
        if row.in_exfor:
            by_group[(row.target, row.entry)].append(row)
        else:
            data.outcomes.append(RowOutcome(
                row, False, "the supplement marks this row as absent from EXFOR"))

    for (target, entry), group in sorted(by_group.items(), key=lambda kv: kv[0][1]):
        _retrieve_group(data, target, entry, group, vocal=vocal, min_num_pts=min_num_pts)

    return data


def _retrieve_group(
    data: SectorData,
    target: tuple[int, int],
    entry: str,
    group: list[SpecRow],
    *,
    vocal: bool,
    min_num_pts: int,
) -> None:
    projectile = group[0].projectile_AZ
    reaction = Reaction(target=target, projectile=projectile, process=data.process)

    # Subentries of one entry can need different uncertainty columns, and ExforEntry
    # applies one set to the whole entry, so group the wanted subentries by the parsing
    # keywords they resolve to and issue one query per distinct set.
    plans: dict[tuple, list[SpecRow]] = defaultdict(list)
    unresolvable: list[tuple[SpecRow, str]] = []
    for row in group:
        override = OVERRIDES.get((data.corpus, data.sector, row.subentry)) or \
                   OVERRIDES.get((data.corpus, data.sector, row.entry))
        if override is not None and override.drop:
            unresolvable.append((row, f"excluded by override: {override.reason}"))
            continue
        if override is not None and override.parsing_kwargs is not None:
            plans[_freeze(override.parsing_kwargs)].append(row)
            continue

        assignment = errors.resolve_subentry(row.entry, row.subentry, row.pointer)
        if not assignment.resolved:
            unresolvable.append((row, f"uncertainty unresolved ({assignment.rule}): "
                                      f"{assignment.reason}"))
            continue
        plans[_freeze(assignment.parsing_kwargs)].append(row)

    for row, reason in unresolvable:
        data.outcomes.append(RowOutcome(row, False, reason))

    for frozen, plan_rows in plans.items():
        parsing_kwargs = _thaw(frozen)
        # Retrieve every quantity this sector accepts, in preference order, so that a
        # row can be satisfied by whichever form EXFOR happens to report.
        retrieved, failures = [], []
        for quantity in data.quantities:
            try:
                retrieved.append(ExforEntry(
                    entry=entry,
                    reaction=reaction,
                    quantity=quantity,
                    elastic_only=(data.process == "el"),
                    parsing_kwargs=parsing_kwargs,
                    # Lab-frame angles are accepted and converted to the CM frame
                    # during munging, rather than discarded.
                    filter_kwargs={
                        "min_num_pts": min_num_pts,
                        "allow_cos": True,
                        "filter_lab_angle": False,
                    },
                    vocal=vocal,
                ))
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                failures.append(f"{quantity}: {type(exc).__name__}: {exc}")

        if not retrieved:
            for row in plan_rows:
                data.outcomes.append(RowOutcome(
                    row, False, "retrieval failed: " + "; ".join(failures)))
            continue

        _match_rows(data, retrieved, plan_rows)


def _match_rows(data: SectorData, retrieved: list[ExforEntry], rows: list[SpecRow]) -> None:
    """Assign each row the measurement it asked for, preferring earlier quantities."""
    wanted = {row.subentry for row in rows}
    # (preference rank, ExforEntry, measurement) for every candidate measurement
    available = [
        (rank, exfor_entry, m)
        for rank, exfor_entry in enumerate(retrieved)
        for m in exfor_entry.measurements
        if m.subentry in wanted
    ]
    integral = data.quantities == ("XS",)
    claimed: set[int] = set()

    for row in rows:
        candidates = [
            (i, rank, exfor_entry, m) for i, (rank, exfor_entry, m) in enumerate(available)
            if m.subentry == row.subentry and i not in claimed
            and (integral or energy_matches(row.energy_mev, float(m.Einc)))
        ]
        if not candidates:
            data.outcomes.append(RowOutcome(row, False, _why_not(retrieved, row)))
            continue

        # Prefer the earlier quantity, then the closest energy when a subentry reports
        # several within tolerance.
        candidates.sort(key=lambda c: (
            c[1], 0.0 if integral else abs(float(c[3].Einc) - row.energy_mev)))
        index, _, exfor_entry, measurement = candidates[0]
        claimed.add(index)

        data.entries.setdefault(exfor_entry.entry, exfor_entry)
        data.measurements[exfor_entry.entry].append(measurement)
        measurement.spec_row = row
        data.outcomes.append(RowOutcome(
            row, True, subentry=measurement.subentry,
            energy=float(getattr(measurement, "Einc", row.energy_mev)),
            n_points=measurement.rows,
        ))


def _why_not(retrieved: list[ExforEntry], row: SpecRow) -> str:
    entry = retrieved[0].entry
    failed = {}
    for exfor_entry in retrieved:
        failed.update(getattr(exfor_entry, "failed_parses_by_subentry", {}))
    if row.subentry in failed:
        return f"parse failed: {failed[row.subentry]}"

    energies = sorted(
        float(m.Einc) for exfor_entry in retrieved for m in exfor_entry.measurements
        if m.subentry == row.subentry and hasattr(m, "Einc")
    )
    if not energies:
        if failed:
            return (f"subentry not parsed from entry {entry} "
                    f"(failed subentries: {', '.join(sorted(failed))})")
        return f"subentry not present in entry {entry} for this quantity"
    return (f"no measurement within tolerance of {row.energy_mev} MeV; "
            f"subentry reports {energies}")


def _freeze(kwargs: dict) -> tuple:
    return tuple(sorted(
        (k, tuple(v) if isinstance(v, list) else v) for k, v in kwargs.items()
    ))


def _thaw(frozen: tuple) -> dict:
    return {k: list(v) if isinstance(v, tuple) else v for k, v in frozen}


def apply_overrides(data: SectorData) -> list[str]:
    """Apply the supplement's documented corrections to retrieved measurements."""
    applied = []
    for measurement in data.all_measurements():
        for key in ((data.corpus, data.sector, measurement.subentry),
                    (data.corpus, data.sector, measurement.subentry[:5])):
            override = OVERRIDES.get(key)
            if override is None or override.scale_by is None:
                continue
            munge.scale(measurement, override.scale_by, override.reason)
            applied.append(f"{measurement.subentry}: scaled by {override.scale_by:g}")
            break
    return applied
