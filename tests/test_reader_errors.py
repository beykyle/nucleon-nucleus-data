"""No corpus data point may rest on EXFOR's data-point reader (digitisation) uncertainty alone.

Every record whose EXFOR subentry has points with only a reader/digitisation error must carry the
``author_errors`` correction (author uncertainty, the Doering table, or a drop), or be allowlisted here with a
reason. See docs/DATA_CLEANING.md.
"""

from __future__ import annotations

import importlib.util
import json

import numpy as np
import pytest

from nn_corpora import author_errors as ae
from nn_corpora.spec import DATA_DIR

CORPORA = ["elm", "kduq", "chuq", "sm3"]

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


@pytest.mark.parametrize("corpus", CORPORA)
def test_no_dropped_record_remains(corpus):
    left = [rec["EXFORAccessionNumber"] for _, rec in records(corpus)
            if corpus in {**ae.DROP_FLAGGED, **ae.DROP_DUPLICATES}.get(rec["EXFORAccessionNumber"][:8], set())]
    assert not left, f"{corpus}: dropped subentries still present: {left}"


def test_doering_is_the_thesis_table():
    table = ae._doering()
    seen = 0
    for corpus in ("elm", "sm3"):
        for _, rec in records(corpus):
            sub = rec["EXFORAccessionNumber"][:8]
            if sub in table:
                seen += 1
                rows = sorted(table[sub])
                assert rec["data"]["x"] == [a for a, _, _ in rows]
                assert np.allclose(rec["data"]["y"], [1e-3 * v for _, v, _ in rows])
                assert np.allclose(np.asarray(rec["data"]["y_err"]) / np.asarray(rec["data"]["y"]),
                                   [e / 100 for _, _, e in rows])
                assert rec["data"]["systematic_normalization_error"] == pytest.approx(0.10)
    assert seen == 24, "12 Doering sets in each of elm and sm3"


def test_correction_is_idempotent():
    for corpus in CORPORA:
        for _, rec in records(corpus):
            before = json.dumps(rec, sort_keys=True)
            assert json.dumps(ae.correct(json.loads(before), corpus), sort_keys=True) == before


@pytest.mark.slow
@pytest.mark.parametrize("corpus", CORPORA)
def test_every_reader_only_record_is_corrected(corpus):
    """Audit each record against its EXFOR subentry (scripts/audit_reader_errors.py)."""
    spec_ = importlib.util.spec_from_file_location("audit", DATA_DIR.parent / "scripts" / "audit_reader_errors.py")
    audit = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(audit)
    bad = []
    for path, rec in records(corpus):
        found = audit.audit_record(rec, corpus, path.parent.name, path.name)
        if isinstance(found, dict):
            bad.append((rec["EXFORAccessionNumber"], found.get("error")))
        elif found and ae.MARK not in rec["notes"] and rec["EXFORAccessionNumber"][:8] not in ALLOWLIST:
            bad.append((rec["EXFORAccessionNumber"], rec.get("energy"), f"{found[0]['n_reader_only']} reader-only"))
    assert not bad, f"{corpus}: records resting on reader errors: {bad[:10]}"
