"""Tests for unit homogenisation and the corpus-wide cleaning steps."""

from __future__ import annotations

import numpy as np
import pytest

from nn_corpora import kinematics as kin
from nn_corpora import munge


class FakeMeasurement:
    """A stand-in for exfor_tools' Distribution, carrying only what munging touches."""

    def __init__(self, x, y, err=None, *, quantity="dXS/dA", x_units="CM-degrees",
                 y_units="barns/ster", Einc=65.0, Einc_units="MeV"):
        self.subentry = "X0000002"
        self.quantity = quantity
        self.x = np.asarray(x, dtype=float)
        self.x_err = np.zeros_like(self.x)
        self.y = np.asarray(y, dtype=float)
        self.statistical_err = (np.full_like(self.y, 0.01) if err is None
                                else np.asarray(err, dtype=float))
        self.systematic_norm_err = 0.0
        self.systematic_offset_err = 0.0
        self.rows = len(self.x)
        self.x_units = x_units
        self.y_units = y_units
        self.Einc = Einc
        self.Einc_units = Einc_units
        self.notes = []


class TestUnits:
    @pytest.mark.parametrize("given,expected", [
        ("barns/ster", "b/sr"), ("b/Sr", "b/sr"), ("b/sr", "b/sr"),
    ])
    def test_differential_spellings_normalise(self, given, expected):
        m = FakeMeasurement([30, 60], [1.0, 0.5], y_units=given)
        munge.homogenize_units(m)
        assert m.y_units == expected

    def test_integral_units_normalise(self):
        m = FakeMeasurement([10, 20], [2.0, 1.0], quantity="XS",
                            y_units="barns", x_units="MeV", Einc_units=None)
        munge.homogenize_units(m)
        assert m.y_units == "b"

    def test_wrong_units_for_quantity_are_rejected(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5], quantity="Ay", y_units="barns/ster")
        with pytest.raises(ValueError, match="reported in"):
            munge.homogenize_units(m)

    def test_non_mev_energies_are_rejected(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5], Einc_units="keV")
        with pytest.raises(ValueError, match="not MeV"):
            munge.homogenize_units(m)


class TestPolarizationCrossSection:
    def test_dimensioned_ay_is_recognised(self):
        """EXFOR's POL/DA is the analyzing power only when it is dimensionless."""
        m = FakeMeasurement([30], [1.0], quantity="Ay", y_units="barns/ster")
        assert munge.is_polarization_cross_section(m)

    def test_dimensionless_ay_is_not(self):
        m = FakeMeasurement([30], [0.5], quantity="Ay", y_units="no-dim")
        assert not munge.is_polarization_cross_section(m)


class TestFrames:
    def test_cm_angles_pass_through_unchanged(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5])
        munge.to_cm_degrees(m, (208, 82), (1, 1))
        assert m.notes == []

    def test_lab_angles_are_converted_and_noted(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5], x_units="LAB-degrees")
        munge.to_cm_degrees(m, (208, 82), (1, 1))
        assert m.x_units == "CM-degrees"
        assert np.all(m.x > [30, 60])       # CM angle exceeds lab angle
        assert any("CM frame" in n for n in m.notes)

    def test_unknown_angle_units_are_rejected(self):
        m = FakeMeasurement([30], [1.0], x_units="cos(theta)")
        with pytest.raises(ValueError, match="angle units"):
            munge.to_cm_degrees(m, (208, 82), (1, 1))


class TestRutherfordRatio:
    def test_absolute_becomes_a_ratio(self):
        angles = [30.0, 60.0, 90.0]
        channel = kin.elastic_kinematics((208, 82), (1, 1), 65.0)
        sigma = kin.rutherford_xs_b_per_sr(angles, channel)
        # a data set that is exactly Rutherford must come back as exactly 1
        m = FakeMeasurement(angles, sigma, err=sigma * 0.1)
        munge.to_ratio_to_rutherford(m, (208, 82), (1, 1))
        assert m.quantity == "dXS/dRuth"
        assert m.y_units == "no-dim"
        np.testing.assert_allclose(m.y, 1.0, rtol=1e-12)
        np.testing.assert_allclose(m.statistical_err, 0.1, rtol=1e-12)

    def test_millibarn_input_is_scaled(self):
        angles = [30.0, 60.0]
        channel = kin.elastic_kinematics((90, 40), (1, 1), 40.0)
        sigma_mb = kin.rutherford_xs_mb_per_sr(angles, channel)
        m = FakeMeasurement(angles, sigma_mb, y_units="mb/sr", Einc=40.0)
        munge.to_ratio_to_rutherford(m, (90, 40), (1, 1))
        np.testing.assert_allclose(m.y, 1.0, rtol=1e-12)

    def test_existing_ratio_is_left_alone(self):
        m = FakeMeasurement([30, 60], [0.9, 0.4], quantity="dXS/dRuth", y_units="no-dim")
        munge.to_ratio_to_rutherford(m, (208, 82), (1, 1))
        assert m.notes == []

    def test_forward_angles_are_dropped(self):
        """The Rutherford cross section diverges as the angle goes to zero."""
        m = FakeMeasurement([0.0, 0.5, 30.0, 60.0], [1.0, 1.0, 1.0, 1.0])
        munge.to_ratio_to_rutherford(m, (208, 82), (1, 1))
        assert m.rows == 2
        assert any("diverges" in n for n in m.notes)

    def test_neutral_projectile_is_rejected(self):
        m = FakeMeasurement([30], [1.0])
        with pytest.raises(ValueError, match="neutral projectile"):
            munge.to_ratio_to_rutherford(m, (208, 82), (1, 0))

    def test_lab_angles_must_be_converted_first(self):
        m = FakeMeasurement([30], [1.0], x_units="LAB-degrees")
        with pytest.raises(ValueError, match="CM angles"):
            munge.to_ratio_to_rutherford(m, (208, 82), (1, 1))


class TestEnergyHandling:
    def test_window_trims_and_notes(self):
        m = FakeMeasurement(np.arange(1.0, 11.0), np.ones(10), quantity="XS",
                            x_units="MeV", y_units="barns")
        assert munge.restrict_to_energy_window(m, 3.0, 7.0)
        assert m.rows == 5 and m.x[0] == 3.0 and m.x[-1] == 7.0
        assert any("energy range" in n for n in m.notes)

    def test_window_outside_the_data_returns_false(self):
        m = FakeMeasurement([1.0, 2.0], [1.0, 1.0], quantity="XS", x_units="MeV")
        assert not munge.restrict_to_energy_window(m, 50.0, 60.0)

    def test_downsampling_reaches_one_point_per_mev(self):
        x = np.linspace(1.0, 21.0, 4000)
        m = FakeMeasurement(x, np.ones_like(x), quantity="XS", x_units="MeV")
        munge.downsample_energy(m, max_per_mev=1.0)
        assert m.rows <= 21
        assert any("downsampled" in n for n in m.notes)

    def test_downsampling_keeps_the_endpoints(self):
        x = np.linspace(5.0, 100.0, 2000)
        m = FakeMeasurement(x, np.ones_like(x), quantity="XS", x_units="MeV")
        munge.downsample_energy(m, max_per_mev=1.0)
        assert m.x[0] == pytest.approx(5.0) and m.x[-1] == pytest.approx(100.0)

    def test_downsampling_leaves_sparse_data_alone(self):
        m = FakeMeasurement([1.0, 10.0, 20.0], [1.0, 1.0, 1.0], quantity="XS",
                            x_units="MeV")
        munge.downsample_energy(m, max_per_mev=1.0)
        assert m.rows == 3 and m.notes == []


class TestUncertainties:
    def test_default_norm_err_applied_when_absent(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5])
        munge.apply_default_norm_err(m)
        assert m.systematic_norm_err == munge.DEFAULT_SYSTEMATIC_NORM_ERR
        assert any("default normalisation" in n for n in m.notes)

    def test_reported_norm_err_is_left_alone(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5])
        m.systematic_norm_err = 0.03
        munge.apply_default_norm_err(m)
        assert m.systematic_norm_err == 0.03 and m.notes == []

    def test_zero_uncertainty_is_unusable(self):
        m = FakeMeasurement([30, 60], [1.0, 0.5], err=[0.01, 0.0])
        assert not munge.has_usable_uncertainties(m)

    def test_all_positive_uncertainties_are_usable(self):
        assert munge.has_usable_uncertainties(FakeMeasurement([30, 60], [1.0, 0.5]))


class TestSparsity:
    def test_sparse_distribution_is_flagged(self):
        """Excitation-function data sets unroll into near-empty angular distributions."""
        assert munge.is_too_sparse(FakeMeasurement([30.0], [1.0]), 3)

    def test_dense_distribution_is_not(self):
        m = FakeMeasurement([10.0, 30.0, 60.0, 90.0], [1.0] * 4)
        assert not munge.is_too_sparse(m, 3)


def test_scale_records_its_reason():
    m = FakeMeasurement([30, 60], [1.0, 0.5], err=[0.1, 0.05])
    munge.scale(m, 1000.0, "units mismatch in EXFOR")
    np.testing.assert_allclose(m.y, [1000.0, 500.0])
    np.testing.assert_allclose(m.statistical_err, [100.0, 50.0])
    assert "units mismatch in EXFOR" in m.notes[0]
