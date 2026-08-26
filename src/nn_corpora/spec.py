"""The corpus specifications: which EXFOR subentries belong to which corpus.

For KDUQ, CHUQ and Test these come from the tables of
``supplement_experimentalCorpora.pdf``, transcribed to ``spec/*.csv`` by
``scripts/extract_corpus_tables.py``. The ELM corpus has no such table -- it is
defined by a query over a set of targets and an energy window -- so it is described
here in code instead, mirroring the notebooks in ``~/elm/elm_data``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO_ROOT / "spec"
DATA_DIR = REPO_ROOT / "data"

TABULATED_CORPORA = ("kduq", "chuq", "test")

# Sector -> (exfor_tools quantities, reaction process). "el" is elastic scattering,
# "tot" the neutron total cross section, "non" the proton reaction (nonelastic) cross
# section.
#
# Proton elastic scattering lists two quantities because EXFOR reports some data sets
# as a ratio to Rutherford and others as an absolute cross section. Both are retrieved;
# the ratio is preferred where it exists, and absolute data are divided by the
# Rutherford cross section during munging so the sector is uniformly a ratio.
SECTORS: dict[str, tuple[tuple[str, ...], str]] = {
    "neutron_elastic": (("dXS/dA",), "el"),
    "neutron_ay": (("Ay",), "el"),
    "neutron_total": (("XS",), "tot"),
    "proton_elastic": (("dXS/dRuth", "dXS/dA"), "el"),
    "proton_ay": (("Ay",), "el"),
    "proton_reaction": (("XS",), "non"),
}

PROJECTILES = {"neutron": (1, 0), "proton": (1, 1)}


@dataclass(frozen=True)
class SpecRow:
    """One row of a supplement corpus table: a data set at one scattering energy."""

    corpus: str
    sector: str
    projectile: str
    target_A: int
    target_Z: int
    target_label: str
    energy_mev: float
    energy_hi_mev: float | None
    subentry: str
    pointer: str
    pdf_page: int

    @property
    def entry(self) -> str:
        """The 5-character EXFOR entry number containing this subentry."""
        return self.subentry[:5]

    @property
    def target(self) -> tuple[int, int]:
        return (self.target_A, self.target_Z)

    @property
    def projectile_AZ(self) -> tuple[int, int]:
        return PROJECTILES[self.projectile]

    @property
    def is_range(self) -> bool:
        """True for sectors tabulated as an energy range rather than a single energy."""
        return self.energy_hi_mev is not None

    @property
    def in_exfor(self) -> bool:
        """False for rows the supplement marks "-": not locatable in EXFOR."""
        return bool(self.subentry)

    @property
    def key(self) -> tuple:
        """Identity of this row, for matching against coverage reports."""
        return (self.corpus, self.sector, self.target_label,
                self.energy_mev, self.subentry, self.pointer)


def sector_path(corpus: str, sector: str, spec_dir: Path = SPEC_DIR) -> Path:
    return spec_dir / f"{corpus}_{sector}.csv"


def load_sector(corpus: str, sector: str, spec_dir: Path = SPEC_DIR) -> list[SpecRow]:
    """Load one corpus-sector table."""
    with sector_path(corpus, sector, spec_dir).open(newline="") as f:
        return [
            SpecRow(
                corpus=r["corpus"], sector=r["sector"], projectile=r["projectile"],
                target_A=int(r["target_A"]), target_Z=int(r["target_Z"]),
                target_label=r["target_label"],
                energy_mev=float(r["energy_mev"]),
                energy_hi_mev=float(r["energy_hi_mev"]) if r["energy_hi_mev"] else None,
                subentry=r["subentry"], pointer=r["pointer"],
                pdf_page=int(r["pdf_page"]),
            )
            for r in csv.DictReader(f)
        ]


def available_sectors(spec_dir: Path = SPEC_DIR) -> list[tuple[str, str]]:
    """All (corpus, sector) pairs with a committed spec table."""
    found = []
    for corpus in TABULATED_CORPORA:
        for sector in SECTORS:
            if sector_path(corpus, sector, spec_dir).exists():
                found.append((corpus, sector))
    return found


def load_all(spec_dir: Path = SPEC_DIR) -> list[SpecRow]:
    return [row for cs in available_sectors(spec_dir) for row in load_sector(*cs, spec_dir)]


def group_by_entry(rows: list[SpecRow]) -> dict[tuple[tuple[int, int], str], list[SpecRow]]:
    """Group rows by (target, EXFOR entry), the unit of retrieval.

    ``ExforEntry`` retrieves a whole entry at a time, and one entry commonly supplies
    several targets, so the target is part of the key.
    """
    grouped: dict[tuple[tuple[int, int], str], list[SpecRow]] = {}
    for row in rows:
        if row.in_exfor:
            grouped.setdefault((row.target, row.entry), []).append(row)
    return grouped


# ---------------------------------------------------------------------------
# ELM corpus
# ---------------------------------------------------------------------------

# Targets and quadrupole deformations as used by the ELM curation notebooks. The
# corpus is restricted to near-spherical nuclei, where a spherical optical model is
# defensible; the cut drops 42Ca and 44Ca.
BETA2_BY_TARGET: dict[tuple[int, int], float] = {
    (48, 20): 0.1074, (44, 20): 0.251, (42, 20): 0.2454, (40, 20): 0.11712,
    (64, 28): 0.1583,
    (86, 38): 0.1444, (88, 38): 0.1153,
    (90, 40): 0.091911, (92, 40): 0.1014, (94, 40): 0.08810, (96, 40): 0.0604,
    (92, 42): 0.1093, (94, 42): 0.1511,
    (116, 50): 0.111715, (118, 50): 0.110122, (120, 50): 0.107110,
    (122, 50): 0.102811, (124, 50): 0.0095216,
    (138, 56): 0.0938,
    (144, 62): 0.088, (148, 62): 0.142,
    (206, 82): 0.03235, (208, 82): 0.056314,
}
MAX_BETA2 = 0.16

ELM_ELASTIC_EINC_RANGE = (10.0, 200.0)
ELM_PN_EINC_RANGE = (5.0, 200.0)
ELM_MIN_NUM_PTS = 5

# Excitation energy of the isobaric analog state, in MeV, for the (p,n) sector.
ELM_EX_IAS: dict[tuple[int, int], float] = {
    (48, 20): 6.6775, (64, 28): 6.810,
    (90, 40): 5.008, (92, 40): 9.008, (96, 40): 11.03,
    (92, 42): 3.813,
    (116, 50): 8.37419, (118, 50): 9.289, (120, 50): 10.204, (124, 50): 12.20074,
    (208, 82): 15.164,
}
ELM_IAS_WINDOW = 0.3


def elm_targets() -> list[tuple[int, int]]:
    """ELM elastic/Ay targets: the near-spherical subset."""
    return [t for t, beta2 in BETA2_BY_TARGET.items() if beta2 < MAX_BETA2]


def elm_pn_targets() -> list[tuple[int, int]]:
    """ELM (p,n) targets: near-spherical *and* with a tabulated IAS energy."""
    return [t for t in elm_targets() if t in ELM_EX_IAS]
