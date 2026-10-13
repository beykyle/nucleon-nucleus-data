#!/usr/bin/env python3
"""Scaffold a new tabulated corpus: one empty spec table per sector.

Writes ``spec/<name>_<sector>.csv`` with the header row only, and prints the entry to add to
``nn_corpora.spec.TABULATED`` and the next steps. It never overwrites a spec table and never edits
the source: registering the corpus is a one-line change to review. See docs/ADDING_A_CORPUS.md.

Usage::

    python scripts/new_corpus.py NAME --sectors SECTOR [SECTOR ...] [--spec-dir spec]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nn_corpora import spec  # noqa: E402

#: names that already mean something in data/
RESERVED = {"elm", "sm3"}


def scaffold(name: str, sectors: list[str], spec_dir: Path = spec.SPEC_DIR) -> list[Path]:
    """Write the empty spec tables; raise ValueError on a bad name or sector, FileExistsError on a clash."""
    if not re.fullmatch(r"[a-z][a-z0-9]*", name) or name.endswith("evaluated"):
        raise ValueError(f"{name!r}: use lower-case letters and digits, starting with a letter "
                         "(it names data/<name> and spec/<name>_<sector>.csv)")
    if name in RESERVED or name in spec.TABULATED:
        raise ValueError(f"{name!r} is already a corpus")
    unknown = [s for s in sectors if s not in spec.SECTORS]
    if unknown:
        raise ValueError(f"unknown sectors {unknown}; choose from {', '.join(spec.SECTORS)}")
    paths = [spec.sector_path(name, s, spec_dir) for s in sectors]
    clash = [p for p in paths if p.exists()]
    if clash:
        raise FileExistsError(f"already exist: {', '.join(str(p) for p in clash)}")
    spec_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        with path.open("w", newline="") as f:
            csv.writer(f).writerow(spec.COLUMNS)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="corpus name: lower case, e.g. 'mycorpus'")
    ap.add_argument("--sectors", nargs="+", required=True, choices=list(spec.SECTORS))
    ap.add_argument("--spec-dir", type=Path, default=spec.SPEC_DIR)
    a = ap.parse_args()
    try:
        paths = scaffold(a.name, a.sectors, a.spec_dir)
    except (ValueError, FileExistsError) as e:
        raise SystemExit(str(e))
    for p in paths:
        print(f"wrote {p}")
    print(f"""
Next (docs/ADDING_A_CORPUS.md):
1. Register the corpus in src/nn_corpora/spec.py, in TABULATED:

    TabulatedCorpus(
        "{a.name}", "{a.name.upper()}",
        "One paragraph: what the corpus is and where its table comes from.",
        "The publication or source of the table",
        evaluated_copy=True),  # False: no {a.name}_evaluated

2. Fill the spec tables, one row per data set and energy (columns: {', '.join(spec.COLUMNS)}).
3. uv run python scripts/curate_corpus.py {a.name} --allow-unresolved
4. Review the unresolved rows, then: uv run python scripts/refresh_known_missing.py --corpus {a.name}
5. uv run python scripts/curate_corpus.py {a.name}
6. uv run python scripts/apply_author_errors.py && uv run python scripts/build_manifests.py
""")


if __name__ == "__main__":
    main()
