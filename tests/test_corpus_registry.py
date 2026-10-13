"""The registry of tabulated corpora (``spec.TABULATED``), and the tools that add one.

A spec table that no registered corpus owns would never be curated, and a registered corpus
without tables would be empty; both fail here. See docs/ADDING_A_CORPUS.md.
"""

from __future__ import annotations

import csv
import importlib.util

import pytest

from nn_corpora import author_errors, spec

new_corpus = importlib.util.spec_from_file_location("new_corpus", spec.REPO_ROOT / "scripts" / "new_corpus.py")
new_corpus_mod = importlib.util.module_from_spec(new_corpus)
new_corpus.loader.exec_module(new_corpus_mod)


def test_every_spec_table_belongs_to_a_registered_corpus():
    tables = {p.stem for p in spec.SPEC_DIR.glob("*_*.csv") if p.name != "known_missing.csv"}
    registered = {f"{c}_{s}" for c in spec.TABULATED for s in spec.SECTORS}
    assert not tables - registered, (
        f"spec tables of no registered corpus or sector: {sorted(tables - registered)}; "
        "register the corpus in nn_corpora.spec.TABULATED")


def test_every_registered_corpus_has_tables():
    have = {c for c, _ in spec.available_sectors()}
    assert set(spec.TABULATED) == have


def test_evaluated_copies_follow_the_registry():
    assert author_errors.EVALUATED == {n: f"{n}_evaluated" for n, c in spec.TABULATED.items() if c.evaluated_copy}
    assert not set(spec.TABULATED) & author_errors.SCOPE, "tabulated corpora are static"


# -- scaffolding and validation ----------------------------------------------------------------------------------
# on a temporary spec directory, with a corpus name ("scratch") that is never registered


def write_rows(path, rows):
    with path.open("a", newline="") as f:
        csv.writer(f).writerows(rows)


def test_scaffold_writes_headers_and_refuses_to_overwrite(tmp_path):
    paths = new_corpus_mod.scaffold("scratch", ["proton_elastic", "neutron_total"], tmp_path)
    assert [p.name for p in paths] == ["scratch_proton_elastic.csv", "scratch_neutron_total.csv"]
    assert paths[0].read_text().strip() == ",".join(spec.COLUMNS)
    with pytest.raises(FileExistsError):
        new_corpus_mod.scaffold("scratch", ["proton_elastic"], tmp_path)
    for bad in ("Scratch", "kduq", "elm", "scratch_evaluated"):
        with pytest.raises(ValueError):
            new_corpus_mod.scaffold(bad, ["proton_elastic"], tmp_path)
    with pytest.raises(ValueError):
        new_corpus_mod.scaffold("other", ["proton_inelastic"], tmp_path)


def test_validate_accepts_a_good_table(tmp_path):
    path, = new_corpus_mod.scaffold("scratch", ["proton_elastic"], tmp_path)
    write_rows(path, [
        ["scratch", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, "", "O0142011", "", ""],
        ["scratch", "proton_elastic", "proton", 0, 28, "natNi", 40.0, "", "", "", ""],  # not in EXFOR
    ])
    assert spec.validate_sector("scratch", "proton_elastic", tmp_path) == []
    rows = spec.load_sector("scratch", "proton_elastic", tmp_path)
    assert rows[0].pdf_page is None and not rows[1].in_exfor


@pytest.mark.parametrize("row,expect", [
    (["other", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, "", "O0142011", "", ""], "file name says"),
    (["scratch", "proton_elastic", "neutron", 208, 82, "208Pb", 30.3, "", "O0142011", "", ""], "projectile"),
    (["scratch", "proton_elastic", "proton", 208, 82, "Pb208", 30.3, "", "O0142011", "", ""], "target_label"),
    (["scratch", "proton_elastic", "proton", 300, 82, "300Pb", 30.3, "", "O0142011", "", ""], "unphysical"),
    (["scratch", "proton_elastic", "proton", 208, 82, "208Pb", -1, "", "O0142011", "", ""], "out of range"),
    (["scratch", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, 40.0, "O0142011", "", ""], "energy range"),
    (["scratch", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, "", "O0142", "", ""], "8-character"),
    (["scratch", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, "", "O0142011", "X", ""], "pointer"),
    (["scratch", "proton_elastic", "proton", 208, 82, "208Pb", "thirty", "", "O0142011", "", ""], "not a number"),
])
def test_validate_rejects_a_bad_row(tmp_path, row, expect):
    path, = new_corpus_mod.scaffold("scratch", ["proton_elastic"], tmp_path)
    write_rows(path, [row])
    problems = spec.validate_sector("scratch", "proton_elastic", tmp_path)
    assert len(problems) == 1 and expect in problems[0], problems


def test_validate_rejects_duplicates_and_bad_headers(tmp_path):
    path, = new_corpus_mod.scaffold("scratch", ["proton_elastic"], tmp_path)
    row = ["scratch", "proton_elastic", "proton", 208, 82, "208Pb", 30.3, "", "O0142011", "", ""]
    write_rows(path, [row, row])
    assert ["duplicate" in p for p in spec.validate_sector("scratch", "proton_elastic", tmp_path)] == [True]
    path.write_text("corpus,sector\n")
    assert "header" in spec.validate_sector("scratch", "proton_elastic", tmp_path)[0]
