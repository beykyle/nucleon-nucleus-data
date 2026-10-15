"""scripts/talys_compound.py: TALYS output parsing and the compound-elastic subtraction (no TALYS run needed)."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec_ = importlib.util.spec_from_file_location("talys_compound", ROOT / "scripts" / "talys_compound.py")
tc = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(tc)

ANG_N = """# header
#   E-incident [MeV]: 1.000000E+01
##     Angle           xs           Direct        Compound
##     [deg]         [mb/sr]       [mb/sr]       [mb/sr]
   0.000000E+00   4.000000E+03   3.990000E+03   1.000000E+01
   9.000000E+01   2.000000E+01   1.000000E+01   1.000000E+01
   1.800000E+02   3.000000E+01   1.800000E+01   1.200000E+01
"""
ALL_TOT = """# all.tot
##  E   Non-elastic  Elastic  Total  Compound_elast. Shape_elastic Reaction Compound_nonel. Direct Preequilibrium Direct_capture
##  [MeV] [mb] [mb] [mb] [mb] [mb] [mb] [mb] [mb] [mb] [mb]
 1.0E+01 1.9E+03 2.9E+03 4.8E+03 1.0E+02 2.8E+03 2.0E+03 1.5E+03 1.0E+02 3.0E+02 0.0E+00
 2.0E+01 2.0E+03 2.6E+03 4.6E+03 5.0E+01 2.55E+03 2.05E+03 1.4E+03 2.0E+02 4.0E+02 0.0E+00
"""


def test_parse_angular(tmp_path):
    f = tmp_path / "nn0010.000ang.L00"
    f.write_text(ANG_N)
    t = tc.parse_table(f)
    assert np.allclose(t["xs"], t["direct"] + t["compound"])
    assert list(t["angle"]) == [0, 90, 180]


def test_parse_all_tot(tmp_path):
    f = tmp_path / "all.tot"
    f.write_text(ALL_TOT)
    t = tc.parse_all_tot(f)
    assert np.allclose(t["elastic"], t["compound_elastic"] + t["shape_elastic"])
    assert np.allclose(t["reaction"] - t["nonelastic"], t["compound_elastic"])


def test_energy_tag():
    assert tc.energy_tag(10.0) == "0010.000" and tc.energy_tag(9.97) == "0009.970"


def test_ce_interpolation_in_cos_theta():
    table = {10.0: (np.array([0.0, 90.0, 180.0]), np.array([10.0, 10.0, 12.0]), np.array([4e3, 20.0, 30.0]),
                    np.full(3, np.nan))}
    ce = tc.ce_at(table, 10.0, np.array([90.0, 180.0, 120.0]), ratio=False)
    assert ce[0] == pytest.approx(10.0) and ce[1] == pytest.approx(12.0) and 10.0 < ce[2] < 12.0


def test_apply_subtracts_and_inflates_errors(tmp_path, monkeypatch):
    """Synthetic corpus: measured = TALYS xs; direct = measured - CE reproduces TALYS's Direct."""
    data = tmp_path / "data"
    sec = data / "elm" / "elastic_diff_xs"
    sec.mkdir(parents=True)
    tal = tmp_path / "cache" / "elm" / "elastic_diff_xs" / "n_Sn_120"
    tal.mkdir(parents=True)
    (tal / "angular.csv").write_text("E_MeV,angle_cm_deg,xs_mb_sr,direct_mb_sr,compound_mb_sr,ratio_rutherford\n"
                                     "10.000,0,4000,3990,10,nan\n10.000,90,20,10,10,nan\n10.000,180,30,18,12,nan\n")
    (tal / "meta.json").write_text(json.dumps({"talys_commit": "abcdef0"}))
    rec = {"EXFORAccessionNumber": "X0000002", "projectile": "neutron", "energy": 10.0, "y_units": "b/sr",
           "data": {"x": [90.0, 180.0], "y": [0.020, 0.030], "y_err": [0.001, 0.001]}, "notes": []}
    (sec / "Sn_120.json").write_text(json.dumps([rec]))
    monkeypatch.setattr(tc.spec, "DATA_DIR", data)
    monkeypatch.setattr(tc, "CACHE", tmp_path / "cache")
    tc.apply(type("A", (), {"corpus": "elm", "sector": "elastic_diff_xs"})())
    out = json.loads((data / "elm" / "elastic_diff_xs_direct" / "Sn_120.json").read_text())[0]["data"]
    assert out["y"] == pytest.approx([0.010, 0.018])
    assert out["compound_elastic"] == pytest.approx([0.010, 0.012])
    assert out["y_err"] == pytest.approx(np.hypot([0.001, 0.001], 0.3 * np.array([0.010, 0.012])))
    assert out["y_measured"] == pytest.approx([0.020, 0.030])
