"""Coverage reporting and the known-missing allowlist.

Every row of every supplement corpus table must be accounted for: it either produced
data, or it is listed in ``spec/known_missing.csv`` with a reason. An unresolved row
that is *not* on the allowlist fails the sector, so a regression -- an EXFOR revision
that withdraws a data set, a parser change that starts silently dropping one -- cannot
pass unnoticed.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .spec import SPEC_DIR

KNOWN_MISSING_PATH = SPEC_DIR / "known_missing.csv"
KNOWN_MISSING_FIELDS = ["corpus", "sector", "target_label", "energy_mev", "subentry",
                        "category", "reason"]


@dataclass(frozen=True)
class KnownMissing:
    corpus: str
    sector: str
    target_label: str
    energy_mev: float
    subentry: str
    category: str
    reason: str

    @property
    def key(self) -> tuple:
        return (self.corpus, self.sector, self.target_label,
                round(self.energy_mev, 6), self.subentry)


def load_known_missing(path: Path = KNOWN_MISSING_PATH) -> dict[tuple, KnownMissing]:
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        rows = [
            KnownMissing(
                corpus=r["corpus"], sector=r["sector"], target_label=r["target_label"],
                energy_mev=float(r["energy_mev"]), subentry=r["subentry"],
                category=r["category"], reason=r["reason"],
            )
            for r in csv.DictReader(f)
        ]
    return {r.key: r for r in rows}


def write_known_missing(rows: list[KnownMissing], path: Path = KNOWN_MISSING_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KNOWN_MISSING_FIELDS)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r.key):
            writer.writerow({
                "corpus": row.corpus, "sector": row.sector,
                "target_label": row.target_label, "energy_mev": row.energy_mev,
                "subentry": row.subentry, "category": row.category, "reason": row.reason,
            })


def outcome_key(outcome) -> tuple:
    row = outcome.row
    return (row.corpus, row.sector, row.target_label, round(row.energy_mev, 6), row.subentry)


def categorize(reason: str) -> str:
    """Bucket an unresolved row's reason, for the allowlist's ``category`` column."""
    if reason.startswith("the supplement marks"):
        return "absent-from-exfor"
    if "not present in the database" in reason or "not present in entry" in reason:
        return "subentry-withdrawn"
    if "not in the x4i3 index" in reason:
        return "x4i3-parse-failure"
    if reason.startswith("retrieval failed") or "not parsed from entry" in reason:
        return "x4i3-parse-failure"
    if reason.startswith("parse failed"):
        return "x4i3-parse-failure"
    if reason.startswith("uncertainty unresolved"):
        return "uncertainty-unresolved"
    if reason.startswith("no measurement within tolerance"):
        return "energy-not-found"
    if reason.startswith("excluded by override"):
        return "excluded"
    if "no uncertainty" in reason or "too sparse" in reason or "analyzing power" in reason:
        return "dropped-in-cleaning"
    return "other"


def unexpected(data, known: dict[tuple, KnownMissing] | None = None) -> list:
    """Unresolved rows that are not on the known-missing allowlist."""
    known = load_known_missing() if known is None else known
    return [o for o in data.unresolved if outcome_key(o) not in known]


def check_coverage(data, known: dict[tuple, KnownMissing] | None = None) -> None:
    """Raise unless every unresolved row is on the allowlist."""
    surprises = unexpected(data, known)
    if surprises:
        lines = "\n".join(
            f"  {o.row.target_label:8s} {o.row.energy_mev:9.3f} {o.row.subentry:9s} {o.reason}"
            for o in surprises[:20]
        )
        more = f"\n  ... and {len(surprises) - 20} more" if len(surprises) > 20 else ""
        raise AssertionError(
            f"{data.corpus}/{data.sector}: {len(surprises)} spec row(s) did not resolve "
            f"and are not listed in spec/known_missing.csv:\n{lines}{more}\n\n"
            "Either fix the retrieval, or add these rows to the allowlist with a reason."
        )


def summarize(data) -> str:
    """A human-readable coverage report for a sector, for display in a notebook."""
    in_exfor = [o for o in data.outcomes if o.row.in_exfor]
    resolved = [o for o in in_exfor if o.resolved]
    lines = [
        f"{data.corpus}/{data.sector}",
        f"  spec rows              {len(data.outcomes)}",
        f"  ... marked absent      {len(data.outcomes) - len(in_exfor)}",
        f"  ... resolved           {len(resolved)} / {len(in_exfor)} ({data.coverage:.1%})",
        f"  measurements           {data.n_measurements}",
        f"  data points            {data.n_points}",
        f"  EXFOR entries          {len(data.entries)}",
    ]
    if data.unresolved:
        buckets: dict[str, int] = {}
        for outcome in data.unresolved:
            buckets[categorize(outcome.reason)] = buckets.get(categorize(outcome.reason), 0) + 1
        lines.append("  unresolved by category")
        for category, n in sorted(buckets.items(), key=lambda kv: -kv[1]):
            lines.append(f"    {category:24s} {n}")
    return "\n".join(lines)


def unresolved_table(data) -> str:
    """Every unresolved row with its reason, for triage in a notebook."""
    if not data.unresolved:
        return "all spec rows resolved"
    width = max(len(o.row.target_label) for o in data.unresolved)
    return "\n".join(
        f"{o.row.target_label:{width}s} {o.row.energy_mev:9.3f} {o.row.subentry:9s} "
        f"[{categorize(o.reason)}] {o.reason}"
        for o in data.unresolved
    )
