# Author uncertainties, group G3 (O0254, O0259, O0272, O0370, O0384, O0387)

PDF page = page index in the PDF file (journal page in brackets). Figures were inspected visually. "Not stated" means absent from the text.
Overall: NONE of the six papers tabulates errors for the elastic dσ/dΩ subentries used by the corpus. Only O0384 and O0370 state error composition/normalisation in text; O0254 tabulates errors only for polarization (Ay), which are not the corpus subentries.

---
## O0254 Baugh et al., NP 65, 33 (17.8 MeV polarization paper)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0254009 (Si-28) | dσ/dΩ, RELATIVE shape | not stated; "same order of statistical accuracy as the polarization values"; no error bars in Fig. 2 (open circles only) | arbitrary: relative cross sections, "require a normalization procedure"; no absolute value | text PDF p4 [p36]; Fig. 2 PDF p7 [p39] | low | Polarization stat errors are ~1-4 points of asymmetry (Si: ±1.0 to ±4.0), implying counting stat of a few %. Use ~3-5% per point as inferred; mark as low. Data are relative only, so the normalisation must be a free fit parameter (corpus norm 0.05 has no author basis). |
| O0254010 (Ca-40) | dσ/dΩ, RELATIVE shape | same as above | same as above | same | low | Same: ~3-5% inferred (low); relative normalisation free. |
| (O0254003/004, not in brief) | Ay Si-28, Ca-40 | tabulated, Table 1 (absolute, in % polarization units) | beam polarization taken as 1.00 | Table 1 PDF p5 [p37] | high | Si-28: ±0.010 to ±0.040 (i.e. 1.0-4.0 %); Ca-40: ±0.013 to ±0.040 (≈1.3-3.5 %) in Ay units, angle-dependent; read Table 1 per point. |

Quotes
- PDF p4 [p36]: "For Si, Ca and Mo relative differential cross sections were obtained by adding the left and right polarization counts recorded for a given monitored beam. The results have only the same order of statistical accuracy as the polarization values and require a normalization procedure to be adopted in the optical model fitting."
- p4: "the uncertainties involved in resolving these [inelastic groups] from the elastic groups have been included in the quoted errors."
- Fig. 2 caption (p7): "Differential cross sections for the scattering of 17.8 MeV protons. The crosses represent data of ref. 2)." No error bars drawn for Si/Ca/Mo circles.
- Beam polarization: "a value 1.0 for the polarization of the incident protons"; check: C at 45 deg "-0.47±0.01"; Au 23 deg "0.01±0.01" (p3-4).
- Other details: angular setting accuracy 0.1 deg, acceptance ±1.5 deg; beam energy 18.2±0.2 MeV on target, resolution 0.8 MeV FWHM.
Note: the corpus uses these data as absolute (norm 0.05); the paper provides no absolute scale. Ca-40 here has an overall energy spread ±300 keV.

---
## O0259 McDaniels et al., PRC 33, 1943 (Pb-208, 200 MeV)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0259002 (Pb-208) | elastic dσ/dΩ (Fig. 3) | not stated; Fig. 3 shows solid circles (data of Ref. 25, precise TRIUMF values) and crosses (Orsay) with NO visible error bars (log scale, 10^1-10^5 mb/sr) | check of absolute scale: p-p on CH2 "within ±6%" of standard; Pb elastic vs TRIUMF values "within ±7%"; no formal total stated | text PDF p3 [p1945]; Fig. 3 | low | Per-point: not stated; symbols obscure bars, so statistical error is small (inferred ≲3%); keep reader ~2.6-3% as a placeholder at low confidence. Normalisation: use 7% (author's agreement figure) rather than 5%. |

Quotes (PDF p3 [p1945])
- "On the average our measured p-p cross sections were within ±6% of the standard values obtained from the phase-shift calculations. In addition, the values of the 208Pb elastic-scattering cross sections measured in this experiment were compared with the precise TRIUMF values at 200 MeV; agreement to within ±7% was obtained."
- Fig. 3 caption: "Elastic scattering data used to obtain our optical model parameters. The solid circles are points from Ref. 25." Text: "The forward angle elastic scattering data used to determine our optical model parameters are shown in Fig. 3." (p4 [p1946]).
- Ay (not in brief, for reference), p4 [p1946]: "Beam polarization ... varied from 0.72 to 0.75 ... The uncertainty of an individual determination was ±0.005, whereas the larger variation between runs was due to changing ion source conditions." Fig. 3 inset shows analyzing power without error bars.
Note: the Fig. 3 solid circles are attributed to Ref. 25 (TRIUMF; Miller et al.-type data), so the EXFOR points may be the earlier TRIUMF data rather than new measurements. Forward angles only (5-25 deg lab). Absolute cross sections: from "integrated beam current, target thickness, and spectrograph acceptance solid angle".

---
## O0272 Lee et al., PLB 205, 219 (Pb-208, 200 MeV; also Ca, Zr)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0272002 (Pb-208, 200 MeV) | dσ/dΩ vs q (Fig. 1) | not stated anywhere; Fig. 1 spans 14 decades (10^8 to 10^-12 mb/sr) with symbols and no visible error bars | not stated | Fig. 1 PDF p3 [p221]; text p2-3 | low | Cannot be determined from this paper. Text refers to "More detailed descriptions of the experiments ... elsewhere [5,6]" (Drake, Bad Honnef 1985; Miller et al. PLB 169, 166 (1986)). Keep 7% reader value only as a placeholder (low); better to take errors from those references. |

Quotes
- PDF p2 [p220]: "More detailed descriptions of the experiments are presented elsewhere [5,6]." (the Pb-200 data are from Ref. 5, "older and remeasured" data summarised on PDF p1 [p219]: "we summarize some of the older and remeasured cross section and analyzing power data; for 208Pb at 200 MeV [5]").
- Beam polarization "typically 75%" (p2). Resolution 120-230 keV.
Notes: No error statement at all. Fig. 2 (Ay) also has no visible error bars; Ay absolute error not stated.

---
## O0370 Gray et al., PR 142, 735 (Zr-90(p,p'), 18.8 MeV)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0370002 (Zr-90, 18.8 MeV) | elastic dσ/dσ_R (ratio to Rutherford), Fig. 3 | statistical error + background uncertainty; no numbers given; no error bars visible in Fig. 3 (bars hidden within symbols) | "estimated error on the absolute normalization" about 5%; target thickness 2.39±0.05 mg/cm2 (2.1%); angle ±1 deg | text PDF p3 [p736]; PDF p5 [p739] | medium (norm), low (per-point) | Per-point: not stated (stat only, small, bars within points; inferred ~2%). The chi2 analysis used a uniform 10% weight (not an author error estimate). Use per-point ~2% (low) with an overall normalisation of 5% (medium); the reader's 1.7-2.0% is consistent. |

Quotes
- PDF p3 [p736]: "metallic foil 2.39±0.05 mg/cm2 thick ... The thickness was determined in two ways: by direct weighing and by measuring the energy loss for 5.477-MeV alpha particles ... The thickness from these methods agreed within the above-stated error."
- p3: "allowed determination of target and detector angle to within ±1°." Dead time "always held to less than 5%".
- p3: "Error bars on the data are the statistical error and background uncertainty, in the case of single peaks, but include an additional error estimate if the peak was a member of a partially resolved doublet or multiplet." (generic statement for the data figures)
- PDF p4 [p738]-p5 [p739]: "the optical-model fits to the present data would be improved if the data were increased uniformly by about 10%, although this is roughly twice the estimated error on the absolute normalization."  => normalisation error ~5%.
- p4: "chi2 was calculated with Δσ_EX/σ_EX=10% for all N=38 angles" (a weighting choice).
Notes: The 18.8 MeV elastic distribution is plotted as dσ/dσ_R on a log scale (Fig. 3, three panels, data repeated with sets of fits; the lowest panel multiplies data by 1.1). Angular range about 20-160 deg c.m.

---
## O0384 Gray et al., NP 67, 542 (Ar-40 and Ca-40 (p,p'), 14.6 and 17.3 MeV Ca-40)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0384002 (Ca-40, 14.6 MeV) | elastic dσ/dΩ, Fig. 4 | not stated for elastic; Fig. 4 circles show no error bars; general statement: error bars are relative (statistics + background), "When no error bars are shown, the estimated relative error is less than the radius of the circles." (that sentence is for the inelastic Figs. 8-9) | ±15% overall (10% scale factor + target thickness, geometry, current) | normalisation text PDF p5 [p545-546]; Fig. 4 PDF p9 [p550] | high (norm), low (per-point) | Per-point: not stated; inferred ≲5% (symbol radius). Keep 5% (low). Systematic normalisation: 15%, not 5%. Note the authors found fit "rather poor" and possible compound elastic scattering near the (p,n) threshold (14.68 MeV). |
| O0384003 (Ca-40, 17.3 MeV) | elastic dσ/dΩ, Fig. 5 | same | ±15% overall | same; Fig. 5 PDF p9 [p550] | high (norm), low (per-point) | same: 5% per point (low), 15% normalisation. |

Quotes
- PDF p5 [p545-546]: "As the normalization of the original Ca40 data at both 14.6 and 17.3 MeV was very questionable owing to large uncertainties in the target thicknesses, the elastic cross section at both energies was rechecked experimentally with a new evaporated target ... a relative scale factor could be established such that the two sets of data overlapped within 10% at all points. The final normalization was therefore taken from the new data, with an error of 10% assigned due to the uncertainty in ascertaining the correct scale factor. The overall uncertainty in the normalization of the Ca40 cross sections is estimated at ±15% when other factors such as the uncertainties in target thickness, geometry and integrated incident flux are taken into account."
- Ar-40 cross sections (not used): "estimated to be accurate to ±5%".
- Angle resolution: detector aperture 3.2 mm at 17.7 cm, "typical overall angular resolution of from 1.5-3 deg"; beam energy accurate to ±100 keV, "could lead to 1-2% discrepancies in the optical fits to the elastic scattering at forward angles".
- Inelastic Figs 8-9 (PDF p11): "The error bars represent relative errors only and are based on statistical errors plus an uncertainty in estimating background."
Note: the Ca-40 targets suffered O and C contamination (corrected by subtraction); at 14.6 MeV the foil was "wrinkled" and 5.8 mg/cm2 thick, which suggests the 14.6 MeV data are less reliable than the 17.3 MeV data.

---
## O0387 Tellez et al., NPA 127, 438 (Ca-40, Ca-48 (p,p'gamma), 12 MeV)
| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| O0387002 (Ca-48, 12 MeV; Saclay circles + Argonne crosses in Fig. 3) | elastic dσ/dΩ (mb/sr) | not stated; Fig. 3 plots circles/crosses without error bars | absolute scale NOT measured: set by matching a forward-angle point to the Argonne curve (Marinov et al., Ref. 6); no uncertainty quoted | text and Fig. 3 PDF p4 [p441] | low | Per-point: not stated. Inferred from point scatter, ~3-5% (low). Normalisation inherited from Ref. 6 (uncertainty not quoted here); the corpus 5% is an assumption; consider 10% (low). The reader value of 1.6% looks too small. |

Quote (PDF p4 [p441]): "The absolute magnitude of the elastic differential cross section was obtained by comparison with a forward angle point of the curve of ref. 6). The normalization factor thus determined was applied to the inelastic groups."
Notes: Fig. 3 mixes Saclay (this work, circles) and Argonne (crosses); the 22 EXFOR points may include both. Targets: 48Ca 0.4 mg/cm2 (≈3% 40Ca contamination) on 30 ug/cm2 C; resolution 25-30 keV in the angular distribution. Ca-40 elastic not analysed (resonances).
