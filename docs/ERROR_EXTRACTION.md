# Author uncertainties extracted from the papers: summary for review

Consolidated from the five extraction reports in `docs/extraction/extract_G{1..5}.md` (each with PDF page, table/figure
and verbatim quotes), 2026-10-08. PDFs are in `papers/` (git-ignored). Nothing here is applied yet: each row needs
Kyle's OK, then it goes into `nn_corpora/author_errors.py` (DATA_CLEANING.md step 3).

**Confidence levels:**
- **high:** tabulated or explicitly stated;
- **medium:** stated as a fit weight or bound, or read off a figure;
- **low:** inferred, e.g. from the same group's other paper, or a figure where bars are invisible.

Ay uncertainties are absolute.

## Findings that change data, not just errors

1. **208Pb(p,n) 45 MeV, O0178015.** Doering's thesis Table 5 (PDF p.129) ends at 160.1°. The two EXFOR points at
   161.9° and 164.0° (0.049 and 0.072 mb/sr, the 9–11σ outliers) are **not in the authors' tabulation**. They are
   probably digitisation artefacts of Fig. 3. The last tabulated rows are 155.2° (0.0038 mb/sr, 118 %) and 160.1°
   (0.0165 mb/sr, 65 %). **Proposal: drop the two points** (or give them ≥ 65–118 %; the fill rule already gives
   220 %).
2. **ELM double-counts Fulmer et al. 61.4 MeV elastic** for 40Ca, 90Zr, 116Sn and 208Pb. It contains both EXFOR's
   figure digitisations (O0211004/007/008/009, STATUS CURVE, reader errors only) and the authors' tables
   (O0211012/015/016/017, STATUS TABLE, author errors 5–30 %). **Proposal: drop the CURVE subentries from ELM**, as
   KDUQ does.
3. **O0157 (Devins et al. 1962):** the compilation's file is the wrong paper (Moonen 1993). Not yet extracted; EXFOR's
   own text gives about 3.5 % (forward) to 10 % (backward).
4. **Doering Table 5** (thesis pp.124–129) has per-point author errors for all 12 sets. The 25 MeV sets on 48Ca,
   90Zr and 120Sn (no author errors in EXFOR) can take them: 48Ca 1.9–10.1 %, 90Zr 3.2–7.5 %, 120Sn 1.9–12.2 %
   (32 rows each; EXFOR has 36 points for 48Ca). The values stay EXFOR's; the errors are matched by angle and
   interpolated. The reviewer also suggests using Table 5 for every Doering point instead of the fill rule (Q1
   below).

## Per entry

| entry | records (corpus) | per-point author error | normalisation (author) | conf. | proposal |
|---|---|---|---|---|---|
| O0178 Doering (p,n) | sm3, elm | Table 5: statistical ⊕ peak-fit systematic, 1.5 % to > 100 % | 10 % (ERR-1; < 5 % components) | high | Table 5 errors for 25 MeV ×3; fill rule elsewhere (or Table 5 everywhere, Q1); drop 208Pb 162°/164° |
| O0328 Fricke 40 MeV | sm3, elm, kduq, chuq | ERR-1 = "relative probable errors incl. statistics and background subtraction" (confirmed); no numbers in the paper; figure about 3 % (6 % > 120°); Ay about 0.03 (0.1 at large angles) | 5 % (target); EXFOR's 2 % current integration not in the text; Ay 1.8 % (beam polarisation) | low–med | ERR-1 where present (override) plus fill rule; figure values where blank |
| O0211 Fulmer 61.4 MeV | elm, kduq | tables: 5 % forward, 10 % at minima, 11–30 % at large angles | 5 % ⊕ 10 % | high | drop the CURVE duplicates; tables stand |
| O0382 Yagi | elm | not stated, no bars | 15 % | low | 5 % per point, 15 % norm |
| O0552 Rathmell | elm | 0.5–3 % total | about 1 % | high | 1.5 %; Ay 0.002–0.01 |
| O0580 Fretwurst 94Mo | elm | statistical bars inside the symbols; fluctuations may exceed them | about 1 % (scale fixed to the OM fit) | low–med | 5 % |
| O0124 Put | elm, kduq | fitted with 5 %, "actual always smaller" | from refs [3],[4], not stated | med | 5 % (check that the corpus points are the present-work triangles) |
| O0157 Devins | elm, kduq | (wrong PDF) EXFOR: 3.5 % → 10 % | — | low | 3.5 → 10 % ramp until the paper is in hand |
| O0225 Wagner 208Pb 35 MeV | elm | not stated, no visible bars | 5 % counter / 10 % plates; scale set to the BG optical model | low | 2 % floor; norm 5 % |
| O0239 Lombardi Ca 14–16 MeV | elm | 1 % statistical, 2 % assigned; Ay "typical 2 %" | 10 % | high (σ) / med (Ay) | 2 %; Ay 0.02; note the 3.6 % 40Ca impurity in 48Ca |
| O0246 Kruse 148Sm | elm | 10 % assigned for fitting | Rutherford at 5 MeV | med | 10 % |
| O0253 Dicello Ca 14–22 MeV | elm | about 2 % relative ("about the symbol size") | 5 % (3 % ⊕ 2 %) | high | 2 % |
| O0254 Baugh Si/Ca | elm, kduq | relative σ only; "same statistical accuracy as the polarisation" (Ay 1–4 %) | none (free normalisation) | low | 3–5 % (use 4 %); normalisation should be free or large |
| O0259 McDaniels 208Pb 200 MeV | elm | not stated (solid circles from TRIUMF, ref. 25) | 7 % | low | 3 %; norm 7 % |
| O0272 Lee 208Pb 200 MeV | elm | not stated; refs 5, 6 | — | low | 7 % placeholder (or get refs 5, 6) |
| O0370 Gray 90Zr 18.8 MeV | elm, kduq | not stated | about 5 % | low / med | 2 %; norm 5 % |
| O0384 Gray 40Ca 14.6/17.3 MeV | elm | not stated | **15 %** | low / high | 5 %; norm 15 %; possible compound elastic at 14.6 MeV |
| O0387 Tellez 48Ca 12 MeV | elm | not stated; scale matched to the Argonne curve | not quoted | low | 4 %; norm 10 % |
| O0458 Beuzit 64Ni 12 MeV | elm | not stated; tiny bars | normalised to Lee & Schiffer | low | 3 % |
| O0471 Burger 92/94Mo 12.5 MeV | elm | ≤ 6 % | fitted (≤ 20 %) | med | 6 % |
| O0545 Stautberg 92/94Zr 19.4 MeV | elm | < 1 % (< 90°), < 3 % (> 90°) statistical | 5 % | high | 1 % / 3 % |
| O0549 Sinha Mo 20–49 MeV | elm | about 4 % (statistical + 1 % thickness) | — | high | 4 %; Ay 0.03 → 0.1 |
| O1199 Fabrici 40Ca Ay | elm | σ 4 % absolute; nothing for Ay | — | low | Ay 0.02–0.03 (paper II, PRC 21 844, may say) |
| O0169 Wassenaar (many) | elm, kduq, chuq | stated minimum: σ 2 %, Ay 0.01 absolute; bars = statistics | free fit (< 5 % target to target) | high (floors) | 2 %; Ay max(0.01, figure bar), 0.02 if one number |
| O0079 Tesmer 54Fe | kduq | not stated, no bars | — | low | 5 % |
| O0091 Van Hall Fe/Ni | kduq, chuq | 3 % (Fe) / 2 % (Ni) assigned; relative only | relative | high | 3 % / 2 %; Ay 0.02 floor |
| O0300 Kwiatkowski | kduq | statistical ≤ 1 % (< 50°), ≤ 3 % (< 80°); total about 4 % | < 8 % | high | 4 %; norm 8 % |
| O0456 Brussel | kduq | statistical about 3 %; probable error 6–10 % | — | high | 3 % (or 4.2 % with the nonelastic term) |
| O0553 Rolland | kduq | statistical bars invisible; 12C table 3–6 % | 5 % (150 MeV) / 10 % (75 MeV) | med–low | 4 % / 5 % |
| O1103, O1109 Moonen | chuq | not stated (same group as O1104) | fitted | low | 2 % (σ); Ay 0.02 |
| O1104 Petit | chuq | stated minimum 2 % for σ and Ay | — | high / med | 2 %; Ay max(2 % \|Ay\|, 0.01) |
| F0733 Van der Bijl | sm3 | 3 % (ERR-ANALYS) | — | high | already applied |
| F1173, O0083, O0372, O0446 | — | PDF not available | — | — | — |

## Normalisation corrections (author-stated vs corpus default 5 %)

| entry | author | corpus |
|---|---|---|
| O0384 | 15 % | 5 % |
| O0382 | 15 % | 5 % |
| O0239 | 10 % | 5 % |
| O0300 | 8 % | 5 % |
| O0259 | 7 % | 5 % |
| O0211 | 5 % ⊕ 10 % | — |
| O0254 | none (relative data): free | 5 % |
| O0091 | relative data | — |

## Questions for Kyle

- **Q1. Doering:** use the thesis Table 5 errors at every point (matched by angle) instead of the fill rule? The
  values stay EXFOR's. This is the author source, and it supersedes the 7 % forward bound, which Table 5 shows is
  sometimes 2 % and sometimes > 7 %.
- **Q2.** Drop the two 208Pb 45 MeV points absent from Table 5 (161.9°, 164.0°)?
- **Q3.** Drop ELM's CURVE duplicates of Fulmer (O0211004/007/008/009)?
- **Q4.** Defaults for "not stated" (low-confidence rows): take the proposals above, or one uniform default (e.g.
  5 % σ, 0.03 Ay) for all of them?
- **Q5.** Apply the author normalisation errors where they differ from the corpus default?
- **Q6.** Find Devins (O0157, correct PDF), and optionally Lee refs 5/6 (O0272) and Fabrici II (O1199).
