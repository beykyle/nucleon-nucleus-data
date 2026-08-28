"""Write curated measurements to JSON, with bibliography and provenance manifest.

The record schema extends the one ``exfor_tools`` produces via
``Distribution.to_dataframe``, so files remain readable by
``AngularDistribution.from_dataframe`` and ``EnergyDistribution.from_dataframe``.
Five fields are added, because the ELM corpus format cannot express them:

``corpus``, ``sector``
    which corpus and sector a record belongs to, so files can be recombined.
``projectile``
    ``"neutron"`` or ``"proton"``. The ELM corpus files key only on the target, so
    (n,n) and (p,p) data for one nucleus are indistinguishable within a file.
``notes``
    every transformation applied during munging, in order.
``summed_excitation_max_MeV``
    present only on the quasi-elastic records: EXFOR writes these as scattering (SCT)
    summed below an upper bound on the residual's excitation rather than as resolved
    elastic scattering, and this is that bound. The supplement counts them as elastic;
    the field is here so a consumer can decide whether to.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from exfor_tools.reaction import get_exfor_particle_symbol

from .spec import DATA_DIR

#: Corpus-sector -> the ``type`` values its records may carry.
EXPECTED_TYPES = {
    "neutron_elastic": {"ECS"},
    "neutron_ay": {"APower"},
    "neutron_total": {"CS"},
    "proton_elastic": {"ECS_Rutherford"},
    "proton_ay": {"APower"},
    "proton_reaction": {"CS"},
    # ELM sectors
    "elastic_diff_xs": {"ECS", "ECS_Rutherford"},
    "elastic_ay": {"APower"},
    "charge_exchange": {"ECS"},
}

#: Corpus-sector -> the ``y_units`` its records may carry.
EXPECTED_UNITS = {
    "neutron_elastic": {"b/sr"},
    "neutron_ay": {"no-dim"},
    "neutron_total": {"b"},
    "proton_elastic": {"no-dim"},
    "proton_ay": {"no-dim"},
    "proton_reaction": {"b"},
    "elastic_diff_xs": {"b/sr", "no-dim"},
    "elastic_ay": {"no-dim"},
    "charge_exchange": {"b/sr"},
}


def target_filename(target: tuple[int, int]) -> str:
    """``(48, 20)`` -> ``"Ca_48"``, ``(0, 26)`` -> ``"Fe_0"`` for a natural target."""
    return get_exfor_particle_symbol(*target).replace("-", "_")


@dataclass
class Record:
    """One serialized measurement, ready to be written."""

    target: tuple[int, int]
    payload: dict


def to_record(
    measurement,
    *,
    corpus: str,
    sector: str,
    projectile: str,
    target: tuple[int, int],
    citation: str = "",
) -> Record:
    """Build one JSON record from a parsed measurement."""
    frame: pd.DataFrame = measurement.to_dataframe(citation)
    payload = json.loads(frame.to_json(orient="records"))[0]

    payload["corpus"] = corpus
    payload["sector"] = sector
    payload["projectile"] = projectile
    payload["target"] = get_exfor_particle_symbol(*target)
    notes = getattr(measurement, "notes", None) or []
    payload["notes"] = list(notes) if isinstance(notes, list) else [notes]
    bound = getattr(measurement, "summed_excitation_max_mev", None)
    if bound is not None:
        payload["summed_excitation_max_MeV"] = bound

    return Record(target=target, payload=payload)


def write_sector(
    records: list[Record],
    *,
    corpus: str,
    sector: str,
    bibtex: dict[str, str] | None = None,
    data_dir: Path = DATA_DIR,
) -> Path:
    """Write one corpus-sector: ``<Target>.json`` per target, plus a ``.bib``."""
    out = data_dir / corpus / sector
    out.mkdir(parents=True, exist_ok=True)

    for stale in out.glob("*.json"):
        stale.unlink()

    by_target: dict[tuple[int, int], list[dict]] = {}
    for record in records:
        by_target.setdefault(record.target, []).append(record.payload)

    for target, payloads in sorted(by_target.items()):
        payloads.sort(key=lambda p: (p.get("energy", 0.0), p["EXFORAccessionNumber"]))
        path = out / f"{target_filename(target)}.json"
        path.write_text(json.dumps(payloads, indent=4) + "\n")

    if bibtex:
        entries = [b for _, b in sorted(bibtex.items()) if b]
        (out / f"{sector}.bib").write_text("\n".join(entries) + "\n")

    return out


def write_manifest(
    corpus: str,
    sectors: dict[str, dict],
    *,
    provenance: dict,
    data_dir: Path = DATA_DIR,
) -> Path:
    """Record how a corpus was produced, alongside its data."""
    path = data_dir / corpus / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        {"corpus": corpus, "provenance": provenance, "sectors": sectors},
        indent=4, sort_keys=True) + "\n")
    return path


def exfor_database_tag() -> str:
    """Which EXFOR release the database in use is, as ``X4-YYYY-MM-DD``.

    x4i3 names the release in a marker file beside the database. Taking it from the
    directory name instead only works when ``X43I_DATAPATH`` points at a release
    directory built by ``x4i3_tools``; on the snapshot x4i3 downloads for itself the
    database sits in the package's own ``data/`` directory, whose name says nothing.
    """
    import x4i3

    # the downloaded snapshot's marker is the tarball's name, e.g. x4i3_X4-2023-04-29
    return x4i3.dbTagFile.stem.removeprefix("x4i3_")


def provenance() -> dict:
    """Versions and database identity, for reproducibility."""
    import exfor_tools
    import x4i3

    return {
        "exfor_database": exfor_database_tag(),
        "exfor_tools_version": exfor_tools.__version__,
        "x4i3_version": x4i3.__version__,
    }


def sector_summary(data, records: list[Record]) -> dict:
    """A sector's counts and coverage, for the manifest."""
    return {
        "spec_rows": len(data.outcomes),
        "rows_in_exfor": sum(o.row.in_exfor for o in data.outcomes),
        "rows_resolved": sum(o.resolved for o in data.outcomes),
        "coverage": round(data.coverage, 4),
        "measurements": len(records),
        "data_points": sum(len(r.payload["data"]["x"]) for r in records),
        "entries": sorted({r.payload["EXFORAccessionNumber"][:5] for r in records}),
    }
