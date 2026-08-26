"""Tests for the inspection plots and the ELM corrections they are meant to expose.

Outliers in these corpora are found by eye, so a data set that is never drawn is a data
set whose outliers are never found. These tests pin the two properties that guarantee
the plots are a complete view: every measurement is plotted, and every correction lands
on the one data set it was written for.
"""

from __future__ import annotations

import numpy as np
import pytest

from nn_corpora import elm, elm_curate, plotting


class FakeMeasurement:
    def __init__(self, subentry, target, *, quantity="dXS/dA", n=5, err=1.0):
        self.subentry = subentry
        self.quantity = quantity
        self.target = target
        self.x = np.linspace(20.0, 160.0, n)
        self.x_err = np.zeros(n)
        self.y = np.ones(n)
        self.statistical_err = np.full(n, err)
        self.systematic_norm_err = 0.0
        self.rows = n
        self.x_units = "CM-degrees"
        self.y_units = "b/sr"
        self.Einc = 24.0
        self.Einc_units = "MeV"
        self.notes = []


class FakeEntry:
    def __init__(self, measurements):
        self.measurements = list(measurements)


class FakeReactionData:
    def __init__(self, entries):
        self.entries = dict(entries)


class FakeMulti:
    def __init__(self, data):
        self.data = dict(data)


class TestTargetLabel:
    def test_isotope(self):
        assert plotting.target_latex((208, 82)) == r"$^{208}$Pb"

    def test_natural_target(self):
        assert plotting.target_latex((0, 26)) == r"$^{\rm nat}$Fe"


class TestUncertaintyPatchScope:
    """Entry 10817 measures five Sn isotopes; the patch belongs to 118Sn alone.

    Keyed by entry rather than subentry, it would overwrite a perfectly good
    uncertainty on every other isotope the entry measured.
    """

    def _data(self):
        return {
            (116, 50): FakeMulti({"dXS/dA": FakeReactionData({
                "10817": FakeEntry([FakeMeasurement("10817006", (116, 50), n=25),
                                    FakeMeasurement("10817006", (116, 50), n=25)])})}),
            (118, 50): FakeMulti({"dXS/dA": FakeReactionData({
                "10817": FakeEntry([FakeMeasurement("10817007", (118, 50), n=25),
                                    FakeMeasurement("10817007", (118, 50), n=25)])})}),
        }

    def test_only_the_named_subentry_is_patched(self):
        data = self._data()
        result = elm_curate.ElmSectorResult(sector="elastic_diff_xs")
        elm_curate.apply_uncertainty_patches(data, result)

        patched = data[(118, 50)].data["dXS/dA"].entries["10817"].measurements[1]
        assert patched.statistical_err[7] == pytest.approx(3.0e-4)
        assert np.all(np.delete(patched.statistical_err, 7) == 1.0)

        for m in data[(116, 50)].data["dXS/dA"].entries["10817"].measurements:
            assert np.all(m.statistical_err == 1.0), "116Sn must not be touched"
            assert m.notes == []

    def test_index_counts_within_the_subentry(self):
        data = self._data()
        result = elm_curate.ElmSectorResult(sector="elastic_diff_xs")
        elm_curate.apply_uncertainty_patches(data, result)

        measurements = data[(118, 50)].data["dXS/dA"].entries["10817"].measurements
        assert measurements[0].notes == [], "the first measurement is not the patched one"
        assert measurements[1].notes != []

    def test_every_patch_names_a_subentry_not_an_entry(self):
        for patch in elm.UNCERTAINTY_PATCHES:
            assert len(patch.subentry) == 8, patch
            assert patch.entry == patch.subentry[:5]


class TestPlotMulti:
    def test_counts_every_measurement(self):
        data = {
            (40, 20): FakeMulti({"dXS/dA": FakeReactionData({
                "A0001": FakeEntry([FakeMeasurement("A0001002", (40, 20))])})}),
            (208, 82): FakeMulti({"dXS/dA": FakeReactionData({
                "A0002": FakeEntry([FakeMeasurement("A0002002", (208, 82)),
                                    FakeMeasurement("A0002003", (208, 82))])})}),
        }
        assert plotting.plot_multi(data, label="(n,n)") == 3

    def test_a_quantity_filter_still_counts_what_it_draws(self):
        data = {
            (40, 20): FakeMulti({
                "dXS/dA": FakeReactionData({
                    "A0001": FakeEntry([FakeMeasurement("A0001002", (40, 20))])}),
                "Ay": FakeReactionData({
                    "A0001": FakeEntry([FakeMeasurement("A0001003", (40, 20),
                                                        quantity="Ay")])}),
            }),
        }
        assert plotting.plot_multi(data, quantities=("Ay",)) == 1

    def test_empty_input(self):
        assert plotting.plot_multi({}) == 0


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    from matplotlib import pyplot as plt

    plt.close("all")
