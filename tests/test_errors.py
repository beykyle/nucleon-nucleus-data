"""Tests for the overall-uncertainty resolver.

The supplement's preference rule is the reason this repo can assemble the KDUQ, CHUQ
and Test corpora without hand-adjudicating every data set, so it is tested directly
on synthetic label sets and on real subentries.
"""

from __future__ import annotations

import pytest

from nn_corpora import errors


class TestCandidateLabels:
    def test_keeps_observable_uncertainties(self):
        labels = ["EN", "ANG-CM", "DATA-CM", "ERR-T", "ERR-1"]
        assert errors.candidate_labels(labels) == ["ERR-T", "ERR-1"]

    @pytest.mark.parametrize("label", ["EN-ERR", "ANG-ERR", "E-LVL-ERR", "E-EXC-ERR"])
    def test_drops_independent_variable_uncertainties(self, label):
        """These qualify the energy or angle, not the observable."""
        assert errors.candidate_labels(["DATA", label, "DATA-ERR"]) == ["DATA-ERR"]

    def test_keeps_monitor_and_beam_uncertainties(self):
        """MONIT-ERR and POL-BM-ERR reach the parser, so the resolver must rank them."""
        assert errors.candidate_labels(["DATA-ERR1", "MONIT-ERR", "POL-BM-ERR"]) == [
            "DATA-ERR1", "MONIT-ERR", "POL-BM-ERR",
        ]


class TestPreferenceOrder:
    def test_err_t_wins_over_partial_errors(self):
        """The case that motivates the rule: 30463008, the first KDUQ row."""
        a = errors.resolve("30463008", ["ERR-1", "ERR-2", "ERR-3", "EN", "EN-ERR",
                                        "ANG-CM", "DATA-CM", "ERR-T"])
        assert a.resolved
        assert a.chosen == ["ERR-T"]
        assert a.treatment == "independent"

    @pytest.mark.parametrize(
        "labels,expected",
        [
            (["ERR-T", "DATA-ERR", "ERR-S", "ERR-DIG", "ERR-SYS"], ["ERR-T"]),
            (["DATA-ERR", "ERR-S", "ERR-DIG", "ERR-SYS"], ["DATA-ERR"]),
            (["ERR-S", "ERR-DIG", "ERR-SYS"], ["ERR-S"]),
            (["ERR-DIG", "ERR-SYS"], ["ERR-DIG"]),
            (["ERR-SYS"], ["ERR-SYS"]),
        ],
    )
    def test_full_preference_chain(self, labels, expected):
        assert errors.resolve("X", labels).chosen == expected

    def test_asymmetric_pair_is_averaged(self):
        """(+DATA-ERR + -DATA-ERR)/2, per the supplement."""
        a = errors.resolve("X", ["+DATA-ERR", "-DATA-ERR"])
        assert a.chosen == ["+DATA-ERR", "-DATA-ERR"]
        assert a.treatment == "average"

    def test_asymmetric_pair_loses_to_err_t(self):
        a = errors.resolve("X", ["+DATA-ERR", "-DATA-ERR", "ERR-T"])
        assert a.chosen == ["ERR-T"]

    def test_lone_asymmetric_column_is_not_averaged(self):
        """A "+DATA-ERR" with no partner is not the supplement's averaging case."""
        a = errors.resolve("X", ["+DATA-ERR", "ERR-S"])
        assert a.chosen == ["ERR-S"]

    def test_numbered_partial_errors_combine_in_quadrature(self):
        """The CHUQ treatment of the Ferrer (n,n) data sets."""
        a = errors.resolve("X", ["DATA-ERR1", "DATA-ERR2", "MONIT-ERR"])
        assert a.chosen == ["DATA-ERR1", "DATA-ERR2"]
        assert a.treatment == "independent"
        assert a.rule == "quadrature:DATA-ERRn"

    def test_numbered_partials_lose_to_named_total(self):
        a = errors.resolve("X", ["DATA-ERR1", "DATA-ERR2", "ERR-T"])
        assert a.chosen == ["ERR-T"]


class TestUnresolved:
    def test_no_uncertainty_column(self):
        a = errors.resolve("X", ["EN", "ANG-CM", "DATA-CM"])
        assert not a.resolved and a.rule == "no-uncertainty"

    def test_unrecognised_partial_errors(self):
        """ERR-1/ERR-2 carry no standard meaning; these need an explicit override."""
        a = errors.resolve("X", ["ERR-1", "ERR-2"])
        assert not a.resolved and a.rule == "unrecognised"

    def test_unresolved_assignment_selects_nothing(self):
        a = errors.resolve("X", ["ERR-1", "ERR-2"])
        assert a.parsing_kwargs["statistical_err_labels"] == []


class TestRepeatedColumns:
    """A repeated label means partial uncertainties split across columns.

    The CHUQ notes for the Mellema (n,n) data sets: "the first and second DATA-ERR
    columns listed errors in percent and in absolute units, respectively. The first
    column contained mostly 'null' values ... we converted the percent errors that did
    exist in the first DATA-ERR column into absolute units, then merged the two columns
    into one absolute DATA-ERR column." Nulls parse as zero, so quadrature is that merge.
    """

    def test_both_occurrences_are_taken(self):
        a = errors.resolve("X", ["DATA-ERR", "DATA-ERR"])
        assert a.resolved
        assert a.chosen == ["DATA-ERR", "DATA-ERR"]
        assert a.treatment == "independent"
        assert a.rule.endswith(":merged")

    def test_unrepeated_label_is_not_marked_merged(self):
        assert not errors.resolve("X", ["DATA-ERR"]).rule.endswith(":merged")

    def test_repeat_does_not_override_preference(self):
        a = errors.resolve("X", ["DATA-ERR", "DATA-ERR", "ERR-T"])
        assert a.chosen == ["ERR-T"]


def test_parsing_kwargs_shape():
    """systematic_err_labels is empty by design: one overall uncertainty per datum."""
    kwargs = errors.resolve("X", ["ERR-T", "ERR-SYS"]).parsing_kwargs
    assert kwargs == {
        "statistical_err_labels": ["ERR-T"],
        "statistical_err_treatment": "independent",
        "systematic_err_labels": [],
    }


@pytest.mark.slow
class TestAgainstDatabase:
    @pytest.mark.parametrize(
        "entry,subentry,pointer,chosen",
        [
            ("30463", "30463008", "", ["ERR-T"]),
            ("O0032", "O0032002", "S", ["ERR-S"]),
            ("13753", "13753010", "", ["ERR-S"]),
            ("D0314", "D0314002", "", ["DATA-ERR"]),
        ],
    )
    def test_real_subentries(self, entry, subentry, pointer, chosen):
        assert errors.resolve_subentry(entry, subentry, pointer).chosen == chosen

    def test_pointer_selects_a_block(self):
        """O0032002 carries the cross section under S and the analyzing power under A."""
        for pointer in ("S", "A"):
            blocks = errors.data_sets_for("O0032", "O0032002", pointer)
            assert {k[2].strip() for k in blocks} == {pointer}

    def test_absent_pointer_falls_back_to_all_blocks(self):
        """O0208006 carried pointers 1 and 2 in the supplement, but none in 2025."""
        blocks = errors.data_sets_for("O0208", "O0208006", "1")
        assert blocks and {k[2].strip() for k in blocks} == {""}

    def test_missing_subentry_is_reported_not_raised(self):
        a = errors.resolve_subentry("13585", "13585002", "")
        assert not a.resolved and a.rule == "missing"
