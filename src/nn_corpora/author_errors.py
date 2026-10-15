"""Author-based uncertainties: our best evaluation of the experimental uncertainty of a corpus record.

The corpora come in two kinds. KDUQ, CHUQ and Test are static: they reproduce the published corpora as their
papers' rules curate them, and these corrections never touch them. ELM and sm3 are evaluated: every record passes
through ``correct`` before it is written. ``kduq_evaluated``, ``chuq_evaluated`` and ``test_evaluated`` are copies of
the static corpora with the same corrections (``scripts/apply_author_errors.py``), so a user can choose either. The
evaluation uses the EXFOR entry and the publication, and where the two disagree the publication wins.

No data point may rest on EXFOR's data-point reader (digitisation) uncertainty alone: that is the compilers' estimate
of how precisely they read a point off a published figure, not a measurement uncertainty. What each rule does, and the
publication behind it, is documented in ``docs/AUTHOR_UNCERTAINTIES.md``; the quotes from the papers in
``docs/AUTHOR_UNCERTAINTY_SOURCES.md``. In order, per record:

1. DROP: records with no usable author source of uncertainty (``DROP_FLAGGED``), and ELM's figure digitisations of
   Fulmer et al. that duplicate the authors' tables (``DROP_DUPLICATES``).
2. TABLE: Doering (p,n) to the IAS (EXFOR O0178, digitised from a figure) is replaced by the thesis Table 5
   tabulation, values and errors (``external/doering_1974_table5.csv``). EXFOR points with no table row go with it.
3. AUTHOR: Fricke (O0328) has the authors' errors in a column EXFOR relabelled ERR-T -> ERR-1 in 2023
   (``COLUMN_AUTHOR``); the per-point error becomes EXFOR's reader error (+) that column, filled by interpolation in
   angle where it is blank. For the entries in ``COLUMNS``, whose error columns no label-based rule reads correctly,
   the per-point error is rebuilt from the columns ERR-ANALYS names: reader (+) the authors' per-point columns, and
   the normalisation from the authors' common column. For the entries in ``PER_PAPER``, the uncertainty the paper
   states is added in quadrature at every point whose EXFOR author-error columns are blank.
4. NORM: the authors' normalisation uncertainty where it differs from the record's: of the cross sections
   (``NORM``) or, separately, of the analysing powers (``NORM_AY``, e.g. a beam-polarisation uncertainty).

Which error columns are author or reader columns is read from each subentry's ERR-ANALYS text (``classify``), not
from the labels, which EXFOR has changed between releases. A corrected record carries ``MARK`` in its notes and is
never corrected twice.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import spec, x4text
from .errors import candidate_labels, entry_data_sets
from .retrieve import _TO_MEV

MARK = "author-errors v4 (docs/AUTHOR_UNCERTAINTIES.md)"
ROOT = Path(__file__).resolve().parents[2]
DOERING_CSV = ROOT / "external" / "doering_1974_table5.csv"
#: static (tabulated) corpus -> its evaluated copy, for those registered with one (``spec.TABULATED``)
EVALUATED = {name: f"{name}_evaluated" for name, c in spec.TABULATED.items() if c.evaluated_copy}
#: corpora the corrections cover; the static corpora never are
SCOPE = {"elm", "sm3", *EVALUATED.values()}
#: largest angle difference (deg) at which a record point is the same point as an EXFOR row
ANGLE_TOL = 0.06
#: largest lab -> centre-of-mass angle shift (deg) accepted when matching records to EXFOR rows by position
FRAME_TOL = 5.0

# -- 1. drops -------------------------------------------------------------------------------------------------------

#: subentries removed from every evaluated corpus: no author statement of the per-point uncertainty could be found
#: (no paper available, or the paper gives none), so the data would rest on the reader error alone.
DROP_FLAGGED = {
    "F1173002", "O0079006", "O0083016", "O0083019", "O0225146", "O0254009", "O0254010", "O0259002",
    "O0272002", "O0370002", "O0372013", "O0372014", "O0382002", "O0384002", "O0384003", "O0387002",
    "O0446002", "O0446003", "O0458004", "O0553004", "O0553006", "O0553010", "O0553014", "O0580002",
    "O1103004", "O1103006", "O1103012", "O1103014", "O1109002", "O1109004", "O1109005", "O1109006", "O1109008",
    "O1199008", "O1199009",
    # entering ELM with its 0 MeV window and 112Sn (2026-10-14); EXFOR only, the publications not checked
    "F1407013", "O1823002", "F0930002",
}
#: Fulmer et al. 61.4 MeV elastic is in EXFOR twice: figure digitisations (STATUS CURVE, reader errors only) and the
#: authors' tables (O0211012/015/016/017). ELM carried both; the digitisations are removed, and only the tables kept.
#: Van Oers et al. 208Pb(p,p) 21-47.3 MeV is in EXFOR twice: figure digitisations with a flat 6 % reader error
#: (O0287004-010) and the tabulated data with per-point author errors from B. Clark's collection (O0287011-017, the
#: version sm3 uses). ELM carried both at all seven energies (found by the elm_lane data audit, 2026-10-14).
DROP_DUPLICATES = {"O0211004", "O0211007", "O0211008", "O0211009",
                   "O0287004", "O0287005", "O0287006", "O0287007", "O0287008", "O0287009", "O0287010"}
#: EXFOR entries (5 characters) or subentries (8) removed from every evaluated corpus as inconsistent -> reason
DROP_INCONSISTENT = {
    "14662004": ("dropped as inconsistent (2026-10-14): Pruitt, thesis (2019), 124Sn(n,n) 11 MeV lies 1.4-2.5x above "
                 "Rapaport et al. (10817010) at the same energy and 1.57x KD03 (median), while Pruitt's own 17 MeV set "
                 "(14662005) agrees with KD03 (0.95); neither TALYS compound elastic (0.003 mb) nor the 2+ inelastic "
                 "(2-5 mb/sr vs a 12-110 mb/sr excess) accounts for it; 10 % errors on both sets leave chi2 46/16"),
    "C0622": ("dropped as inconsistent (elm_lane data audit, 2026-10-14): Moyer, Finlay et al., NPA 352, 221 (1981) "
              "92Mo(p,p) 25-45 MeV quotes 0.1-0.7 % errors with no normalisation, departs 1.4-2.5x from both KD03 and "
              "the ELM-Lane prior centre away from forward angles, and is ~2x off D0295010 at 30 MeV"),
}

# -- 3. per-paper author uncertainties --------------------------------------------------------------------------------
# A rule maps (angles in deg, y, is_ay, target) -> the author uncertainty per point, absolute in the record's units.


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


def _by_element(table, ay_rule):
    def f(th, y, is_ay, tgt):
        if is_ay:
            return ay_rule(th, y, is_ay, tgt)
        return table[re.search(r"[A-Za-z]+", tgt or "").group(0).capitalize()] * np.abs(y)
    return f


#: entry -> (rule, citation)
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
    "O0091": (_by_element({"Fe": 0.03, "Ni": 0.02}, _abs(0.02)), "Van Hall et al., NPA 291 (1977) 63: 3 % (Fe), 2 % (Ni) assigned; Ay 0.02 (figures)"),
    "O0300": (_rel(0.04), "Kwiatkowski & Wall, NPA 301 (1978) 349: total relative error about 4 %"),
    "O0456": (_rel(0.03), "Brussel & Williams, PR 114 (1959) 525: statistical accuracy about 3 %"),
    "F1100": (_step(30.0, 0.05, 0.03), "Kurepin, Madsen & Albek, Izv. 31 (1967) 195, as EXFOR's ERR-ANALYS "
              "quotes it (no ERR-S column): 5 % at 20 deg, 2-3 % beyond 30 deg"),
    "O1104": (_split(_rel(0.02), lambda th, y, ay, tgt: np.maximum(0.02 * np.abs(y), 0.01)),
              "Petit et al., JPG 20 (1994) 1955: minimal error of 2 % assumed for cross section and analysing power"),
}

#: entry -> the EXFOR column holding the authors' per-point errors, read as absolute in the data's units whatever its
#: unit label. Fricke et al., PR 156 (1967) 1207: the authors' bars ("relative probable errors which include
#: statistical errors and the uncertainty in background subtraction") are ERR-1, relabelled from ERR-T in 2023 and
#: labelled PER-CENT although the values are absolute.
COLUMN_AUTHOR = {"O0328": "ERR-1"}

#: subentry or entry -> (the authors' per-point error columns, their normalisation columns, what ERR-ANALYS says).
#: The per-point error is EXFOR's reader error (+) the per-point columns; the normalisation is the normalisation
#: columns (constant) in quadrature, or the record's own if there are none. These are the entries where the
#: supplement's label preference (ERR-T > DATA-ERR > ERR-S > ERR-DIG) picks the wrong column or folds a normalisation
#: into the per-point error; ELM's curation (``elm.PARSE_RECIPES``) read most of them the same way.
COLUMNS = {
    "O0142": (["ERR-T"], ["ERR-1"], "ERR-T reported by the authors; ERR-1 normalisation (target thickness)"),
    "O0287002": (["DATA-ERR"], ["ERR-1"], "ERR-1 absolute uncertainty 8.3 % (calibration, target thickness)"),
    **{f"O0287{k:03d}": (["ERR-T"], [], "DATA-ERR is the data-point reader uncertainty; ERR-T the authors' error "
                                       "(< 3 %)") for k in range(4, 11)},
    "O0302": (["DATA-ERR1"], ["DATA-ERR2"], "DATA-ERR1 5 % for the relative, DATA-ERR2 7 % for the absolute cross sections"),
    "O0434008": (["ERR-S"], [], "DATA-ERR is the data-point reader uncertainty; ERR-S the authors' overall < 5 %"),
    "T0101": (["DATA-ERR"], ["DATA-ERR1"], "DATA-ERR total relative uncertainty; DATA-ERR1 total systematic 8-10 %"),
    "10633": (["DATA-ERR1"], ["DATA-ERR2"], "DATA-ERR1 relative uncertainties; DATA-ERR2 normalization error"),
    "12701": (["DATA-ERR1"], ["DATA-ERR2"], "DATA-ERR1 relative uncertainties; DATA-ERR2 normalization error"),
    "22987": (["ERR-T"], [], "ERR-T total (statistical, background subtraction, multiple scattering); ERR-S its "
                             "statistical part"),
}
#: entry -> columns ERR-ANALYS (or their values) show to be a common uncertainty, not a per-point one
COMMON = {
    "D0289": ({"DATA-ERR1", "DATA-ERR"}, "DATA-ERR1 an undescribed constant 5 % (cross sections); DATA-ERR the "
              "polarimeter calibration (analysing powers)"),
    "O0090": ({"ERR-T"}, "an absolute error in the cross section of 10 %, including the efficiency"),
    "22987": ({"ERR-1"}, "the cross-section change from the angle uncertainty (target and chamber positions, about "
              "1 deg): an angle offset common to the data set"),
}


def columns_rule(subentry: str):
    return COLUMNS.get(subentry[:8]) or COLUMNS.get(subentry[:5])


def is_common(label: str, subentry: str) -> bool:
    """A column that is never a per-point uncertainty of the observable: a systematic (ERR-SYS), a monitor, beam
    polarisation or auxiliary-quantity (MISC) error, or one the tables above name as common for the entry."""
    if label == "ERR-SYS" or any(f in label for f in ("MONIT", "POL", "MISC")):
        return True
    return label in (columns_rule(subentry) or ((), (), ""))[1] or label in COMMON.get(subentry[:5], ((),))[0]

#: subentry -> (rule, citation): the authors' stated *total* per-point uncertainty where EXFOR carries only part of it
#: in its error column; y_err = max(EXFOR's error, the total). Rapaport et al., NPA 341 (1980) 56, Sn(n,n) 11 and
#: 24 MeV: ERR-ANALYS gives ERR-T 5-15 % (statistics, multiple scattering, inelastic and compound contributions,
#: angle, efficiency) but the data carry only DATA-ERR, the "absolute" part (geometry, yields, monitor), 3-6 %. The
#: range is read as rising with angle, as for Devins (O0157). Found comparing 124Sn(n,n) 11 MeV with Pruitt (14662004,
#: dropped as inconsistent), 2026-10-14.
TOTAL = {f"10817{k:03d}": (_ramp(0.05, 0.15), "Rapaport et al., NPA 341 (1980) 56, EXFOR ERR-ANALYS: total "
                                             "uncertainty (ERR-T) 5-15 %, not filed as a column; read as rising "
                                             "from 5 % forward to 15 % at the most backward angle")
         for k in range(6, 11)}

# -- 4. normalisation -----------------------------------------------------------------------------------------------

#: entry or subentry -> the authors' normalisation uncertainty (fraction) of the cross sections, applied where it
#: differs from the record's; never to analysing powers
NORM = {
    "O0178": (float(np.hypot(0.10, 0.05)), "Doering: neutron-detection efficiency about 10 % (+) target thickness, "
              "beam integration and neutron attenuation, less than 5 %"),
    "O0328": (float(np.hypot(0.02, 0.05)), "Fricke: ERR-2 current integration 2 % (+) ERR-3 target thickness 5 %"),
    "O0239": (0.10, "Lombardi: 10 % (Rutherford normalisation at 4 MeV)"),
    "O0300": (0.08, "Kwiatkowski & Wall: absolute accuracy better than 8 %"),
    "O0211012": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211015": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211016": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
    "O0211017": (float(np.hypot(0.05, 0.10)), "Fulmer: thickness 5 % (+) charge collection 10 %"),
}
#: entry -> the authors' normalisation uncertainty of the analysing powers (fraction): a beam-polarisation scale.
#: Analysing powers of other entries keep their curated normalisation: the cross-section figures above (target
#: thickness, beam integration, efficiency) cancel in a ratio of counts.
NORM_AY = {
    "O0328": (0.018, "Fricke: beam polarisation (27.4 +- 0.5) %, including the uncertainty in P_C"),
}

# -- EXFOR error columns --------------------------------------------------------------------------------------------


def classify(subentry: str, ds) -> tuple[list[str], list[str], list[str]]:
    """(reader, author, systematic) uncertainty columns of an EXFOR data set.

    - reader: ERR-DIG, or any column ERR-ANALYS describes as a data-point reader / reading / digitisation error;
    - systematic: a numbered ERR-n column with the same value in every row (a common normalisation-type error),
      and the columns ``is_common`` names;
    - author: every other uncertainty column on the observable.
    """
    labels = list(ds.labels)
    desc = x4text.err_analys(subentry)
    forced = COLUMN_AUTHOR.get(subentry[:5])
    cands = candidate_labels(labels)
    reader = [lab for lab in cands if x4text.is_reader(lab, desc)]
    systematic = [lab for lab in cands if lab not in reader and lab != forced and (
        is_common(lab, subentry)
        or (re.match(r"ERR-\d", lab) and len({r[labels.index(lab)] for r in ds.data}) == 1))]
    author = [lab for lab in cands if lab not in reader and lab not in systematic]
    return reader, author, systematic


@dataclass
class ExforPoints:
    """The rows of one EXFOR subentry at one energy; uncertainties absolute, in the units of ``data``."""

    angles: np.ndarray
    data: np.ndarray
    reader: np.ndarray  # the largest reader column (zero where blank)
    author: dict[str, np.ndarray]  # author columns (zero where blank)
    reader_cols: list[str]
    systematic: dict[str, np.ndarray] | None = None  # common (normalisation-type) columns

    @property
    def has_author(self) -> np.ndarray:
        return np.any([v > 0 for v in self.author.values()], axis=0) if self.author else np.zeros(len(self.angles), bool)


def _absolute(ds, label, rows, dat, as_absolute=False):
    i = list(ds.labels).index(label)
    vals = np.array([r[i] if r[i] is not None else 0.0 for r in rows], dtype=float)
    if "PER-CENT" in ds.units[i].upper() and not as_absolute:
        vals = vals / 100 * np.abs(dat)
    return vals


def _blocks(subentry: str) -> list:
    """The x4i3 data sets of a subentry; empty if the entry cannot be parsed."""
    try:
        return [d for k, d in entry_data_sets(subentry[:5]).items() if k[1] == subentry[:8]]
    except Exception:  # noqa: BLE001  (entries x4i3 cannot parse)
        return []


def energy_column(ds) -> tuple[int | None, float]:
    """(index of the EN column or None, factor converting it to MeV)."""
    labels = list(ds.labels)
    if "EN" not in labels:
        return None, 1.0
    i = labels.index("EN")
    unit = str(ds.units[i]).upper()
    if unit not in _TO_MEV:
        raise ValueError(f"EN in unknown unit {ds.units[i]!r}")
    return i, _TO_MEV[unit]


def rows_at(ds, energy: float | None) -> list:
    """The data set's rows at ``energy`` in MeV (within 0.1 %), or all rows if None or the set has no EN column."""
    en, to_mev = energy_column(ds)
    if energy is None or en is None:
        return list(ds.data)
    return [r for r in ds.data if r[en] is None or abs(r[en] * to_mev - energy) <= 1e-3 * max(1.0, energy)]


def is_polarisation(ds) -> bool:
    """A polarisation data set (REACTION quantity POL/DA, e.g. ``POL/DA,,ANA``), not a cross section (DA, or DA,RTH:
    a ratio to Rutherford, dimensionless like an analysing power)."""
    try:
        return str(ds.reaction[0].quantity[0]).startswith("POL")
    except (AttributeError, IndexError, TypeError):
        return False


def best_data_set(subentry: str, energy: float | None, x=None, is_ay: bool | None = None):
    """(x4i3 data set, its ``ExforPoints``) of an EXFOR subentry at ``energy`` (all rows if None), or None if it
    cannot be read or has no angle and data columns (e.g. given in cos(theta)). When the subentry holds several data
    sets, the one whose angles match ``x`` best; ``is_ay`` True keeps only polarisation (analysing-power) data
    sets, False only the others (``is_polarisation``)."""
    blocks = _blocks(subentry)
    best = None
    for ds in blocks:
        labels = list(ds.labels)
        ang = next((i for i, l in enumerate(labels) if l.startswith("ANG") and "ERR" not in l and "RSL" not in l
                    and l != "ANG-NRM"), None)
        dat = next((i for i, l in enumerate(labels) if l.startswith("DATA") and "ERR" not in l), None)
        if ang is None or dat is None:
            continue
        if is_ay is not None and is_polarisation(ds) != is_ay:
            continue
        rows = rows_at(ds, energy)
        angles = np.array([r[ang] for r in rows], dtype=float)
        data = np.array([r[dat] if r[dat] is not None else 0.0 for r in rows], dtype=float)
        reader_cols, author_cols, sys_cols = classify(subentry, ds)
        forced = COLUMN_AUTHOR.get(subentry[:5])
        # several reader columns are alternatives (e.g. O0124: one per figure the points were read from), not parts
        reader = np.max([_absolute(ds, lab, rows, data) for lab in reader_cols] or [np.zeros(len(rows))], axis=0)
        author = {lab: _absolute(ds, lab, rows, data, as_absolute=(lab == forced)) for lab in author_cols}
        for lab in [lab for lab in author if lab.startswith("+") and "-" + lab[1:] in author]:
            author[lab[1:]] = (author.pop(lab) + author.pop("-" + lab[1:])) / 2  # asymmetric: the average
        systematic = {lab: _absolute(ds, lab, rows, data) for lab in sys_cols}
        pts = ExforPoints(angles, data, reader, author, reader_cols, systematic)
        score = 0 if x is None else int((match(x, angles) >= 0).sum())
        if best is None or score > best[0]:
            best = (score, ds, pts)
    return best[1:] if best else None


def exfor_points(subentry: str, energy: float | None, x=None, is_ay: bool | None = None) -> ExforPoints | None:
    """The rows of an EXFOR subentry at ``energy``, from ``best_data_set``; None if it cannot be read."""
    found = best_data_set(subentry, energy, x, is_ay)
    return found[1] if found else None


def match(x, ex_angles) -> np.ndarray:
    """Index of the EXFOR row at each record angle, or -1.

    Rows match on angle (within ``ANGLE_TOL``). Records of EXFOR data given in the laboratory frame carry
    centre-of-mass angles, which match no row; such a record is matched row by row instead, provided it has as many
    points as EXFOR, in the same order, and no angle moved by more than ``FRAME_TOL``.
    """
    x = np.asarray(x, dtype=float)
    ex_angles = np.asarray(ex_angles, dtype=float)
    out = np.full(len(x), -1)
    if len(ex_angles):
        for k, xi in enumerate(x):
            j = int(np.argmin(np.abs(ex_angles - xi)))
            if abs(ex_angles[j] - xi) < ANGLE_TOL:
                out[k] = j
    if (out < 0).any() and len(x) == len(ex_angles):
        order = np.argsort(ex_angles, kind="stable")
        if np.all(np.diff(x) > 0) and np.all(np.abs(x - ex_angles[order]) < FRAME_TOL):
            return order
    return out


def unit_factor(p: ExforPoints, idx, y, is_ay) -> tuple[np.ndarray, np.ndarray]:
    """(factor, consistent): EXFOR absolute uncertainties at rows ``idx`` times ``factor`` are in the units of a
    record with values ``y``; ``consistent`` marks the points whose value is EXFOR's.

    Analysing powers are absolute in both (factor 1); a point is consistent where the values agree. For cross
    sections the factor is the ratio of the record's value to EXFOR's (units, a ratio to Rutherford), which a line in
    log sin(theta/2) describes (slope 0, or about 4 for a ratio to Rutherford). A point off that line by more than a
    factor 3 is a value the curation rescaled (``elm.POINT_FIXES``, e.g. 12701005 by 10) while keeping EXFOR's
    absolute error; it takes the line's factor.
    """
    y = np.asarray(y, dtype=float)
    ex = p.data[idx]
    if is_ay:
        return np.ones(len(y)), np.abs(y - ex) <= np.maximum(1e-3, 0.01 * np.abs(ex))
    lu = np.log(np.abs(y) / np.where(ex != 0, np.abs(ex), np.nan))
    with np.errstate(divide="ignore"):
        ls = np.log(np.sin(np.radians(np.asarray([p.angles[i] for i in idx], dtype=float)) / 2))
    ok = np.isfinite(lu) & np.isfinite(ls)
    for _ in range(2):
        if ok.sum() < 2:
            break
        with np.errstate(invalid="ignore"):
            fit = np.polyval(np.polyfit(ls[ok], lu[ok], 1), ls)
        ok = np.isfinite(lu) & (np.abs(lu - fit) <= np.log(3.0))
    if ok.sum() >= 2:
        lu = np.where(ok | ~np.isfinite(fit), lu, fit)
    return np.exp(lu), ok


def to_record(vals, p: ExforPoints, idx, y, is_ay) -> np.ndarray:
    """EXFOR absolute uncertainties at rows ``idx``, in the units of a record with values ``y`` (``unit_factor``)."""
    return np.asarray(vals, dtype=float) * unit_factor(p, idx, y, is_ay)[0]


def audit_record(rec: dict) -> dict | None:
    """A corpus record's points that rest on a reader error: None if there are none, ``{"error": ...}`` if its
    subentry cannot be read. Only angular distributions are audited; counts and angles are the record's.

    - reader-only: EXFOR has a reader error and no author error at the point;
    - author unused: EXFOR has one, but the record's error is less than 95 % of it (the curation took another
      column). Points whose value is not EXFOR's, or whose angle the record repeats, cannot be checked;
    - unmatched: record points at no EXFOR angle (e.g. the Doering table's own angles). They cannot be cleared, so
      when EXFOR has reader-only rows they count as reader-only.
    """
    if "deg" not in str(rec.get("x_units", "")).lower():
        return None
    sub = str(rec["EXFORAccessionNumber"])
    is_ay = rec.get("type") == "APower"
    x = np.asarray(rec["data"]["x"], dtype=float)
    p = exfor_points(sub, rec.get("energy"), x, is_ay)
    if p is None:
        if _blocks(sub):  # readable, but not in angle (e.g. cos theta)
            return None
        return dict(subentry=sub, error="EXFOR subentry not readable")
    idx = match(x, p.angles)
    hit = idx >= 0
    reader_rows = ~p.has_author if p.reader_cols else np.zeros(len(p.angles), bool)
    mask = np.zeros(len(x), bool)
    mask[hit] = reader_rows[idx[hit]]
    if reader_rows.any():
        mask |= ~hit
    unused = []
    if p.author and hit.all() and sub[:8] not in doering_table():
        y = np.asarray(rec["data"]["y"], dtype=float)
        factor, ok = unit_factor(p, idx, y, is_ay)
        ok &= np.array([np.sum(x == v) == 1 for v in x])
        author = np.max(list(p.author.values()), axis=0)[idx] * factor
        ye = np.asarray(rec["data"]["y_err"], dtype=float)
        unused = [float(x[k]) for k in np.flatnonzero(ok & (ye < 0.95 * author))]
    if not mask.any() and not unused:
        return None
    return dict(subentry=sub, energy=rec.get("energy"), n_points=len(x), n_reader_only=int(mask.sum()),
                reader_only_angles=[float(a) for a in x[mask]], unmatched_angles=[float(a) for a in x[~hit]],
                author_unused_angles=unused, reader_cols=p.reader_cols, author_cols=list(p.author),
                corrected=MARK in (rec.get("notes") or []))


def _fill(th, known):
    """Interpolate known values (NaN = unknown) linearly in angle; flat beyond the first and last known point."""
    ok = ~np.isnan(known)
    if not ok.any():
        raise ValueError("no known value to interpolate from")
    return np.interp(th, th[ok], known[ok])


# -- application ----------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def doering_table() -> dict[str, list[tuple[float, float, float]]]:
    """subentry -> [(c.m. angle deg, cross section mb/sr, relative error %)] from the thesis Table 5."""
    out = {}
    with open(DOERING_CSV) as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            out.setdefault(r["exfor_subentry"], []).append(
                (float(r["theta_cm_deg"]), float(r["dsdo_mb_sr"]), float(r["err_pct"])))
    return {k: sorted(v) for k, v in out.items()}


def _note(p, text):
    p.setdefault("notes", []).append(text)


def _matched(sub, x, energy, is_ay=None):
    p = exfor_points(sub, energy, x, is_ay)
    if p is None:
        raise ValueError(f"{sub} at {energy} MeV: EXFOR subentry not readable")
    idx = match(x, p.angles)
    if (idx < 0).any():
        raise ValueError(f"{sub} at {energy} MeV: record angles {list(np.asarray(x)[idx < 0])} not found in EXFOR")
    return p, idx


def drop_reason(subentry: str, corpus: str) -> str | None:
    """Why a subentry is removed from a corpus, or None if it is kept."""
    if corpus not in SCOPE:
        return None
    if subentry[:8] in DROP_FLAGGED:
        return ("dropped in reader-error cleaning: no author uncertainty source, data rest on the EXFOR reader "
                "error (docs/AUTHOR_UNCERTAINTIES.md, section 6)")
    if subentry[:8] in DROP_DUPLICATES:
        return ("dropped in reader-error cleaning: figure digitisation duplicating the authors' table "
                "(docs/AUTHOR_UNCERTAINTIES.md, section 6)")
    for key in (subentry[:8], subentry[:5]):
        if key in DROP_INCONSISTENT:
            return DROP_INCONSISTENT[key]
    return None


def correct(payload: dict, corpus: str) -> dict | None:
    """The corrected payload, or None if the record is dropped. Never applied twice (``MARK``)."""
    notes = payload.get("notes") or []
    # an ELM record already through the ELM calibration evaluation, which runs after this step, was corrected then
    if corpus not in SCOPE or MARK in notes or "elm-evaluation v1 (src/nn_corpora/elm_evaluation.py)" in notes:
        return payload
    sub = str(payload.get("EXFORAccessionNumber", ""))[:8]
    entry = sub[:5]
    if drop_reason(sub, corpus):
        return None
    if "deg" not in str(payload.get("x_units", "")).lower():  # energy distributions: none of this applies
        return payload
    data = payload["data"]
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    ye = np.asarray(data["y_err"], dtype=float)
    is_ay = payload.get("type") == "APower"
    energy = payload.get("energy")
    changed = False

    if sub in doering_table():  # 2. the thesis tabulation
        t = doering_table()[sub]
        scale = 1e-3 if payload.get("y_units") == "b/sr" else 1.0
        data["x"] = [a for a, _, _ in t]
        data["y"] = [v * scale for _, v, _ in t]
        data["y_err"] = [v * scale * e / 100 for _, v, e in t]
        _note(payload, f"values and errors replaced by Doering thesis (MSU 1974) Table 5, {len(t)} rows "
                       f"(EXFOR {len(x)} digitised points); external/doering_1974_table5.csv")
        changed = True
    elif entry in COLUMN_AUTHOR:  # 3a. the authors' column, filled where blank
        p, idx = _matched(sub, x, energy, is_ay)
        col = p.author[COLUMN_AUTHOR[entry]][idx]
        reader = p.reader[idx]
        if not is_ay:  # relative to the data, so the record's units do not matter
            ex_y = np.abs(p.data[idx])
            col, reader = col / ex_y, reader / ex_y
        known = np.where(col > 0, col, np.nan)
        author = _fill(x, known)
        new = np.hypot(reader, author) * (1.0 if is_ay else np.abs(y))
        data["y_err"] = [float(v) for v in new]
        _note(payload, f"per-point error = EXFOR {'+'.join(p.reader_cols)} (reader) (+) {COLUMN_AUTHOR[entry]} "
                       f"(the authors' errors; relabelled from ERR-T in 2023, absolute in data units); "
                       f"{int(np.isnan(known).sum())} of {len(x)} points without {COLUMN_AUTHOR[entry]} filled by "
                       f"linear interpolation in angle, flat beyond the ends")
        changed = True
    elif columns_rule(sub):  # 3b. the columns ERR-ANALYS names
        per_point, norm_cols, why = columns_rule(sub)
        p, idx = _matched(sub, x, energy, is_ay)
        author = np.sqrt(sum(p.author[lab][idx] ** 2 for lab in per_point))
        if not (author > 0).all():
            raise ValueError(f"{sub} at {energy} MeV: no {'+'.join(per_point)} at "
                             f"{list(x[author <= 0])} deg")
        new = to_record(np.hypot(p.reader[idx], author), p, idx, y, is_ay)
        parts = []
        # a record already carrying these columns (to rounding, or from a source with slightly different values,
        # e.g. Test's 22987) is left as it is
        if not np.allclose(new, ye, rtol=0.05, atol=0):
            data["y_err"] = [float(v) for v in new]
            parts.append(f"per-point error = EXFOR {' (+) '.join(p.reader_cols + per_point)}")
        if norm_cols:
            rel = [p.systematic[lab][idx] / np.abs(p.data[idx]) for lab in norm_cols]
            if any(np.ptp(r) > 1e-6 for r in rel):
                raise ValueError(f"{sub}: normalisation columns {norm_cols} are not constant")
            norm = float(np.sqrt(sum(r[0] ** 2 for r in rel)))
            if abs(float(data.get("systematic_normalization_error") or 0.0) - norm) > 1e-9:
                data["systematic_normalization_error"] = norm
                parts.append(f"normalisation {' (+) '.join(norm_cols)} = {100 * norm:.1f} %")
        if parts:
            _note(payload, f"{'; '.join(parts)} (ERR-ANALYS: {why})")
            changed = True
    elif entry in PER_PAPER:  # 3c. the paper's statement where EXFOR has no author error
        rule, cite = PER_PAPER[entry]
        p, idx = _matched(sub, x, energy, is_ay)
        blank = ~p.has_author[idx]
        # EXFOR's reader error, not the record's y_err: the record may already hold an author error EXFOR files as a
        # constant ERR-n column (e.g. O0253 ERR-1 "relative uncertainties" 2 %), which would count twice
        reader = to_record(p.reader[idx], p, idx, y, is_ay)
        # where EXFOR has the authors' error the record must carry it (the curation may have taken the reader's)
        exfor_author = to_record(np.max(list(p.author.values()) or [np.zeros(len(p.angles))], axis=0)[idx],
                                 p, idx, y, is_ay)
        low = ~blank & (ye < 0.95 * exfor_author)
        new = ye.copy()
        if blank.any():
            author = rule(x, y, is_ay, payload.get("target", ""))
            new[blank] = np.hypot(reader[blank], author[blank])
            _note(payload, f"author uncertainty at {int(blank.sum())} of {len(x)} points without one in EXFOR "
                           f"(added in quadrature to the reader error): {cite}")
        if low.any():
            new[low] = np.hypot(reader[low], exfor_author[low])
            _note(payload, f"EXFOR's author error, not the reader error alone, at {int(low.sum())} of {len(x)} "
                           f"points: reader (+) author")
        if blank.any() or low.any():
            data["y_err"] = [float(v) for v in new]
            changed = True

    if sub in TOTAL and not is_ay:  # 3d. the authors' total where EXFOR files only a part of it
        rule, cite = TOTAL[sub]
        total = rule(x, y, is_ay, payload.get("target", ""))
        cur = np.asarray(data["y_err"], dtype=float)
        if np.any(total > cur):
            data["y_err"] = [float(v) for v in np.maximum(cur, total)]
            _note(payload, f"per-point error = max(EXFOR DATA-ERR, the authors' total) at {int((total > cur).sum())} "
                           f"of {len(x)} points: {cite}")
            changed = True

    # 4. normalisation: cross-section figures (target thickness, beam integration, efficiency) cancel in an analysing
    # power, which has its own scale (the beam polarisation)
    norms = NORM_AY if is_ay else NORM
    for key in (sub, entry):
        if key in norms:
            val, why = norms[key]
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
