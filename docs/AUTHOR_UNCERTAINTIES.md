# Author uncertainties for data digitised from figures

Many angular distributions in EXFOR were not published as tables. The compilers read them off the published figures
and recorded, as the only per-point uncertainty, their own estimate of how precisely each point could be read: the
*data-point reader* (digitisation) uncertainty. That number says nothing about the measurement. It can be far
smaller than the authors' error (0.4 % for Fricke et al., whose bars reach 15 %) or unrelated to it.

## Which corpora

| corpus | uncertainties |
|---|---|
| `kduq`, `chuq`, `test` | **static**: exactly as the published corpora curate them (the supplement's tables and rules). Not corrected; they keep reader-only points where EXFOR has them (36 records in KDUQ, 67 in CHUQ, none in Test), and three KDUQ records use a reader column where EXFOR has the authors' error (§4.2). Use these to reproduce published fits. |
| `kduq_evaluated`, `chuq_evaluated`, `test_evaluated` | the static corpora with the corrections on this page applied: the same records, minus those removed (§6). Test needs only one correction (22987, §4.2). |
| `elm`, `sm3` | **evaluated** throughout: our best evaluation of each record's experimental uncertainty, from the EXFOR entry and the publication. |

In the evaluated corpora **no data point rests on a reader uncertainty alone**. Wherever EXFOR gives only a reader
uncertainty, the record carries an uncertainty stated by the authors (from a table, the text, or EXFOR's own
author column), or the record is removed. Where EXFOR and the publication disagree, the publication wins. This page
explains what was changed relative to EXFOR, what was removed, and why.

A record shared by several evaluated corpora carries the same uncertainties in each. The static corpora choose
error columns by a generic label preference (`ERR-T`, then `DATA-ERR`, `ERR-S`, `ERR-DIG`); ELM's curation
(`nn_corpora.elm.PARSE_RECIPES`) names them per entry from ERR-ANALYS. Where the two disagree, the evaluated corpora
use the columns ERR-ANALYS supports (§4.2). Two shared records, D0295002 and O0392007 (`elm` against
`kduq_evaluated`), still differ, by under 1 %: ELM adds the reader error `ERR-DIG` to the authors' column.

- Per-record changes: [AUTHOR_ERRORS_DIFF.md](AUTHOR_ERRORS_DIFF.md) (generated).
- The statements in the publications behind every rule, with page, table and figure references and verbatim
  quotes: [AUTHOR_UNCERTAINTY_SOURCES.md](AUTHOR_UNCERTAINTY_SOURCES.md).
- The publications, with DOIs and EXFOR links: [../papers/INDEX.md](../papers/INDEX.md).

## Contents

1. [How reader uncertainties are identified](#1-how-reader-uncertainties-are-identified)
2. [The rule](#2-the-rule)
3. [Records whose values were replaced: Doering (p,n)](#3-records-whose-values-were-replaced-doering-pn)
4. [Records whose uncertainties were changed](#4-records-whose-uncertainties-were-changed)
5. [Normalisation uncertainties](#5-normalisation-uncertainties)
6. [Records removed](#6-records-removed)
7. [How the corrections are applied and checked](#7-how-the-corrections-are-applied-and-checked)

## 1. How reader uncertainties are identified

A subentry's uncertainty columns are classified from the free-text ERR-ANALYS of the subentry and of the entry's
common subentry 001, not from the column labels:

- **reader:** `ERR-DIG`, or any column ERR-ANALYS describes as a data-point reader, reading or digitisation
  uncertainty (often `DATA-ERR` in older releases);
- **systematic:** a numbered `ERR-n` column with the same value in every row (a normalisation-type error);
  `ERR-SYS`, monitor (`MONIT-ERR`), beam-polarisation (`POL-BM-ERR`) and auxiliary-quantity (`MISC`) errors; and the
  columns §4.2 names as common;
- **author:** every other uncertainty column on the observable (`ERR-T`, `ERR-S`, a `DATA-ERR` the authors gave).

A point is *reader-only* if a reader column is present and every author column is blank or zero there.

The labels can't be trusted on their own because EXFOR relabels columns between releases. Between 2019 and 2023
the compilers renamed `DATA-ERR → ERR-DIG` in many entries, and in Fricke et al. (O0328, 2023) the authors' errors
moved from `ERR-T` to `ERR-1`. The uncertainty-preference rule of the corpus supplement (`ERR-T`, then `DATA-ERR`,
…, `ERR-DIG`) predates these changes, so on the 2025 database it fell back to the reader column for these records.

The "constant `ERR-n` is systematic" rule is a heuristic. Where an entry files the authors' per-point error as a
single common value, as Dicello et al. (O0253, `ERR-1` "relative uncertainties" 2 %) and Van Hall et al. (O0091,
`ERR-1` "relative error" 3 % / 2 %) do, the classification calls the points reader-only. The per-paper rule then
supplies that same author value, so the result is still correct.

## 2. The rule

At every reader-only point the uncertainty becomes

  σ = σ_reader ⊕ σ_author  (sum in quadrature)

where σ_reader is EXFOR's reader uncertainty (the largest reader column, where there are several) and σ_author is
the authors' uncertainty, taken from the best source available:

1. a tabulation by the authors (Doering, §3);
2. EXFOR's own author column, filled by interpolation in angle where it is blank (Fricke, §4);
3. a statement in the paper's text, as a relative error for cross sections and an absolute error for analysing
   powers (Ay) (§4).

The reader term is kept because the values themselves were read off a figure. A record with reader-only points and
no usable author statement is removed (§6).

Where EXFOR does give an author error, the record must carry it: its error may not be below the author error at any
point. Most records already do. Where a column-preference rule took the wrong column, or folded a normalisation into
the per-point error, the error columns are re-read from ERR-ANALYS (§4.2).

## 3. Records whose values were replaced: Doering (p,n)

**R. R. Doering, D. M. Patterson, A. Galonsky, Phys. Rev. C 12, 378 (1975); EXFOR O0178.** 48Ca, 90Zr, 120Sn,
208Pb (p,n) to the isobaric analogue state at 25, 35 and 45 MeV: 12 records (O0178006–O0178017), in ELM and sm3
(`charge_exchange`).

EXFOR digitised these from Fig. 3 of the paper, with a 7 % reader uncertainty at every point and the authors' bars
only where they were legible. The three 25 MeV sets on 48Ca, 90Zr and 120Sn have no author error at any point.

The same angular distributions are tabulated, with errors, in Table 5 of Doering's PhD thesis (Michigan State
University, 1974, open access: [doi:10.25335/8r9s-9621](https://doi.org/10.25335/8r9s-9621)). The thesis says
the errors combine in quadrature the statistical and systematic uncertainties of the peak fitting. **For all 12
records, the angles, cross sections and errors are those of Table 5**, not EXFOR's digitisation:

- The transcription is [external/doering_1974_table5.csv](../external/doering_1974_table5.csv): 377 rows, 32 per
  set, apart from 25 at 48Ca 45 MeV. Two independent transcriptions agree on 376 rows; the remaining row was
  resolved from a higher-resolution scan. The table reproduces the thesis's integrated cross sections (Table 6),
  and the median ratio of table to EXFOR values is 0.98.
- Point counts change where EXFOR's digitisation had a different number of points, e.g. 48Ca 25 MeV goes from 36
  to 32. In particular, **the 208Pb 45 MeV EXFOR points at 161.9° and 164.0° (0.049 and 0.072 mb/sr) are gone**:
  Table 5 ends at 160.1° and has nothing near those values. They are most likely artefacts of reading Fig. 3.
- Errors run from 1.5 % at forward angles to over 100 % at the deepest backward minima.
- Normalisation: 11.2 %. That is the authors' "about 10 %" from the neutron-detection efficiency (EXFOR `ERR-1`)
  ⊕ the "less than 5 %" they give for target thickness, beam integration and neutron attenuation, taken at its
  bound.

## 4. Records whose uncertainties were changed

### 4.1 Author uncertainties supplied from the publication

Values are unchanged. "σ" is the relative per-point error added for cross sections; "Ay" is the absolute error
added for analysing powers. Confidence: **high** means tabulated or stated as a measured error; **medium** means
stated as a fit weight, a bound or a minimum, or ambiguous in units; **low** means inferred.

| entry | publication | records | author uncertainty applied | confidence |
|---|---|---|---|---|
| O0328 | Fricke, Gross, Morton, Zucker, PR 156, 1207 (1967) | 40 MeV, 59Co, 68Zn, 120Sn; σ: 004, 005, 007; Ay: 009, 010, 011 (elm, kduq_evaluated, chuq_evaluated, sm3) | EXFOR `ERR-1` (the authors' bars, see below), filled where blank | high where present; medium where filled |
| O0157 | Devins, Forster, Gigas, NP 35, 617 (1962) | 30.8 MeV 60Ni (002, kduq_evaluated), 208Pb (004, elm) | σ rising linearly in angle from 3.5 % (most forward point) to 10 % (most backward point) | medium |
| O0124 | Put, Urone, Paans, PLB 35, 311 (1971) | 30.4 MeV 28Si (002, kduq_evaluated), 120Sn (004, elm) | σ 5 % (the fit weight; "the experimental error was always smaller") | medium |
| O0169 | Wassenaar et al., J. Phys. G 15, 181 (1989) | 20.4 and 24.6 MeV Ni, Sr, Cd, Sn, σ and Ay (elm, kduq_evaluated, chuq_evaluated) | σ 2 %; Ay 0.02 (stated minima 2 % and 0.01; Ay bars are larger) | high (σ), medium (Ay) |
| O0239 | Lombardi et al., NPA 188, 103 (1972) | 14–16.3 MeV 40Ca and 48Ca, σ and Ay (elm) | σ 2 % (assigned for angular misalignment; statistics 1 %); Ay 0.02 ("typical errors 2 %") | high (σ), medium (Ay) |
| O0246 | Kruse et al., NPA 169, 177 (1971) | 16 MeV 148Sm (017, elm) | σ 10 % ("arbitrarily assigned to each point" for fitting) | medium |
| O0253 | Dicello, Igo, Leland, Perey, PRC 4, 1130 (1971) | 14–21.7 MeV 40Ca, 10 energies (017, elm) | σ 2 % ("relative uncertainties are approximately ±2 %"); EXFOR carries the same 2 % as constant `ERR-1`, so the total is as curated | high |
| O0471 | Burger & Heymann, NPA 243, 461 (1975) | 12.52 MeV 92Mo, 94Mo (007, 008, elm) | σ 6 % ("not more than 6 %") | medium |
| O0545 | Stautberg & Kraushaar, PR 151, 969 (1966) | 19.4 MeV 92Zr, 94Zr (002, 006, elm) | σ 1 % below 90°, 3 % above (statistical upper bounds; the paper's 90° is applied to the corpus's c.m. angle) | high |
| O0549 | Sinha et al., NPA 183, 401 (1972) | 19.85–49.45 MeV 92Mo, 94Mo (003, 005, elm) | σ 4 % ("typically ~4 %"); Ay 0.03 | high |
| O0552 | Rathmell & Haeberli, NPA 178, 458 (1972) | 12.98 MeV 208Pb (008, elm) | σ 1.5 % (middle of the stated 0.5–3 %); Ay 0.01 | high |
| O0091 | Van Hall et al., NPA 291, 63 (1977) | 17.2–24.6 MeV Fe and Ni isotopes, σ and Ay (kduq_evaluated, chuq_evaluated) | σ 3 % (Fe), 2 % (Ni), as assigned by the authors; Ay 0.02 (read from the figures) | high (σ), low (Ay) |
| O0300 | Kwiatkowski & Wall, NPA 301, 349 (1978) | 100.4 MeV 90Zr, 120Sn (004, 005, kduq_evaluated) | σ 4 % ("of order ±4 % for relative cross sections") | high |
| O0456 | Brussel & Williams, PR 114, 525 (1959) | 39.8 MeV 54Fe, 56Fe (002, 003, kduq_evaluated) | σ 3 % ("statistical accuracy of ~3 %") | high |
| O1104 | Petit et al., J. Phys. G 20, 1955 (1994) | 22.3 MeV 106–116Cd, σ and Ay (chuq_evaluated) | σ 2 %; Ay max(0.02 \|Ay\|, 0.01) ("a minimal error of 2 % was assumed") | high (σ), medium (Ay) |

**Fricke (O0328).** EXFOR's `ERR-1` ("statistical errors and the uncertainty in background subtraction") matches,
word for word, the paper's definition of its error bars. It is absolute, in the data's units, although labelled
PER-CENT. The bars were legible only at some points (e.g. 10 of 34 for 120Sn Ay), so the others are filled:

- the relative error (cross sections) or absolute error (Ay) is interpolated linearly in angle between the nearest
  points that have one;
- beyond the first and last such point the value is held constant (e.g. 6 % forward and 14.8 % backward for 120Sn
  cross sections).

Each point's error is then EXFOR's `ERR-DIG` ⊕ `ERR-1`.

### 4.2 Error columns re-read from ERR-ANALYS

For these entries the per-point error is rebuilt as EXFOR's reader column (if any) ⊕ the authors' per-point
columns, and the normalisation is taken from the authors' common column (§5). These are the columns ERR-ANALYS
describes; ELM's curation already read most of them this way. A record whose error already equals the result to
within 5 % is left as it is.

| entry | publication | records | per-point error | normalisation | what was wrong |
|---|---|---|---|---|---|
| O0302 | Roos & Wall, PR 140, B1237 (1965) | 160 MeV 40Ca, 120Sn, 208Pb, 58Ni (elm, kduq_evaluated) | `ERR-DIG` ⊕ `DATA-ERR1` ("5 % for the relative cross sections") | `DATA-ERR2`, 7 % ("for the absolute cross sections") | `kduq` took `ERR-DIG` alone: 0.4 % |
| O0434 | Baron, Leonard, Lind, PR 180, 978 (1969) | 21.3 MeV 58Ni σ (008, kduq_evaluated) | `DATA-ERR` ⊕ `ERR-S` (overall "less than 5 %") | default 5 % | `kduq` took `DATA-ERR`, the reader error: 3 % |
| O0287 | van Oers et al., PRC 10, 307 (1974) | 21–47.3 MeV 208Pb (004–010, elm) | `DATA-ERR` ⊕ `ERR-T` (the authors' "less than 3 %") | default 5 % | `elm` took `DATA-ERR`, the reader error. Since 2026-10-14 these digitisations are removed as duplicates of the tables 011–017 (§6); the rule is kept for reference |
| O0287 | van Oers et al. | 185 MeV 208Pb (002, elm, kduq_evaluated) | `DATA-ERR` | `ERR-1`, 8.3 % (calibration, target thickness) | `kduq` defaulted to 5 % |
| O0142 | Ridley & Turner, NP 58, 497 (1964) | 30.3 MeV Ca, Fe, Ni, Sn, Pb (elm, kduq_evaluated; 120Sn also sm3) | `ERR-T` | `ERR-1` (target thickness), 1–5 % | `kduq` defaulted to 5 % |
| T0101 | Nadasen et al., PRC 23, 1023 (1981) | 80–182 MeV 40Ca, 90Zr, 208Pb (elm, kduq_evaluated) | `DATA-ERR` (total relative) | `DATA-ERR1`, 10 % ("8–10 %") | `kduq` defaulted to 5 % |
| 10633 | Ferrer, Carlson, Rapaport, NPA 275, 325 (1977) | 11 MeV (n,n), 17 targets (elm, kduq_evaluated, chuq_evaluated) | `DATA-ERR1` (relative) | `DATA-ERR2`, 3.5 % ("normalization error") | `kduq` and `chuq` summed `DATA-ERR2` into every point and added the default 5 % on top |
| 12701 | DeVito, thesis (1980) | 30.3, 40 MeV 208Pb (n,n) (elm, kduq_evaluated, sm3) | `DATA-ERR1` (relative) | `DATA-ERR2`, 2.6 % | as 10633 |
| 22987 | Öhrn et al., PRC 77, 024605 (2008) | 96 MeV 56Fe, 89Y, 208Pb (n,n) (002, 003: test_evaluated; 004: elm, test_evaluated) | `ERR-T` (statistics, background, multiple scattering) | default 5 % | `elm` took `ERR-S`, the statistical part; `test` already carries `ERR-T` |

Columns named common, not per-point:
- **22987 `ERR-1`:** the cross-section change from the ~1° angle uncertainty of the target and chamber positions,
  an offset common to the data set (up to 40 % at the forward minima).
- **D0289 `DATA-ERR1`, `DATA-ERR`:** an undescribed constant 5 % (cross sections), and the polarimeter calibration
  (analysing powers).
- **O0090 `ERR-T`:** "an absolute error in the cross section of 10 %, including the uncertainty in the measured
  efficiency".

Also:
- **O0091 (Van Hall), analysing powers, kduq_evaluated and chuq_evaluated:** at the points where EXFOR has the
  authors' `DATA-ERR` (0.02–0.04), the curated records used the reader error `ERR-DIG` (0.01). These points now
  carry `ERR-DIG` ⊕ `DATA-ERR`.
- **F1100 (Kurepin, Madsen & Albek, Izv. AN SSSR 31, 195 (1967)), 148Sm 12 MeV, elm:** EXFOR has no per-point author
  column, and `ERR-DIG` is about 0.001 %. ERR-ANALYS quotes the authors: "5 % at 20°, 2–3 % beyond 30°". The record
  now carries 5 % below 30° and 3 % from there on, ⊕ `ERR-DIG`, with `ERR-SYS` (4 %) as its normalisation. This is
  from EXFOR's quotation; the publication was not checked.

- **10817 (Rapaport et al., NPA 341, 56 (1980)), Sn(n,n) 11 and 24 MeV (006–010), elm, sm3:** ERR-ANALYS gives
  the total uncertainty as ERR-T 5–15 % (statistics, monitor, multiple scattering, inelastic and compound
  contributions, angle, detector efficiency), but EXFOR files no ERR-T column: the data carry only `DATA-ERR`, the
  "absolute" part (geometry, yields, monitor), 3–6 %. Each point now carries max(`DATA-ERR`, total), the total read
  as rising linearly with angle from 5 % (most forward point) to 15 % (most backward), as for Devins (O0157)
  (`author_errors.TOTAL`). Found comparing 124Sn(n,n) 11 MeV with Pruitt (14662004, removed, §6), 2026-10-14.

- **Angle-integrated data (neutron total, proton reaction), 2026-10-14:** the authors' normalisations where stated,
  Finlay et al. (13569: < 3 % for 40Ca and 90Zr, < 0.5 % for 208Pb), Auce et al. (D0356 ERR-SYS, 2–4 %), Dicello &
  Igo (O0341, 4 % ⊕ 2 %) and Menet et al. (O0081, 5 %); and Pruitt et al.'s per-point ERR-SYS (14661) added in
  quadrature (`SYS_COLUMN`).

**Already author-based, not changed:**
- Fulmer et al. (O0211), whose tables carry per-point errors: only the normalisation changes (§5).
- Van der Bijl et al. (F0733003, sm3, 90Zr 25.05 MeV), where sm3 curation already uses the authors' 3 % from
  ERR-ANALYS. This is the one record the reader-error test allowlists.

## 5. Normalisation uncertainties

Each record's `systematic_normalization_error` defaults to 5 % where EXFOR reports none. Where the authors state
their own, it is used instead. Cross sections and analysing powers are treated separately. Target thickness, beam
integration and detector efficiency scale absolute cross sections but cancel in an analysing power, whose scale is
set by the beam polarisation. Ay records take only an Ay statement (Fricke's beam polarisation); the others keep
the normalisation they were curated with.

| entry | records | normalisation | authors' statement |
|---|---|---|---|
| O0178 | Doering (p,n), all 12 | 11.2 % | neutron-detection efficiency "about 10 %" ⊕ other systematics "less than 5 %" |
| O0239 | Lombardi, cross sections | 10 % | Rutherford normalisation at 4 MeV, "accurate to within 10 %" |
| O0300 | Kwiatkowski & Wall | 8 % | "better than 8 % accuracy for the absolute cross sections" |
| O0211 | Fulmer tables 012, 015, 016, 017 | 11.2 % | target thickness ~5 % ⊕ charge collection ~10 % |
| O0328 | Fricke, cross sections | 5.4 % | target thickness 5 % (paper) ⊕ current integration 2 % (EXFOR `ERR-2`; not in the paper's text) |
| O0328 | Fricke, analysing powers | 1.8 % | beam polarisation (27.4 ± 0.5) %, "including the uncertainty in P_C" |
| O0302, O0287002, O0142, T0101, 10633, 12701 | the authors' common columns | 7 %, 8.3 %, 1–5 %, 10 %, 3.5 %, 2.6 % | see §4.2 |

The remaining corrected entries keep the default 5 %. Several papers state none, or normalised their data to an
optical-model fit or to other measurements (O0091, O0124, O0169, O1104). For those, the normalisation is better
treated as free in a fit.

## 6. Records removed

Records are removed from the evaluated corpora for three reasons: no author statement of their per-point uncertainty
could be found (47 records), they duplicate tabulated data (11), or they are inconsistent with independent data (C0622,
14662004). [AUTHOR_ERRORS_DIFF.md](AUTHOR_ERRORS_DIFF.md) lists each removed record. ELM removes them during curation
(`elm_curate.finalize`), so `sm3`, which takes its records from ELM, never holds them; the evaluated copies drop
them when they are built. The static corpora keep them, so [spec/known_missing.csv](../spec/known_missing.csv), which
accounts for the static corpora, doesn't list them.

**Duplicates.** ELM held both EXFOR's figure digitisations (STATUS CURVE, reader errors only) and the authors' own
tables (STATUS TABLE, with errors) of Fulmer et al. 61.4 MeV elastic scattering, PR 181, 1565 (1969). The
digitisations O0211004 (40Ca), O0211007 (90Zr), O0211008 (116Sn) and O0211009 (208Pb) are removed; the tables
O0211012/015/016/017 stay, as in `kduq`. Likewise van Oers et al. 208Pb(p,p) 21–47.3 MeV, PRC 10, 307 (1974): ELM
held both the digitisations O0287004–010 (flat 6 % reader error) and the tables with the authors' per-point errors
O0287011–017 (B. Clark's collection; the version sm3 uses) at all seven energies. The digitisations are removed
(found by the elm_lane data audit, 2026-10-14).

**Inconsistent with independent data** (`DROP_INCONSISTENT`, 2026-10-14). A set is removed only when it disagrees
with independent data on the same target at the same energy:
- **C0622, Moyer, Finlay et al., NPA 352, 221 (1981), 92Mo(p,p) 25–45 MeV (4 records, elm):** 0.1–0.7 % errors with
  no normalisation; 1.4–2.5× off KD03 away from forward angles and about 2× off D0295010 at 30 MeV.
- **14662004, Pruitt, thesis, Washington University (2019), 124Sn(n,n) 11 MeV (elm, test_evaluated):** 1.4–2.5×
  Rapaport et al. (10817010) at the same energy, and 1.57× KD03 (median), while Pruitt's own 17 MeV set (14662005)
  agrees with KD03 (0.95). The excess follows the elastic maxima, a scale error: TALYS's compound elastic
  (0.003 mb) and 2+ inelastic (2–5 mb/sr, against an excess of 12–110 mb/sr) do not account for it, and 10 % errors
  on both sets still leave χ² = 46 for 16 points.

**No author uncertainty.** In the table below, "Not stated" means the paper gives no per-point error and shows no
legible bars. The last column is what the paper does offer: a set could be restored with that value.

| entry | publication | removed records (corpus, observable, target, energy MeV) | reason | what the paper offers |
|---|---|---|---|---|
| F1173 | Kurepin & Lombard, Izv. AN SSSR 36, 2232 (1972) | F1173002 (`elm`, σ, 148Sm, 24.5) | publication not available; EXFOR has author errors at 3 of 24 points | — |
| O0083 | Colombo et al., JPSJ Suppl. 44, 543 (1978) | O0083016 (`kduq_evaluated`, σ, 56Fe, 35.2), O0083019 (`kduq_evaluated`, σ, 27Al, 35.2) | publication not available | — |
| O0372 | Matsuda et al., JPSJ 22, 1311 (1967) | O0372013 (`elm`, `kduq_evaluated`, σ, 90Zr, 14.71), O0372014 (`elm`, σ, 92Zr, 14.25) | publication not available | — |
| O0446 | Kobayashi et al., JPSJ 15, 1151 (1960) | O0446002 (`kduq_evaluated`, σ, 58Ni, 10.7, 14.4, 15.4), O0446003 (`kduq_evaluated`, σ, 60Ni, 14.4, 15.4) | publication not available | — |
| O0079 | Tesmer & Schmidt, PRC 5, 864 (1972) | O0079006 (`kduq_evaluated`, σ, 54Fe, 19.6) | not stated | — |
| O0225 | Wagner et al., PRC 12, 757 (1975) | O0225146 (`elm`, σ, 208Pb, 35) | not stated; bars smaller than the symbols | normalisation 5 % (fixed by an optical-model fit) |
| O0254 | Baugh et al., NP 65, 33 (1965) | O0254009 (`kduq_evaluated`, σ, 28Si, 17.8), O0254010 (`elm`, σ, 40Ca, 17.8) | not stated; relative cross sections only | "same order of statistical accuracy as the polarization values" (1–4 %) |
| O0259 | McDaniels et al., PRC 33, 1943 (1986) | O0259002 (`elm`, σ, 208Pb, 200) | not stated; data partly from another experiment | agreement with TRIUMF data within ±7 % |
| O0272 | Lee et al., PLB 205, 219 (1988) | O0272002 (`elm`, σ, 208Pb, 200) | not stated; details deferred to other references | — |
| O0370 | Gray et al., PR 142, 735 (1966) | O0370002 (`elm`, `kduq_evaluated`, σ, 90Zr, 18.8) | not stated; bars inside the symbols | normalisation about 5 % |
| O0382 | Yagi et al., PL 10, 186 (1964) | O0382002 (`elm`, σ, 40Ca, 55) | not stated; EXFOR has author errors at 2 of 18 points | normalisation ±15 % |
| O0384 | Gray et al., NP 67, 542 (1965) | O0384002 (`elm`, σ, 40Ca, 14.6), O0384003 (`elm`, σ, 40Ca, 17.3) | not stated | normalisation ±15 % |
| O0387 | Tellez et al., NPA 127, 438 (1969) | O0387002 (`elm`, σ, 48Ca, 12) | not stated; scale set by matching another data set | — |
| O0458 | Beuzit et al., NPA 128, 594 (1969) | O0458004 (`elm`, σ, 64Ni, 12) | not stated; scale normalised to another data set | — |
| O0553 | Rolland et al., NP 80, 625 (1966) | O0553004, O0553010 (`kduq_evaluated`, σ, 40Ca, 152, 75), O0553006, O0553014 (`kduq_evaluated`, σ, 209Bi, 153, 78) | statistical errors only "on the curves", not legible; numbers given for 12C only | normalisation 5 % (150 MeV), 10 % (75 MeV) |
| O0580 | Fretwurst et al., NPA 468, 247 (1987) | O0580002 (`elm`, σ, 94Mo, 25.6) | statistical bars inside the symbols; "point-to-point fluctuations … may occur, exceeding these statistical errors" | — |
| O1103 | Moonen et al., J. Phys. G 19, 635 (1993) | O1103004, O1103006 (`chuq_evaluated`, σ, 72Ge, 74Ge, 22.3), O1103012, O1103014 (`chuq_evaluated`, σ, 78Se, 80Se, 22.3) | not stated | the same group states 2 % in O1104 |
| O1109 | Moonen et al., J. Phys. G 19, 1191 (1993) | O1109002, O1109004, O1109006, O1109008 (`chuq_evaluated`, σ, 64–70Zn, 20.4), O1109005 (`chuq_evaluated`, Ay, 66Zn, 20.4) | not stated | the same group states 2 % in O1104 |
| F1407 | Gubin et al., Izv. AN SSSR 38, 133 (1974) | F1407013 (`elm`, σ, 64Ni, 5.9–6.2) | EXFOR: "no source of uncertainties is given" for 64Ni; publication not checked | 5–7 % absolute error at small angles (EXFOR ERR-ANALYS) |
| O1823 | Blankert, Blok & Blok, NPA 356, 74 (1981) | O1823002 (`elm`, σ, 112Sn, 27.45) | EXFOR gives the error only for the (p,d) data (statistics ⊕ 3 % relative normalisation); publication not checked | — |
| F0930 | Arking et al., NPA 155, 480 (1970) | F0930002 (`elm`, σ, 120Sn, 9.85) | only the absolute uncertainty is stated (EXFOR); publication not checked | normalisation 5 % |
| O1199 | Fabrici et al., PRC 21, 830 (1980) | O1199008 (`elm`, Ay, 40Ca, 35), O1199009 (`elm`, Ay, 40Ca, 26.3, 40) | nothing stated for Ay; no bars | the companion paper PRC 21, 844 may |

**To restore a removed set:**
1. Delete its subentry from `DROP_FLAGGED` in [src/nn_corpora/author_errors.py](../src/nn_corpora/author_errors.py).
2. Add a `PER_PAPER` rule citing the source.
3. Regenerate the data (§7).

## 7. How the corrections are applied and checked

**Where.** [src/nn_corpora/author_errors.py](../src/nn_corpora/author_errors.py) holds every rule: `DROP_FLAGGED`,
`DROP_DUPLICATES`, `DROP_INCONSISTENT`, the Doering table, `COLUMN_AUTHOR`, `COLUMNS`, `COMMON`, `PER_PAPER`, `TOTAL`, `NORM` and `NORM_AY`. `author_errors.SCOPE`
lists the corpora they apply to, and `author_errors.EVALUATED` names the evaluated copy of each static corpus.

- **ELM:** removals take effect in `elm_curate.finalize`, and every record passes through `author_errors.correct`
  in `serialize.write_sector`, so rebuilding ELM from its notebooks applies them all. sm3 is corrected the same way
  when `scripts/curate_sm3.py` writes it.
- **`scripts/apply_author_errors.py`:**
  - builds the evaluated copy of each static corpus registered with one (`kduq_evaluated`, `chuq_evaluated`,
    `test_evaluated`, and any newly added tabulated corpus, [ADDING_A_CORPUS.md](ADDING_A_CORPUS.md));
  - with `--elm`, also re-corrects ELM in `data/` directly, starting from the uncorrected records at a fixed git
    revision, so a rule change reaches ELM without rerunning its notebooks. Do not pass it after rebuilding ELM
    from the notebooks: it would replace the rebuild with that revision's data;
  - writes [AUTHOR_ERRORS_DIFF.md](AUTHOR_ERRORS_DIFF.md) (`--report`; ELM rows only with `--elm`).

  It never writes to the static corpora.
- **ELM calibration evaluation:** after these corrections, ELM records also pass through
  [src/nn_corpora/elm_evaluation.py](../src/nn_corpora/elm_evaluation.py) (excluded targets, a 2 % error floor;
  [ELM_CALIBRATION_DATA.md](ELM_CALIBRATION_DATA.md)). sm3 undoes it for the records it copies.

Since the ELM rebuild from 0 MeV (2026-10-14), ELM is rebuilt from its notebooks, so `--elm` writes only the report
(`--dry-run`); ELM's rows in it compare the 10–200 MeV records of the baseline:

```bash
source scripts/setup_exfor_db.sh 2025
uv run pytest --nbmake notebooks/elm/ && uv run python scripts/curate_elm_integral.py
uv run python scripts/apply_author_errors.py
uv run python scripts/apply_author_errors.py --elm --dry-run --report docs/AUTHOR_ERRORS_DIFF.md
uv run python scripts/curate_sm3.py && uv run python scripts/build_manifests.py
```

**Provenance in each record.** A corrected record's `notes` say what was done, at how many points, and from which
publication, and end with the marker `author-errors v4 (docs/AUTHOR_UNCERTAINTIES.md)`. The marker also keeps the
correction from being applied twice.

**Tests** ([tests/test_reader_errors.py](../tests/test_reader_errors.py)):
- the static corpora carry no correction, and each evaluated copy holds the same records less the removals;
- no removed record remains in an evaluated corpus;
- the Doering records equal the thesis table;
- correcting a corrected record changes nothing;
- a corrected record has the same uncertainties and normalisation in every evaluated corpus it appears in;
- analysing powers carry only an Ay normalisation;
- the following check each record against its EXFOR subentry (marked `slow`; they need the EXFOR database):
  - every record with reader-only points is corrected;
  - no point's error is below the author error EXFOR gives for it;
  - a per-paper correction covers exactly those points;
  - Fricke's errors equal `ERR-DIG` ⊕ `ERR-1` wherever `ERR-1` is given.

**Audit.** `uv run python scripts/audit_reader_errors.py [corpus ...]` lists every record with reader-only points in
EXFOR, or with points whose error is below EXFOR's author error, and whether it is corrected. By default it covers the evaluated
corpora; name a static corpus (`kduq`, `chuq`, `test`) to see what it carries.

**Matching records to EXFOR rows.** Points are matched by angle (within 0.06°). Where EXFOR gives laboratory angles
and the corpus converted them to centre-of-mass, the points are matched in order instead. This is allowed only when
the record has the same number of points and no angle moved by more than 5°. A record that can't be matched stops
the correction with an error rather than being corrected blindly.

**Units.** EXFOR's absolute errors are converted to a record's units by the ratio of the record's value to EXFOR's at
each point (a unit change, or a ratio to Rutherford). A point whose ratio is off its neighbours' by more than a
factor 3 is a value the curation rescaled (ELM's point fixes, e.g. one 12701005 point by 10); it keeps EXFOR's
absolute error.
