"""W2 season-level inputs per region and vintage, from the municipal tables (prereg-1 A–C;
Amendment 35; items 1–9). Local only. The same functions serve the backtest: every fit takes
`exclude`, the held-out crop, which is left out of every climatology and z-score (§5 step 8).

Municipal tables (frozen, checksummed):
  EVI    data/derived/w1_series_muni_*.csv (W1)
  rain   data/derived/w2_rain_muni.csv;  soil  w2_soil_muni.csv;  heat  w2_heat_muni.csv
  frost  data/derived/w2_frost_region_season.csv (a fixed offset; not standardised)
Members and weights: docs/week0/members_by_season.csv (Amendment 35; PAM year S−2).

Rules (as registered):
  climatology   per municipality and period (16-day slot or window), the mean over the seasons
                whose window falls in 2000–2025, member seasons only, at least 10 years, else no
                anomaly. Refitted without the held-out crop.
  anomaly       municipal value minus that mean, in the input's units.
  regional      PAM-weighted mean of members' anomalies; z-score against the same period across
                the baseline (heat days: standard deviation floored at 1 day).
  four-region   the same over all members of the four regions.
  cut dates     November 20 Nov of S−1; December 1 Dec of S−1; January 1 Jan of S.
  EVI           reading counts with ≥ 1 pixel of cloud-free coffee; composite missing when members
                with an anomaly hold < 50% of member PAM weight; season value = unweighted mean of
                the regional z of composites from 1 May of S−1 (sensitivity: 1 Sep) that ended at
                least 14 days before the cut.
  rain          flowering total from 1 Sep to the end of the last pentad ending ≥ 5 days before the
                cut (or 30 Nov); bean-fill rain to date from 1 Dec likewise (reported); consecutive
                dry days (< 1 mm) in the flowering window to date (reported).
  soil          May–Aug mean of the layer-weighted root-zone moisture (closed before every cut).
  heat          days above 34 °C from 1 Sep to the earlier of 30 Nov and 10 days before the cut.

Run:    .venv/Scripts/python gee/w2_season_inputs.py [evi] [rain] [soil] [heat]
Writes: data/derived/w2_season_inputs.csv (region × crop × vintage × input),
        docs/week0/w2_ranks.csv
"""
import datetime as dt
import glob
import sys

import numpy as np
import pandas as pd

from common import ROOT, WEEK0

D = ROOT / "data" / "derived"
VINTAGES = {"Nov": (-1, 11, 20), "Dec": (-1, 12, 1), "Jan": (0, 1, 1)}  # (year offset from S, month, day)
CLIM_YEARS = (2000, 2025)
MIN_YEARS = 10
TOTAL = "Four-region total"


def cut_date(crop, vintage):
    off, m, d = VINTAGES[vintage]
    return dt.date(crop + off, m, d)


def last_pentad_end(limit):
    """The last pentad end (5, 10, 15, 20, 25, month end) on or before `limit`."""
    d = limit
    while True:
        month_end = (d + dt.timedelta(days=1)).day == 1
        if d.day in (5, 10, 15, 20, 25) or month_end:
            return d
        d -= dt.timedelta(days=1)


def members():
    m = pd.read_csv(WEEK0 / "members_by_season.csv", dtype={"code": str})
    return m[m.member][["code", "region", "season", "pam_ha"]].rename(columns={"season": "crop"})


def regional(df, value, clim_key, exclude=None, extra_keys=()):
    """df: one row per member municipality × crop (× extra keys), with `value`, `pam_ha`, `region`,
    `clim_year` (calendar year of the window, for the 2000–2025 rule). Returns regional and total
    anomalies and z-scores per crop (× extra keys)."""
    d = df.dropna(subset=[value]).copy()
    base = d[d.clim_year.between(*CLIM_YEARS) & (d.crop != exclude)]
    g = base.groupby(["code"] + list(clim_key))[value].agg(["mean", "count"]).reset_index()
    g = g[g["count"] >= MIN_YEARS]
    d = d.merge(g[["code"] + list(clim_key) + ["mean"]], on=["code"] + list(clim_key), how="inner")
    d["anom"] = d[value] - d["mean"]
    keys = ["crop"] + list(extra_keys)
    out = []
    for label, sub in (("region", d), ("total", d.assign(region=TOTAL))):
        r = sub.groupby(["region"] + keys).apply(
            lambda x: pd.Series({"anom": np.average(x.anom, weights=x.pam_ha), "pam_with": x.pam_ha.sum()}))
        out.append(r.reset_index())
    r = pd.concat(out, ignore_index=True)
    return r


def zscore(r, clim_key, exclude=None, sd_floor=None, clim_year_col="clim_year"):
    base = r[r[clim_year_col].between(*CLIM_YEARS) & (r.crop != exclude)]
    s = base.groupby(["region"] + list(clim_key)).anom.agg(["mean", "std"]).reset_index()
    if sd_floor:
        s["std"] = s["std"].clip(lower=sd_floor)
    r = r.merge(s, on=["region"] + list(clim_key), how="left")
    r["z"] = (r.anom - r["mean"]) / r["std"]
    return r.drop(columns=["mean", "std"])


# ---------------------------------------------------------------- EVI
def evi(exclude=None, start_month=5):
    s = pd.concat([pd.read_csv(f, dtype={"code": str}) for f in sorted(glob.glob(str(D / "w1_series_muni_*.csv")))],
                  ignore_index=True)
    s["start"] = pd.to_datetime(s.composite_start)
    s["period"] = s.start.dt.dayofyear
    s["clim_year"] = s.start.dt.year
    s = s.rename(columns={"season": "crop"})
    s["value"] = np.where(s.f_q1_w_valid_sum >= 1, s.f_q1_EVI_median, np.nan)  # one cloud-free coffee pixel
    mem = members()
    s = s.merge(mem.drop(columns="region"), on=["code", "crop"], how="inner")
    r = regional(s, "value", ["period"], exclude, extra_keys=("composite_start", "period", "clim_year"))
    pam_all = pd.concat([mem.groupby(["region", "crop"]).pam_ha.sum().reset_index(),
                         mem.groupby("crop").pam_ha.sum().reset_index().assign(region=TOTAL)])
    r = r.merge(pam_all.rename(columns={"pam_ha": "pam_members"}), on=["region", "crop"], how="left")
    r["covered"] = r.pam_with / r.pam_members
    r = r[r.covered >= 0.5]  # the cloud floor: the regional composite is missing otherwise
    r = zscore(r, ["period"], exclude)
    r["end"] = pd.to_datetime(r.composite_start) + pd.Timedelta(days=16)
    rows = []
    for (reg, crop), x in r.groupby(["region", "crop"]):
        for v in VINTAGES:
            cut = pd.Timestamp(cut_date(crop, v))
            sel = x[(pd.to_datetime(x.composite_start) >= pd.Timestamp(crop - 1, start_month, 1))
                    & (x.end <= cut - pd.Timedelta(days=14))]
            rows.append(dict(region=reg, crop=crop, vintage=v, input="evi" if start_month == 5 else "evi_from_sep",
                             value=sel.z.mean() if len(sel) else np.nan, n_composites=len(sel)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- weather tables
def muni_table(product):
    t = pd.read_csv(D / f"w2_{product}_muni.csv", dtype={"code": str}).rename(columns={"season": "crop"})
    bands = [c for c in t.columns if c[:2] in ("d_", "p_", "h_") or c == "sm"]
    t[bands] = t[bands].div(t.w, axis=0)  # coffee-weighted municipal means
    return t, bands


def windowed(product, total_fn, input_name, exclude=None, sd_floor=None, vintages=VINTAGES):
    t, bands = muni_table(product)
    mem = members()
    rows = []
    for v in vintages:
        x = t.copy()
        x["value"] = [total_fn(row, crop, v) for row, crop in zip(x[bands].to_dict("records"), x.crop)]
        x["clim_year"] = x.crop - 1
        x["vintage"] = v
        x = x.merge(mem.drop(columns="region"), on=["code", "crop"], how="inner")
        r = regional(x, "value", ["vintage"], exclude, extra_keys=("vintage",))
        r["clim_year"] = r.crop - 1
        r = zscore(r, ["vintage"], exclude, sd_floor)
        r["vintage"], r["input"] = v, input_name
        rows.append(r.rename(columns={"z": "value"})[["region", "crop", "vintage", "input", "value", "anom"]])
    return pd.concat(rows, ignore_index=True)


def flowering_end(crop, v):
    return min(dt.date(crop - 1, 11, 30), last_pentad_end(cut_date(crop, v) - dt.timedelta(days=5)))


def rain_total(row, crop, v):
    end = flowering_end(crop, v)
    return sum(row[f"d_{d:%m%d}"] for d in pd.date_range(dt.date(crop - 1, 9, 1), end).date)


def dry_days(row, crop, v):
    end = flowering_end(crop, v)
    run = best = 0
    for d in pd.date_range(dt.date(crop - 1, 9, 1), end).date:
        run = run + 1 if row[f"d_{d:%m%d}"] < 1.0 else 0
        best = max(best, run)
    return best


def beanfill(row, crop, v):
    end = last_pentad_end(cut_date(crop, v) - dt.timedelta(days=5))
    if end < dt.date(crop - 1, 12, 5):
        return np.nan  # no complete bean-fill pentad before the cut
    starts = [k for k in row if k.startswith("p_")]
    tot = 0.0
    for k in starts:
        m, d = int(k[2:4]), int(k[4:6])
        y = crop - 1 if m == 12 else crop
        if dt.date(y, m, d) <= end - dt.timedelta(days=4):
            tot += row[k]
    return tot


def heat_days(row, crop, v):
    end = min(dt.date(crop - 1, 11, 30), cut_date(crop, v) - dt.timedelta(days=10))
    return sum(row[f"h_{d:%m%d}"] for d in pd.date_range(dt.date(crop - 1, 9, 1), end).date)


def soil(exclude=None):
    t, bands = muni_table("soil")
    mem = members()
    x = t.merge(mem.drop(columns="region"), on=["code", "crop"], how="inner")
    x["value"], x["clim_year"], x["k"] = x.sm, x.crop - 1, 0
    r = regional(x, "value", ["k"], exclude, extra_keys=("k",))
    r["clim_year"], r["k"] = r.crop - 1, 0
    r = zscore(r, ["k"], exclude)
    out = []
    for v in VINTAGES:
        out.append(r.assign(vintage=v, input="soil_moisture").rename(columns={"z": "value"})
                   [["region", "crop", "vintage", "input", "value", "anom"]])
    return pd.concat(out, ignore_index=True)


WORSE_IS_LOW = {"evi": True, "evi_from_sep": True, "rain_flowering": True, "soil_moisture": True,
                "heat_days": False, "dry_days": False, "beanfill_rain": True, "frost_penalty": False}


def frost():
    f = pd.read_csv(D / "w2_frost_region_season.csv")
    rows = []
    for v in VINTAGES:
        rows.append(f[["region", "crop"]].assign(vintage=v, input="frost_penalty",
                                                 value=f.penalty_with_unresolved, anom=np.nan))
    return pd.concat(rows, ignore_index=True)


def ranks(df):
    out = []
    for (inp, reg, v), x in df.dropna(subset=["value"]).groupby(["input", "region", "vintage"]):
        x = x[x.crop.between(2001, 2025)]
        asc = WORSE_IS_LOW[inp]
        x = x.assign(rank_worst=x.value.rank(ascending=asc, method="min").astype(int), seasons=len(x))
        out.append(x)
    return pd.concat(out, ignore_index=True)


def main(parts):
    pieces = []
    if "frost" in parts:
        pieces.append(frost())
    if "rain" in parts:
        pieces += [windowed("rain", rain_total, "rain_flowering"),
                   windowed("rain", dry_days, "dry_days"),
                   windowed("rain", beanfill, "beanfill_rain", vintages={"Jan": VINTAGES["Jan"]})]
    if "soil" in parts:
        pieces.append(soil())
    if "heat" in parts:
        pieces.append(windowed("heat", heat_days, "heat_days", sd_floor=1.0))
    if "evi" in parts:
        pieces += [evi(), evi(start_month=9)]
    df = pd.concat(pieces, ignore_index=True)
    df.to_csv(D / "w2_season_inputs.csv", index=False, float_format="%.5f")
    rk = ranks(df)
    rk.to_csv(WEEK0 / "w2_ranks.csv", index=False, float_format="%.5f")
    return df, rk


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    parts = sys.argv[1:] or ["frost", "rain", "soil", "heat", "evi"]
    df, rk = main(parts)
    k = rk[rk.crop.isin([2022, 2025]) & (rk.vintage == "Nov")]
    print(k.pivot_table(index=["input", "region"], columns="crop", values="rank_worst").to_string())
