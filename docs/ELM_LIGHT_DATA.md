# ELM-light calibration data (branch elm-light-data)

A corpus `data/elm_light` built the way `data/elm` is (docs/ELM_CALIBRATION_DATA.md): EXFOR query, curation decisions
in code, author errors, the ELM calibration evaluation (2 % floor), TALYS compound elastic. It serves ELM-Lane-light,
the ELM-Lane model forms on light targets.

**Scope (Kyle, 2026-11-10).** Even-even targets 12 ≤ A ≤ 40, deformed or not, except 40Ca (in `data/elm`):
`spec.ELM_LIGHT_TARGETS`. Natural targets as their dominant isotope where it is at least 90 % (natC, natO, natNe,
natSi, natS, natAr; `spec.ELM_LIGHT_NATURAL`; the rule was ~99 % until 2026-11-11, item 5); natMg (79 % 24Mg) is not
used. Which targets a calibration uses is
decided in the calibration, not here. Compound elastic as for ELM; the calibration chooses its energy floors from
the CE report below.

**Decisions after the survey (Kyle, 2026-11-10).**
1. 36S and 36Ar are dropped. EXFOR holds nothing for 36S, and for 36Ar only (p,p) excitation functions below
   ~3.4 MeV (F0980, F1005) and σ_tot below 6 keV (11570, 11573), none inside the survey's windows (§1).
2. The thin targets are kept: 14C, 22Ne, 30Si and 38Ar carry mostly (p,n) to the IAS and little else, but they are
   the only (p,n) data on those isotopes. Whether a calibration uses them is decided there. (22Ne and 38Ar later
   dropped, item 4.)
3. The ~99 % natural rule stays. natSi and natS are not used, although they hold the only Si and S σ_tot above
   ~19 MeV and ~10 MeV (34 and 33 sets up to 200 MeV).
4. After curation, 22Ne and 38Ar were dropped too: their only data, (p,n), do not isolate the IAS (section 2).
5. **2026-11-11: natural targets at >= 90 % (Kyle; supersedes item 3).** Reviewing the (n,n) papers showed that EXFOR
   codes many natural-sample measurements as the dominant isotope; only the SAMPLE text says so (e.g. Virdis 21773,
   "SAMPLE (12-MG-24,NAT=0.79)"). Of the records filed as 28Si, 32S, 24Mg and 20Ne, 31, 22, 3 and 2 elastic were natural
   samples, including 28Si training sets (σ_tot, (p,p) at 10.6, 20.5 and 40 MeV). Applied consistently, the 99 % rule
   would have left 28Si with almost no data. Natural Ne (90.5 %), Si (92.2 %) and S (95.0 %) are now used as 20Ne, 28Si
   and 32S, both when EXFOR codes them as natural and when it codes them as the isotope (`elm_light.natural_sample`,
   records flagged `natural_target`). Natural Mg samples are dropped wherever EXFOR files them (21773002/010, 21490002,
   D0191002). An admixture of 5-10 % neighbouring isotopes changes elastic and σ_tot by about a percent; for Mg (21 %,
   with 25Mg states at 0.59 and 0.98 MeV unresolved in time-of-flight) it does not.

`spec.ELM_LIGHT_TARGETS` is therefore 12 targets: 12,14C, 16,18O, 20Ne, 24,26Mg, 28,30Si, 32,34S, 40Ar.

**How it is built.** ELM's curation runs as notebooks (`notebooks/elm/`); ELM-light runs as one script,
`scripts/curate_elm_light.py`, with every decision in `src/nn_corpora/elm_light.py` and the full record of what was
excluded, repaired and dropped in `docs/elm_light_curation_report.txt` (and, with `--plots`, every data set plotted in
`build/elm_light_plots.pdf`, not committed). Tests: `tests/test_elm_light_evaluation.py`.

**IAS energies** (`spec.ELM_LIGHT_EX_IAS`): ENSDF via the IAEA LiveChart API (2026-11-10), the lowest 0⁺ level with
T = (N−Z)/2 in (A, Z+1). They agree with elm_light's `LIGHT_EX_IAS` to 0.3 keV where both exist.

## 1. Survey (scripts/survey_elm_light.py, 2026-11-10; X4-2025-12-31)

Run before the decisions above, so it still lists 36S and 36Ar (and `survey_elm_light.py` now skips them). Read-only: what EXFOR holds per target and observable, before any curation decision. Raw counts, in the windows of
`spec` (elastic and Ay 0–200 MeV with ≥ 5 points; (p,n) to the IAS ±0.3 MeV, 5–200 MeV; σ_tot and σ_R 0.1–200 MeV).
σ_R counts EXFOR (p,non) and (p,R) together. Excluded natural targets are listed for information only. Machine-readable:
`docs/elm_light_survey.csv`.

EXFOR cells: entries/sets/points (energy span, MeV); 'unparsed': entries exfor_tools failed to parse (curation may recover them). Corpora: sets in kduq / test / chuq.

| target | nn | pp | nAy | pAy | pn | ntot | pR | corpora |
|---|---|---|---|---|---|---|---|---|
| 12C | 32/95/1205 (0.5–185), 22 unparsed | 30/166/3837 (1.36–200), 38 unparsed | 11/107/927 (1.9–18.2), 5 unparsed | 26/112/2875 (3.5–200), 9 unparsed | — | 36/40/19309 (0.1–198), 8 unparsed | 10/11/98 (16.5–180), 2 unparsed | — |
| 14C | 0 | 1/1/21 (14.5–14.5), 3 unparsed | 0 | 1/15/210 (3.8–6.68) | 4/12/153 (7.2–45), 2 unparsed | 0 | 0 | — |
| 16O | 14/22/353 (0.9–26), 11 unparsed | 18/48/1487 (1.79–200), 16 unparsed | 2/9/67 (2.25–3.9), 3 unparsed | 14/35/816 (3–200), 4 unparsed | — | 10/12/476 (0.102–151), 2 unparsed | 3/3/29 (20.9–138), 1 unparsed | — |
| 18O | 2/43/484 (5.07–24), 3 unparsed | 3/18/257 (5.59–24.5), 3 unparsed | 0 | 0 (1 unparsed) | 1/1/20 (35–35), 2 unparsed | 6/6/897 (0.145–196) | 0 | — |
| 20Ne | 0 (1 unparsed) | 5/21/291 (3.65–65), 4 unparsed | 0 | 2/2/52 (65–65) | — | 0 (1 unparsed) | 1/1/5 (22.9–47) | — |
| 22Ne | 0 | 0 (1 unparsed) | 0 | 0 | 1/1/15 (35–35) | 1/1/121 (0.14–1.94), 1 unparsed | 0 | — |
| 24Mg | 2/2/24 (1.5–6.1), 2 unparsed | 16/29/777 (2.6–135), 10 unparsed | 1/1/10 (1.5–1.5) | 9/117/1667 (3.99–185), 2 unparsed | — | 2/2/1656 (0.164–5.19) | 1/1/7 (17.5–48) | nn: kduq 4; pp: test 1 |
| 26Mg | 1/1/23 (24–24) | 5/114/754 (1.5–12.6), 5 unparsed | 0 | 1/1/25 (20.3–20.3) | 3/6/115 (23–35), 3 unparsed | 1/1/22 (0.105–0.37) | 0 | — |
| 28Si | 9/16/210 (0.8–21.7), 7 unparsed | 11/23/477 (4.95–180), 12 unparsed | 0 (1 unparsed) | 10/21/404 (5.75–200), 2 unparsed | — | 3/3/11274 (1.75–19) | 1/1/1 (65.5–65.5) | nn: kduq 1, test 2; pp: kduq 8; pAy: kduq 7; pR: kduq 1; nAy: test 2 |
| 30Si | 0 | 2/2/57 (40.8–180), 1 unparsed | 0 | 1/1/28 (180–180) | 1/1/13 (35–35) | 0 | 0 | — |
| 32S | 8/69/470 (0.641–21.7), 4 unparsed | 6/31/424 (1.9–65), 7 unparsed | 0 (1 unparsed) | 1/1/23 (65–65), 1 unparsed | — | 1/1/1913 (0.75–10.3) | 0 | nn: kduq 1, test 7; nAy: test 4 |
| 34S | 1/2/76 (21.7–25.5) | 2/2/28 (6.03–29.8), 1 unparsed | 0 | 0 | 2/2/33 (35–35) | 2/2/1134 (0.1–1.77) | 0 | — |
| 36S | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| 36Ar | 0 | 0 | 0 | 0 | — | 0 | 0 | — |
| 38Ar | 0 | 0 | 0 | 0 | 2/2/21 (35–135) | 0 | 0 | — |
| 40Ar | 0 (1 unparsed) | 6/21/646 (1.87–65), 7 unparsed | 0 (1 unparsed) | 6/9/240 (9.8–65), 1 unparsed | 2/2/29 (23–35), 1 unparsed | 2/3/12076 (0.1–150) | 1/1/5 (22.9–46.9) | nn: kduq 1 |
| natC (→ 12C, 98.93 %) | 25/609/5939 (0.5–75), 18 unparsed | 2/16/460 (10.2–30.6), 6 unparsed | 2/40/250 (0.5–2.19), 2 unparsed | 2/3/69 (29–49) | — | 91/109/24711 (0.1–200), 16 unparsed | 4/4/17 (16.2–180), 1 unparsed | — |
| natO (→ 16O, 99.76 %) | 12/81/1328 (0.41–26), 3 unparsed | 1/148/852 (3.99–5.99), 2 unparsed | 0 | 1/1/18 (10–10) | — | 41/46/14818 (0.102–200), 6 unparsed | 0 | — |
| natAr (→ 40Ar, 99.60 %) | 0 (2 unparsed) | 0 (1 unparsed) | 0 | 1/1/9 (7.6–7.6) | — | 5/5/1631 (0.1–88), 1 unparsed | 0 | nn: kduq 1, test 1 |
| natNe (excluded: < 99 %) | 0 (2 unparsed) | 0 | 0 | 2/2/27 (8–10.3) | — | 2/2/263 (0.157–19.8), 1 unparsed | 0 | — |
| natMg (excluded: < 99 %) | 8/14/185 (0.3–21.6), 6 unparsed | 1/125/750 (2.69–4.24), 6 unparsed | 0 | 3/3/38 (8.5–17.8) | — | 35/36/2412 (0.102–200), 3 unparsed | 1/1/1 (16.5–16.5), 2 unparsed | nn: kduq 8; ntot: kduq 1 |
| natSi (excluded: < 99 %) | 17/42/690 (0.3–75), 15 unparsed | 3/214/2055 (1.69–28), 4 unparsed | 2/4/64 (1.5–17), 1 unparsed | 1/52/1047 (1.69–3.68), 1 unparsed | — | 30/34/34716 (0.1–200), 12 unparsed | 2/3/66 (14–38.1), 1 unparsed | nn: kduq 18; pp: kduq 1; ntot: kduq 3; pR: kduq 2 |
| natS (excluded: < 99 %) | 12/21/366 (3.15–26), 14 unparsed | 0 (1 unparsed) | 1/3/59 (10–17) | 2/2/32 (10.4–17.8) | — | 33/33/7619 (0.1–200), 5 unparsed | 0 | nn: kduq 17; ntot: kduq 3, test 1 |

## 2. Curation (scripts/curate_elm_light.py, 2026-11-10)

`scripts/curate_elm_light.py` curates all five sectors from EXFOR (decisions in `src/nn_corpora/elm_light.py`) and
writes `data/elm_light/<sector>/` through the author-error and ELM evaluations (2 % floor, `MARK`). The full log is
`docs/elm_light_curation_report.txt`; `--plots` writes `build/elm_light_plots.pdf` (not committed).

- Elastic, Ay, (p,n): as ELM (`elm_curate`): ELM's parse recipes, then the supplement's uncertainty-column rule for
  parses those do not cover; ELM's entry exclusions except the heavy-target "duplicate of X" ones; `finalize`.
  Natural C, O, Ne, Si, S, Ar are munged as 12C, 16O, 20Ne, 28Si, 32S, 40Ar and flagged `natural_target`; so are
  natural samples EXFOR codes as the isotope (item 5 above).
- σ_tot and σ_R: every EXFOR (n,tot) / (p,non) SIG subentry on the targets becomes a spec row over 0.1–200 MeV and
  goes through the tabulated-corpus machinery (`corpus.curate`, as `curate_elm_integral.py`), no thinning. EXFOR
  codes no light-target σ_R as (p,R). Dropped: subentries without an uncertainty (~60, mostly old natC/natO
  transmission), and 6 whose incident column is not an energy (beam momentum, meV, none).
- Duplicates: the 17 `MANUAL_DROPS` of curate_light.py all still match; 4 added after this review (identical values:
  C0796002/003 = C0152, F0566003 = E2076, D0292002 = C1018004). The report then flagged 61 further pairs
  agreeing to < 3 %; Kyle chose to drop all possible duplicates, so each pair lost one record (below). The check
  compares angular distributions from different entries only, not σ_tot sets or subentries of one entry.

Records (sets / points; σ_tot and σ_R energy points), after all drops (2026-11-11):

| target | nn | pp | nAy | pAy | pn | σtot | σR |
|---|---|---|---|---|---|---|---|
| 12C | 766/8566 | 289/5620 | 151/1211 | 83/2266 | — | 120/41660 | 16/60 |
| 14C | — | 1/21 | — | 15/210 | 8/85 | — | — |
| 16O | 115/2050 | 223/2515 | 14/161 | 26/713 | — | 51/11277 | 4/103 |
| 18O | 43/484 | 13/230 | — | — | — | 4/528 | — |
| 20Ne | — | 12/316 | — | 1/26 | — | — | 1/5 |
| 24Mg | 5/91 | 120/1937 | 1/10 | 115/1624 | — | 1/1600 | 1/7 |
| 26Mg | 1/23 | 101/613 | — | 1/25 | 1/19 | — | — |
| 28Si | 13/271 | 70/905 | 2/31 | 16/325 | — | 2/10605 | 1/1 |
| 30Si | — | 1/28 | — | 1/28 | 1/13 | — | — |
| 32S | 18/401 | 16/204 | 4/75 | 1/23 | — | 1/1913 | — |
| 34S | 2/76 | 11/108 | — | — | 1/17 | — | — |
| 40Ar | 3/56 | 8/418 | 1/16 | 6/110 | 2/29 | 4/12078 | 1/5 |

(p,n) to the IAS: only 14C, 26Mg, 30Si, 34S and 40Ar. 18O and 22Ne (E1667, E1673) sum unresolved levels around the
IAS, and 38Ar's two sets do not resolve or name the IAS (Kyle, 2026-11-10); in 26Mg (D0049008) the IAS window also
admits the 26Al 5+ ground state and 3+ at 0.417 MeV, which are excluded (`PN_NOT_IAS_RECORDS`). 22Ne and 38Ar
therefore have no data at all.

Further drops (2026-11-10): 36 records as possible duplicates (every flagged pair loses one, `MANUAL_RECORD_DROPS`);
records resting on reader (digitisation) errors only, or with errors below an author error EXFOR carries
(`READER_ONLY_DROPS`, `BELOW_AUTHOR_DROPS`; section 4).

From the independent review (2026-11-11; four reviewers: code, data vs docs, inputs, ELM lessons):
- O0257007 (12C Ay, 38 MeV) held two records: EXFOR data set 1 is the asymmetry (beam polarisation 0.20–0.29 × Ay),
  data set 2 the Ay. The asymmetry is dropped (`VALUE_KEYED_DROPS`).
- 22184003 (Moxon, natC σ_tot) is cut above 5 MeV: EXFOR's STATUS says the data above 5 MeV "are not thought to be
  meaningful", and they run 1.5–3× the other 12C sets (`POINT_ENERGY_MAX`).
- 14269002 (Shane, natC σ_tot) now keeps both of its measurements (pointers 1 and 2: two samples); integral rows were
  built per subentry and silently took only the first.
- Angular records need ≥ 5 *distinct* angles (`MIN_DISTINCT_ANGLES`): C1177003, a 14.02 MeV 12C Ay resonance scan
  grouped into 21 pseudo-distributions of 4–6 angles, is dropped, as are a few others.
- D0498002 (Daehnick, 16O(p,p), 27 records) is restored: the reader detector matched "angular readings" in the
  authors' own error description (allowlisted in tests/test_reader_errors.py).
- ELM exclusions about the entry itself are now inherited even when the reason mentions a duplicate within the same
  entry (O0253) or no uncertainties (E0795, C0078).
- The report lists every drop-table key that matched no record (`tests/test_elm_light_evaluation.py` requires none).

## 3. Compound elastic (scripts/talys_compound.py --corpus elm_light, 2026-11-10)

TALYS 49ef834 (as ELM), default settings + outangle/cpang; natural targets run as their dominant isotope (their
records are filed under it). `elastic_diff_xs_direct` (4670 records; 1831 before natural Si, S and Ne joined on 2026-11-11) and `proton_reaction_direct` (26). Systems with more than 500 energies (n+28Si, 2567) run in chunks (TALYS allows 600 incident energies per run). The table below is from 2026-11-10 (before the natural targets). Median over
sets of each set's median `ce_fraction_model` (CE / TALYS elastic), with the number of sets, by energy (MeV):

| system | 0–2 | 2–5 | 5–10 | 10–15 | 15–20 | 20–30 | 30–50 | 50–200 |
|---|---|---|---|---|---|---|---|---|
| n+12C | 0.60 (177) | 0.75 (321) | 0.71 (186) | 0.23 (52) | 0.11 (10) | 0.02 (5) | 0.00 (1) | 0.00 (14) |
| p+12C | 0.53 (100) | 0.61 (51) | 0.72 (36) | 0.62 (24) | 0.14 (38) | 0.03 (9) | 0.00 (11) | 0.00 (19) |
| p+14C | — | — | — | 0.07 (1) | — | — | — | — |
| n+16O | 0.41 (11) | 0.78 (46) | 0.61 (25) | 0.21 (25) | 0.01 (2) | 0.00 (5) | — | 0.00 (1) |
| p+16O | 0.19 (2) | 0.78 (73) | 0.84 (87) | 0.38 (12) | 0.08 (30) | 0.01 (3) | 0.00 (10) | 0.00 (5) |
| n+18O | — | — | 0.41 (42) | — | — | 0.00 (1) | — | — |
| p+18O | — | — | 0.09 (5) | 0.05 (6) | 0.00 (1) | 0.00 (1) | — | — |
| p+20Ne | — | 0.28 (10) | 0.38 (1) | — | — | — | — | 0.00 (1) |
| n+24Mg | 0.50 (1) | 0.74 (1) | 0.49 (2) | 0.03 (1) | — | — | — | — |
| p+24Mg | — | 0.49 (51) | 0.59 (58) | — | 0.01 (1) | 0.00 (2) | 0.00 (5) | 0.00 (3) |
| n+26Mg | — | — | — | — | — | 0.00 (1) | — | — |
| p+26Mg | — | — | 0.47 (99) | 0.08 (1) | 0.00 (1) | — | — | — |
| n+28Si | — | 0.54 (1) | 0.62 (3) | 0.03 (5) | 0.00 (2) | 0.00 (2) | — | — |
| p+28Si | 0.09 (28) | 0.27 (18) | 0.33 (5) | 0.14 (4) | 0.02 (5) | 0.00 (1) | 0.00 (2) | 0.00 (7) |
| p+30Si | — | — | — | — | — | — | — | 0.00 (1) |
| n+32S | — | — | 0.24 (7) | 0.00 (6) | 0.00 (3) | 0.00 (2) | — | — |
| p+32S | — | 0.22 (1) | 0.74 (13) | — | 0.00 (1) | — | — | 0.00 (1) |
| n+34S | — | — | — | — | — | 0.00 (2) | — | — |
| p+34S | — | — | 0.60 (10) | — | — | 0.00 (1) | — | — |
| n+40Ar | — | — | 0.09 (2) | 0.00 (1) | — | — | — | — |
| p+40Ar | — | — | — | — | — | 0.00 (3) | 0.00 (4) | 0.00 (1) |

1,198 sets have a median CE fraction above 0.5, none above 20 MeV. σ_R: CE adds < 8 % above 15 MeV (12C O0341002 at
10 MeV: 1.7x, i.e. TALYS CE exceeds the measured nonelastic there). Caveats for the calibration's floors: KD03 is
fitted for A = 24–209, so CE below A = 24 is an extrapolation; Hauser–Feshbach averages over resonances that the
light-target data below ~10 MeV resolve, so CE there is an average, not a prediction of a given energy.


**Trial calibration selection (Kyle, 2026-11-10).** ELM-lane's rules (elm_lane/data.py) with CE cut 0.5 plus a
5 MeV (p,p) floor: (n,n), (p,n) and (p,p) 5–100 MeV, σ_tot and σ_R 0–100 MeV; an elastic set is dropped if its median
`ce_fraction_model` is ≥ 0.5 and its points ≥ 0.5 are masked; ≥ 5 angles. Applied at calibration time; the corpus is
not cut. After all drops (2026-11-11), sets kept (5 MeV (p,p) floor only → with the CE cut): (n,n) 402 → 187,
(p,p) 512 → 195, (p,n) 13, σ_tot 178, σ_R 20; total 1125 → 593 (86,900 points). By target: 12C 289, 16O 141, 18O 51,
28Si 33, 32S 24, 40Ar 18, 24Mg 16, 14C 9, 26Mg 4, 34S 4, 20Ne 3, 30Si 1. Proton Ay (no CE correction, not an elm_lane
type): 178 sets at 5–100 MeV. σ_tot in the calibration is further thinned to a shortlist above 10 MeV (Kyle,
2026-11-11; the plan, Phase C2).

## 4. Reader-only uncertainties (Kyle, 2026-11-10; papers read 2026-11-11)

**2026-11-11 update.** Kyle supplied twelve of the papers below (git-ignored archive, filed by entry). From them:
- **Restored with the papers' errors** (`author_errors.PER_PAPER`): O1242 (Guratzsch, 1.5 % relative, 7 % absolute,
  Ay 0.03; EXFOR files both as constant ERR-n columns), O1367 (Wienhard, the 5 % / 0.05 put into their phase-shift
  fit, as Put O0124; Ay scale 2.9 %), F0996 (Hulubei, < 5 %, up to 15 % below 45 deg, 10 % absolute).
- **Restored from the right EXFOR column:** E0243005 (ERR-T, Kato's total ΔP; `COLUMNS`), 20220002 (ERR-T; its
  constant 10 % ERR-S is the n-γ coincidence statistics, `COMMON`), O0484003-005 (Prior's statistical ERR-S, DATA-ERR
  being the reader error; `COLUMN_AUTHOR`; Ay scale 9 %), O2048002 (its DATA-ERR, the authors' bars read off their
  figure; an audit false positive across the excitation function's energy rows, allowlisted).
- **Kept dropped** (Kyle: no author error means no record): O0486 (Karban), F0471 (Girod) and O0551002 (Rush, 40Ar)
  state no error. O0480011/012 (Clarke's fit-figure readings of Fannon's and their own data), O0551005 (Rush's
  reanalysis of Fannon's 12C) and F0471003 at 24.1 / 26.1 MeV (Dickens's data replotted) are duplicates.
- **D0049 (Carlson (p,n)) normalisation:** the error bars are relative only; absolute ±11 % (±25 % for 208Pb), p.36.
  `author_errors.NORM` now carries it, in `elm_light` (26Mg, 40Ar) and `data/elm` (90,96Zr, 118,120Sn, 208Pb; ELM's
  charge-exchange notebook rerun, only those five records changed), replacing the 5 % default.

The 2026-11-10 text follows.


`elm_light` is in `author_errors.SCOPE`, so the reader-error tests audit it as they do ELM: every record must rest on
author uncertainties, from EXFOR or supplied per paper (docs/AUTHOR_UNCERTAINTIES.md). The light-target subentries were
never through that per-paper cleaning, and the papers were not available, so the failing records are dropped for now:
244 with reader-only points (`READER_ONLY_DROPS`) and 10 with errors below an author error EXFOR carries
(`BELOW_AUTHOR_DROPS`: the parse took ERR-S where EXFOR also gives ERR-T, or, for O2048002 and possibly 20220002, the
audit compares across final states, as it did for D0049008; recoverable from EXFOR alone). D0049008 (26Mg IAS) was an
audit false positive (it matches by angle across the six 26Al levels of the subentry) and is kept, allowlisted in the
test. To restore a record: supply its author uncertainty in `author_errors.py` and delete its key.

The papers, for when they can be read (the table counts records the trial selection would use):

Under the trial selection, about 76 of them would be used (~61 cross sections + 15 proton Ay), from 26 entries. These are
the papers to read, largest first. PDFs go in the git-ignored archive `papers/` of the shared checkout
(/mnt/ufs18/rs/reactiontheoryinitiative/nucleon_nucleus_data/papers/<entry>.pdf; 13 downloaded or already there on
2026-11-10, each checked against its first page). Elsevier and Springer block scripted downloads from the cluster
(403 / landing page), so those need a browser.

| entry | first author | reference (EXFOR) | DOI | used records (xs + Ay) | targets / observable | E (MeV) | PDF |
|---|---|---|---|---|---|---|---|
| F0996 | H.Hulubei et al. | NP,39,686,1962 | 10.1016/0029-5582(62)90425-x | 10 | 20Ne pp | 5.2–6.23 | ✗ Elsevier: browser |
| F0471 | M.Girod et al. | JPR,31,125,1970 | 10.1051/jphys:01970003102-3012500 | 8 | 12C pp | 19.9–28.85 | ✗ J. Physique (open archive) |
| O0486 | O.Karban et al. | NP/A,132,548,1969 | 10.1016/0375-9474(69)90717-9 | 8 | 16O pp | 19.8–30.5 | ✗ Elsevier: browser |
| O0492 | R.A.Blue et al. | PR,137,B284,1965 | 10.1103/physrev.137.b284 | 0 + 6 | 16O pAy | 5.66–10.74 | ✓ archive |
| F0866 | V.B.Gubin et al. | IZV,38,868,1974 | — | 5 | 26Mg pp | 6.15–6.35 | ✗ no DOI (Soviet journal) |
| O1367 | K.Wienhard et al. | ZP,256,457,1972 | 10.1007/bf01386991 | 0 + 4 | 12C pAy | 10.15–10.69 | ✗ Springer: browser |
| C0246 | D.R.Maxson | PR,123,1304,1961 | 10.1103/PhysRev.123.1304 | 4 | 16O pp | 14.1–17.6 | ✓ archive |
| O0484 | R.M.PRIOR et al. | NP/A,167,143,1971 | 10.1016/0375-9474(71)90588-4 | 0 + 3 | 16O pAy | 9.57–12.42 | ✗ Elsevier: browser |
| O0551 | A.A.RUSH et al. | NP/A,166,378,1971 | 10.1016/0375-9474(71)90438-6 | 3 | 12C, 40Ar pp | 30–50 | ✗ Elsevier: browser |
| F0256 | M.Pignanelli et al. | PR/C,33,40,1986 | 10.1103/physrevc.33.40 | 3 | 12C, 24Mg, 28Si pp | 35 | ✓ archive |
| F1135 | A.E.Antropov et al. | IZV,34,106,1970 | — | 3 | 26Mg pp | 5.84–6.03 | ✗ no DOI (Soviet journal) |
| O0384 | W.S.GRAY et al. | NP,67,542,65 | 10.1016/0029-5582(65)90546-8 | 2 | 40Ar pp | 14.1–16.9 | ✓ archive |
| O0434 | N.BARON et al. | PR,180,978,1969 | 10.1103/physrev.180.978 | 2 | 16O, 40Ar pp | 20.93–21.13 | ✓ archive |
| O1133 | L.Alvarez et al. | JP/G,8,987,1982 | 10.1088/0305-4616/8/7/015 | 2 | 12C, 16O pp | 40.9 | ✓ archive |
| O0480 | N.M.Clarke et al. | NP/A,157,145,1970 | 10.1016/0375-9474(70)90105-3 | 2 | 12C, 16O pp | 49.4 | ✗ Elsevier: browser |
| O1242 | H.Guratzsch et al. | NP/A,129,405,1969 | 10.1016/0375-9474(69)90676-9 | 0 + 1 | 12C pAy | 6.9 | ✗ Elsevier: browser |
| E0243 | S.Kato et al. | NIM,169,(3 | 10.1016/0029-554x(80)90963-5 | 0 + 1 | 12C pAy | 65 | ✗ Elsevier: browser |
| 20220 | D.Spaargaren et al. | NP/A,161,354,1971 | 10.1016/0375-9474(71)90374-5 | 1 | 12C nn | 15 | ✗ Elsevier: browser |
| O0254 | D.J.BAUGH et al. | NP,65,33,65 | 10.1016/0029-5582(65)90292-0 | 1 | 12C pp | 17.8 | ✓ archive |
| O0211 | C.B.FULMER et al. | PR,181,1565,69 | 10.1103/physrev.181.1565 | 1 | 12C pp | 61.4 | ✓ archive |
| 22847 | J.Klug et al. | PR/C,68,064605,2003 | 10.1103/PhysRevC.68.064605 | 1 | 12C nn | 96 | ✓ archive |
| O0274 | K.STRAUCH et al. | PR,103,200,56 | 10.1103/physrev.103.200 | 1 | 12C pp | 96 | ✓ archive |
| O1090 | M.Herman et al. | JP/G,2,831,1976 | 10.1088/0305-4616/2/11/008 | 1 | 26Mg pp | 9.1 | ✓ archive |
| O2048 | H.Orihara et al. | NP/A,203,78,1973 | 10.1016/0375-9474(73)90424-7 | 1 | 18O pp | 6.041 | ✗ Elsevier: browser |
| D0922 | H.Hulubei et al. | JET,15,993,1962 | — | 1 | 32S pp | 5.85 | ✗ JETP 1962 |
| O1542 | F.PELLEGRINI et al. | PR/C,18,613,1978 | 10.1103/PhysRevC.18.613 | 1 | 30Si pp | 40.75 | ✓ archive |

The other 13 entries have no record in the trial selection (entry (records)): 21729 (70), D0890 (4), F0059 (4), F0877 (11), F0904 (5), F1013 (4), F1019 (1), F1090 (6), O0062 (1), O0079 (1), O0889 (8), O1030 (6), O1177 (2). 21729 (Hall et al.,
NP A 299, 99 (1978), 70 records) is 32S (62) and 28Si (8) (n,n) at 0.64–3.5 MeV, below the cut.
Not in the table: D0498 (Daehnick, restored, its errors are the authors') and D0049 (Carlson, kept; see above).

## 5. (n,n) energy resolution against low-lying inelastic (papers read 2026-11-11)

Kyle supplied the papers of the (n,n) sets a calibration might train on; each was read for the separation of the
elastic peak from the first excited state. Clean (resolved, or peak-fitted with the state well inside the
resolution): Virdis 24Mg 9.8 / 14.8 MeV (226 / 441 keV; natural Mg, dropped under item 5 anyway), Tailor 26Mg 24 MeV
(700 keV), Alarcon 34S 21.7 / 25.5 MeV (450 keV), Beach 16O and 40Ar 14 MeV (the Ar flight path chosen to resolve the
1.46 MeV state), Nakada 12C 14 MeV, Winfield 12C 40 MeV, Islam 16O 18-26 MeV; and, for the natural-Si / 12C sets the >= 90 % rule brought in: DeVito 28Si 30-40 MeV (0.63-0.86
MeV), Rapaport 28Si 11-26 MeV (750 keV at 20 MeV), Seeliger 28Si 6.8-14.8 MeV (peak-fitted; resolves doublets 0.36 MeV
apart), Meigooni 12C 20.8-26 MeV (13 m flight path). Dropped (Kyle, `MANUAL_DROPS`):
- Hjort 12C and natural Si 65 MeV (13510002/003): 2.7 MeV resolution; the low-lying states (12C 4.44, 28Si 1.78 MeV)
  subtracted with (p,p') strengths and DWUCK4.
- Baba / Ibaraki 12C and natural Si 55-75 MeV (22480002/003/007): resolution not enough to separate elastic from
  inelastic; corrected with factors from the LA150 evaluation (as Hjort).
- Osborne 12C 65-185 MeV (13946002): 2.5-4.5 MeV resolution; the 4.44 MeV state's share estimated with DWUCK4 (< 1 %);
  dropped so that no training set rests on model-corrected inelastic.
- Deconninck 12C 14.7-19.9 MeV (20240003/004): about 3-4 MeV resolution; a two-Gaussian fit separates the 4.44 MeV
  state.
- 22121004 / 022 (40Ar n σ and Ay 7.8 MeV): a private communication (the cited PRC 39, 1774 has no argon); 800 keV,
  separation from the 1.46 MeV state not stated.
- Boerker 28Si 10.2 MeV (22113015) and Yamanouti 28Si 21 MeV (21629002): papers not available to check (Boerker's
  16O sets, first state at 6 MeV, are kept).

Resolved: O0328014 (28Si (p,p), Fricke) failed `test_fricke_is_reader_plus_authors_column` by ~1e-5 because the test
compared the `_direct` copy (measured − CE, with the CE uncertainty added) against EXFOR; it now uses `y_measured` and
`y_err_before_compound` for those copies.

## 6. Review before sampling (ELM-Lane-light stage 0, 2026-11-11; Kyle: agreed)
An adversarial review of the calibration's training sets at the ELM-Lane prior centre found two corpus errors:
- **O2096002 dropped** (`elm_light.MANUAL_DROPS`): Greenlees & Souch, PPS A 69, 686 (1956), Mg(p,p) 9.63 MeV, coded as
  24Mg but measured on "a piece of pure Mg foil", i.e. natural Mg (79 % 24Mg; natMg is excluded, decision 5). The
  sample text names no natural abundance, so `natural_sample` missed it. The CAJAD figure digitisation is also ~300x
  below Rutherford at 7 deg.
- **C0826002 errors read as per cent** (`author_errors.PERCENT_ERR`): Alarcon et al., PRC 31, 697 (1985), 34S(p,p)
  29.8 MeV. EXFOR labels DATA-ERR MB/SR, but its values (14.5, 11.1, ..., 9.1 against 1867 ... 0.33 mb/sr) are per cent:
  read as mb/sr the median error was 93 % and 2700 % at 121 deg. The data are normalised to an optical-model value
  at 15 deg (MONITOR ... CALC), so the normalisation uncertainty is 10 % (`NORM`). The reader-error audit reads the
  column the same way.
Calibration-level choices from the same review (14C(p,n) below 14 MeV, F1068007, elastic anchors, Pruitt
normalisation groups) live in the calibration (`calibrations/elm_lane_light/README.md`); the corpus keeps those data.
