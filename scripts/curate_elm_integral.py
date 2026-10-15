#!/usr/bin/env python3
"""Curate ELM's angle-integrated sectors: isotopic neutron total and proton reaction cross sections.

The supplement corpora (test, kduq) already list EXFOR subentries of these observables. This script takes the rows
for ELM's near-spherical targets (``spec.elm_targets()``: isotopic, beta2 < MAX_BETA2) and curates them for ELM with
two differences from those corpora:

* the energy window is 0.1-200 MeV (``E_RANGE``), not the supplement's tabulated range;
* only isotopic measurements: a row listed under an isotope can resolve to a natural-element measurement;
* neutron total cross sections are not thinned to one point per MeV: the low-energy points (resonance region) are
  kept, and how a calibration energy-averages them is the calibration's choice (Lorentz smoothing).

Records go through the ELM evaluation like every ELM record (``serialize.write_sector``: author errors, excluded
targets, error floor) and are written to data/elm/{neutron_total,proton_reaction}.

Usage::

    source scripts/setup_exfor_db.sh 2025
    uv run python scripts/curate_elm_integral.py
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
from nn_corpora import corpus, serialize, spec  # noqa: E402

SOURCES = ("test", "kduq")
SECTORS = ("neutron_total", "proton_reaction")
#: from 0.1 MeV: below it the total cross sections are resolved resonances (transmission dips to zero and below at
#: 13 keV in 90Zr, 13736003), which no energy-averaged optical model describes
E_RANGE = (0.1, 200.0)


def elm_rows(sector: str) -> list:
    targets = set(spec.elm_targets())
    rows, seen = [], set()
    for src in SOURCES:
        for r in spec.load_sector(src, sector):
            t = (r.target_A, r.target_Z)
            if t not in targets or r.subentry in seen:
                continue
            seen.add(r.subentry)
            rows.append(dataclasses.replace(r, corpus="elm", energy_mev=E_RANGE[0], energy_hi_mev=E_RANGE[1]))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vocal", action="store_true")
    a = ap.parse_args()
    corpus.NEUTRON_TOTAL_POINTS_PER_MEV = 1e9  # keep every point (no thinning)
    for sector in SECTORS:
        rows = elm_rows(sector)
        print(f"{sector}: {len(rows)} subentries: " + ", ".join(f"{r.target_label} {r.subentry}" for r in rows))
        corpus.load_sector = lambda c, s, _rows=rows: _rows  # the ELM rows instead of a tabulated spec
        result = corpus.curate("elm", sector, vocal=a.vocal)
        natural = [r for r in result.records if r.target[0] == 0]
        result.records = [r for r in result.records if r.target[0] != 0]
        for r in natural:
            print(f"  dropped {r.payload['EXFORAccessionNumber']}: natural {r.payload['target']}, not isotopic")
        print(result.summary())
        out = serialize.write_sector(result.records, corpus="elm", sector=sector)
        print(f"wrote {out}")
    print("next: scripts/build_manifests.py; scripts/talys_compound.py run/apply --sector proton_reaction")


if __name__ == "__main__":
    main()
