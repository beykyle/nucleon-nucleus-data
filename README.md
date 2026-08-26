# nucleon_nucleus_data

Curation of four corpora of nucleon-nucleus scattering data from
[EXFOR](https://nds.iaea.org/exfor/), as JSON.

| corpus | what it is |
|---|---|
| **ELM** | Elastic nucleon scattering and $(p,n)$ charge exchange to the isobaric analog state, on near-spherical targets between 10 and 200 MeV. Ported from the ELM curation notebooks. |
| **KDUQ** | A reconstruction of the experimental data used in the Koning-Delaroche global optical potential analysis. |
| **CHUQ** | A reconstruction of the experimental data used in the CH89 global optical potential analysis. |
| **Test** | Directly-measured data post-dating the KD and CH89 publications, drawn entirely from EXFOR. |

KDUQ, CHUQ and Test are specified by the tables of
`supplement_experimentalCorpora.pdf`, which lists, per corpus and sector, the EXFOR
subentry and scattering energy of every data set. Those tables are transcribed to
`spec/*.csv` and are the ground truth for what belongs in each corpus.

This repository does curation only: EXFOR in, cleaned JSON out. Nothing here fits an
optical potential or evaluates a model.

## Getting started

```bash
uv sync --extra dev                       # environment, incl. the pinned exfor_tools
source scripts/setup_exfor_db.sh 2025     # or 2024; exports X43I_DATAPATH
uv run pytest tests/ -q                   # unit and data-integrity tests
uv run jupyter lab notebooks/             # the curation notebooks
```

`external/exfor_tools` is a submodule pinned to a branch carrying fixes this curation
needs; clone with `--recurse-submodules`, or run `git submodule update --init`.

## Layout

```
spec/                    the corpus tables, transcribed from the supplement, plus the
                         known-missing allowlist
scripts/                 PDF table extraction, EXFOR database setup, notebook scaffolding
src/nn_corpora/          the curation library
notebooks/<corpus>/      one notebook per corpus-sector
data/<corpus>/<sector>/  <Target>.json, <sector>.bib, and a per-corpus manifest.json
```

## Conventions

Everything is homogenised, so a consumer never has to ask what units a record is in.

| quantity | stored as | `type` |
|---|---|---|
| neutron differential elastic, $(p,n)$ | b/sr | `ECS` |
| charged-projectile differential elastic | ratio to Rutherford | `ECS_Rutherford` |
| analyzing power | dimensionless | `APower` |
| neutron total, proton reaction | b | `CS` |

Energies are in MeV and angles in CM degrees throughout.

**Charged-projectile elastic data are stored as a ratio to Rutherford whether or not
EXFOR reports them that way.** Absolute cross sections are divided by the Rutherford
cross section computed in `nn_corpora.kinematics`, which is a port of jitr's
(semi-relativistic $\eta$ and $k$, checked against jitr to 1e-12 in
`tests/test_kinematics.py`). This is the opposite of the supplement, which rescales
ratios into absolute mb/sr. Storing the ratio keeps the low-angle Coulomb divergence out
of the data and matches what the ELM corpus and `rxmc` work in; the conversion is exactly
invertible given the record's energy and target.

### Record schema

Records extend the schema `exfor_tools` writes via `Distribution.to_dataframe`, so files
stay readable by `AngularDistribution.from_dataframe` and
`EnergyDistribution.from_dataframe`. Four fields are added:

- `corpus`, `sector` — so files can be recombined after being split by target
- `projectile` — `"neutron"` or `"proton"`. The ELM corpus format keys only on the
  target, so $(n,n)$ and $(p,p)$ data for one nucleus are otherwise indistinguishable
- `notes` — every transformation applied to the record, in order

```json
{
    "type": "ECS_Rutherford",
    "energy": 65.0,
    "energy_err": 0.0,
    "energy_units": "MeV",
    "EXFORAccessionNumber": "O0032002",
    "source": "...",
    "x_units": "CM-degrees",
    "y_units": "no-dim",
    "data": {
        "x": [...], "y": [...], "y_err": [...],
        "systematic_normalization_error": 0.05
    },
    "corpus": "kduq", "sector": "proton_elastic",
    "projectile": "proton", "target": "Ca-40",
    "notes": ["divided by the Rutherford cross section ..."]
}
```

`y_err` is the overall per-point uncertainty; `systematic_normalization_error` is a
fractional correlated normalisation uncertainty, defaulting to 5% where EXFOR reports
none.

## How the cleaning works

**Uncertainties.** EXFOR data sets often carry several uncertainty columns with no
machine-readable statement of how they relate, and `exfor_tools` refuses to guess. The
supplement states a rule instead — prefer `ERR-T`, then the average of `+DATA-ERR` and
`-DATA-ERR`, then `ERR-S`, `ERR-DIG`, `ERR-SYS` — and `nn_corpora.errors` implements it,
extended with `DATA-ERR` and with quadrature over numbered `DATA-ERRn` partials as the
CHUQ notes direct. It resolves about 92% of subentries automatically; the rest are
handled explicitly in `nn_corpora.overrides` or recorded as unresolved.

**Documented corrections.** The supplement's Comments describe specific corrections —
data sets a factor of 1000 out through a units mismatch, error columns to ignore, a
transcribed uncertainty of 3.0034 that should read 0.0034. These are encoded in
`nn_corpora.overrides`, each citing the note that motivates it. Target reassignments the
Comments describe need no code: the tables already list the corrected target.

**Downsampling.** Neutron total cross sections are trimmed to the tabulated energy range
and thinned to at most one datum per MeV, following the supplement: the cross section
varies slowly enough over this range that the full complement of energy bins — nearly
50,000 for one data set — carries nothing an optical model analysis can use.

**Sparse data sets.** Angular distributions with too few angles to constrain a potential
are dropped after unrolling. This is the criterion the supplement applies repeatedly when
it excludes data that "included over 100 scattering energies but only a few angles for
each energy".

## Coverage

Every row of every corpus table is accounted for: it either produces data, or it appears
in `spec/known_missing.csv` with a reason. A row that stops resolving fails its notebook
rather than disappearing quietly. The categories are:

- `absent-from-exfor` — the supplement itself marks the row as not locatable
- `x4i3-parse-failure` — the entry is in EXFOR as a `.x4` file but x4i3 cannot parse it,
  raising `BrokenNumberError` on a malformed numeric field, and so it never reaches the
  index. Affects the 2024 and 2025 databases alike
- `subentry-withdrawn` — EXFOR has renumbered or removed the subentry since the
  supplement was written
- `energy-not-found`, `uncertainty-unresolved`

Where a subentry has been renumbered but the data survive elsewhere in the same entry —
the same publication and measurement campaign — retrieval substitutes it, requiring an
unambiguous energy match and recording the substitution in the coverage report and the
record's `notes`.

## Differences from the sources

Faithful reproduction was the goal, but three departures are deliberate:

1. **Rutherford ratios rather than absolute cross sections** for charged projectiles, as
   above. This also changes the ELM corpus relative to its original notebooks, where
   proton elastic records typed `ECS` become `ECS_Rutherford`.
2. **Lab-frame angles are converted, not discarded.** The ELM notebooks reject subentries
   reporting lab angles except where converted by hand; here every such data set is
   converted, which admits data the original corpora did not have.
3. **Older EXFOR analyzing-power codes are recognised.** `exfor_tools` matched only
   `POL/DA,ANA`; a bare `POL/DA` (the outgoing-particle polarization, equal to the
   analyzing power for elastic scattering) and `POL/DA,ASY` (the measured asymmetry) are
   now matched too, which likewise admits data the original corpora did not have.
   Dimensioned `POL/DA` columns are the polarization *cross section*, a different
   observable, and are excluded.

## Reproducing

```bash
python scripts/extract_corpus_tables.py     # PDF -> spec/*.csv
uv run pytest --nbmake notebooks/           # execute every notebook, rewriting data/
python scripts/refresh_known_missing.py     # regenerate the allowlist after review
```

The EXFOR database version is recorded in each corpus's `manifest.json`, alongside the
`exfor_tools` and `x4i3` versions used.
