#!/usr/bin/env python3
"""Compound-elastic corrections from TALYS for a curated corpus sector.

The optical model describes the direct (shape) elastic scattering; measured elastic cross sections also contain
compound-nucleus elastic scattering (CE), which matters at low energy and back angles. This script computes CE with
TALYS (the git submodule external/talys) and writes a "direct-only" copy of a sector, which calibrations use:

    elastic angular data:      direct = measured - CE(theta)
    proton reaction (nonelastic) cross sections:   sigma_R(OM) = sigma_nonel + sigma_CE   (CE is part of the OM
                                                   absorption, but not of the measured nonelastic cross section)
    neutron total cross sections: no correction (sigma_tot = sigma_SE + sigma_R(OM) already contains CE)

Usage::

    uv run python scripts/talys_compound.py build                       # init the submodule, compile, smoke test
    uv run python scripts/talys_compound.py run --sector elastic_diff_xs [--targets Ca_40 ...] [--workers 8]
    uv run python scripts/talys_compound.py apply --sector elastic_diff_xs

``run`` writes TALYS's parsed results per system (projectile, target) to compound_elastic/<corpus>/<sector>/<proj>_<Target>/:
angular.csv (E, angle_cm, xs, direct, compound, ratio_rutherford) and integral.csv (E, compound_elastic,
shape_elastic, reaction, total, nonelastic), plus talys.inp and meta.json (TALYS commit, settings). Raw TALYS output
stays in a scratch directory. ``apply`` reads those and writes data/<corpus>/<sector>_direct/ (same file layout and
records, with data.y the direct-only value, data.y_measured, data.compound_elastic, data.ce_fraction (CE / measured),
data.talys_model (TALYS's elastic or sigma_R at the data points), data.ce_fraction_model (CE / talys_model),
data.y_err_before_compound, data.compound_uncertainty and y_err = sqrt(y_err^2 + (CE_UNCERTAINTY * CE)^2)).

TALYS settings: defaults, plus ``outangle y`` and ``fileelastic y`` (elastic angular distributions with the compound
part angle-dependent from Hauser-Feshbach Legendre coefficients, up to 50 MeV; isotropic above) and, for protons,
``cpang y`` (angle-dependent compound elastic for charged particles).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
from nn_corpora import serialize, spec  # noqa: E402

TALYS = REPO_ROOT / "external" / "talys"
CACHE = REPO_ROOT / "compound_elastic"  # parsed TALYS results, outside data/ (not corpus records)
CE_UNCERTAINTY = 0.30  # fractional uncertainty of the TALYS compound elastic, added in quadrature
PROJ = {"neutron": ("n", "nn"), "proton": ("p", "pp")}
SMOKE = Path(os.environ.get("JITR_TALYS_REGRESSION", Path.home() / "jitr-jax-core/tests/regression/talys"))


# -- build ----------------------------------------------------------------------------------------------------------
def talys_bin() -> Path:
    return TALYS / "bin" / "talys"


def talys_env() -> dict:
    env = dict(os.environ)
    env["TALYS_DIR"] = str(TALYS) + "/"
    env["PATH"] = f"{TALYS / 'bin'}:{env.get('PATH', '')}"
    return env


def build(args) -> None:
    if not (TALYS / "source").exists():
        subprocess.run(["git", "submodule", "update", "--init", "--depth", "1", "external/talys"], cwd=REPO_ROOT,
                       check=True)
    if not talys_bin().exists() or args.rebuild:
        fc = os.environ.get("FC", "gfortran")
        (TALYS / "bin").mkdir(exist_ok=True)
        subprocess.run(["make", f"FC={fc}"], cwd=TALYS / "source", check=True)
    if not (TALYS / "structure" / "abundance" / "H.abun").exists():
        raise SystemExit(f"TALYS structure database missing under {TALYS / 'structure'}")
    print(f"TALYS binary {talys_bin()} (commit {talys_commit()})")
    smoke_test()


def talys_commit() -> str:
    r = subprocess.run(["git", "-C", str(TALYS), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def smoke_test() -> None:
    """n + 120Sn at 10 MeV with the JLM potential (jitr regression case T1): Direct within 10 % of the stored one."""
    inp = SMOKE / "inputs" / "T1_jlm_elastic.inp"
    ref = SMOKE / "reference" / "T1_jlm_elastic.csv"
    if not inp.exists():
        print(f"smoke test skipped: {inp} not found (set JITR_TALYS_REGRESSION)")
        return
    with tempfile.TemporaryDirectory() as d:
        for f in inp.parent.glob("T1_jlm_elastic.*"):
            shutil.copy(f, d)
        subprocess.run(f"{talys_bin()} < T1_jlm_elastic.inp > talys.out", shell=True, cwd=d, env=talys_env(),
                       check=True)
        ang = parse_table(Path(d) / "nn0010.000ang.L00")
    lines = [l for l in ref.read_text().splitlines() if l.strip() and not l.startswith("#")][1:]  # comments, header
    r = np.loadtxt(lines, delimiter=",", ndmin=2)
    direct = np.interp(r[:, 0], ang["angle"], ang["direct"])
    dev = np.max(np.abs(direct / r[:, 1] - 1))
    print(f"smoke test (jitr T1, n+120Sn 10 MeV JLM): max |Direct/reference - 1| = {dev:.3g}")
    if dev > 0.10:
        raise SystemExit("smoke test FAILED")


# -- TALYS output parsing ---------------------------------------------------------------------------------------------
def parse_table(path: Path) -> dict[str, np.ndarray]:
    """A TALYS YANDF table: the '##' header line names the columns; numeric rows follow."""
    names, rows = None, []
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.startswith("##") and names is None:
            names = [n.lower() for n in s.lstrip("#").split()]
            continue
        if names is None or not s or s.startswith("#"):
            continue
        try:
            rows.append([float(v) for v in s.split()])
        except ValueError:
            continue
    if names is None:
        raise ValueError(f"{path}: no column header")
    a = np.array(rows)
    key = {"angle": "angle", "xs": "xs", "direct": "direct", "compound": "compound", "xs/rutherford": "ratio_rutherford"}
    if "angle" in names:
        return {key.get(n, n): a[:, i] for i, n in enumerate(names[: a.shape[1]])}
    return {n: a[:, i] for i, n in enumerate(names[: a.shape[1]])}


def parse_all_tot(path: Path) -> dict[str, np.ndarray]:
    """all.tot: E, Non-elastic, Elastic, Total, Compound_elast., Shape_elastic, Reaction, ... (mb)."""
    t = parse_table(path)
    cols = list(t)
    want = {"e": 0, "nonelastic": 1, "elastic": 2, "total": 3, "compound_elastic": 4, "shape_elastic": 5, "reaction": 6}
    return {k: t[cols[i]] for k, i in want.items()}


# -- run ------------------------------------------------------------------------------------------------------------
def energy_tag(E: float) -> str:
    return f"{int(E):04d}.{round((E - int(E)) * 1000):03d}"


def systems(corpus: str, sector: str, targets=None) -> dict:
    """{(projectile, target file stem): sorted energies} for the angular records of a corpus sector."""
    out = {}
    for path in sorted((spec.DATA_DIR / corpus / sector).glob("*.json")):
        if targets and path.stem not in targets:
            continue
        for rec in json.loads(path.read_text()):
            if "energy" in rec:
                Es = [float(rec["energy"])]
            else:  # energy distributions: their x
                Es = [float(e) for e in rec["data"]["x"]]
            out.setdefault((rec["projectile"], path.stem), set()).update(round(e, 3) for e in Es if e > 0)
    return {k: sorted(v) for k, v in out.items()}


def talys_input(projectile: str, stem: str, angular: bool) -> str:
    sym, A = stem.split("_")
    p = PROJ[projectile][0]
    lines = [f"projectile {p}", f"element {sym.lower()}", f"mass {int(A)}", "energy energies", "filetotal y"]
    if angular:
        lines += ["outangle y", "fileelastic y"] + (["cpang y"] if p == "p" else [])
    return "\n".join(lines) + "\n"


def talys_dir(corpus: str, sector: str, proj: str, stem: str) -> Path:
    """Parsed TALYS results for one system, per sector (each sector's run has its own energies)."""
    return CACHE / corpus / sector / f"{proj}_{stem}"


def run_system(task) -> tuple[str, str]:
    corpus, sector, projectile, stem, energies, angular = task
    out = talys_dir(corpus, sector, PROJ[projectile][0], stem)
    out.mkdir(parents=True, exist_ok=True)
    inp = talys_input(projectile, stem, angular)
    with tempfile.TemporaryDirectory(prefix=f"talys_{stem}_") as d:
        Path(d, "talys.inp").write_text(inp)
        Path(d, "energies").write_text("\n".join(f"{e:.3f}" for e in energies) + "\n")
        r = subprocess.run(f"{talys_bin()} < talys.inp > talys.out", shell=True, cwd=d, env=talys_env())
        if r.returncode != 0:
            return stem, f"TALYS failed (exit {r.returncode})"
        tot = parse_all_tot(Path(d) / "all.tot")
        with open(out / "integral.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["E_MeV", "compound_elastic_mb", "shape_elastic_mb", "reaction_mb", "total_mb", "nonelastic_mb"])
            for i in range(len(tot["e"])):
                w.writerow([f"{tot['e'][i]:.6g}"] + [f"{tot[k][i]:.6g}" for k in
                           ("compound_elastic", "shape_elastic", "reaction", "total", "nonelastic")])
        if angular:
            pref = PROJ[projectile][1]
            with open(out / "angular.csv", "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["E_MeV", "angle_cm_deg", "xs_mb_sr", "direct_mb_sr", "compound_mb_sr", "ratio_rutherford"])
                missing = []
                for e in energies:
                    f = Path(d) / f"{pref}{energy_tag(e)}ang.L00"
                    if not f.exists():
                        missing.append(e)
                        continue
                    t = parse_table(f)
                    rr = t.get("ratio_rutherford", np.full_like(t["angle"], np.nan))
                    for j in range(len(t["angle"])):
                        w.writerow([f"{e:.3f}", f"{t['angle'][j]:.4g}", f"{t['xs'][j]:.6g}", f"{t['direct'][j]:.6g}",
                                    f"{t['compound'][j]:.6g}", f"{rr[j]:.6g}"])
        shutil.copy(Path(d) / "talys.inp", out / "talys.inp")
    meta = dict(talys_commit=talys_commit(), projectile=projectile, target=stem, energies=energies,
                settings=inp.strip().splitlines(), missing_angular=missing if angular else [])
    (out / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return stem, f"{len(energies)} energies" + (f", missing angular {missing}" if angular and missing else "")


def run(args) -> None:
    if not talys_bin().exists():
        raise SystemExit("no TALYS binary: run  talys_compound.py build  first")
    angular = args.sector != "proton_reaction" and args.sector != "neutron_total"
    sysm = systems(args.corpus, args.sector, args.targets)
    tasks = [(args.corpus, args.sector, proj, stem, Es, angular) for (proj, stem), Es in sysm.items()]
    print(f"{len(tasks)} systems: " + ", ".join(f"{p[0]}+{s} ({len(E)} E)" for (p, s), E in sysm.items()))
    with ProcessPoolExecutor(args.workers) as ex:
        for f in as_completed([ex.submit(run_system, t) for t in tasks]):
            stem, msg = f.result()
            print(f"  {stem}: {msg}", flush=True)


# -- apply ----------------------------------------------------------------------------------------------------------
def load_angular(path: Path) -> dict[float, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    """{E: (angle_deg, compound_mb_sr, xs_mb_sr, ratio_rutherford)}."""
    out: dict = {}
    with open(path) as fh:
        for row in csv.DictReader(fh):
            e = round(float(row["E_MeV"]), 3)
            out.setdefault(e, []).append([float(row[k]) for k in ("angle_cm_deg", "compound_mb_sr", "xs_mb_sr",
                                                                  "ratio_rutherford")])
    return {e: tuple(np.array(v).T) for e, v in out.items()}


def talys_at(table, E: float, theta_deg: np.ndarray, ratio: bool) -> tuple[np.ndarray, np.ndarray]:
    """(CE, TALYS elastic) at the record angles, interpolated in cos(theta): mb/sr, or as ratios to Rutherford."""
    ang, ce, xs, rr = table[round(E, 3)]
    keep = (ang > 0) & np.isfinite(ce) & (xs < 1e30)
    c = np.cos(np.radians(ang[keep]))[::-1]
    at = np.cos(np.radians(theta_deg))
    out_ce, out_xs = np.interp(at, c, ce[keep][::-1]), np.interp(at, c, xs[keep][::-1])
    if ratio:  # the Rutherford cross section implied by TALYS: xs / (xs/Rutherford)
        ruth = np.interp(at, c, (xs[keep] / rr[keep])[::-1])
        out_ce, out_xs = out_ce / ruth, out_xs / ruth
    return out_ce, out_xs


def ce_at(table, E: float, theta_deg: np.ndarray, ratio: bool) -> np.ndarray:
    """CE at the record angles, interpolated in cos(theta): mb/sr, or as a ratio to Rutherford."""
    return talys_at(table, E, theta_deg, ratio)[0]


def apply(args) -> None:
    src = spec.DATA_DIR / args.corpus / args.sector
    dst = spec.DATA_DIR / args.corpus / f"{args.sector}_direct"
    dst.mkdir(exist_ok=True)
    for stale in dst.glob("*.json"):
        stale.unlink()
    n_rec = 0
    for path in sorted(src.glob("*.json")):
        out = []
        for rec in json.loads(path.read_text()):
            proj = PROJ[rec["projectile"]][0]
            base = talys_dir(args.corpus, args.sector, proj, path.stem)
            rec = json.loads(json.dumps(rec))
            d = rec["data"]
            y, e = np.asarray(d["y"], float), np.asarray(d["y_err"], float)
            if args.sector == "proton_reaction":
                t = np.loadtxt(base / "integral.csv", delimiter=",", skiprows=1, ndmin=2)
                ce = np.interp(np.asarray(d["x"], float), t[:, 0], t[:, 1]) / 1000.0  # mb -> b
                model = np.interp(np.asarray(d["x"], float), t[:, 0], t[:, 3]) / 1000.0  # TALYS sigma_R (OM)
                d["y"] = (y + ce).tolist()
                note = "reaction (OM) = measured nonelastic + TALYS compound elastic"
            else:
                table = load_angular(base / "angular.csv")
                ratio = str(rec.get("y_units", "")).lower() in ("no-dim", "", "arb-units") and rec["projectile"] == "proton"
                ce, model = talys_at(table, float(rec["energy"]), np.asarray(d["x"], float), ratio)
                if not ratio:
                    ce, model = ce / 1000.0, model / 1000.0  # mb/sr -> b/sr
                d["y"] = (y - ce).tolist()
                note = "direct (shape) elastic = measured - TALYS compound elastic"
            d["y_measured"] = y.tolist()
            d["compound_elastic"] = ce.tolist()
            d["ce_fraction"] = (np.abs(ce) / np.abs(y)).tolist()
            # TALYS's own elastic (measured-like: shape + compound) or sigma_R, and CE as a fraction of it: a model
            # quantity, so a cut on it does not select on the measured values (ce_fraction does)
            d["talys_model"] = model.tolist()
            d["ce_fraction_model"] = (np.abs(ce) / np.abs(model)).tolist()
            d["y_err_before_compound"] = e.tolist()
            d["compound_uncertainty"] = CE_UNCERTAINTY
            d["y_err"] = np.sqrt(e ** 2 + (CE_UNCERTAINTY * ce) ** 2).tolist()
            rec.setdefault("notes", []).append(
                f"{note} (TALYS {json.loads((base / 'meta.json').read_text())['talys_commit'][:7]}, default settings + "
                f"outangle/cpang; CE uncertainty {100 * CE_UNCERTAINTY:g} % in quadrature; scripts/talys_compound.py)")
            rec["sector"] = f"{args.sector}_direct"
            out.append(rec)
            n_rec += 1
        (dst / path.name).write_text(json.dumps(out, indent=4) + "\n")
    for bib in src.glob("*.bib"):
        shutil.copy(bib, dst / f"{args.sector}_direct.bib")
    print(f"wrote {dst} ({n_rec} records)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--rebuild", action="store_true")
    for name in ("run", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--corpus", default="elm")
        p.add_argument("--sector", required=True)
        if name == "run":
            p.add_argument("--targets", nargs="*")
            p.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    {"build": build, "run": run, "apply": apply}[a.cmd](a)


if __name__ == "__main__":
    main()
