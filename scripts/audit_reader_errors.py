"""Audit every corpus record for data points whose only uncertainty is a data-point reader (digitisation) error.

    uv run python scripts/audit_reader_errors.py [corpus ...] [--json out.json]   (default: all corpora but test)

For each record (EXFOR subentry) the EXFOR BIB ERR-ANALYS text of the subentry and of the entry's common subentry 001
is parsed to classify each uncertainty column:
- reader: the description mentions a data-point reader, reading or digitisation, or the label is ERR-DIG;
- author: any other per-point uncertainty on the observable (ERR-T, ERR-S, DATA-ERR not described as reader, ±...).

Systematic columns from the common block (ERR-1.. with a constant value in every row) are reported separately and are
not counted as per-point author errors. A point is "reader-only" if a reader column is present and every author
column is missing or zero.

Output:
- a table of the records with reader-only points: corpus, sector, file, subentry, energy, n reader-only / n
  points, their angles, the corpus y_err there (%), and the author errors of the neighbouring points;
- a summary per corpus;
- the full detail as JSON (--json path).
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from nn_corpora.errors import candidate_labels, entry_data_sets

X4 = Path("/mnt/research/reactiontheoryinitiative/beyerkyl_local/x4db/unpack_exfor-2025/X4-2025-12-31/db")
READER = re.compile(r"reader|reading|digiti[sz]", re.I)


def subent_text(entry, sub):
    f = X4 / entry[:3] / f"{entry}.x4"
    txt = f.read_text(errors="replace").splitlines()
    out, on = [], False
    for line in txt:
        if line.startswith("SUBENT") and line[15:22].strip() == f"{entry}{sub}"[:8][-8:] or line.startswith("SUBENT") and f"{entry}{sub}" in line[:30]:
            on = True
        if on:
            out.append(line[:66])
            if line.startswith("ENDBIB"):
                break
    return out


def err_analys(lines):
    """{label: description} from the ERR-ANALYS keyword block of BIB lines."""
    desc, cur, in_block = {}, None, False
    for line in lines:
        key, body = line[:11].strip(), line[11:66]
        if key and key != "ERR-ANALYS":
            if in_block:
                break
            continue
        if key == "ERR-ANALYS":
            in_block = True
        if not in_block:
            continue
        m = re.match(r"\s*\(([A-Z0-9+\-]+)(?:,[^)]*)?\)\.?(.*)", body)
        if m:
            cur = m.group(1)
            desc[cur] = m.group(2).strip()
        elif cur:
            desc[cur] += " " + body.strip()
    return desc


def classify(entry, sub, labels):
    d = {**err_analys(subent_text(entry, "001")), **err_analys(subent_text(entry, sub))}
    cands = candidate_labels(labels)
    reader = [l for l in cands if l == "ERR-DIG" or READER.search(d.get(l, ""))]
    return cands, reader, d


def audit_record(rec, corpus, sector, fname):
    acc = str(rec.get("EXFORAccessionNumber", ""))
    if len(acc) < 8:
        return None
    entry, sub = acc[:5], acc[5:8]
    try:
        blocks = {k: v for k, v in entry_data_sets(entry).items() if k[1] == acc[:8]}
    except Exception as exc:  # noqa: BLE001
        return dict(subentry=acc, error=f"{type(exc).__name__}: {exc}")
    if not blocks:
        return dict(subentry=acc, error="subentry not found")
    rx = rec["data"]
    x_rec = list(rx["x"])
    out = []
    for key, ds in blocks.items():
        labels = list(ds.labels)
        cands, reader, desc = classify(entry, acc[5:8], labels)
        if not reader:
            continue
        rows = ds.data
        const = [l for l in cands if len({r[labels.index(l)] for r in rows}) == 1 and l not in reader
                 and re.match(r"ERR-\d", l)]
        author = [l for l in cands if l not in reader and l not in const]
        ang_l = next((l for l in labels if l.startswith("ANG") and "ERR" not in l), None)
        en_l = "EN" if "EN" in labels else None
        if ang_l is None:
            continue
        E = rec.get("energy")
        ro, n = [], 0
        for r in rows:
            if en_l and E is not None and r[labels.index(en_l)] is not None and abs(r[labels.index(en_l)] - E) > 1e-3 * max(1, E):
                continue
            n += 1
            has_author = any((r[labels.index(l)] or 0) > 0 for l in author)
            if not has_author:
                ro.append(r[labels.index(ang_l)])
        if not ro:
            continue
        # corpus y_err at those angles, and the author errors (relative, %) of the points around them
        yerr = {}
        for a in ro:
            j = min(range(len(x_rec)), key=lambda k: abs(x_rec[k] - a)) if x_rec else None
            if j is not None and abs(x_rec[j] - a) < 0.06:
                yerr[a] = round(100 * rx["y_err"][j] / rx["y"][j], 1) if rx["y"][j] else None
        out.append(dict(corpus=corpus, sector=sector, file=fname, subentry=acc, pointer=key[2].strip(), energy=E,
                        projectile=rec.get("projectile"), n_points=n, n_reader_only=len(ro), reader_only_angles=ro,
                        corpus_rel_err_pct=yerr, reader_cols=reader, author_cols=author, systematic_cols=const,
                        descriptions={l: desc.get(l, "") for l in reader + author}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpora", nargs="*")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    root = Path("data")
    corpora = a.corpora or sorted(p.name for p in root.iterdir() if p.is_dir() and p.name != "test")
    found, errors, totals = [], [], defaultdict(lambda: [0, 0, 0, 0])
    for corpus in corpora:
        for f in sorted((root / corpus).rglob("*.json")):
            if f.name == "manifest.json":
                continue
            sector = f.parent.name
            try:
                recs = json.loads(f.read_text())
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(recs, list):
                continue
            for rec in recs:
                if not isinstance(rec, dict) or "data" not in rec:
                    continue
                totals[corpus][0] += 1
                res = audit_record(rec, corpus, sector, f.name)
                if res is None:
                    continue
                if isinstance(res, dict):
                    errors.append(res)
                    continue
                for r in res:
                    found.append(r)
                    totals[corpus][1] += 1
                    totals[corpus][2] += r["n_reader_only"]
                    totals[corpus][3] += r["n_points"]
    print(f"{'corpus':6s} {'sector':18s} {'subentry':9s} {'E':>7s} {'reader-only/n':>14s}  angles (corpus rel. err %)")
    for r in found:
        angs = ", ".join(f"{x:g}({r['corpus_rel_err_pct'].get(x, '-')})" for x in r["reader_only_angles"])
        print(f"{r['corpus']:6s} {r['sector']:18s} {r['subentry']:9s} {r['energy']!s:>7s} {r['n_reader_only']:>5d}/{r['n_points']:<8d}  {angs[:150]}")
    print("\nsummary: corpus: records, records with reader-only points, reader-only points / points in those records")
    for c, (n, k, ro, npts) in totals.items():
        print(f"  {c}: {n} records, {k} with reader-only points, {ro}/{npts} points")
    if errors:
        print(f"\n{len(errors)} records not auditable (entry not parseable / missing):")
        for e in errors[:40]:
            print("  ", e)
    if a.json:
        a.json.write_text(json.dumps(dict(found=found, errors=errors), indent=1, default=str))
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
