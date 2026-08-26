"""Homogenise units and frames, and apply the corpus-wide cleaning steps.

Conventions for every corpus in this repo:

===========================================  ==================  ==============
quantity                                     units               ``type`` in JSON
===========================================  ==================  ==============
neutron differential elastic / (p,n)         b/sr                ``ECS``
charged-projectile differential elastic      ratio to Rutherford ``ECS_Rutherford``
analyzing power                              dimensionless       ``APower``
neutron total / proton reaction              b                   ``CS``
===========================================  ==================  ==============

with energies in MeV and angles in CM degrees throughout.

Note that charged-projectile elastic data are stored as a *ratio* whether or not
EXFOR reports them that way; absolute cross sections are divided by the Rutherford
cross section of :mod:`nn_corpora.kinematics`. This deviates from the supplement,
which rescales the other way, into absolute mb/sr. Storing the ratio keeps the
low-angle Coulomb divergence out of the data, matches what the ELM corpus and
``rxmc`` work in, and is exactly invertible given the tabulated energy and target.

Every transformation records what it did in the measurement's ``notes``, following
the ELM notebooks' practice of keeping an auditable record of each edit.
"""

from __future__ import annotations

import numpy as np

from . import kinematics as kin

# Units exfor_tools may emit, mapped to the spelling used in this corpus.
DIFFERENTIAL_UNITS = {"barns/ster": "b/sr", "b/Sr": "b/sr", "b/sr": "b/sr"}
INTEGRAL_UNITS = {"barns": "b", "b": "b"}
DIMENSIONLESS_UNITS = {"no-dim": "no-dim", "unitless": "no-dim"}

CM_DEGREES = "CM-degrees"
LAB_DEGREES = "LAB-degrees"

# If a data set reports no correlated normalisation uncertainty, assign this. The ELM
# notebooks use the same 5%, and the KDUQ/CHUQ analyses likewise carry an
# unaccounted-for uncertainty term rather than trusting the tabulated errors alone.
DEFAULT_SYSTEMATIC_NORM_ERR = 0.05

# Below this CM angle the Rutherford cross section diverges fast enough that the
# ratio is dominated by the angular resolution rather than the measurement.
MIN_RATIO_ANGLE_DEG = 1.0


def note(measurement, text: str) -> None:
    """Record an edit on a measurement, for provenance."""
    if not isinstance(getattr(measurement, "notes", None), list):
        measurement.notes = [] if not measurement.notes else [measurement.notes]
    measurement.notes.append(text)


def to_cm_degrees(measurement, target: tuple[int, int], projectile: tuple[int, int]) -> None:
    """Put a differential measurement's angles in the CM frame, in degrees."""
    if measurement.x_units == CM_DEGREES:
        return
    if measurement.x_units != LAB_DEGREES:
        raise ValueError(
            f"{measurement.subentry}: cannot interpret angle units {measurement.x_units!r}"
        )

    measurement.x = kin.lab_to_cm_angle_elastic(measurement.x, target, projectile)
    measurement.x_units = CM_DEGREES
    note(measurement, "converted scattering angles from the lab to the CM frame")

    if not np.all(np.diff(measurement.x) >= 0):
        raise ValueError(f"{measurement.subentry}: CM angles are not monotonic")


def to_ratio_to_rutherford(
    measurement, target: tuple[int, int], projectile: tuple[int, int]
) -> None:
    """Convert an absolute charged-particle elastic cross section to a Rutherford ratio.

    A no-op for data EXFOR already reports as a ratio.
    """
    if measurement.quantity == "dXS/dRuth":
        return
    if measurement.quantity != "dXS/dA":
        raise ValueError(
            f"{measurement.subentry}: cannot form a Rutherford ratio from "
            f"{measurement.quantity!r}"
        )
    if projectile[1] == 0:
        raise ValueError(
            f"{measurement.subentry}: Rutherford ratio is undefined for a neutral projectile"
        )
    if measurement.x_units != CM_DEGREES:
        raise ValueError(
            f"{measurement.subentry}: convert to CM angles before forming the ratio"
        )

    keep = measurement.x >= MIN_RATIO_ANGLE_DEG
    if not np.all(keep):
        dropped = int((~keep).sum())
        _select(measurement, keep)
        note(measurement,
             f"dropped {dropped} point(s) below {MIN_RATIO_ANGLE_DEG} degrees, where the "
             "Rutherford cross section diverges")
    if measurement.rows == 0:
        return

    channel = kin.elastic_kinematics(target, projectile, float(measurement.Einc))
    sigma_ruth = kin.rutherford_xs_b_per_sr(measurement.x, channel)

    scale = _to_b_per_sr(measurement.y_units, measurement.subentry)
    measurement.y = measurement.y * scale / sigma_ruth
    measurement.statistical_err = measurement.statistical_err * scale / sigma_ruth
    measurement.quantity = "dXS/dRuth"
    measurement.y_units = "no-dim"
    note(measurement,
         "divided by the Rutherford cross section (semi-relativistic kinematics) to "
         "give a ratio to Rutherford")


def _to_b_per_sr(units: str, subentry: str) -> float:
    if units in DIFFERENTIAL_UNITS:
        return 1.0
    if units in ("mb/sr", "mb/Sr", "millibarns/ster"):
        return 1.0 / kin.MB_PER_BARN
    raise ValueError(f"{subentry}: unexpected differential cross section units {units!r}")


def _select(measurement, keep: np.ndarray) -> None:
    """Restrict a measurement to a boolean subset of its points, in place."""
    measurement.x = measurement.x[keep]
    measurement.x_err = measurement.x_err[keep]
    measurement.y = measurement.y[keep]
    measurement.statistical_err = measurement.statistical_err[keep]
    measurement.rows = int(keep.sum())


def homogenize_units(measurement) -> None:
    """Normalise unit spellings and assert the quantity carries the expected units."""
    quantity, units = measurement.quantity, measurement.y_units

    if quantity == "dXS/dA":
        measurement.y_units = _require(units, DIFFERENTIAL_UNITS, measurement)
    elif quantity in ("dXS/dRuth", "Ay"):
        measurement.y_units = _require(units, DIMENSIONLESS_UNITS, measurement)
    elif quantity == "XS":
        measurement.y_units = _require(units, INTEGRAL_UNITS, measurement)
    else:
        raise ValueError(f"{measurement.subentry}: unknown quantity {quantity!r}")

    energy_units = getattr(measurement, "Einc_units", None) or measurement.x_units
    if energy_units != "MeV":
        raise ValueError(f"{measurement.subentry}: energies are in {energy_units!r}, not MeV")


def _require(units: str, allowed: dict[str, str], measurement) -> str:
    if units not in allowed:
        raise ValueError(
            f"{measurement.subentry}: {measurement.quantity} reported in {units!r}, "
            f"expected one of {sorted(allowed)}"
        )
    return allowed[units]


def restrict_to_energy_window(measurement, lo: float, hi: float) -> bool:
    """Trim an energy-dependent measurement to [lo, hi]. Returns False if nothing remains.

    The supplement tabulates each neutron total cross section data set over the energy
    range it drew from EXFOR, which is often narrower than the full data set.
    """
    keep = (measurement.x >= lo) & (measurement.x <= hi)
    if not np.any(keep):
        return False
    if np.all(keep):
        return True
    dropped = int((~keep).sum())
    _select(measurement, keep)
    note(measurement,
         f"restricted to the tabulated energy range {lo}-{hi} MeV, dropping {dropped} point(s)")
    return True


def downsample_energy(measurement, max_per_mev: float = 1.0) -> None:
    """Thin an energy-dependent measurement to at most ``max_per_mev`` points per MeV.

    The supplement's rationale (p.1): many neutron total cross section data sets have
    "an unnecessarily large number of energy bins for the requirements of optical
    potential optimization" -- one set spans 250 keV to 20 MeV in nearly 50,000 bins --
    and "given the slowly-varying nature of the total cross section in this energy
    regime ... we downsampled each data set to have one datum per MeV".

    Points are taken from uniform energy bins, keeping the one nearest each bin centre,
    so the retained points sample the range evenly and the endpoints are preserved.
    """
    span = float(measurement.x[-1] - measurement.x[0])
    target = max(int(np.ceil(span * max_per_mev)), 1)
    if measurement.rows <= target:
        return

    edges = np.linspace(measurement.x[0], measurement.x[-1], target + 1)
    centres = 0.5 * (edges[:-1] + edges[1:])
    keep = np.zeros(measurement.rows, dtype=bool)
    keep[np.unique(np.abs(measurement.x[:, None] - centres[None, :]).argmin(axis=0))] = True
    keep[0] = keep[-1] = True

    before = measurement.rows
    _select(measurement, keep)
    note(measurement,
         f"downsampled from {before} to {measurement.rows} points, at most "
         f"{max_per_mev:g} per MeV")


def apply_default_norm_err(measurement, default: float = DEFAULT_SYSTEMATIC_NORM_ERR) -> None:
    """Assign a default correlated normalisation uncertainty where none is reported."""
    if np.allclose(measurement.systematic_norm_err, 0):
        measurement.systematic_norm_err = default
        note(measurement,
             f"assigned a default normalisation uncertainty of {default:.0%}, none reported")


def scale(measurement, factor: float, reason: str) -> None:
    """Rescale a measurement's values and uncertainties, recording why.

    Used for the transcription errors the supplement documents, e.g. Test corpus
    54Fe: "we reduced the cross section values and reported errors ... by a factor of
    1000; the data as listed in EXFOR appear to be 1000 too small".
    """
    measurement.y = measurement.y * factor
    measurement.statistical_err = measurement.statistical_err * factor
    note(measurement, f"scaled values and uncertainties by {factor:g}: {reason}")


def has_usable_uncertainties(measurement) -> bool:
    """Whether every datum carries a non-zero uncertainty.

    The supplement removes data sets missing a "necessary feature", listing "scattering
    energy, scattering angle, cross section, and cross section error" as necessary for
    differential cross sections.
    """
    return measurement.rows > 0 and not np.any(measurement.statistical_err <= 0)
