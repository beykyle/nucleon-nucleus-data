"""Tests for the JSON record schema."""

from __future__ import annotations

import json

import numpy as np
import pytest

from nn_corpora import serialize, spec


class FakeDistribution:
    """Enough of an AngularDistribution to serialize."""

    def __init__(self):
        self.subentry = "O0032002"
        self.quantity = "dXS/dRuth"
        self.x = np.array([30.0, 60.0, 90.0])
        self.x_err = np.zeros(3)
        self.y = np.array([0.9, 0.5, 0.2])
        self.statistical_err = np.array([0.01, 0.01, 0.01])
        self.systematic_norm_err = 0.05
        self.systematic_offset_err = 0.0
        self.rows = 3
        self.x_units = "CM-degrees"
        self.y_units = "no-dim"
        self.Einc, self.Einc_err, self.Einc_units = 65.0, 0.0, "MeV"
        self.Ex, self.Ex_err, self.Ex_units = 0.0, 0.0, "MeV"
        self.notes = ["divided by the Rutherford cross section"]

    def to_dataframe(self, citation=""):
        from exfor_tools.distribution import AngularDistribution
        return AngularDistribution.to_dataframe(self, citation)


@pytest.mark.parametrize("target,expected", [
    ((48, 20), "Ca_48"), ((0, 26), "Fe_0"), ((208, 82), "Pb_208"), ((1, 0), "N"),
])
def test_target_filenames(target, expected):
    assert serialize.target_filename(target) == expected


class TestRecord:
    @pytest.fixture
    def record(self):
        return serialize.to_record(
            FakeDistribution(), corpus="kduq", sector="proton_elastic",
            projectile="proton", target=(40, 20), citation="Someone et al.",
        )

    def test_carries_the_added_fields(self, record):
        """The ELM schema records neither the projectile nor the corpus."""
        payload = record.payload
        assert payload["corpus"] == "kduq"
        assert payload["sector"] == "proton_elastic"
        assert payload["projectile"] == "proton"
        assert payload["target"] == "Ca-40"

    def test_preserves_notes(self, record):
        assert record.payload["notes"] == ["divided by the Rutherford cross section"]

    def test_type_follows_the_quantity(self, record):
        assert record.payload["type"] == "ECS_Rutherford"

    def test_is_json_serializable(self, record):
        assert json.loads(json.dumps(record.payload))["energy"] == 65.0

    def test_round_trips_through_exfor_tools(self, record):
        import pandas as pd
        from exfor_tools.distribution import AngularDistribution
        restored = AngularDistribution.from_dataframe(pd.DataFrame([record.payload]))
        np.testing.assert_allclose(restored[0].y, [0.9, 0.5, 0.2])
        assert restored[0].subentry == "O0032002"


def test_expected_types_and_units_cover_every_sector():
    for _, sector in spec.available_sectors():
        assert sector in serialize.EXPECTED_TYPES
        assert sector in serialize.EXPECTED_UNITS


def test_elm_sectors_are_covered_too():
    from nn_corpora.elm_curate import ELM_SECTORS
    for sector in ELM_SECTORS:
        assert sector in serialize.EXPECTED_TYPES
        assert sector in serialize.EXPECTED_UNITS


def test_provenance_records_the_database_and_versions():
    p = serialize.provenance()
    assert p["exfor_database"].startswith("X4-")
    assert p["exfor_tools_version"] and p["x4i3_version"]


def test_writing_a_sector(tmp_path):
    records = [serialize.to_record(
        FakeDistribution(), corpus="kduq", sector="proton_elastic",
        projectile="proton", target=(40, 20))]
    out = serialize.write_sector(records, corpus="kduq", sector="proton_elastic",
                                 bibtex={"O0032": "@article{x,}"}, data_dir=tmp_path)
    assert (out / "Ca_40.json").exists()
    assert (out / "proton_elastic.bib").exists()
    assert json.loads((out / "Ca_40.json").read_text())[0]["target"] == "Ca-40"
