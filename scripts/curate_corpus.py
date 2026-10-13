#!/usr/bin/env python3
"""Curate a tabulated corpus from its spec tables and write it to data/, without notebooks.

For each sector of the corpus (``spec/<name>_<sector>.csv``): validate the table, retrieve and
clean it (``nn_corpora.corpus.curate``), print the summary and the rows that did not resolve,
and write it (``nn_corpora.corpus.write``). This is what each sector's notebook does, less the
plots; use ``scripts/generate_notebooks.py --corpus NAME`` for those.

As in the notebooks, the write fails if a spec row does not resolve in EXFOR and is not listed in
``spec/known_missing.csv``; rows dropped in cleaning must be listed there too, which the tests
check. ``--allow-unresolved`` writes anyway: for a corpus's first build, before its rows are
reviewed and recorded with ``scripts/refresh_known_missing.py``.

Usage::

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/curate_corpus.py NAME [--sector SECTOR ...] [--allow-unresolved]

See docs/ADDING_A_CORPUS.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nn_corpora import corpus, report, spec  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="a corpus registered in nn_corpora.spec.TABULATED")
    ap.add_argument("--sector", nargs="+", help="only these sectors (default: every sector with a spec table)")
    ap.add_argument("--allow-unresolved", action="store_true",
                    help="write even if rows are neither resolved nor in spec/known_missing.csv")
    a = ap.parse_args()

    if a.name not in spec.TABULATED:
        raise SystemExit(f"{a.name!r} is not registered in nn_corpora.spec.TABULATED "
                         f"(registered: {', '.join(spec.TABULATED)})")
    sectors = corpus.all_sectors(a.name)
    if not sectors:
        raise SystemExit(f"no spec tables spec/{a.name}_<sector>.csv")
    if a.sector:
        missing = set(a.sector) - set(sectors)
        if missing:
            raise SystemExit(f"no spec table for {', '.join(sorted(missing))}")
        sectors = [s for s in sectors if s in a.sector]

    problems = [p for s in sectors for p in spec.validate_sector(a.name, s)]
    if problems:
        raise SystemExit("spec tables are malformed:\n  " + "\n  ".join(problems))

    unaccounted = 0
    for sector in sectors:
        print(f"== {a.name}/{sector}", flush=True)
        result = corpus.curate(a.name, sector)
        print(result.summary())
        table = report.unresolved_table(result.data)
        if table.strip():
            print(table)
        try:
            corpus.write(result, check=not a.allow_unresolved)
        except AssertionError as e:  # report.check_coverage: rows neither resolved nor allowlisted
            raise SystemExit(f"{a.name}/{sector} not written: {e}\nReview the rows above; record them with "
                             f"scripts/refresh_known_missing.py --corpus {a.name}, or rerun with --allow-unresolved")
        # rows dropped in cleaning must be allowlisted too (tests/test_data_integrity.py)
        known = report.load_known_missing()
        unaccounted += len(report.unexpected(result.data, known)) + sum(
            1 for row, _, _ in result.dropped
            if (row.corpus, row.sector, row.target_label, round(row.energy_mev, 6), row.subentry) not in known)
        print(f"wrote {len(result.records)} measurements to data/{a.name}/{sector}/\n")

    steps = []
    if unaccounted:
        steps.append(f"{unaccounted} rows are not yet in spec/known_missing.csv: review them, then "
                     f"uv run python scripts/refresh_known_missing.py --corpus {a.name}")
    if a.name in spec.TABULATED and spec.TABULATED[a.name].evaluated_copy:
        steps.append(f"uv run python scripts/apply_author_errors.py   # builds data/{a.name}_evaluated")
    steps.append("uv run python scripts/build_manifests.py")
    print("next:\n  " + "\n  ".join(steps))


if __name__ == "__main__":
    main()
