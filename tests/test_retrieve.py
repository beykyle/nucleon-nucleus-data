"""Tests for matching supplement rows to EXFOR measurements."""

from __future__ import annotations

import pytest

from nn_corpora import retrieve, spec
from nn_corpora.overrides import OVERRIDES


class TestEnergyMatching:
    """The supplement quotes energies inconsistently, so matching is tolerant."""

    @pytest.mark.parametrize("spec_energy,measured", [
        (3.4, 3.4), (3.4, 3.42), (3.4, 3.36),
        (100.0, 100.9), (100.0, 99.1),        # 1% relative at high energy
        (16.917, 16.92),
    ])
    def test_close_energies_match(self, spec_energy, measured):
        assert retrieve.energy_matches(spec_energy, measured)

    @pytest.mark.parametrize("spec_energy,measured", [
        (3.4, 3.6), (3.4, 4.0), (100.0, 105.0), (11.0, 12.0),
    ])
    def test_distant_energies_do_not(self, spec_energy, measured):
        assert not retrieve.energy_matches(spec_energy, measured)

    def test_tolerance_is_absolute_at_low_energy(self):
        """1% of 1.5 MeV is smaller than EXFOR's own rounding, so a floor applies."""
        assert retrieve.energy_matches(1.5, 1.54)
        assert not retrieve.energy_matches(1.5, 1.7)


class TestPlanKeys:
    """Parsing keywords are grouped so one query serves every subentry needing them."""

    def test_round_trip(self):
        kwargs = {"statistical_err_labels": ["ERR-T"],
                  "statistical_err_treatment": "independent",
                  "systematic_err_labels": []}
        assert retrieve._thaw(retrieve._freeze(kwargs)) == kwargs

    def test_equal_kwargs_share_a_key(self):
        a = {"statistical_err_labels": ["ERR-T"], "systematic_err_labels": []}
        b = {"systematic_err_labels": [], "statistical_err_labels": ["ERR-T"]}
        assert retrieve._freeze(a) == retrieve._freeze(b)

    def test_different_kwargs_do_not(self):
        a = {"statistical_err_labels": ["ERR-T"]}
        b = {"statistical_err_labels": ["ERR-S"]}
        assert retrieve._freeze(a) != retrieve._freeze(b)


def test_every_sector_maps_to_a_quantity_and_process():
    for corpus, sector in spec.available_sectors():
        quantities, process = spec.SECTORS[sector]
        assert quantities and process in ("el", "tot", "non")


def test_proton_elastic_requests_both_forms():
    """EXFOR reports some proton elastic data as ratios and some as absolute."""
    quantities, _ = spec.SECTORS["proton_elastic"]
    assert quantities == ("dXS/dRuth", "dXS/dA")


def test_overrides_reference_real_sectors():
    known = {(c, s) for c, s in spec.available_sectors()}
    for corpus, sector, _ in OVERRIDES:
        assert (corpus, sector) in known, f"override for unknown sector {corpus}/{sector}"


def test_overrides_are_documented():
    for key, override in OVERRIDES.items():
        assert override.reason, f"override {key} carries no reason"


@pytest.mark.slow
class TestAgainstDatabase:
    def test_smallest_sector_resolves_completely(self):
        data = retrieve.build_sector(spec.load_sector("test", "proton_reaction"))
        assert data.coverage == 1.0
        assert data.n_measurements == 4

    def test_energy_ranges_are_retrieved_whole(self):
        """Integral sectors match on subentry alone; the range is applied when munging."""
        data = retrieve.build_sector(spec.load_sector("test", "proton_reaction"))
        measurement = data.all_measurements()[0]
        assert measurement.rows > 1

    def test_measurements_carry_their_spec_row(self):
        data = retrieve.build_sector(spec.load_sector("test", "proton_reaction"))
        for measurement in data.all_measurements():
            assert measurement.spec_row.subentry
            assert measurement.target
