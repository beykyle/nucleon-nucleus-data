"""Corrections the supplement documents in prose, encoded as data.

Each entry cites the Comments section of ``supplement_experimentalCorpora.pdf`` that
motivates it, or -- where the supplement is silent and the data still cannot be parsed
-- records the judgement made here and why.

Target reassignments the supplement describes (28Si data actually from natSi, 120Sn
from natSn, and so on) need no code: the tables already list the corrected target, and
``spec/*.csv`` transcribes them as tabulated.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Override:
    """A documented correction to one entry or subentry of one corpus-sector."""

    reason: str
    parsing_kwargs: dict | None = None
    scale_by: float | None = None
    drop: bool = False


def _key(corpus: str, sector: str, subentry_or_entry: str) -> tuple[str, str, str]:
    return (corpus, sector, subentry_or_entry)


#: (corpus, sector, subentry-or-entry) -> Override
OVERRIDES: dict[tuple[str, str, str], Override] = {}


def _register(corpora, sectors, targets, override: Override) -> None:
    for corpus in corpora:
        for sector in sectors:
            for target in targets:
                OVERRIDES[_key(corpus, sector, target)] = override


# ---------------------------------------------------------------------------
# Uncertainty columns the supplement's preference rule cannot resolve
# ---------------------------------------------------------------------------

# O0208 (Fricke et al.) reports ERR-1 and ERR-2 with no standard label. The ELM
# notebooks, working from the entry's ERR-ANALYS text, take ERR-2 as the per-point
# uncertainty and ERR-1 as a correlated normalisation term. The same reading is used
# here; since this repo assigns a single overall uncertainty per datum, ERR-2 is taken
# as that uncertainty and ERR-1 is left to the default normalisation treatment.
_register(
    ("kduq", "chuq"),
    ("proton_elastic", "proton_ay"),
    ("O0208",),
    Override(
        reason="ERR-1/ERR-2 carry no standard EXFOR meaning; ERR-2 is the per-point "
               "uncertainty and ERR-1 a correlated normalisation term, per the entry's "
               "ERR-ANALYS text",
        parsing_kwargs={
            "statistical_err_labels": ["ERR-2"],
            "statistical_err_treatment": "independent",
            "systematic_err_labels": [],
        },
    ),
)

# The CHUQ notes for the Fricke et al. data sets: "as listed in EXFOR, the data sets
# for these nuclei ... have mostly null values in the ERR-T column. It was unclear to
# us how to combine or assess the few given ERR-T data with the error data in the other
# provided error columns. As such, we ignored the ERR-T column in these cases and took
# the DATA-ERR column for the total error."
_register(
    ("chuq",),
    ("proton_elastic", "proton_ay"),
    ("O0393", "O0389", "O0436"),
    Override(
        reason="ERR-T is mostly null for the Fricke data sets; the CHUQ notes direct "
               "that it be ignored in favour of DATA-ERR",
        parsing_kwargs={
            "statistical_err_labels": ["DATA-ERR"],
            "statistical_err_treatment": "independent",
            "systematic_err_labels": [],
        },
    ),
)

# The CHUQ notes for 118Sn: "For the data sets at 11 and 24 MeV Rapaport et al. ...
# a 'null' value was listed in the DATA-ERR column; we elected to use the following
# column ERR-T, which listed a 5% relative uncertainty for all data points."
# This is already what the preference rule does, since ERR-T outranks DATA-ERR; the
# entry is recorded so the provenance is explicit rather than incidental.
_register(
    ("chuq",),
    ("neutron_elastic",),
    ("10817",),
    Override(
        reason="DATA-ERR is null for the Rapaport 118Sn data sets; the CHUQ notes "
               "direct that ERR-T be used instead",
        parsing_kwargs={
            "statistical_err_labels": ["ERR-T"],
            "statistical_err_treatment": "independent",
            "systematic_err_labels": [],
        },
    ),
)

# ---------------------------------------------------------------------------
# Transcription errors the supplement documents
# ---------------------------------------------------------------------------

# Test corpus, 54Fe: "We reduced the cross section values and reported errors of
# J. R. Vanhoy et al. (Nucl. Phys. A 972 (2018) 107) by a factor of 1000; the data as
# listed in EXFOR appear to be 1000 too small, possible due to a units mismatch."
_register(
    ("test",),
    ("neutron_elastic",),
    ("14570",),
    Override(
        reason="Vanhoy et al. 54Fe data are a factor of 1000 too small in EXFOR, "
               "apparently a units mismatch (Test corpus Comments)",
        scale_by=1000.0,
    ),
)

# Test corpus, 64Zn: "We reduced the cross section values and reported errors of
# K. G. Leach et al. (Phys. Rev. C 100 (2019) 014320) by a factor of 1000; the data as
# listed in EXFOR appear to be a factor of 1000 too large, possibly due to a units
# mismatch."
_register(
    ("test",),
    ("proton_elastic",),
    ("C2382",),
    Override(
        reason="Leach et al. 64Zn data are a factor of 1000 too large in EXFOR, "
               "apparently a units mismatch (Test corpus Comments)",
        scale_by=1e-3,
    ),
)


def for_sector(corpus: str, sector: str) -> dict[str, Override]:
    """All overrides registered for one corpus-sector, keyed by entry or subentry."""
    return {k[2]: v for k, v in OVERRIDES.items() if k[0] == corpus and k[1] == sector}
