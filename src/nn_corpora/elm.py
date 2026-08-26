"""The ELM corpus: curation decisions ported from the ELM notebooks.

Unlike KDUQ, CHUQ and Test, the ELM corpus is not defined by a table of subentries.
It is a query -- every EXFOR data set for elastic nucleon scattering on a set of
near-spherical targets in a given energy window -- followed by a long sequence of
human judgements: entries excluded as duplicates or as lacking uncertainties, parses
repaired by naming the right uncertainty columns, and individual points corrected for
apparent transcription errors.

Those judgements are the corpus. They are collected here as data, with the reasons
recorded in the ELM notebooks preserved verbatim, so that the notebooks in
``notebooks/elm/`` read as a curation record rather than a wall of edits.

Source: ``~/elm/elm_data/curate_elastic_dataset_from_exfor.ipynb``,
``curate_Ay_from_exfor.ipynb`` and ``curate_pn_from_exfor.ipynb``.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Entries excluded, with the reason recorded in the notebooks
# ---------------------------------------------------------------------------

EXCLUDED_PP_ABSOLUTE: dict[str, str] = {
    "E0120": "no uncertainties reported",
    "C0078": "redundant, huge uncertainties",
    "E0795": "duplicate, no uncertainties",
    "O0032": "duplicate to E0166 and E0249",
    "E0249": "duplicate to E0166 and O0032",
    "O0253": "duplicate to the ratio to Rutherford from the same entry",
    "C3000": "no uncertainties",
    "E0904": "no uncertainties",
    "C1019": "old and in poor agreement with other measurements due to normalization, "
             "but no normalization uncertainty given",
    "O0553": "ratio to Rutherford does not go to 1 at low angle",
    "O0166": "ratio to Rutherford does not go to 1 at low angle",
    "C0081": "apparent mistranscriptions",
    "T0289": "no uncertainties",
}

EXCLUDED_PP_RUTHERFORD: dict[str, str] = {
    "O0490": "no uncertainties",
    "E0120": "no uncertainties",
    "O0432": "no uncertainties",
    "C3001": "no uncertainties",
    "E1846": "no uncertainties",
    "C1397": "no uncertainties",
    "C1019": "old and in poor agreement with other measurements due to normalization, "
             "but no normalization uncertainty given",
    "O0553": "ratio to Rutherford does not go to 1 at low angle",
    "O0166": "ratio to Rutherford does not go to 1 at low angle",
    "O1199": "angles in EXFOR are systematically offset compared to the figures in the "
             "paper (lab vs CM angle?)",
    "O0169": "no uncertainties",
    "F0733": "no uncertainties",
    "O0300": "no uncertainties",
    "O1825": "no uncertainties",
    "T0289": "no uncertainties",
    "O0581": "no uncertainties",
    "O01240": "no uncertainties",
    "E0904": "no uncertainties",
}

EXCLUDED_NN: dict[str, str] = {
    "14317": "duplicate",
}

EXCLUDED_PN: dict[str, str] = {
    "T0162": "dominated by Gamow-Teller strength, not the isobaric analog state",
}

# ---------------------------------------------------------------------------
# Uncertainty-column assignments read from each entry's ERR-ANALYS text
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParseRecipe:
    statistical: tuple[str, ...]
    systematic: tuple[str, ...] = ()
    treatment: str = "independent"

    @property
    def parsing_kwargs(self) -> dict:
        return {
            "statistical_err_labels": list(self.statistical),
            "statistical_err_treatment": self.treatment,
            "systematic_err_labels": list(self.systematic),
        }


PARSE_RECIPES: dict[str, ParseRecipe] = {
    "C0624": ParseRecipe(("DATA-ERR",), ("ERR-SYS",)),
    "O0211": ParseRecipe(("DATA-ERR", "ERR-T")),
    "O0253": ParseRecipe(("ERR-1", "ERR-DIG"), ("ERR-2",)),
    "O0302": ParseRecipe(("DATA-ERR1", "ERR-DIG"), ("DATA-ERR2",)),
    "O0287": ParseRecipe(("DATA-ERR",), ("ERR-1",)),
    "O0552": ParseRecipe(("DATA-ERR", "ERR-T")),
    "O0142": ParseRecipe(("ERR-T",), ("ERR-1",)),
    "O0208": ParseRecipe(("ERR-2",), ("ERR-1",)),
    "O0382": ParseRecipe(("ERR-T", "DATA-ERR")),
    "T0101": ParseRecipe(("DATA-ERR",), ("DATA-ERR1",)),
    "O0389": ParseRecipe(("ERR-2",), ("ERR-1",)),
    "O0124": ParseRecipe(("DATA-ERR1",)),
    "O0328": ParseRecipe(("ERR-1", "ERR-DIG"), ("ERR-2", "ERR-3")),
    "D0289": ParseRecipe(("ERR-S", "ERR-DIG"), ("ERR-1", "ERR-2")),
    "F1173": ParseRecipe(("DATA-ERR2", "ERR-DIG")),
    "10633": ParseRecipe(("DATA-ERR1",), ("DATA-ERR2",)),
    "12701": ParseRecipe(("DATA-ERR1",), ("DATA-ERR2",)),
    "22987": ParseRecipe(("ERR-S",), ("ERR-1", "ERR-2")),
    "10867": ParseRecipe(("ERR-T",), ("ERR-1",)),
    "C0134": ParseRecipe(("ERR-S",), ("ERR-SYS",)),
    "O0178": ParseRecipe(("ERR-T", "DATA-ERR"), ("ERR-1",)),
    "O0090": ParseRecipe(("DATA-ERR",), ("ERR-T",)),
    "O0138": ParseRecipe(("+ERR-T", "-ERR-T"), treatment="sum"),
}

# ---------------------------------------------------------------------------
# Point-level corrections made after inspecting the plotted data
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PointFix:
    """A single data point rescaled, with the note recorded in the notebook."""

    entry: str
    quantity: str
    target: tuple[int, int]
    measurement_index: int
    point_index: int
    factor: float
    note: str
    scale_uncertainty: bool = True


POINT_FIXES: tuple[PointFix, ...] = (
    PointFix("12701", "dXS/dA", (208, 82), 1, 1, 10.0,
             "2nd point increased by a factor of 10", scale_uncertainty=False),
    PointFix("O0142", "dXS/dA", (208, 82), 0, 3, 0.1,
             "12th to last point decreased by a factor of 10"),
    PointFix("O0157", "dXS/dA", (208, 82), 0, 0, 0.1,
             "1st point decreased by a factor of 10"),
    PointFix("O0211", "dXS/dRuth", (208, 82), 0, -12, 0.1,
             "12th from last point decreased by a factor of 10"),
    PointFix("C2174", "dXS/dA", (120, 50), 0, 8, 10.0,
             "8th point increased by a factor of 10", scale_uncertainty=False),
)

@dataclass(frozen=True)
class UncertaintyPatch:
    """An uncertainty absent from EXFOR, supplied from the original publication.

    Scoped to a single subentry. The original notebooks index into a per-entry list of
    measurements that spans several targets, so a patch written for one isotope would
    otherwise be applied to every isotope the entry measured -- overwriting perfectly
    good uncertainties elsewhere. `measurement_index` counts within this subentry.
    `point_index` of None patches every point whose uncertainty is missing.
    """

    subentry: str
    quantity: str
    measurement_index: int
    point_index: int | None
    value: float
    note: str

    @property
    def entry(self) -> str:
        return self.subentry[:5]


#: 10817007: 118Sn, "this one looks like it is just missing a data point" -- the
#: original flags (entry 1, measurement 1) of entry 10817, which is subentry 10817007.
#: C0134004: read off Fig. 5 of Phys. Rev. C 31 (1985) 1147, where "the markers used are
#: larger than the error bars for the points with missing error"; set conservatively to
#: about the size of the first reported one.
UNCERTAINTY_PATCHES: tuple[UncertaintyPatch, ...] = (
    UncertaintyPatch("10817007", "dXS/dA", 1, 7, 3.0e-4,
                     "single missing uncertainty supplied by interpolation from its "
                     "neighbours"),
    UncertaintyPatch("C0134004", "dXS/dA", 0, None, 3.0e-5,
                     "missing uncertainties set to the size of the first reported one, "
                     "read from Fig. 5 of Phys. Rev. C 31 (1985) 1147"),
)

#: 144Sm: the two 65 MeV data sets, published by the same author in consecutive years,
#: are the same data at different normalizations. Take the normalization from the later
#: (E0904) and the uncertainties from the earlier (O0032), which E0904 lacks.
UNCERTAINTY_TRANSPLANT = {
    "target": (144, 62),
    "quantity": "dXS/dA",
    "into": "E0904",
    "from": "O0032",
    "note": "the two 65 MeV data sets, published by the same author in consecutive "
            "years, are the same data at different normalizations; the normalization is "
            "taken from the later E0904 and the uncertainties from O0032, which E0904 "
            "does not report",
}

#: Entries reporting lab-frame angles, converted to the CM frame during munging.
LAB_ANGLE_ENTRIES = {"O0090": "Batty et al. report lab-frame angles"}

#: 208Pb (p,n): D0049 (Carlson) reports the analog-state excitation energy differently
#: from modern compilations, so its excitation-energy window is widened.
WIDE_IAS_WINDOW_ENTRIES = {
    "D0049": ("Carlson data are older and report the isobaric analog state excitation "
              "energy differently from modern compilations"),
}
WIDE_IAS_WINDOW = 0.5

#: E1667 carries a duplicate empty measurement ahead of the real one.
MEASUREMENT_DROPS = (("E1667", 0, "duplicate/blank measurement within the entry"),)

#: The floor below which a reported uncertainty is treated as absent, per quantity.
#: Looser for the dimensionless analyzing power than for cross sections.
MIN_STAT_ERR = {"dXS/dA": 1.0e-9, "dXS/dRuth": 1.0e-9, "Ay": 1.0e-3}
