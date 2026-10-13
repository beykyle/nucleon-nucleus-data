"""Audit corpus records for data points that rest on EXFOR's data-point reader (digitisation) error.

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/audit_reader_errors.py [corpus ...] [--json out.json]   (default: the evaluated corpora)

Each record is compared with its EXFOR subentry. The uncertainty columns are classified from the ERR-ANALYS text of
the subentry and of the entry's common subentry 001 (``nn_corpora.author_errors.classify``;
the per-record check is ``author_errors.audit_record``):
- reader: ERR-DIG, or described as a data-point reader / reading / digitisation uncertainty;
- systematic: numbered ERR-n columns with one value in every row, and the common columns ``author_errors.is_common``
  names (normalisation-type errors);
- author: every other per-point uncertainty on the observable.
Two kinds of point are reported:
- reader-only: a reader column is present and every author column is blank or zero there;
- author unused: EXFOR has an author error there, but the record's error is below 95 % of it.

In the evaluated corpora (ELM, sm3, ``*_evaluated``), a reader-only point is acceptable only if the record carries
``author_errors.MARK`` (an author uncertainty was supplied, see docs/AUTHOR_UNCERTAINTIES.md), and an author-unused
point never is. The table lists every record with either; the summary counts them per corpus.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from nn_corpora import author_errors as ae
from nn_corpora.spec import DATA_DIR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpora", nargs="*")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    corpora = a.corpora or sorted(ae.SCOPE)
    found, errors, totals = [], [], defaultdict(lambda: np.zeros(5, int))
    for corpus in corpora:
        for f in sorted((DATA_DIR / corpus).rglob("*.json")):
            if f.name == "manifest.json":
                continue
            for rec in json.loads(f.read_text()):
                totals[corpus][0] += 1
                r = ae.audit_record(rec)
                if r is None:
                    continue
                if "error" in r:
                    errors.append(dict(corpus=corpus, file=f.name, **r))
                    continue
                found.append(dict(corpus=corpus, sector=f.parent.name, file=f.name, **r))
                ok = (r["corrected"] or not r["n_reader_only"]) and not r["author_unused_angles"]
                totals[corpus] += [0, 1, r["n_reader_only"], len(r["author_unused_angles"]), 0 if ok else 1]
    print(f"{'corpus':6s} {'sector':18s} {'subentry':9s} {'E':>7s} {'reader-only/n':>14s} {'unused':>6s}  corrected  "
          f"reader-only angles")
    for r in found:
        angs = ", ".join(f"{x:g}" for x in r["reader_only_angles"])
        print(f"{r['corpus']:6s} {r['sector']:18s} {r['subentry']:9s} {r['energy']!s:>7s} "
              f"{r['n_reader_only']:>5d}/{r['n_points']:<8d} {len(r['author_unused_angles']):>6d}  "
              f"{'yes' if r['corrected'] else 'NO ':9s}  {angs[:120]}")
    print("\nsummary: corpus: records, with reader-only or author-unused points, such points, failing")
    for c, (n, k, ro, un, bad) in totals.items():
        print(f"  {c}: {n} records, {k} flagged ({ro} reader-only points, {un} author-unused), {bad} failing")
    if errors:
        print(f"\n{len(errors)} records not auditable:")
        for e in errors:
            print("  ", e)
    if a.json:
        a.json.write_text(json.dumps(dict(found=found, errors=errors), indent=1, default=str))
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
