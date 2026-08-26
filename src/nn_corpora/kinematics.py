"""Relativistic kinematics and the Rutherford cross section.

Ported from ``jitr`` (``jitr.utils.kinematics.semi_relativistic_kinematics`` and
``jitr.xs.elastic.ElasticXS.rutherford_xs``) so that curation does not depend on the
modelling stack. Keeping the two in step matters: this repo stores charged-projectile
elastic data as a ratio to Rutherford, and ``rxmc`` divides model cross sections by
its own Rutherford cross section when comparing against them.

``tests/test_kinematics.py`` checks agreement with ``jitr`` directly, where it is
importable.

Masses come from ``periodictable``, whose isotope masses are the experimental atomic
masses; the electron rest masses are subtracted to give nuclear masses. Natural
abundance targets, which EXFOR denotes ``A = 0`` and which the KDUQ and CHUQ corpora
use heavily, take the abundance-weighted atomic mass.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from periodictable import elements

# CODATA / PDG values, matching jitr.utils.constants
HBARC = 197.3269804  # MeV fm
ALPHA = 1.0 / 137.0359991
AMU = 931.494102  # MeV / c^2
MASS_E = 0.51099895  # MeV / c^2
MASS_N = 1.008665 * AMU
MASS_P = 1.007276 * AMU

# barns/sr -> mb/sr, and back
MB_PER_BARN = 1000.0


@dataclass(frozen=True)
class ChannelKinematics:
    """CM energy, reduced mass, wavenumber and Sommerfeld parameter of a channel."""

    Elab: float
    Ecm: float
    mu: float
    k: float
    eta: float


def nuclear_mass(A: int, Z: int) -> float:
    """Nuclear rest mass in MeV/c^2.

    ``A = 0`` denotes a natural-abundance target and returns the abundance-weighted
    mass, which is what a natural target's kinematics are governed by to the accuracy
    relevant here.
    """
    if (A, Z) == (1, 0):
        return MASS_N
    if (A, Z) == (1, 1):
        return MASS_P

    element = elements[Z]
    if A == 0:
        atomic_mass_u = element.mass
    else:
        try:
            atomic_mass_u = element[A].mass
        except KeyError as exc:
            raise ValueError(f"no mass tabulated for A={A}, Z={Z}") from exc
        if atomic_mass_u is None:
            raise ValueError(f"no mass tabulated for A={A}, Z={Z}")

    return atomic_mass_u * AMU - Z * MASS_E


def semi_relativistic_kinematics(
    mass_target: float, mass_projectile: float, Elab: float, Zz: float = 0
) -> ChannelKinematics:
    """CM kinetic energy and wavenumber in the relativistic approximation.

    Follows Ingemarsson (1974), https://doi.org/10.1088/0031-8949/9/3/004.

    Args:
        mass_target: target rest mass [MeV]
        mass_projectile: projectile rest mass [MeV]
        Elab: incident kinetic energy in the lab frame [MeV]
        Zz: product of the charges of the two nuclei
    """
    m_t, m_p = mass_target, mass_projectile

    Ecm = m_t / (m_t + m_p) * Elab
    Ep = Ecm + m_p

    k = (
        m_t
        * np.sqrt(Elab * (Elab + 2 * m_p))
        / np.sqrt((m_t + m_p) ** 2 + 2 * m_t * Elab)
        / HBARC
    )
    mu = k**2 * Ep / (Ep**2 - m_p * m_p) * HBARC**2
    eta = ALPHA * Zz * mu / (HBARC * k)

    return ChannelKinematics(Elab, Ecm, mu, k, eta)


def elastic_kinematics(
    target: tuple[int, int], projectile: tuple[int, int], Elab: float
) -> ChannelKinematics:
    """Kinematics of ``projectile`` elastically scattering from ``target`` at ``Elab``."""
    A_t, Z_t = target
    A_p, Z_p = projectile
    return semi_relativistic_kinematics(
        nuclear_mass(A_t, Z_t), nuclear_mass(A_p, Z_p), Elab, Zz=Z_t * Z_p
    )


def rutherford_xs_mb_per_sr(angles_cm_deg: np.ndarray, kin: ChannelKinematics) -> np.ndarray:
    """Rutherford differential cross section in mb/sr, on a CM angular grid."""
    angles = np.deg2rad(np.asarray(angles_cm_deg, dtype=float))
    if np.any(angles <= 0.0) or np.any(angles >= np.pi):
        raise ValueError(
            "Rutherford cross section diverges at 0 degrees and is undefined at 180; "
            "angles must lie strictly within (0, 180)"
        )
    sin2 = np.sin(angles / 2.0) ** 2
    return 10 * kin.eta**2 / (4 * kin.k**2 * sin2**2)


def rutherford_xs_b_per_sr(angles_cm_deg: np.ndarray, kin: ChannelKinematics) -> np.ndarray:
    """Rutherford differential cross section in b/sr, on a CM angular grid."""
    return rutherford_xs_mb_per_sr(angles_cm_deg, kin) / MB_PER_BARN


def lab_to_cm_angle_elastic(
    angles_lab_deg: np.ndarray, target: tuple[int, int], projectile: tuple[int, int]
) -> np.ndarray:
    """Convert lab-frame to CM-frame scattering angles for elastic scattering.

    For elastic scattering the CM angle is single valued in the lab angle whenever the
    projectile is lighter than the target, which holds throughout these corpora:

        theta_cm = theta_lab + arcsin(tau sin theta_lab),    tau = m_projectile / m_target

    which inverts ``tan theta_lab = sin theta_cm / (cos theta_cm + tau)`` exactly.
    """
    tau = nuclear_mass(*projectile) / nuclear_mass(*target)
    if tau >= 1.0:
        raise ValueError(
            f"projectile is not lighter than the target (tau={tau:.3f}); the lab to CM "
            "angle map is not single valued"
        )
    lab = np.deg2rad(np.asarray(angles_lab_deg, dtype=float))
    return np.rad2deg(lab + np.arcsin(tau * np.sin(lab)))
