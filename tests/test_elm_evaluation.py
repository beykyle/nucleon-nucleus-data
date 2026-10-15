"""The ELM calibration evaluation (src/nn_corpora/elm_evaluation.py) and the data it produced in data/elm."""
import copy
import json

import numpy as np
import pytest

from nn_corpora import author_errors, elm_evaluation, spec
from nn_corpora.serialize import Record

ELM = spec.DATA_DIR / "elm"


def _payload(y, e, notes=None):
    return {"EXFORAccessionNumber": "X0000002", "data": {"x": list(range(len(y))), "y": list(y), "y_err": list(e)},
            "notes": list(notes or [])}


def test_floor_raises_only_small_errors_and_keeps_the_originals():
    p = elm_evaluation.evaluate(_payload([1.0, 2.0, 4.0], [0.001, 0.1, 0.5]), "elastic_diff_xs", (208, 82))
    assert p["data"]["y_err"] == pytest.approx([0.02, 0.1, 0.5])
    assert p["data"]["y_err_before_floor"] == pytest.approx([0.001, 0.1, 0.5])
    assert elm_evaluation.MARK in p["notes"]


def test_no_floor_on_analysing_powers():
    p = elm_evaluation.evaluate(_payload([0.1, -0.2], [0.0001, 0.0001]), "elastic_ay", (208, 82))
    assert p["data"]["y_err"] == [0.0001, 0.0001] and "y_err_before_floor" not in p["data"]


def test_idempotent():
    p = elm_evaluation.evaluate(_payload([1.0], [0.001]), "elastic_diff_xs", (40, 20))
    q = elm_evaluation.evaluate(copy.deepcopy(p), "elastic_diff_xs", (40, 20))
    assert p == q


def test_excluded_targets_dropped():
    r = [Record(target=(148, 62), payload=_payload([1.0], [0.1])), Record(target=(208, 82), payload=_payload([1.0], [0.1]))]
    out = elm_evaluation.apply(r, "elm", "elastic_diff_xs")
    assert [x.target for x in out] == [(208, 82)]
    assert elm_evaluation.apply(r[:1], "kduq_evaluated", "elastic_diff_xs")  # other corpora untouched


def test_revert_restores_the_published_errors():
    p = elm_evaluation.evaluate(_payload([1.0, 2.0], [0.001, 0.1]), "elastic_diff_xs", (40, 20))
    r = elm_evaluation.revert(p)
    assert r["data"]["y_err"] == pytest.approx([0.001, 0.1]) and elm_evaluation.MARK not in r["notes"]


def test_new_drops_have_reasons():
    for sub in ("O0287004", "O0287010", "C0622002", "14662004"):
        assert author_errors.drop_reason(sub, "elm")
    assert author_errors.drop_reason("O0287011", "elm") is None  # the tabulated Van Oers data stay
    assert author_errors.drop_reason("14662005", "elm") is None  # Pruitt 17 MeV stays


def test_rapaport_total_uncertainty():
    """10817 elastic: y_err at least the authors' 5-15 % total, rising with angle."""
    n = 0
    for path, rec in _elm_records():
        if path.parent.name == "elastic_diff_xs" and rec["EXFORAccessionNumber"].startswith("10817"):
            x, y, e = (np.asarray(rec["data"][k]) for k in ("x", "y", "y_err"))
            rel = e / y
            assert rel[np.argmin(x)] >= 0.05 - 1e-9 and rel[np.argmax(x)] >= 0.15 - 1e-9
            n += 1
    assert n > 0


def _elm_records():
    for path in ELM.glob("*/*.json"):
        if path.parent.name.startswith("_"):
            continue
        for rec in json.loads(path.read_text()):
            yield path, rec


def test_elm_data_carry_the_evaluation():
    """Every ELM record has been through the evaluation; no excluded target or dropped entry remains."""
    n = 0
    for path, rec in _elm_records():
        if path.parent.name.endswith("_direct"):
            continue
        n += 1
        assert elm_evaluation.MARK in rec.get("notes", []), path
        assert not path.stem.startswith("Sm_148"), path
        assert not str(rec["EXFORAccessionNumber"]).startswith("C0622"), path
        assert elm_evaluation.excluded_record(rec) is None, (path, rec["EXFORAccessionNumber"], rec.get("energy"))
        if path.parent.name in elm_evaluation.FLOOR_SECTORS:
            y, e = np.abs(rec["data"]["y"]), np.asarray(rec["data"]["y_err"])
            assert np.all(e >= elm_evaluation.REL_ERR_FLOOR * y * (1 - 1e-9)), (path, rec["EXFORAccessionNumber"])
    assert n > 0
