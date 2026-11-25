#!/usr/bin/env python3
"""Survey of the data available for the ELM-light corpus (read-only; docs/ELM_LIGHT_DATA.md).

For every ELM-light target (spec.ELM_LIGHT_TARGETS), the natural targets mapped to them (spec.ELM_LIGHT_NATURAL),
and for information the natural targets the ~99 % rule excludes (natNe, natMg, natSi, natS), counts what EXFOR
holds per observable, and what the tabulated corpora (kduq, test, chuq) already curate:

    nn, pp        elastic dsigma/dOmega (pp: ratio to Rutherford or absolute), 0-200 MeV, >= 5 points
    nAy, pAy      elastic analyzing power, 0-200 MeV, >= 5 points
    pn            (p,n) to the isobaric analog state (spec.ELM_LIGHT_EX_IAS, +-0.3 MeV), 5-200 MeV, >= 1 point
    ntot          neutron total cross section (n,tot), 0.1-200 MeV
    pR            proton reaction cross section: EXFOR (p,non) and (p,R), 0.1-200 MeV

Nothing is curated or written to data/. Output: a markdown table (stdout or --out) and a CSV (--csv).

    source scripts/setup_exfor_db.sh 2025
    python scripts/survey_elm_light.py --out docs/elm_light_survey.md --csv docs/elm_light_survey.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from exfor_tools import curate as exfor_curate  # noqa: E402
from exfor_tools.reaction import Reaction  # noqa: E402

from nn_corpora import spec  # noqa: E402

SYMBOL = {6: "C", 8: "O", 10: "Ne", 12: "Mg", 14: "Si", 16: "S", 18: "Ar"}
#: natural targets outside the ~99 % rule, surveyed for information only
NATURAL_INFO = ((0, 10), (0, 12), (0, 14), (0, 16))
OBSERVABLES = ("nn", "pp", "nAy", "pAy", "pn", "ntot", "pR")
#: tabulated-corpus sector -> survey observable
CORPUS_SECTORS = {"neutron_elastic": "nn", "proton_elastic": "pp", "neutron_ay": "nAy", "proton_ay": "pAy",
                  "neutron_total": "ntot", "proton_reaction": "pR"}
N, P = (1, 0), (1, 1)


def label(t):
    A, Z = t
    return f"nat{SYMBOL[Z]}" if A == 0 else f"{A}{SYMBOL[Z]}"


class _Query:
    """MultiQuantityReactionData without its all-or-nothing failure: an entry that raises while being parsed (x4i3
    errors on some malformed entries) is counted as unparsed instead of aborting the query."""

    def __init__(self, reaction, quantities, settings):
        from types import SimpleNamespace
        from exfor_tools.exfor_entry import ExforEntry
        from exfor_tools.reaction import query_for_reaction
        self.data = {}
        for q in quantities:
            ok, bad = {}, {}
            for eid in query_for_reaction(reaction, q):
                if eid in ("11848",):  # exfor_tools.curate.query_for_entries skips it too
                    continue
                try:
                    e = ExforEntry(eid, reaction, q, **settings)
                except Exception:  # noqa: BLE001 - counted as unparsed
                    bad[eid] = None
                    continue
                if e.failed_parses:
                    bad[eid] = e
                elif e.measurements:
                    ok[eid] = e
            self.data[q] = SimpleNamespace(entries=ok, failed_parses=bad)
        if {"dXS/dA", "dXS/dRuth"} <= set(quantities):  # keep the ratio where both forms exist, as curation does
            exfor_curate.remove_duplicates(*reaction.target, self.data["dXS/dRuth"].entries,
                                           self.data["dXS/dA"].entries)


def angular(target, projectile, quantities, einc, min_pts, ex_range=None, product=None):
    settings = {"Einc_range": list(einc), "filter_kwargs": {"min_num_pts": min_pts, "allow_cos": True,
                                                            "filter_lab_angle": False}}
    if ex_range is None:
        settings["elastic_only"] = True
        rxn = Reaction(target=target, projectile=projectile, process="el")
    else:
        settings["Ex_range"] = list(ex_range)
        A, Z = target
        rxn = Reaction(target=target, projectile=projectile, product=product, residual=(A, Z + 1))
    return _Query(rxn, quantities, settings)


def integral(target, projectile, process):
    return _Query(Reaction(target=target, projectile=projectile, process=process), ["XS"],
                  {"filter_kwargs": {"min_num_pts": 1}})


def summarise(datas, emin=None, emax=None, min_pts=1):
    """{entries, sets, points, emin, emax, failed} over MultiQuantityReactionData objects; angular sets with
    fewer than min_pts points are not counted (the query filter does not catch every one)."""
    entries, sets, pts, es, failed = set(), 0, 0, [], set()
    for d in datas:
        for q, re_ in d.data.items():
            failed |= set(re_.failed_parses)
            for eid, entry in re_.entries.items():
                for m in entry.measurements:
                    if hasattr(m, "Einc"):  # angular distribution: one set per energy
                        if int(m.rows) < min_pts:
                            continue
                        e = np.array([float(m.Einc)])
                    else:  # energy distribution: keep the points inside the window
                        e = np.asarray(m.x, dtype=float)
                        if emin is not None:
                            e = e[(e >= emin) & (e <= emax)]
                        if e.size == 0:
                            continue
                    entries.add(eid)
                    sets += 1
                    pts += int(m.rows) if hasattr(m, "Einc") else int(e.size)
                    es.extend(e.tolist())
    return dict(entries=len(entries), sets=sets, points=pts, emin=min(es) if es else None,
                emax=max(es) if es else None, failed=len(failed), failed_ids=sorted(failed))


def survey_exfor(t):
    out = {}
    el = spec.ELM_LIGHT_ELASTIC_EINC_RANGE
    out["nn"] = summarise([angular(t, N, ("dXS/dA",), el, spec.ELM_MIN_NUM_PTS)], min_pts=spec.ELM_MIN_NUM_PTS)
    out["pp"] = summarise([angular(t, P, ("dXS/dRuth", "dXS/dA"), el, spec.ELM_MIN_NUM_PTS)], min_pts=spec.ELM_MIN_NUM_PTS)
    out["nAy"] = summarise([angular(t, N, ("Ay",), el, spec.ELM_MIN_NUM_PTS)], min_pts=spec.ELM_MIN_NUM_PTS)
    out["pAy"] = summarise([angular(t, P, ("Ay",), el, spec.ELM_MIN_NUM_PTS)], min_pts=spec.ELM_MIN_NUM_PTS)
    if t in spec.ELM_LIGHT_EX_IAS:
        ex = spec.ELM_LIGHT_EX_IAS[t]
        w = spec.ELM_IAS_WINDOW
        out["pn"] = summarise([angular(t, P, ("dXS/dA",), spec.ELM_LIGHT_PN_EINC_RANGE, 1,
                                       ex_range=(ex - w, ex + w), product=N)])
    lo, hi = spec.ELM_LIGHT_INTEGRAL_EINC_RANGE
    out["ntot"] = summarise([integral(t, N, "tot")], lo, hi)
    out["pR"] = summarise([integral(t, P, "non"), integral(t, P, "R")], lo, hi)
    return out


def survey_corpora(t):
    """{observable: {corpus: sets}} from data/<corpus>/<sector>/<Sym>_<A>.json."""
    out = {}
    stem = f"{SYMBOL[t[1]]}_{t[0]}"
    for corpus in ("kduq", "test", "chuq"):
        for sector, obs in CORPUS_SECTORS.items():
            f = spec.DATA_DIR / corpus / sector / f"{stem}.json"
            if f.exists():
                n = len(json.loads(f.read_text()))
                out.setdefault(obs, {})[corpus] = n
    return out


def cell(s):
    if s is None:
        return "—"
    if not s["sets"]:
        return "0" + (f" ({s['failed']} unparsed)" if s["failed"] else "")
    rng = f"{s['emin']:.3g}–{s['emax']:.3g}"
    return f"{s['entries']}/{s['sets']}/{s['points']} ({rng})" + (f", {s['failed']} unparsed" if s["failed"] else "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--json", type=Path, help="raw results (incl. unparsed entry ids)")
    ap.add_argument("--only", nargs="*", help="labels, e.g. 12C natO")
    a = ap.parse_args()
    targets = list(spec.ELM_LIGHT_TARGETS) + list(spec.ELM_LIGHT_NATURAL) + list(NATURAL_INFO)
    if a.only:
        targets = [t for t in targets if label(t) in a.only]
    res = {}
    for t in targets:
        print(f"surveying {label(t)} ...", file=sys.stderr, flush=True)
        res[label(t)] = dict(target=t, exfor=survey_exfor(t), corpora=survey_corpora(t))
    head = ("EXFOR cells: entries/sets/points (energy span, MeV); 'unparsed': entries exfor_tools failed to parse "
            "(curation may recover them). Corpora: sets in kduq / test / chuq.")
    lines = [head, "", "| target | " + " | ".join(OBSERVABLES) + " | corpora |",
             "|---|" + "---|" * (len(OBSERVABLES) + 1)]
    for lab, r in res.items():
        t = r["target"]
        note = ""
        if t in spec.ELM_LIGHT_NATURAL:
            d, ab = spec.ELM_LIGHT_NATURAL[t]
            note = f" (→ {label(d)}, {100 * ab:.2f} %)"
        elif t in NATURAL_INFO:
            note = " (excluded: < 99 %)"
        corp = "; ".join(f"{o}: " + ", ".join(f"{c} {n}" for c, n in v.items()) for o, v in r["corpora"].items())
        lines.append(f"| {lab}{note} | " + " | ".join(cell(r["exfor"].get(o)) for o in OBSERVABLES)
                     + f" | {corp or '—'} |")
    text = "\n".join(lines) + "\n"
    if a.out:
        a.out.write_text(text)
    print(text)
    if a.csv:
        with a.csv.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["target", "observable", "entries", "sets", "points", "emin", "emax", "unparsed"])
            for lab, r in res.items():
                for o in OBSERVABLES:
                    s = r["exfor"].get(o)
                    if s:
                        w.writerow([lab, o, s["entries"], s["sets"], s["points"], s["emin"], s["emax"], s["failed"]])
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
