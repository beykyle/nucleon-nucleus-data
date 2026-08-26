"""Plots for visual inspection of a curated sector.

Outliers in these corpora are found by eye: the ELM notebooks plot every data set,
grouped by energy, and mistranscribed points show up as a single point an order of
magnitude off its neighbours. These helpers reproduce that view for the sector-based
corpora, using the same conventions the ELM notebooks settled on.
"""

from __future__ import annotations

import math

import numpy as np
from matplotlib import pyplot as plt

from exfor_tools.curate import categorize_measurement_list
from exfor_tools.distribution import AngularDistribution, EnergyDistribution

#: Per-quantity plot styling, matching the ELM notebooks.
STYLE = {
    # absolute cross sections span decades, so they are stacked multiplicatively
    "dXS/dA": {"log": True, "offsets": 10, "draw_baseline": False,
               "label_offset_factor": 1e-2},
    # ratios are O(1), stacked additively against a baseline at 1
    "dXS/dRuth": {"log": False, "offsets": 2, "draw_baseline": True,
                  "baseline_offset": 1, "label_offset_factor": 0.5},
    "Ay": {"log": False, "offsets": 2, "draw_baseline": True,
           "baseline_offset": 0, "label_offset_factor": 0.5},
}

LABEL_KWARGS = {
    "label_xloc_deg": None,
    "label_energy_err": False,
    "label_offset": True,
    "label_incident_energy": True,
    "label_excitation_energy": False,
    "label_exfor": True,
}


def plot_angular(measurements, *, title: str = "", n_per_plot: int = 8,
                 y_size: float = 10.0, einc_tol: float = 0.1):
    """Plot angular distributions, grouped by incident energy and offset for legibility."""
    if not measurements:
        return []

    quantity = measurements[0].quantity
    style = dict(STYLE.get(quantity, STYLE["dXS/dA"]))
    label_kwargs = dict(LABEL_KWARGS)
    label_kwargs["label_offset_factor"] = style.pop("label_offset_factor")

    grouped = categorize_measurement_list(measurements, min_num_pts=1, Einc_tol=einc_tol)
    n_plots = math.ceil(len(grouped) / n_per_plot)
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, y_size), squeeze=False)

    for i, ax in enumerate(axes[0]):
        chunk = grouped[i * n_per_plot:(i + 1) * n_per_plot]
        if not chunk:
            ax.set_visible(False)
            continue
        AngularDistribution.plot(
            chunk, ax,
            offsets=style["offsets"],
            data_symbol=_symbol(quantity),
            rxn_label=title,
            log=style["log"],
            draw_baseline=style["draw_baseline"],
            baseline_offset=style.get("baseline_offset"),
            label_kwargs=label_kwargs,
        )
    fig.tight_layout()
    return list(axes[0])


def plot_energy(measurements, *, title: str = "", n_per_plot: int = 12, y_size: float = 6.0):
    """Plot energy-dependent cross sections, one panel per group of data sets."""
    if not measurements:
        return []

    n_plots = math.ceil(len(measurements) / n_per_plot)
    fig, axes = plt.subplots(n_plots, 1, figsize=(11, y_size * n_plots), squeeze=False)

    for i, ax in enumerate(axes[:, 0]):
        chunk = measurements[i * n_per_plot:(i + 1) * n_per_plot]
        if not chunk:
            ax.set_visible(False)
            continue
        EnergyDistribution.plot(chunk, ax, data_symbol=r"$\sigma$", rxn_label=title, log=True)
        ax.set_xscale("log")
    fig.tight_layout()
    return list(axes[:, 0])


def plot_sector(result, *, by_target: bool = True, max_targets: int | None = None, **kwargs):
    """Plot a curated sector, one figure per target by default."""
    measurements = [
        m for entry_id, ms in result.data.measurements.items() for m in ms
    ]
    if not measurements:
        print("nothing to plot")
        return

    integral = result.sector in ("neutron_total", "proton_reaction")
    plot = plot_energy if integral else plot_angular

    if not by_target:
        plot(measurements, title=f"{result.corpus} {result.sector}", **kwargs)
        return

    by = {}
    for m in measurements:
        by.setdefault(m.spec_row.target_label, []).append(m)
    for i, (label, group) in enumerate(sorted(by.items())):
        if max_targets is not None and i >= max_targets:
            print(f"... {len(by) - max_targets} further targets not plotted")
            break
        plot(group, title=_latex(label), **kwargs)


def _symbol(quantity: str) -> str:
    return {
        "dXS/dA": r"$d\sigma/d\Omega$",
        "dXS/dRuth": r"$\sigma / \sigma_{Rutherford}$",
        "Ay": r"$A_y$",
        "XS": r"$\sigma$",
    }.get(quantity, quantity)


def _latex(target_label: str) -> str:
    if target_label.startswith("nat"):
        return rf"$^{{\rm nat}}${target_label[3:]}"
    mass = "".join(c for c in target_label if c.isdigit())
    return rf"$^{{{mass}}}${target_label[len(mass):]}"


def check_uncertainties(result, floor: float = 0.0) -> list[str]:
    """Report measurements with missing or suspiciously small uncertainties."""
    flags = []
    for ms in result.data.measurements.values():
        for m in ms:
            if np.allclose(m.statistical_err, 0.0):
                flags.append(f"{m.subentry}: no uncertainties reported")
            elif floor and np.any(m.statistical_err < floor):
                n = int(np.sum(m.statistical_err < floor))
                flags.append(f"{m.subentry}: {n} uncertainties below {floor:g}")
    return flags
