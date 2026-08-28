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


from exfor_tools import ExforEntry
from exfor_tools.reaction import Reaction

from . import errors, munge
from .overrides import OVERRIDES
from .spec import SECTORS, SpecRow

# The supplement quotes scattering energies inconsistently -- some to three decimals,
# some to one -- and EXFOR occasionally revises them, so rows are matched to
# measurements within a tolerance rather than exactly.
ENERGY_ABS_TOL_MEV = 0.05
ENERGY_REL_TOL = 0.01


#: Columns by which EXFOR resolves the residual excitation to a single level.
EXCITATION_LEVEL_LABELS = ("E-LVL", "E-EXC", "LVL-NUMB")

#: Columns by which it instead states only an upper bound on the excitation summed
#: over. EXFOR spells the bound several ways; all of them mean the same thing.
EXCITATION_BOUND_LABELS = ("E-LVL-MAX", "E-LVL-MX-A", "E-EXC-MAX", "E-EXC-MX-A")

#: EXFOR energy units, to MeV.
_TO_MEV = {"EV": 1e-6, "KEV": 1e-3, "MEV": 1.0}


def summed_excitation_bound(data_set) -> float | None:
    """The excitation in MeV a data set sums up to, when it only bounds it.

    ``None`` when the data set resolves the residual's level, which is the case the
    excitation filter can act on. Otherwise EXFOR states only an upper bound, and the
    measurement is the ground state summed together with every level below that bound
    -- the low-lying states the experiment could not separate.
    """
    labels, units = list(data_set.labels), list(data_set.units)
    if any(label in EXCITATION_LEVEL_LABELS for label in labels):
        return None

    bounds = []
    for index, label in enumerate(labels):
        if label not in EXCITATION_BOUND_LABELS:
            continue
        scale = _TO_MEV.get(units[index].upper())
        if scale is None:
            continue
        values = [row[index] for row in data_set.data if row[index] is not None]
        if values:
            bounds.append(max(values) * scale)

    return max(bounds) if bounds else None


def summed_scattering_bound(entry: str, subentry: str, pointer: str = "") -> float | None:
    """The excitation bound of a subentry that is summed scattering, else ``None``.

    EXFOR's SCT is "Total scattering (elastic + inelastic)". A data set written that
    way satisfies an elastic query only because it says which excitation it covers; when
    all it says is an upper bound, what reaches the corpus is quasi-elastic rather than
    elastic. The published corpora count these as elastic -- twelve of their twenty-two
    SCT subentries are of this kind, with bounds from 30 keV up to 800 keV -- so they
    are kept, and flagged with the bound so a consumer can judge for itself.
    """
    try:
        blocks = errors.data_sets_for(entry, subentry, pointer)
    except errors.EntryUnavailable:
        return None

    bounds = [
        bound
        for data_set in blocks.values()
        if getattr(data_set.reaction[0], "products", None) == ["SCT"]
        for bound in [summed_excitation_bound(data_set)]
        if bound is not None
    ]
    return max(bounds) if bounds else None


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
    substituted: bool = False


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
    #: rows whose target EXFOR now assigns differently from the supplement's table
    reassigned_targets: dict = field(default_factory=dict)

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
    def substitutions(self) -> list[RowOutcome]:
        """Rows satisfied by a renumbered subentry rather than the one tabulated."""
        return [o for o in self.outcomes if o.substituted]

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
    allow_substitution: bool = True,
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
    reassigned: dict[tuple, tuple[int, int]] = {}
    for row in rows:
        if not row.in_exfor:
            data.outcomes.append(RowOutcome(
                row, False, "the supplement marks this row as absent from EXFOR"))
            continue
        # Group by the target EXFOR currently assigns, not the one tabulated: the two
        # disagree for a few dozen data sets, and the target is what the reaction match
        # is made against.
        target = errors.subentry_target(row.entry, row.subentry, row.pointer) or row.target
        if target != row.target:
            reassigned[row.key] = target
        by_group[(target, row.entry)].append(row)
    data.reassigned_targets = reassigned

    for (target, entry), group in sorted(by_group.items(), key=lambda kv: kv[0][1]):
        _retrieve_group(data, target, entry, group, vocal=vocal, min_num_pts=min_num_pts,
                        allow_substitution=allow_substitution)

    return data


def _retrieve_group(
    data: SectorData,
    target: tuple[int, int],
    entry: str,
    group: list[SpecRow],
    *,
    vocal: bool,
    min_num_pts: int,
    allow_substitution: bool = True,
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
        if assignment.rule == "missing":
            # The tabulated subentry is gone but the entry is not; resolve from the
            # entry's prevailing column layout so retrieval can still run, and let
            # substitution below find the renumbered data set.
            assignment = errors.resolve_entry(row.entry)
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

        _match_rows(data, retrieved, plan_rows, target,
                    allow_substitution=allow_substitution)


def _match_rows(data: SectorData, retrieved: list[ExforEntry], rows: list[SpecRow],
                target: tuple[int, int], *, allow_substitution: bool = True) -> None:
    """Assign each row the measurement it asked for, preferring earlier quantities."""
    # (preference rank, ExforEntry, measurement) for every measurement of the entry.
    # Deliberately not restricted to the tabulated subentries: substitution below needs
    # to see the entry's other subentries when a tabulated one has been renumbered.
    available = [
        (rank, exfor_entry, m)
        for rank, exfor_entry in enumerate(retrieved)
        for m in exfor_entry.measurements
    ]
    integral = data.quantities == ("XS",)
    claimed: set[int] = set()

    for row in rows:
        candidates = [
            (i, rank, exfor_entry, m) for i, (rank, exfor_entry, m) in enumerate(available)
            if m.subentry == row.subentry and i not in claimed
            and (integral or energy_matches(row.energy_mev, float(m.Einc)))
        ]
        if not candidates and allow_substitution and not integral:
            candidates = _substitution_candidates(available, row, claimed)
            if candidates:
                data.outcomes.append(_record(
                    data, retrieved, row, candidates, claimed, integral, target,
                    substituted=True))
                continue

        if not candidates:
            data.outcomes.append(RowOutcome(row, False, _why_not(retrieved, row)))
            continue

        data.outcomes.append(
            _record(data, retrieved, row, candidates, claimed, integral, target))


def _substitution_candidates(available, row, claimed):
    """Measurements in the same entry that match the row's energy, at any subentry.

    EXFOR renumbers subentries between releases -- O0208 has since moved its analyzing
    powers from subentries 006-009 to 010-014, and O0091 likewise -- so the subentry the
    supplement tabulates may no longer exist while the data still do. Substitution is
    confined to the same entry, which is the same publication and measurement campaign,
    is only attempted when the tabulated subentry is genuinely absent, and requires an
    unambiguous energy match. Every substitution is reported.
    """
    matches = [
        (i, rank, exfor_entry, m) for i, (rank, exfor_entry, m) in enumerate(available)
        if i not in claimed and energy_matches(row.energy_mev, float(m.Einc))
    ]
    # ambiguous matches are not substituted
    if len({m.subentry for _, _, _, m in matches}) != 1:
        return []
    return matches


def _record(data, retrieved, row, candidates, claimed, integral, target,
            substituted=False):
    """Claim the best candidate for a row and record the outcome."""
    # Prefer the earlier quantity, then the closest energy when a subentry reports
    # several within tolerance.
    candidates.sort(key=lambda c: (
        c[1], 0.0 if integral else abs(float(c[3].Einc) - row.energy_mev)))
    index, _, exfor_entry, measurement = candidates[0]
    claimed.add(index)

    data.entries.setdefault(exfor_entry.entry, exfor_entry)
    data.measurements[exfor_entry.entry].append(measurement)
    measurement.spec_row = row
    measurement.target = target
    bound = summed_scattering_bound(exfor_entry.entry, measurement.subentry, row.pointer)
    if bound is not None:
        from .munge import note
        measurement.summed_excitation_max_mev = bound
        note(measurement,
             f"EXFOR records this as scattering (SCT) summed over excitations up to "
             f"{bound * 1e3:.0f} keV rather than as resolved elastic scattering; the "
             f"supplement counts it as elastic, and it is kept on that basis")
    if target != row.target:
        from .munge import note
        note(measurement,
             f"the supplement tabulates this data set under {row.target_label}; EXFOR "
             f"now assigns it to A={target[0] or 'nat'}, Z={target[1]}, which is used here")
    if substituted:
        from .munge import note
        note(measurement,
             f"the supplement tabulates subentry {row.subentry} for this data set, which "
             f"is no longer in EXFOR; taken from {measurement.subentry} in the same entry "
             "at the same scattering energy")
    return RowOutcome(
        row, True,
        reason=(f"substituted {measurement.subentry} for the tabulated {row.subentry}"
                if substituted else ""),
        subentry=measurement.subentry,
        energy=float(getattr(measurement, "Einc", row.energy_mev)),
        n_points=measurement.rows,
        substituted=substituted,
    )


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
