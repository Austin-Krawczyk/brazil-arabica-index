"""Prelim-versus-final CHIRPS check (§9, Amendment 9; owner, 2026-10-15), windows in 2015–2025.
Local only, from two watched exports with the same reduction: w2_rain_muni.csv (final) and
w2_prelim_muni.csv (CHC prelim pentads, the ingested collection).

Per member municipality (Amendment 35; PAM year S−2) and crop 2016–2026, window totals:
  flowering_full     1 Sep – 30 Nov of S−1
  flowering_nov      1 Sep – 15 Nov (the November vintage's to-date window)
  flowering_dec      1 Sep – 25 Nov (the December vintage's)
  beanfill_full      1 Dec of S−1 – 31 Mar of S
  beanfill_jan       1 – 25 Dec (the January vintage's)
Final flowering totals are summed from daily values, prelim from pentads; the windows are whole
pentads, so the two cover the same days. Reported: prelim minus final, in mm and as a share of
final, per region (PAM-weighted mean over members) and over all municipalities; mean, mean
absolute and largest differences across seasons. No correction is applied (§9).

Run:    .venv/Scripts/python gee/w2_prelim_bias.py
Writes: docs/week0/w2_prelim_bias_region.csv, docs/week0/w2_prelim_bias_summary.csv
"""
import datetime as dt

import numpy as np
import pandas as pd

from common import ROOT, WEEK0
from w2_season_inputs import TOTAL, members

D = ROOT / "data" / "derived"
CROPS = range(2016, 2027)
WINDOWS = {"flowering_full": ((9, 1), (11, 30)), "flowering_nov": ((9, 1), (11, 15)),
           "flowering_dec": ((9, 1), (11, 25)), "beanfill_full": ((12, 1), (3, 31)),
           "beanfill_jan": ((12, 1), (12, 25))}


def date_of(crop, m, d):
    return dt.date(crop - 1 if m >= 9 else crop, m, d)


def totals(row, crop, kind):
    out = {}
    for name, ((m0, d0), (m1, d1)) in WINDOWS.items():
        a, b = date_of(crop, m0, d0), date_of(crop, m1, d1)
        tot = 0.0
        if kind == "final":
            for d in pd.date_range(a, min(b, dt.date(crop - 1, 11, 30))).date:
                if a.month >= 9 and d <= dt.date(crop - 1, 11, 30):
                    tot += row.get(f"d_{d:%m%d}", 0.0)
            for k, v in row.items():
                if k.startswith("p_"):
                    m, dd = int(k[2:4]), int(k[4:6])
                    if a <= date_of(crop, m, dd) <= b - dt.timedelta(days=4):
                        tot += v
        else:
            for k, v in row.items():
                if k.startswith("q_"):
                    m, dd = int(k[2:4]), int(k[4:6])
                    if a <= date_of(crop, m, dd) <= b - dt.timedelta(days=4):
                        tot += v
        out[name] = tot
    return out


def table(product, kind):
    t = pd.read_csv(D / f"w2_{product}_muni.csv", dtype={"code": str}).rename(columns={"season": "crop"})
    t = t[t.crop.isin(CROPS)]
    bands = [c for c in t.columns if c[:2] in ("d_", "p_", "q_")]
    t[bands] = t[bands].div(t.w, axis=0)
    rows = [dict(code=c, crop=s, **totals(r, s, kind)) for c, s, r in zip(t.code, t.crop, t[bands].to_dict("records"))]
    return pd.DataFrame(rows)


def main():
    f, p = table("rain", "final"), table("prelim", "prelim")
    m = f.merge(p, on=["code", "crop"], suffixes=("_final", "_prelim"))
    mem = members()
    m = m.merge(mem, on=["code", "crop"], how="inner")
    rows = []
    for (reg, crop), x in pd.concat([m, m.assign(region=TOTAL)]).groupby(["region", "crop"]):
        for w in WINDOWS:
            fin = np.average(x[f"{w}_final"], weights=x.pam_ha)
            pre = np.average(x[f"{w}_prelim"], weights=x.pam_ha)
            rows.append(dict(region=reg, crop=crop, window=w, final_mm=fin, prelim_mm=pre,
                             diff_mm=pre - fin, diff_share=(pre - fin) / fin if fin else np.nan,
                             muni_mean_abs_diff_mm=(x[f"{w}_prelim"] - x[f"{w}_final"]).abs().mean()))
    r = pd.DataFrame(rows)
    r.to_csv(WEEK0 / "w2_prelim_bias_region.csv", index=False, float_format="%.4f")
    s = r.groupby(["region", "window"]).agg(seasons=("crop", "size"), mean_diff_mm=("diff_mm", "mean"),
                                            mean_abs_diff_mm=("diff_mm", lambda v: v.abs().mean()),
                                            max_abs_diff_mm=("diff_mm", lambda v: v.abs().max()),
                                            mean_diff_share=("diff_share", "mean"),
                                            mean_abs_diff_share=("diff_share", lambda v: v.abs().mean())).reset_index()
    s.to_csv(WEEK0 / "w2_prelim_bias_summary.csv", index=False, float_format="%.4f")
    return r, s


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    r, s = main()
    print(s.round(3).to_string(index=False))
