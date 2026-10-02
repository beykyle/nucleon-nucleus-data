"""Build data/sm3: the data sets of Danielewicz, Singh & Lee (2017), from nn_corpora.sm3.

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/curate_sm3.py
    uv run python scripts/build_manifests.py

Records named in sm3.SELECTION with source "elm" or "kduq" are copied from that corpus
(corpus/sector relabelled, notes kept, one provenance note added); those with source "exfor"
are curated here with the ELM machinery (lab -> CM, (p,p) as a ratio to Rutherford, default
normalization error) plus the uncertainty treatment in sm3.EXFOR_UNCERTAINTIES.  Every pick
must match exactly one record.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from nn_corpora import elm_curate, munge, serialize, sm3, spec  # noqa: E402

DATA = ROOT / "data"
PROJECTILE_TUPLE = {"proton": (1, 1), "neutron": (1, 0)}


def copied(pick: sm3.Pick, target) -> tuple[dict, str | None]:
    """The record of another corpus for this pick, relabelled for sm3, and its bib entry."""
    src_sector = sm3.SOURCE_SECTOR[(pick.source, pick.sector)]
    path = DATA / pick.source / src_sector / f"{serialize.target_filename(target)}.json"
    recs = [r for r in json.loads(path.read_text())
            if r["EXFORAccessionNumber"] == pick.subentry and r["projectile"] == pick.projectile
            and abs(float(r["energy"]) - pick.energy) < 1e-6]
    if len(recs) != 1:
        raise LookupError(f"{pick}: {len(recs)} records in {path}")
    rec = dict(recs[0])
    rec["notes"] = list(rec.get("notes") or []) + [
        f"copied from the {pick.source} corpus ({src_sector}) for sm3 ({pick.reference})"]
    rec["corpus"], rec["sector"] = "sm3", pick.sector
    bib = None
    bibfile = DATA / pick.source / src_sector / f"{src_sector}.bib"
    if bibfile.exists():
        entry = pick.subentry[:5]
        text = bibfile.read_text()
        for block in text.split("\n@")[0:]:
            if entry in block:
                bib = block if block.startswith("@") else "@" + block
                break
    return rec, bib


def curated(pick: sm3.Pick, target) -> tuple[dict, str | None]:
    """Curate one EXFOR subentry at one energy with the ELM machinery."""
    proj = PROJECTILE_TUPLE[pick.projectile]
    quantities = ("dXS/dA", "dXS/dRuth") if pick.projectile == "proton" else ("dXS/dA",)
    data = elm_curate.query_elastic(proj, quantities, [target],
                                    (pick.energy - 0.05, pick.energy + 0.05), spec.ELM_MIN_NUM_PTS)
    found = []
    for q in quantities:
        for entry_id, entry in data[target].data[q].entries.items():
            for m in entry.measurements:
                if m.subentry == pick.subentry and abs(m.Einc - pick.energy) < 1e-6:
                    found.append((q, entry_id, entry, m))
    if len(found) != 1:
        raise LookupError(f"{pick}: {len(found)} EXFOR measurements")
    q, entry_id, entry, m = found[0]
    if pick.subentry in sm3.EXFOR_UNCERTAINTIES:
        frac, norm, text = sm3.EXFOR_UNCERTAINTIES[pick.subentry]
        m.statistical_err = frac * np.abs(m.y)
        m.systematic_norm_err = norm
        munge.note(m, text)
    # keep only this measurement in the entry, then run the ELM munging and serialization
    entry.measurements[:] = [m]
    for qq in quantities:
        store = data[target].data[qq].entries
        for k in list(store):
            if k != entry_id or qq != q:
                del store[k]
    result = elm_curate.ElmSectorResult(sector=pick.sector)
    elm_curate.finalize(data, pick.sector, pick.projectile, result)
    if len(result.records) != 1:
        raise RuntimeError(f"{pick}: curation gave {len(result.records)} records ({result.dropped})")
    rec = result.records[0].payload
    rec["corpus"] = "sm3"
    rec["notes"] = list(rec.get("notes") or []) + [f"curated from EXFOR for sm3 ({pick.reference})"]
    return rec, result.bibtex.get(entry_id)


def main():
    by_sector: dict[str, list[serialize.Record]] = {s: [] for s in sm3.SECTORS}
    bib: dict[str, dict[str, str]] = {s: {} for s in sm3.SECTORS}
    for target, picks in sm3.SELECTION.items():
        for pick in picks:
            rec, b = (curated if pick.source == "exfor" else copied)(pick, target)
            by_sector[pick.sector].append(serialize.Record(target=target, payload=rec))
            if b:
                bib[pick.sector][pick.subentry[:5]] = b
            print(f"{serialize.target_filename(target):7s} {pick.sector:16s} {pick.projectile:8s} "
                  f"{pick.subentry} {pick.energy:7.3f}  {len(rec['data']['x']):3d} pts  from {pick.source}")
    for sector, records in by_sector.items():
        out = serialize.write_sector(records, corpus="sm3", sector=sector, bibtex=bib[sector])
        print(f"wrote {out} ({len(records)} measurements)")
    print("missing from EXFOR:", *sm3.MISSING, sep="\n  ")


if __name__ == "__main__":
    main()
