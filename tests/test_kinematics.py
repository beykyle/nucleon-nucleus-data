"""Tests for the kinematics ported from jitr.

The critical property is agreement with jitr: this repo divides charged-projectile
elastic cross sections by a Rutherford cross section computed here, while rxmc
multiplies model predictions by one computed in jitr. Any disagreement would show up
as a spurious normalisation offset in every proton elastic data set.
"""

from __future__ import annotations

import numpy as np
import pytest

from nn_corpora import kinematics as kin

jitr = pytest.importorskip("jitr", reason="jitr not installed; cross-check skipped")

from jitr.utils import constants as jitr_constants  # noqa: E402
from jitr.utils import kinematics as jitr_kinematics  # noqa: E402
from jitr.utils import mass as jitr_mass  # noqa: E402

TARGETS = [(40, 20), (48, 20), (90, 40), (120, 50), (208, 82)]
ENERGIES = [10.0, 30.0, 65.0, 100.0, 200.0]
ANGLES = np.array([5.0, 15.0, 30.0, 60.0, 90.0, 120.0, 170.0])


def test_constants_match_jitr():
    assert kin.HBARC == jitr_constants.HBARC
    assert kin.ALPHA == jitr_constants.ALPHA
    assert kin.AMU == jitr_constants.AMU
    assert kin.MASS_N == jitr_constants.MASS_N
    assert kin.MASS_P == jitr_constants.MASS_P


@pytest.mark.parametrize("target", TARGETS)
def test_masses_match_jitr(target):
    """periodictable atomic masses reproduce jitr's AME2020 nuclear masses.

    They are not the same table, so agreement is only expected to the level of
    electron binding energies -- a relative tolerance of 1e-6 is ~50 keV at A=208.
    """
    A, Z = target
    assert kin.nuclear_mass(A, Z) == pytest.approx(jitr_mass.mass(A, Z)[0], rel=1e-6)


def test_natural_target_mass_is_between_isotopes():
    """A = 0 denotes a natural target; its mass must lie within the isotopic range."""
    assert kin.nuclear_mass(54, 26) < kin.nuclear_mass(0, 26) < kin.nuclear_mass(58, 26)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("Elab", ENERGIES)
def test_kinematics_match_jitr(target, Elab):
    A, Z = target
    m_t, m_p = jitr_mass.mass(A, Z)[0], jitr_constants.MASS_P
    expected = jitr_kinematics.semi_relativistic_kinematics(m_t, m_p, Elab, Zz=Z)
    got = kin.semi_relativistic_kinematics(m_t, m_p, Elab, Zz=Z)

    assert got.Ecm == pytest.approx(expected.Ecm, rel=1e-12)
    assert got.mu == pytest.approx(expected.mu, rel=1e-12)
    assert got.k == pytest.approx(expected.k, rel=1e-12)
    assert got.eta == pytest.approx(expected.eta, rel=1e-12)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("Elab", ENERGIES)
def test_rutherford_matches_jitr(target, Elab):
    A, Z = target
    m_t, m_p = jitr_mass.mass(A, Z)[0], jitr_constants.MASS_P
    jk = jitr_kinematics.semi_relativistic_kinematics(m_t, m_p, Elab, Zz=Z)

    expected = 10 * jk.eta**2 / (4 * jk.k**2 * np.sin(np.deg2rad(ANGLES) / 2) ** 4)
    got = kin.rutherford_xs_mb_per_sr(ANGLES, kin.semi_relativistic_kinematics(
        m_t, m_p, Elab, Zz=Z))

    np.testing.assert_allclose(got, expected, rtol=1e-12)


def test_neutron_rutherford_vanishes():
    k = kin.elastic_kinematics((208, 82), (1, 0), 20.0)
    assert k.eta == 0.0
    np.testing.assert_allclose(kin.rutherford_xs_mb_per_sr(ANGLES, k), 0.0)


@pytest.mark.parametrize("angle", [0.0, 180.0, -5.0, 200.0])
def test_rutherford_rejects_endpoints(angle):
    k = kin.elastic_kinematics((208, 82), (1, 1), 65.0)
    with pytest.raises(ValueError):
        kin.rutherford_xs_mb_per_sr([angle], k)


def test_unit_conversion_consistent():
    k = kin.elastic_kinematics((90, 40), (1, 1), 40.0)
    np.testing.assert_allclose(
        kin.rutherford_xs_mb_per_sr(ANGLES, k),
        kin.rutherford_xs_b_per_sr(ANGLES, k) * kin.MB_PER_BARN,
        rtol=1e-14,
    )


@pytest.mark.parametrize("target", TARGETS)
def test_lab_to_cm_inverts_the_forward_relation(target):
    """theta_cm must satisfy tan(theta_lab) = sin(theta_cm) / (cos(theta_cm) + tau).

    Compared in cross-multiplied form, which stays finite at theta_lab = 90 degrees
    where the tangent diverges.
    """
    projectile = (1, 1)
    tau = kin.nuclear_mass(*projectile) / kin.nuclear_mass(*target)
    lab = np.deg2rad(np.array([1.0, 10.0, 45.0, 90.0, 135.0, 179.0]))
    cm = np.deg2rad(kin.lab_to_cm_angle_elastic(np.rad2deg(lab), target, projectile))

    np.testing.assert_allclose(
        np.sin(lab) * (np.cos(cm) + tau), np.cos(lab) * np.sin(cm), atol=1e-12
    )


def test_lab_to_cm_is_monotonic_and_bounded():
    lab = np.linspace(0.5, 179.5, 200)
    cm = kin.lab_to_cm_angle_elastic(lab, (40, 20), (1, 0))
    assert np.all(np.diff(cm) > 0)
    assert cm[0] > lab[0] and cm[-1] <= 180.0


def test_lab_to_cm_equal_masses_rejected():
    with pytest.raises(ValueError):
        kin.lab_to_cm_angle_elastic([30.0], (1, 1), (1, 1))
