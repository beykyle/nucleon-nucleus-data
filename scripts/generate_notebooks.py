#!/usr/bin/env python3
"""Scaffold the corpus-sector curation notebooks.

The KDUQ, CHUQ and Test notebooks all do the same thing -- load a sector's spec table,
retrieve it, report coverage, plot it for inspection, write JSON -- because the
sector-specific judgement lives in ``spec/known_missing.csv`` and
``src/nn_corpora/overrides.py`` rather than in the notebooks. They are generated here
so that structure stays uniform and reviewable.

Regenerating overwrites hand edits, so run this only when the shared structure changes.

Usage::

    python scripts/generate_notebooks.py [--outdir notebooks] [--force]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat as nbf

REPO_ROOT = Path(__file__).resolve().parents[1]

CORPUS_BLURB = {
    "kduq": (
        "The KDUQ corpus is a reconstruction of the experimental data used in the "
        "Koning-Delaroche global optical potential analysis, assembled from EXFOR by "
        "the supplement's authors and tabulated in Supplemental Material B."
    ),
    "chuq": (
        "The CHUQ corpus is a reconstruction of the experimental data used in the "
        "CH89 global optical potential analysis, assembled from EXFOR by the "
        "supplement's authors and tabulated in Supplemental Material B."
    ),
    "test": (
        "The Test corpus comprises directly-measured elastic scattering, analyzing "
        "power and integral cross section data that post-date the KD and CH89 "
        "publications, drawn entirely from EXFOR."
    ),
}

SECTOR_BLURB = {
    "neutron_elastic": (
        "Neutron differential elastic scattering cross sections, stored in b/sr "
        "against CM scattering angle."
    ),
    "neutron_ay": (
        "Neutron analyzing powers, dimensionless, against CM scattering angle."
    ),
    "neutron_total": (
        "Neutron total cross sections, in barns against incident lab energy. Each data "
        "set is trimmed to the energy range the supplement tabulates and downsampled to "
        "at most one datum per MeV, following the supplement: the total cross section "
        "varies slowly enough over this range that the full complement of energy bins "
        "-- nearly 50,000 for one data set -- carries no information an optical model "
        "analysis can use."
    ),
    "proton_elastic": (
        "Proton differential elastic scattering cross sections, stored as a ratio to "
        "Rutherford against CM scattering angle. EXFOR reports some of these data sets "
        "as ratios and others as absolute cross sections; the absolute ones are divided "
        "by the Rutherford cross section so the sector is uniform."
    ),
    "proton_ay": (
        "Proton analyzing powers, dimensionless, against CM scattering angle."
    ),
    "proton_reaction": (
        "Proton reaction (nonelastic) cross sections, in barns against incident lab "
        "energy."
    ),
}


def notebook_for(corpus: str, sector: str) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    title = f"{corpus.upper()} corpus: {sector.replace('_', ' ')}"

    def md(text):
        nb.cells.append(nbf.v4.new_markdown_cell(text.strip()))

    def code(text):
        nb.cells.append(nbf.v4.new_code_cell(text.strip()))

    md(f"""
# {title}

{CORPUS_BLURB[corpus]}

{SECTOR_BLURB[sector]}

The subentries and scattering energies below are transcribed from the supplement's
tables into `spec/{corpus}_{sector}.csv`. Every row must be accounted for: it either
produces data, or it is listed in `spec/known_missing.csv` with a reason. Uncertainties
are assigned by the supplement's preference rule (`nn_corpora.errors`), and the
corrections its Comments describe are applied from `nn_corpora.overrides`.
""")

    code("""
%matplotlib inline
import matplotlib
from matplotlib import pyplot as plt

import pandas as pd

from nn_corpora import corpus, plotting, report, spec

pd.set_option("display.max_rows", 200)
""")

    md("## The specification")

    code(f"""
rows = spec.load_sector({corpus!r}, {sector!r})
print(f"{{len(rows)}} rows, {{len({{r.subentry for r in rows if r.in_exfor}})}} distinct subentries")
pd.DataFrame([vars(r) for r in rows]).head(15)
""")

    md("""
## Retrieve and clean

`corpus.curate` retrieves each entry, matches measurements back to the rows that asked
for them, applies the documented corrections, and homogenises units and frames.
""")

    code(f"""
result = corpus.curate({corpus!r}, {sector!r})
print(result.summary())
""")

    md("""
## Rows that did not resolve

Every row listed here must appear in `spec/known_missing.csv`, or the write below will
fail. The categories are: `absent-from-exfor` (the supplement itself marks the row as
not locatable), `x4i3-parse-failure` (the entry is in EXFOR but x4i3 cannot read it),
`subentry-withdrawn` (EXFOR has renumbered or removed the subentry since the supplement
was written), `energy-not-found`, and `uncertainty-unresolved`.
""")

    code("""
print(report.unresolved_table(result.data))
""")

    md("""
## Uncertainty audit

Data sets with missing uncertainties are dropped during munging, following the
supplement's removal of any data set lacking a necessary feature. This lists anything
that survived but still looks suspicious.
""")

    code("""
flags = plotting.check_uncertainties(result)
print("\\n".join(flags) if flags else "every measurement carries uncertainties")
""")

    md("""
## Inspect

Outliers here are found by eye. A mistranscribed point shows up as a single datum an
order of magnitude away from its neighbours; a badly normalised data set shows up as a
whole curve offset from others at the same energy.
""")

    code("""
plotting.plot_sector(result, max_targets=8)
plt.show()
""")

    md("""
## Write

`corpus.write` re-checks coverage against the allowlist before writing, so a data set
that silently disappears from EXFOR fails here rather than passing unnoticed.
""")

    code("""
corpus.write(result)
print(f"wrote {len(result.records)} measurements to data/{result.corpus}/{result.sector}/")
""")

    nb.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    return nb


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=REPO_ROOT / "notebooks")
    ap.add_argument("--force", action="store_true",
                    help="overwrite notebooks that already exist")
    args = ap.parse_args()

    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from nn_corpora.spec import available_sectors

    written, skipped = 0, 0
    for corpus, sector in available_sectors():
        path = args.outdir / corpus / f"{sector}.ipynb"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            skipped += 1
            continue
        nbf.write(notebook_for(corpus, sector), path)
        written += 1
        print(f"wrote {path.relative_to(REPO_ROOT)}")

    print(f"\n{written} written, {skipped} left alone (use --force to overwrite)")


if __name__ == "__main__":
    main()
