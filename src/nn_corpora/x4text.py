"""The free-text BIB section of EXFOR entries, read straight from the local X4 database.

x4i3 parses the data tables but not the bibliography keywords this package needs to judge uncertainties: the
ERR-ANALYS text that says which error column is the authors' and which is the compilers' data-point reader
(digitisation) uncertainty, and the STATUS that says whether the numbers come from a table or were read off a
figure (CURVE).
"""

from __future__ import annotations

import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

#: ERR-ANALYS descriptions of a data-point reader (digitisation) uncertainty
READER = re.compile(r"reader|reading|digiti[sz]", re.I)


def x4_dir() -> Path:
    """The ``db`` directory of the database x4i3 is using: the release ``X43I_DATAPATH`` names (see
    ``scripts/setup_exfor_db.sh``), or else the snapshot x4i3 downloads for itself."""
    import x4i3

    return Path(x4i3.fullDBPath)


@lru_cache(maxsize=256)
def subentries(entry: str) -> dict[str, tuple[str, ...]]:
    """{subentry accession number: its lines (columns 1-66)} of one entry.

    Raises FileNotFoundError if the database has no file for the entry: an empty result would silently read as
    "no ERR-ANALYS", which turns reader columns into author columns.
    """
    path = x4_dir() / entry[:3] / f"{entry}.x4"
    if not path.exists():
        raise FileNotFoundError(f"EXFOR entry {entry}: no {path}")
    out, cur = {}, None
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("SUBENT"):
            cur = line[14:22].strip()
            out[cur] = []
        if cur:
            out[cur].append(line[:66].rstrip())
        if line.startswith("ENDSUBENT"):
            cur = None
    return {k: tuple(v) for k, v in out.items()}


def bib_lines(lines) -> dict[str, list[str]]:
    """{BIB keyword: its text lines (columns 12-66)}."""
    fields, key, in_bib = defaultdict(list), None, False
    for line in lines:
        if line.startswith("BIB"):
            in_bib = True
            continue
        if line.startswith("ENDBIB"):
            break
        if not in_bib:
            continue
        k = line[:11].strip()
        if k:
            key = k
        if key:
            fields[key].append(line[11:66].rstrip())
    return dict(fields)


def bib_fields(lines) -> dict[str, str]:
    """{BIB keyword: its text joined into one line}."""
    return {k: " ".join(s.strip() for s in v if s.strip()) for k, v in bib_lines(lines).items()}


def parse_err_analys(lines) -> dict[str, str]:
    """{label: description} from ERR-ANALYS lines; a label opens a line as ``(LABEL)`` or ``(LABEL,...)``."""
    desc, cur = {}, None
    for body in lines:
        m = re.match(r"\s*\(([A-Z0-9+\-]+)(?:,[^)]*)?\)\.?(.*)", body)
        if m:
            cur = m.group(1)
            desc[cur] = m.group(2).strip()
        elif cur:
            desc[cur] = (desc[cur] + " " + body.strip()).strip()
    return desc


def err_analys(subentry: str) -> dict[str, str]:
    """{label: description} for one subentry: the entry's common subentry 001, overridden by the subentry's own."""
    entry = subentry[:5]
    subs = subentries(entry)
    out = {}
    for sub in (f"{entry}001", subentry[:8]):
        out.update(parse_err_analys(bib_lines(subs.get(sub, ())).get("ERR-ANALYS", [])))
    return out


def is_reader(label: str, descriptions: dict[str, str]) -> bool:
    """A data-point reader (digitisation) uncertainty column: ERR-DIG, or described as one in ERR-ANALYS."""
    return label == "ERR-DIG" or bool(READER.search(descriptions.get(label, "")))
