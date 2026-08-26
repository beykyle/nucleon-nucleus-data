#!/usr/bin/env python3
"""Regenerate ``spec/known_missing.csv`` from a full curation run.

Every row of the supplement's corpus tables must be accounted for. Rows that do not
resolve are listed in the allowlist with a reason, and any row that stops resolving
later -- because EXFOR was revised, or because a change here silently dropped it --
fails its notebook instead of passing unnoticed.

Run this only after reviewing why the rows in question do not resolve: it records the
current state, it does not judge it.

Usage::

    python scripts/refresh_known_missing.py [--dry-run]
"""

from __future__ import annotations

import argparse
import collections

from nn_corpora import corpus, report, spec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be written without writing it")
    args = ap.parse_args()

    rows: list[report.KnownMissing] = []
    counts: collections.Counter = collections.Counter()

    for corpus_name, sector in spec.available_sectors():
        result = corpus.curate(corpus_name, sector)
        print(f"{corpus_name}/{sector}: coverage {result.data.coverage:.1%}, "
              f"{len(result.records)} measurements, {result.n_points} points", flush=True)
        for outcome in result.data.unresolved:
            category = report.categorize(outcome.reason)
            counts[category] += 1
            rows.append(report.KnownMissing(
                corpus=outcome.row.corpus, sector=outcome.row.sector,
                target_label=outcome.row.target_label, energy_mev=outcome.row.energy_mev,
                subentry=outcome.row.subentry, category=category,
                reason=outcome.reason,
            ))

        # Rows that retrieved but did not survive cleaning -- no usable uncertainties,
        # too few scattering angles, the wrong observable -- are equally absent from the
        # corpus and equally need a recorded reason.
        for row, subentry, reason in result.dropped:
            counts["dropped-in-cleaning"] += 1
            rows.append(report.KnownMissing(
                corpus=row.corpus, sector=row.sector, target_label=row.target_label,
                energy_mev=row.energy_mev, subentry=row.subentry,
                category="dropped-in-cleaning", reason=reason,
            ))

    print(f"\n{len(rows)} unresolved rows:")
    for category, n in counts.most_common():
        print(f"  {n:5d}  {category}")

    if args.dry_run:
        print("\n(dry run; nothing written)")
        return

    report.write_known_missing(rows)
    print(f"\nwrote {report.KNOWN_MISSING_PATH}")


if __name__ == "__main__":
    main()
