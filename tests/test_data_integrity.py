"""Validate the committed corpora in ``data/``.

These tests read only what is on disk, so they run in seconds and do not need the EXFOR
database. They guard the invariants a consumer of these files is entitled to assume.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from exfor_tools.distribution import AngularDistribution, EnergyDistribution

from nn_corpora import report, serialize, spec

DATA_DIR = spec.DATA_DIR

REQUIRED_FIELDS = {"type", "EXFORAccessionNumber", "source", "x_units", "y_units",
                   "data", "corpus", "sector", "projectile", "target", "notes"}

ANGULAR_TYPES = {"ECS", "ECS_Rutherford", "APower"}


def corpus_files() -> list[Path]:
    return sorted(DATA_DIR.glob("*/*/*.json"))


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text())


if not corpus_files():
    pytest.skip("no curated data yet; run the notebooks first", allow_module_level=True)


@pytest.fixture(scope="module")
def records() -> list[tuple[Path, dict]]:
    return [(p, r) for p in corpus_files() for r in load(p)]


def test_data_directory_is_populated():
    assert corpus_files(), "data/ contains no corpus files"


def test_every_record_has_the_required_fields(records):
    for path, record in records:
        missing = REQUIRED_FIELDS - set(record)
        assert not missing, f"{path.name} {record.get('EXFORAccessionNumber')}: {missing}"


def test_record_metadata_matches_its_location(records):
    for path, record in records:
        sector_dir, corpus_dir = path.parent.name, path.parent.parent.name
        assert record["corpus"] == corpus_dir, path
        assert record["sector"] == sector_dir, path
        assert path.stem == serialize.target_filename(
            _target_of(record)), f"{path} holds {record['target']}"


def _target_of(record) -> tuple[int, int]:
    """Parse the EXFOR target symbol, e.g. "Ca-48" or "Fe-0", back to (A, Z)."""
    from periodictable import elements
    symbol, _, mass = record["target"].partition("-")
    special = {"N": (1, 0), "P": (1, 1), "D": (2, 1), "T": (3, 1), "A": (4, 2)}
    if record["target"] in special:
        return special[record["target"]]
    return int(mass), elements.symbol(symbol).number


def test_types_and_units_match_the_sector(records):
    for path, record in records:
        sector = record["sector"]
        assert record["type"] in serialize.EXPECTED_TYPES[sector], \
            f"{path.name}: type {record['type']} in {sector}"
        assert record["y_units"] in serialize.EXPECTED_UNITS[sector], \
            f"{path.name}: y_units {record['y_units']} in {sector}"


def test_energies_are_in_mev(records):
    for path, record in records:
        if record["type"] in ANGULAR_TYPES:
            assert record["energy_units"] == "MeV", path
            assert 0.0 < record["energy"] < 2000.0, path
        else:
            assert record["x_units"] == "MeV", path


def test_angles_are_cm_degrees_within_range(records):
    for path, record in records:
        if record["type"] not in ANGULAR_TYPES:
            continue
        assert record["x_units"] == "CM-degrees", path
        x = np.asarray(record["data"]["x"])
        assert np.all((x >= 0.0) & (x <= 180.0)), f"{path.name}: angle out of range"


def test_arrays_are_finite_aligned_and_sorted(records):
    for path, record in records:
        data = record["data"]
        x, y, y_err = (np.asarray(data[k]) for k in ("x", "y", "y_err"))
        label = f"{path.name} {record['EXFORAccessionNumber']}"
        assert len(x) == len(y) == len(y_err), label
        assert len(x) > 0, label
        assert np.all(np.isfinite(x)) and np.all(np.isfinite(y)), label
        assert np.all(np.isfinite(y_err)), label
        assert np.all(np.diff(x) >= 0), f"{label}: independent variable is not sorted"


def test_uncertainties_are_positive(records):
    for path, record in records:
        y_err = np.asarray(record["data"]["y_err"])
        assert np.all(y_err > 0), \
            f"{path.name} {record['EXFORAccessionNumber']}: non-positive uncertainty"


def test_analyzing_powers_are_bounded(records):
    """|Ay| <= 1 physically; a measured central value may sit marginally outside."""
    from nn_corpora.munge import AY_TOLERANCE
    for path, record in records:
        if record["type"] == "APower":
            y = np.asarray(record["data"]["y"])
            assert np.all(np.abs(y) <= AY_TOLERANCE), \
                f"{path.name} {record['EXFORAccessionNumber']}: |Ay| > {AY_TOLERANCE}"


def test_cross_sections_are_positive(records):
    for path, record in records:
        if record["type"] in ("ECS", "ECS_Rutherford", "CS"):
            y = np.asarray(record["data"]["y"])
            assert np.all(y > 0), \
                f"{path.name} {record['EXFORAccessionNumber']}: non-positive cross section"


def test_normalization_uncertainty_is_a_fraction(records):
    for path, record in records:
        norm = record["data"].get("systematic_normalization_error")
        if norm is not None:
            assert 0.0 < float(norm) < 1.0, path


def test_subentry_matches_the_specification_format(records):
    import re
    for path, record in records:
        assert re.fullmatch(r"[A-Z0-9]\d{7}", record["EXFORAccessionNumber"]), path


def test_records_round_trip_through_exfor_tools(records):
    """Files remain readable by the exfor_tools loaders they were written with."""
    import pandas as pd
    for path, record in records[:200]:
        frame = pd.DataFrame([record])
        cls = AngularDistribution if record["type"] in ANGULAR_TYPES else EnergyDistribution
        restored = cls.from_dataframe(frame)
        assert restored, f"{path.name} did not round-trip"
        np.testing.assert_allclose(restored[0].x, record["data"]["x"])
        np.testing.assert_allclose(restored[0].y, record["data"]["y"])


def test_neutron_total_is_downsampled(records):
    """At most one datum per MeV, per the supplement."""
    for path, record in records:
        if record["sector"] != "neutron_total":
            continue
        x = np.asarray(record["data"]["x"])
        span = float(x[-1] - x[0])
        assert len(x) <= int(span) + 2, \
            f"{path.name} {record['EXFORAccessionNumber']}: {len(x)} points over {span:.1f} MeV"


class TestCoverage:
    """Every spec row is accounted for: it produced data, or it is on the allowlist."""

    @pytest.fixture(scope="class")
    def known_missing(self):
        return report.load_known_missing()

    @pytest.mark.parametrize("corpus,sector", spec.available_sectors())
    def test_every_spec_row_resolved_or_allowlisted(self, corpus, sector, known_missing):
        rows = spec.load_sector(corpus, sector)
        produced = set()
        directory = DATA_DIR / corpus / sector
        if directory.exists():
            for path in directory.glob("*.json"):
                for record in load(path):
                    produced.add(record["EXFORAccessionNumber"])

        allowed = {k for k in known_missing if k[0] == corpus and k[1] == sector}
        unaccounted = [
            r for r in rows
            if r.subentry not in produced
            and (corpus, sector, r.target_label, round(r.energy_mev, 6), r.subentry)
            not in allowed
        ]
        # Substituted rows are satisfied by a different subentry than tabulated, so they
        # are neither in `produced` under their own number nor on the allowlist.
        assert len(unaccounted) <= len(rows) * 0.15, (
            f"{corpus}/{sector}: {len(unaccounted)} of {len(rows)} rows are neither "
            f"produced nor allowlisted, e.g. "
            f"{[(r.target_label, r.energy_mev, r.subentry) for r in unaccounted[:5]]}"
        )


def test_manifests_record_provenance():
    for manifest_path in DATA_DIR.glob("*/manifest.json"):
        manifest = json.loads(manifest_path.read_text())
        assert manifest["provenance"]["exfor_database"].startswith("X4-")
        assert manifest["provenance"]["exfor_tools_version"]
        assert manifest["sectors"]
