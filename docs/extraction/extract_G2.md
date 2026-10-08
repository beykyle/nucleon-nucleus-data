# Author uncertainties extracted for group G2 (O0124, O0157, O0225, O0239, O0246, O0253)

Conventions: "PDF p." = page index of the PDF file in /mnt/ufs18/rs/reactiontheoryinitiative/nucleon_nucleus_data/papers/. Confidence: high = stated/tabulated; medium = stated but arbitrary/partial, or read off a figure; low = inferred.
No entry has tabulated per-point errors. None of the EXFOR subentries carries author per-point errors; all are digitised from figures.

---
## O0124 - Put, Urone, Paans, PLB 35, 311 (1971): 30.4 MeV p on 28Si, 58Ni, 120Sn, backward angles

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0124002 (28Si) | dsigma/dOmega | not stated as a measured error; "experimental error was always smaller" than the 5% used as fit weight | relative data scaled to absolute cross sections of refs [3],[4] in first-maximum overlap region; uncertainty of that scaling not stated | PDF p.1 (text, left+right col.); Fig. 1, 2 (PDF p.2) | medium | 5% (author's fit-weight upper bound). Real stat. error is smaller, but nothing quantitative given |
| O0124004 (120Sn) | dsigma/dOmega | same | same | same | medium | 5% (as above) |

Quotes (PDF p.1; text layer is letter-spaced, wording reconstructed):
- "In the optical model fit each data point was assigned an error of 5%, though the experimental error was always smaller."
- "The relative differential cross sections have been normalized to the absolute cross sections of ref. [3] and [4] in the angular range of the first maximum at which we took overlapping data."
- Beam energy 30.4 +- 0.4 MeV; detector angular acceptance 1.0 deg; targets 28Si 2.4, 58Ni (99.9%) 2.5, 120Sn (98.4%) 1.9 mg/cm2.

Notes:
- Figs. 1-2 (PDF p.2): symbols only, no visible error bars. Fig. 1 plots only every other data point; Fig. 2 (backward detail, 130-180 deg) plots all points. In Fig. 1/2 the dots are earlier data from refs [3] (Cole et al., NP 75, 241, 1966) and [4] (Ridley & Turner, NP 58, 497, 1964); triangles are the present work. EXFOR (O0124002/004, "CURVE by CAJAD", 42-44 points) may mix both data sets if the whole curve was digitised; check that the corpus points are the triangles (present work), otherwise the normalisation/errors belong to refs [3],[4].
- The data are normalised to refs [3],[4], so the absolute scale is inherited (not independent). No numeric systematic is stated.
- EXFOR gives ANG-ERR 0.4 deg (reader) and EN-ERR 0.4 MeV (author).

---
## O0157 - Devins, Forster, Gigas, NP 35, 617 (1962): 30.8 MeV p on 60Ni, 208Pb

**WRONG PDF.** /mnt/ufs18/.../papers/O0157.pdf (21 pp.) is Moonen et al., J. Phys. G 19, 635 (1993), "Polarized-proton scattering by even-mass germanium and selenium isotopes at 22 MeV". It is not the Devins paper and contains nothing on 30.8 MeV p + Ni/Pb. The only author information available is the EXFOR bibliography ERR-ANALYS (compiler's transcription of the paper, not verified here).

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0157002 (60Ni) | dsigma/dOmega | "absolute errors" ~3.5% at forward angles rising to ~10% at extreme backward angles (angle-dependent; intermediate values not given) | not separately stated; the quoted errors are called "absolute" | EXFOR ERR-ANALYS (001) of O0157 (exfor_crosscheck_generated.md, "## O0157"); original paper NOT available | low-medium (stated in EXFOR, unverified, PDF wrong) | 3.5% forward, ramping to 10% at the most backward angles (the ramp shape is my inference). Replace the current flat 2.6% (reader) |
| O0157004 (208Pb) | dsigma/dOmega | same | same | same | low-medium | same as above; replace flat 4.0% (reader) |

EXFOR quote: "THE ABSOLUTE ERRORS OF THE EXPERIMENT WERE ESTIMATED TO VARY FOR ELASTIC SCATTERING BETWEEN APPROX. 3.5% AT FORWARD ANGLES TO APPROX. 10% AT EXTREME BACKWARD ANGLES."
Action: obtain the correct PDF (Nucl. Phys. 35 (1962) 617) to confirm and to find the angle at which the error grows, and whether the 3.5-10% is the total (including normalisation) or per-point.

---
## O0225 - Wagner, Crawley, Hammerstein, McManus, PRC 12, 757 (1975): 35 MeV p on 208Pb

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0225146 | dsigma/dOmega (elastic) | not stated. Counting-statistics bars are drawn in Figs. 2-5 only "when greater than the symbol size"; in Fig. 6 (the elastic figure) no error bars are visible (smaller than symbols), dσ spans ~5 decades | counter data: absolute normalisation "good to about 5%" (obtained by matching Becchetti-Greenlees OM to the measured elastic distribution) ; plate data 10% | PDF p.2 (normalisation paragraph); PDF p.8 (caption Figs. 2-5 text); PDF p.9 (Fig. 6, text) | per-point: low; norm: high | Per-point: use a small floor, ~2% (inferred, Fig. 6 bars < symbols; keep the present reader value 1.9% as the floor). Norm: 5% (stated) - but see note on circularity |

Quotes:
- (PDF p.2) "Absolute normalization of the counter data was done by comparison of the optical model using Becchetti-Greenlees best-fit parameters with the measured elastic angular distribution."
- (PDF p.2) "Absolute normalization of the counter and plate data is believed good to about 5 and 10%, respectively."
- (PDF p.2) "The normalization from the NaI detector agreed to within 10% with the normalization using the integrated beam current."
- (PDF p.8) "The error bars indicate statistical errors and were drawn only when greater than the symbol size."

Notes:
- EXFOR says "From Fig.5", but Fig. 5 is the inelastic cross sections (6.9-8.2 MeV excitation). The elastic distribution is Fig. 6, PDF p.9 ("Figure 6 displays the 35 MeV proton elastic scattering angular distribution as measured with the wire counter"). Digitised points are 10-100 deg c.m. (23 points).
- Circularity: the absolute scale of the elastic data was fixed by agreement with a BG optical-model prediction, so the 5% is an uncertainty of the model matching, and the data are biased toward BG predictions. Flag as a weakly independent normalisation.
- Fig. 6 is a log plot spanning 10^5 to 1 mb/sr, so any error bar is tiny; digitisation reader error dominates.

---
## O0239 - Lombardi, Boyd, Arking, Robbins, NPA 188, 103 (1972): 40,44,48Ca, 10.8-16.3 MeV

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0239002 (40Ca 16.25) | dsigma | statistical 1%; 2% assigned for OM analyses (angular misalignment) | 10% | PDF p.3 (Sec. 2), Fig. 2 | high | 2% rel. |
| O0239004 (40Ca 15.65) | dsigma | same | 10% | same | high | 2% rel. |
| O0239006 (40Ca 14.08) | dsigma | same | 10% | same | high | 2% rel. |
| O0239014 (48Ca 15.63) | dsigma | same (+ extra uncertainty from 3.6% 40Ca-impurity correction at angles where 40Ca xsec >> 48Ca, not quantified) | 10% | PDF p.3, Fig. 4 (p.5) | high (2%), medium for impurity-affected angles | 2% rel.; consider inflating near 40Ca-dominated angles (not quantified by authors) |
| O0239016 (48Ca 15.05) | dsigma | same | 10% | same | same | same |
| O0239018 (48Ca 14.03) | dsigma | same | 10% | same | same | same |
| O0239003/005/007 (40Ca 16.25/15.65/14.08) | Ay | "statistical and include the uncertainties in the measured beam polarization. Typical errors ... 2%" (unit not specified; no tabulated values) | polarization uncertainty folded into the per-point error; no separate scale error stated | PDF p.3; Figs. 2 p.4, 4 p.5 | medium (value stated, unit ambiguous) | Ay absolute error 0.02 (reading "2%" as absolute Ay units; Ay oscillates through zero so a relative error is meaningless). Replace the corpus's relative Ay "errors" (e.g. -20.8%, -400%) |
| O0239015/017/019 (48Ca 15.63/15.05/14.03) | Ay | same | same | same | medium | 0.02 absolute |

Quotes (PDF p.3, Sec. 2):
- "To determine the normalizations of our cross-section data we used targets of 1 mg/cm2 or less and measured the yield at 4.00 MeV where the scattering is Rutherford at forward angles. These normalizations are estimated to be accurate to within 10 %."
- "The statistical uncertainties in the cross-section data are 1 %. Relative errors of 2 % were assigned for the optical-model analyses to account for angular misalignments. Errors assigned to the analyzing-power data are statistical and include the uncertainties in the measured beam polarization. Typical errors for these data are 2 %."
- (PDF p.5, text under Fig. 4) "Figs. 2, 3 and 4 show the cross-section and analyzing-power angular distributions and their optical-model fits. The uncertainties are smaller than the dot size, and the" [sentence is cut at the page break; the text on the next page is a table, so the continuation is not in the PDF].
- (PDF p.3) detector placement "done to within 1/4 deg" [fraction garbled in text layer]; targets about 3 mg/cm2; 40Ca/44Ca targets 99.99% / 98.5% enriched; 48Ca target had 3.6% 40Ca impurity.
- Authors note nuclear sizes were "relatively insensitive to normalization".

Notes:
- chi2 in eq. (3) (PDF p.5) uses Delta-sigma and Delta-A, "the respective experimental uncertainties", i.e. the 2% (dσ) and ~2% (Ay) values are the ones the authors actually fitted with.
- Whether the "2%" for Ay is relative or absolute is the one ambiguity; the figures (Fig. 2, 4) show Ay ranging about +-0.8 with dots whose size is roughly 0.03-0.05 in Ay, consistent with an absolute ~0.02.
- Dσ digitised values drawn from figures that plot dσ in mb/sr on a linear (not log) scale; the corpus's current per-point 0.6-1.6% (reader) is below the authors' 2%.

---
## O0246 - Kruse et al., NPA 169, 177 (1971): 16 MeV p on heavy collective nuclei (148Sm)

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0246017 (148Sm, 16 MeV) | dsigma/dOmega (shown as ratio to Rutherford, Fig. 2) | not stated for the data. Fig. 2 has points only, no error bars. For optical-model fits "an experimental error of 10% was arbitrarily assigned to each point" | cross sections normalised to Rutherford yields measured at 5 MeV with identical configuration; no uncertainty given | PDF p.2 (Sec. 2); PDF p.3 (Fig. 2, journal p.179); PDF p.5-6 (Sec. 4) | medium (stated, but an arbitrary fit weight, not a measurement) | 10% rel. (the only author-stated figure; statistical error is certainly smaller, probably a few %, but nothing is stated). Norm: not stated; keep the 5% default |

Quotes:
- (PDF p.2) "The resulting angular distributions were converted to absolute cross sections by normalizing with respect to angular distributions taken at 5 MeV incident proton energy, with the identical experimental configurations as in the 16 MeV runs. The 5 MeV data were assumed to be purely Rutherford."
- (PDF p.5-6) "(In order to avoid over-emphasis on the large forward angle cross sections, an experimental error of 10% was arbitrarily assigned to each point.)"
- (PDF p.3) Fig. 2: "Ratio to Rutherford cross section of the differential cross sections for scattering of 16 MeV protons for various nuclei in the mass range A = 148-198." Angles 50-165 deg in 5 deg steps.

Notes:
- The text says "For completeness the Sm data from ref. 1) is also shown", where ref. 1 = Stoler, Slagowitz, Makofske, Kruse, Phys. Rev. 155 (1967) 1334. The 148Sm points in Fig. 2 (EXFOR "Fig.2") therefore may come from that earlier work (same group), not the new measurement; their normalisation/errors are not restated here.
- The 10% weight was applied "to avoid over-emphasis on large forward-angle cross sections", so it is an angle-independent weight. EXFOR ERR-DIG 0.6e-2 (ratio-to-Rutherford units) is the reader error only.
- Corpus rows are "not matched to EXFOR angles (frame conversion?)"; Fig. 2 abscissa is theta_lab, not c.m.

---
## O0253 - Dicello, Igo, Leland, Perey, PRC 4, 1130 (1971): p + 40Ca, 9.8-21.7 MeV

| subentry | observable | per-point error (author) | normalisation | source | conf. | recommendation |
|---|---|---|---|---|---|---|
| O0253017 (all 10 energies: 13.98, 14.51, 15.57, 15.97, 16.57, 17.57, 18.57, 19.57, 20.57, 21.68 MeV) | dsigma/dOmega (Fig. 5, ratio to Rutherford) | relative uncertainties "approximately +-2%" (abstract); "approximately the size of the symbols unless otherwise indicated" (Fig. 4 caption); larger at forward angles through carbon/oxygen subtraction (+-25% of that correction). Angle-resolved values tabulated "elsewhere" (not in paper) | absolute uncertainty approx +-5%: target areal density +-3%, collimator solid angle (9.5+-0.2)x10^-? in^-2 (about 2%), plus (+0.5% current integration is in the relative part) | PDF p.1 (abstract); PDF p.5 (Sec. IV.D, "listed elsewhere"); PDF p.6 (Fig. 4 caption, Sec. IV.E); PDF p.7 (Fig. 5) | high for the 2%; medium for the angle dependence | 2% rel. per point (high). Forward angles (where C/O subtraction matters): larger, not quantified. Norm 5% (high) |

Quotes:
- (PDF p.1, abstract) "Relative uncertainties are approximately +-2%. Absolute uncertainties are approximately +-5%."
- (PDF p.2) "The principle sources of uncertainties, aside from the angular inaccuracy, were (1) the statistical uncertainties in the number of events recorded and (2) errors associated with uneven density of the target in the region struck by the beam."
- (PDF p.5, IV.D) "The following uncertainties were included in calculating the relative errors for the differential cross sections: (1) uncertainties arising from counting statistics on the number of counts in the elastic peak and the number of counts lost because of the dead time of the computer, (2) the uncertainty (+-25%) in the corrections for carbon and oxygen at forward angles (see Sec. III B), (3) the uncertainty for normalization of the data (see Sec. III D), (4) the uncertainty (+-0.5%) in the current integration."
- (PDF p.5) "The differential elastic cross sections, the relative uncertainties, and the absolute uncertainties are listed elsewhere." (the numerical tables are not in the paper)
- (PDF p.6, Fig. 4 caption) "The relative uncertainties are approximately the size of the symbols unless otherwise indicated."
- (PDF p.6, IV.E) "The average areal densities of the two targets used for these measurements were known to an accuracy of +-3%." / collimator area "(9.5+-0.2)x10^-? in.^-2" [exponent garbled in text layer] / "There were two additional sources of uncertainty not included in either the relative errors or absolute errors. These were an uncertainty in the energy of the beam of +-30 keV and an uncertainty in the position of the E+DE detector of +-0.2 deg."
- (PDF p.2) Angle setting "to an accuracy of +-0.1 deg".

Notes:
- EXFOR common block lists ERR-1 = 2% (relative), ERR-2 = 5% (absolute), ERR-3 = 25% (carbon/oxygen correction uncertainty), EN-ERR 0.03 MeV; these match the paper. The corpus currently combines ERR-1 with the reader ERR-DIG (3%) = 3.6% total; recommend instead 2% per point (author) and drop the reader term, or keep reader term only if you want to include the digitisation error of the Fig. 5 re-digitisation (ANG-ERR-D 1.1 deg is large relative to the 0.1 deg authors' angle accuracy).
- Fig. 5 is plotted as sigma/sigma_Rutherford (log scale) with 4 + 4 + 2 panels (10 energies used here); the optical model is fitted separately above/below 16.6 MeV. Polarization data in Fig. 6 are from other works (not this experiment).
- The +-25% C/O correction applies to the correction, not to the cross section; effect on dσ is largest at forward angles (thin target oxygen/carbon contamination) and not quantified in the paper.
