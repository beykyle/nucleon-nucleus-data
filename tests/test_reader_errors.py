"""Author-based uncertainties in the evaluated corpora; the static corpora left as published.

- In the evaluated corpora (ELM, sm3, ``*_evaluated``) no data point may rest on EXFOR's data-point reader
  (digitisation) uncertainty alone. Every record whose EXFOR subentry has reader-only points carries the
  ``author_errors`` correction (author uncertainty, the Doering table, or a drop), or is allowlisted here with a
  reason.
- The static corpora (KDUQ, CHUQ, Test) reproduce the published corpora and carry no correction.

See docs/AUTHOR_UNCERTAINTIES.md.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from nn_corpora import author_errors as ae
from nn_corpora.spec import DATA_DIR

#: corpora the corrections apply to, and the static ones they must never touch
CORRECTED = sorted(ae.SCOPE)
STATIC = sorted(ae.EVALUATED)

#: subentry -> why its reader-only points are acceptable as they are
ALLOWLIST = {
    "F0733003": "sm3 curates it with the authors' 3 % from ERR-ANALYS (sm3.EXFOR_UNCERTAINTIES)",
}


def records(corpus):
    for path in sorted((DATA_DIR / corpus).rglob("*.json")):
        if path.name == "manifest.json":
            continue
        for rec in json.loads(path.read_text()):
            yield path, rec


def keys(corpus):
    return {(path.parent.name, rec["EXFORAccessionNumber"], rec.get("energy"), rec["type"])
            for path, rec in records(corpus)}


# -- static corpora ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("corpus", STATIC)
def test_static_corpora_are_not_corrected(corpus):
    bad = [rec["EXFORAccessionNumber"] for _, rec in records(corpus)
           if any("author-errors" in n or "from the authors" in n or "Doering thesis" in n for n in rec["notes"])]
    assert not bad, f"{corpus} is static, but records carry author-uncertainty corrections: {bad[:10]}"


@pytest.mark.parametrize("static", STATIC)
def test_evaluated_corpus_is_its_static_corpus_less_the_drops(static):
    evaluated = ae.EVALUATED[static]
    kept = {k for k in keys(static) if not ae.drop_reason(k[1], evaluated)}
    assert kept == keys(evaluated)


# -- evaluated corpora -------------------------------------------------------------------------------------------


@pytest.mark.parametrize("corpus", CORRECTED)
def test_no_dropped_record_remains(corpus):
    left = [rec["EXFORAccessionNumber"] for _, rec in records(corpus) if ae.drop_reason(rec["EXFORAccessionNumber"], corpus)]
    assert not left, f"{corpus}: dropped subentries still present: {left}"


def author_y_err(data):
    """The author-error evaluation's y_err: an ELM record may have had it raised by the ELM error floor since."""
    return data.get("y_err_before_floor", data["y_err"])


def test_doering_is_the_thesis_table():
    table = ae.doering_table()
    seen = 0
    for corpus in ("elm", "sm3"):
        for _, rec in records(corpus):
            sub = rec["EXFORAccessionNumber"][:8]
            if sub in table:
                seen += 1
                rows = table[sub]
                assert rec["data"]["x"] == [a for a, _, _ in rows]
                assert np.allclose(rec["data"]["y"], [1e-3 * v for _, v, _ in rows])
                assert np.allclose(np.asarray(author_y_err(rec["data"])) / np.asarray(rec["data"]["y"]),
                                   [e / 100 for _, _, e in rows])
                assert rec["data"]["systematic_normalization_error"] == pytest.approx(np.hypot(0.10, 0.05))
    assert seen == 24, "12 Doering sets in each of elm and sm3"


def assert_idempotent(corpus, rec):
    before = json.dumps(rec, sort_keys=True)
    assert json.dumps(ae.correct(json.loads(before), corpus), sort_keys=True) == before, rec["EXFORAccessionNumber"]


def test_corrected_records_are_not_corrected_again():
    """Records carrying MARK are returned as they are, without reading EXFOR."""
    seen = 0
    for corpus in CORRECTED:
        for _, rec in records(corpus):
            if ae.MARK in rec["notes"]:
                assert_idempotent(corpus, rec)
                seen += 1
    assert seen


@pytest.mark.slow
def test_correction_is_idempotent():
    """Every record, including those the rules leave unchanged (which correct() checks against EXFOR again)."""
    for corpus in CORRECTED:
        for _, rec in records(corpus):
            assert_idempotent(corpus, rec)


def test_fill_interpolates_and_extrapolates_flat():
    th = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    filled = ae._fill(th, np.array([np.nan, 0.02, np.nan, 0.04, np.nan]))
    assert np.allclose(filled, [0.02, 0.02, 0.03, 0.04, 0.04])


def test_same_record_same_corrections_in_every_corpus():
    """A corrected record that appears in several evaluated corpora has the same uncertainties in each."""
    seen = {}
    for corpus in CORRECTED:
        for _, rec in records(corpus):
            if ae.MARK not in rec["notes"]:
                continue
            key = (rec["EXFORAccessionNumber"], rec.get("energy"), tuple(rec["data"]["x"]), tuple(rec["data"]["y"]))
            d = rec["data"]
            if key in seen:
                other, (y_err, norm) = seen[key]
                assert np.allclose(author_y_err(d), y_err), f"{key[:2]}: y_err {corpus} vs {other}"
                assert d["systematic_normalization_error"] == pytest.approx(norm), f"{key[:2]}: norm {corpus} vs {other}"
            else:
                seen[key] = (corpus, (author_y_err(d), d["systematic_normalization_error"]))


def test_analysing_powers_take_only_their_own_normalisation():
    """Cross-section normalisations (NORM) cancel in an analysing power; NORM_AY is the Ay scale."""
    fricke = 0
    for corpus in CORRECTED:
        for _, rec in records(corpus):
            if rec["type"] != "APower":
                continue
            sub = rec["EXFORAccessionNumber"]
            norm = rec["data"]["systematic_normalization_error"]
            if sub[:5] in ae.NORM_AY:
                assert norm == pytest.approx(ae.NORM_AY[sub[:5]][0]), (corpus, sub)
                fricke += 1
            for key in (sub[:8], sub[:5]):
                if key in ae.NORM:
                    assert norm != pytest.approx(ae.NORM[key][0]), f"{corpus} {sub}: Ay with a cross-section norm"
    assert fricke >= 4, "the Fricke Ay sets of elm, kduq_evaluated and chuq_evaluated"


def test_drop_reasons_only_in_scope():
    for sub in ae.DROP_FLAGGED | ae.DROP_DUPLICATES:
        for corpus in CORRECTED:
            assert ae.drop_reason(sub, corpus)
        for corpus in STATIC:
            assert ae.drop_reason(sub, corpus) is None
    assert ae.drop_reason("O0211012", "elm") is None, "Fulmer's tables are kept"


@pytest.mark.slow
def test_fricke_is_reader_plus_authors_column():
    """O0328: at points where EXFOR has the authors' ERR-1, the error is exactly ERR-DIG (+) ERR-1."""
    checked = 0
    for corpus in CORRECTED:
        for _, rec in records(corpus):
            if not rec["EXFORAccessionNumber"].startswith("O0328"):
                continue
            p = ae.exfor_points(rec["EXFORAccessionNumber"], rec["energy"], rec["data"]["x"])
            idx = ae.match(rec["data"]["x"], p.angles)
            col = p.author["ERR-1"][idx]
            has = col > 0
            ay = rec["type"] == "APower"
            scale = 1.0 if ay else np.abs(np.asarray(rec["data"]["y"]) / p.data[idx])
            want = np.hypot(p.reader[idx], col) * scale
            assert np.allclose(np.asarray(rec["data"]["y_err"])[has], want[has], rtol=1e-6), rec["EXFORAccessionNumber"]
            checked += 1
    assert checked >= 11


@pytest.mark.slow
@pytest.mark.parametrize("corpus", CORRECTED)
def test_every_reader_only_record_is_corrected(corpus):
    """Audit each record against its EXFOR subentry (also scripts/audit_reader_errors.py): no point without an
    author error, and no point whose error is below the author error EXFOR has for it."""
    bad = []
    for _, rec in records(corpus):
        found = ae.audit_record(rec)
        if found is None or rec["EXFORAccessionNumber"][:8] in ALLOWLIST:
            continue
        if "error" in found:
            bad.append((rec["EXFORAccessionNumber"], found["error"]))
        elif found["author_unused_angles"]:
            bad.append((rec["EXFORAccessionNumber"], rec.get("energy"),
                        f"error below EXFOR's author error at {found['author_unused_angles'][:5]} deg"))
        elif found["n_reader_only"] and not found["corrected"]:
            bad.append((rec["EXFORAccessionNumber"], rec.get("energy"), f"{found['n_reader_only']} reader-only"))
        else:  # a per-paper correction must cover exactly the reader-only points
            for note in rec["notes"] if found["n_reader_only"] else []:
                m = re.search(r"author uncertainty at (\d+) of (\d+) points", note)
                if m and int(m.group(1)) != found["n_reader_only"]:
                    bad.append((rec["EXFORAccessionNumber"], rec.get("energy"),
                                f"corrected {m.group(1)} points, {found['n_reader_only']} reader-only"))
    assert not bad, f"{corpus}: records resting on reader errors: {bad[:10]}"


@pytest.mark.slow
def test_missing_exfor_entry_raises():
    """A missing entry file must not read as an entry without ERR-ANALYS."""
    from nn_corpora import x4text

    with pytest.raises(FileNotFoundError):
        x4text.subentries("Z9999")


def test_unit_factor_keeps_exfor_error_of_a_rescaled_point():
    """A value the curation rescaled (elm.POINT_FIXES) keeps EXFOR's absolute error, converted like its neighbours."""
    th = np.array([20.0, 30.0, 40.0, 50.0, 60.0])
    ex = np.array([100.0, 50.0, 1.0, 10.0, 5.0])  # EXFOR's third value is 10x too small
    p = ae.ExforPoints(th, ex, np.zeros(5), {}, [])
    idx = np.arange(5)
    y = 1e-3 * ex * np.array([1, 1, 10, 1, 1])  # mb -> b, with the third value fixed
    factor, ok = ae.unit_factor(p, idx, y, False)
    assert np.allclose(factor, 1e-3) and list(ok) == [True, True, False, True, True]


# -- data-set selection, the audit, and the scripts --------------------------------------------------------------


class FakeDataSet:
    """The parts of an x4i3 data set that author_errors reads."""

    def __init__(self, labels, units, data, quantity=("DA",)):
        self.labels, self.units, self.data = labels, units, data
        self.reaction = [type("R", (), {"quantity": list(quantity)})()]


def test_rows_at_converts_the_energy_unit():
    rows = [[3.0e6, 10.0, 1.0], [5.0e6, 10.0, 2.0], [None, 20.0, 3.0]]
    ds = FakeDataSet(["EN", "ANG-CM", "DATA"], ["EV", "ADEG", "MB/SR"], rows)
    assert ae.rows_at(ds, 3.0) == [rows[0], rows[2]]
    ds = FakeDataSet(["EN", "ANG-CM", "DATA"], ["KEV", "ADEG", "MB/SR"], [[3000.0, 10.0, 1.0]])
    assert len(ae.rows_at(ds, 3.0)) == 1 and len(ae.rows_at(ds, 3.1)) == 0
    assert len(ae.rows_at(FakeDataSet(["ANG-CM", "DATA"], ["ADEG", "MB/SR"], rows), 3.0)) == 3


def test_ratio_to_rutherford_is_not_a_polarisation():
    """A ratio to Rutherford is dimensionless like an analysing power; the REACTION quantity tells them apart."""
    assert not ae.is_polarisation(FakeDataSet([], [], [], ("DA", "RTH")))
    assert ae.is_polarisation(FakeDataSet([], [], [], ("POL/DA", "ANA")))


@pytest.mark.slow
def test_cross_section_and_ay_take_their_own_data_set():
    """O0032002 holds a cross section (MB/SR) and an analysing power at the same angles."""
    xs, ay = ae.best_data_set("O0032002", None, None, False), ae.best_data_set("O0032002", None, None, True)
    assert not ae.is_polarisation(xs[0]) and ae.is_polarisation(ay[0])


@pytest.mark.slow
def test_audit_counts_the_records_own_points():
    """A record holding part of EXFOR's rows is audited over its own points."""
    for _, rec in records("chuq"):
        if rec["EXFORAccessionNumber"] == "O0091002" and rec["type"] != "APower":
            break
    full = ae.audit_record(rec)
    assert full["n_points"] == len(rec["data"]["x"]) and full["n_reader_only"] == full["n_points"]
    part = json.loads(json.dumps(rec))
    for k in ("x", "y", "y_err"):
        part["data"][k] = part["data"][k][::3]
    found = ae.audit_record(part)
    assert found["n_points"] == found["n_reader_only"] == len(part["data"]["x"])
    assert found["reader_only_angles"] == part["data"]["x"]


def load_script(name):
    import importlib.util

    from nn_corpora.spec import REPO_ROOT

    s = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod


def test_apply_skips_a_corpus_not_built_yet(tmp_path, monkeypatch, capsys):
    from nn_corpora import spec

    apply = load_script("apply_author_errors")
    monkeypatch.setattr(spec, "DATA_DIR", tmp_path)
    monkeypatch.setitem(ae.EVALUATED, "scratch", "scratch_evaluated")
    pending, replaced = {}, []
    apply.evaluate_static("scratch", apply.Report(), pending, replaced)
    assert not pending and not replaced and "not built yet" in capsys.readouterr().out


def test_crosscheck_without_error_columns_and_at_zero_degrees(monkeypatch):
    """A data set without error columns reports no match instead of failing; a 0 deg point matches."""
    xc = load_script("exfor_crosscheck")
    rows = [[0.0, 10.0], [10.0, 5.0]]
    ds = FakeDataSet(["ANG-CM", "DATA"], ["ADEG", "MB/SR"], rows)
    p = ae.ExforPoints(np.array([0.0, 10.0]), np.array([10.0, 5.0]), np.zeros(2), {}, [])
    monkeypatch.setattr(ae, "best_data_set", lambda *a, **k: (ds, p))
    monkeypatch.setattr(ae, "classify", lambda *a: ([], [], []))
    monkeypatch.setattr(ae, "audit_record", lambda rec: None)
    rec = dict(type="Absolute", energy=None, data=dict(x=[0.0, 10.0], y=[10.0, 5.0], y_err=[1.0, 0.5]))
    inf = xc.infer_columns(rec, "Z9999002")
    assert inf["columns"] == () and inf["frac"] == 0 and inf["n"] == 2
