# G4 extraction of authors' uncertainties

PDF page numbers are PDF pages (not printed). Unless stated, quotes are verbatim from pdftotext (OCR noise kept minimal). Figures were inspected visually.

## O0458 Beuzit et al., NPA 128, 594 (1969) (Ni-62, Ni-64 at 12 MeV)

| subentry | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| O0458004 (Ni-64 elastic, 12 MeV) | dσ/dΩ | not stated. Fig. 3 symbols have tiny horizontal/vertical bars of roughly symbol size (estimate only) | cross sections normalised to Lee & Schiffer (ref 12) data; no uncertainty quoted | p4 (Sect. 3.2); Fig. 3 on p7 | low | Keep ~3% relative (cannot beat reader value); treat normalisation as not stated, i.e. inherited from Lee-Schiffer (ref 12), which is not in this paper. |

Quote (p4, 3.2): "They agree well with those measured by Lee and Schiffer [ref. 12)], hence the absolute values of the cross sections were obtained by normalizing our experimental points to the values of ref. 22)."
Notes: no statistical or systematic error statement anywhere in the paper (searched for error/uncertaint/accura/statistic: only the normalisation sentence). Fig. 3 caption: "Angular distributions of elastically scattered protons (12 MeV) on 62Ni and 64Ni for Argonne and Saclay measurements..." (two datasets, Argonne and Saclay, shown with different symbols). Since the absolute scale is borrowed, the normalisation uncertainty is that of Lee & Schiffer (not extracted here).

## O0471 Burger & Heymann, NPA 243, 461 (1975) (Mo-92, Mo-94, p at 12.52 MeV)

| subentry | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| O0471007 (Mo-92, 12.52 MeV) | dσ/dΩ (ratio to Rutherford) | "relative errors ... not more than 6 % for each isotope"; Fig. 3 shows no visible bars (open circles only; bars smaller than symbols, circle diameter ~ 3-5% of ratio, estimate) | overall abs. norm from normalising to optical model at forward angles; "upper limit for the total error ... +-20 %" | p4 text; Fig. 3 on p8 | medium | 6% relative per point (upper limit stated by authors); high confidence this is the authors' stated bound, medium as a typical value. |
| O0471008 (Mo-94, 12.52 MeV) | same | same | same | same | medium | 6% |

Quotes (p4): "The over-all absolute normalization depends on accuracy in beam integration (1 %), solid angle determination (1 %), and target thickness measurement (12 %). Measurements with an a-particle thickness gauge indicated variations of up to 12 % in foil thickness. Absolute normalization factors were therefore determined by normalizing the elastic cross sections to the optical model predictions at those forward angles..." "The relative errors in the determination of the elastic scattering cross sections were estimated to be not more than 6 % for each isotope. The upper limit for the total error in the final elastic scattering cross sections was set at +-20 %."
Notes: the normalisation to the optical model means the absolute scale is model-dependent (effective norm uncertainty is not 20% for fits; 20% is the quoted upper limit). Inelastic errors (20-50%) not relevant. Angle precision "better than 0.1 deg". Energy error 0.02 MeV is EXFOR's.

## O0545 Stautberg & Kraushaar, PR 151, 969 (1966) (Zr-92, Zr-94, 19.4 MeV)

| subentry | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| O0545002 (Zr-92) | dσ/dΩ | statistical error "less than 1% for angles less than 90 deg and less than 3% for angles greater than 90 deg"; no error bars shown for elastic | "uncertain by 5%" | p4, Sect. II; Fig. 3 | high (text) | angle-dependent: 1% for theta < 90 deg, 3% for theta > 90 deg (lab angle per text); optional floor of 1% |
| O0545006 (Zr-94) | dσ/dΩ | same | same | same | high | same |

Quotes (p4): "Error bars are not shown for the elastic distributions, but the statistical error is less than 1% for angles less than 90' and less than 3% for angles greater than 90'. The absolute normalization of the elastic and inelastic cross sections is uncertain by 5%, owing to errors in measuring the solid angle, target-thickness uncertainty, and charge-collection efficiency." (p3-4) additional 5% enrichment-related error applies only to inelastic cross sections.
Notes: "less than" values are upper bounds. In the optical-model fit the authors themselves used "Delta sigma = 10% for all 29 angles" (p4), not an experimental error. Normalisation components: solid angle, target thickness, charge collection (individual sizes not stated; 5% total).

## O0549 Sinha et al., NPA 183, 401 (1972) (Mo-92 at 19.85, 30.3, 49.45 MeV; Mo-94 at 49.45)

| subentry | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| O0549003 (Mo-92; 19.85, 30.3, 49.45 MeV) | dσ/dΩ | "typically ~ 4%", fairly constant over angle; mostly statistical; not visible on graphs (Figs. 1, 2, 4 show only open circles) | 1% target-thickness uncertainty; no other absolute-scale statement | p7 Sect. 2 text; Figs 1-2 p3-4, Fig. 4 p6 | high | 4% relative at all angles |
| O0549005 (Mo-94, 49.45 MeV) | dσ/dΩ | same ~4% | same | same | high | 4% |

Quote (p7): "The cross section errors are too small to show on the graphs. They are fairly constant through the angular range and are typically ~ 4 %, most of which is statistical and the remainder is due mainly to a 1 % uncertainty in target thickness. The errors shown for the polarization are largely statistical and varied between +-0.03 at forward angles and +-0.1 at backward angles."
Notes: composition: statistical (~3.9% quadrature, inferred) plus 1% target thickness. Polarisation (O0549006 etc., not in our brief): +-0.03 forward to +-0.1 backward (absolute, Ay units), p7. Angular spread 0.6 deg for cross sections. No beam-integration or solid-angle normalisation uncertainty given; treat overall normalisation as not stated beyond the 1%.

## O1199 Fabrici et al., PRC 21, 830 (1980) (Ca-40 Ay at 35, 26.3, 40 MeV)

| subentry | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| O1199008 (Ca-40, 35 MeV, Fig. 9) | Ay | not stated for Ay; Fig. 9 shows plain dots with no error bars | not stated for Ay (beam polarisation not discussed) | Fig. 9 p8 | low | Use a floor of about 0.02-0.03 absolute (inferred from dot scatter; no author number). Flag as low confidence. |
| O1199009 (Ca-40, 26.3 and 40 MeV, Fig. 11) | Ay | not stated; Fig. 11 plain dots without bars | not stated | Fig. 11 p11 | low | same as above |

Quote (p2, Sect. I/II): "The uncertainty in absolute cross section values was estimated to be about 4%. Statistical errors were generally negligible. A more detailed discussion of the errors affecting the present measurements is given in paper II." (paper II = PRC 21, 844, not in this entry's PDF; may give the polarisation error discussion.)
Notes: the only stated number is for cross sections (4% absolute); no statement on polarisation uncertainty or beam-polarisation calibration. Fig. 6 error bars refer to peak positions, not data. Suggest consulting PRC 21, 844 (Paper II) for polarisation error if available.

## O0169 Wassenaar et al., J. Phys. G 15, 181 (1989) (Ni, Sr, Cd, Sn, p at 20.4 and 24.6 MeV)

General statement (p5, Sect. 3.1): "As a consequence of the uncertainties in the normalisations of the separate runs and of the various detectors we estimate the minimal relative errors of the elastic cross sections to be 2% and the minimal absolute errors of the analysing powers to be 1%. In general the statistical errors were less for the elastic scattering. These errors give about equal chi-squared values for the cross section and analysing power in the minimalisation procedure."
Figures (Figs 2-7, p10-15): caption of Fig. 2 (p10): "The error bars, if not smaller than the dots, indicate the statistical errors." In the Ni (Fig. 2) and Cd (Fig. 4) figures, error bars are mostly invisible for dσ and visible for Ay mainly near minima/at large angles (estimated size 0.02-0.05, estimate only).
Normalisation (p6-7, Sect. 3.3): "Since we performed no absolute measurement of the cross section, we normalised the experimental elastic cross section to the optical-model value ... the ultimate normalisation for the diverse targets did not differ much (less than 5%) when we accounted for the specific thicknesses." Also "For different sets of optical-model parameters the resulting normalisations can be quite different: e.g. ... 120Sn at 24.6 MeV ... a factor of 1.24 larger [with Beer's geometry]". Ay normalisation checked: "stayed near the value of 1.0".

Mapping inferred from the EXFOR common block and Figs. (Fig. 2 Ni, 3 Sr, 4 Cd, 6 Sn at 20.4, 7 Sn at 24.6).

| subentries | obs | per-point error (author) | normalisation | source | conf | recommendation |
|---|---|---|---|---|---|---|
| 004 (Ni-64), 006, 008 (Sr-86, 88, 24.6), 010, 012, 014 (Cd-110, 112, 114), 016, 018, 020, 022, 024 (Sn-116..124) at 20.4; 026 (Sn, 24.6) | dσ/dΩ (ratio to Rutherford) | "minimal relative errors ... 2%"; statistical smaller; bars hidden by dots | no absolute measurement; normalised to optical model (free); target-to-target norms agree within 5% | p5 Sect. 3.1; p6-7 Sect. 3.3; Figs 2-7 | high (2% stated as minimal) | use 2% relative (high: the authors' stated minimum; it is a floor, so true error may be somewhat larger, e.g. at minima) |
| 005 (Ni-64), 007, 009 (Sr-86, 88), 011 (Cd-110), 017, 019, 021, 023, 025 (Sn at 20.4), 027 (Sn at 24.6) | Ay | "minimal absolute errors of the analysing powers ... 1%" (i.e. 0.01 in Ay units); statistical bars shown if larger than dots (typically 0.01-0.05 off-extrema; estimate) | Ay normalisation near 1.0 (beam polarisation deduced correctly); polarisation scale uncertainty not stated | p5; Figs 2-7; p7 | high for floor of 0.01; low-medium for larger local values | use absolute 0.01 as floor, in quadrature with statistical size read from figure when needed; if only one number, use 0.02 (medium/low, inferred) |

Notes: "Minimal" means a floor from normalisation/detector uncertainties; actual statistical errors add in quadrature and are larger for Ay than for dσ ("In general the statistical errors were less for the elastic scattering"). EXFOR O0169007 carries an extra ERR-T column (compiler states authors' uncertainty reported); not checked against the paper numerically. 24.6 MeV Sr/Sn data subentries not individually confirmed against bars. EXFOR's 1.6/1.9/2.8% reader values are digitisation errors, below the authors' 2% floor, so replace with >= 2%.
