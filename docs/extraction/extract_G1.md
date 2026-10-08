# Author-uncertainty extraction, group G1 (O0178, O0328, O0211, O0382, O0552, O0580)

PDF page = page index in the PDF file. Journal page in brackets. Error bars estimated from figures are labelled "estimate".

---------------------------------------------------------------------
## O0178  Doering, Patterson, Galonsky, PRC 12, 378 (1975) + MSU thesis (Doering 1974)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 006/009/012/015 (45 MeV), 007/010/013/016 (35 MeV), 017 (208Pb 25 MeV) | (p,n) IAS dsigma/dOmega | Fig. 3 error bars = peak-fit statistics (+) independent +-2% (beam charge x target thickness). Exact per-point values are in thesis Table 5 (1.5% to >100%, see below). Paper: tabulations "available upon request". | 10% (neutron detection efficiency) + <5% (target thickness, beam integration, neutron attenuation) | paper PDF p.5 [382], p.6 [383] ; thesis Table 5 PDF pp.124-129 | high for 25 and 35 MeV and 45 MeV points whose angles match Table 5 | Where a thesis Table 5 point matches (same angle), use the Table 5 % error. For reader-only points, interpolate with the same set (see summary of ranges). Do NOT use flat 7%. Norm 11% (10% (+) 5%). |
| 008 (48Ca 25 MeV), 011 (90Zr 25), 014 (120Sn 25) | same | Thesis Table 5 errors, transcribed below (all 32 rows each): 48Ca 1.9-10.1% (median 3.8%, mean 4.2%); 90Zr 3.2-7.5% (median 5.2%); 120Sn 1.9-12.2% (median 7.2%) | as above | thesis Table 5, PDF p.124 (thesis p.95), p.126 (p.96), p.128 (p.97) | high (tabulated) | Use the tabulated per-point errors, interpolated onto EXFOR angles. |

### Paper statements (verbatim)
- p.6 [383] (PDF): "The error bars displayed on the data in Fig. 3 represent relative errors within each angular distribution which result from statistical uncertainties in the peak fitting combined independently with +-2% fluctuations in the product of beam charge and target thickness. Since the IAS peak area is a search parameter, its variance is the corresponding diagonal element of an error matrix obtained from inverting the curvature matrix determined by the fitting algorithm."
- p.6: "The errors in the absolute magnitudes of the cross sections due to uncertainties in the neutron detection efficiency calculations are estimated to be about 10%. There are also small uncertainties in target thickness, beam current integration, and neutron attenuation along the flight path, which introduce systematic errors estimated to be less than 5%. ANNIE has been used to evaluate the additional systematic errors arising from uncertainties in the IAS intrinsic widths."  (IAS widths used: 20+-10, 30+-5, 231+-6 keV for Zr, Sn, Pb analogs.)
- p.5 [382]: "errors in the efficiency calculations do not diminish the relative accuracy within each angular distribution."
- p.6: "Tabulations of the differential cross sections and their relative errors are available upon request."
- Total cross-section errors (Table I) combine statistical and systematic errors independently.
- EXFOR ERR-ANALYS matches (10% efficiency, 5% for thickness, current, attenuation). Note the EXFOR COMMON lists 10%, 5%, 5%, 5%; the paper says the three small ones together are "less than 5%", so EXFOR's quadrature sum is overstated (paper: 10% (+) <5%, about 11%).

### Thesis statements (PDF p.123 = thesis p.94 and PDF p.130 = thesis p.99)
- "The dominant source of relative errors in the angular distributions is the neutron yield. The errors given in Table 5 result from combining in quadrature statistical and systematic uncertainties in the peak fitting." (systematic part = IAS-width uncertainty.)
- "The principal error in the absolute magnitude of the cross sections is the estimated +-10% reliability of the neutron detection efficiency calculations ... small uncertainties in target thickness, beam current integration, and neutron attenuation along the flight path, which may introduce additional systematic errors estimated to be less than 5%."
- Table 6 total cross sections (mb), 25/35/45 MeV: 48Ca 10.6+-1.2 / 10.2+-1.1 / 8.4+-1.0; 90Zr 6.7+-0.8 / 4.8+-0.5 / 4.4+-0.5; 120Sn 8.5+-1.0 / 5.6+-0.6 / 5.8+-0.7; 208Pb 9.2+-1.0 / 6.7+-0.8 / 5.3+-0.6.
- Note the thesis table error does not explicitly include the +-2% charge x thickness term (paper does); differences are tiny relative to the quoted errors.
- Fig. 3 of the paper (PDF p.5): bars are mostly inside the symbols at forward angles for 25 and 35 MeV, and are large (up to full-scale) at backward angles for 45 MeV (Pb, Sn, Ca). Consistent with Table 5.

### Thesis Table 5, 25 MeV sets, c.m. angle (deg), cross section (mb/sr), error (%)
(Table is printed rotated 90 degrees in the thesis; transcribed from a rendered image; format ".277E 01" = 2.77. First row angle is printed as ".0", read as 0.0.)

**48Ca(p,n)48Sc IAS, 25 MeV** (PDF p.124, thesis p.95; 32 rows. EXFOR O0178008 has 36 points, so 4 EXFOR points are not in Table 5.)
0.0 2.77 2.9 | 10.3 2.32 1.9 | 15.4 1.96 3.4 | 20.5 1.75 3.1 | 25.6 1.75 3.8 | 30.7 1.62 2.4 | 35.8 1.43 4.1 | 40.9 1.27 2.8 | 46.0 1.18 3.6 | 51.1 1.27 2.9 | 56.2 1.32 2.9 | 61.3 1.25 2.7 | 66.3 1.18 3.1 | 71.4 1.09 2.8 | 76.4 1.05 3.4 | 81.4 0.906 3.3 | 86.5 0.796 4.1 | 91.5 0.586 4.4 | 96.5 0.416 5.5 | 101.4 0.446 5.6 | 106.4 0.463 5.2 | 111.4 0.566 4.3 | 116.3 0.624 4.8 | 121.3 0.494 4.8 | 126.2 0.357 5.9 | 131.1 0.210 8.2 | 136.0 0.130 10.1 | 140.9 0.236 7.1 | 145.8 0.380 4.6 | 150.7 0.517 3.8 | 155.6 0.636 3.3 | 160.5 0.536 4.0

**90Zr(p,n)90Nb IAS, 25 MeV** (PDF p.126, thesis p.96; 32 rows, EXFOR O0178011 has 32)
0.0 6.02 3.2 | 10.2 4.12 3.5 | 15.2 2.91 3.7 | 20.3 1.74 4.1 | 25.4 1.09 4.8 | 30.5 0.895 5.2 | 35.5 0.947 4.9 | 40.6 0.884 5.1 | 45.6 0.801 5.3 | 50.7 0.715 5.5 | 55.7 0.554 5.1 | 60.8 0.480 5.3 | 65.8 0.429 5.6 | 70.9 0.431 5.4 | 75.9 0.424 5.3 | 80.9 0.373 5.8 | 85.9 0.353 6.0 | 90.9 0.363 5.6 | 95.9 0.365 4.6 | 100.9 0.350 4.6 | 105.9 0.314 4.8 | 110.9 0.225 5.4 | 115.8 0.177 6.1 | 120.8 0.200 5.8 | 125.7 0.269 4.9 | 130.7 0.329 4.5 | 135.6 0.275 4.8 | 140.6 0.200 5.7 | 145.5 0.122 7.5 | 150.5 0.173 6.0 | 155.4 0.365 4.4 | 160.3 0.579 3.8

**120Sn(p,n)120Sb IAS, 25 MeV** (PDF p.128, thesis p.97; 32 rows, EXFOR O0178014 has 32)
0.0 6.65 1.9 | 10.1 4.32 2.4 | 15.2 3.30 3.1 | 20.2 2.35 3.5 | 25.3 2.51 3.5 | 30.4 2.54 3.3 | 35.4 2.48 3.3 | 40.5 2.10 3.6 | 45.5 1.47 4.5 | 50.6 0.844 6.4 | 55.6 0.512 9.0 | 60.6 0.441 10.0 | 65.7 0.492 8.4 | 70.7 0.542 8.2 | 75.7 0.589 6.8 | 80.7 0.532 8.0 | 85.7 0.385 9.1 | 90.7 0.223 10.4 | 95.7 0.168 8.7 | 100.7 0.224 7.1 | 105.7 0.264 6.7 | 110.7 0.243 6.6 | 115.7 0.193 7.3 | 120.6 0.164 9.8 | 125.6 0.148 12.2 | 130.6 0.148 8.6 | 135.5 0.193 8.5 | 140.5 0.152 9.3 | 145.4 0.139 11.2 | 150.4 0.107 10.9 | 155.3 0.227 7.1 | 160.2 0.302 5.8

(Digit misreads of 1 in the last digit are possible in a few rows because the table is a low-quality dot-matrix print; the errors are +-0.1 at worst. The reader should verify against the PDF if a value is critical.)

### 208Pb 45 MeV points near 162 and 164 deg
Table 5 for 208Pb 45 MeV (PDF p.129, thesis p.98) ends at 160.1 deg. The last rows are: 145.2 0.391E-01 25.7% | 150.2 0.468E-01 22.4% | 155.2 0.380E-02 117.8% | 160.1 0.165E-01 65.4%. There are NO points at about 162 and 164 deg and no cross sections of 0.049 or 0.072 mb/sr near there. The EXFOR 0.049 / 0.072 mb/sr values cannot be matched with Table 5 (compare 0.0468 at 150.2 only by coincidence in magnitude). Verdict: not in Table 5; errors not available from the thesis. Those two EXFOR points are most likely digitisation of Fig. 3 (the backward points of 208Pb 45 MeV have bars of order 65-120%). Recommendation: assign a large error, 65% (error of the 160.1 point) or drop them (low confidence).
(Also: Pb 45 MeV Table 5 has 32 rows, EXFOR O0178015 has 35 points.)

### Recommendation summary
Per-point rel. error: use Table 5 values (tabulated; high). For the 25, 35, 45 MeV sets of 48Ca, 90Zr, 120Sn, 208Pb the full Table 5 is available in the thesis (PDF pp.124, 126, 128, 129) and can be used for all of the O0178 subentries, replacing the flat 7% reader value. Overall scale error 10% (efficiency) with an extra <5%: use 11%.

---------------------------------------------------------------------
## O0328  Fricke, Gross, Morton, Zucker, Phys. Rev. 156, 1207 (1967)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 004 (59Co), 005 (68Zn), 007 (120Sn) | dsigma/dOmega, 40 MeV | "Error bars ... relative probable errors which include statistical errors and the uncertainty in background subtraction"; "Typical statistical error bars are shown." No numbers in text. Fig. 2: bars mostly within the symbol (<~3%), larger (about 10-20%) at the backward angles (estimate). Tables deposited with ADI (not in PDF). | +-5% target thickness ("absolute error of +-5% due to the uncertainty in determining the target thickness") | PDF p.5 [1211] text; Fig. 2 PDF p.3 [1209] | medium-low (estimate from figure) | 3% at angles < 120 deg, 6% for 120-180 deg (estimate), norm 5%. Do not use 0.4%. |
| 009 (59Co), 010 (68Zn), 011 (120Sn) | Ay (polarization), 40 MeV | Same bar definition. Fractional error of asymmetry from L and R counts. Fig. 3 (PDF p.4, [1210]), 120Sn panel (estimate): most bars at or below the symbol size, i.e. <= 0.02-0.03 absolute; a few larger points reach +-0.1 to +-0.2 (large angles, near minima). | beam polarization P_B = (27.4+-0.5)%, i.e. 1.8% relative scale error on all Ay (including P_C uncertainty) | PDF p.4 [1210], p.5 [1211] | medium-low | Absolute 0.03 for most points; 0.1 for angles above about 120 deg (estimate); scale 1.8%. Do not use the "-1.7, -0.5, 0.2 ..." relative values. |

### Verbatim quotes
- p.5 [1211]: "The error bars in Figs. 2 and 3 are relative probable errors which include statistical errors and the uncertainty in background subtraction. The fractional error in the asymmetry delta e/e is calculated from delta L and delta R, the errors in L and R, from the relation ..."
- p.5: "Relative errors in the differential-cross-section measurement are chiefly statistical. In addition there is an absolute error of +-5% due to the uncertainty in determining the target thickness. Corrections were made for the loss of counts from the elastic peak caused by reactions in the crystal. Multiple-scattering corrections were unnecessary."
- p.5 footnote: "Copies of the tables may be obtained at $2.00 per microfilm copy ..." from the American Documentation Institute (tables not in the PDF).
- p.4 [1210]: "Our result is that the polarization of the 40-MeV beam is (27.4+-0.5)%, including the uncertainty in P_C."  Also "Again the measurement of the target thickness introduced the most serious errors into the absolute normalization of the differential cross section."
- Figure captions (PDF p.3, p.4): "Typical statistical error bars are shown."
- Confirmation of the ERR-1 question: EXFOR's ERR-1 text, "Statistical errors and the uncertainty in background subtraction", matches the paper's error-bar definition (p.5) word for word, so ERR-1 is the authors' per-point (relative probable) error as shown in Figs. 2 and 3. Since the data were digitised from figures, ERR-1 can only be an error bar read from the figure (the paper gives no numeric tables, they are deposited with ADI), so even ERR-1 carries digitisation resolution. For Ay the bars are in absolute polarization units.
- EXFOR ERR-2 "2% uncertainty in current integration" is NOT in the paper text (searched: no "current integration" statement); the paper gives only +-5% target thickness. Treat ERR-2 as not confirmed.
- The 120Sn 40 MeV data (cross section and Ay) are new in this paper (Fig. 2 and 3 text says only C, Ca, Ni, Zr, Pb are reproduced from Ref. 1); there is no separate error statement for 120Sn.
- Energy: EXFOR EN-ERR 0.4 MeV; not checked in this paper.

---------------------------------------------------------------------
## O0211  Fulmer, Ball, Scott, Whiten, Phys. Rev. 181, 1565 (1969)

The paper TABULATES cross sections and errors in the Appendix (Tables V-XII, PDF pp.12-15, journal pp.1576-1579) for all targets. Column header "+-%". Errors are given as integers (%). EXFOR subentries O0211012, 015, 016, 017 contain these table values with the author errors (STATUS TABLE); O0211004/007/008/009 are separate figure digitisations of the same data, the reader-only ones. Use the tables.

| subentry | target | per-point error (author, tabulated "+-%") | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 004 (= table VII) | 40Ca | 5% for 31.8-93.4 deg; 10% at 29.7, 99.4-107.4; 8% at 95.4 (36 rows, 29.7-107.4 deg) | 10% (thickness + beam monitoring); 40Ca normalized to optical-model fit (not independent) ; 5% target thickness, 10% charge | PDF p.13 [1577] Table VII | high | tabulated +-% per point |
| 007 (= table X) | 90Zr | 5% to 10% (20.2-40.4 deg mostly 5), mostly 10% 42-76 deg, 11-17% at 82-112.6 deg | as above | PDF p.14 [1578] Table X | high | tabulated +-% per point |
| 008 (= table XI) | 116Sn (OCR "116Sn") | 5% (20-34 deg), 10% (36-86 deg), 13-30% at 88.5-112.5 deg | as above | PDF p.15 [1579] Table XI | high | tabulated +-% per point |
| 009 (= table XII) | 208Pb | 5% (20-40 deg), 7-8% (42-70 deg), 10-15% at 60-98 deg, 12-25% at 100-112 deg | as above | PDF p.15 [1579] Table XII | high | tabulated +-% per point |

Other tables (VI 27Al, VIII 58Ni, IX 68Zn) similar: 5% forward, 8-10% at the minima, 11-20% at the largest angles. 58Ni: 5-10% to 90 deg, 10-19% 87-113 deg.

### Verbatim quotes
- p.3 [1566-1567]: "Errors shown with the data include both the statistical error of the counts and an estimate of the uncertainty in determining the tail of the Gaussian elastic peak. The latter is significant where a contaminant peak or an inelastic peak is strongly excited. The uncertainty in the absolute value of the cross sections due to the determination of the effective target thickness is of order 5%, and the uncertainty in the charge collection measurements is about 10%."
- Appendix (p.12, [1576]): "The errors shown are based on counting statistics and uncertainties in the subtraction of contaminant or inelastic peaks. Target thickness and beam monitoring uncertainties could contribute as much as 10% error to the absolute cross sections. The normalization of the 40Ca cross sections is based on fixed-geometry optical-model calculations, as described in Sec. III."
- Fig. 3 caption: "Typical statistical errors are shown for a few large-angle data points. At angles smaller than about 50 deg the statistical errors are smaller than the plotted points." (so the digitised reader values of 1.7% reflect the figure, not the authors).
- Table header example (Table VII, PDF p.13): columns theta_c.m. (deg), sigma(theta) (mb/sr), +-%.
- Details of the exact assignment of table rows to angles should be done from the tables directly; the EXFOR 012-017 subentries should carry them. Note the corpus entries for 004/007/008/009 and 012/015/016/017 appear to refer to the same data (duplicate); prefer the tabulated ones.

---------------------------------------------------------------------
## O0382  Yagi et al., Phys. Lett. 10, 186 (1964)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 002 | 40Ca(p,p) elastic, 55 MeV, Fig. 2 | NOT STATED in text. Figure 2 shows small cross symbols with no resolvable error bars on a log axis; they are not larger than the symbols (estimate: <~5%). Numerical cross sections "published in the INS-Journal" (not in the PDF). | "Errors in absolute values of the cross sections are estimated to be +-15%" | PDF p.2 [187], text before Fig. 2 and Fig. 2 | low (inferred) | Per-point 5% (estimate; symbol size on a log plot), norm 15%. The 6% reader value is of the same order; 15% is the stated scale error. |

Verbatim (p.2): "Errors in absolute values of the cross sections are estimated to be +-15%." Also: "total experimental energy resolution was 0.9% FWHM"; "* Numerical differential cross sections are published in the INS-Journal." Other statements (about +-10% uncertainty in beta_l values; spectrometer rho = 114 cm +-10%) do not bear on the points. Statistical errors: not stated.

---------------------------------------------------------------------
## O0552  Rathmell & Haeberli, Nucl. Phys. A178, 458 (1972)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 008 | 208Pb(p,p) 12.98 MeV, sigma/sigma_R (Fig. 2) | "The total uncertainty in the relative cross-section measurements ranges from 0.5% to 3%." Contributions: statistics, detector-angle uncertainty, unresolved contaminants, inelastic subtraction (50% of inelastic cross section added), integration limits (+-0.3%), +-0.5% Pb subtraction at 30 deg. Bars on Fig. 2 are within the plotted symbols (not resolvable). | about 1% absolute (solid angle ratio +-0.3%, slit area +-1%, monitor); 13.8 MeV normalization unknown, but not 12.98 MeV | PDF p.3 [461] section 4; Fig. 2 PDF p.6 [463] | high for the 0.5-3% range; the angle dependence is not stated | 1.5% constant (middle of the stated 0.5-3% range); use 3% at the largest angle/uncertain points; norm 1%. |
| 009 (Ay, already author-only) | Ay | "The uncertainties in the polarization range from 0.002 to 0.01." | beam-monitor false-asymmetry about 0.002 | PDF p.3 [461] | high | 0.002-0.01 absolute |

Verbatim (p.3 [461]): "The total uncertainty in the relative cross-section measurements ranges from 0.5% to 3%. The uncertainty in the relative solid angles and in the cross section at the monitor detectors at 13 deg (sect. 2) and effects of slit edge scattering give rise to an estimated uncertainty in the absolute normalization of the cross section of about 1%." Also "The uncertainties in the polarization range from 0.002 to 0.01." and "(sect. 3) was included in the error bars." Also "A table of the results can be obtained from the authors."
EXFOR ERR-ANALYS in the entry has a typo: "ranges from 0.5% To 0.3%" and "0.002 to 0.001"; the paper says 0.5% to 3% and 0.002 to 0.01.
For the corpus values "0.6, 0.7, 0.8 %..." (already within the 0.5-3% range): acceptable, but the corpus errors for reader-only points should be at least 0.5%, preferably ~1.5% (the angular dependence is not given).

---------------------------------------------------------------------
## O0580  Fretwurst et al., Nucl. Phys. A468, 247 (1987)

| subentry | observable | per-point error (author) | normalisation | source | confidence | recommendation |
|---|---|---|---|---|---|---|
| 002 | 94Mo(p,p) 25.6 MeV, sigma/sigma_R, Fig. 2 | "Error bars given to single points in the angular distributions result from the peak-integrating procedure and are related to statistics." No numbers. In Fig. 2 the bars are mostly smaller than the plotted symbols (a few visible bars, a larger one near 160 deg); on a log scale symbol size equals approx 4-5% (estimate). "point-to-point fluctuations of the cross sections may occur, exceeding these statistical errors", especially at small cross sections. | Absolute integrated elastic cross sections "fixed to about +-1%" by normalising to the optical-model fit at forward angles (theta < 30 deg); target thickness the main uncertainty | PDF p.4 [250] section 2; Fig. 2 PDF p.13 [259]; sect. 4.1 | low-medium (estimate) | 5% per point (estimate from symbol size, plus allowance for point-to-point fluctuation beyond statistics), norm 1% (note: it was fitted to OMP in the forward region, so normalisation is model dependent). The corpus's 0.1% is the digitisation resolution, not the data error. |

Verbatim (p.4): "One of the main contributions to the inaccuracy of the absolute cross sections is given by the uncertainty in our knowledge of the actual target thickness. However, ... this difficulty could be overcome by extracting a target thickness normalization factor from the optical model fit of the elastic scattering in the very forward region. This way the absolute integrated cross sections for the elastic scattering were fixed to about +-1%. Error bars given to single points in the angular distributions result from the peak-integrating procedure and are related to statistics (see ref. 33). Due to small target contaminations, which could not explicitly be accounted for, as well as due to uncertainties in the background determination, point-to-point fluctuations of the cross sections may occur, exceeding these statistical errors."
EXFOR's ERR-S ("graphic bars ... related to statistics") matches this.
