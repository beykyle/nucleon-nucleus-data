"""Assign an overall experimental uncertainty to each EXFOR data set.

EXFOR data sets frequently carry several uncertainty columns -- statistical,
systematic, digitisation, monitor normalisation -- with no machine-readable statement
of how they relate. ``exfor_tools`` refuses to guess and raises
``ValueError("Ambiguous statistical error labels: ...")``, which the ELM notebooks
resolve by hand, one entry at a time.

The supplement states a rule instead (Supplemental Material B, p.1):

    Many EXFOR-based data list more than one type of error, for instance,
    digitization error, statistical error, etc. For a given datum, we assigned the
    overall error according to the following list of EXFOR error labels in order of
    preference: ERR-T (total error), (+DATA-ERR + -DATA-ERR)/2 (average of positive
    and negative error), ERR-S (statistical error), ERR-DIG (digitization error),
    ERR-SYS (systematic error).

That rule is implemented here, so the corpora are assembled reproducibly rather than
by case-by-case adjudication. Data sets it cannot resolve are reported and handled
explicitly in ``overrides.py``.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

from exfor_tools.db import __EXFOR_DB__

# exfor_tools treats every label containing "ERR" as a candidate uncertainty column
# for the observable, except those qualifying the independent variables. Mirrored
# here so the resolver sees exactly the labels the parser will categorise.
# See AngularDistribution.parse_subentry in exfor_tools/distribution.py.
INDEPENDENT_VARIABLE_FRAGMENTS = ("ANG", "EN", "E-LVL", "E-EXC")

# The supplement's order of preference, most preferred first. DATA-ERR is not named
# in the supplement -- it is the single unlabelled uncertainty column and needs no
# adjudication when it stands alone -- but it must be ranked to break ties when it
# appears alongside ERR-S or ERR-DIG. It sits directly below the explicit total
# errors and above the partial ones, since it denotes an overall uncertainty.
PREFERENCE: tuple[tuple[tuple[str, ...], str], ...] = (
    (("ERR-T",), "independent"),
    (("+ERR-T", "-ERR-T"), "average"),
    (("+DATA-ERR", "-DATA-ERR"), "average"),
    (("DATA-ERR",), "independent"),
    (("ERR-S",), "independent"),
    (("ERR-DIG",), "independent"),
    (("ERR-SYS",), "independent"),
)

# Partial uncertainties split across numbered columns. The CHUQ notes direct that
# these be summed in quadrature -- e.g. for the Ferrer (n,n) data sets, "we converted
# the percent error to absolute units and summed both sources of partial error in
# quadrature to yield an overall error". exfor_tools converts percent columns to
# absolute during parsing, so quadrature is all that remains here.
NUMBERED_DATA_ERR = tuple(f"DATA-ERR{i}" for i in range(1, 10))


@dataclass
class ErrorAssignment:
    """How one subentry's overall uncertainty was chosen."""

    subentry: str
    labels: list[str]
    chosen: list[str]
    treatment: str
    rule: str
    resolved: bool = True
    reason: str = ""

    @property
    def parsing_kwargs(self) -> dict:
        """Keyword arguments for ``ExforEntry(parsing_kwargs=...)``.

        ``systematic_err_labels`` is deliberately empty: the supplement assigns a
        single overall uncertainty per datum, and the residual correlated component is
        supplied as a default normalisation uncertainty during munging.
        """
        return {
            "statistical_err_labels": list(self.chosen),
            "statistical_err_treatment": self.treatment,
            "systematic_err_labels": [],
        }


def candidate_labels(labels) -> list[str]:
    """The uncertainty columns that describe the observable, in EXFOR order."""
    return [
        label for label in labels
        if "ERR" in label
        and not any(frag in label for frag in INDEPENDENT_VARIABLE_FRAGMENTS)
    ]


@functools.lru_cache(maxsize=512)
def entry_data_sets(entry: str) -> dict:
    """All data sets of one EXFOR entry, cached.

    Retrieval parses the entry from disk and is by far the dominant cost of curation;
    one entry commonly supplies dozens of the subentries a corpus asks for.
    """
    return dict(__EXFOR_DB__.retrieve(ENTRY=entry)[entry].getDataSets())


def data_sets_for(entry: str, subentry: str, pointer: str = ""):
    """Return the x4i3 data sets for one subentry, preferring the requested pointer.

    The pointer selects one data block within a subentry -- e.g. O0032002 holds the
    cross section under pointer "S" and the analyzing power under "A". Pointers are
    not stable across EXFOR releases (O0208006 carried pointers 1 and 2 when the
    supplement was written but carries none in the 2025 database), so a requested
    pointer that no longer exists falls back to every block of the subentry, leaving
    the quantity match to disambiguate.
    """
    blocks = {key: ds for key, ds in entry_data_sets(entry).items() if key[1] == subentry}
    if pointer:
        exact = {k: ds for k, ds in blocks.items() if k[2].strip() == pointer}
        if exact:
            return exact
    return blocks


def resolve(subentry: str, labels) -> ErrorAssignment:
    """Choose the overall uncertainty column(s) for one subentry."""
    candidates = candidate_labels(labels)

    if not candidates:
        return ErrorAssignment(
            subentry, list(labels), [], "independent", rule="no-uncertainty",
            resolved=False, reason="subentry reports no uncertainty on the observable",
        )

    duplicates = {c for c in candidates if candidates.count(c) > 1}
    if duplicates:
        # exfor_tools raises "Expected only one <label> column" before categorisation
        # is ever reached, so no choice of labels can rescue these.
        return ErrorAssignment(
            subentry, list(labels), [], "independent", rule="duplicate-columns",
            resolved=False,
            reason=f"repeated uncertainty column(s) {sorted(duplicates)}",
        )

    for group, treatment in PREFERENCE:
        if all(label in candidates for label in group):
            return ErrorAssignment(
                subentry, list(labels), list(group), treatment,
                rule=f"preference:{'+'.join(group)}",
            )

    numbered = [label for label in NUMBERED_DATA_ERR if label in candidates]
    if numbered:
        return ErrorAssignment(
            subentry, list(labels), numbered, "independent", rule="quadrature:DATA-ERRn",
        )

    return ErrorAssignment(
        subentry, list(labels), [], "independent", rule="unrecognised",
        resolved=False,
        reason=f"no preferred uncertainty column among {candidates}",
    )


def resolve_subentry(entry: str, subentry: str, pointer: str = "") -> ErrorAssignment:
    """Resolve the overall uncertainty for a subentry, reading its labels from EXFOR."""
    blocks = data_sets_for(entry, subentry, pointer)
    if not blocks:
        return ErrorAssignment(
            subentry, [], [], "independent", rule="missing",
            resolved=False, reason=f"subentry {subentry} not present in the database",
        )
    # Blocks of one subentry share their column layout; take the first.
    return resolve(subentry, next(iter(blocks.values())).labels)
