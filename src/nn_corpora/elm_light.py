"""The ELM-light corpus: curation decisions for the light targets (even-even 12 <= A <= 40 except 40Ca).

ELM-light is curated the way the ELM corpus is (:mod:`nn_corpora.elm_curate`): an EXFOR query for elastic nucleon
scattering, analysing powers and (p,n) to the isobaric analog state, plus an EXFOR query for the angle-integrated
sigma_tot (n,tot) and sigma_R (p,non), then the author-error and ELM evaluations (``serialize.write_sector``) and TALYS
compound elastic (``scripts/talys_compound.py``). Targets, natural-target mapping and IAS energies are in ``spec``
(``ELM_LIGHT_*``); the decisions specific to the light targets are collected here, with their reasons.

Origin: ``elm/elm_light/curate_light.py`` (2026-09-24), a curation for the old elm_light calibration that used this
package as a library, 10-100 MeV, elastic and (p,n) only. Its manual drops and (p,n) exclusions are ported unchanged;
the energy range, sectors and natural-target handling follow the ELM corpus. See docs/ELM_LIGHT_DATA.md.

Entry point: ``scripts/curate_elm_light.py``.
"""
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

from . import elm, errors, serialize, spec, x4text

CORPUS = "elm_light"

# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------


def _generic(exclusions: dict[str, str]) -> dict[str, str]:
    """ELM's entry exclusions whose reason is a property of the entry (no uncertainties, mistranscription, a ratio
    that does not go to one, a duplicate within the same entry). Only the bare "duplicate" / "duplicate to <other
    entry>" ones were judged for heavy targets, where the other entry exists; for the light targets duplicates are
    judged on the data (``MANUAL_DROPS``, ``near_duplicates``)."""
    def heavy_only(reason):
        return reason == "duplicate" or (re.match(r"duplicate (to|of) ", reason) and "same entry" not in reason)
    return {k: v for k, v in exclusions.items() if not heavy_only(v)}


EXCLUDED_NN = _generic(elm.EXCLUDED_NN)
EXCLUDED_PP_ABSOLUTE = _generic(elm.EXCLUDED_PP_ABSOLUTE)
EXCLUDED_PP_RUTHERFORD = _generic(elm.EXCLUDED_PP_RUTHERFORD)
#: the ELM Ay notebook's exclusions, generic ones only (E0904: no uncertainties)
EXCLUDED_AY = {"E0904": "no uncertainties"}
EXCLUDED_PN = dict(elm.EXCLUDED_PN)

#: (p,n) entries the IAS window lets through although they are not the analog transition (curate_light.py)
EXCLUDED_PN_BY_TARGET: dict[tuple[tuple[int, int], str], str] = {
    ((18, 8), "E1667"): "sums the unresolved 18F quartet at 0.937 (3+), 1.042 (0+ IAS), 1.081 (0-) and "
                        "1.121 (5+) MeV, so it is not the analog transition alone",
    ((18, 8), "E1673"): "the 1.0 MeV group is the same unresolved quartet, and most points carry no uncertainty",
    ((34, 16), "E1361"): "the same Tohoku 35 MeV measurement as E1667009, with most uncertainties missing",
    ((26, 12), "C0733"): "5.5 MeV transition to the 26Al 5+ ground state, not the 0+ analog at 0.228 MeV",
}

#: (subentry, energy MeV, ex_energy MeV or None) -> reason: (p,n) records inside the +-0.3 MeV IAS window that are a
#: different final state. The window is wide for the light odd-odd residuals; curate_elm_light.py reports every (p,n)
#: record whose final state is not within 50 keV of the IAS.
PN_NOT_IAS_RECORDS: dict[tuple, str] = {
    ("D0049008", 23.0, None): "26Al 5+ ground state (EXFOR E-EXC 0.00), not the 0+ analog at 0.228 MeV",
    ("D0049008", 23.0, 0.418): "26Al 3+ level at 0.417 MeV, not the 0+ analog at 0.228 MeV",
}

#: subentry -> reason: records dropped after reviewing the near-duplicate report (same target, projectile and
#: energy, different EXFOR entries). The first 17 are curate_light.py's (10-100 MeV review, 2026-09-24).
MANUAL_DROPS: dict[str, str] = {
    # natural sulphur (Kyle 2026-11-11, >= 90 % natural targets): 12927 (natS) and 14345 (coded 32S, natural sample)
    # are the same Ohio data, ratio 1.000 at every angle; 14345 kept
    "12927004": "same data as 14345005 (natural S, n Ay 10 and 14 MeV)",
    "12927008": "same data as 14345004 (natural S, (n,n) 8-17 MeV)",
    # (n,n) energy-resolution review against the low-lying inelastic states (papers checked 2026-11-11; Kyle: drop)
    "13510002": "Hjort et al., PRC 50, 275 (1994), 12C 65 MeV: resolution 2.7 MeV does not resolve the 4.44 MeV "
                "state; subtracted with (p,p') strengths and DWUCK4 (up to 10 % at some points)",
    "13510003": "Hjort et al., PRC 50, 275 (1994), natural Si 65 MeV: resolution 2.7 MeV does not resolve the 1.78 MeV "
                "2+ state; low-lying states subtracted with (p,p') strengths and DWUCK4 (as 13510002)",
    "22480002": "Baba et al., JNST 39 Suppl. 2, 204 (2002); Ibaraki et al., NIM A 446, 536 (2000), TIARA 55-75 MeV: energy resolution not enough to separate elastic from inelastic; corrected with factors from the LA150 evaluation (as Hjort) (12C)",
    "22480003": "Baba et al., JNST 39 Suppl. 2, 204 (2002); Ibaraki et al., NIM A 446, 536 (2000), TIARA 55-75 MeV: energy resolution not enough to separate elastic from inelastic; corrected with factors from the LA150 evaluation (as Hjort) (natural Si)",
    "22480007": "Baba et al., JNST 39 Suppl. 2, 204 (2002); Ibaraki et al., NIM A 446, 536 (2000), TIARA 55-75 MeV: energy resolution not enough to separate elastic from inelastic; corrected with factors from the LA150 evaluation (as Hjort) (12C 75 MeV)",
    "13946002": "Osborne, Brady & Romero, PRC 70, 054613 (2004), 12C 65-185 MeV: resolution 2.5-4.5 MeV does not resolve "
                "the 4.44 MeV 2+; its contribution estimated with DWUCK4 (< 1 %; Kyle: no model-corrected inelastic)",
    "20240003": "Deconninck & Meulders, PRC 1, 1326 (1970), 12C 17-20 MeV: 3.5 ns over 2 m (about 3-4 MeV at 20 MeV); "
                "elastic and the 4.44 MeV state separated only by a two-Gaussian fit",
    "20240004": "Deconninck & Meulders, PRC 1, 1326 (1970), 12C: as 20240003",
    "22121004": "40Ar(n,n) 7.8 MeV, private communication (Hammer 1989; the cited PRC 39, 1774 has no argon): "
                "resolution about 800 keV, the 1.46 MeV 2+ separation not stated",
    "22121022": "40Ar n Ay 7.8 MeV: same source and resolution as 22121004",
    "22113015": "Boerker et al., Mito 1988, 28Si(n,n) 10.2 MeV: paper not available to check the 1.78 MeV 2+ separation",
    "21629002": "Yamanouti & Tanaka, NEANDC(J)-51/U (1977), 28Si(n,n) 21 MeV: paper not available to check the 1.78 MeV "
                "2+ separation",
    # Sakaguchi et al., 65 MeV (p,p): O0032 and E0166 are the same data (ELM excludes O0032 on the same grounds);
    # ratio to E0166 is 1.000 at every angle
    "O0032052": "same data as E0166002 (16O, 65 MeV)",
    "O0032003": "same data as E0166004 (20Ne, 65 MeV)",
    "O0032053": "same data as E0166006 (24Mg, 65 MeV)",
    "O0032054": "same data as E0166008 (28Si, 65 MeV)",
    "O0032055": "same data as E0166010 (40Ar, 65 MeV)",
    "22189002": "same data as 22284003 (12C, 14.1 MeV), which has more angles",
    "22160005": "same data as 22160002 (12C, 28.2 MeV), which has more angles",
    "O0480005": "subset of O0480012 (16O, 49.5 MeV) from the same entry",
    "O0445002": "same data as E2035009-E2035021 (16O, 10.2-15.6 MeV), at every energy",
    "22544002": "same data as 20559003 (12C, 10-11 MeV), at every energy",
    "E0926002": "the 12C 65 MeV measurement re-reported as E2076030 (26 angles; ratio within 2%)",
    "C0828002": "same data as C0618002 (16O, 17.5 MeV)",
    "C0828008": "same data as C0618004 (24Mg, 17.5 MeV)",
    "C0828012": "same data as C0618006 (26Mg, 17.5 MeV)",
    "C0828016": "same data as C0618008 (28Si, 17.5 MeV)",
    "C0828020": "same data as C0618010 (32S, 17.5 MeV)",
    "F0566002": "the Ieiri/Sakaguchi 12C(p,p) 21-84 MeV data (NIM A257, 253, 1987), re-reported by the "
                "authors as E2076 (2007, CM angles); same angles, a flat ~10% normalisation difference",
    # ELM-light review of the 0-200 MeV near-duplicate report (2026-11-10): identical values (ratio 1.000 at every angle)
    "F0566003": "the Ieiri/Sakaguchi 12C Ay 21-84 MeV, re-reported by the authors as E2076 (as F0566002 for dsigma)",
    "D0292002": "12C Ay 8.6 MeV, the same values as C1018004 (both Rosen et al., PR 124, 199 (1961) and NP 33, 458 "
                "(1962))",
    "C0796002": "28Si(p,p) 180 MeV, the same data as C0152002 (Chen et al., PRC 41, 2514 (1990), compiled twice)",
    "C0796003": "28Si Ay 180 MeV, the same data as C0152004 (Chen et al., PRC 41, 2514 (1990), compiled twice)",
}

#: (subentry, energy MeV) -> reason: single records dropped as possible duplicates (Kyle, 2026-11-10: "drop all possible
#: dups"). Every pair the near-duplicate report flagged (different EXFOR entries, same target/projectile/sector, energies
#: within max(0.1 MeV, 0.5 %), >= 5 common angles agreeing to a median 3 %; 61 pairs) loses one record: the one with
#: fewer angles, on a tie the one with the larger median relative error (before the 2 % floor).
MANUAL_RECORD_DROPS: dict[tuple[str, float], str] = {
    ("10027002", 5.04): "C_12 n elastic_diff_xs 5.04 MeV: within 3 % of 10174002 at 5.05 MeV, which is kept",
    ("10037030", 5.59): "C_12 n elastic_diff_xs 5.59 MeV: within 3 % of 10174002 at 5.57 MeV, which is kept",
    ("10859002", 10.207): "O_16 n elastic_diff_xs 10.207 MeV: within 3 % of 22113003 at 10.159 MeV, which is kept",
    ("11276002", 2.33): "C_12 n elastic_diff_xs 2.33 MeV: within 3 % of 20502002 at 2.36 MeV, which is kept",
    ("14784003", 4.0): "C_12 n elastic_diff_xs 4.0 MeV: within 3 % of 40221005 at 4.0 MeV, which is kept",
    ("20492005", 2.24): "C_12 n elastic_diff_xs 2.24 MeV: within 3 % of 20502002 at 2.26 MeV, which is kept",
    ("23365002", 2.23485): "C_12 n elastic_diff_xs 2.23485 MeV: within 3 % of 23664002 at 2.1369 MeV, which is kept",
    ("23365002", 2.2518): "C_12 n elastic_diff_xs 2.2518 MeV: within 3 % of 23664002 at 2.1688 MeV, which is kept",
    ("23365002", 2.26895): "C_12 n elastic_diff_xs 2.26895 MeV: within 3 % of 23664002 at 2.18505 MeV, which is kept",
    ("23365002", 2.28635): "C_12 n elastic_diff_xs 2.28635 MeV: within 3 % of 23664002 at 2.2518 MeV, which is kept",
    ("23365002", 2.3039): "C_12 n elastic_diff_xs 2.3039 MeV: within 3 % of 23664002 at 2.2518 MeV, which is kept",
    ("23365002", 2.32165): "C_12 n elastic_diff_xs 2.32165 MeV: within 3 % of 23664002 at 2.28635 MeV, which is kept",
    ("23365002", 2.4137): "C_12 n elastic_diff_xs 2.4137 MeV: within 3 % of 23664002 at 2.37625 MeV, which is kept",
    ("23365002", 2.4328): "C_12 n elastic_diff_xs 2.4328 MeV: within 3 % of 23664002 at 2.35785 MeV, which is kept",
    ("23365002", 2.4521): "C_12 n elastic_diff_xs 2.4521 MeV: within 3 % of 23664002 at 2.39485 MeV, which is kept",
    ("23365002", 2.61505): "C_12 n elastic_diff_xs 2.61505 MeV: within 3 % of 23664002 at 2.5728 MeV, which is kept",
    ("23365002", 3.21495): "C_12 n elastic_diff_xs 3.21495 MeV: within 3 % of 23664002 at 3.21495 MeV, which is kept",
    ("23365002", 3.2443): "C_12 n elastic_diff_xs 3.2443 MeV: within 3 % of 23664002 at 3.2443 MeV, which is kept",
    ("23365002", 3.5613): "C_12 n elastic_diff_xs 3.5613 MeV: within 3 % of 23664002 at 3.5613 MeV, which is kept",
    ("23365002", 3.77445): "C_12 n elastic_diff_xs 3.77445 MeV: within 3 % of 23664002 at 3.7376 MeV, which is kept",
    ("23365002", 5.7089): "C_12 n elastic_diff_xs 5.7089 MeV: within 3 % of 23664002 at 5.77865 MeV, which is kept",
    ("23365002", 5.9958): "C_12 n elastic_diff_xs 5.9958 MeV: within 3 % of 23664002 at 6.0709 MeV, which is kept",
    ("23365002", 6.0709): "C_12 n elastic_diff_xs 6.0709 MeV: within 3 % of 23664002 at 6.0709 MeV, which is kept",
    ("C0585002", 121.8): "C_12 p elastic_diff_xs 121.8 MeV: within 3 % of C0055002 at 122.0 MeV, which is kept",
    ("E0926003", 65.0): "C_12 p elastic_ay 65.0 MeV: within 3 % of E0243005 at 65.0 MeV, which is kept",
    ("E0926013", 65.0): "Mg_24 p elastic_ay 65.0 MeV: within 3 % of E0166007 at 65.0 MeV, which is kept",
    ("E2076031", 64.9): "C_12 p elastic_ay 64.9 MeV: within 3 % of E0243005 at 65.0 MeV, which is kept",
    ("F0571003", 1.6): "C_12 p elastic_diff_xs 1.6 MeV: within 3 % of O0852002 at 1.55 MeV, which is kept",
    ("F0571003", 1.65): "C_12 p elastic_diff_xs 1.65 MeV: within 3 % of O0852002 at 1.65 MeV, which is kept",
    ("F0571003", 1.734): "C_12 p elastic_diff_xs 1.734 MeV: within 3 % of O0852002 at 1.725 MeV, which is kept",
    ("F0571003", 1.738): "C_12 p elastic_diff_xs 1.738 MeV: within 3 % of O0852002 at 1.73 MeV, which is kept",
    ("F0571003", 1.742): "C_12 p elastic_diff_xs 1.742 MeV: within 3 % of O0852002 at 1.735 MeV, which is kept",
    ("F0571003", 1.746): "C_12 p elastic_diff_xs 1.746 MeV: within 3 % of O0852002 at 1.74 MeV, which is kept",
    ("O0852002", 2.25): "C_12 p elastic_diff_xs 2.25 MeV: within 3 % of F1090007 at 2.195 MeV, which is kept",
    ("O0852002", 2.425): "C_12 p elastic_diff_xs 2.425 MeV: within 3 % of F1090007 at 2.378 MeV, which is kept",
    ("O0852002", 2.45): "C_12 p elastic_diff_xs 2.45 MeV: within 3 % of F1090007 at 2.378 MeV, which is kept",
}

#: (subentry, energy MeV) -> reason: records whose uncertainties rest, at some or all points, only on the EXFOR
#: compilers' data-point reader (digitisation) error. ELM resolved such records paper by paper (docs/AUTHOR_UNCERTAINTIES.md);
#: the light-target papers were not available, so these were dropped (Kyle, 2026-11-10). 2026-11-11: twelve papers
#: (Kyle) restored O1242, O1367 and F0996 (author_errors.PER_PAPER) and confirmed the drops of O0486, F0471, O0480011/012
#: and O0551 (no author error, or a duplicate; reasons below; Kyle: drop those without one). Restore a record by
#: supplying its author uncertainty in author_errors.py and removing it here (docs/ELM_LIGHT_DATA.md section 4 lists the
#: papers). Generated from author_errors.audit_record over the curated sectors, 2026-11-10.
#: Not here: D0498002 (Daehnick, 16O(p,p)), whose DATA-ERR is the authors' random uncertainty; the reader detector
#: (x4text.READER) matched "angular readings" in its ERR-ANALYS text (data review, 2026-11-10).
READER_ONLY_DROPS: dict[tuple[str, float], str] = {
    ("21729002", 0.641): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.653): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.673): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.681): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.685): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.697): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.701): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.713): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.717): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.737): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.753): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.769): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.785): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.789): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.805): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.849): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.897): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.905): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 0.973): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.0): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.037): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.232): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.252): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.261): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.296): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.308): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.58): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.632): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.64): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.652): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.712): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.752): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.844): "S_32 n elastic_diff_xs: 7 of 7 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.904): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.928): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.94): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.944): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 1.992): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.008): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.044): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.064): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.076): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.108): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.124): "S_32 n elastic_diff_xs: 7 of 7 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.192): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.216): "S_32 n elastic_diff_xs: 7 of 7 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.348): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.372): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.607): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 2.999): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.031): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.079): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.187): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.199): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.227): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.287): "S_32 n elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.411): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729002", 3.455): "S_32 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729003", 0.986): "Si_28 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729003", 1.19): "Si_28 n elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("21729006", 1.05): "S_32 n elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("21729006", 1.65): "S_32 n elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("21729006", 2.25): "S_32 n elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("21729006", 2.85): "S_32 n elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 0.8): "Si_28 n elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 1.3): "Si_28 n elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 1.8): "Si_28 n elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 2.3): "Si_28 n elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 2.8): "Si_28 n elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("21729007", 3.3): "Si_28 n elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("C0246006", 14.1): "O_16 p elastic_diff_xs: 10 of 12 points carry only the EXFOR reader (digitisation) error",
    ("C0246006", 14.7): "O_16 p elastic_diff_xs: 9 of 11 points carry only the EXFOR reader (digitisation) error",
    ("C0246006", 16.6): "O_16 p elastic_diff_xs: 17 of 19 points carry only the EXFOR reader (digitisation) error",
    ("C0246006", 17.6): "O_16 p elastic_diff_xs: 17 of 19 points carry only the EXFOR reader (digitisation) error",
    ("D0890004", 3.65): "Ne_20 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("D0890004", 4.0): "Ne_20 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("D0890004", 4.15): "Ne_20 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("D0890004", 4.35): "Ne_20 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("D0922004", 5.7): "S_32 p elastic_diff_xs: 20 of 20 points carry only the EXFOR reader (digitisation) error",
    ("D0922004", 5.85): "S_32 p elastic_diff_xs: 22 of 22 points carry only the EXFOR reader (digitisation) error",
    ("D0922004", 6.02): "S_32 p elastic_diff_xs: 21 of 21 points carry only the EXFOR reader (digitisation) error",
    ("D0922004", 6.2): "S_32 p elastic_diff_xs: 23 of 23 points carry only the EXFOR reader (digitisation) error",
    ("D0922004", 6.34): "S_32 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0059003", 1.79): "O_16 p elastic_diff_xs: 7 of 10 points carry only the EXFOR reader (digitisation) error",
    ("F0059003", 1.99): "O_16 p elastic_diff_xs: 9 of 10 points carry only the EXFOR reader (digitisation) error",
    ("F0059003", 2.191): "O_16 p elastic_diff_xs: 6 of 10 points carry only the EXFOR reader (digitisation) error",
    ("F0059003", 2.382): "O_16 p elastic_diff_xs: 7 of 10 points carry only the EXFOR reader (digitisation) error",
    ("F0256003", 35.0): "C_12 p elastic_diff_xs: 34 of 34 points carry only the EXFOR reader (digitisation) error",
    ("F0256004", 35.0): "Mg_24 p elastic_diff_xs: 30 of 30 points carry only the EXFOR reader (digitisation) error",
    ("F0256005", 35.0): "Si_28 p elastic_diff_xs: 25 of 25 points carry only the EXFOR reader (digitisation) error",
    ("F0471003", 19.9): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0471003", 21.2): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0471003", 22.65): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0471003", 24.1): "duplicate (paper checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: 24.1 MeV is not among their measured energies (p.129): Dickens et al.'s data replotted",
    ("F0471003", 24.4): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0471003", 26.1): "duplicate (paper checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: 26.1 MeV is not among their measured energies (p.129): Dickens et al.'s data replotted",
    ("F0471003", 27.0): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0471003", 28.85): "no author error in the paper (checked 2026-11-11): Girod et al., J. Phys. 31 (1970) 125: no error stated; normalised to Dickens et al.",
    ("F0866004", 6.05): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.1): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.15): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.2): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.25): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.3): "Mg_24 p elastic_diff_xs: 15 of 15 points carry only the EXFOR reader (digitisation) error",
    ("F0866004", 6.35): "Mg_24 p elastic_diff_xs: 14 of 14 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.1): "Mg_26 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.15): "Mg_26 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.2): "Mg_26 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.25): "Mg_26 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.3): "Mg_26 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("F0866005", 6.35): "Mg_26 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("F0877003", 5.93): "Si_28 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.35): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.45): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.5): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.58): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.65): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.72): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.79): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.85): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.9): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0877005", 5.93): "S_32 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("F0904002", 4.491): "C_12 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("F0904002", 4.615): "C_12 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("F0904002", 5.0): "C_12 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("F0904002", 5.122): "C_12 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("F0904002", 5.222): "C_12 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("F1013003", 4.134): "O_16 p elastic_diff_xs: 22 of 22 points carry only the EXFOR reader (digitisation) error",
    ("F1013003", 4.268): "O_16 p elastic_diff_xs: 20 of 20 points carry only the EXFOR reader (digitisation) error",
    ("F1013003", 4.402): "O_16 p elastic_diff_xs: 23 of 23 points carry only the EXFOR reader (digitisation) error",
    ("F1013003", 4.54): "O_16 p elastic_diff_xs: 23 of 23 points carry only the EXFOR reader (digitisation) error",
    ("F1019002", 6.03): "Mg_24 p elastic_diff_xs: 29 of 29 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 1.365): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 1.548): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 1.734): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 1.917): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 2.195): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1090007", 2.378): "C_12 p elastic_diff_xs: 32 of 32 points carry only the EXFOR reader (digitisation) error",
    ("F1135002", 5.94): "Mg_24 p elastic_diff_xs: 19 of 19 points carry only the EXFOR reader (digitisation) error",
    ("F1135004", 5.84): "Mg_26 p elastic_diff_xs: 14 of 14 points carry only the EXFOR reader (digitisation) error",
    ("F1135004", 5.94): "Mg_26 p elastic_diff_xs: 18 of 18 points carry only the EXFOR reader (digitisation) error",
    ("F1135004", 6.03): "Mg_26 p elastic_diff_xs: 13 of 13 points carry only the EXFOR reader (digitisation) error",
    ("O0062002", 135.0): "O_16 p elastic_diff_xs: 27 of 33 points carry only the EXFOR reader (digitisation) error",
    ("O0079002", 20.0): "C_12 p elastic_diff_xs: 21 of 21 points carry only the EXFOR reader (digitisation) error",
    ("O0211002", 61.4): "C_12 p elastic_diff_xs: 33 of 38 points carry only the EXFOR reader (digitisation) error",
    ("O0254008", 17.8): "C_12 p elastic_diff_xs: 21 of 21 points carry only the EXFOR reader (digitisation) error",
    ("O0384022", 14.1): "Ar_40 p elastic_diff_xs: 27 of 27 points carry only the EXFOR reader (digitisation) error",
    ("O0384023", 16.9): "Ar_40 p elastic_diff_xs: 25 of 25 points carry only the EXFOR reader (digitisation) error",
    ("O0480011", 49.4): "duplicate (paper checked 2026-11-11): Clarke et al., NPA 157 (1970) 145: a reading of the optical-model fit figure (Fig. 8); the data are Fannon et al. (forward) and O0480002 (backward, with the authors' errors)",
    ("O0480012", 49.4): "duplicate (paper checked 2026-11-11): Clarke et al., NPA 157 (1970) 145: a reading of the optical-model fit figure (Fig. 9); the data are Fannon et al. (forward) and O0480005 (backward, with the authors' errors)",
    ("O0486002", 19.8): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 20.4): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 20.8): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 21.4): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 22.1): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 24.3): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 26.2): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0486002", 30.5): "no author error in the paper (checked 2026-11-11): Karban et al., NPA 132 (1969) 548: no error stated beyond 'statistical errors smaller than the points' (Fig. 1)",
    ("O0492002", 2.5): "O_16 p elastic_diff_xs: 23 of 23 points carry only the EXFOR reader (digitisation) error",
    ("O0492002", 3.0): "O_16 p elastic_diff_xs: 26 of 26 points carry only the EXFOR reader (digitisation) error",
    ("O0492002", 3.4): "O_16 p elastic_diff_xs: 26 of 26 points carry only the EXFOR reader (digitisation) error",
    ("O0492002", 3.8): "O_16 p elastic_diff_xs: 26 of 26 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 3.0): "O_16 p elastic_ay: 1 of 5 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 3.4): "O_16 p elastic_ay: 1 of 5 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 5.66): "O_16 p elastic_ay: 2 of 7 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 6.0): "O_16 p elastic_ay: 1 of 12 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 7.01): "O_16 p elastic_ay: 1 of 14 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 8.5): "O_16 p elastic_ay: 3 of 14 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 9.5): "O_16 p elastic_ay: 4 of 11 points carry only the EXFOR reader (digitisation) error",
    ("O0492003", 10.74): "O_16 p elastic_ay: 1 of 11 points carry only the EXFOR reader (digitisation) error",
    ("O0551002", 30.0): "no author error in the paper (checked 2026-11-11): Rush, Burge & Smith, NPA 166 (1971) 378: no error stated for the elastic cross sections (figures only)",
    ("O0551002", 50.0): "no author error in the paper (checked 2026-11-11): Rush, Burge & Smith, NPA 166 (1971) 378: no error stated for the elastic cross sections (figures only)",
    ("O0551005", 50.0): "duplicate (paper checked 2026-11-11): Rush, Burge & Smith, NPA 166 (1971) 378, p.385: Fannon et al.'s 12C 50 MeV data reanalysed, not this experiment's",
    ("O0889003", 1.873): "Ar_40 p elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.874): "Ar_40 p elastic_diff_xs: 8 of 8 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.877): "Ar_40 p elastic_diff_xs: 7 of 7 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.886): "Ar_40 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.887): "Ar_40 p elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.891): "Ar_40 p elastic_diff_xs: 7 of 7 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.893): "Ar_40 p elastic_diff_xs: 6 of 6 points carry only the EXFOR reader (digitisation) error",
    ("O0889003", 1.895): "Ar_40 p elastic_diff_xs: 5 of 5 points carry only the EXFOR reader (digitisation) error",
    ("O1030004", 2.6): "Mg_24 p elastic_diff_xs: 12 of 12 points carry only the EXFOR reader (digitisation) error",
    ("O1030004", 2.8): "Mg_24 p elastic_diff_xs: 14 of 14 points carry only the EXFOR reader (digitisation) error",
    ("O1030004", 3.0): "Mg_24 p elastic_diff_xs: 10 of 10 points carry only the EXFOR reader (digitisation) error",
    ("O1030005", 1.5): "Mg_26 p elastic_diff_xs: 9 of 9 points carry only the EXFOR reader (digitisation) error",
    ("O1030005", 2.03): "Mg_26 p elastic_diff_xs: 10 of 10 points carry only the EXFOR reader (digitisation) error",
    ("O1030005", 2.5): "Mg_26 p elastic_diff_xs: 11 of 11 points carry only the EXFOR reader (digitisation) error",
    ("O1090002", 9.1): "Mg_24 p elastic_diff_xs: 26 of 26 points carry only the EXFOR reader (digitisation) error",
    ("O1090006", 9.1): "Mg_26 p elastic_diff_xs: 28 of 28 points carry only the EXFOR reader (digitisation) error",
    ("O1133002", 40.9): "C_12 p elastic_diff_xs: 48 of 48 points carry only the EXFOR reader (digitisation) error",
    ("O1133003", 40.9): "O_16 p elastic_diff_xs: 43 of 43 points carry only the EXFOR reader (digitisation) error",
    ("O1177002", 150.0): "C_12 p elastic_ay: 14 of 23 points carry only the EXFOR reader (digitisation) error",
    ("O1177003", 150.0): "C_12 p elastic_diff_xs: 19 of 19 points carry only the EXFOR reader (digitisation) error",
    ("O1542002", 40.75): "Si_30 p elastic_diff_xs: 29 of 29 points carry only the EXFOR reader (digitisation) error",
}

#: (subentry, energy MeV) -> reason: records whose uncertainty is below an author uncertainty EXFOR itself carries
#: (the parse chose another column). Recoverable from EXFOR alone (an ELM-style PARSE_RECIPE naming the author column);
#: dropped for now with the reader-only records (2026-11-10).
BELOW_AUTHOR_DROPS: dict[tuple, str] = {
    ("22847002", 96.0): "C_12 n elastic_diff_xs: errors below the authors' own EXFOR error at 22 of 22 angles",
    ("O0274009", 96.0): "C_12 p elastic_diff_xs: errors below the authors' own EXFOR error at 6 of 46 angles",
    ("O0434004", 20.93): "O_16 p elastic_diff_xs: errors below the authors' own EXFOR error at 40 of 40 angles",
    ("O0434006", 21.13): "Ar_40 p elastic_diff_xs: errors below the authors' own EXFOR error at 39 of 39 angles",
}

#: (subentry, energy MeV, first y) -> reason: one of several records sharing subentry and energy, told apart by value
#: (code review, 2026-11-10)
VALUE_KEYED_DROPS: dict[tuple[str, float, float], str] = {
    ("O0257007", 38.0, 0.004): "EXFOR data set 1 of O0257007 is the asymmetry (beam polarisation 0.20-0.29 x Ay), "
                               "not the analysing power; data set 2, the Ay itself, is kept",
}

#: subentry -> (E_max MeV, reason): sigma_tot/sigma_R points above E_max removed (code review, 2026-11-10)
POINT_ENERGY_MAX: dict[str, tuple[float, str]] = {
    "22184003": (5.0, "Moxon et al. (natC sigma_tot): EXFOR STATUS 'the cross section above 5 MeV are not thought to "
                      "be meaningful' (background, gamma flash); 1.5-3x the other 12C sets above 5 MeV"),
}

#: angular records need this many distinct angles (spec.ELM_MIN_NUM_PTS counts points, which repeats can inflate:
#: C1177003, a 14.02 MeV 12C Ay resonance scan grouped into 21 'angular distributions' of 4-6 angles each)
MIN_DISTINCT_ANGLES = spec.ELM_MIN_NUM_PTS

#: energy (MeV) of each target's first excited state, to judge summed-scattering records whose excitation bound is
#: only an upper limit (ENSDF)
FIRST_EXCITED: dict[tuple[int, int], float] = {
    (12, 6): 4.439, (14, 6): 6.094, (16, 8): 6.049, (18, 8): 1.982, (20, 10): 1.634,
    (24, 12): 1.369, (26, 12): 1.809, (28, 14): 1.779, (30, 14): 2.235, (32, 16): 2.230, (34, 16): 2.128,
    (40, 18): 1.461,
}  # fmt: skip


def label(target: tuple[int, int]) -> str:
    return serialize.target_filename(target)


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def repair_by_supplement_rule(data: dict, quantities, result) -> None:
    """Parses ELM's per-entry recipes (``elm.PARSE_RECIPES``) do not cover: choose the uncertainty column by the
    supplement's rule (ERR-T, then +-DATA-ERR, DATA-ERR, ERR-S, ERR-DIG, ERR-SYS), as this package does for the
    tabulated corpora (``errors.resolve_entry``)."""
    for target, multi in data.items():
        for q in quantities:
            entries = multi.data[q]
            for entry_id in list(entries.failed_parses):
                try:
                    a = errors.resolve_entry(entry_id)
                except Exception:  # noqa: BLE001 - an entry x4i3 cannot read stays failed
                    continue
                if not a.resolved:
                    continue
                entries.reattempt_parse(entry_id, a.parsing_kwargs)
                if entry_id in entries.entries:
                    result.repaired.append(f"{q} {entry_id} ({label(target)}): supplement rule {a.rule} -> "
                                           f"{a.chosen}")


def exclude_pn_by_target(pn: dict, result) -> None:
    for (target, entry_id), reason in EXCLUDED_PN_BY_TARGET.items():
        multi = pn.get(target)
        if multi is None:
            continue
        store = multi.data["dXS/dA"]
        for s in (store.entries, store.failed_parses):
            if entry_id in s:
                del s[entry_id]
                result.excluded.append(f"dXS/dA {entry_id} ({label(target)}): {reason}")


def record_failed_parses(data: dict, result, what: str) -> None:
    for target, multi in data.items():
        for q, entries in multi.data.items():
            for entry_id in entries.failed_parses:
                result.dropped.append(f"{what} {q} {entry_id} ({label(target)}): parse failed")


def split_natural(data: dict) -> tuple[dict, dict]:
    """(isotopic, natural) query results; natural ones re-keyed by their dominant isotope, so they are munged (CM
    angles, Rutherford ratio) as that isotope."""
    iso = {t: m for t, m in data.items() if t[0] != 0}
    nat = {spec.ELM_LIGHT_NATURAL[t][0]: m for t, m in data.items() if t[0] == 0}
    return iso, nat


def mark_natural(records) -> None:
    """Flag records measured on a natural target (already keyed by the dominant isotope)."""
    abundance = {iso: ab for iso, ab in spec.ELM_LIGHT_NATURAL.values()}
    for rec in records:
        rec.payload["natural_target"] = True
        rec.payload.setdefault("notes", []).append(
            f"measured on a natural {rec.payload['target'].split('-')[0]} target; treated as "
            f"{rec.payload['target']} ({abundance[rec.target]:.2%} abundant)")


def _reader_key(r):
    """The READER_ONLY_DROPS / BELOW_AUTHOR_DROPS key matching record r, or None. (subentry, energy) keys, or
    (subentry, energy, n points) where one subentry has several records at an energy."""
    sub, E, n = r.payload["EXFORAccessionNumber"], r.payload.get("energy"), len(r.payload["data"]["x"])
    for key in ((sub, E, n), (sub, E)):
        if key in READER_ONLY_DROPS or key in BELOW_AUTHOR_DROPS:
            return key
    return None


def cut_point_energies(records, result) -> None:
    """Trim sigma_tot / sigma_R records to POINT_ENERGY_MAX (before the evaluation floor is applied)."""
    for r in records:
        sub = r.payload["EXFORAccessionNumber"]
        if sub not in POINT_ENERGY_MAX:
            continue
        emax, why = POINT_ENERGY_MAX[sub]
        d = r.payload["data"]
        keep = np.asarray(d["x"], dtype=float) <= emax
        n = len(keep)
        for k, v in list(d.items()):
            if isinstance(v, list) and len(v) == n:
                d[k] = [x for x, ok in zip(v, keep) if ok]
        r.payload.setdefault("notes", []).append(f"points above {emax:g} MeV removed ({int((~keep).sum())} of {n}): {why}")
        result.repaired.append(f"{sub}: {int((~keep).sum())} of {n} points above {emax:g} MeV removed")


def drop_nonpositive_points(records, result) -> None:
    """Remove sigma_tot / sigma_R points <= 0 (transmission data at deep resonance minima, e.g. Larson natSi 14203002
    below 3.7 MeV; a cross section is positive, and the likelihoods work in log space)."""
    for r in records:
        d = r.payload["data"]
        keep = np.asarray(d["y"], dtype=float) > 0
        if keep.all():
            continue
        n = len(keep)
        for k, v in list(d.items()):
            if isinstance(v, list) and len(v) == n:
                d[k] = [x for x, ok in zip(v, keep) if ok]
        x = np.asarray(r.payload["data"]["x"], dtype=float)
        r.payload.setdefault("notes", []).append(f"{n - int(keep.sum())} of {n} points <= 0 removed")
        result.repaired.append(f"{r.payload['EXFORAccessionNumber']}: {n - int(keep.sum())} of {n} points <= 0 removed")


def drop_pn_not_ias(records, result) -> list:
    keep = []
    for r in records:
        p = r.payload
        key = (p["EXFORAccessionNumber"], p.get("energy"), p.get("ex_energy"))
        if key in PN_NOT_IAS_RECORDS:
            result.excluded.append(f"{key[0]} ({label(r.target)} {key[1]} MeV, Ex {key[2]}): {PN_NOT_IAS_RECORDS[key]}")
        else:
            keep.append(r)
    return keep


def pn_final_state_report(records) -> list[str]:
    """(p,n) records whose tabulated final state is not within 50 keV of the IAS (review aid)."""
    out = []
    for r in records:
        ex, ias = r.payload.get("ex_energy"), spec.ELM_LIGHT_EX_IAS[tuple(r.target)]
        if ex is None or abs(float(ex) - ias) > 0.05:
            out.append(f"  {label(r.target)} {r.payload['EXFORAccessionNumber']} {r.payload['energy']} MeV: "
                       f"Ex {ex} vs IAS {ias} MeV")
    return out


#: dominant isotope (A) and natural abundance by Z, for the SAMPLE check (spec.ELM_LIGHT_NATURAL and _EXCLUDED)
_DOMINANT = {**{z: (a, ab) for (_, z), ((a, _), ab) in spec.ELM_LIGHT_NATURAL.items()},
             **spec.ELM_LIGHT_NATURAL_EXCLUDED}
_NATURAL = re.compile(r"NAT=|natur", re.I)
_ENRICHED = re.compile(r"enrich|ENR=", re.I)


def natural_sample(subentry: str) -> bool:
    """Whether EXFOR's SAMPLE text (the entry's common subentry 001 and the subentry's own) says the sample was of
    natural isotopic composition, and not enriched: EXFOR often codes such data as the dominant isotope (e.g.
    Virdis 21773, "SAMPLE (12-MG-24,NAT=0.79)"). Found reviewing the (n,n) papers, 2026-11-11."""
    entry = subentry[:5]
    try:
        subs = x4text.subentries(entry)
    except FileNotFoundError:
        return False
    text = " ".join(x4text.bib_fields(subs.get(k, ())).get("SAMPLE", "") for k in (entry + "001", subentry))
    return bool(_NATURAL.search(text)) and not _ENRICHED.search(text)


def apply_natural_samples(records, result) -> list:
    """Records EXFOR codes as the dominant isotope but measured on a natural sample: kept and marked natural where
    the dominant isotope is >= spec.ELM_LIGHT_NATURAL_MIN abundant, dropped otherwise (natMg; Kyle, 2026-11-11)."""
    keep = []
    for r in records:
        A, Z = tuple(r.target)
        if A == 0 or r.payload.get("natural_target") or _DOMINANT.get(Z, (None,))[0] != A \
                or not natural_sample(r.payload["EXFORAccessionNumber"][:8]):
            keep.append(r)
            continue
        ab = _DOMINANT[Z][1]
        if ab < spec.ELM_LIGHT_NATURAL_MIN:
            result.dropped.append(f"{r.payload['EXFORAccessionNumber']} ({label(r.target)} {r.payload.get('energy')}): "
                                  f"natural sample (EXFOR SAMPLE), {ab:.1%} {label(r.target)}: below the "
                                  f"{spec.ELM_LIGHT_NATURAL_MIN:.0%} natural-target threshold")
            continue
        r.payload["natural_target"] = True
        r.payload.setdefault("notes", []).append(
            f"measured on a natural {r.payload['target'].split('-')[0]} target (EXFOR SAMPLE; coded as the isotope); "
            f"treated as {r.payload['target']} ({ab:.2%} abundant)")
        keep.append(r)
    return keep


def apply_manual_drops(records, result) -> list:
    records = apply_natural_samples(records, result)
    keep = []
    for r in records:
        sub = r.payload["EXFORAccessionNumber"]
        rec_key = next((k for k in MANUAL_RECORD_DROPS
                        if k[0] == sub and "energy" in r.payload and abs(float(r.payload["energy"]) - k[1]) < 1e-6), None)
        if sub in MANUAL_DROPS:
            result.dropped.append(f"{sub} ({label(r.target)} {r.payload.get('energy')}): {MANUAL_DROPS[sub]}")
        elif rec_key is not None:
            result.dropped.append(f"{sub} ({label(r.target)} {r.payload['energy']}): {MANUAL_RECORD_DROPS[rec_key]}")
        elif (sub, r.payload.get("energy"), (r.payload["data"]["y"] or [None])[0]) in VALUE_KEYED_DROPS:
            why = VALUE_KEYED_DROPS[(sub, r.payload.get("energy"), r.payload["data"]["y"][0])]
            result.dropped.append(f"{sub} ({label(r.target)} {r.payload.get('energy')}): {why}")
        elif "energy" in r.payload and len(set(np.round(r.payload["data"]["x"], 2))) < MIN_DISTINCT_ANGLES:
            result.dropped.append(f"{sub} ({label(r.target)} {r.payload['energy']}): only "
                                  f"{len(set(np.round(r.payload['data']['x'], 2)))} distinct angles")
        elif _reader_key(r) is not None:
            key = _reader_key(r)
            why = READER_ONLY_DROPS.get(key) or BELOW_AUTHOR_DROPS[key]
            result.dropped.append(f"{sub} ({label(r.target)} {r.payload.get('energy')}): dropped for now: {why}")
        else:
            keep.append(r)
    return keep


# ---------------------------------------------------------------------------
# Angle-integrated sectors: spec rows from an EXFOR query
# ---------------------------------------------------------------------------

#: sector -> (projectile name, x4i3 reaction product code)
INTEGRAL_SECTORS = {"neutron_total": ("neutron", "TOT"), "proton_reaction": ("proton", "NON")}


ENERGY_UNITS = {"EV", "KEV", "MEV", "GEV"}
#: subentries integral_rows passed over, with the reason (for the curation report)
SKIPPED_ROWS: list[str] = []


def integral_rows(sector: str, targets, e_range=spec.ELM_LIGHT_INTEGRAL_EINC_RANGE) -> list[spec.SpecRow]:
    """``spec.SpecRow`` s for every EXFOR subentry of sigma_tot (n,tot) or sigma_R (p,non) on ``targets``, as if
    tabulated over ``e_range``, so the tabulated-corpus machinery (``corpus.curate``: uncertainty-column rules,
    overrides, energy window, munging) curates them. Only the measured cross section is taken (SIG or SIG,,EXP; not
    CALC, ratios or averages)."""
    from exfor_tools.reaction import Reaction, query_for_reaction

    proj_name, product = INTEGRAL_SECTORS[sector]
    projectile = spec.PROJECTILES[proj_name]
    process = spec.SECTORS[sector][1]
    rows, seen = [], set()
    for target in targets:
        for entry in query_for_reaction(Reaction(target=target, projectile=projectile, process=process), "XS"):
            try:
                data_sets = errors.entry_data_sets(entry)
            except errors.EntryUnavailable:
                continue
            for (_, sub, ptr), ds in data_sets.items():
                rx = ds.reaction[0]
                if not hasattr(rx, "targ") or (sub, ptr.strip()) in seen:
                    continue
                A, Z = rx.targ.getA(), rx.targ.getZ()
                t = (0, Z) if A == -3000 else (A, Z)
                quantity = list(getattr(rx, "quantity", None) or [])
                if (t != tuple(target) or quantity[:1] != ["SIG"] or set(quantity[1:]) - {"EXP"}
                        or [str(p).upper() for p in (getattr(rx, "products", None) or [])] != [product]
                        or str(getattr(rx, "proj", "")).lower() != proj_name[0]):
                    continue
                seen.add((sub, ptr.strip()))
                units = dict(zip(ds.labels, ds.units))
                en = next((units[k] for k in ds.labels if k.startswith("EN")
                           and not k.startswith(("EN-RSL", "EN-ERR", "EN-RES", "+EN-ERR", "-EN-ERR"))), "")
                if en.upper() not in ENERGY_UNITS:  # e.g. beam momentum (GEV/C): not an incident energy
                    SKIPPED_ROWS.append(f"{sub} ({label(t)}): incident energy column in {en!r}, not an energy")
                    continue
                rows.append(spec.SpecRow(corpus=CORPUS, sector=sector, projectile=proj_name, target_A=t[0],
                                         target_Z=t[1], target_label=label(t), energy_mev=e_range[0],
                                         energy_hi_mev=e_range[1], subentry=sub, pointer=ptr.strip(), pdf_page=None))
    return rows


# ---------------------------------------------------------------------------
# Review aids
# ---------------------------------------------------------------------------


def _compare(a: dict, b: dict) -> tuple[int, float]:
    """(n common angles, median |ya/yb - 1|) over angles within 0.3 degrees."""
    xa, ya = np.asarray(a["data"]["x"]), np.asarray(a["data"]["y"])
    xb, yb = np.asarray(b["data"]["x"]), np.asarray(b["data"]["y"])
    ratios = []
    for x, y in zip(xa, ya):
        j = np.argmin(np.abs(xb - x))
        if abs(xb[j] - x) <= 0.3 and yb[j] != 0:
            ratios.append(y / yb[j])
    if not ratios:
        return 0, np.inf
    return len(ratios), float(np.median(np.abs(np.asarray(ratios) - 1)))


def near_duplicates(records) -> list[tuple[str, str]]:
    """(verdict, description) for pairs of angular distributions from different EXFOR entries on one target,
    projectile, sector and energy; LIKELY DUPLICATE when >= 5 common angles agree to a median 3 %."""
    rows = []
    by = defaultdict(list)
    for r in records:
        if "energy" in r.payload:
            by[(r.target, r.payload["projectile"], r.payload["sector"])].append(r.payload)
    for (t, proj, sector), L in sorted(by.items()):
        L = sorted(L, key=lambda p: (float(p["energy"]), p["EXFORAccessionNumber"]))
        for i, a in enumerate(L):
            for b in L[i + 1:]:
                Ea, Eb = float(a["energy"]), float(b["energy"])
                if Eb - Ea > max(0.1, 0.005 * Ea):
                    break
                if a["EXFORAccessionNumber"][:5] == b["EXFORAccessionNumber"][:5]:
                    continue
                n, dev = _compare(a, b)
                verdict = "LIKELY DUPLICATE" if n >= 5 and dev < 0.03 else "distinct"
                rows.append((verdict, f"{label(t)} {proj} {sector} E={Ea:g}/{Eb:g} {a['EXFORAccessionNumber']} "
                                      f"({len(a['data']['x'])} pts) vs {b['EXFORAccessionNumber']} "
                                      f"({len(b['data']['x'])} pts): {n} common angles, median |ratio-1| = {dev:.3f}"))
    return rows
