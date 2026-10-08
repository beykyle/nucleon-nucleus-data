#!/usr/bin/env python3
"""Apply ``nn_corpora.author_errors`` to the corpus files already in ``data/``, and report what changed.

The same correction runs inside ``serialize.write_sector``, so rebuilding a sector from its notebook gives the
same result; this script avoids re-running every notebook. Records already carrying ``author_errors.MARK`` are
left alone, so it is safe to rerun. Afterwards rebuild sm3 and the manifests::

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/apply_author_errors.py [--dry-run] [--report docs/author_errors_diff.md]
    uv run python scripts/curate_sm3.py && uv run python scripts/build_manifests.py
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np

from nn_corpora import author_errors, spec


def rel(d):
    y, e = np.abs(np.asarray(d["y"], float)), np.asarray(d["y_err"], float)
    return np.where(y > 0, e / np.where(y > 0, y, 1), np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", type=Path)
    ap.add_argument("corpora", nargs="*", default=["elm", "kduq", "chuq"])
    a = ap.parse_args()
    lines = ["| corpus | sector | target | subentry | E (MeV) | change | points | median err before → after | norm |",
             "|---|---|---|---|---|---|---|---|---|"]
    n = {"dropped": 0, "changed": 0, "unchanged": 0}
    for corpus in a.corpora:
        for path in sorted((spec.DATA_DIR / corpus).rglob("*.json")):
            if path.name == "manifest.json":
                continue
            recs = json.loads(path.read_text())
            out = []
            for rec in recs:
                before = copy.deepcopy(rec)
                new = author_errors.correct(rec, corpus)
                row = [corpus, path.parent.name, rec.get("target"), rec["EXFORAccessionNumber"], f"{rec.get('energy', float('nan')):g}"]
                if new is None:
                    n["dropped"] += 1
                    lines.append("| " + " | ".join(row + ["**dropped**", str(len(before["data"]["x"])), "", ""]) + " |")
                    continue
                out.append(new)
                b, c = before["data"], new["data"]
                if b == c:
                    n["unchanged"] += 1
                    continue
                n["changed"] += 1
                ay = rec.get("type") == "APower"
                f = (lambda d: np.nanmedian(np.asarray(d["y_err"], float))) if ay else (lambda d: np.nanmedian(rel(d)))
                fmt = (lambda v: f"{v:.3f}") if ay else (lambda v: f"{100 * v:.1f} %")
                what = "table" if len(b["x"]) != len(c["x"]) or b["y"] != c["y"] else "errors"
                norm = (f"{100 * b.get('systematic_normalization_error', 0):.1f} → "
                        f"{100 * c.get('systematic_normalization_error', 0):.1f} %"
                        if b.get("systematic_normalization_error") != c.get("systematic_normalization_error") else "")
                lines.append("| " + " | ".join(row + [what, f"{len(b['x'])} → {len(c['x'])}",
                                                    f"{fmt(f(b))} → {fmt(f(c))}", norm]) + " |")
            if not a.dry_run:
                path.write_text(json.dumps(out, indent=4) + "\n")
    print(n)
    text = "\n".join(lines) + "\n"
    if a.report:
        a.report.write_text("# Author-error corrections applied to data/ (scripts/apply_author_errors.py)\n\n"
                            f"Totals: {n}. sm3 copies its records from elm and kduq; see the sm3 rebuild.\n\n" + text)
    else:
        print(text)


if __name__ == "__main__":
    main()
