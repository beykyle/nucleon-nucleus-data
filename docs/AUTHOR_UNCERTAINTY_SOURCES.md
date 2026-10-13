# Author uncertainties: what the publications say

The evidence behind every rule in [AUTHOR_UNCERTAINTIES.md](AUTHOR_UNCERTAINTIES.md). Each entry covers one
publication behind corpus records whose EXFOR uncertainties are, at some or all points, only the compilers'
data-point reader (digitisation) uncertainty. For each, it gives what the authors state about per-point and
normalisation uncertainties, with page, table and figure references and verbatim quotes. It ends with the rule the
corpora apply. Citations, DOIs and EXFOR links are in [../papers/INDEX.md](../papers/INDEX.md); the publications
themselves are not distributed with this repository.

The rules apply to the evaluated corpora: `elm`, `sm3`, `kduq_evaluated`, `chuq_evaluated` and `test_evaluated`.
The static `kduq`, `chuq` and `test` keep the published curation. "Removed" and "Applied" below refer to the
evaluated corpora only.

**Conventions.**
- "PDF p." is the page index in the PDF file; the journal page follows in brackets where it differs.
- Quotes are verbatim from the text layer, with OCR noise corrected only where unambiguous; "[...]" marks a garbled
  or cut passage.
- Values read off a figure are labelled *estimate*.
- **Confidence:**
  - *high*: tabulated, or stated as a measured error;
  - *medium*: stated as a fit weight, a bound or a minimum, ambiguous in units, or read off a figure;
  - *low*: inferred (e.g. from the same group's other paper), or not stated.
- σ is the relative per-point error for cross sections; Ay errors are absolute.

Entries, in EXFOR order:
[F1173](#f1173) · [O0079](#o0079) · [O0083](#o0083) · [O0091](#o0091) · [O0124](#o0124) · [O0157](#o0157) ·
[O0169](#o0169) · [O0178](#o0178) · [O0211](#o0211) · [O0225](#o0225) · [O0239](#o0239) · [O0246](#o0246) ·
[O0253](#o0253) · [O0254](#o0254) · [O0259](#o0259) · [O0272](#o0272) · [O0300](#o0300) · [O0328](#o0328) ·
[O0370](#o0370) · [O0372](#o0372) · [O0382](#o0382) · [O0384](#o0384) · [O0387](#o0387) · [O0446](#o0446) ·
[O0456](#o0456) · [O0458](#o0458) · [O0471](#o0471) · [O0545](#o0545) · [O0549](#o0549) · [O0552](#o0552) ·
[O0553](#o0553) · [O0580](#o0580) · [O1103](#o1103) · [O1104](#o1104) · [O1109](#o1109) · [O1199](#o1199)

---

## F1173

**A. B. Kurepin, R. M. Lombard, Izv. Akad. Nauk SSSR Ser. Fiz. 36, 2232 (1972)**; 148Sm(p,p) 24.5 MeV (F1173002).

The publication was not available. EXFOR gives author errors at 3 of the 24 points; the rest carry only the reader
uncertainty.

**Applied:** removed.

---

## O0079

**J. R. Tesmer, F. H. Schmidt, Phys. Rev. C 5, 864 (1972)**; 54Fe(p,p) 19.6 MeV (O0079006, Fig. 8 left).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0079006 | dσ/dΩ | not stated for elastic scattering; Fig. 8 (left) is log-scale with symbols only, no error bars | not stated | PDF p.9 [872], Fig. 8 | low |

- The paper is a p–γ angular-correlation study. Fig. 8 caption: "Cross-section data for 54Fe. The curves are DWBA
  predictions with the full Thomas form of ΔU_so" (PDF p.9).
- The only uncertainty statement concerns the γ efficiency, not elastic scattering (PDF pp.3–4): "The uncertainty
  in F derives primarily from the calibration measurement and is ±2%."
- Nothing is said about how the elastic cross section was normalised or its error.

**Applied:** removed.

---

## O0083

**E. Colombo, R. De Leo et al., J. Phys. Soc. Jpn. Suppl. 44, 543 (1978)**; 27Al and 56Fe(p,p) 35.2 MeV (O0083019,
O0083016).

Conference proceedings; the publication was not available.

**Applied:** removed.

---

## O0091

**P. J. Van Hall, J. P. M. G. Melssen et al., Nucl. Phys. A291, 63 (1977)**; Fe and Ni isotopes, 17.2, 20.4, 24.6 MeV.

Subentries: cross sections 002 (54Fe, Fig. 2), 008 (56Fe, Fig. 3), 014 (58Ni, Fig. 4), 018 (60Ni, Fig. 5),
022 (62Ni, Fig. 6); Ay 003, 009, 015, 019, 023. EXFOR merged and relabelled the entry in 2022 (HISTORY: "ERR-T →
DATA-ERR; DATA-ERR → ERR-DIG"). Its COMMON block carries `ERR-1` = 3 % (Fe) / 2 % (Ni) "Relative error", and
`ERR-DIG` 0.9 % (cross sections) and 0.010 (Ay).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| 002, 008 (54Fe, 56Fe) | σ/σ_R | "Relative errors of 3%" assigned to the Fe cross sections (an assignment for the optical-model fit); no bars visible in Figs. 2–3 | relative angular distributions only; normalisation a free fit parameter; no absolute error stated | PDF p.4 (Sec. 3.1); Figs. 2–3 | high |
| 014, 018, 022 (58Ni, 60Ni, 62Ni) | σ/σ_R | "2 % was used for the Ni isotopes" | as above | PDF p.4; Figs. 4–6 | high |
| 003, 009, 015, 019, 023 | Ay | not stated; Figs. 2–6: most bars smaller than the symbols (≤ 0.02, *estimate*), a few 0.05–0.1 at forward angles and near minima | beam polarisation monitored by carbon scattering at 52°, calibrated with Faivre's data; no uncertainty quoted | PDF p.3 (Sec. 2); Figs. 2–6 | low (*estimate*) |

Quotes:
- PDF p.4: "As we had measured relative angular distributions only the normalization was also used as a parameter.
  Relative errors of 3 % were assigned to the cross sections of the Fe isotopes while 2 % was used for the Ni
  isotopes."
- PDF p.3: "The polarization was continuously monitored downstream from the target … by scattering from a thick
  carbon target through 52 deg … For calibration we used the data of Faivre."
- PDF p.3: "At 20.4 and 24.6 MeV the cross sections were measured separately with an unpolarized beam. From these
  measurements we deduced the calibration of the solid angles for the various detectors."

Note: the 3 % / 2 % are fit weights, so no absolute normalisation uncertainty follows from this paper.

**Applied:** σ 3 % (Fe), 2 % (Ni); Ay 0.02; both ⊕ the reader error. Normalisation: corpus default.

---

## O0124

**L. W. Put, P. P. Urone, A. M. J. Paans, Phys. Lett. B 35, 311 (1971)**; 30.4 MeV p on 28Si (O0124002) and 120Sn
(O0124004), backward angles.

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0124002 (28Si), O0124004 (120Sn) | dσ/dΩ | not stated as a measured error; "the experimental error was always smaller" than the 5 % used as fit weight | relative data scaled to the absolute cross sections of refs. [3], [4] in the overlap at the first maximum; uncertainty of that scaling not stated | PDF p.1; Figs. 1–2 (PDF p.2) | medium |

Quotes (PDF p.1; the text layer is letter-spaced, wording reconstructed):
- "In the optical model fit each data point was assigned an error of 5%, though the experimental error was always
  smaller."
- "The relative differential cross sections have been normalized to the absolute cross sections of ref. [3] and [4]
  in the angular range of the first maximum at which we took overlapping data."
- Beam energy 30.4 ± 0.4 MeV; detector angular acceptance 1.0°.

Notes:
- Figs. 1–2 show symbols only. The dots are earlier data from refs. [3] (Cole et al., NP 75, 241, 1966) and [4]
  (Ridley & Turner, NP 58, 497, 1964); the triangles are the present work.
- EXFOR has two reader columns, `DATA-ERR1` and `DATA-ERR2`, one for each figure the points were read from.

**Applied:** σ 5 % ⊕ the reader error (the larger reader column). Normalisation: corpus default.

---

## O0157

**D. W. Devins, H. H. Forster, G. G. Gigas, Nucl. Phys. 35, 617 (1962)**; 30.8 MeV p on 60Ni (O0157002) and 208Pb
(O0157004).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0157002 (60Ni), O0157004 (208Pb) | dσ/dΩ | "absolute errors" about 3.5 % at forward angles rising to about 10 % at extreme backward angles; intermediate values not given | not separately stated; the quoted errors are called absolute | paper p.619; EXFOR ERR-ANALYS (001) | medium |

EXFOR's ERR-ANALYS transcribes the paper's statement (p.619): "THE ABSOLUTE ERRORS OF THE EXPERIMENT WERE ESTIMATED
TO VARY FOR ELASTIC SCATTERING BETWEEN APPROX. 3.5% AT FORWARD ANGLES TO APPROX. 10% AT EXTREME BACKWARD ANGLES."

The paper does not give the angular dependence between the two ends.

**Applied:** σ rising linearly in angle from 3.5 % (most forward point) to 10 % (most backward point) ⊕ the reader
error. Normalisation: corpus default 5 %, kept although the quoted errors are called absolute (a conservative,
slight double count).

---

## O0169

**S. D. Wassenaar et al., J. Phys. G 15, 181 (1989)**; Ni, Sr, Cd, Sn, 20.4 and 24.6 MeV. Subentries are mapped
from the EXFOR common block and the figures (Fig. 2 Ni, 3 Sr, 4 Cd, 6 Sn at 20.4 MeV, 7 Sn at 24.6 MeV).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| 004 (64Ni), 006, 008 (86Sr, 88Sr), 010, 012, 014 (110–114Cd), 016–024 (116–124Sn) at 20.4 MeV; 026 (Sn, 24.6 MeV) | σ/σ_R | "minimal relative errors … 2%"; statistical errors smaller; bars hidden by the dots | no absolute measurement: normalised to the optical model (free); target-to-target normalisations agree within 5 % | PDF p.5 (Sec. 3.1); PDF pp.6–7 (Sec. 3.3); Figs. 2–7 | high (stated minimum) |
| 005, 007, 009, 011, 017–025 (20.4 MeV), 027 (24.6 MeV) | Ay | "minimal absolute errors of the analysing powers … 1%" (0.01); statistical bars drawn where larger than the dots, typically 0.01–0.05 (*estimate*) | Ay normalisation stayed near 1.0; polarisation scale uncertainty not stated | PDF p.5; Figs. 2–7; PDF p.7 | high for the 0.01 floor; medium for larger values |

Quotes:
- PDF p.5, Sec. 3.1: "As a consequence of the uncertainties in the normalisations of the separate runs and of the
  various detectors we estimate the minimal relative errors of the elastic cross sections to be 2% and the minimal
  absolute errors of the analysing powers to be 1%. In general the statistical errors were less for the elastic
  scattering. These errors give about equal chi-squared values for the cross section and analysing power in the
  minimalisation procedure."
- Fig. 2 caption (PDF p.10): "The error bars, if not smaller than the dots, indicate the statistical errors."
- PDF pp.6–7, Sec. 3.3: "Since we performed no absolute measurement of the cross section, we normalised the
  experimental elastic cross section to the optical-model value … the ultimate normalisation for the diverse
  targets did not differ much (less than 5%) when we accounted for the specific thicknesses."

Notes:
- "Minimal" means a floor set by normalisation and detector uncertainties. The statistical errors add to it and
  are larger for Ay than for cross sections, so a single Ay value of 0.02 is used rather than the 0.01 floor.
- EXFOR's O0169007 (86Sr Ay 24.6 MeV) carries an `ERR-T` (authors') value at one point (164.8°); that point keeps
  it.

**Applied:** σ 2 %; Ay 0.02; both ⊕ the reader error, at points without an EXFOR author error. Normalisation:
corpus default.

---

## O0178

**R. R. Doering, D. M. Patterson, A. Galonsky, Phys. Rev. C 12, 378 (1975)**, and **R. R. Doering, PhD thesis,
Michigan State University (1974)**, [doi:10.25335/8r9s-9621](https://doi.org/10.25335/8r9s-9621) (open access).
48Ca, 90Zr, 120Sn, 208Pb(p,n) to the isobaric analogue state at 25, 35, 45 MeV: subentries 006–017.

EXFOR digitised the paper's Fig. 3 (STATUS CURVE). Its `DATA-ERR` (7 %) is "Data-Point Reader Uncertainty" and its
`ERR-T` the authors' bars, which are blank at many points; the three 25 MeV sets on 48Ca, 90Zr and 120Sn (008, 011,
014) have none.

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| all 12 | (p,n) IAS dσ/dΩ | thesis Table 5: per-point errors, statistical ⊕ peak-fitting systematic, 1.5 % to > 100 %. Paper Fig. 3 bars: peak-fit statistics ⊕ ±2 % (beam charge × target thickness) | 10 % (neutron detection efficiency); further < 5 % (target thickness, beam integration, neutron attenuation) | paper PDF p.5 [382], p.6 [383]; thesis Table 5, PDF pp.124–129 (thesis pp.95–98) | high (tabulated) |

Paper (verbatim):
- PDF p.6 [383]: "The error bars displayed on the data in Fig. 3 represent relative errors within each angular
  distribution which result from statistical uncertainties in the peak fitting combined independently with ±2%
  fluctuations in the product of beam charge and target thickness."
- PDF p.6: "The errors in the absolute magnitudes of the cross sections due to uncertainties in the neutron
  detection efficiency calculations are estimated to be about 10%. There are also small uncertainties in target
  thickness, beam current integration, and neutron attenuation along the flight path, which introduce systematic
  errors estimated to be less than 5%."
- PDF p.5 [382]: "errors in the efficiency calculations do not diminish the relative accuracy within each angular
  distribution."
- PDF p.6: "Tabulations of the differential cross sections and their relative errors are available upon request."
- EXFOR's COMMON lists 10 %, 5 %, 5 %, 5 %; the paper says the three small terms *together* are less than 5 %.

Thesis (PDF p.123 = thesis p.94; PDF p.130 = thesis p.99):
- "The dominant source of relative errors in the angular distributions is the neutron yield. The errors given in
  Table 5 result from combining in quadrature statistical and systematic uncertainties in the peak fitting." The
  systematic part is the IAS-width uncertainty.
- "The principal error in the absolute magnitude of the cross sections is the estimated ±10% reliability of the
  neutron detection efficiency calculations … small uncertainties in target thickness, beam current integration,
  and neutron attenuation along the flight path, which may introduce additional systematic errors estimated to be
  less than 5%."
- Table 6, integrated cross sections (mb) at 25 / 35 / 45 MeV: 48Ca 10.6±1.2 / 10.2±1.1 / 8.4±1.0; 90Zr 6.7±0.8 /
  4.8±0.5 / 4.4±0.5; 120Sn 8.5±1.0 / 5.6±0.6 / 5.8±0.7; 208Pb 9.2±1.0 / 6.7±0.8 / 5.3±0.6.

Table 5 is printed rotated, in dot-matrix type, in the format ".277E 01" (= 2.77). Its 25 MeV sets, as an example
of its content (c.m. angle in deg, cross section in mb/sr, error in %):

- **48Ca 25 MeV** (PDF p.124, 32 rows; EXFOR O0178008 has 36 points): 0.0 2.77 2.9 | 10.3 2.32 1.9 | 15.4 1.96 3.4 |
  20.5 1.75 3.1 | 25.6 1.75 3.8 | 30.7 1.62 2.4 | 35.8 1.43 4.1 | 40.9 1.27 2.8 | 46.0 1.18 3.6 | 51.1 1.27 2.9 |
  56.2 1.32 2.9 | 61.3 1.25 2.7 | 66.3 1.18 3.1 | 71.4 1.09 2.8 | 76.4 1.05 3.4 | 81.4 0.906 3.3 | 86.5 0.796 4.1 |
  91.5 0.586 4.4 | 96.5 0.416 5.5 | 101.4 0.446 5.6 | 106.4 0.463 5.2 | 111.4 0.566 4.3 | 116.3 0.624 4.8 |
  121.3 0.494 4.8 | 126.2 0.357 5.9 | 131.1 0.210 8.2 | 136.0 0.130 10.1 | 140.9 0.236 7.1 | 145.8 0.380 4.6 |
  150.7 0.517 3.8 | 155.6 0.636 3.3 | 160.5 0.536 4.0
- **90Zr 25 MeV** (PDF p.126, 32 rows): 0.0 6.02 3.2 | 10.2 4.12 3.5 | 15.2 2.91 3.7 | 20.3 1.74 4.1 | 25.4 1.09 4.8 |
  30.5 0.895 5.2 | 35.5 0.947 4.9 | 40.6 0.884 5.1 | 45.6 0.801 5.3 | 50.7 0.715 5.5 | 55.7 0.554 5.1 |
  60.8 0.480 5.3 | 65.8 0.429 5.6 | 70.9 0.431 5.4 | 75.9 0.424 5.3 | 80.9 0.373 5.8 | 85.9 0.353 6.0 |
  90.9 0.363 5.6 | 95.9 0.365 4.6 | 100.9 0.350 4.6 | 105.9 0.314 4.8 | 110.9 0.225 5.4 | 115.8 0.177 6.1 |
  120.8 0.200 5.8 | 125.7 0.269 4.9 | 130.7 0.329 4.5 | 135.6 0.275 4.8 | 140.6 0.200 5.7 | 145.5 0.122 7.5 |
  150.5 0.173 6.0 | 155.4 0.365 4.4 | 160.3 0.579 3.8
- **120Sn 25 MeV** (PDF p.128, 32 rows): 0.0 6.65 1.9 | 10.1 4.32 2.4 | 15.2 3.30 3.1 | 20.2 2.35 3.5 |
  25.3 2.51 3.5 | 30.4 2.54 3.3 | 35.4 2.48 3.3 | 40.5 2.10 3.6 | 45.5 1.47 4.5 | 50.6 0.844 6.4 | 55.6 0.512 9.0 |
  60.6 0.441 10.0 | 65.7 0.492 8.4 | 70.7 0.542 8.2 | 75.7 0.589 6.8 | 80.7 0.532 8.0 | 85.7 0.385 9.1 |
  90.7 0.223 10.4 | 95.7 0.168 8.7 | 100.7 0.224 7.1 | 105.7 0.264 6.7 | 110.7 0.243 6.6 | 115.7 0.193 7.3 |
  120.6 0.164 9.8 | 125.6 0.148 12.2 | 130.6 0.148 8.6 | 135.5 0.193 8.5 | 140.5 0.152 9.3 | 145.4 0.139 11.2 |
  150.4 0.107 10.9 | 155.3 0.227 7.1 | 160.2 0.302 5.8

The complete table (all 12 sets) is [external/doering_1974_table5.csv](../external/doering_1974_table5.csv), with
its transcription and checks in the file header.

**208Pb 45 MeV near 162° and 164°.** Table 5 for 208Pb 45 MeV (PDF p.129, thesis p.98) ends at 160.1°; its last
rows are 145.2° 0.0391 mb/sr 25.7 % | 150.2° 0.0468 22.4 % | 155.2° 0.00380 117.8 % | 160.1° 0.0165 65.4 %. There
are no points near 162° and 164° and no cross sections of 0.049 or 0.072 mb/sr nearby. The two EXFOR points there
(161.9° and 164.0°) are most likely artefacts of reading Fig. 3, where the backward 208Pb 45 MeV points carry bars of
65–120 %.

**Applied:** angles, values and errors replaced by Table 5 for all 12 records; EXFOR points with no table row
removed. Normalisation 11.2 %: the efficiency's 10 % ⊕ the other systematics' "less than 5 %", taken at
its bound (where EXFOR's 10 % `ERR-1` and the paper differ, the paper is followed).

---

## O0211

**C. B. Fulmer, J. B. Ball, A. Scott, M. L. Whiten, Phys. Rev. 181, 1565 (1969)**; 61.4 MeV elastic scattering.

The paper tabulates cross sections and errors in its Appendix (Tables V–XII, PDF pp.12–15 [1576–1579], column
"±%", integer percentages). EXFOR has these tables as O0211012 (40Ca), 015 (90Zr), 016 (116Sn), 017 (208Pb), STATUS
TABLE, with the authors' errors. O0211004, 007, 008, 009 are separate digitisations of the same data from the
figures (STATUS CURVE), with reader errors only.

| table | target | per-point error (authors, "±%") | source |
|---|---|---|---|
| VII | 40Ca | 5 % at 31.8–93.4°; 10 % at 29.7° and 99.4–107.4°; 8 % at 95.4° | PDF p.13 [1577] |
| X | 90Zr | mostly 5 % at 20.2–40.4°; mostly 10 % at 42–76°; 11–17 % at 82–112.6° | PDF p.14 [1578] |
| XI | 116Sn | 5 % (20–34°), 10 % (36–86°), 13–30 % (88.5–112.5°) | PDF p.15 [1579] |
| XII | 208Pb | 5 % (20–40°), 7–8 % (42–70°), 10–15 % (60–98°), 12–25 % (100–112°) | PDF p.15 [1579] |

Quotes:
- PDF p.3 [1566–1567]: "Errors shown with the data include both the statistical error of the counts and an
  estimate of the uncertainty in determining the tail of the Gaussian elastic peak. … The uncertainty in the
  absolute value of the cross sections due to the determination of the effective target thickness is of order 5%,
  and the uncertainty in the charge collection measurements is about 10%."
- Appendix, PDF p.12 [1576]: "The errors shown are based on counting statistics and uncertainties in the
  subtraction of contaminant or inelastic peaks. Target thickness and beam monitoring uncertainties could
  contribute as much as 10% error to the absolute cross sections. The normalization of the 40Ca cross sections is
  based on fixed-geometry optical-model calculations, as described in Sec. III."
- Fig. 3 caption: "Typical statistical errors are shown for a few large-angle data points. At angles smaller than
  about 50 deg the statistical errors are smaller than the plotted points."

**Applied:** the CURVE digitisations (004, 007, 008, 009) removed from ELM; the tables (012, 015, 016, 017) keep
their per-point errors. Normalisation 5 % ⊕ 10 % = 11.2 %.

---

## O0225

**W. T. Wagner, G. M. Crawley, G. R. Hammerstein, H. McManus, Phys. Rev. C 12, 757 (1975)**; 208Pb(p,p) 35 MeV
(O0225146).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0225146 | dσ/dΩ | not stated; statistical bars drawn only "when greater than the symbol size", and none are visible in the elastic figure (Fig. 6) | counter data "good to about 5%", fixed by matching an optical model (Becchetti–Greenlees) to the measured elastic distribution | PDF p.2; PDF p.8; PDF p.9 (Fig. 6) | low (per point) |

Quotes:
- PDF p.2: "Absolute normalization of the counter data was done by comparison of the optical model using
  Becchetti-Greenlees best-fit parameters with the measured elastic angular distribution."
- PDF p.2: "Absolute normalization of the counter and plate data is believed good to about 5 and 10%,
  respectively."
- PDF p.8: "The error bars indicate statistical errors and were drawn only when greater than the symbol size."

Notes: EXFOR says "From Fig.5", but Fig. 5 shows inelastic cross sections; the elastic distribution is Fig. 6
(PDF p.9), 10–100° c.m., 23 points. Because the absolute scale was fixed with an optical model, the normalisation
is not independent of optical-model predictions.

**Applied:** removed.

---

## O0239

**J. C. Lombardi, R. N. Boyd, R. Arking, A. B. Robbins, Nucl. Phys. A188, 103 (1972)**; 40Ca and 48Ca, 14–16.3 MeV.

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| 002, 004, 006 (40Ca 16.25, 15.65, 14.08 MeV); 014, 016, 018 (48Ca 15.63, 15.05, 14.03 MeV) | dσ/dΩ | statistical 1 %; 2 % assigned for the optical-model analyses (angular misalignment) | 10 % | PDF p.3 (Sec. 2); Figs. 2, 4 | high |
| 003, 005, 007 (40Ca); 015, 017, 019 (48Ca) | Ay | "statistical and include the uncertainties in the measured beam polarization. Typical errors … 2%" (unit not stated) | folded into the per-point error | PDF p.3 | medium |

Quotes (PDF p.3, Sec. 2):
- "To determine the normalizations of our cross-section data we used targets of 1 mg/cm2 or less and measured the
  yield at 4.00 MeV where the scattering is Rutherford at forward angles. These normalizations are estimated to be
  accurate to within 10 %."
- "The statistical uncertainties in the cross-section data are 1 %. Relative errors of 2 % were assigned for the
  optical-model analyses to account for angular misalignments. Errors assigned to the analyzing-power data are
  statistical and include the uncertainties in the measured beam polarization. Typical errors for these data are
  2 %."
- PDF p.5: "The uncertainties are smaller than the dot size, and the [...]" (cut at the page break).

Notes:
- The fit of eq. (3) (PDF p.5) uses these values as "the respective experimental uncertainties".
- The Ay "2 %" is read as 0.02 absolute: Ay passes through zero, and the dots in Figs. 2 and 4 are about 0.03–0.05
  in Ay, consistent with an absolute 0.02.
- The 48Ca target contained 3.6 % 40Ca. Its correction adds an unquantified uncertainty where the 40Ca cross
  section dominates.

**Applied:** σ 2 %; Ay 0.02; both ⊕ the reader error. Normalisation 10 % for the cross sections; the Ay
records keep their curated normalisation.

---

## O0246

**T. Kruse, W. Makofske et al., Nucl. Phys. A169, 177 (1971)**; 148Sm(p,p) 16 MeV (O0246017).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0246017 | dσ/dΩ (shown as ratio to Rutherford, Fig. 2) | not stated for the data; no bars in Fig. 2. For the fits "an experimental error of 10% was arbitrarily assigned to each point" | normalised to Rutherford yields at 5 MeV in the same configuration; no uncertainty given | PDF p.2 (Sec. 2); PDF p.3 (Fig. 2); PDF pp.5–6 (Sec. 4) | medium |

Quotes:
- PDF p.2: "The resulting angular distributions were converted to absolute cross sections by normalizing with
  respect to angular distributions taken at 5 MeV incident proton energy, with the identical experimental
  configurations as in the 16 MeV runs. The 5 MeV data were assumed to be purely Rutherford."
- PDF pp.5–6: "(In order to avoid over-emphasis on the large forward angle cross sections, an experimental error of
  10% was arbitrarily assigned to each point.)"

Notes:
- "For completeness the Sm data from ref. 1) is also shown" (ref. 1: Stoler et al., Phys. Rev. 155, 1334 (1967),
  the same group). The 148Sm points may therefore be from that earlier work.
- Fig. 2 is plotted against the laboratory angle; the corpus record carries c.m. angles.

**Applied:** σ 10 % ⊕ the reader error. Normalisation: corpus default.

---

## O0253

**J. F. Dicello, G. Igo, W. T. Leland, F. G. Perey, Phys. Rev. C 4, 1130 (1971)**; 40Ca(p,p) at 10 energies,
13.98–21.68 MeV (O0253017).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0253017 | dσ/dΩ (Fig. 5, ratio to Rutherford) | relative uncertainties "approximately ±2%"; "approximately the size of the symbols unless otherwise indicated"; larger at forward angles through the carbon/oxygen subtraction (±25 % of that correction) | about ±5 %: target areal density ±3 %, collimator solid angle about 2 % | PDF p.1 (abstract); PDF p.5 (Sec. IV.D); PDF p.6 (Fig. 4, Sec. IV.E) | high |

Quotes:
- PDF p.1, abstract: "Relative uncertainties are approximately ±2%. Absolute uncertainties are approximately ±5%."
- PDF p.5, IV.D: "The following uncertainties were included in calculating the relative errors for the
  differential cross sections: (1) uncertainties arising from counting statistics on the number of counts in the
  elastic peak and the number of counts lost because of the dead time of the computer, (2) the uncertainty (±25%)
  in the corrections for carbon and oxygen at forward angles (see Sec. III B), (3) the uncertainty for
  normalization of the data (see Sec. III D), (4) the uncertainty (±0.5%) in the current integration."
- PDF p.5: "The differential elastic cross sections, the relative uncertainties, and the absolute uncertainties are
  listed elsewhere."
- PDF p.6, Fig. 4 caption: "The relative uncertainties are approximately the size of the symbols unless otherwise
  indicated."

EXFOR's COMMON block has `ERR-1` 2 % ("relative uncertainties"), `ERR-2` 5 % (absolute) and `ERR-3` 25 % (the C/O
correction), matching the paper, plus `ERR-DIG` 3 %.

**Applied:** σ 2 % ⊕ the reader error (3 %), i.e. 3.6 %. This is the same total the record had before, since the
curated error already combined `ERR-1` with `ERR-DIG`. Normalisation: corpus default 5 % (as stated).

---

## O0254

**D. J. Baugh, G. W. Greenlees et al., Nucl. Phys. 65, 33 (1965)**; 17.8 MeV, 28Si (O0254009) and 40Ca (O0254010).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0254009 (28Si), O0254010 (40Ca) | dσ/dΩ, relative | not stated: "the same order of statistical accuracy as the polarization values"; no bars in Fig. 2 | arbitrary: relative cross sections that "require a normalization procedure" | PDF p.4 [36]; Fig. 2, PDF p.7 [39] | low |
| (O0254003, 004, not in the corpora) | Ay 28Si, 40Ca | tabulated, Table 1: 28Si ±0.010 to ±0.040, 40Ca ±0.013 to ±0.040 | beam polarisation taken as 1.00 | Table 1, PDF p.5 [37] | high |

Quotes:
- PDF p.4 [36]: "For Si, Ca and Mo relative differential cross sections were obtained by adding the left and right
  polarization counts recorded for a given monitored beam. The results have only the same order of statistical
  accuracy as the polarization values and require a normalization procedure to be adopted in the optical model
  fitting."
- Fig. 2 caption (PDF p.7): "Differential cross sections for the scattering of 17.8 MeV protons. The crosses
  represent data of ref. 2)."

**Applied:** removed.

---

## O0259

**D. K. McDaniels, J. R. Tinsley et al., Phys. Rev. C 33, 1943 (1986)**; 208Pb(p,p) 200 MeV (O0259002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0259002 | dσ/dΩ (Fig. 3) | not stated; Fig. 3 shows solid circles (data of ref. 25, TRIUMF) and crosses with no visible bars | p–p cross sections "within ±6%" of the standard; 208Pb elastic "within ±7%" of the TRIUMF values | PDF p.3 [1945]; Fig. 3 | low |

Quotes (PDF p.3 [1945]):
- "On the average our measured p-p cross sections were within ±6% of the standard values obtained from the
  phase-shift calculations. In addition, the values of the 208Pb elastic-scattering cross sections measured in this
  experiment were compared with the precise TRIUMF values at 200 MeV; agreement to within ±7% was obtained."
- Fig. 3 caption: "Elastic scattering data used to obtain our optical model parameters. The solid circles are points
  from Ref. 25."

Note: the points digitised by EXFOR may be the earlier TRIUMF data (ref. 25) rather than this measurement.

**Applied:** removed.

---

## O0272

**L. Lee, T. E. Drake et al., Phys. Lett. B 205, 219 (1988)**; 208Pb(p,p) 200 MeV (O0272002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0272002 | dσ/dΩ vs q (Fig. 1) | not stated; Fig. 1 spans 20 decades with no visible bars | not stated | Fig. 1, PDF p.3 [221]; PDF pp.2–3 | low |

Quote (PDF p.2 [220]): "More detailed descriptions of the experiments are presented elsewhere [5,6]." The 208Pb
data are "older and remeasured" data from ref. 5 (PDF p.1 [219]).

**Applied:** removed.

---

## O0300

**K. Kwiatkowski, N. S. Wall, Nucl. Phys. A301, 349 (1978)**; 100.4 MeV, 90Zr (O0300004) and 120Sn (O0300005).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0300004, O0300005 | dσ/dΩ (shown as ratio to Rutherford, 10–80°) | statistical ≤ 1 % to 50°, ≤ 3 % to 80°; an angle term of up to 3.8 % added; total relative error "of order ±4%"; bars drawn "where larger than the point" | "better than 8%": solid angle ±3 %, target thickness 1 %, tail-correction normalisation 5 %, detector-reaction correction (9 ± 4.5) %, dead time 0.6 % | PDF pp.2–3; Fig. 1 caption (PDF p.3); Fig. 2 (PDF p.4) | high |

Quotes (PDF pp.2–3):
- "Statistical errors were ≤ 1 % for data out to 50 deg and in the range out to 80 deg did not exceed 3 %."
- "An additional error was assigned to the differential cross section which was obtained from a consideration of
  the angular aperture and the angular uncertainty and added at most 3.8 % to the overall relative error, with the
  major contribution coming from the angular uncertainty."
- "A consideration of all the errors … lead to a better than 8 % accuracy for the absolute cross sections and of
  order ±4 % for relative cross sections."

**Applied:** σ 4 % ⊕ the reader error. Normalisation 8 %.

---

## O0328

**M. P. Fricke, E. E. Gross, B. J. Morton, A. Zucker, Phys. Rev. 156, 1207 (1967)**; 40 MeV: cross sections 004
(59Co), 005 (68Zn), 007 (120Sn); Ay 009 (59Co), 010 (68Zn), 011 (120Sn).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| 004, 005, 007 | dσ/dΩ | "relative probable errors which include statistical errors and the uncertainty in background subtraction"; no numbers in the text (tables deposited with the American Documentation Institute). Fig. 2: bars mostly within the symbol, about 10–20 % at backward angles (*estimate*) | ±5 % target thickness | PDF p.5 [1211]; Fig. 2, PDF p.3 [1209] | high (EXFOR `ERR-1`) |
| 009, 010, 011 | Ay | same bar definition; Fig. 3: most bars ≤ 0.02–0.03, a few ±0.1–0.2 at large angles and near minima (*estimate*) | beam polarisation (27.4 ± 0.5) %, i.e. 1.8 % relative on all Ay | PDF p.4 [1210]; PDF p.5 [1211] | high (EXFOR `ERR-1`) |

Quotes:
- PDF p.5 [1211]: "The error bars in Figs. 2 and 3 are relative probable errors which include statistical errors and
  the uncertainty in background subtraction."
- PDF p.5: "Relative errors in the differential-cross-section measurement are chiefly statistical. In addition
  there is an absolute error of ±5% due to the uncertainty in determining the target thickness."
- PDF p.4 [1210]: "Our result is that the polarization of the 40-MeV beam is (27.4±0.5)%, including the
  uncertainty in P_C."
- Figure captions (PDF pp.3–4): "Typical statistical error bars are shown."

Notes:
- EXFOR's `ERR-1` reads "Statistical errors and the uncertainty in background subtraction", the paper's definition
  of its bars word for word.
- Since 2023 (HISTORY: re-digitised; `ERR-T → ERR-1`) the authors' bars are in `ERR-1`. They are absolute in the
  data's units although the column is labelled PER-CENT. They exist only where a bar was legible in the figure.
- EXFOR's `ERR-2` "2% uncertainty in current integration" does not appear in the paper's text.

**Applied:** per-point error = `ERR-DIG` ⊕ `ERR-1`. Where `ERR-1` is blank, it is interpolated linearly in angle
(relative for cross sections, absolute for Ay) and held constant beyond the first and last point that has one.
Normalisation `ERR-2` ⊕ `ERR-3` = 5.4 % for the cross sections, and the beam polarisation's 1.8 % for the analysing
powers.

---

## O0370

**W. S. Gray, R. A. Kenefick et al., Phys. Rev. 142, 735 (1966)**; 90Zr(p,p) 18.8 MeV (O0370002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0370002 | dσ/dσ_R (Fig. 3) | statistical and background uncertainty; no numbers; no bars visible in Fig. 3 | about 5 % ("the estimated error on the absolute normalization"); target 2.39 ± 0.05 mg/cm² | PDF p.3 [736]; PDF pp.4–5 [738–739] | low (per point), medium (normalisation) |

Quotes:
- PDF p.3: "Error bars on the data are the statistical error and background uncertainty, in the case of single
  peaks, but include an additional error estimate if the peak was a member of a partially resolved doublet or
  multiplet."
- PDF pp.4–5: "the optical-model fits to the present data would be improved if the data were increased uniformly by
  about 10%, although this is roughly twice the estimated error on the absolute normalization."
- PDF p.4: "χ² was calculated with Δσ_EX/σ_EX = 10% for all N = 38 angles" (a fit weight).

**Applied:** removed.

---

## O0372

**K. Matsuda, H. Nakamura et al., J. Phys. Soc. Jpn. 22, 1311 (1967)**; 90Zr (O0372013) and 92Zr (O0372014) at
14.25–14.71 MeV.

The publication was not available.

**Applied:** removed.

---

## O0382

**K. Yagi, H. Ejiri et al., Phys. Lett. 10, 186 (1964)**; 40Ca(p,p) 55 MeV (O0382002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0382002 | dσ/dΩ, Fig. 2 | not stated; small symbols with no resolvable bars on a log axis; numerical values "published in the INS-Journal" | ±15 % | PDF p.2 [187] | low |

Quote (PDF p.2): "Errors in absolute values of the cross sections are estimated to be ±15%."

EXFOR gives author errors at 2 of the 18 points.

**Applied:** removed.

---

## O0384

**W. S. Gray, R. A. Kenefick et al., Nucl. Phys. 67, 542 (1965)**; 40Ca(p,p) at 14.6 MeV (O0384002, Fig. 4) and
17.3 MeV (O0384003, Fig. 5).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0384002, O0384003 | dσ/dΩ | not stated for elastic; no bars in Figs. 4–5. For the inelastic figures: "When no error bars are shown, the estimated relative error is less than the radius of the circles." | ±15 % | PDF p.5 [545–546]; Figs. 4–5, PDF p.9 [550] | low (per point), high (normalisation) |

Quote (PDF p.5): "The final normalization was therefore taken from the new data, with an error of 10% assigned due to
the uncertainty in ascertaining the correct scale factor. The overall uncertainty in the normalization of the Ca40
cross sections is estimated at ±15% when other factors such as the uncertainties in target thickness, geometry and
integrated incident flux are taken into account."

Note: the authors found the fit at 14.6 MeV "rather poor", with possible compound-elastic scattering near the (p,n)
threshold (14.68 MeV); the 14.6 MeV target was "wrinkled".

**Applied:** removed.

---

## O0387

**A. Tellez, R. Ballini et al., Nucl. Phys. A127, 438 (1969)**; 48Ca(p,p) 12 MeV (O0387002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0387002 | dσ/dΩ (Fig. 3: Saclay circles, Argonne crosses) | not stated; no bars | not measured: set by matching a forward-angle point to the Argonne curve (ref. 6) | PDF p.4 [441] | low |

Quote (PDF p.4): "The absolute magnitude of the elastic differential cross section was obtained by comparison with a
forward angle point of the curve of ref. 6)."

**Applied:** removed.

---

## O0446

**S. Kobayashi, K. Matsuda et al., J. Phys. Soc. Jpn. 15, 1151 (1960)**; 58Ni and 60Ni(p,p), 10.7–15.4 MeV
(O0446002, O0446003).

The publication was not available.

**Applied:** removed.

---

## O0456

**M. K. Brussel, J. H. Williams, Phys. Rev. 114, 525 (1959)**; 39.8 MeV, 54Fe (O0456002, Fig. 4) and 56Fe
(O0456003, Fig. 6).

| subentries | observable | per-point error (authors) | normalisation / systematic | source | confidence |
|---|---|---|---|---|---|
| O0456002, O0456003 | dσ/dΩ | "statistical accuracy of ~3%"; non-elastic contamination "about 3%" on average; counting standard deviation "less than 3.3%, … closer to 2.5%" | angle-dependent geometric error 0–7.5 % (±0.15° detector angle); target angle up to 3 %; current drift 1 %; multiple scattering up to 10 % at the first minimum; target thickness 1 %; "probable error" ±6 % to ±10 % | abstract (PDF p.1); PDF p.4; PDF p.7 (Sec. C) | high |

Quotes:
- PDF p.1, abstract: "Absolute differential cross sections obtained with a statistical accuracy of ~3% have been
  determined for the elastically scattered …"
- PDF p.7: "Nonelastic scattering contributions to the measured elastic cross sections also were a function of
  scattering angle. An over-all average estimate of such errors, however, is about 3%. The statistical accuracy of
  most points at which measurements were taken was also 3%."
- PDF p.7: "To summarize: The probable error for the experimental unaveraged absolute cross sections lies from ±6%
  to ±10% for Fe54, Fe56, Ni58, and from ±7% to ±11% for Ni60 and Cu65."

Note: the statistical (3 %) and non-elastic (3 %) terms are separate; with both, the per-point error would be
about 4.2 %.

**Applied:** σ 3 % ⊕ the reader error. Normalisation: corpus default.

---

## O0458

**P. Beuzit, J. Delaunay et al., Nucl. Phys. A128, 594 (1969)**; 64Ni(p,p) 12 MeV (O0458004).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0458004 | dσ/dΩ | not stated; Fig. 3 symbols carry tiny bars of about symbol size (*estimate*) | normalised to Lee & Schiffer (ref. 12); no uncertainty quoted | PDF p.4 (Sec. 3.2); Fig. 3, PDF p.7 | low |

Quote (PDF p.4): "They agree well with those measured by Lee and Schiffer [ref. 12)], hence the absolute values of
the cross sections were obtained by normalizing our experimental points to the values of ref. 22)."

The paper contains no statistical or systematic error statement.

**Applied:** removed.

---

## O0471

**S. J. Burger, G. Heymann, Nucl. Phys. A243, 461 (1975)**; 12.52 MeV, 92Mo (O0471007) and 94Mo (O0471008).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0471007, O0471008 | dσ/dΩ (ratio to Rutherford) | "not more than 6 % for each isotope"; no visible bars in Fig. 3 | normalised to the optical model at forward angles; "upper limit for the total error … ±20 %" | PDF p.4; Fig. 3, PDF p.8 | medium |

Quote (PDF p.4): "The over-all absolute normalization depends on accuracy in beam integration (1 %), solid angle
determination (1 %), and target thickness measurement (12 %). … Absolute normalization factors were therefore
determined by normalizing the elastic cross sections to the optical model predictions at those forward angles … The
relative errors in the determination of the elastic scattering cross sections were estimated to be not more than
6 % for each isotope. The upper limit for the total error in the final elastic scattering cross sections was set at
±20 %."

**Applied:** σ 6 % ⊕ the reader error. Normalisation: corpus default.

---

## O0545

**M. M. Stautberg, J. J. Kraushaar, Phys. Rev. 151, 969 (1966)**; 19.4 MeV, 92Zr (O0545002) and 94Zr (O0545006).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0545002, O0545006 | dσ/dΩ | statistical "less than 1% for angles less than 90° and less than 3% for angles greater than 90°"; no bars shown for elastic | "uncertain by 5%" | PDF pp.3–4 (Sec. II); Fig. 3 | high |

Quote (PDF pp.3–4): "Error bars are not shown for the elastic distributions, but the statistical error is less than
1% for angles less than 90° and less than 3% for angles greater than 90°. The absolute normalization of the elastic
and inelastic cross sections is uncertain by 5%, owing to errors in measuring the solid angle, target-thickness
uncertainty, and charge-collection efficiency."

Notes: these are upper bounds. The authors' own fit used "Δσ = 10% for all 29 angles" (PDF p.4), a fit weight.

**Applied:** σ 1 % below 90°, 3 % above, ⊕ the reader error. The corpus applies the paper's 90° to its c.m. angle.
Normalisation: corpus default 5 % (as stated).

---

## O0549

**B. C. Sinha, V. R. W. Edwards et al., Nucl. Phys. A183, 401 (1972)**; 92Mo at 19.85, 30.3, 49.45 MeV
(O0549003) and 94Mo at 49.45 MeV (O0549005).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0549003, O0549005 | dσ/dΩ | "typically ~ 4 %", fairly constant over angle, mostly statistical; too small to show | 1 % target thickness; nothing else stated | PDF p.7 (Sec. 2); Figs. 1, 2, 4 | high |
| (Ay subentries) | Ay | ±0.03 at forward angles to ±0.1 at backward angles | — | PDF p.7 | high |

Quote (PDF p.7): "The cross section errors are too small to show on the graphs. They are fairly constant through the
angular range and are typically ~ 4 %, most of which is statistical and the remainder is due mainly to a 1 %
uncertainty in target thickness. The errors shown for the polarization are largely statistical and varied between
±0.03 at forward angles and ±0.1 at backward angles."

**Applied:** σ 4 %; Ay 0.03; both ⊕ the reader error. Normalisation: corpus default.

---

## O0552

**R. D. Rathmell, W. Haeberli, Nucl. Phys. A178, 458 (1972)**; 208Pb(p,p) 12.98 MeV (O0552008).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0552008 | σ/σ_R (Fig. 2) | "total uncertainty in the relative cross-section measurements ranges from 0.5% to 3%"; bars within the symbols | about 1 % | PDF p.3 [461] (Sec. 4); Fig. 2, PDF p.6 [463] | high (range); angle dependence not stated |
| O0552009 | Ay | "range from 0.002 to 0.01" (EXFOR already has the authors' values) | — | PDF p.3 | high |

Quote (PDF p.3 [461]): "The total uncertainty in the relative cross-section measurements ranges from 0.5% to 3%. The
uncertainty in the relative solid angles and in the cross section at the monitor detectors at 13 deg (sect. 2) and
effects of slit edge scattering give rise to an estimated uncertainty in the absolute normalization of the cross
section of about 1%." Also: "The uncertainties in the polarization range from 0.002 to 0.01."

Note: EXFOR's ERR-ANALYS misquotes these as "0.5% To 0.3%" and "0.002 to 0.001".

**Applied:** σ 1.5 % (middle of the stated range) ⊕ the reader error at points without an EXFOR author error; Ay
0.01. Normalisation: corpus default.

---

## O0553

**C. Rolland, B. Geoffrion et al., Nucl. Phys. 80, 625 (1966)** (in French); 40Ca and 209Bi at 150 MeV (O0553004,
O0553006) and 75 MeV (O0553010, O0553014).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0553004, O0553006 (152–153 MeV) | dσ/dΩ | statistical errors only "on the curves", not legible; the only numbers are for 12C (Table 1): 3–6 %, 11 % at 73.6° | "une erreur systématique possible de 5%" | PDF p.4; Table 1, PDF pp.3–4 | low |
| O0553010, O0553014 (75–78 MeV) | dσ/dΩ | not given; "La statistique était moins bonne qu'à 150 MeV" | ±10 % | PDF pp.10–11 | low |

Quotes:
- PDF p.4: "En dehors des erreurs statistiques, une erreur systématique possible de 5%, la même pour tous les corps
  à tous les angles, a été admise. Seules sont portées sur les courbes et dans le tableau 1, les erreurs
  statistiques."
- PDF pp.10–11: "Pour les valeurs des sections efficaces absolues, nous avons en plus de l'erreur statistique, une
  incertitude systématique, identique pour toutes les cibles et à tous les angles, de ±10%."

**Applied:** removed.

---

## O0580

**E. Fretwurst, G. Lindström et al., Nucl. Phys. A468, 247 (1987)**; 94Mo(p,p) 25.6 MeV (O0580002).

| subentry | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O0580002 | σ/σ_R, Fig. 2 | "related to statistics", no numbers; bars mostly smaller than the symbols (about 4–5 % on the log scale, *estimate*); fluctuations "exceeding these statistical errors" may occur | about ±1 %, by normalising to the optical-model fit at forward angles | PDF p.4 [250] (Sec. 2); Fig. 2, PDF p.13 [259] | low |

Quote (PDF p.4): "This way the absolute integrated cross sections for the elastic scattering were fixed to about
±1%. Error bars given to single points in the angular distributions result from the peak-integrating procedure and
are related to statistics (see ref. 33). Due to small target contaminations, which could not explicitly be
accounted for, as well as due to uncertainties in the background determination, point-to-point fluctuations of the
cross sections may occur, exceeding these statistical errors."

EXFOR's reader uncertainty for this record is 0.1 %.

**Applied:** removed.

---

## O1103

**W. H. L. Moonen, P. J. Van Hall et al., J. Phys. G 19, 635 (1993)**; 22.3 MeV, 72Ge, 74Ge, 78Se, 80Se (O1103004,
006, 012, 014; Figs. 1–2, PDF p.5).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O1103004, 006, 012, 014 | σ/σ_R | not stated for elastic; the only figure is a design goal for the inelastic levels: "an accuracy of 3% (1000 counts) in the two-phonon levels"; bars not visible | free parameter in the optical-model search | PDF pp.4–5 | low |

Quote (PDF p.4): "The experiments were designed to obtain an accuracy of 3% (1000 counts) in the two-phonon levels.
It was not possible, however, to achieve this in all instances."

**Applied:** removed. (The same group's O1104 states 2 %; it is not carried over.)

---

## O1104

**R. M. A. L. Petit, B. W. Van der Pluym et al., J. Phys. G 20, 1955 (1994)**; 22.3 MeV, 106–116Cd: cross sections
002, 004, 006, 008, 010, 012; Ay 003, 005, 007, 009, 011, 013 (Figs. 2–3).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| cross sections | σ/σ_R | "A minimal error of 2% was assumed in the values of cross section and analysing power"; statistics "usually better than 2%" | by extrapolating the optical-model fits to θ = 0 (free); differences from Cereda of up to 35 % (usually < 20 %) | PDF p.3; PDF p.10 | high |
| Ay | Ay | the same sentence (relative to \|Ay\| or a floor: not specified) | beam polarisation about 90 %; no uncertainty quoted | PDF p.3 | medium |

Quotes:
- PDF p.3: "A minimal error of 2% was assumed in the values of cross section and analysing power, due to the
  normalization procedure."
- PDF p.10: "While statistics in our experiment are usually better than 2% in the individual points, we notice some
  normalization differences (up to 35% but usually less than 20%) between our values and Cereda's."

**Applied:** σ 2 %; Ay max(0.02 |Ay|, 0.01); both ⊕ the reader error. Normalisation: corpus default.

---

## O1109

**W. H. L. Moonen, J. H. A. M. Krabbenborg et al., J. Phys. G 19, 1191 (1993)**; 20.4 MeV, 64–70Zn: cross sections
002, 004, 006, 008; Ay 005 (66Zn); Fig. 2, PDF p.5.

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| 002, 004, 006, 008 | σ/σ_R | not stated; bars not visible beyond the symbols | fit parameter; two data sets merged "after a suitable normalization to the forward-angle data points" | PDF p.3 (Sec. 2); Fig. 2 | low |
| 005 | Ay (66Zn) | not stated; mostly symbol-sized bars | not stated | PDF p.5 | low |

Quote (PDF p.3): "After a suitable normalization to the forward-angle data points of the elastic scattering, the
results of the two sets of experiments were in good agreement with one another."

**Applied:** removed. (The same group's O1104 states 2 %; it is not carried over.)

---

## O1199

**E. Fabrici, S. Micheletti et al., Phys. Rev. C 21, 830 (1980)**; 40Ca Ay at 35 MeV (O1199008, Fig. 9) and at 26.3
and 40 MeV (O1199009, Fig. 11).

| subentries | observable | per-point error (authors) | normalisation | source | confidence |
|---|---|---|---|---|---|
| O1199008, O1199009 | Ay | not stated; plain dots without bars | not stated (beam polarisation not discussed) | Figs. 9, 11 (PDF pp.8, 11) | low |

Quote (PDF p.2): "The uncertainty in absolute cross section values was estimated to be about 4%. Statistical errors
were generally negligible. A more detailed discussion of the errors affecting the present measurements is given in
paper II." Paper II is Phys. Rev. C 21, 844 (1980), which was not consulted.

**Applied:** removed.
