#!/usr/bin/env python3
"""Extract the KDUQ / CHUQ / Test corpus tables from supplement_experimentalCorpora.pdf.

The supplement lists, for each corpus and sector, a table of
(target isotope, scattering energy, EXFOR accession number). Those tables are the
ground truth for which EXFOR subentries belong to each corpus, so they are parsed
here once and committed to ``spec/`` as CSV rather than re-parsed at curation time.

Plain text extraction is not reliable here: the supplement is two-column, tables and
prose sit side by side on several pages, and the mass numbers are superscripts that
land on their own line. This parser therefore works from ``pdftotext -bbox`` word
coordinates. Table columns are located by clustering the x positions of the EXFOR
accession numbers; only words inside a band to the left of an accession column are
treated as table content, which excludes the adjacent prose. Mass numbers are
identified by their smaller glyph height.

Usage::

    python scripts/extract_corpus_tables.py [--pdf PDF] [--outdir spec]
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import statistics
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

from periodictable import elements

# Page range holding the corpus tables (1-indexed, inclusive). Pages 1-3 are prose.
FIRST_TABLE_PAGE = 4
LAST_TABLE_PAGE = 33

# Superscripts (mass numbers, "nat") are set ~5.3pt tall against ~8pt body text.
SUPERSCRIPT_MAX_HEIGHT = 6.5

# How far left of an accession column the table's energy and isotope fields extend.
TABLE_BAND_WIDTH = 105.0

# Words whose vertical extents overlap within this tolerance are on the same line.
LINE_TOLERANCE = 3.0

CORPUS_HEADINGS = {
    "KDUQ CORPUS": "kduq",
    "CHUQ CORPUS": "chuq",
    "TEST CORPUS": "test",
}

SECTOR_HEADINGS = {
    "Neutron differential elastic cross sections": ("neutron_elastic", "neutron"),
    "Neutron analyzing powers": ("neutron_ay", "neutron"),
    "Neutron total cross sections": ("neutron_total", "neutron"),
    "Proton differential elastic cross sections": ("proton_elastic", "proton"),
    "Proton analyzing powers": ("proton_ay", "proton"),
    "Proton reaction cross sections": ("proton_reaction", "proton"),
}

# An EXFOR subentry is 8 characters: a 5-character entry number followed by a 3-digit
# subentry number. Neutron (numeric) entries are all digits; charged-particle entries
# begin with a letter. A trailing 9th character is an EXFOR pointer, selecting one
# data block within the subentry -- e.g. O0032002 carries the cross section under
# pointer "S" and the analyzing power under pointer "A".
ACCESSION = re.compile(r"^(?P<subentry>[A-Z0-9]\d{7})(?P<pointer>[A-Z0-9])?$")

ENERGY = re.compile(r"^\d+(?:\.\d+)?$")
ENERGY_RANGE = re.compile(r"^(?P<lo>\d+(?:\.\d+)?)-(?P<hi>\d+(?:\.\d+)?)$")

WORD = re.compile(
    r'<word xMin="(?P<x0>[-\d.]+)" yMin="(?P<y0>[-\d.]+)" '
    r'xMax="(?P<x1>[-\d.]+)" yMax="(?P<y1>[-\d.]+)">(?P<text>.*?)</word>'
)
PAGE = re.compile(r'<page width="(?P<w>[\d.]+)" height="[\d.]+">(?P<body>.*?)</page>', re.S)

SYMBOLS = {el.symbol: el.number for el in elements if el.number > 0}

# Rows the supplement marks with an em dash: listed in the original KD/CH89 corpus but
# not locatable in EXFOR. They are kept in the spec with an empty subentry so the
# tables stay a faithful transcription, and excluded from retrieval by known_missing.
NOT_IN_EXFOR = {"-", "–", "—"}


@dataclass
class Word:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def is_superscript(self) -> bool:
        return self.height < SUPERSCRIPT_MAX_HEIGHT


@dataclass
class SpecRow:
    corpus: str
    sector: str
    projectile: str
    target_A: int
    target_Z: int
    target_label: str
    energy_mev: float
    energy_hi_mev: str
    subentry: str
    pointer: str
    pdf_page: int


def read_pages(pdf: Path) -> list[tuple[float, list[Word]]]:
    """Return, per page, its width and its words with bounding boxes."""
    xml = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(FIRST_TABLE_PAGE), "-l", str(LAST_TABLE_PAGE),
         str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    pages = []
    for page in PAGE.finditer(xml):
        words = [
            Word(float(m["x0"]), float(m["y0"]), float(m["x1"]), float(m["y1"]),
                 html.unescape(m["text"]))
            for m in WORD.finditer(page["body"])
        ]
        pages.append((float(page["w"]), words))
    return pages


def group_lines(words: list[Word]) -> list[list[Word]]:
    """Group words into visual lines, ordered top to bottom, left to right."""
    lines: list[list[Word]] = []
    for word in sorted(words, key=lambda w: (w.y1, w.x0)):
        if lines and abs(word.y1 - lines[-1][-1].y1) <= LINE_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    return [sorted(line, key=lambda w: w.x0) for line in lines]


def accession_bands(words: list[Word]) -> list[tuple[float, float]]:
    """Locate table columns as x bands, by clustering accession-number positions."""
    accessions = [w for w in words if ACCESSION.match(w.text)]
    if not accessions:
        return []
    clusters: list[list[Word]] = []
    for word in sorted(accessions, key=lambda w: w.x0):
        if clusters and word.x0 - clusters[-1][-1].x0 < 20.0:
            clusters[-1].append(word)
        else:
            clusters.append([word])
    return [
        (statistics.median(w.x0 for w in c) - TABLE_BAND_WIDTH, max(w.x1 for w in c) + 3.0)
        for c in clusters
    ]


def parse_column(words: list[Word], page: int, state: dict, rows: list[SpecRow]) -> None:
    bands = accession_bands(words)

    for line in group_lines(words):
        text = " ".join(w.text for w in line).strip()

        if text in CORPUS_HEADINGS:
            state["corpus"] = CORPUS_HEADINGS[text]
            continue
        if text in SECTOR_HEADINGS:
            state["sector"], state["projectile"] = SECTOR_HEADINGS[text]
            state["in_table"] = True
            state["A"], state["Z"] = None, None
            continue
        if text == "Comments":
            state["in_table"] = False
            continue
        if not state["in_table"]:
            continue

        in_band = [w for w in line
                   if any(lo <= w.x0 and w.x1 <= hi for lo, hi in bands)]
        if not in_band:
            continue

        # Only two kinds of line carry table content: a data row, which ends in an
        # accession number (or the supplement's "-" for rows absent from EXFOR), and
        # an isotope header, which is at most a superscript mass number and an element
        # symbol. Everything else on the page is prose, and is skipped -- otherwise
        # ordinary words like "In" or "No" would be read as element symbols.
        is_data_row = any(
            ACCESSION.match(w.text) or w.text in NOT_IN_EXFOR for w in in_band
        )
        is_isotope_header = len(in_band) <= 2 and all(
            w.is_superscript or w.text in SYMBOLS for w in in_band
        )
        if not (is_data_row or is_isotope_header):
            continue

        for word in in_band:
            if word.is_superscript:
                state["A"] = 0 if word.text == "nat" else (
                    int(word.text) if word.text.isdigit() else state["A"]
                )
            elif word.text in SYMBOLS:
                state["Z"] = SYMBOLS[word.text]
            elif (acc := ACCESSION.match(word.text)) is not None:
                # tested before ENERGY: neutron accessions are all-digit, and an
                # 8-digit token is always a subentry, never a scattering energy
                rows.append(_row(state, page, acc["subentry"], acc["pointer"] or ""))
            elif (rng := ENERGY_RANGE.match(word.text)) is not None:
                state["energy"] = float(rng["lo"])
                state["energy_hi"] = rng["hi"]
            elif ENERGY.match(word.text):
                state["energy"], state["energy_hi"] = float(word.text), ""
            elif word.text in NOT_IN_EXFOR:
                rows.append(_row(state, page, "", ""))


def _row(state: dict, page: int, subentry: str, pointer: str) -> SpecRow:
    if state["A"] is None or state["Z"] is None or state["energy"] is None:
        raise ValueError(f"page {page}: accession {subentry!r} with no target or energy")
    symbol = elements[state["Z"]].symbol
    label = f"nat{symbol}" if state["A"] == 0 else f"{state['A']}{symbol}"
    return SpecRow(
        corpus=state["corpus"], sector=state["sector"], projectile=state["projectile"],
        target_A=state["A"], target_Z=state["Z"], target_label=label,
        energy_mev=state["energy"], energy_hi_mev=state["energy_hi"],
        subentry=subentry, pointer=pointer, pdf_page=page,
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, default=root / "supplement_experimentalCorpora.pdf")
    ap.add_argument("--outdir", type=Path, default=root / "spec")
    args = ap.parse_args()

    state = {"corpus": None, "sector": None, "projectile": None, "in_table": False,
             "A": None, "Z": None, "energy": None, "energy_hi": ""}
    rows: list[SpecRow] = []

    for offset, (width, words) in enumerate(read_pages(args.pdf)):
        page = FIRST_TABLE_PAGE + offset
        split = width / 2.0
        left = [w for w in words if (w.x0 + w.x1) / 2 < split]
        right = [w for w in words if (w.x0 + w.x1) / 2 >= split]
        parse_column(left, page, state, rows)
        parse_column(right, page, state, rows)

    args.outdir.mkdir(parents=True, exist_ok=True)
    sectors: dict[tuple[str, str], list[SpecRow]] = {}
    for row in rows:
        sectors.setdefault((row.corpus, row.sector), []).append(row)

    fields = list(asdict(rows[0]).keys())
    order = {"kduq": 0, "chuq": 1, "test": 2}
    for (corpus, sector), sector_rows in sorted(
        sectors.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])
    ):
        path = args.outdir / f"{corpus}_{sector}.csv"
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in sector_rows:
                writer.writerow(asdict(row))
        n_sub = len({r.subentry for r in sector_rows if r.subentry})
        n_missing = sum(1 for r in sector_rows if not r.subentry)
        print(f"{path.name:34s} {len(sector_rows):4d} rows  "
              f"{n_sub:4d} subentries  {n_missing:2d} not in EXFOR")

    print(f"\ntotal: {len(rows)} rows across {len(sectors)} sectors")


if __name__ == "__main__":
    main()
