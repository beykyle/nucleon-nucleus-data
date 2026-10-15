# ELM calibration data

`data/elm` is the data the ELM-family optical-model calibrations use, exactly. On top of the author-error evaluation
([AUTHOR_UNCERTAINTIES.md](AUTHOR_UNCERTAINTIES.md)) it carries three things, all decided on 2026-10-14 from the
data audit of the ELM-Lane calibration (`elm/calibrations/elm_lane/DATA_AUDIT.md`):

1. **The ELM calibration evaluation** ([src/nn_corpora/elm_evaluation.py](../src/nn_corpora/elm_evaluation.py)).
2. **Data from 0 MeV.** Elastic scattering is curated from 0 MeV (previously 10 MeV), and the corpus gains the
   isotopic angle-integrated observables.
3. **Compound-elastic-corrected copies** of the elastic and proton reaction sectors, computed with TALYS
   ([scripts/talys_compound.py](../scripts/talys_compound.py)).

## Sectors

| sector | contents | use in a calibration |
|---|---|---|
| `elastic_diff_xs` | (n,n) dσ/dΩ (b/sr) and (p,p) σ/σ_Ruth, 0–200 MeV, as measured | — (reference) |
| `elastic_diff_xs_direct` | the same records, compound elastic subtracted | elastic angular data |
| `elastic_ay` | analysing powers | as is |
| `charge_exchange` | (p,n) to the IAS, ≥ 22 MeV | as is (IAS compound negligible) |
| `neutron_total` | isotopic σ_tot, 0.1–200 MeV, every point | as is: σ_tot = σ_SE + σ_R(OM) already contains compound elastic |
| `proton_reaction` | measured σ_R (nonelastic) | — (reference) |
| `proton_reaction_direct` | σ_R(OM) = σ_nonel + σ_CE | proton reaction cross sections |

## 1. The ELM calibration evaluation

`elm_evaluation.apply` runs after `author_errors` when ELM sectors are written (`serialize.write_sector`), and in
`scripts/apply_author_errors.py --elm`:
- **Excluded targets:** 148Sm (deformed, β2 0.142).
- **Relative error floor:** y_err = max(y_err, 2 % |y|) on cross sections (elastic, charge exchange, σ_tot, σ_R).
  Analysing powers are exempt, since they cross zero. The errors before the floor are kept in
  `data.y_err_before_floor`, and `elm_evaluation.revert` restores them. `scripts/curate_sm3.py` does this, so sm3
  keeps the published errors.
- **Marker:** each record is marked `elm-evaluation v1`, which makes the step idempotent.

The same audit removed sets from every evaluated corpus (AUTHOR_UNCERTAINTIES.md §6): the Van Oers digitised
duplicates O0287004–010, C0622 (92Mo(p,p)) and 14662004 (Pruitt 124Sn(n,n) 11 MeV). It also added Rapaport's
total uncertainty for entry 10817 (§4.2).

## 2. Data from 0 MeV

- **Elastic window:** `spec.ELM_ELASTIC_EINC_RANGE` is now (0, 200) MeV. The neutron elastic sector gained 391 sets
  below 10 MeV, among them 92/94Mo (229), 208Pb and 206Pb (54), 40/48Ca (23), 90/92/94Zr (44) and Sn (43). Proton
  elastic gained 15 sets below 10 MeV. Three newly entering
  subentries rest on reader errors alone and are removed (F1407013, O1823002, F0930002; AUTHOR_UNCERTAINTIES.md §6).
- **Angle-integrated sectors:** [scripts/curate_elm_integral.py](../scripts/curate_elm_integral.py) curates the
  test and kduq spec subentries for ELM targets: σ_tot 14269, 14661, 10721, 13569, 10338, 10468, 13736, 12215 and
  13735; σ_R D0356, O0341, O0330, O0150, O0579, C1217, O0081 and C0424.
  - The energy window is 0.1–200 MeV. Below 0.1 MeV the data are resolved resonances: 90Zr transmission (13736003)
    reaches zero at 13 keV.
  - There is no thinning to one point per MeV. How to energy-average the resonance region (Lorentz smoothing) is
    the calibration's choice.
  - Only isotopic measurements are kept. A row listed under 208Pb resolved to natural Pb (10047089) and was
    dropped.
  - Three σ_R subentries do not parse with x4i3.
- **112Sn:** added to `spec.BETA2_BY_TARGET` with β2 0.123, from B(E2)↑ 0.242(8) e²b² (Kumar et al., PRC 81, 024306
  (2010)).

**Screening the new low-energy neutron sets.** Each set was compared with TALYS's elastic (KD03 shape elastic +
compound). The median ratio over the 400 sets is 0.99, with 5–95 % between 0.84 and 1.26. Outside 0.67–1.5:
- Fowler et al. (12217002), 208Pb, 0.7–1.8 MeV: 1.5–2.7×. These are isolated resonances in doubly magic 208Pb.
- Bostrom et al. (11130029), 206Pb, 4.2 MeV: 1.8×.
- Hicks et al., 48Ca: 13507002 at 8.0 MeV, 1.7×; 13508002 at 2.35 MeV, 0.64×.

None has independent data on the same target at the same energy. The ones in the isolated-resonance region are
removed (`elm_evaluation.EXCLUDED_RECORDS`, 2026-10-14): the 8 Fowler 208Pb energies and Hicks 48Ca at 2.35 MeV.
That region is where σ_tot shows resonance structure above 20 % beyond statistics:

| E (MeV) | 208Pb (13735002) | 40Ca (10721002) | 90Zr (13736003) |
|---|---:|---:|---:|
| 0.1–0.3 | 16 % | 140 % | 64 % |
| 0.5–0.75 | 51 % | 71 % | 28 % |
| 1–1.5 | 28 % | 39 % | 16 % |
| 2–2.5 | 21 % | 30 % | 7 % |
| 3–4 | 10 % | 15 % | — |
| 4–5 | 5 % | 9 % | — |
| 6–8 | 1 % | 4 % | — |

Bostrom 206Pb at 4.2 MeV and Hicks 48Ca at 8.0 MeV lie above the region and are kept. The other 21 Fowler 208Pb
energies (0.7–1.8 MeV) are kept too, with a median ratio of 1.33. A calibration should keep the region's
fluctuations out of the fit: energy-average there, or start above it.

## 3. Compound elastic from TALYS

The optical model describes shape (direct) elastic scattering. Compound-nucleus elastic scattering (CE) is part of
its absorption. So:
- **Elastic angular data:** direct = measured − CE(θ). The record keeps `y_measured`, `compound_elastic` and
  `ce_fraction` = |CE|/|measured|, and y_err = √(y_err² + (0.3 CE)²).
- **Proton reaction:** σ_R(OM) = σ_nonel + σ_CE.
- **Neutron total:** no correction.

**TALYS** is the git submodule `external/talys` (github.com/arjankoning1/talys, MIT, commit 49ef834, TALYS-2.24
output headers). It is shallow, with `update = none` in `.gitmodules`, because the repository with its structure
database is about 9 GB, so a plain clone or CI never fetches it. Settings: TALYS defaults (KD03 optical potentials,
Hauser–Feshbach with width fluctuations) plus `outangle y`, `fileelastic y`, `filetotal y`, and `cpang y` for
protons.

```bash
uv run python scripts/talys_compound.py build      # init the submodule, make (gfortran), smoke test
uv run python scripts/talys_compound.py run --sector elastic_diff_xs --workers 8      # ~2 min, all 35 systems
uv run python scripts/talys_compound.py run --sector proton_reaction --workers 8
uv run python scripts/talys_compound.py apply --sector elastic_diff_xs
uv run python scripts/talys_compound.py apply --sector proton_reaction
```

- **Smoke test:** reproduces the Direct column of jitr's TALYS regression case T1 (n + 120Sn, 10 MeV, JLM).
- **Cache:** `run` writes the parsed TALYS results to `compound_elastic/<corpus>/<sector>/<proj>_<Target>/`:
  `angular.csv`, `integral.csv`, `talys.inp` and `meta.json` with the commit. `apply` reads only that cache, so the
  `_direct` sectors can be rebuilt without TALYS.
- **Interpolation:** CE is interpolated to the data angles in cos θ. For (p,p) ratio data, CE/σ_Ruth uses TALYS's
  own Rutherford cross section (xs / (xs/Rutherford)).

**What TALYS finds.** Compound elastic matters only below about 6 MeV:

| E (MeV) | neutron sets | median CE fraction (median over sets) | largest set median |
|---|---:|---:|---:|
| 0–3 | 324 | 0.38 | 1.04 |
| 3–6 | 43 | 0.18 | 0.83 |
| 6–10 | 33 | 0.006 | 0.27 |
| 10–15 | 28 | 4e-5 | 0.003 |
| ≥ 15 | 41 | < 1e-6 | 2e-4 |

- **Protons:** CE is at most 1 % of the data (40Ca, 14 MeV).
- **The 40Ca excess:** the audit found 40Ca at 10–20 MeV 20–60 % above KD03. Compound elastic does not explain
  this.
- **Negative direct values:** below about 2 MeV, where TALYS's energy-averaged CE exceeds a measurement in the
  resonance region, `elastic_diff_xs_direct` can go negative. Those points carry ce_fraction > 1. Calibrations
  should keep data sets whose median ce_fraction is below a threshold (0.5 in ELM-Lane) and mask points above it.

**Tests:**
- [tests/test_talys_compound.py](../tests/test_talys_compound.py): TALYS output parsing, interpolation, and the
  subtraction on a synthetic case.
- [tests/test_elm_evaluation.py](../tests/test_elm_evaluation.py): the floor, exclusions, idempotency, `revert`,
  the drops, and Rapaport's total.
