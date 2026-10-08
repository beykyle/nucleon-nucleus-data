"""Author-based uncertainties: corrections applied to every corpus record before it is written.

No data point may rest on EXFOR's data-point reader (digitisation) uncertainty alone. The decisions are in
``docs/DATA_CLEANING.md``; the evidence (paper, page, quote) in ``docs/ERROR_EXTRACTION.md`` and
``docs/extraction/``. In order, per record:

1. DROP: records without a usable author source (``docs/FLAGGED_DATASETS.md``, Kyle 2026-10-08), and ELM's figure
   digitisations of Fulmer et al. that duplicate the authors' tables.
2. TABLE: Doering (p,n) to the IAS (EXFOR O0178, digitised from Fig. 3) is replaced by the thesis Table 5
   tabulation, values and errors (``external/doering_1974_table5.csv``). EXFOR points with no table row (e.g. 208Pb
   45 MeV at 161.9 and 164.0 deg) go with it.
3. AUTHOR: at every point whose EXFOR author-error columns are blank, the author uncertainty from the paper
   (``PER_PAPER``) is added in quadrature to the reader uncertainty the record carries. Fricke (O0328) has the
   authors' errors in a column EXFOR relabelled ERR-T -> ERR-1 in 2023 (absolute, in the data's units despite its
   PER-CENT label). Where ERR-1 is blank they are filled: linear interpolation in angle of the relative (cross
   section) or absolute (Ay) error between the nearest points with ERR-1, and flat extrapolation beyond the first
   and last.
4. NORM: the authors' normalisation uncertainty where it differs from the default.

Idempotent: a corrected record carries ``MARK`` in its notes and is left alone; the others are unchanged by a rerun. Which error columns are author or reader
columns is read from each subentry's ERR-ANALYS text, not from the labels, which EXFOR has changed between
releases.
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

MARK = "author-errors v1 (docs/DATA_CLEANING.md)"
ROOT = Path(__file__).resolve().parents[2]
DOERING_CSV = ROOT / "external" / "doering_1974_table5.csv"
#: corpora the cleaning covers (DATA_CLEANING.md decision 3); the Test corpus is not part of it.
SCOPE = {"elm", "kduq", "chuq", "sm3"}

# -- 1. drops -------------------------------------------------------------------------------------------------------

#: subentry -> corpora it is dropped from (docs/FLAGGED_DATASETS.md, Kyle 2026-10-08: "drop them from corpora for
#: now"). O0157 (Devins) was found and O0328 (Fricke) is kept as a partial record (Kyle 2026-10-08).
DROP_FLAGGED = {
    "F1173002": {"elm"}, "O0079006": {"kduq"}, "O0083016": {"kduq"}, "O0083019": {"kduq"},
    "O0225146": {"elm"}, "O0254009": {"kduq"}, "O0254010": {"elm"}, "O0259002": {"elm"},
    "O0272002": {"elm"}, "O0370002": {"elm", "kduq"}, "O0372013": {"elm", "kduq"}, "O0372014": {"elm"},
    "O0382002": {"elm"}, "O0384002": {"elm"}, "O0384003": {"elm"}, "O0387002": {"elm"},
    "O0446002": {"kduq"}, "O0446003": {"kduq"}, "O0458004": {"elm"},
    "O0553004": {"kduq"}, "O0553006": {"kduq"}, "O0553010": {"kduq"}, "O0553014": {"kduq"},
    "O0580002": {"elm"},
    "O1103004": {"chuq"}, "O1103006": {"chuq"}, "O1103012": {"chuq"}, "O1103014": {"chuq"},
    "O1109002": {"chuq"}, "O1109004": {"chuq"}, "O1109005": {"chuq"}, "O1109006": {"chuq"}, "O1109008": {"chuq"},
    "O1199008": {"elm"}, "O1199009": {"elm"},
}
#: ELM carried both EXFOR's figure digitisations (STATUS CURVE, reader errors only) and the authors' tables
#: (O0211012/015/016/017) of Fulmer et al. 61.4 MeV elastic: the digitisations are dropped (Kyle 2026-10-08).
DROP_DUPLICATES = {"O0211004": {"elm"}, "O0211007": {"elm"}, "O0211008": {"elm"}, "O0211009": {"elm"}}

# -- 3. per-paper author uncertainties --------------------------------------------------------------------------------
# A spec maps (angles in deg, y, is_ay, target) -> the author uncertainty per point, absolute in the record's units.


def _rel(frac):
    return lambda th, y, ay, tgt: frac * np.abs(y)


def _abs(a):
    return lambda th, y, ay, tgt: np.full_like(y, a, dtype=float)


def _split(xs, ay):
    """A cross-section rule and an Ay rule."""
    return lambda th, y, is_ay, tgt: (ay if is_ay else xs)(th, y, is_ay, tgt)


def _ramp(lo, hi):
    """Relative error rising linearly in angle from lo (most forward point) to hi (most backward point)."""
    def f(th, y, ay, tgt):
        t = (th - th.min()) / max(th.max() - th.min(), 1e-9)
        return (lo + (hi - lo) * t) * np.abs(y)
    return f


def _step(theta, below, above):
    return lambda th, y, ay, tgt: np.where(th < theta, below, above) * np.abs(y)


def _by_target(table, ay_rule):
    def f(th, y, is_ay, tgt):
        if is_ay:
            return ay_rule(th, y, is_ay, tgt)
        z = re.match(r"([A-Za-z]+)", tgt or "").group(1).capitalize()
        return table[z] * np.abs(y)
    return f


#: entry -> (rule, citation). Values and sources: docs/ERROR_EXTRACTION.md (Kyle: "per paper", 2026-10-08).
PER_PAPER = {
    "O0157": (_ramp(0.035, 0.10), "Devins et al., NP 35 (1962) 617, p.619: absolute errors ~3.5 % forward to ~10 % at extreme backward angles"),
    "O0124": (_rel(0.05), "Put et al., PLB 35 (1971) 311: fitted with 5 %, actual errors always smaller"),
    "O0169": (_split(_rel(0.02), _abs(0.02)), "Wassenaar et al., JPG 15 (1989) 181, p.5: minimal errors 2 % (sigma), 0.01 (Ay); Ay 0.02"),
    "O0239": (_split(_rel(0.02), _abs(0.02)), "Lombardi et al., NPA 188 (1972) 103: 2 % assigned (1 % statistical); Ay typical 0.02"),
    "O0246": (_rel(0.10), "Kruse et al., NPA 169 (1971) 177: 10 % assigned to each point"),
    "O0253": (_rel(0.02), "Dicello et al., PRC 4 (1971) 1130: relative error about 2 %"),
    "O0471": (_rel(0.06), "Burger & Heymann, NPA 243 (1975) 461, p.4: relative errors not more than 6 %"),
    "O0545": (_step(90.0, 0.01, 0.03), "Stautberg & Kraushaar, PR 151 (1966) 969, p.4: statistical < 1 % below 90 deg, < 3 % above"),
    "O0549": (_split(_rel(0.04), _abs(0.03)), "Sinha et al., NPA 183 (1972) 401, p.7: typically ~4 %; Ay +-0.03 forward"),
    "O0552": (_split(_rel(0.015), _abs(0.01)), "Rathmell & Haeberli, NPA 178 (1972) 458: relative 0.5-3 %; Ay 0.002-0.01"),
    "O0091": (_by_target({"Fe": 0.03, "Ni": 0.02}, _abs(0.02)), "Van Hall et al., NPA 291 (1977) 63: 3 % (Fe), 2 % (Ni) assigned; Ay 0.02 (figures)"),
    "O0300": (_rel(0.04), "Kwiatkowski & Wall, NPA 301 (1978) 349: total relative error about 4 %"),
    "O0456": (_rel(0.03), "Brussel & Williams, PR 114 (1959) 525: statistical accuracy about 3 %"),
    "O1104": (_split(_rel(0.02), lambda th, y, ay, tgt: np.maximum(0.02 * np.abs(y), 0.01)),
              "Petit et al., JPG 20 (1994) 1955: minimal error of 2 % assumed for cross section and analysing power"),
}

#: Fricke et al., PR 156 (1967) 1207: the authors' bars ("relative probable errors which include statistical errors
#: and the uncertainty in background subtraction") are EXFOR's ERR-1 (relabelled from ERR-T in 2023), absolute in the
#: data's units although labelled PER-CENT.
COLUMN_AUTHOR = {"O0328": "ERR-1"}

# -- 4. normalisation -----------------------------------------------------------------------------------------------

#: entry or subentry -> the authors' normalisation uncertainty (fraction). Kyle 2026-10-08: apply where it differs.
NORM = {
    "O0178": (0.10, "Doering: 10 % neutron-detection efficiency (ERR-1)"),
    "O0328": (float(np.hypot(0.02, 0.05)), "Fricke: ERR-2 current integration 2 % (+) ERR-3 target thickness 5 %"),
    "O0239": (0.10, "Lombardi: 10 % (Rutherford normalisation at 4 MeV)"),
    "O0300": (0.08, "Kwiatkowski & Wall: absolute accuracy better than 8 %"),
    "O0211012": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211015": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211016": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211017": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
}

# -- EXFOR column classification ----------------------------------------------------------------------------------

READER = re.compile(r"reader|reading|digiti[sz]", re.I)


def _x4_dir():
    from exfor_tools.db import __EXFOR_DB__  # noqa: F401  (sets up the database path)
    import os
    return Path(os.environ.get("X43I_DATAPATH", "")) / "db"


@lru_cache(maxsize=None)
def _err_analys(entry: str, sub: str) -> dict:
    """{label: description} from the ERR-ANALYS of subentry 001 and of this subentry."""
    path = _x4_dir() / entry[:3] / f"{entry}.x4"
    if not path.exists():
        return {}
    lines = path.read_text(errors="replace").splitlines()
    out = {}
    for want in (f"{entry}001", sub):
        on, block = False, []
        for line in lines:
            if line.startswith("SUBENT") and want in line[:30]:
                on = True
            if on:
                if line.startswith("ENDBIB"):
                    break
                key, body = line[:11].strip(), line[11:66]
                if key and key != "ERR-ANALYS" and block:
                    break
                if key == "ERR-ANALYS" or (block and not key):
                    block.append(body)
        for m in re.finditer(r"\(([A-Z0-9+\-]+)(?:,[^)]*)?\)\.?\s*([^()]*)", " ".join(block)):
            out[m.group(1)] = m.group(2).strip()
    return out


@lru_cache(maxsize=None)
def _exfor_block(sub: str):
    from .errors import entry_data_sets

    blocks = [d for k, d in entry_data_sets(sub[:5]).items() if k[1] == sub]
    return blocks[0] if blocks else None


def _author_matrix(sub: str, energy: float):
    """-> (angles, data, {label: values}) of the author-error columns of an EXFOR subentry at one energy,
    or None. Author columns: uncertainty columns on the observable that are neither reader/digitisation columns nor
    common systematic ERR-n columns (constant over the subentry)."""
    d = _exfor_block(sub)
    if d is None:
        return None
    labels = list(d.labels)
    ang = next((i for i, l in enumerate(labels) if l.startswith("ANG") and "ERR" not in l), None)
    dat = labels.index("DATA") if "DATA" in labels else None
    if ang is None or dat is None:
        return None
    desc = _err_analys(sub[:5], sub)
    rows = [r for r in d.data if not ("EN" in labels and r[labels.index("EN")] is not None
                                       and abs(r[labels.index("EN")] - energy) > 1e-3 * max(1.0, energy))]
    cols = {}
    for i, l in enumerate(labels):
        if "ERR" not in l or l.startswith(("ANG", "EN", "E-")):
            continue
        if l == "ERR-DIG" or READER.search(desc.get(l, "")):
            continue
        vals = [r[i] for r in rows]
        if re.match(r"ERR-\d", l) and len({v for v in vals}) == 1 and sub[:5] not in COLUMN_AUTHOR:
            continue
        cols[l] = np.array([v if v is not None else 0.0 for v in vals], dtype=float)
        if "PER-CENT" in d.units[i].upper() and sub[:5] not in COLUMN_AUTHOR:
            cols[l] = cols[l] / 100 * np.abs(np.array([r[dat] or 0.0 for r in rows], dtype=float))
    return (np.array([r[ang] for r in rows], dtype=float), np.array([r[dat] or 0.0 for r in rows], dtype=float), cols)


def _match(x, ex_angles):
    """Index of the EXFOR row at each record angle (within 0.06 deg), or -1."""
    out = np.full(len(x), -1)
    for k, xi in enumerate(x):
        if len(ex_angles):
            j = int(np.argmin(np.abs(ex_angles - xi)))
            if abs(ex_angles[j] - xi) < 0.06:
                out[k] = j
    return out


def _fill(th, known):
    """Interpolate known values (NaN = unknown) linearly in angle; flat beyond the first and last known point."""
    ok = ~np.isnan(known)
    if not ok.any():
        return known
    return np.interp(th, th[ok], known[ok])


# -- application ----------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _doering() -> dict:
    out = {}
    with open(DOERING_CSV) as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        for r in rows:
            out.setdefault(r["exfor_subentry"], []).append((float(r["theta_cm_deg"]), float(r["dsdo_mb_sr"]),
                                                            float(r["err_pct"])))
    return out


def _note(p, text):
    p.setdefault("notes", []).append(text)


def correct(payload: dict, corpus: str) -> dict | None:
    """The corrected payload, or None if the record is dropped. Never applied twice (MARK)."""
    if corpus not in SCOPE or MARK in (payload.get("notes") or []):
        return payload
    sub = str(payload.get("EXFORAccessionNumber", ""))[:8]
    entry = sub[:5]
    for table in (DROP_FLAGGED, DROP_DUPLICATES):
        if corpus in table.get(sub, set()):
            return None
    if "deg" not in str(payload.get("x_units", "")).lower():  # energy distributions: none of this applies
        return payload
    data = payload["data"]
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    ye = np.asarray(data["y_err"], dtype=float)
    is_ay = payload.get("type") == "APower"
    tgt = payload.get("target", "")
    changed = False

    if sub in _doering():  # 2. the thesis tabulation
        t = sorted(_doering()[sub])
        scale = 1e-3 if payload.get("y_units") == "b/sr" else 1.0
        data["x"] = [a for a, _, _ in t]
        data["y"] = [v * scale for _, v, _ in t]
        data["y_err"] = [v * scale * e / 100 for _, v, e in t]
        _note(payload, f"values and errors replaced by Doering thesis (MSU 1974) Table 5, {len(t)} rows "
                       f"(EXFOR {len(x)} digitised points); external/doering_1974_table5.csv")
        changed = True
    else:  # 3. author uncertainties where EXFOR's are blank
        m = _author_matrix(sub, float(payload.get("energy") or 0.0))
        if entry in COLUMN_AUTHOR and m is not None:
            ex_th, ex_y, cols = m
            col = cols.get(COLUMN_AUTHOR[entry])
            if col is not None:
                idx = _match(x, ex_th)
                # the author error as a fraction (cross sections) or absolute (Ay), at the matched points
                known = np.full(len(x), np.nan)
                for k, j in enumerate(idx):
                    if j >= 0 and col[j] > 0:
                        known[k] = col[j] if is_ay else col[j] / abs(ex_y[j]) if ex_y[j] else np.nan
                filled = _fill(x, known)
                author = filled if is_ay else filled * np.abs(y)
                blank = np.isnan(known)
                new = np.sqrt(ye ** 2 + author ** 2)  # reader (+) author, everywhere: the record held reader only
                data["y_err"] = [float(v) for v in new]
                _note(payload, f"author errors from EXFOR {COLUMN_AUTHOR[entry]} (relabelled from ERR-T in 2023; "
                               f"absolute in data units) added in quadrature to the reader error; {int(blank.sum())} "
                               f"of {len(x)} points filled by interpolation in angle, flat beyond the ends")
                changed = True
        elif entry in PER_PAPER:
            rule, cite = PER_PAPER[entry]
            if m is None:
                blank = np.ones(len(x), dtype=bool)
            else:
                ex_th, ex_y, cols = m
                idx = _match(x, ex_th)
                has = np.zeros(len(x), dtype=bool)
                for k, j in enumerate(idx):
                    if j >= 0:
                        has[k] = any(c[j] > 0 for c in cols.values())
                blank = ~has if cols else np.ones(len(x), dtype=bool)
            if blank.any():
                author = rule(x, y, is_ay, tgt)
                new = ye.copy()
                new[blank] = np.sqrt(ye[blank] ** 2 + author[blank] ** 2)
                data["y_err"] = [float(v) for v in new]
                _note(payload, f"author uncertainty at {int(blank.sum())} of {len(x)} points without one in EXFOR "
                               f"(added in quadrature to the reader error): {cite}")
                changed = True

    for key in (sub, entry):  # 4. normalisation
        if key in NORM:
            val, why = NORM[key]
            if abs(float(data.get("systematic_normalization_error") or 0.0) - val) > 1e-9:
                data["systematic_normalization_error"] = val
                _note(payload, f"normalisation uncertainty {100 * val:.1f} % from the authors: {why}")
                changed = True
            break

    if changed:
        _note(payload, MARK)
    return payload


def apply(records, corpus: str, sector: str):
    """Correct a sector's records (serialize.Record) before writing; drops removed."""
    out = []
    for r in records:
        p = correct(r.payload, corpus)
        if p is not None:
            r.payload = p
            out.append(r)
    return out
