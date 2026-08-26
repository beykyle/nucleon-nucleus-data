"""End-to-end curation of one corpus-sector: retrieve, correct, munge, serialize.

The notebooks drive this module. Each does the same thing -- load a sector's spec,
retrieve it, report coverage, plot for inspection, write JSON -- with the sector's own
judgement calls kept visible in the notebook rather than hidden here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import munge, report, retrieve, serialize
from .spec import SECTORS, load_sector

#: Sectors whose data are stored as a ratio to Rutherford, whatever EXFOR reports.
RATIO_SECTORS = {"proton_elastic"}

#: Sectors tabulated over an energy range, which are trimmed and thinned.
INTEGRAL_SECTORS = {"neutron_total", "proton_reaction"}

#: The supplement downsamples neutron total cross sections to one datum per MeV.
NEUTRON_TOTAL_POINTS_PER_MEV = 1.0

@dataclass
class SectorResult:
    """A curated corpus-sector."""

    data: retrieve.SectorData
    records: list[serialize.Record] = field(default_factory=list)
    dropped: list[tuple[str, str]] = field(default_factory=list)
    applied_overrides: list[str] = field(default_factory=list)

    @property
    def corpus(self) -> str:
        return self.data.corpus

    @property
    def sector(self) -> str:
        return self.data.sector

    @property
    def n_points(self) -> int:
        return sum(len(r.payload["data"]["x"]) for r in self.records)

    def summary(self) -> str:
        lines = [report.summarize(self.data)]
        lines.append(f"  serialized             {len(self.records)} measurements, "
                     f"{self.n_points} points")
        if self.applied_overrides:
            lines.append("  overrides applied")
            lines.extend(f"    {a}" for a in self.applied_overrides)
        if self.dropped:
            lines.append("  dropped during munging")
            lines.extend(f"    {sub}: {why}" for sub, why in self.dropped)
        return "\n".join(lines)


def curate(
    corpus: str,
    sector: str,
    *,
    vocal: bool = False,
    min_num_pts: int = 1,
    min_points_per_distribution: int = 3,
    default_norm_err: float = munge.DEFAULT_SYSTEMATIC_NORM_ERR,
) -> SectorResult:
    """Retrieve and clean one corpus-sector. Does not write anything to disk."""
    data = retrieve.build_sector(load_sector(corpus, sector), vocal=vocal,
                                 min_num_pts=min_num_pts)
    result = SectorResult(data=data)
    result.applied_overrides = retrieve.apply_overrides(data)

    for entry_id, measurements in data.measurements.items():
        exfor_entry = data.entries[entry_id]
        citation = exfor_entry.meta.citation() if exfor_entry.meta is not None else ""
        keep = []
        for measurement in measurements:
            why = _munge_one(measurement, sector, default_norm_err,
                             min_points_per_distribution)
            if why is not None:
                result.dropped.append((measurement.subentry, why))
                continue
            keep.append(measurement)
            result.records.append(serialize.to_record(
                measurement,
                corpus=corpus, sector=sector,
                projectile=measurement.spec_row.projectile,
                target=measurement.spec_row.target,
                citation=citation,
            ))
        data.measurements[entry_id] = keep

    return result


def _munge_one(measurement, sector: str, default_norm_err: float,
               min_points: int = 3) -> str | None:
    """Clean one measurement in place. Returns a reason if it must be dropped."""
    row = measurement.spec_row

    if sector in INTEGRAL_SECTORS:
        lo = row.energy_mev
        hi = row.energy_hi_mev if row.energy_hi_mev is not None else row.energy_mev
        # A single tabulated energy still needs a window, since EXFOR energies and the
        # supplement's rounding rarely agree exactly.
        if hi <= lo:
            lo, hi = lo - retrieve.ENERGY_ABS_TOL_MEV, hi + retrieve.ENERGY_ABS_TOL_MEV
        if not munge.restrict_to_energy_window(measurement, lo, hi):
            return f"no data in the tabulated energy range {lo}-{hi} MeV"
        if sector == "neutron_total":
            munge.downsample_energy(measurement, NEUTRON_TOTAL_POINTS_PER_MEV)
    else:
        if munge.is_too_sparse(measurement, min_points):
            return (f"only {measurement.rows} scattering angle(s); too sparse to "
                    "constrain an optical potential")
        munge.to_cm_degrees(measurement, row.target, row.projectile_AZ)
        if sector in RATIO_SECTORS:
            munge.to_ratio_to_rutherford(measurement, row.target, row.projectile_AZ)
            if measurement.rows == 0:
                return "no points remain above the minimum ratio angle"

    if munge.is_polarization_cross_section(measurement):
        return ("reported as a polarization cross section in "
                f"{measurement.y_units}, not a dimensionless analyzing power")

    munge.homogenize_units(measurement)

    if not munge.has_usable_uncertainties(measurement):
        # The supplement removes any data set missing a "necessary feature", listing
        # the cross section error among them.
        return "one or more data points carry no uncertainty"

    if sector.endswith("_ay"):
        why = munge.check_analyzing_power(measurement)
        if why is not None:
            return why

    munge.apply_default_norm_err(measurement, default_norm_err)
    return None


def write(result: SectorResult, *, check: bool = True) -> None:
    """Validate coverage and write a curated sector to ``data/``."""
    if check:
        report.check_coverage(result.data)

    bibtex = {
        entry_id: exfor_entry.bibtex()
        for entry_id, exfor_entry in result.data.entries.items()
        if result.data.measurements.get(entry_id)
    }
    serialize.write_sector(
        result.records, corpus=result.corpus, sector=result.sector, bibtex=bibtex,
    )


def write_manifest(results: list[SectorResult]) -> None:
    """Write one corpus's manifest from its curated sectors."""
    corpus = results[0].corpus
    serialize.write_manifest(
        corpus,
        {r.sector: serialize.sector_summary(r.data, r.records) for r in results},
        provenance=serialize.provenance(),
    )


def all_sectors(corpus: str) -> list[str]:
    from .spec import available_sectors
    return [s for c, s in available_sectors() if c == corpus]


__all__ = ["SectorResult", "curate", "write", "write_manifest", "all_sectors", "SECTORS"]
