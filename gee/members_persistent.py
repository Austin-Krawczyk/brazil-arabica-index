"""Members per season on the persistent-pixel mask (Amendment 41), for the backtest's
persistent-pixel sensitivity. The same rule as Amendment 35, with the mask changed only: kept by the
stable filter, PAM area for PAM year S−2, and at least one MODIS pixel of persistent-pixel coffee
under season S's mask (summed coffee fraction ≥ 1). Local only.

Run:    .venv/Scripts/python gee/members_persistent.py
Reads:  data/derived/w1p_series_muni_*.csv, docs/week0/members_by_season.csv (PAM and kept)
Writes: docs/week0/members_by_season_persistent.csv (same columns as members_by_season.csv)
"""
import glob

import numpy as np
import pandas as pd

from common import ROOT, WEEK0


def main():
    s = pd.concat([pd.read_csv(f, dtype={"code": str})
                   for f in sorted(glob.glob(str(ROOT / "data" / "derived" / "w1p_series_muni_*.csv")))],
                  ignore_index=True)
    px = s.groupby(["code", "season"]).f_w_total_sum.agg(["min", "max"])
    assert np.allclose(px["min"], px["max"], rtol=1e-6), "coffee weight varies within a season"
    px = px["max"].rename("pixels").reset_index()
    base = pd.read_csv(WEEK0 / "members_by_season.csv", dtype={"code": str}).drop(columns=["pixels", "member"])
    m = base.merge(px, on=["code", "season"], how="left")
    m["pixels"] = m.pixels.fillna(0.0)
    m["member"] = m.kept & (m.pam_ha > 0) & (m.pixels >= 1)
    m = m[["code", "region", "season", "mask_year", "pam_ha", "pixels", "kept", "member"]]
    m.to_csv(WEEK0 / "members_by_season_persistent.csv", index=False, float_format="%.4f")
    return m


if __name__ == "__main__":
    m = main()
    full = pd.read_csv(WEEK0 / "members_by_season.csv", dtype={"code": str})
    print("members per season, persistent vs full:")
    print(pd.DataFrame({"persistent": m.groupby("season").member.sum(),
                        "full": full.groupby("season").member.sum()}).describe().round(0).to_string())
