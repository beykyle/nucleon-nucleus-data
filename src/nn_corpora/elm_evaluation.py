"""ELM calibration evaluation: the choices the ELM-family calibrations make on top of the author-error evaluation.

Applied to the ELM corpus only, after ``author_errors`` (``serialize.write_sector`` for corpus "elm"), so every
calibration reading ``data/elm`` uses exactly this data:

1. Excluded targets (``EXCLUDED_TARGETS``): deformed nuclei, for which a spherical optical model is not adequate;
   and excluded subentries and measurements (``EXCLUDED_SUBENTRIES``, ``EXCLUDED_RECORDS``): Fowler 208Pb(n,n),
   outliers in the isolated-resonance region, and Shane's natural-Ca sigma_tot labelled 40Ca.
2. A per-point relative error floor on cross sections (``REL_ERR_FLOOR``, 2 %): y_err = max(y_err, floor * |y|).
   Unrecognised systematic uncertainties of this size are typical; without a floor a few sets with sub-percent errors
   dominate any calibration that does not first learn a model error. Analysing powers (sector elastic_ay) are exempt:
   they cross zero, so a relative floor is meaningless there. The errors before the floor are kept in
   ``data["y_err_before_floor"]`` (only for records the floor changed), so a derived corpus that must stay faithful to
   the published errors (sm3) can undo the step (``revert``).

Every record this step touches gets ``MARK`` as a note, and a record already carrying it is returned unchanged, so the
step is idempotent. The audit behind these choices: elm/calibrations/elm_lane/DATA_AUDIT.md (2026-10-14).
"""
from __future__ import annotations

import copy

import numpy as np

MARK = "elm-evaluation v1 (src/nn_corpora/elm_evaluation.py)"
#: (A, Z) -> reason
EXCLUDED_TARGETS: dict[tuple[int, int], str] = {
    (148, 62): "148Sm is deformed (beta2 0.142): excluded from the spherical-model ELM calibrations (2026-10-14)",
}
_RES = ("in the isolated-resonance region and {r} the TALYS (KD03 + compound) elastic; removed (2026-10-14). "
        "Resonance structure in sigma_tot exceeds 20 % (beyond statistics) up to ~3 MeV in 208Pb (13735002) and "
        "40Ca (10721002), which an energy-averaged optical model does not describe (docs/ELM_CALIBRATION_DATA.md)")
#: subentry -> reason: every measurement of the subentry removed from the ELM calibrations
EXCLUDED_SUBENTRIES: dict[str, str] = {
    "12217002": ("Fowler, PR 147, 870 (1966), 208Pb(n,n) 0.7-1.8 MeV: all in the isolated-resonance region, 1.33x the "
                 "TALYS (KD03 + compound) elastic (median over its energies, up to 2.7x); removed (2026-10-14)"),
    "14269004": ("Shane et al., NIM A 614, 468 (2010), sigma_tot labelled 40Ca is a natural-Ca sample (~97 % 40Ca); the "
                 "isotopic calibrations use Finlay et al. (13569010, enriched 40Ca) over the same energies; removed "
                 "(2026-10-14)"),
}
#: (subentry, energy MeV) -> reason: single measurements removed from the ELM calibrations
EXCLUDED_RECORDS: dict[tuple[str, float], str] = {
    **{("12217002", e): _RES.format(r=f"{q} x") for e, q in (
        (0.723, 2.18), (0.821, 2.74), (0.953, 1.61), (1.154, 1.54), (1.239, 1.76), (1.477, 1.75), (1.701, 1.77),
        (1.749, 1.69))},
    ("13508002", 2.35): _RES.format(r="0.64 x"),
}
REL_ERR_FLOOR = 0.02
#: sectors the relative error floor applies to (cross sections, not analysing powers)
FLOOR_SECTORS = {"elastic_diff_xs", "charge_exchange", "neutron_total", "proton_reaction"}
FLOOR_NOTE = "relative error floor"


def evaluate(payload: dict, sector: str, target: tuple[int, int]) -> dict | None:
    """The evaluated payload, or None if the record is excluded."""
    if tuple(target) in EXCLUDED_TARGETS or excluded_record(payload):
        return None
    if MARK in (payload.get("notes") or []):
        return payload
    if sector in FLOOR_SECTORS:
        data = payload["data"]
        y = np.asarray(data["y"], dtype=float)
        e = np.asarray(data["y_err"], dtype=float)
        floor = REL_ERR_FLOOR * np.abs(y)
        raised = e < floor
        if raised.any():
            data["y_err_before_floor"] = e.tolist()
            data["y_err"] = np.where(raised, floor, e).tolist()
            payload.setdefault("notes", []).append(
                f"{FLOOR_NOTE} {100 * REL_ERR_FLOOR:g} % applied at {int(raised.sum())} of {y.size} points "
                "(ELM calibration evaluation; errors before the floor in data.y_err_before_floor)")
    payload.setdefault("notes", []).append(MARK)
    return payload


def excluded_record(payload: dict) -> str | None:
    sub, energy = str(payload.get("EXFORAccessionNumber", ""))[:8], payload.get("energy")
    if sub in EXCLUDED_SUBENTRIES:
        return EXCLUDED_SUBENTRIES[sub]
    for (s, e), why in EXCLUDED_RECORDS.items():
        if s == sub and energy is not None and abs(float(energy) - e) < 1e-3:
            return why
    return None


def apply(records, corpus: str, sector: str):
    """Evaluate a sector's records (serialize.Record) of the ELM corpus; excluded records removed."""
    if corpus != "elm":
        return records
    out = []
    for r in records:
        p = evaluate(r.payload, sector, r.target)
        if p is not None:
            r.payload = p
            out.append(r)
    return out


def revert(payload: dict) -> dict:
    """A copy of an ELM record with this step undone (floor removed, its notes dropped), for derived corpora."""
    p = copy.deepcopy(payload)
    data = p["data"]
    if "y_err_before_floor" in data:
        data["y_err"] = data.pop("y_err_before_floor")
    p["notes"] = [n for n in (p.get("notes") or []) if n != MARK and not str(n).startswith(FLOOR_NOTE)]
    return p
