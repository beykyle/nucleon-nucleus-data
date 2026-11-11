#!/usr/bin/env python3
"""Curate the ELM-light corpus (data/elm_light; docs/ELM_LIGHT_DATA.md).

Sectors, as the ELM corpus (notebooks/elm, scripts/curate_elm_integral.py):

    elastic_diff_xs   (n,n) dsigma/dOmega and (p,p) ratio to Rutherford, 0-200 MeV, >= 5 angles
    elastic_ay        n and p analysing powers, 0-200 MeV, >= 5 angles
    charge_exchange   (p,n) to the isobaric analog state, 5-200 MeV, IAS +- 0.3 MeV (spec.ELM_LIGHT_EX_IAS)
    neutron_total     sigma_tot (n,tot), 0.1-200 MeV, every point (no thinning)
    proton_reaction   sigma_R (p,non), 0.1-200 MeV

on spec.ELM_LIGHT_TARGETS, plus natural C, O and Ar treated as 12C, 16O and 40Ar (spec.ELM_LIGHT_NATURAL; other
natural targets are not used). Decisions: nn_corpora.elm_light. Records pass through the author-error and ELM
evaluations (serialize.write_sector). Writes data/elm_light/<sector>/ and docs/elm_light_curation_report.txt; with
--plots, build/elm_light_plots.pdf (every angular distribution, for review; not committed).

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/curate_elm_light.py [--sectors ...] [--plots]

Next: scripts/talys_compound.py run/apply --corpus elm_light; scripts/build_manifests.py.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nn_corpora import author_errors, corpus, elm_curate, elm_evaluation, elm_light, serialize, spec  # noqa: E402
from nn_corpora.elm_light import CORPUS, label  # noqa: E402

SECTORS = ("elastic_diff_xs", "elastic_ay", "charge_exchange", "neutron_total", "proton_reaction")
REPORT = REPO_ROOT / "docs" / "elm_light_curation_report.txt"
QUERY_TARGETS = list(spec.ELM_LIGHT_TARGETS) + list(spec.ELM_LIGHT_NATURAL)


def finalize_with_natural(data, sector, projectile, result):
    iso, nat = elm_light.split_natural(data)
    elm_curate.finalize(iso, sector, projectile, result, corpus=CORPUS)
    n0 = len(result.records)
    elm_curate.finalize(nat, sector, projectile, result, corpus=CORPUS)
    elm_light.mark_natural(result.records[n0:])


def curate_elastic(sector: str):
    result = elm_curate.ElmSectorResult(sector=sector)
    if sector == "elastic_diff_xs":
        plan = (("neutron", ("dXS/dA",), {"dXS/dA": elm_light.EXCLUDED_NN}),
                ("proton", ("dXS/dA", "dXS/dRuth"), {"dXS/dA": elm_light.EXCLUDED_PP_ABSOLUTE,
                                                     "dXS/dRuth": elm_light.EXCLUDED_PP_RUTHERFORD}))
    else:
        plan = (("neutron", ("Ay",), {}), ("proton", ("Ay",), {"Ay": elm_light.EXCLUDED_AY}))
    for proj, quantities, exclusions in plan:
        data = elm_curate.query_elastic(spec.PROJECTILES[proj], quantities, QUERY_TARGETS,
                                        spec.ELM_LIGHT_ELASTIC_EINC_RANGE, spec.ELM_MIN_NUM_PTS)
        elm_curate.repair_failed_parses(data, quantities, result)
        elm_light.repair_by_supplement_rule(data, quantities, result)
        for q, excl in exclusions.items():
            elm_curate.exclude_entries(data, q, excl, result)
        elm_light.record_failed_parses(data, result, proj)
        finalize_with_natural(data, sector, proj, result)
        result.data.update({t: m for t, m in data.items() if t[0] != 0})
    result.records = elm_light.apply_manual_drops(result.records, result)
    return result


def curate_pn():
    result = elm_curate.ElmSectorResult(sector="charge_exchange")
    targets = spec.elm_light_pn_targets()
    pn = elm_curate.query_pn(targets, spec.ELM_LIGHT_PN_EINC_RANGE, spec.ELM_IAS_WINDOW,
                             ex_ias=spec.ELM_LIGHT_EX_IAS)
    elm_curate.repair_failed_parses(pn, ("dXS/dA",), result)
    elm_light.repair_by_supplement_rule(pn, ("dXS/dA",), result)
    elm_curate.exclude_entries(pn, "dXS/dA", elm_light.EXCLUDED_PN, result)
    elm_light.exclude_pn_by_target(pn, result)
    elm_light.record_failed_parses(pn, result, "proton")
    elm_curate.finalize(pn, "charge_exchange", "proton", result, corpus=CORPUS)
    result.data = dict(pn)
    result.records = elm_light.drop_pn_not_ias(result.records, result)
    result.records = elm_light.apply_manual_drops(result.records, result)
    return result


def curate_integral(sector: str, vocal: bool = False):
    rows = elm_light.integral_rows(sector, QUERY_TARGETS)
    load, thin = corpus.load_sector, corpus.NEUTRON_TOTAL_POINTS_PER_MEV
    corpus.NEUTRON_TOTAL_POINTS_PER_MEV = 1e9  # keep every point, as ELM (curate_elm_integral.py)
    corpus.load_sector = lambda c, s, _rows=rows: _rows
    try:
        res = corpus.curate(CORPUS, sector, vocal=vocal)
    finally:
        corpus.load_sector, corpus.NEUTRON_TOTAL_POINTS_PER_MEV = load, thin
    out = elm_curate.ElmSectorResult(sector=sector)
    out.dropped += elm_light.SKIPPED_ROWS
    elm_light.SKIPPED_ROWS.clear()
    for o in res.data.unresolved:
        out.dropped.append(f"{o.row.subentry} ({o.row.target_label}): not retrieved: {o.reason}")
    for _, sub, why in res.dropped:
        out.dropped.append(f"{sub}: {why}")
    natural = []
    for r in res.records:
        t = tuple(r.target)
        if t[0] == 0:
            if t not in spec.ELM_LIGHT_NATURAL:
                out.dropped.append(f"{r.payload['EXFORAccessionNumber']}: natural {r.payload['target']}, not "
                                   "~99 % one isotope (spec.ELM_LIGHT_NATURAL)")
                continue
            iso = spec.ELM_LIGHT_NATURAL[t][0]
            r.target = iso
            r.payload["target"] = serialize.get_exfor_particle_symbol(*iso)
            natural.append(r)
        elif t not in spec.ELM_LIGHT_TARGETS:
            out.dropped.append(f"{r.payload['EXFORAccessionNumber']}: EXFOR target {r.payload['target']} is not an "
                               "ELM-light target")
            continue
        out.records.append(r)
    elm_light.mark_natural(natural)
    elm_light.cut_point_energies(out.records, out)
    out.data = {tuple(r.target): None for r in out.records}
    out.bibtex = {e: x.bibtex() for e, x in res.data.entries.items() if res.data.measurements.get(e)}
    out.records = elm_light.apply_manual_drops(out.records, out)
    return out


SPARSE = "too sparse to constrain an optical potential"


def compact_summary(res) -> str:
    """res.summary(), with the too-sparse drops (mostly excitation functions at 1-4 angles, one record per energy)
    collapsed to one line per subentry."""
    sparse = Counter(d.split(":")[0] for d in res.dropped if SPARSE in d)
    keep = [d for d in res.dropped if SPARSE not in d]
    dropped, res.dropped = res.dropped, keep
    text = res.summary().replace("elm/", f"{CORPUS}/", 1)
    res.dropped = dropped
    if sparse:
        text += (f"\n  dropped as {SPARSE} (< {spec.ELM_MIN_NUM_PTS} angles): {sum(sparse.values())} measurements of "
                 f"{len(sparse)} subentries\n" + "\n".join(f"    {s}: {n}" for s, n in sorted(sparse.items())))
    return text


def unused_drop_keys(results) -> list[str]:
    """Drop-table keys that matched no record (EXFOR re-numbered or re-rounded): checked by subentry and energy."""
    text = "\n".join(s for res in results.values() for s in res.dropped + res.excluded)
    out = [f"MANUAL_DROPS {k}" for k in elm_light.MANUAL_DROPS if k not in text]
    for name in ("MANUAL_RECORD_DROPS", "READER_ONLY_DROPS", "BELOW_AUTHOR_DROPS", "VALUE_KEYED_DROPS",
                 "PN_NOT_IAS_RECORDS"):
        for k in getattr(elm_light, name):
            if f"{k[0]} ({label(_target_of(k[0], results))} {k[1]}" not in text and \
                    f"{k[0]} ({label(_target_of(k[0], results))} {k[1]} MeV" not in text:
                out.append(f"{name} {k}")
    for (t, entry), _ in elm_light.EXCLUDED_PN_BY_TARGET.items():
        if f"{entry} ({label(t)})" not in text:
            out.append(f"EXCLUDED_PN_BY_TARGET {label(t)} {entry}")
    out += [f"POINT_ENERGY_MAX {k}" for k in elm_light.POINT_ENERGY_MAX if f"{k}: " not in "\n".join(
        s for res in results.values() for s in res.repaired)]
    return out


def _target_of(sub, results):
    for res in results.values():
        for r in res.records:
            if r.payload["EXFORAccessionNumber"] == sub:
                return tuple(r.target)
    for res in results.values():  # dropped: the target is in its message
        for s in res.dropped + res.excluded:
            if s.startswith(sub + " ("):
                stem = s.split("(")[1].split(" ")[0].rstrip(")")
                sym, A = stem.split("_")
                Z = {v: k for k, v in {6: "C", 8: "O", 10: "Ne", 12: "Mg", 14: "Si", 16: "S", 18: "Ar"}.items()}[sym]
                return (int(A), Z)
    return (0, 6)


def counts_table(results) -> list[str]:
    c = defaultdict(lambda: [0, 0])
    for res in results.values():
        for r in res.records:
            key = {"elastic_diff_xs": "{p}{p}", "elastic_ay": "{p}Ay", "charge_exchange": "pn",
                   "neutron_total": "σtot", "proton_reaction": "σR"}[res.sector].format(p=r.payload["projectile"][0])
            c[(r.target, key)][0] += 1
            c[(r.target, key)][1] += len(r.payload["data"]["x"])
    cols = ["nn", "pp", "nAy", "pAy", "pn", "σtot", "σR"]
    lines = ["| target | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for t in sorted({t for t, _ in c}, key=lambda t: (t[1], t[0])):
        lines.append(f"| {label(t)} | " + " | ".join(f"{c[(t, k)][0]}/{c[(t, k)][1]}" if (t, k) in c else "—"
                                                     for k in cols) + " |")
    return lines


def plot(records, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    groups = defaultdict(list)
    for r in records:
        groups[(r.target[1], r.target[0], r.payload["sector"], r.payload["projectile"])].append(r.payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(path) as pdf:
        for (Z, A, sector, proj), L in sorted(groups.items()):
            integral = sector in ("neutron_total", "proton_reaction")
            L = sorted(L, key=lambda p: (float(p.get("energy", 0)), p["EXFORAccessionNumber"]))
            per = 40 if integral else 12
            for start in range(0, len(L), per):
                chunk = L[start:start + per]
                fig, ax = plt.subplots(figsize=(7, 9))
                for k, p in enumerate(chunk):
                    x, y, e = (np.asarray(p["data"][c], dtype=float) for c in ("x", "y", "y_err"))
                    s = 1.0 if integral else 10.0 ** (-k) if sector != "elastic_ay" else None
                    if sector == "elastic_ay":
                        ax.errorbar(x, y - 2 * k, e, fmt=".", ms=3, lw=0.8)
                        ax.annotate(f"{p['energy']:g} {p['EXFORAccessionNumber']}", (x[-1], y[-1] - 2 * k),
                                    fontsize=6)
                    else:
                        ax.errorbar(x, y * s, e * s, fmt=".", ms=2 if integral else 3, lw=0.6,
                                    label=p["EXFORAccessionNumber"] if integral else None)
                        if not integral:
                            ax.annotate(f"{p['energy']:g} MeV {p['EXFORAccessionNumber']}", (x[-1], y[-1] * s),
                                        fontsize=6)
                if integral:
                    ax.set_xscale("log")
                    ax.legend(fontsize=5, ncol=3)
                    ax.set_xlabel("E (MeV)")
                elif sector != "elastic_ay":
                    ax.set_yscale("log")
                    ax.set_xlabel(r"$\theta_{cm}$ (deg)")
                else:
                    ax.set_xlabel(r"$\theta_{cm}$ (deg)")
                ax.set_title(f"{label((A, Z))} {proj} {sector} ({start + 1}-{start + len(chunk)} of {len(L)})")
                pdf.savefig(fig)
                plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sectors", nargs="*", default=list(SECTORS), choices=SECTORS)
    ap.add_argument("--plots", action="store_true")
    ap.add_argument("--no-write", action="store_true", help="curate and report only")
    a = ap.parse_args()

    results = {}
    for sector in a.sectors:
        print(f"curating {sector} ...", flush=True)
        if sector in ("elastic_diff_xs", "elastic_ay"):
            results[sector] = curate_elastic(sector)
        elif sector == "charge_exchange":
            results[sector] = curate_pn()
        else:
            results[sector] = curate_integral(sector)
        res = results[sector]
        # the evaluations write_sector applies (both idempotent), applied here so the report counts what is written
        n0 = len(res.records)
        res.records = elm_evaluation.apply(author_errors.apply(res.records, CORPUS, sector), CORPUS, sector)
        if len(res.records) < n0:
            res.dropped.append(f"{n0 - len(res.records)} record(s) removed by the author-error / ELM evaluations")
        print(compact_summary(res), flush=True)
        if not a.no_write:
            serialize.write_sector(res.records, corpus=CORPUS, sector=sector, bibtex=res.bibtex)
    unused = unused_drop_keys(results)
    report = ["# ELM-light curation report (scripts/curate_elm_light.py)", "",
              f"EXFOR {serialize.exfor_database_tag()}", ""]
    report += ["## records / points per target", ""] + counts_table(results) + [""]
    for res in results.values():
        report += [compact_summary(res), ""]
    all_records = [r for res in results.values() for r in res.records]
    dups = elm_light.near_duplicates(all_records)
    report += ["## same target/projectile/sector/energy, different EXFOR entries", ""]
    report += [f"  [{v}] {s}" for v, s in dups if v == "LIKELY DUPLICATE"]
    report += [f"  ({sum(v != 'LIKELY DUPLICATE' for v, _ in dups)} further pairs judged distinct: "
               "elm_light.near_duplicates)"]
    if "charge_exchange" in results:
        report += ["", "## (p,n) records whose final state is not tabulated within 50 keV of the IAS", ""]
        report += elm_light.pn_final_state_report(results["charge_exchange"].records) or ["  none"]
    report += ["", "## summed (quasi-elastic) records", ""]
    for r in all_records:
        b = r.payload.get("summed_excitation_max_mev") or r.payload.get("summed_excitation_max_MeV")
        if b is not None:
            ok = "below" if b < elm_light.FIRST_EXCITED[r.target] else "ABOVE"
            report.append(f"  {label(r.target)} {r.payload['EXFORAccessionNumber']} {r.payload.get('energy')}: bound "
                          f"{b} MeV, {ok} first excited state {elm_light.FIRST_EXCITED[r.target]} MeV")
    if set(a.sectors) == set(SECTORS):
        report += ["", "## drop-table keys matching no record", ""] + ([f"  {u}" for u in unused] or ["  none"])
    n_dup = Counter(v for v, _ in dups)["LIKELY DUPLICATE"]
    report += ["", f"{len(all_records)} records; {n_dup} likely-duplicate pairs to review"]
    if not a.no_write:
        REPORT.write_text("\n".join(report) + "\n")
        print(f"wrote {REPORT}")
    print("\n".join(report[:40]))
    if a.plots:
        out = REPO_ROOT / "build" / "elm_light_plots.pdf"
        plot(all_records, out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
