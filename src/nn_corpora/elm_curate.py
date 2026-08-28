"""Curation of the ELM corpus.

The ELM corpus is a query rather than a table: every EXFOR data set for elastic
nucleon scattering, or (p,n) to the isobaric analog state, on a set of near-spherical
targets within an energy window. The decisions that turn that query into a corpus are
in :mod:`nn_corpora.elm`; this module applies them.

Output follows the same conventions as the other corpora, which means one departure
from the ELM notebooks: proton elastic data are stored as a ratio to Rutherford
throughout, so data sets EXFOR reports as absolute cross sections are divided by the
Rutherford cross section rather than kept in b/sr.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from exfor_tools import curate as exfor_curate
from exfor_tools.reaction import Reaction

from . import elm, munge, retrieve, serialize, spec
from .kinematics import lab_to_cm_angle_elastic

#: ELM sector -> (quantities, process, output directory name).
ELM_SECTORS = {
    "elastic_diff_xs": (("dXS/dA", "dXS/dRuth"), "el"),
    "elastic_ay": (("Ay",), "el"),
    "charge_exchange": (("dXS/dA",), "pn"),
}


@dataclass
class ElmSectorResult:
    sector: str
    data: dict = field(default_factory=dict)
    records: list[serialize.Record] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)
    repaired: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    #: EXFOR entry -> BibTeX entry, for the sector's bibliography
    bibtex: dict = field(default_factory=dict)

    @property
    def n_points(self) -> int:
        return sum(len(r.payload["data"]["x"]) for r in self.records)

    def summary(self) -> str:
        lines = [
            f"elm/{self.sector}",
            f"  targets                {len(self.data)}",
            f"  measurements           {len(self.records)}",
            f"  data points            {self.n_points}",
        ]
        for label, items in (("excluded", self.excluded), ("repaired", self.repaired),
                             ("dropped", self.dropped)):
            if items:
                lines.append(f"  {label}")
                lines.extend(f"    {i}" for i in items)
        return "\n".join(lines)


def query_elastic(projectile: tuple[int, int], quantities: tuple[str, ...],
                  targets, einc_range, min_num_pts: int, vocal: bool = False) -> dict:
    """Query EXFOR for elastic scattering on every ELM target."""
    settings = {
        "Einc_range": list(einc_range),
        # EXFOR writes some elastic data as scattering (SCT) against an excitation
        # column, so the elastic channel must be selected by excitation energy, not by
        # the reaction code alone. Where that column only bounds the excitation there is
        # nothing for the filter to select on; those data sets are kept, and flagged
        # with their bound by _flag_summed_scattering.
        "elastic_only": True,
        "filter_kwargs": {"min_num_pts": min_num_pts, "allow_cos": True,
                          "filter_lab_angle": False},
    }
    return {
        target: exfor_curate.MultiQuantityReactionData(
            Reaction(target=target, projectile=projectile, process="el"),
            quantities=list(quantities), settings=settings, vocal=vocal,
        )
        for target in targets
    }


def query_pn(targets, einc_range, ias_window: float, vocal: bool = False) -> dict:
    """Query EXFOR for (p,n) scattering to the isobaric analog state.

    The analog state is selected by a window on the residual excitation energy rather
    than by ``elastic_only``. Entries that report the excitation energy some other way
    -- via a Q value, a level number, an analog-state number -- fall outside the window
    and are re-added by hand in the notebook.
    """
    data = {}
    for (A, Z) in targets:
        ex = spec.ELM_EX_IAS[(A, Z)]
        settings = {
            "Einc_range": list(einc_range),
            "Ex_range": [ex - ias_window, ex + ias_window],
            # analog-state angular distributions are sparse, so no minimum point count
            "filter_kwargs": {"min_num_pts": 1, "allow_cos": True,
                              "filter_lab_angle": False},
        }
        data[(A, Z)] = exfor_curate.MultiQuantityReactionData(
            Reaction(target=(A, Z), projectile=(1, 1), product=(1, 0), residual=(A, Z + 1)),
            quantities=["dXS/dA"], settings=settings, vocal=vocal,
        )
    return data


def readd_entry(data: dict, target: tuple[int, int], entry_id: str, result: ElmSectorResult,
                *, einc_range, ex_range=None, parsing_kwargs=None, reason: str = "") -> None:
    """Re-add an entry the excitation-energy window rejected, on explicit grounds.

    Some entries report the analog state differently from modern compilations, or do not
    report an excitation energy at all, and so fall outside the window even though the
    data are the analog-state transition.
    """
    from exfor_tools import ExforEntry

    A, Z = target
    reaction = Reaction(target=target, projectile=(1, 1), product=(1, 0), residual=(A, Z + 1))
    kwargs = {"Einc_range": list(einc_range)}
    if ex_range is not None:
        kwargs["Ex_range"] = list(ex_range)
    entry = ExforEntry(
        entry=entry_id, reaction=reaction, quantity="dXS/dA",
        parsing_kwargs=parsing_kwargs or {},
        filter_kwargs={"min_num_pts": 1, "allow_cos": True, "filter_lab_angle": False},
        **kwargs,
    )
    if not entry.measurements:
        result.dropped.append(f"{entry_id}: re-add produced no measurements")
        return
    data[target].data["dXS/dA"].entries[entry_id] = entry
    result.repaired.append(f"{entry_id} re-added for {A}/{Z}: {reason}")


def repair_failed_parses(data: dict, quantities: tuple[str, ...], result: ElmSectorResult) -> None:
    """Re-parse entries that failed, naming the uncertainty columns explicitly.

    The recipes come from reading each entry's EXFOR ERR-ANALYS text, as recorded in
    the ELM notebooks.
    """
    for target, multi in data.items():
        for quantity in quantities:
            entries = multi.data[quantity]
            for entry_id in list(entries.failed_parses):
                recipe = elm.PARSE_RECIPES.get(entry_id)
                if recipe is None:
                    continue
                entries.reattempt_parse(entry_id, recipe.parsing_kwargs)
                if entry_id in entries.entries:
                    result.repaired.append(f"{quantity} {entry_id} via {recipe.statistical}")


def exclude_entries(data: dict, quantity: str, exclusions: dict[str, str],
                    result: ElmSectorResult) -> None:
    """Remove entries the ELM notebooks reject, recording the reason."""
    for target, multi in data.items():
        entries = multi.data[quantity]
        for entry_id, reason in exclusions.items():
            for store in (entries.entries, entries.failed_parses):
                if entry_id in store:
                    del store[entry_id]
                    result.excluded.append(f"{quantity} {entry_id}: {reason}")


def apply_point_fixes(data: dict, result: ElmSectorResult) -> None:
    """Correct individual points that the ELM notebooks identify as mistranscribed."""
    for fix in elm.POINT_FIXES:
        multi = data.get(fix.target)
        if multi is None or fix.quantity not in multi.data:
            continue
        entry = multi.data[fix.quantity].entries.get(fix.entry)
        if entry is None or len(entry.measurements) <= fix.measurement_index:
            continue
        measurement = entry.measurements[fix.measurement_index]
        measurement.y[fix.point_index] *= fix.factor
        if fix.scale_uncertainty:
            measurement.statistical_err[fix.point_index] *= fix.factor
        munge.note(measurement, fix.note)
        result.repaired.append(f"{fix.entry} {fix.note}")


def apply_uncertainty_patches(data: dict, result: ElmSectorResult) -> None:
    """Supply uncertainties EXFOR omits, from the original publications."""
    for patch in elm.UNCERTAINTY_PATCHES:
        for multi in data.values():
            if patch.quantity not in multi.data:
                continue
            entry = multi.data[patch.quantity].entries.get(patch.entry)
            if entry is None:
                continue
            # index within the patched subentry, not within the entry: one entry can
            # carry several targets, and the patch belongs to exactly one of them
            matching = [m for m in entry.measurements if m.subentry == patch.subentry]
            if len(matching) <= patch.measurement_index:
                continue
            measurement = matching[patch.measurement_index]
            if patch.point_index is None:
                mask = measurement.statistical_err <= 0
                if not np.any(mask):
                    continue
                measurement.statistical_err[mask] = patch.value
            else:
                measurement.statistical_err[patch.point_index] = patch.value
            munge.note(measurement, patch.note)
            result.repaired.append(f"{patch.subentry}: {patch.note}")


def apply_uncertainty_transplant(data: dict, result: ElmSectorResult) -> None:
    """144Sm: take the normalization from one 65 MeV data set and the errors from the other."""
    spec_ = elm.UNCERTAINTY_TRANSPLANT
    multi = data.get(spec_["target"])
    if multi is None or spec_["quantity"] not in multi.data:
        return
    entries = multi.data[spec_["quantity"]].entries
    into, source = entries.get(spec_["into"]), entries.get(spec_["from"])
    if into is None or source is None:
        return
    into.measurements[0].statistical_err = source.measurements[0].statistical_err.copy()
    munge.note(into.measurements[0], spec_["note"])
    del entries[spec_["from"]]
    result.repaired.append(f"{spec_['into']} uncertainties taken from {spec_['from']}")


def finalize(data: dict, sector: str, projectile: str, result: ElmSectorResult,
             default_norm_err: float = munge.DEFAULT_SYSTEMATIC_NORM_ERR,
             min_points: int = spec.ELM_MIN_NUM_PTS) -> None:
    """Munge and serialize every measurement of one ELM sector."""
    for target, multi in data.items():
        for quantity, entries in multi.data.items():
            for entry_id, entry in entries.entries.items():
                citation = entry.meta.citation() if entry.meta is not None else ""
                if entry_id not in result.bibtex:
                    try:
                        result.bibtex[entry_id] = entry.bibtex()
                    except Exception:  # noqa: BLE001 - a missing citation is not fatal
                        result.bibtex[entry_id] = None
                for measurement in list(entry.measurements):
                    why = _munge_one(measurement, sector, target, projectile, quantity,
                                     default_norm_err, min_points)
                    if why is not None:
                        result.dropped.append(f"{measurement.subentry}: {why}")
                        entry.measurements.remove(measurement)
                        continue
                    # ELM queries EXFOR directly rather than row by row, so the
                    # quasi-elastic flag is applied here rather than in retrieve.
                    _flag_summed_scattering(measurement, entry_id)
                    result.records.append(serialize.to_record(
                        measurement, corpus="elm", sector=sector,
                        projectile=projectile, target=target, citation=citation,
                    ))


def _flag_summed_scattering(measurement, entry_id: str) -> None:
    """Record the excitation bound of a measurement that is summed scattering."""
    bound = retrieve.summed_scattering_bound(entry_id, measurement.subentry)
    if bound is None:
        return
    measurement.summed_excitation_max_mev = bound
    munge.note(measurement,
               f"EXFOR records this as scattering (SCT) summed over excitations up to "
               f"{bound * 1e3:.0f} keV rather than as resolved elastic scattering; the "
               f"corpus counts it as elastic, and it is kept on that basis")


def _munge_one(measurement, sector, target, projectile_name, quantity,
               default_norm_err, min_points) -> str | None:
    if munge.is_too_sparse(measurement, min_points):
        return (f"only {measurement.rows} scattering angle(s); too sparse to constrain "
                "an optical potential")

    projectile = spec.PROJECTILES[projectile_name]
    munge.to_cm_degrees(measurement, target, projectile)

    # ELM stores charged-projectile elastic data as a ratio to Rutherford, matching the
    # other corpora in this repo; the ELM notebooks keep absolute cross sections where
    # EXFOR reports them that way.
    if sector == "elastic_diff_xs" and projectile[1] > 0:
        munge.to_ratio_to_rutherford(measurement, target, projectile)
        if measurement.rows == 0:
            return "no points remain above the minimum ratio angle"

    if munge.is_polarization_cross_section(measurement):
        return ("reported as a polarization cross section in "
                f"{measurement.y_units}, not a dimensionless analyzing power")

    munge.homogenize_units(measurement)

    if measurement.quantity == "Ay":
        why = munge.check_analyzing_power(measurement)
        if why is not None:
            return why

    floor = elm.MIN_STAT_ERR.get(measurement.quantity, 0.0)
    if measurement.rows == 0 or np.any(measurement.statistical_err < floor):
        return f"one or more uncertainties below the {measurement.quantity} floor {floor:g}"

    munge.apply_default_norm_err(measurement, default_norm_err)
    return None


def convert_lab_angles(entry, target: tuple[int, int], projectile: tuple[int, int]) -> None:
    """Convert an entry's lab-frame angles to the CM frame.

    Kept for entries curated by hand in the notebooks; :func:`finalize` does the same
    for everything else.
    """
    for measurement in entry.measurements:
        if measurement.x_units == "LAB-degrees":
            measurement.x = lab_to_cm_angle_elastic(measurement.x, target, projectile)
            measurement.x_units = "CM-degrees"
            munge.note(measurement, "converted scattering angles from the lab to the CM frame")
