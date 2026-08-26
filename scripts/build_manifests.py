#!/usr/bin/env python3
"""Write a provenance manifest for each corpus in ``data/``.

Reads what the notebooks wrote rather than re-running curation, so the manifest always
describes the files actually on disk. Records the EXFOR database and library versions
used, and, for the tabulated corpora, how much of each sector's specification the files
account for.

Usage::

    python scripts/build_manifests.py
"""

from __future__ import annotations

import json
from collections import defaultdict

from nn_corpora import report, serialize, spec


def sector_stats(corpus: str, sector: str) -> dict:
    directory = spec.DATA_DIR / corpus / sector
    records = [r for p in sorted(directory.glob("*.json"))
               for r in json.loads(p.read_text())]

    stats = {
        "targets": sorted({r["target"] for r in records}),
        "measurements": len(records),
        "data_points": sum(len(r["data"]["x"]) for r in records),
        "entries": sorted({r["EXFORAccessionNumber"][:5] for r in records}),
        "types": sorted({r["type"] for r in records}),
        "units": sorted({r["y_units"] for r in records}),
    }

    if corpus in spec.TABULATED_CORPORA:
        rows = spec.load_sector(corpus, sector)
        in_exfor = [r for r in rows if r.in_exfor]
        allowlisted = {k for k in report.load_known_missing()
                       if k[0] == corpus and k[1] == sector}
        stats["spec_rows"] = len(rows)
        stats["spec_rows_in_exfor"] = len(in_exfor)
        stats["spec_rows_allowlisted"] = len(allowlisted)
        stats["coverage"] = round(
            1.0 - len(allowlisted) / len(in_exfor), 4) if in_exfor else 1.0

    return stats


def main() -> None:
    corpora = defaultdict(list)
    for path in sorted(spec.DATA_DIR.glob("*/*")):
        if path.is_dir():
            corpora[path.parent.name].append(path.name)

    provenance = serialize.provenance()
    for corpus, sectors in sorted(corpora.items()):
        stats = {sector: sector_stats(corpus, sector) for sector in sorted(sectors)}
        path = serialize.write_manifest(corpus, stats, provenance=provenance)
        total_m = sum(s["measurements"] for s in stats.values())
        total_p = sum(s["data_points"] for s in stats.values())
        print(f"{corpus:5s} {len(stats)} sectors  {total_m:5d} measurements  "
              f"{total_p:7d} points  -> {path.relative_to(spec.REPO_ROOT)}")


if __name__ == "__main__":
    main()
