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


@pytest.mark.slow
class TestScatteringCode:
    """EXFOR's SCT is "Total scattering (elastic + inelastic)" per its dictionary.

    Summed, that is a different observable from elastic scattering. It may satisfy an
    elastic query only when the data set resolves the residual's levels, so that the
    excitation-energy filter can select the ground state.
    """

    def test_level_resolved_scattering_matches_elastic(self):
        from exfor_tools.db import __EXFOR_DB__
        from exfor_tools.reaction import Reaction, is_match, is_level_resolved

        entry = __EXFOR_DB__.retrieve(ENTRY="13965")["13965"]
        data_set = next(ds for k, ds in entry.getDataSets().items() if k[1] == "13965002")
        assert data_set.reaction[0].products == ["SCT"]
        assert is_level_resolved(data_set)
        assert is_match(Reaction(target=(181, 73), projectile=(1, 0), process="el"),
                        data_set)

    def test_summed_scattering_does_not(self):
        """A scattering data set with no level column is elastic plus inelastic."""
        from exfor_tools.reaction import Reaction, is_match

        class FakeReaction:
            targ = type("t", (), {"getA": lambda s: 181, "getZ": lambda s: 73})()
            proj = type("p", (), {"getA": lambda s: 1, "getZ": lambda s: 0})()
            products = ["SCT"]
            residual = type("r", (), {"getA": lambda s: 181, "getZ": lambda s: 73})()

        summed = type("ds", (), {"reaction": [FakeReaction()],
                                 "labels": ["EN", "ANG-CM", "DATA", "DATA-ERR"]})()
        assert not is_match(
            Reaction(target=(181, 73), projectile=(1, 0), process="el"), summed)

    def test_every_admitted_scattering_set_is_level_resolved(self):
        """No summed elastic-plus-inelastic data reaches an elastic sector."""
        from exfor_tools.reaction import is_level_resolved

        from nn_corpora import errors

        elastic_sectors = {"neutron_elastic", "proton_elastic", "neutron_ay", "proton_ay"}
        for row in spec.load_all():
            if not row.in_exfor or row.sector not in elastic_sectors:
                continue
            try:
                blocks = errors.data_sets_for(row.entry, row.subentry, row.pointer)
            except Exception:
                continue
            for data_set in blocks.values():
                reaction = data_set.reaction[0]
                if getattr(reaction, "products", None) == ["SCT"]:
                    assert is_level_resolved(data_set), (
                        f"{row.subentry} is summed scattering, not elastic")
