# Author uncertainties, group G5 (O0079, O0091, O0300, O0456, O0553, O1103, O1104, O1109)

Page numbers are PDF page indices (not journal pages). Confidence: high = stated in text; medium = read off a figure or table proxy; low = inferred. Figure-bar estimates were made by eye on 90-130 dpi renders and are estimates only. No PDF was copied (temporary page renders were deleted).

General observation: in none of these papers are the elastic cross sections or Ay tabulated numerically (O0553 tabulates 12C only). All corpus subentries are digitised from figures, so the only author information is the text statements below.

---
## O0079 (Tesmer & Schmidt, PRC 5, 864) - 54Fe(p,p) 19.6 MeV, subentry 006 (Fig. 8 left)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0079006 | dsigma/dOmega, 54Fe 19.6 MeV | not stated for elastic. Fig. 8 (left) is log-scale; no error bars visible, symbols only | not stated for elastic | p9 (journal p.872), Fig. 8 | low | No author number exists. Keep an assumed floor of about 5% (inferred, generic); do not use 2.3% reader value as an author error. Flag as unverifiable. |

Quotes/notes:
- Paper is a p-gamma angular-correlation paper; the "cross-section data" in Fig. 8 caption: "FIG. 8. Cross-section data for 54Fe. The curves are DWBA predictions with the full Thomas form of DeltaU_so" (p9).
- Only related uncertainty statement (p3-4, Sec. on data analysis, for the gamma efficiency, not elastic scattering): "The uncertainty in F derives primarily from the calibration measurement and is +-2%." and "The uncertainty in W is found by the usual combination of the uncertainties of T, P, and F."
- Text says nothing on how the elastic cross section was normalised or its error. Fig. 7 (polarization, not in the corpus subentry) is the only place the authors discuss reference data (Escudie, Hendrie).

---
## O0091 (Van Hall et al., NPA 291, 63) - Fe/Ni isotopes, 17.2, 20.4, 24.6 MeV

Subentries (after 2022 merge; EXFOR HISTORY: "ERR-T->DATA-ERR; DATA-ERR->ERR-DIG"): DA subentries 002 (54Fe, Fig. 2), 008 (56Fe, Fig. 3), 014 (58Ni, Fig. 4), 018 (60Ni, Fig. 5), 022 (62Ni, Fig. 6); Ay subentries 003 (54Fe), 009 (56Fe), 015 (58Ni), 019 (60Ni), 023 (62Ni). EXFOR COMMON carries ERR-1 = 3% (Fe) / 2% (Ni) "Relative error", ERR-DIG 0.9% (DA) and 0.010 (Ay).

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 002, 008 (Fe-54, Fe-56; 17.2, 20.4, 24.6) | sigma/sigma_R | "Relative errors of 3%" assigned to cross sections of the Fe isotopes (an assignment for the optical-model fit, not a measured statistical error). No bars visible in Figs. 2-3 | Only relative angular distributions measured; normalisation is a free fit parameter in the paper. No absolute error stated. Solid-angle calibration came from separate unpolarised cross-section runs at 20.4 and 24.6 MeV (no number) | p4 (Sec. 3.1); Figs 2-3 pp5-6 | high (text) | 3% relative |
| 014, 018, 022 (Ni-58, 60, 62; 20.4, 24.6) | sigma/sigma_R | "2% was used for the Ni isotopes" (same sentence) | as above | p4; Figs 4-6 pp7-9 | high (text) | 2% relative |
| 003, 009, 015, 019, 023 | Ay | not stated in text. Figs 2-6 right panels: most points have bars smaller than the symbols (about 0.02 or less); a few points show bars of roughly 0.05-0.1 (forward region and near minima/at the largest angles, e.g. the 56Fe 20.4 MeV panel, p6; 58Ni 20.4 MeV panel, p7) | polarization monitored by 52 deg scattering from thick carbon calibrated with Faivre data; beam polarization about 70% (later 85%); no uncertainty quoted | p3 (Sec. 2), Figs. 2-6 | low-medium (estimated from figure) | absolute 0.02 (floor), larger (0.05) only where bars are visibly bigger than the symbol; the 0.010 reader value is too small for visibly barred points |

Quotes:
- p4: "As we had measured relative angular distributions only the normalization was also used as a parameter. Relative errors of 3 % were assigned to the cross sections of the Fe isotopes while 2 % was used for the Ni isotopes."
- p3: "The polarization was continuously monitored downstream from the target ... by scattering from a thick carbon target through 52 deg ... For calibration we used the data of Faivre." ; "At 20.4 and 24.6 MeV the cross sections were measured separately with an unpolarized beam. From these measurements we deduced the calibration of the solid angles for the various detectors."
- p3: "Typical values ... 70 % polarization"; improved to "85 % polarization".

Notes:
- The listed corpus "rel err" for Ay are negative numbers (e.g. -35.7, -250); the corpus appears to divide the absolute error by a signed Ay. The absolute Ay error is the quantity to fix; relative-to-|Ay| is meaningless near zero crossings (-250%, -142.9%).
- 3%/2% are fit weights, hence an overall absolute normalisation uncertainty cannot be given from this paper. The corpus 5% "norm err" is not author-sourced; if a normalisation is used it must be treated as free.
- The 17.2 MeV data have no Ay subentries in the corpus list.

---
## O0300 (Kwiatkowski & Wall, NPA 301, 349) - 90Zr (004) and 120Sn (005), 100.4 MeV

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0300004 (90Zr), O0300005 (120Sn) | dsigma/dOmega (Figs shown as ratio to Rutherford, 10-80 deg) | statistical <= 1% to 50 deg; <= 3% from 50-80 deg; >80 deg <= 10% (not reached in Fig. 2 which ends at 80 deg). Additional angle-aperture/angle-uncertainty error up to 3.8% added to relative error. Total relative error "of order +-4%". Bars drawn "where larger than the point" and are smaller than symbols in Fig. 2 | absolute accuracy "better than 8%": solid-angle +-3%, target thickness 1%, tail-correction normalisation 5%, detector nuclear-reaction correction (9+-4.5)%, dead time 0.6% | p2 (stat), p3 (totals), p3 Fig. 1 caption, p4 Fig. 2 | high | 4% per-point relative (total relative error stated by the authors); angle-dependent alternative: 1% (<50 deg), 3% (50-80 deg) statistical in quadrature with up to 3.8% angle term. Normalisation 8% (corpus uses 5%: increase) |

Quotes (p2-3):
- "Statistical errors were <= 1 % for data out to 50 deg and in the range out to 80 deg did not exceed 3 %. At the largest angles (> 80 deg) the errors did not exceed 10 % except where the differential cross section was ~ 10^-? cm2/sr."
- "An additional error was assigned to the differential cross section which was obtained from a consideration of the angular aperture and the angular uncertainty and added at most 3.8 % to the overall relative error, with the major contribution coming from the angular uncertainty."
- "A consideration of all the errors ... lead to a better than 8 % accuracy for the absolute cross sections and of order +-4 % for relative cross sections." (EXFOR ERR-ANALYS reproduces: ERR-S 1-3, ERR-1 4, ERR-2 8.)
- "solid angle was 0.11 msr with an uncertainty of +-3 %"; "thicknesses known to an accuracy of 1 %"; "uncertainty in the overall absolute normalization of 5 %" (tail correction); "A correction of (9+-4.5) % was supplied ... for nuclear reactions in the detector"; Fig. 1 caption: "experimental points with appropriate error bars indicated (where larger than the point)".

---
## O0456 (Brussel & Williams, PR 114, 525) - 54Fe (002, Fig. 4), 56Fe (003, Fig. 6), 39.8 MeV

| subentry | observable | per-point error (author) | normalisation / systematic | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0456002 (54Fe), O0456003 (56Fe) | dsigma/dOmega | "statistical accuracy of ~3%" (abstract); "statistical accuracy of most points ... was also 3%"; nonelastic-scattering contamination error "over-all average ... about 3%"; counting standard deviation "less than 3.3%, in most instances ... closer to 2.5%". Figures show "typical errors include statistical and nonelastic scattering errors only" (error bars drawn on a few points only, p4 Fig. 4, p5 Fig. 6) | Angle-dependent geometric error: from 0 (at maxima) up to 7.5% (where cross section changes fastest), from +-0.15 deg detector angle error; target angle error +-1.5 deg up to 3% at 45 deg; beam-current drift 1%; multiple scattering up to 10% at the first minimum only; target thickness 1% (Fe54, Fe56, Ni58). "Probable error" of unaveraged absolute cross section +-6% to +-10% (Fe54, Fe56, Ni58). Energy 39.8 +- 0.2 MeV. A 1.9% correction for NaI nuclear interactions applied | abstract p1; p4 (counts); p7 (Sec. C Errors, journal p.531) | high (stat, text); medium for angle dependence | per-point 3% (statistical; about 4.2% if the 3% nonelastic term is added in quadrature, see note below), with the angle-dependent systematics recorded as a correlated component 6-10% (use as total uncertainty at maxima/minima: about 6% at maxima to 10% near steep slopes). Corpus 3.0/2.8% is consistent with the statistical value, but it came from the reader. |

Quotes:
- p1 abstract: "Absolute differential cross sections obtained with a statistical accuracy of ~3% have been determined for the elastically scattered ..."
- p7: "Nonelastic scattering contributions to the measured elastic cross sections also were a function of scattering angle. An over-all average estimate of such errors, however, is about 3%. The statistical accuracy of most points at which measurements were taken was also 3%."
- p7: "To summarize: The probable error for the experimental unaveraged absolute cross sections lies from +-6% to +-10% for Fe54, Fe56, Ni58, and from +-7% to +-11% for Ni60 and Cu65."
- p7: "given an error of +-0.15 deg for the angular position of the detector, a cross-section error contribution from zero (at maxima of the angular distributions) to about 7.5% (where the cross sections were changing most rapidly with angle) would be made." ; "Multiple scattering ... could have been as high as 10%" (first minimum); "Target thicknesses for Fe54, Fe56 and Ni58 were determined to 1%."
- p4: "the number of counts ... was such that the standard deviation was less than 3.3%. In most instances it was closer to 2.5%."

Note: statistical (3%) and nonelastic (3%) are separate components; the figure error bars combine them, so the typical drawn bar is probably about 4% (estimate, not stated). Recommendation: 3% if only the statistical term is wanted, 4.2% (quadrature) for the plotted bar.

---
## O0553 (Rolland et al., NP 80, 625) - 40Ca and 209Bi, 150 and 75 MeV; text in French

Subentries: 004 (40Ca 152 MeV, Fig. 4, p6), 006 (209Bi 153 MeV, Fig. 5, p7), 010 (40Ca 75 MeV, Fig. 7, p9), 014 (209Bi 78 MeV, Fig. 9, p11).

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0553004, 006 (152/153 MeV) | dsigma/dOmega | "Seules sont portees sur les courbes et dans le tableau 1, les erreurs statistiques." Not given numerically for Ca/Bi; no visible bars on the cross-section curves (smaller than symbols). Proxy: Table 1 (12C 150 MeV) statistical errors: about 3-4% at 10-16 deg, about 3-5% at 25-45 deg, about 5-6% at 55-65 deg, 11% at 73.6 deg | "une erreur systematique possible de 5%, la meme pour tous les corps a tous les angles"; H(p,p) reference 3.80 +- 0.11 mb/sr (2.9%) at 150 MeV, 51.1 deg c.m. | p4 text, Table 1 p3-4 | medium-low (proxy from 12C) | 4% per point; norm 5% (corpus uses 5%) |
| O0553010, 014 (75-78 MeV) | dsigma/dOmega | not numerically given. "La statistique etait moins bonne qu'a 150 MeV" (p10); relative measurement on the H reference 4%; no visible bars | "une incertitude systematique, identique pour toutes les cibles et a tous les angles, de +-10%" (reference H cross section 5.0 +- 0.3 mb/sr at 30 deg lab, 76 MeV; relative error on H 4%) | pp10-11 | low-medium | 5% per point; norm 10% (corpus 5% too small for 75/78 MeV) |

Quotes:
- p4: "En dehors des erreurs statistiques, une erreur systematique possible de 5%, la meme pour tous les corps a tous les angles, a ete admise. Seules sont portees sur les courbes et dans le tableau 1, les erreurs statistiques."
- p4: "(dsigma/dOmega) = 3.80 +- 0.11 mb.sr^-1" (H reference at 150 MeV).
- p10-11: "nous avons pris (dsigma/dOmega)c.m. = 5.0 +- 0.3 mb.sr^-1 par interpolation ... la mesure relative des sections efficaces de diffusion sur H est faite avec une erreur relative de 4%. Pour les valeurs des sections efficaces absolues, nous avons en plus de l'erreur statistique, une incertitude systematique, identique pour toutes les cibles et a tous les angles, de +-10%."
- p10: "La statistique etait moins bonne qu'a 150 MeV et nous avons du limiter nos mesures a des angles inferieurs a 40 deg" (the 75-MeV runs).
- Angular resolution +-1.5 deg at 75 MeV; 1 deg to 1.4 deg at 150 MeV.

Notes: Ay subentries 005/011 (ERR-T, author bars) are not in this group's brief. The 12C table values are a proxy only; heavier targets will have different statistics.

---
## O1103 (Moonen et al., J. Phys. G 19, 635) - Ge/Se isotopes, 22.3 MeV: 004 (72Ge), 006 (74Ge), 012 (78Se), 014 (80Se); Fig. 1 (Ge) and Fig. 2 (Se), p5

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O1103004, 006, 012, 014 | sigma/sigma_R (elastic) | not stated for elastic. Only: "The experiments were designed to obtain an accuracy of 3% (1000 counts) in the two-phonon levels" (inelastic design goal). Error bars in Figs. 1-2 are not visible beyond symbol size for most points | Normalisation is a free parameter ("During the search with the program OPTIMO the normalization of the experimental data was continuously adjusted"); no absolute error stated. Beam polarization 90% | p4 (experiment, optics), p5 (Figs 1-2) | low | 2% (inferred from sister papers O1104 "minimal error of 2%" and O1109 same group/setup); not an author statement for this paper. Corpus 1.6% reader value is probably slightly low. |

Quotes (p4):
- "The experiments were designed to obtain an accuracy of 3% (1000 counts) in the two-phonon levels. It was not possible, however, to achieve this in all instances."
- "Because of the presence of unwanted isotopes in per cent amounts in our targets we started the analysis of the elastic peaks by determining the values of the normalization and of the optical-model parameters as if the data contained no contributions from isotopic impurities. Then the experimental data were corrected ... until the normalization factors became stable."
- Optical-parameter inaccuracies (table 2 note): "Inaccuracies usually 4% for V, a, a; up to 10% for r, W, V; up to 20% for ..." (parameter errors, not data errors).
- Isotopic enrichments: >90% for 72Ge, 74Ge, 78Se, 80Se; about 85% for 70Ge, 76Se.

---
## O1104 (Petit et al., J. Phys. G 20, 1955) - Cd isotopes 106-116, 22.3 MeV

DA subentries 002, 004, 006 (Fig. 2), 008, 010, 012 (Fig. 3); Ay subentries 003, 005, 007 (Fig. 2), 009, 011, 013 (Fig. 3). Figures on p6 (Fig. 2) and the next page (Fig. 3).

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 002, 004, 006, 008, 010, 012 | sigma/sigma_R | "A minimal error of 2% was assumed in the values of cross section and analysing power, due to the normalization procedure." Also "statistics in our experiment are usually better than 2% in the individual points" | normalisation obtained by extrapolation to theta=0 of OM fits (free); authors find differences to Cereda of up to 35% (usually <20%) and say they cannot pinpoint the cause; a 0.1 deg angle error at 20 deg gives 2% in Rutherford | p3 (2% statement), p10 (comparison) | high | 2% relative |
| 003, 005, 007, 009, 011, 013 | Ay | same sentence applies to analysing power: "minimal error of 2% ... in the values of ... analysing power" (ambiguous whether relative to |Ay| or a floor). Figure 2: bars not visible beyond symbol size for most points | polarization about 90%, continuously monitored; no uncertainty quoted | p3 | medium (text, interpretation ambiguous) | absolute = max(0.02*|Ay|, 0.01); at least keep statistical bars as read from figure, so avoid 6e-3 reader value being treated as author error |

Quotes (p3, p10):
- "In the spin-up and spin-down spectra obtained, the peak intensities were integrated ... A minimal error of 2% was assumed in the values of cross section and analysing power, due to the normalization procedure."
- "While statistics in our experiment are usually better than 2% in the individual points, we notice some normalization differences (up to 35% but usually less than 20%) between our values and Cereda's. This normalization originates from the extrapolation to theta = 0 of the sigma/sigma_R curves in the elastic scattering experiments."
- "an adjustment error of the scattering angle of 0.1 degree at 20 deg would bring about an error of 2% in the Rutherford cross section due to the factor sin^4(theta/2)."
- Counting goal: "at least 500 counts ... in each of the assumed two-phonon states" (inelastic only). Target purity 96-98%; 106Cd 91%, 108Cd 64% pure.

---
## O1109 (Moonen et al., J. Phys. G 19, 1191) - Zn isotopes, 20.4 MeV: DA 002 (64Zn), 004 (66Zn), 006 (68Zn), 008 (70Zn); Ay 005 (66Zn); Fig. 2 on p5

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 002, 004, 006, 008 | sigma/sigma_R | not stated for the elastic data. Fig. 1 caption only: "Statistical uncertainties indicated at the right-hand side" (sample spectrum). Fig. 2 bars not visible beyond symbols | "After a suitable normalization to the forward-angle data points of the elastic scattering, the results of the two sets of experiments were in good agreement"; normalisation is a fit parameter; no absolute error | p3 (Sec. 2), p5 (Fig. 2) | low | 2% (inferred from the same-group O1104 "minimal error 2%"); 1.6/1.9% reader values are close but not author-sourced |
| 005 | Ay (66Zn) | not stated; Fig. 2 right panel: mostly symbol-sized bars, few larger | polarization beam 70-90% era, no number in this paper | p5 | low | absolute 0.02 floor (estimated), or 0.01 if only the statistical bars are wanted |

Quotes (p3): "After a suitable normalization to the forward-angle data points of the elastic scattering, the results of the two sets of experiments were in good agreement with one another." ; "Figure 1. Sample spectrum showing scattering from 66Zn. Statistical uncertainties indicated at the right-hand side." ; "enriched to over 96% in the relevant isotope, except for the rare isotope 70Zn where the corrections for isotopic impurities were appreciable."
Notes: two data sets with different setups (100 keV resolution early set, 35 keV later) were merged by normalising to forward-angle elastic data; no uncertainty for that merge is given.

---
## Cross-entry summary (recommended per-point uncertainty)

| entry | elastic (relative %) | Ay (absolute) | confidence | normalisation (author) |
|---|---|---|---|---|
| O0079 | none stated; assume about 5% | n/a | low | not stated |
| O0091 | 3% Fe, 2% Ni | about 0.02 (figure estimate) | high / low | free (relative only) |
| O0300 | 4% (stat 1-3% plus angle term); | n/a | high | 8% |
| O0456 | 3% (stat) or about 4% incl. nonelastic; systematic 6-10% | n/a | high / medium | probable error 6-10%, angle dependent |
| O0553 | 4% (152/153), 5% (75/78) | n/a | medium-low | 5% (150 MeV), 10% (75-78 MeV) |
| O1103 | 2% (inferred) | n/a | low | free parameter |
| O1104 | 2% | 2% of |Ay| with 0.01 floor | high / medium | free (extrapolation to 0 deg) |
| O1109 | 2% (inferred) | 0.02 (estimate) | low | free; forward-angle normalisation |
