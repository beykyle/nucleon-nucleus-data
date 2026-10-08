# Data sets without a good author source of uncertainties (for case-by-case review)

Flagged 2026-10-08 (DATA_CLEANING.md decision log). These records currently rest on EXFOR's data-point reader /
digitisation uncertainty, and the original paper either is not available, is the wrong file, or does not state
per-point errors. For each, decide: **drop** from the corpora, a **uniform fallback**, or the **per-paper proposal**.

Sources: `docs/ERROR_EXTRACTION.md`, `docs/extraction/extract_G*.md`, `papers/exfor_crosscheck_generated.md`.
Only records with reader-only points are listed (the corpora they appear in are shown per row).

## Decisions (Kyle, 2026-10-08: "For the rest of the flagged data sets, drop them from corpora for now")

Applied by `nn_corpora.author_errors` (`DROP_FLAGGED`); dropped spec rows are allowlisted in `spec/known_missing.csv`
(category `dropped-in-cleaning`). To restore a set, remove it from `DROP_FLAGGED` and give it an author rule.

| entry | decision (drop / fallback / proposal) | note |
|---|---|---|
| O0157 | keep: Devins found (papers/devins.pdf) | p.619: absolute errors ~3.5 % forward → ~10 % extreme backward; ramp in angle, default 5 % normalisation |
| F1173 | drop (for now) |  |
| O0083 | drop (for now) |  |
| O0372 | drop (for now) |  |
| O0446 | drop (for now) |  |
| O0328 | keep: partial record | EXFOR ERR-1 (authors' errors) ⊕ ERR-DIG; ERR-1 blanks filled by interpolation, flat beyond the ends; ERR-2 ⊕ ERR-3 = 5.4 % normalisation |
| O0382 | drop (for now) |  |
| O0580 | drop (for now) |  |
| O0225 | drop (for now) |  |
| O0254 | drop (for now) |  |
| O0259 | drop (for now) |  |
| O0272 | drop (for now) |  |
| O0370 | drop (for now) |  |
| O0384 | drop (for now) |  |
| O0387 | drop (for now) |  |
| O0458 | drop (for now) |  |
| O1199 | drop (for now) |  |
| O0079 | drop (for now) |  |
| O0553 | drop (for now) |  |
| O1103 | drop (for now) |  |
| O1109 | drop (for now) |  |

## Flagged: no usable author source

### O0157: wrong PDF

- **What the paper gives:** compilation file is Moonen 1993; EXFOR text: ~3.5 % forward to ~10 % backward
- **Proposal (if kept):** 3.5→10 % ramp (EXFOR text only)

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0157002 | kduq | dσ/dΩ | Ni-60 | 30.8 | 75/75 | 2.6 % | [O0157.002](https://www-nds.iaea.org/EXFOR/O0157.002) |
| O0157004 | elm | dσ/dΩ | Pb-208 | 30.8 | 67/67 | 4.0 % | [O0157.004](https://www-nds.iaea.org/EXFOR/O0157.004) |

### F1173: no PDF

- **What the paper gives:** Izv. AN SSSR 36, 2232 (1972) not available
- **Proposal (if kept):** fill rule (partial record)

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| F1173002 | elm | dσ/dΩ | Sm-148 | 24.5 | 21/24 | 0.0 % | [F1173.002](https://www-nds.iaea.org/EXFOR/F1173.002) |

### O0083: no PDF

- **What the paper gives:** JPSJ Suppl. 44, 543 (1978) not available
- **Proposal (if kept):** —

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0083016 | kduq | dσ/dΩ | Fe-56 | 35.2 | 30/30 | 1.6 % | [O0083.016](https://www-nds.iaea.org/EXFOR/O0083.016) |
| O0083019 | kduq | dσ/dΩ | Al-27 | 35.2 | 27/27 | 2.3 % | [O0083.019](https://www-nds.iaea.org/EXFOR/O0083.019) |

### O0372: no PDF

- **What the paper gives:** JPSJ 22, 1311 (1967) not available
- **Proposal (if kept):** —

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0372013 | elm | dσ/dΩ | Zr-90 | 14.71 | 13/13 | 5.0 % | [O0372.013](https://www-nds.iaea.org/EXFOR/O0372.013) |
| O0372013 | kduq | dσ/dΩ | Zr-90 | 14.71 | 13/13 | 5.0 % | [O0372.013](https://www-nds.iaea.org/EXFOR/O0372.013) |
| O0372014 | elm | dσ/dΩ | Zr-92 | 14.25 | 13/13 | 5.0 % | [O0372.014](https://www-nds.iaea.org/EXFOR/O0372.014) |

### O0446: no PDF

- **What the paper gives:** JPSJ 15, 1151 (1960) not available
- **Proposal (if kept):** —

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0446002 | kduq | dσ/dΩ | Ni-58 | 10.7 | 15/15 | 3.0 % | [O0446.002](https://www-nds.iaea.org/EXFOR/O0446.002) |
| O0446002 | kduq | dσ/dΩ | Ni-58 | 14.4 | 15/15 | 3.0 % | [O0446.002](https://www-nds.iaea.org/EXFOR/O0446.002) |
| O0446002 | kduq | dσ/dΩ | Ni-58 | 15.4 | 15/15 | 3.0 % | [O0446.002](https://www-nds.iaea.org/EXFOR/O0446.002) |
| O0446003 | kduq | dσ/dΩ | Ni-60 | 14.4 | 15/15 | 3.0 % | [O0446.003](https://www-nds.iaea.org/EXFOR/O0446.003) |
| O0446003 | kduq | dσ/dΩ | Ni-60 | 15.4 | 15/15 | 3.0 % | [O0446.003](https://www-nds.iaea.org/EXFOR/O0446.003) |

### O0328: not stated (partial)

- **What the paper gives:** ERR-1 = author error where present; no numbers in paper for blank points (tables at ADI)
- **Proposal (if kept):** figure: σ 3 % (6 % >120°), Ay 0.03 (0.1 large angles)

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0328004 | chuq | dσ/dΩ | Co-59 | 40.0 | 50/65 | 0.4 % | [O0328.004](https://www-nds.iaea.org/EXFOR/O0328.004) |
| O0328005 | chuq | dσ/dΩ | Zn-68 | 40.0 | 51/64 | 0.4 % | [O0328.005](https://www-nds.iaea.org/EXFOR/O0328.005) |
| O0328007 | chuq | dσ/dΩ | Sn-120 | 40.0 | 54/64 | 0.4 % | [O0328.007](https://www-nds.iaea.org/EXFOR/O0328.007) |
| O0328007 | elm | dσ/dΩ | Sn-120 | 40.0 | 54/64 | 0.4 % | [O0328.007](https://www-nds.iaea.org/EXFOR/O0328.007) |
| O0328007 | kduq | dσ/dΩ | Sn-120 | 40.0 | 54/64 | 0.4 % | [O0328.007](https://www-nds.iaea.org/EXFOR/O0328.007) |
| O0328007 | sm3 | dσ/dΩ | Sn-120 | 40.0 | 54/64 | 0.4 % | [O0328.007](https://www-nds.iaea.org/EXFOR/O0328.007) |
| O0328009 | chuq | Ay | Co-59 | 40.0 | 11/22 | reader (abs.) | [O0328.009](https://www-nds.iaea.org/EXFOR/O0328.009) |
| O0328010 | chuq | Ay | Zn-68 | 40.0 | 14/24 | reader (abs.) | [O0328.010](https://www-nds.iaea.org/EXFOR/O0328.010) |
| O0328011 | chuq | Ay | Sn-120 | 40.0 | 24/34 | reader (abs.) | [O0328.011](https://www-nds.iaea.org/EXFOR/O0328.011) |
| O0328011 | elm | Ay | Sn-120 | 40.0 | 24/34 | reader (abs.) | [O0328.011](https://www-nds.iaea.org/EXFOR/O0328.011) |
| O0328011 | kduq | Ay | Sn-120 | 40.0 | 24/34 | reader (abs.) | [O0328.011](https://www-nds.iaea.org/EXFOR/O0328.011) |

### O0382: not stated

- **What the paper gives:** only the 15 % scale stated; no bars
- **Proposal (if kept):** 5 % σ, norm 15 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0382002 | elm | dσ/dΩ | Ca-40 | 55.0 | 16/18 | 6.0 % | [O0382.002](https://www-nds.iaea.org/EXFOR/O0382.002) |

### O0580: not stated

- **What the paper gives:** statistical bars inside symbols; no numbers
- **Proposal (if kept):** 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0580002 | elm | dσ/dΩ | Mo-94 | 25.6 | 41/42 | 0.1 % | [O0580.002](https://www-nds.iaea.org/EXFOR/O0580.002) |

### O0225: not stated

- **What the paper gives:** no per-point error, no visible bars
- **Proposal (if kept):** 2 % floor, norm 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0225146 | elm | dσ/dΩ | Pb-208 | 35.0 | 23/23 | 1.9 % | [O0225.146](https://www-nds.iaea.org/EXFOR/O0225.146) |

### O0254: not stated

- **What the paper gives:** relative σ; 'same statistical accuracy as the polarisation' (Ay 1-4 %)
- **Proposal (if kept):** 4 %, free / large norm

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0254009 | kduq | dσ/dΩ | Si-28 | 17.8 | 19/19 | 2.1 % | [O0254.009](https://www-nds.iaea.org/EXFOR/O0254.009) |
| O0254010 | elm | dσ/dΩ | Ca-40 | 17.8 | 23/23 | 2.1 % | [O0254.010](https://www-nds.iaea.org/EXFOR/O0254.010) |

### O0259: not stated

- **What the paper gives:** data from TRIUMF ref. 25; no bars
- **Proposal (if kept):** 3 %, norm 7 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0259002 | elm | dσ/dΩ | Pb-208 | 200.0 | 65/65 | 2.6 % | [O0259.002](https://www-nds.iaea.org/EXFOR/O0259.002) |

### O0272: not stated

- **What the paper gives:** nothing stated; details in refs 5, 6
- **Proposal (if kept):** 7 % placeholder

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0272002 | elm | dσ/dΩ | Pb-208 | 200.0 | 75/75 | 7.0 % | [O0272.002](https://www-nds.iaea.org/EXFOR/O0272.002) |

### O0370: not stated

- **What the paper gives:** per-point not stated; norm ~5 %
- **Proposal (if kept):** 2 %, norm 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0370002 | elm | dσ/dΩ | Zr-90 | 18.8 | 36/36 | 1.7–25.9 % | [O0370.002](https://www-nds.iaea.org/EXFOR/O0370.002) |
| O0370002 | kduq | dσ/dΩ | Zr-90 | 18.8 | 36/36 | 1.7–25.9 % | [O0370.002](https://www-nds.iaea.org/EXFOR/O0370.002) |

### O0384: not stated

- **What the paper gives:** per-point not stated; norm 15 % stated
- **Proposal (if kept):** 5 %, norm 15 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0384002 | elm | dσ/dΩ | Ca-40 | 14.6 | 25/25 | 5.0 % | [O0384.002](https://www-nds.iaea.org/EXFOR/O0384.002) |
| O0384003 | elm | dσ/dΩ | Ca-40 | 17.3 | 23/23 | 5.0 % | [O0384.003](https://www-nds.iaea.org/EXFOR/O0384.003) |

### O0387: not stated

- **What the paper gives:** per-point not stated; scale matched to the Argonne curve
- **Proposal (if kept):** 4 %, norm 10 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0387002 | elm | dσ/dΩ | Ca-48 | 12.0 | 22/22 | 1.6 % | [O0387.002](https://www-nds.iaea.org/EXFOR/O0387.002) |

### O0458: not stated

- **What the paper gives:** nothing stated; tiny bars
- **Proposal (if kept):** 3 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0458004 | elm | dσ/dΩ | Ni-64 | 12.0 | 23/23 | 2.6 % | [O0458.004](https://www-nds.iaea.org/EXFOR/O0458.004) |

### O1199: not stated (Ay)

- **What the paper gives:** σ 4 % stated; nothing for Ay
- **Proposal (if kept):** Ay 0.02–0.03

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O1199008 | elm | Ay | Ca-40 | 35.0 | 31/31 | reader (abs.) | [O1199.008](https://www-nds.iaea.org/EXFOR/O1199.008) |
| O1199009 | elm | Ay | Ca-40 | 26.3 | 29/29 | reader (abs.) | [O1199.009](https://www-nds.iaea.org/EXFOR/O1199.009) |
| O1199009 | elm | Ay | Ca-40 | 40.0 | 32/32 | reader (abs.) | [O1199.009](https://www-nds.iaea.org/EXFOR/O1199.009) |

### O0079: not stated

- **What the paper gives:** nothing stated, no bars
- **Proposal (if kept):** 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0079006 | kduq | dσ/dΩ | Fe-54 | 19.6 | 30/30 | 2.3 % | [O0079.006](https://www-nds.iaea.org/EXFOR/O0079.006) |

### O0553: weak

- **What the paper gives:** statistical bars invisible; 12C table 3–6 % as a proxy
- **Proposal (if kept):** 4 % / 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0553004 | kduq | dσ/dΩ | Ca-40 | 152.0 | 28/28 | 7.0 % | [O0553.004](https://www-nds.iaea.org/EXFOR/O0553.004) |
| O0553006 | kduq | dσ/dΩ | Bi-209 | 153.0 | 22/22 | 6.0 % | [O0553.006](https://www-nds.iaea.org/EXFOR/O0553.006) |
| O0553010 | kduq | dσ/dΩ | Ca-40 | 75.0 | 9/9 | 5.0 % | [O0553.010](https://www-nds.iaea.org/EXFOR/O0553.010) |
| O0553014 | kduq | dσ/dΩ | Bi-209 | 78.0 | 13/13 | 5.0 % | [O0553.014](https://www-nds.iaea.org/EXFOR/O0553.014) |

### O1103: not stated

- **What the paper gives:** nothing stated (same group as O1104)
- **Proposal (if kept):** 2 %, Ay 0.02

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O1103004 | chuq | dσ/dΩ | Ge-72 | 22.3 | 25/25 | 1.6 % | [O1103.004](https://www-nds.iaea.org/EXFOR/O1103.004) |
| O1103006 | chuq | dσ/dΩ | Ge-74 | 22.3 | 26/26 | 1.6 % | [O1103.006](https://www-nds.iaea.org/EXFOR/O1103.006) |
| O1103012 | chuq | dσ/dΩ | Se-78 | 22.3 | 33/33 | 1.6 % | [O1103.012](https://www-nds.iaea.org/EXFOR/O1103.012) |
| O1103014 | chuq | dσ/dΩ | Se-80 | 22.3 | 28/28 | 1.6 % | [O1103.014](https://www-nds.iaea.org/EXFOR/O1103.014) |

### O1109: not stated

- **What the paper gives:** nothing stated (same group as O1104)
- **Proposal (if kept):** 2 %, Ay 0.02

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O1109002 | chuq | dσ/dΩ | Zn-64 | 20.4 | 30/30 | 1.6 % | [O1109.002](https://www-nds.iaea.org/EXFOR/O1109.002) |
| O1109004 | chuq | dσ/dΩ | Zn-66 | 20.4 | 30/30 | 1.9 % | [O1109.004](https://www-nds.iaea.org/EXFOR/O1109.004) |
| O1109005 | chuq | Ay | Zn-66 | 20.4 | 31/31 | reader (abs.) | [O1109.005](https://www-nds.iaea.org/EXFOR/O1109.005) |
| O1109006 | chuq | dσ/dΩ | Zn-68 | 20.4 | 31/31 | 1.6 % | [O1109.006](https://www-nds.iaea.org/EXFOR/O1109.006) |
| O1109008 | chuq | dσ/dΩ | Zn-70 | 20.4 | 30/30 | 1.9 % | [O1109.008](https://www-nds.iaea.org/EXFOR/O1109.008) |

## Borderline: author source exists but is a fit weight, a bound, or ambiguous for Ay


### O0124: fitted with 5 %, 'actual always smaller' → 5 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0124002 | kduq | dσ/dΩ | Si-28 | 30.4 | 44/44 | 2.3 % | [O0124.002](https://www-nds.iaea.org/EXFOR/O0124.002) |
| O0124004 | elm | dσ/dΩ | Sn-120 | 30.4 | 42/42 | 1.9 % | [O0124.004](https://www-nds.iaea.org/EXFOR/O0124.004) |

### O0246: 10 % 'arbitrarily assigned' for fitting → 10 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0246017 | elm | dσ/dΩ | Sm-148 | 16.0 | 24/24 | — | [O0246.017](https://www-nds.iaea.org/EXFOR/O0246.017) |

### O0471: 'not more than 6 %' → 6 %

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0471007 | elm | dσ/dΩ | Mo-92 | 12.52 | 7/7 | 2.8 % | [O0471.007](https://www-nds.iaea.org/EXFOR/O0471.007) |
| O0471008 | elm | dσ/dΩ | Mo-94 | 12.52 | 8/8 | 2.8 % | [O0471.008](https://www-nds.iaea.org/EXFOR/O0471.008) |

### O0091: Ay not stated (σ 2–3 % assigned, high) → Ay 0.02 floor

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0091002 | chuq | dσ/dΩ | Fe-54 | 17.2 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091002 | chuq | dσ/dΩ | Fe-54 | 20.4 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091002 | chuq | dσ/dΩ | Fe-54 | 24.6 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091002 | kduq | dσ/dΩ | Fe-54 | 17.2 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091002 | kduq | dσ/dΩ | Fe-54 | 20.4 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091002 | kduq | dσ/dΩ | Fe-54 | 24.6 | 30/30 | 0.9 % | [O0091.002](https://www-nds.iaea.org/EXFOR/O0091.002) |
| O0091003 | chuq | Ay | Fe-54 | 20.4 | 21/29 | reader (abs.) | [O0091.003](https://www-nds.iaea.org/EXFOR/O0091.003) |
| O0091003 | chuq | Ay | Fe-54 | 24.6 | 28/30 | reader (abs.) | [O0091.003](https://www-nds.iaea.org/EXFOR/O0091.003) |
| O0091003 | kduq | Ay | Fe-54 | 20.4 | 21/29 | reader (abs.) | [O0091.003](https://www-nds.iaea.org/EXFOR/O0091.003) |
| O0091003 | kduq | Ay | Fe-54 | 24.6 | 28/30 | reader (abs.) | [O0091.003](https://www-nds.iaea.org/EXFOR/O0091.003) |
| O0091008 | chuq | dσ/dΩ | Fe-56 | 17.2 | 30/30 | 0.9 % | [O0091.008](https://www-nds.iaea.org/EXFOR/O0091.008) |
| O0091008 | chuq | dσ/dΩ | Fe-56 | 20.4 | 31/31 | 0.9 % | [O0091.008](https://www-nds.iaea.org/EXFOR/O0091.008) |
| O0091008 | chuq | dσ/dΩ | Fe-56 | 24.6 | 30/30 | 0.9 % | [O0091.008](https://www-nds.iaea.org/EXFOR/O0091.008) |
| O0091009 | chuq | Ay | Fe-56 | 20.4 | 14/30 | reader (abs.) | [O0091.009](https://www-nds.iaea.org/EXFOR/O0091.009) |
| O0091009 | chuq | Ay | Fe-56 | 24.6 | 22/30 | reader (abs.) | [O0091.009](https://www-nds.iaea.org/EXFOR/O0091.009) |
| O0091009 | kduq | Ay | Fe-56 | 20.4 | 14/30 | reader (abs.) | [O0091.009](https://www-nds.iaea.org/EXFOR/O0091.009) |
| O0091009 | kduq | Ay | Fe-56 | 24.6 | 22/30 | reader (abs.) | [O0091.009](https://www-nds.iaea.org/EXFOR/O0091.009) |
| O0091014 | chuq | dσ/dΩ | Ni-58 | 20.4 | 30/30 | 0.9 % | [O0091.014](https://www-nds.iaea.org/EXFOR/O0091.014) |
| O0091014 | chuq | dσ/dΩ | Ni-58 | 24.6 | 30/30 | 0.9 % | [O0091.014](https://www-nds.iaea.org/EXFOR/O0091.014) |
| O0091015 | chuq | Ay | Ni-58 | 24.6 | 18/30 | reader (abs.) | [O0091.015](https://www-nds.iaea.org/EXFOR/O0091.015) |
| O0091015 | kduq | Ay | Ni-58 | 24.6 | 18/30 | reader (abs.) | [O0091.015](https://www-nds.iaea.org/EXFOR/O0091.015) |
| O0091018 | chuq | dσ/dΩ | Ni-60 | 20.4 | 29/29 | 0.9 % | [O0091.018](https://www-nds.iaea.org/EXFOR/O0091.018) |
| O0091018 | chuq | dσ/dΩ | Ni-60 | 24.6 | 30/30 | 0.9 % | [O0091.018](https://www-nds.iaea.org/EXFOR/O0091.018) |
| O0091019 | chuq | Ay | Ni-60 | 24.6 | 13/30 | reader (abs.) | [O0091.019](https://www-nds.iaea.org/EXFOR/O0091.019) |
| O0091019 | kduq | Ay | Ni-60 | 24.6 | 13/30 | reader (abs.) | [O0091.019](https://www-nds.iaea.org/EXFOR/O0091.019) |
| O0091022 | chuq | dσ/dΩ | Ni-62 | 20.4 | 30/30 | 0.9 % | [O0091.022](https://www-nds.iaea.org/EXFOR/O0091.022) |
| O0091022 | chuq | dσ/dΩ | Ni-62 | 24.6 | 29/29 | 0.9 % | [O0091.022](https://www-nds.iaea.org/EXFOR/O0091.022) |
| O0091023 | chuq | Ay | Ni-62 | 24.6 | 15/29 | reader (abs.) | [O0091.023](https://www-nds.iaea.org/EXFOR/O0091.023) |

### O0169: Ay: stated 0.01 minimum; actual bars from figures

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0169004 | chuq | dσ/dΩ | Ni-64 | 20.4 | 29/29 | 1.6 % | [O0169.004](https://www-nds.iaea.org/EXFOR/O0169.004) |
| O0169005 | chuq | Ay | Ni-64 | 20.4 | 30/30 | reader (abs.) | [O0169.005](https://www-nds.iaea.org/EXFOR/O0169.005) |
| O0169005 | elm | Ay | Ni-64 | 20.4 | 30/30 | reader (abs.) | [O0169.005](https://www-nds.iaea.org/EXFOR/O0169.005) |
| O0169006 | chuq | dσ/dΩ | Sr-86 | 24.6 | 29/29 | 1.6 % | [O0169.006](https://www-nds.iaea.org/EXFOR/O0169.006) |
| O0169007 | elm | Ay | Sr-86 | 24.6 | 28/29 | reader (abs.) | [O0169.007](https://www-nds.iaea.org/EXFOR/O0169.007) |
| O0169008 | chuq | dσ/dΩ | Sr-88 | 24.6 | 29/29 | 1.6 % | [O0169.008](https://www-nds.iaea.org/EXFOR/O0169.008) |
| O0169009 | chuq | Ay | Sr-88 | 24.6 | 29/29 | reader (abs.) | [O0169.009](https://www-nds.iaea.org/EXFOR/O0169.009) |
| O0169009 | elm | Ay | Sr-88 | 24.6 | 29/29 | reader (abs.) | [O0169.009](https://www-nds.iaea.org/EXFOR/O0169.009) |
| O0169010 | chuq | dσ/dΩ | Cd-110 | 20.4 | 30/30 | 1.6 % | [O0169.010](https://www-nds.iaea.org/EXFOR/O0169.010) |
| O0169011 | chuq | Ay | Cd-110 | 20.4 | 30/30 | reader (abs.) | [O0169.011](https://www-nds.iaea.org/EXFOR/O0169.011) |
| O0169012 | chuq | dσ/dΩ | Cd-112 | 20.4 | 30/30 | 1.6 % | [O0169.012](https://www-nds.iaea.org/EXFOR/O0169.012) |
| O0169014 | chuq | dσ/dΩ | Cd-114 | 20.4 | 28/28 | 1.6 % | [O0169.014](https://www-nds.iaea.org/EXFOR/O0169.014) |
| O0169016 | chuq | dσ/dΩ | Sn-116 | 20.4 | 25/25 | 1.9 % | [O0169.016](https://www-nds.iaea.org/EXFOR/O0169.016) |
| O0169017 | chuq | Ay | Sn-116 | 20.4 | 27/27 | reader (abs.) | [O0169.017](https://www-nds.iaea.org/EXFOR/O0169.017) |
| O0169017 | elm | Ay | Sn-116 | 20.4 | 27/27 | reader (abs.) | [O0169.017](https://www-nds.iaea.org/EXFOR/O0169.017) |
| O0169018 | chuq | dσ/dΩ | Sn-118 | 20.4 | 27/27 | 1.9 % | [O0169.018](https://www-nds.iaea.org/EXFOR/O0169.018) |
| O0169019 | chuq | Ay | Sn-118 | 20.4 | 29/29 | reader (abs.) | [O0169.019](https://www-nds.iaea.org/EXFOR/O0169.019) |
| O0169019 | elm | Ay | Sn-118 | 20.4 | 29/29 | reader (abs.) | [O0169.019](https://www-nds.iaea.org/EXFOR/O0169.019) |
| O0169020 | chuq | dσ/dΩ | Sn-120 | 20.4 | 30/30 | 1.9 % | [O0169.020](https://www-nds.iaea.org/EXFOR/O0169.020) |
| O0169020 | kduq | dσ/dΩ | Sn-120 | 20.4 | 30/30 | 1.9 % | [O0169.020](https://www-nds.iaea.org/EXFOR/O0169.020) |
| O0169021 | chuq | Ay | Sn-120 | 20.4 | 30/30 | reader (abs.) | [O0169.021](https://www-nds.iaea.org/EXFOR/O0169.021) |
| O0169021 | elm | Ay | Sn-120 | 20.4 | 30/30 | reader (abs.) | [O0169.021](https://www-nds.iaea.org/EXFOR/O0169.021) |
| O0169021 | kduq | Ay | Sn-120 | 20.4 | 30/30 | reader (abs.) | [O0169.021](https://www-nds.iaea.org/EXFOR/O0169.021) |
| O0169022 | chuq | dσ/dΩ | Sn-122 | 20.4 | 27/27 | 1.9 % | [O0169.022](https://www-nds.iaea.org/EXFOR/O0169.022) |
| O0169023 | chuq | Ay | Sn-122 | 20.4 | 29/29 | reader (abs.) | [O0169.023](https://www-nds.iaea.org/EXFOR/O0169.023) |
| O0169023 | elm | Ay | Sn-122 | 20.4 | 29/29 | reader (abs.) | [O0169.023](https://www-nds.iaea.org/EXFOR/O0169.023) |
| O0169024 | chuq | dσ/dΩ | Sn-124 | 20.4 | 27/27 | 1.9 % | [O0169.024](https://www-nds.iaea.org/EXFOR/O0169.024) |
| O0169025 | chuq | Ay | Sn-124 | 20.4 | 27/27 | reader (abs.) | [O0169.025](https://www-nds.iaea.org/EXFOR/O0169.025) |
| O0169025 | elm | Ay | Sn-124 | 20.4 | 27/27 | reader (abs.) | [O0169.025](https://www-nds.iaea.org/EXFOR/O0169.025) |
| O0169026 | chuq | dσ/dΩ | Sn-120 | 24.6 | 21/21 | 2.8 % | [O0169.026](https://www-nds.iaea.org/EXFOR/O0169.026) |
| O0169026 | kduq | dσ/dΩ | Sn-120 | 24.6 | 21/21 | 2.8 % | [O0169.026](https://www-nds.iaea.org/EXFOR/O0169.026) |
| O0169027 | chuq | Ay | Sn-120 | 24.6 | 20/20 | reader (abs.) | [O0169.027](https://www-nds.iaea.org/EXFOR/O0169.027) |
| O0169027 | elm | Ay | Sn-120 | 24.6 | 20/20 | reader (abs.) | [O0169.027](https://www-nds.iaea.org/EXFOR/O0169.027) |
| O0169027 | kduq | Ay | Sn-120 | 24.6 | 20/20 | reader (abs.) | [O0169.027](https://www-nds.iaea.org/EXFOR/O0169.027) |

### O1104: Ay: '2 %' minimum, relative or absolute unclear

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O1104002 | chuq | dσ/dΩ | Cd-106 | 22.3 | 28/28 | 1.4 % | [O1104.002](https://www-nds.iaea.org/EXFOR/O1104.002) |
| O1104003 | chuq | Ay | Cd-106 | 22.3 | 27/27 | reader (abs.) | [O1104.003](https://www-nds.iaea.org/EXFOR/O1104.003) |
| O1104004 | chuq | dσ/dΩ | Cd-108 | 22.3 | 30/30 | 1.4 % | [O1104.004](https://www-nds.iaea.org/EXFOR/O1104.004) |
| O1104005 | chuq | Ay | Cd-108 | 22.3 | 30/30 | reader (abs.) | [O1104.005](https://www-nds.iaea.org/EXFOR/O1104.005) |
| O1104006 | chuq | dσ/dΩ | Cd-110 | 22.3 | 27/27 | 1.4 % | [O1104.006](https://www-nds.iaea.org/EXFOR/O1104.006) |
| O1104007 | chuq | Ay | Cd-110 | 22.3 | 28/28 | reader (abs.) | [O1104.007](https://www-nds.iaea.org/EXFOR/O1104.007) |
| O1104008 | chuq | dσ/dΩ | Cd-112 | 22.3 | 27/27 | 1.4 % | [O1104.008](https://www-nds.iaea.org/EXFOR/O1104.008) |
| O1104009 | chuq | Ay | Cd-112 | 22.3 | 29/29 | reader (abs.) | [O1104.009](https://www-nds.iaea.org/EXFOR/O1104.009) |
| O1104010 | chuq | dσ/dΩ | Cd-114 | 22.3 | 32/32 | 1.4 % | [O1104.010](https://www-nds.iaea.org/EXFOR/O1104.010) |
| O1104011 | chuq | Ay | Cd-114 | 22.3 | 30/30 | reader (abs.) | [O1104.011](https://www-nds.iaea.org/EXFOR/O1104.011) |
| O1104012 | chuq | dσ/dΩ | Cd-116 | 22.3 | 31/31 | 1.4 % | [O1104.012](https://www-nds.iaea.org/EXFOR/O1104.012) |
| O1104013 | chuq | Ay | Cd-116 | 22.3 | 31/31 | reader (abs.) | [O1104.013](https://www-nds.iaea.org/EXFOR/O1104.013) |

### O0239: Ay 'typical 2 %', unit unstated → 0.02

| subentry | corpus | observable | target | E (MeV) | points (reader-only/n) | current error | EXFOR |
|---|---|---|---|---|---|---|---|
| O0239002 | elm | dσ/dΩ | Ca-40 | 16.25 | 27/27 | 0.6–8.7 % | [O0239.002](https://www-nds.iaea.org/EXFOR/O0239.002) |
| O0239003 | elm | Ay | Ca-40 | 16.25 | 27/27 | reader (abs.) | [O0239.003](https://www-nds.iaea.org/EXFOR/O0239.003) |
| O0239004 | elm | dσ/dΩ | Ca-40 | 15.65 | 27/27 | 0.6–12.5 % | [O0239.004](https://www-nds.iaea.org/EXFOR/O0239.004) |
| O0239005 | elm | Ay | Ca-40 | 15.65 | 28/28 | reader (abs.) | [O0239.005](https://www-nds.iaea.org/EXFOR/O0239.005) |
| O0239006 | elm | dσ/dΩ | Ca-40 | 14.08 | 27/27 | 1.4–18.2 % | [O0239.006](https://www-nds.iaea.org/EXFOR/O0239.006) |
| O0239007 | elm | Ay | Ca-40 | 14.08 | 26/26 | reader (abs.) | [O0239.007](https://www-nds.iaea.org/EXFOR/O0239.007) |
| O0239014 | elm | dσ/dΩ | Ca-48 | 15.63 | 27/27 | 0.6–7.6 % | [O0239.014](https://www-nds.iaea.org/EXFOR/O0239.014) |
| O0239015 | elm | Ay | Ca-48 | 15.63 | 26/26 | reader (abs.) | [O0239.015](https://www-nds.iaea.org/EXFOR/O0239.015) |
| O0239016 | elm | dσ/dΩ | Ca-48 | 15.05 | 28/28 | 0.7–7.4 % | [O0239.016](https://www-nds.iaea.org/EXFOR/O0239.016) |
| O0239017 | elm | Ay | Ca-48 | 15.05 | 27/27 | reader (abs.) | [O0239.017](https://www-nds.iaea.org/EXFOR/O0239.017) |
| O0239018 | elm | dσ/dΩ | Ca-48 | 14.03 | 27/27 | 0.7–6.0 % | [O0239.018](https://www-nds.iaea.org/EXFOR/O0239.018) |
| O0239019 | elm | Ay | Ca-48 | 14.03 | 26/26 | reader (abs.) | [O0239.019](https://www-nds.iaea.org/EXFOR/O0239.019) |
