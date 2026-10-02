"""The sm3 corpus: the data sets of Danielewicz, Singh & Lee, "Symmetry energy III:
isovector skins", Nucl. Phys. A 958 (2017) 147, Sec. 3.2 and Figs. 8-11.

Quasielastic (p,n) to the isobaric analog state from Doering, Patterson and Galonsky at 25,
35 and 45 MeV, and elastic (p,p) and (n,n) on 48Ca, 90Zr, 120Sn and 208Pb.  The selection is a
table: every set is named by its EXFOR subentry and energy, and either copied from another
corpus of this repository (with that corpus's curation decisions) or curated here from EXFOR.

Departures from the paper's list, forced by EXFOR:
  * 90Zr(p,p) Van der Bijl et al.: the paper's text says 21.05 MeV, but its Fig. 9 shows
    25.1 MeV and EXFOR has only 25.05 MeV (F0733003, digitized from a figure).  That set is used.
  * 120Sn(p,p) 39.6 MeV, Boyd & Greenlees: not in EXFOR; absent.
  * 208Pb(p,p) Van Oers et al.: EXFOR has each energy twice, digitized from figures with a flat
    6 % reading error (O0287004-010) and tabulated with per-point errors from B. Clark's
    collection (O0287011-017, 15-168 deg as in the paper's Fig. 11).  The tabulated set is used.
"""

from __future__ import annotations

from dataclasses import dataclass

#: corpus sector -> projectile
SECTORS = {"elastic_diff_xs": None, "charge_exchange": "proton"}


@dataclass(frozen=True)
class Pick:
    """One data set: sector, projectile, EXFOR subentry, lab energy (MeV), and where it comes
    from ("elm" or "kduq": copied from that corpus; "exfor": curated here)."""

    sector: str
    projectile: str
    subentry: str
    energy: float
    source: str
    reference: str


def _pn(subentry, energy):
    return Pick("charge_exchange", "proton", subentry, energy, "elm", "Doering et al.")


SELECTION: dict[tuple[int, int], tuple[Pick, ...]] = {
    (48, 20): (
        _pn("O0178008", 25.0), _pn("O0178007", 35.0), _pn("O0178006", 45.0),
        *(Pick("elastic_diff_xs", "proton", "C0624005", e, "elm", "McCamis et al.")
          for e in (21.0, 25.0, 30.0, 35.0, 40.0, 45.0, 48.4)),
        Pick("elastic_diff_xs", "neutron", "14303005", 16.8, "elm", "Mueller et al."),
    ),
    (90, 40): (
        _pn("O0178011", 25.0), _pn("O0178010", 35.0), _pn("O0178009", 45.0),
        Pick("elastic_diff_xs", "proton", "F0733003", 25.05, "exfor", "Van der Bijl et al."),
        Pick("elastic_diff_xs", "proton", "D0295002", 30.0, "elm", "De Swiniarski et al."),
        Pick("elastic_diff_xs", "proton", "O0208008", 40.0, "elm", "Blumberg et al."),
        Pick("elastic_diff_xs", "proton", "O0788017", 49.35, "elm", "Mani et al."),
        Pick("elastic_diff_xs", "neutron", "10729002", 11.0, "elm", "Bainum et al."),
        Pick("elastic_diff_xs", "neutron", "13160004", 24.0, "elm", "Wang & Rapaport"),
    ),
    (120, 50): (
        _pn("O0178014", 25.0), _pn("O0178013", 35.0), _pn("O0178012", 45.0),
        Pick("elastic_diff_xs", "proton", "O0142010", 30.3, "elm", "Ridley & Turner"),
        Pick("elastic_diff_xs", "proton", "O0328007", 40.0, "elm", "Fricke et al."),
        Pick("elastic_diff_xs", "proton", "O0788010", 49.35, "elm", "Mani et al."),
        Pick("elastic_diff_xs", "neutron", "10817008", 11.0, "elm", "Rapaport et al."),
        Pick("elastic_diff_xs", "neutron", "13158007", 13.923, "elm", "Guss et al."),
        Pick("elastic_diff_xs", "neutron", "13158007", 16.905, "elm", "Guss et al."),
    ),
    (208, 82): (
        _pn("O0178017", 25.0), _pn("O0178016", 35.0), _pn("O0178015", 45.0),
        *(Pick("elastic_diff_xs", "proton", s, e, "elm", "Van Oers et al.")
          for s, e in (("O0287012", 24.1), ("O0287014", 30.3), ("O0287015", 35.0),
                       ("O0287016", 45.0), ("O0287017", 47.3))),
        Pick("elastic_diff_xs", "proton", "O0788009", 49.35, "elm", "Mani et al."),
        Pick("elastic_diff_xs", "neutron", "13531002", 7.97, "kduq", "Roberts et al."),
        Pick("elastic_diff_xs", "neutron", "13635003", 9.97, "exfor", "Delaroche et al."),
        *(Pick("elastic_diff_xs", "neutron", "12865002", e, "elm", "Finlay et al.")
          for e in (20.0, 22.0, 24.0)),
        Pick("elastic_diff_xs", "neutron", "10871002", 26.0, "elm", "Rapaport et al."),
        Pick("elastic_diff_xs", "neutron", "12701005", 30.3, "elm", "DeVito et al."),
        Pick("elastic_diff_xs", "neutron", "12701005", 40.0, "elm", "DeVito et al."),
    ),
}

#: the paper's data sets that EXFOR does not have
MISSING = (
    "120Sn(p,p) 39.6 MeV, Boyd & Greenlees: not in EXFOR",
)

#: per-subentry treatment of sets curated from EXFOR here: (statistical fraction, norm error, note)
EXFOR_UNCERTAINTIES = {
    "F0733003": (0.03, 0.05,
                 "EXFOR gives no uncertainty column for this digitized set; per its ERR-ANALYS "
                 "the relative errors combine statistics with a 3% relative normalization, and "
                 "the absolute scale carries 5%: 3% point errors and a 5% normalization error "
                 "are assigned"),
}

#: corpus key of another corpus's sector for a copied record
SOURCE_SECTOR = {
    ("elm", "elastic_diff_xs"): "elastic_diff_xs",
    ("elm", "charge_exchange"): "charge_exchange",
    ("kduq", "elastic_diff_xs"): "neutron_elastic",
}
