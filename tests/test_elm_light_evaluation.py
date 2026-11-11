"""The ELM-light corpus (data/elm_light; src/nn_corpora/elm_light.py, scripts/curate_elm_light.py)."""
import json
from collections import Counter

import numpy as np
import pytest

from nn_corpora import elm_evaluation, elm_light, spec

LIGHT = spec.DATA_DIR / "elm_light"
SYMBOL = {6: "C", 8: "O", 10: "Ne", 12: "Mg", 14: "Si", 16: "S", 18: "Ar"}
STEMS = {f"{SYMBOL[Z]}_{A}": (A, Z) for A, Z in spec.ELM_LIGHT_TARGETS}

pytestmark = pytest.mark.skipif(not LIGHT.is_dir(), reason="data/elm_light not built")


def _records(direct=False):
    for path in sorted(LIGHT.glob("*/*.json")):
        if path.parent.name.endswith("_direct") != direct:
            continue
        for rec in json.loads(path.read_text()):
            yield path, rec


# --- spec ------------------------------------------------------------------------------------------------------------
def test_target_spec():
    for A, Z in spec.ELM_LIGHT_TARGETS:
        assert 12 <= A <= 40 and A % 2 == 0 and Z % 2 == 0 and (A, Z) != (40, 20)
    for gone in ((36, 16), (36, 18), (22, 10), (38, 18)):  # no usable data (docs/ELM_LIGHT_DATA.md)
        assert gone not in spec.ELM_LIGHT_TARGETS
    for (A, Z), ex in spec.ELM_LIGHT_EX_IAS.items():
        assert (A, Z) in spec.ELM_LIGHT_TARGETS and A - Z > Z and 0.0 <= ex < 5.0
    assert set(spec.elm_light_pn_targets()) == set(spec.ELM_LIGHT_EX_IAS)
    for nat, (iso, abundance) in spec.ELM_LIGHT_NATURAL.items():
        assert nat[0] == 0 and nat[1] == iso[1] and abundance >= spec.ELM_LIGHT_NATURAL_MIN and iso in spec.ELM_LIGHT_TARGETS


def test_drop_tables_have_reasons():
    for table in (elm_light.MANUAL_DROPS, elm_light.MANUAL_RECORD_DROPS, elm_light.READER_ONLY_DROPS,
                  elm_light.BELOW_AUTHOR_DROPS, elm_light.PN_NOT_IAS_RECORDS, elm_light.EXCLUDED_PN_BY_TARGET):
        assert table and all(isinstance(v, str) and len(v) > 10 for v in table.values())
    assert not set(elm_light.READER_ONLY_DROPS) & set(elm_light.BELOW_AUTHOR_DROPS)


# --- data ------------------------------------------------------------------------------------------------------------
def test_files_are_light_targets():
    for path in LIGHT.glob("*/*.json"):
        assert path.stem in STEMS, path


def test_records_carry_the_evaluation():
    n = 0
    for path, rec in _records():
        n += 1
        assert rec["corpus"] == "elm_light" and rec["sector"] == path.parent.name, path
        assert elm_evaluation.MARK in rec["notes"], (path, rec["EXFORAccessionNumber"])
        if path.parent.name in elm_evaluation.FLOOR_SECTORS:
            y, e = np.abs(rec["data"]["y"]), np.asarray(rec["data"]["y_err"])
            assert np.all(e >= elm_evaluation.REL_ERR_FLOOR * y * (1 - 1e-9)), (path, rec["EXFORAccessionNumber"])
    assert n > 2000


def test_natural_targets_only_where_one_isotope_dominates():
    dominant = {iso for iso, _ in spec.ELM_LIGHT_NATURAL.values()}
    for path, rec in _records():
        if rec.get("natural_target"):
            assert STEMS[path.stem] in dominant, (path, rec["EXFORAccessionNumber"])
            assert any("measured on a natural" in n for n in rec["notes"])


def test_natural_samples_below_threshold_are_absent():
    """Natural Mg (79 % 24Mg) is not used, also where EXFOR codes the natural sample as 24Mg (Kyle, 2026-11-11);
    natural samples of the other elements are flagged."""
    for path, rec in _records():
        A, Z = STEMS[path.stem]
        sub = rec["EXFORAccessionNumber"][:8]
        if Z in spec.ELM_LIGHT_NATURAL_EXCLUDED and A == spec.ELM_LIGHT_NATURAL_EXCLUDED[Z][0]:
            assert not elm_light.natural_sample(sub), (path, sub)
        elif any(A == a and Z == z for (a, z), _ in spec.ELM_LIGHT_NATURAL.values()) and elm_light.natural_sample(sub):
            assert rec.get("natural_target"), (path, sub)


def test_dropped_records_are_absent():
    for path, rec in _records():
        sub, E = rec["EXFORAccessionNumber"], rec.get("energy")
        assert sub not in elm_light.MANUAL_DROPS, (path, sub)
        assert (sub, E) not in elm_light.MANUAL_RECORD_DROPS, (path, sub, E)
        assert (sub, E) not in elm_light.READER_ONLY_DROPS and (sub, E) not in elm_light.BELOW_AUTHOR_DROPS
        assert (sub, E, rec.get("ex_energy")) not in elm_light.PN_NOT_IAS_RECORDS


def test_charge_exchange_is_the_ias():
    """(p,n) only on N > Z targets with a tabulated IAS, and every final state within 50 keV of it (or untabulated
    where the IAS is the ground state, 34Cl)."""
    n = 0
    for path, rec in _records():
        if path.parent.name != "charge_exchange":
            continue
        target, ex = STEMS[path.stem], rec.get("ex_energy")
        ias = spec.ELM_LIGHT_EX_IAS[target]
        assert (ex is None and ias == 0.0) or abs(float(ex or 0.0) - ias) <= 0.05, (path, rec["EXFORAccessionNumber"])
        n += 1
    assert n >= 10


def test_no_likely_duplicates_remain():
    rec = [type("R", (), {"target": STEMS[p.stem], "payload": r})() for p, r in _records()]
    assert not [d for v, d in elm_light.near_duplicates(rec) if v == "LIKELY DUPLICATE"]


def test_direct_copies_mirror_the_curated_sectors():
    """Compound-elastic copies (scripts/talys_compound.py): one per curated record, with the CE fields."""
    for sector in ("elastic_diff_xs", "proton_reaction"):
        base = Counter(p.stem for p, _ in _records() if p.parent.name == sector)
        direct = Counter(p.stem for p, _ in _records(direct=True) if p.parent.name == f"{sector}_direct")
        assert base == direct, sector
    for path, rec in _records(direct=True):
        d = rec["data"]
        for k in ("y_measured", "compound_elastic", "ce_fraction_model", "y_err_before_compound"):
            assert len(d[k]) == len(d["x"]), (path, k)
        assert np.all(np.isfinite(d["ce_fraction_model"])), (path, rec["EXFORAccessionNumber"])


def test_records_unique():
    """No two records share sector, target, subentry, energy and final state (O0257007 once held the asymmetry and the
    Ay of one 38 MeV data set under one key)."""
    # integral sets: one subentry can hold several measurements (14269002, natC sigma_tot of two samples, pointers 1
    # and 2), so their first value is part of the key; a duplicate repeats it
    keys = Counter((p.parent.name, p.stem, r["EXFORAccessionNumber"], r.get("energy"), r.get("ex_energy"),
                    r["data"]["y"][0] if "energy" not in r else None) for p, r in _records())
    assert not [k for k, n in keys.items() if n > 1]


def test_angular_records_have_distinct_angles():
    for path, rec in _records():
        if "energy" in rec:
            assert len(set(np.round(rec["data"]["x"], 2))) >= elm_light.MIN_DISTINCT_ANGLES, (path, rec["EXFORAccessionNumber"])


def test_every_drop_key_still_matches():
    """The curation report lists drop-table keys that matched no record (EXFOR re-numbered or re-rounded)."""
    report = (spec.DATA_DIR.parent / "docs" / "elm_light_curation_report.txt").read_text()
    section = report.split("## drop-table keys matching no record", 1)[1].split("\n\n", 2)[1]
    assert section.strip() == "none", section


def test_point_energy_cuts_applied():
    for path, rec in _records():
        cut = elm_light.POINT_ENERGY_MAX.get(rec["EXFORAccessionNumber"])
        if cut and "energy" not in rec:
            assert max(rec["data"]["x"]) <= cut[0], path
