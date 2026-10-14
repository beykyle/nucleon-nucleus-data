"""Tests for the corpus specification tables.

Every table must be well formed (``spec.validate_sector``). The tables transcribed from the
supplement PDF are also checked against it: if ``scripts/extract_corpus_tables.py`` is re-run
and silently drops or invents rows, the counts and spot checks here fail.
"""

from __future__ import annotations

import re
import subprocess

import pytest

from nn_corpora import spec

# (rows, unique subentries) per corpus-sector, counted from the supplement tables.
# Rows exceed subentries because one subentry usually supplies several energies.
EXPECTED = {
    ("kduq", "neutron_elastic"): (608, 237),
    ("kduq", "neutron_ay"): (31, 14),
    ("kduq", "neutron_total"): (68, 68),
    ("kduq", "proton_elastic"): (132, 117),
    ("kduq", "proton_ay"): (61, 55),
    ("kduq", "proton_reaction"): (89, 84),
    ("chuq", "neutron_elastic"): (66, 38),
    ("chuq", "neutron_ay"): (11, 5),
    ("chuq", "proton_elastic"): (85, 85),
    ("chuq", "proton_ay"): (82, 82),
    ("test", "neutron_elastic"): (196, 42),
    ("test", "neutron_ay"): (8, 4),
    ("test", "neutron_total"): (28, 28),
    ("test", "proton_elastic"): (12, 12),
    ("test", "proton_ay"): (14, 14),
    ("test", "proton_reaction"): (4, 4),
}

# Rows the supplement marks "-": present in the original KD/CH89 corpus but not
# locatable in EXFOR. Each is explained in the supplement's Comments.
EXPECTED_NOT_IN_EXFOR = {
    ("kduq", "neutron_elastic", "natCu", 155.0),
    ("kduq", "neutron_elastic", "natPb", 155.0),
    ("kduq", "proton_elastic", "56Fe", 10.93),
    ("kduq", "proton_elastic", "56Fe", 11.7),
    ("kduq", "proton_elastic", "58Ni", 11.7),
    ("kduq", "proton_reaction", "27Al", 185.0),
    ("kduq", "proton_reaction", "63Cu", 6.75),
    ("kduq", "proton_reaction", "63Cu", 9.85),
    ("kduq", "proton_reaction", "natCu", 185.0),
    ("kduq", "proton_reaction", "natPb", 185.0),
}


SUPPLEMENT = {name for name, c in spec.TABULATED.items() if c.from_supplement}


@pytest.fixture(scope="module")
def all_rows():
    return spec.load_all()


@pytest.fixture(scope="module")
def supplement_rows(all_rows):
    return [r for r in all_rows if r.corpus in SUPPLEMENT]


@pytest.mark.parametrize("corpus,sector", spec.available_sectors())
def test_table_is_well_formed(corpus, sector):
    problems = spec.validate_sector(corpus, sector)
    assert not problems, "\n".join(problems)


def test_every_supplement_sector_present():
    assert {cs for cs in spec.available_sectors() if cs[0] in SUPPLEMENT} == set(EXPECTED)


@pytest.mark.parametrize("corpus,sector", sorted(EXPECTED))
def test_sector_counts(corpus, sector):
    rows = spec.load_sector(corpus, sector)
    subentries = {r.subentry for r in rows if r.in_exfor}
    assert (len(rows), len(subentries)) == EXPECTED[(corpus, sector)]


def test_not_in_exfor_rows(supplement_rows):
    found = {
        (r.corpus, r.sector, r.target_label, r.energy_mev)
        for r in supplement_rows if not r.in_exfor
    }
    assert found == EXPECTED_NOT_IN_EXFOR


@pytest.mark.parametrize(
    "corpus,sector,label,energy,subentry,pointer",
    [
        ("kduq", "neutron_elastic", "24Mg", 3.4, "30463008", ""),
        ("kduq", "neutron_elastic", "natMg", 1.969, "11493004", ""),
        # a numeric entry carrying an EXFOR pointer
        ("kduq", "neutron_elastic", "208Pb", 1.8, "40075004", "1"),
        ("kduq", "neutron_total", "natMg", 5.293, "13753010", ""),
        # one subentry supplying the cross section (pointer S) and the analyzing
        # power (pointer A) to two different sectors
        ("chuq", "proton_elastic", "40Ca", 65.0, "O0032002", "S"),
        ("chuq", "proton_ay", "40Ca", 65.0, "O0032002", "A"),
        ("kduq", "proton_reaction", "27Al", 8.87, "D0314002", ""),
        ("test", "proton_reaction", "208Pb", 81.0, "D0356006", ""),
    ],
)
def test_spot_checks(corpus, sector, label, energy, subentry, pointer):
    rows = [
        r for r in spec.load_sector(corpus, sector)
        if r.target_label == label and r.energy_mev == energy
    ]
    assert [(r.subentry, r.pointer) for r in rows] == [(subentry, pointer)]


def test_no_accession_invented_or_dropped():
    """Every accession in the PDF tables appears in the spec, and vice versa.

    Cross-checked against a plain text extraction, which is an independent code path
    from the coordinate-based parser used to build the spec.
    """
    pdf = spec.REPO_ROOT / "supplement_experimentalCorpora.pdf"
    text = subprocess.run(
        ["pdftotext", "-f", "4", "-l", "33", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    in_text = set(re.findall(r"\b([A-Z0-9]\d{7})[A-Z0-9]?\b", text))
    in_spec = {r.subentry for r in spec.load_all() if r.in_exfor and r.corpus in SUPPLEMENT}

    assert not in_spec - in_text, "spec contains subentries absent from the PDF"
    # These two appear only in the Test corpus Comments, which direct them to be
    # merged into a sibling subentry; they are not table rows.
    assert in_text - in_spec == {"22962024", "22987006"}
