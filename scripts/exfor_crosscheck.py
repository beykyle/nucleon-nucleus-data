"""Cross-check corpus records against their EXFOR entries -> papers/exfor_crosscheck_generated.md (hand summary: papers/notes_from_exfor.md).

    uv run python scripts/exfor_crosscheck.py [--entries O0178 O0328 ...]   (default: the entries in papers/INDEX.md)

For each entry, from the local X4 database (the same entries the IAEA EXFOR website shows; the website itself sits
behind a browser challenge and cannot be scripted):
- the bibliography: TITLE, AUTHOR, every REFERENCE code, each mapped to a DOI through Crossref (accepted only when
  volume and first page match), compared with the DOI in papers/INDEX.md;
- STATUS (TABLE vs CURVE = digitised), HISTORY (relabelled columns, re-digitisation dates), ERR-ANALYS of subentry 001
  and of each used subentry, and COMMON systematic errors;
- for every corpus record of the entry, the EXFOR column(s) its per-point uncertainty reproduces (single columns,
  or quadrature pairs, matched within 2 % relative at ≥ 90 % of the points), its normalisation error against the
  systematic errors EXFOR states, and the points left with reader/digitisation error only.
Flags are listed at the top of each section; a summary table at the top of the file.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
X4 = Path("/mnt/research/reactiontheoryinitiative/beyerkyl_local/x4db/unpack_exfor-2025/X4-2025-12-31/db")
READER = re.compile(r"reader|reading|digiti[sz]", re.I)
JOURNAL = {"PR/C": "Physical Review C", "PR/D": "Physical Review D", "PR": "Physical Review", "NP/A": "Nuclear Physics A", "NP": "Nuclear Physics",
           "PL/B": "Physics Letters B", "PL": "Physics Letters", "JPJ": "Journal of the Physical Society of Japan", "JPJ/S": "Journal of the Physical Society of Japan",
           "JP/G": "Journal of Physics G", "JPG": "Journal of Physics G", "IZV": "Izvestiya Akademii Nauk SSSR Seriya Fizicheskaya"}


# -- X4 text ------------------------------------------------------------------------------------------------------


def subentries(entry: str) -> dict[str, list[str]]:
    lines = (X4 / entry[:3] / f"{entry}.x4").read_text(errors="replace").splitlines()
    out, cur = {}, None
    for line in lines:
        if line.startswith("SUBENT"):
            cur = line[14:22].strip()
            out[cur] = []
        if cur:
            out[cur].append(line[:66].rstrip())
        if line.startswith("ENDSUBENT"):
            cur = None
    return out


def bib_fields(lines: list[str]) -> dict[str, str]:
    fields, key = defaultdict(str), None
    in_bib = False
    for line in lines:
        if line.startswith("BIB"):
            in_bib = True
            continue
        if line.startswith("ENDBIB"):
            break
        if not in_bib:
            continue
        k, body = line[:11].strip(), line[11:66].strip()
        if k:
            key = k
        if key:
            fields[key] += (" " if fields[key] else "") + body
    return dict(fields)


def common_block(lines: list[str]) -> dict[str, str]:
    for i, line in enumerate(lines):
        if line.startswith("COMMON"):
            labels = [lines[i + 1][j:j + 11].strip() for j in range(0, 66, 11)]
            units = [lines[i + 2][j:j + 11].strip() for j in range(0, 66, 11)]
            vals = [lines[i + 3][j:j + 11].strip() for j in range(0, 66, 11)]
            return {l: f"{v} {u}" for l, v, u in zip(labels, vals, units) if l}
    return {}


def err_analys(text: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r"\(([A-Z0-9+\-]+)(?:,[^)]*)?\)\.?\s*([^()]*)", text or ""):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


# -- DOIs ---------------------------------------------------------------------------------------------------------


def reference_codes(text: str) -> list[tuple]:
    """(type, journal, volume, page, year) from REFERENCE text like '(J,PR/C,12,378,75)'."""
    out = []
    for m in re.finditer(r"\(([A-Z]),([A-Z/]+),(\d+)(?:,\(\d+\))?,(\d+),(\d{2,4})\)", text or ""):
        y = int(m.group(5))
        year = y if y > 1900 else (1900 + y if y > 30 else 2000 + y)
        out.append((m.group(1), m.group(2), m.group(3), m.group(4), year))
    return out


_DOI_CACHE: dict = {}
APS = {"PR": "PhysRev", "PR/C": "PhysRevC", "PR/D": "PhysRevD", "PRL": "PhysRevLett"}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nn-corpora-crosscheck (mailto:kylebeyer1@gmail.com)"})
    return json.load(urllib.request.urlopen(req, timeout=30))["message"]


def _journal_ok(journal: str, container: str) -> bool:
    """The Crossref container title must be the journal of the EXFOR code (letter section included)."""
    want, got = JOURNAL.get(journal, journal).lower(), (container or "").lower()
    if journal in ("PR", "NP", "PL"):  # unsectioned old series: exact title (not 'Physical Review C', etc.)
        return got in (want, want + "s") or got.startswith(want + " (")
    return got.startswith(want)


def crossref_doi(journal: str, vol: str, page: str, year: int) -> str | None:
    """DOI for a journal REFERENCE code: APS DOIs are constructed and checked; others searched. Accepted only when
    the journal title, the volume and the first page match."""
    key = (journal, vol, page)
    if key in _DOI_CACHE:
        return _DOI_CACHE[key]
    doi = None
    try:
        if journal in APS:
            m = _get(f"https://api.crossref.org/works/10.1103/{APS[journal]}.{vol}.{page}")
            if str(m.get("volume")) == vol and str(m.get("page", "")).split("-")[0] == page:
                doi = m["DOI"].lower()
        if doi is None:
            q = urllib.parse.quote(f"{vol} {page} {year}")
            cq = urllib.parse.quote(JOURNAL.get(journal, journal))
            items = _get(f"https://api.crossref.org/works?rows=20&select=DOI,volume,page,container-title"
                         f"&query.bibliographic={q}&query.container-title={cq}")["items"]
            q2 = urllib.parse.quote(f"{JOURNAL.get(journal, journal)} {vol} {page} {year}")
            items += _get(f"https://api.crossref.org/works?rows=20&select=DOI,volume,page,container-title"
                          f"&query.bibliographic={q2}")["items"]
            for it in items:
                if (str(it.get("volume", "")) == vol and str(it.get("page", "")).split("-")[0] == page
                        and _journal_ok(journal, (it.get("container-title") or [""])[0])):
                    doi = it["DOI"].lower()
                    break
    except Exception:  # noqa: BLE001
        doi = None
    time.sleep(0.25)
    _DOI_CACHE[key] = doi
    return doi


# -- corpus records vs EXFOR columns -------------------------------------------------------------------------------


def corpus_records(entry: str) -> list[tuple[str, str, dict]]:
    out = []
    for f in sorted((ROOT / "data").glob("*/*/*.json")):
        if f.name == "manifest.json" or f.parts[-3] == "test":
            continue
        try:
            recs = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        for r in recs if isinstance(recs, list) else []:
            if isinstance(r, dict) and str(r.get("EXFORAccessionNumber", "")).startswith(entry):
                out.append((f.parts[-3], f"{f.parts[-2]}/{f.name}", r))
    return out


def exfor_rows(entry: str, sub: str):
    from nn_corpora.errors import entry_data_sets

    blocks = [ds for k, ds in entry_data_sets(entry).items() if k[1] == sub]
    return blocks


def infer_columns(rec: dict, ds) -> dict:
    """Which EXFOR error column(s) reproduce the corpus per-point uncertainty (relative, within 2 %)."""
    labels, units = list(ds.labels), list(ds.units)
    ang = next((l for l in labels if l.startswith("ANG") and "ERR" not in l), None)
    dat = next((l for l in labels if l.startswith("DATA") and "ERR" not in l), None)
    en = "EN" if "EN" in labels else None
    errs = [l for l in labels if "ERR" in l and not l.startswith(("ANG", "EN", "E-"))]
    if ang is None or dat is None:
        return dict(note="no angle/data column")
    E = rec.get("energy")
    rows = [r for r in ds.data if not (en and E is not None and r[labels.index(en)] is not None
                                       and abs(r[labels.index(en)] - E) > 1e-3 * max(1, E))]
    x, y, ye = rec["data"]["x"], rec["data"]["y"], rec["data"]["y_err"]

    def absolute(row, l):
        """The column's uncertainty in the data's units (per-cent columns converted)."""
        v = row[labels.index(l)]
        if v is None:
            return 0.0
        u = units[labels.index(l)].upper()
        d = row[labels.index(dat)] or 0.0
        return abs(d) * v / 100 if "PER-CENT" in u else v

    ymax = max(map(abs, y)) if y else 1.0
    matched = []  # (corpus error in EXFOR units, EXFOR row): absolute comparison, so Ay near zero works
    for i, xi in enumerate(x):
        r = min(rows, key=lambda r: abs((r[labels.index(ang)] or 1e9) - xi), default=None)
        if r is None or abs((r[labels.index(ang)] or 1e9) - xi) >= 0.06:
            continue
        d = r[labels.index(dat)] or 0.0
        # cross sections may be rescaled in the corpus (b/sr vs mb/sr, ratio to Rutherford): carry the corpus error
        # as relative to its own value, applied to the EXFOR value; dimensionless Ay is compared as is
        is_xs = any("B/SR" in u.upper() or "NO-DIM" not in u.upper() for l, u in zip(labels, units) if l == dat)
        matched.append(((ye[i] / y[i]) * abs(d) if is_xs and y[i] else ye[i], r))
    if not matched:
        return dict(note="corpus points not matched to EXFOR angles (frame conversion?)")
    best = None
    for k in (1, 2):
        for combo in itertools.combinations(errs, k):
            ok = sum(1 for c, r in matched
                     if abs(sum(absolute(r, l) ** 2 for l in combo) ** 0.5 - c) <= max(0.02 * c, 2e-4))
            if best is None or ok > best[1]:
                best = (combo, ok)
    reader = [l for l in errs if l == "ERR-DIG" or READER.search(ERR_DESC.get(l, ""))]
    author = [l for l in errs if l not in reader and not re.match(r"ERR-\d", l)]
    ro = [r[labels.index(ang)] for c, r in matched
          if reader and not any((r[labels.index(l)] or 0) > 0 for l in author)]
    return dict(columns=best[0], frac=best[1] / len(matched), n=len(matched), errs=errs, reader=reader,
                author=author, reader_only=ro, status_cols=dict(zip(labels, units)))


ERR_DESC: dict[str, str] = {}


# -- report -------------------------------------------------------------------------------------------------------


def entry_section(entry: str, index_doi: str | None):
    global ERR_DESC
    subs = subentries(entry)
    b001 = bib_fields(subs.get(f"{entry}001", []))
    refs = reference_codes(b001.get("REFERENCE", ""))
    dois = []
    for t, j, v, p, y in refs:
        dois.append(((t, j, v, p, y), crossref_doi(j, v, p, y) if t == "J" else None))
    flags = []
    jdois = [d for (r, d) in dois if d]
    if index_doi and jdois and index_doi.lower() not in jdois:
        flags.append(f"DOI mismatch: INDEX {index_doi} vs EXFOR REFERENCE {jdois}")
    if not jdois and index_doi:
        flags.append("EXFOR REFERENCE gave no Crossref DOI (INDEX DOI kept)")
    L = [f"## {entry}: {b001.get('AUTHOR', '')}", "",
         f"- **Title:** {b001.get('TITLE', '')}",
         f"- **REFERENCE:** {b001.get('REFERENCE', '')}"]
    for (t, j, v, p, y), d in dois:
        L.append(f"  - ({t},{j},{v},{p},{y}) → " + (f"[{d}](https://doi.org/{d})" if d else "no DOI found"))
    L.append(f"- **INDEX DOI:** {index_doi or '—'}")
    if b001.get("ERR-ANALYS"):
        L.append(f"- **ERR-ANALYS (001):** {b001['ERR-ANALYS']}")
    c001 = common_block(subs.get(f"{entry}001", []))
    if c001:
        L.append(f"- **COMMON (001):** {c001}")
    if b001.get("HISTORY"):
        L.append(f"- **HISTORY (001):** {b001['HISTORY']}")
    recs = corpus_records(entry)
    by_sub = defaultdict(list)
    for corpus, path, r in recs:
        by_sub[str(r["EXFORAccessionNumber"])[:8]].append((corpus, path, r))
    for sub, items in sorted(by_sub.items()):
        bs = bib_fields(subs.get(sub, []))
        cs = common_block(subs.get(sub, []))
        ERR_DESC = {**err_analys(b001.get("ERR-ANALYS", "")), **err_analys(bs.get("ERR-ANALYS", ""))}
        st = bs.get("STATUS", b001.get("STATUS", ""))
        L += ["", f"### {sub}: {bs.get('REACTION', '')[:90]}",
              f"- STATUS: {st or '—'}" + ("  ← digitised from a figure" if "CURVE" in st else ""),
              f"- ERR-ANALYS: {bs.get('ERR-ANALYS', '—')}", f"- COMMON: {cs or '—'}"]
        if bs.get("HISTORY"):
            L.append(f"- HISTORY: {bs['HISTORY']}")
            if re.search(r"->|re-?digiti", bs["HISTORY"], re.I):
                flags.append(f"{sub}: EXFOR relabelled columns / re-digitised ({bs['HISTORY'][:120]})")
        try:
            blocks = exfor_rows(entry, sub)
        except Exception as exc:  # noqa: BLE001
            L.append(f"- (EXFOR data not parseable: {exc})")
            continue
        for corpus, path, r in items:
            if not blocks:
                continue
            inf = infer_columns(r, blocks[0])
            norm = r["data"].get("systematic_normalization_error")
            line = f"- **{corpus}** `{path}` E = {r.get('energy')} MeV, norm err {norm}: "
            if "columns" in inf:
                line += (f"per-point error = {' ⊕ '.join(inf['columns']) or '?'} "
                         f"({100 * inf['frac']:.0f} % of {inf['n']} points); reader columns {inf['reader'] or '—'}; "
                         f"reader-only points: {len(inf['reader_only'])}")
                if inf["frac"] < 0.9:
                    flags.append(f"{sub} {corpus}: corpus errors not reproduced by any EXFOR column combination "
                                 f"({100 * inf['frac']:.0f} % match)")
                if inf["reader_only"]:
                    flags.append(f"{sub} {corpus}: {len(inf['reader_only'])} reader-only points")
                if inf["columns"] and all(c in inf["reader"] for c in inf["columns"]):
                    flags.append(f"{sub} {corpus}: per-point error is reader/digitisation only")
            else:
                line += inf.get("note", "")
            L.append(line)
    stated_sys = " ".join(f"{k}={v}" for k, v in c001.items() if re.match(r"ERR-\d", k))
    return L, flags, dict(entry=entry, refs=len(refs), dois=jdois, flags=len(flags), sys=stated_sys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entries", nargs="*")
    ap.add_argument("--out", type=Path, default=ROOT / "papers" / "exfor_crosscheck_generated.md")
    a = ap.parse_args()
    index = (ROOT / "papers" / "INDEX.md").read_text()
    idx = {}
    for line in index.splitlines():
        m = re.match(r"\| \d+ \| ([A-Z0-9]{5}) \|.*?\| (?:\[([^\]]+)\]|—)", line)
        if m:
            idx[m.group(1)] = m.group(2)
    entries = a.entries or list(idx)
    body, summary = [], []
    for e in entries:
        L, flags, s = entry_section(e, idx.get(e))
        body += L[:1] + [""] + ([f"> **Flags:** " + "; ".join(flags)] if flags else ["> No flags."]) + [""] + L[1:] + [""]
        summary.append((s, flags))
        print(e, len(flags), "flags", flush=True)
    head = ["# Notes from EXFOR: cross-check of the corpus records against their EXFOR entries", "",
            "Generated by `scripts/exfor_crosscheck.py` from the local X4 database (release X4-2025-12-31; the same entries "
            "the IAEA EXFOR website shows, which cannot be scripted from here). Hand notes are added under each entry. "
            "DOIs come from each entry's REFERENCE codes through Crossref (volume and first page must match).", "",
            "| entry | REFERENCE codes | DOI(s) from EXFOR | INDEX DOI agrees | flags |", "|---|---|---|---|---|"]
    for s, flags in summary:
        agree = "yes" if (idx.get(s["entry"]) or "").lower() in s["dois"] else ("— (no DOI)" if not s["dois"] else "**no**")
        head.append(f"| {s['entry']} | {s['refs']} | {', '.join(s['dois']) or '—'} | {agree} | {len(flags)} |")
    a.out.write_text("\n".join(head + ["", "---", ""] + body))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
