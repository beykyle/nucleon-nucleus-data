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


class EntryUnavailable(LookupError):
    """An entry the corpus asks for cannot be read from the x4i3 database.

    Usually because x4i3's index build rejected it: nine of the entries these corpora
    cite (O0162, 10791, O0741, O0150, O0475, O0732, O0436, O1948 and O0479) are present
    in EXFOR as .x4 files but raise BrokenNumberError when parsed, on malformed numeric
    fields, and so never reach the index. This affects the 2024 and 2025 databases
    alike, so it is a parser limitation rather than a change in EXFOR.
    """


@functools.lru_cache(maxsize=512)
def entry_data_sets(entry: str) -> dict:
    """All data sets of one EXFOR entry, cached.

    Retrieval parses the entry from disk and is by far the dominant cost of curation;
    one entry commonly supplies dozens of the subentries a corpus asks for.
    """
    try:
        entry_data = __EXFOR_DB__.retrieve(ENTRY=entry)[entry]
    except KeyError as exc:
        raise EntryUnavailable(
            f"entry {entry} is not in the x4i3 index; it is most likely one of the "
            "entries x4i3 fails to parse"
        ) from exc
    return dict(entry_data.getDataSets())


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


def subentry_target(entry: str, subentry: str, pointer: str = "") -> tuple[int, int] | None:
    """The target EXFOR currently assigns to a subentry, as ``(A, Z)``.

    EXFOR revises target assignments between releases -- a data set the supplement
    tabulates under 40Ca may now be listed under natCa, and vice versa. Since both the
    mass and the asymmetry (N-Z)/A enter an optical potential, the target must be taken
    from EXFOR rather than assumed, which is also what the supplement's authors did when
    they found such discrepancies. ``A = 0`` denotes a natural-abundance target.
    """
    try:
        blocks = data_sets_for(entry, subentry, pointer)
    except EntryUnavailable:
        return None
    for data_set in blocks.values():
        reaction = data_set.reaction[0]
        if not hasattr(reaction, "targ"):
            continue
        A, Z = reaction.targ.getA(), reaction.targ.getZ()
        return (0, Z) if A == -3000 else (A, Z)
    return None


def resolve(subentry: str, labels) -> ErrorAssignment:
    """Choose the overall uncertainty column(s) for one subentry."""
    candidates = candidate_labels(labels)

    if not candidates:
        return ErrorAssignment(
            subentry, list(labels), [], "independent", rule="no-uncertainty",
            resolved=False, reason="subentry reports no uncertainty on the observable",
        )

    for group, treatment in PREFERENCE:
        if all(label in candidates for label in group):
            # A label repeated in one subentry denotes partial uncertainties split
            # across columns -- typically one in per-cent and one absolute, each mostly
            # null. The CHUQ notes for the Mellema (n,n) data sets direct that these be
            # merged into a single absolute column; since nulls parse as zero, summing
            # them in quadrature is exactly that merge.
            chosen = [label for label in candidates if label in group]
            repeated = len(chosen) > len(group)
            return ErrorAssignment(
                subentry, list(labels), chosen,
                "independent" if repeated else treatment,
                rule=f"preference:{'+'.join(group)}" + (":merged" if repeated else ""),
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


def resolve_entry(entry: str) -> ErrorAssignment:
    """Resolve the overall uncertainty from an entry's most common column layout.

    Used when the subentry the supplement tabulates is no longer in EXFOR but the entry
    is, so that retrieval can still run and substitute a renumbered subentry. Subentries
    of one entry come from one measurement campaign and normally share a layout.
    """
    try:
        blocks = entry_data_sets(entry)
    except EntryUnavailable as exc:
        return ErrorAssignment(
            entry, [], [], "independent", rule="entry-unavailable",
            resolved=False, reason=str(exc),
        )

    counts: dict[tuple, int] = {}
    for data_set in blocks.values():
        counts[tuple(data_set.labels)] = counts.get(tuple(data_set.labels), 0) + 1
    if not counts:
        return ErrorAssignment(
            entry, [], [], "independent", rule="missing", resolved=False,
            reason=f"entry {entry} contains no data sets",
        )
    labels = max(counts, key=counts.get)
    assignment = resolve(entry, labels)
    return assignment


def resolve_subentry(entry: str, subentry: str, pointer: str = "") -> ErrorAssignment:
    """Resolve the overall uncertainty for a subentry, reading its labels from EXFOR."""
    try:
        blocks = data_sets_for(entry, subentry, pointer)
    except EntryUnavailable as exc:
        return ErrorAssignment(
            subentry, [], [], "independent", rule="entry-unavailable",
            resolved=False, reason=str(exc),
        )
    if not blocks:
        return ErrorAssignment(
            subentry, [], [], "independent", rule="missing",
            resolved=False, reason=f"subentry {subentry} not present in the database",
        )
    # Blocks of one subentry share their column layout; take the first.
    return resolve(subentry, next(iter(blocks.values())).labels)
