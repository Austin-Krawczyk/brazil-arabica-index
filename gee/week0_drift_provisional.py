"""Week 0, PROVISIONAL Terra drift check (Amendment 26).

Provisional: all class-46 coffee pixels in MG and SP, not the four Conab regions. The formal run,
and trigger (b), wait for the regional municipality lists (§3).

Method, fixed in docs/week0_report.md before this ran:
  products    MOD13Q1 (Terra), MYD13Q1 (Aqua), VNP13A1 (SNPP VIIRS); NDVI and EVI
  QA          MODIS SummaryQA 0-1 (good, marginal); VIIRS pixel_reliability 0-3 (excellent..marginal)
  mask        MapBiomas Collection 10, classification_2024 == 46, inside MG and SP
  boundaries  FAO GAUL 2015 level 1 (provisional run only)
  pixels      each product's own pixels, weighted by the coffee fraction of the pixel
  month       composites whose start date falls in the calendar month, averaged per pixel
  anomaly     z-score per calendar month against 2013-2025, per product
  compared    2018-01 to 2026-10

Batch only (owner rule 2026-10-15). The 2026-10-13 run made one interactive request per six months
and rebuilt the 30 m coffee weight inside every request; Cloud Monitoring puts about 356
EECU-hours of interactive use in that run's window, which the watchdog could not see. Now, with
the same mask, states, QA, weights and reducers:
  1. --export-weight GRID --estimate E    the coffee weight, built once per product grid and saved
                                          as an asset: "modis250" (MOD13Q1 and MYD13Q1 share the
                                          MODIS 250 m sinusoidal grid; checked before use) and
                                          "viirs500" (VNP13A1)
  2. --product NAME --estimate E          that product's monthly sums: one batch table export
                                          under gee/ee_watchdog.py, reading the weight asset;
                                          saved to data/derived/_tmp_drift_<product>.csv
  3. no arguments                         anomalies and summary from the saved tables; no Earth
                                          Engine call
Estimates come from a one-month probe (--first/--last on one month) scaled by the month count.

Run:    .venv/Scripts/python gee/week0_drift_provisional.py --export-weight modis250 --estimate E
        .venv/Scripts/python gee/week0_drift_provisional.py --product MOD13Q1 --estimate E
        .venv/Scripts/python gee/week0_drift_provisional.py
Writes: docs/week0/drift_provisional_monthly.csv, docs/week0/drift_provisional_summary.csv
"""
import argparse

import ee
import numpy as np
import pandas as pd

from common import ROOT, WEEK0, init
from week0_hls_test import export_and_fetch

CACHE = ROOT / "data" / "derived"  # _tmp_* files there are gitignored

MAPBIOMAS = ("projects/mapbiomas-public/assets/brazil/lulc/collection10/"
             "mapbiomas_brazil_collection10_integration_v1")
MASK_YEAR = 2024
STATES = ["Minas Gerais", "Sao Paulo"]
# name: (Earth Engine ID, QA band, highest accepted QA value, native resolution in m)
PRODUCTS = {
    "MOD13Q1": ("MODIS/061/MOD13Q1", "SummaryQA", 1, 250),
    "MYD13Q1": ("MODIS/061/MYD13Q1", "SummaryQA", 1, 250),
    "VNP13A1": ("NASA/VIIRS/002/VNP13A1", "pixel_reliability", 3, 500),
}
SCALE = 0.0001  # MODIS: scale factor 0.0001; VNP13A1: stored x10000 (Earthdata). Same arithmetic.
BASELINE = (2013, 2025)
FIRST, LAST = "2013-01-01", "2026-10-01"  # month starts, inclusive
COMPARE_FROM = "2018-01"
TREND_FROM = "2024-01"
PAIRS = [("MOD13Q1", "MYD13Q1"), ("MOD13Q1", "VNP13A1"), ("MYD13Q1", "VNP13A1")]
GRID = {"MOD13Q1": "modis250", "MYD13Q1": "modis250", "VNP13A1": "viirs500"}
SUMS = ["ndvi_w", "w_ndvi", "evi_w", "w_evi", "w"]


def state_mask():
    fc = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM0_NAME", "Brazil"))
          .filter(ee.Filter.inList("ADM1_NAME", STATES)))
    n = fc.size().getInfo()  # interactive: metadata (feature count of a filtered table)
    if n != len(STATES):
        raise SystemExit(f"Expected {len(STATES)} state polygons, found {n}; check GAUL names.")
    return ee.Image.constant(1).clipToCollection(fc), fc.geometry().bounds()


def coffee_weight(proj, region):
    """Coffee fraction of each product pixel, from the 30 m mask; zero-fraction pixels dropped."""
    coffee = ee.Image(MAPBIOMAS).select(f"classification_{MASK_YEAR}").eq(46).unmask(0)
    frac = coffee.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj)
    return frac.updateMask(region).updateMask(frac.gt(0)).rename("w")


def month_feature(col, qa_band, qa_max, w, geom, proj, res):
    reducer = ee.Reducer.sum().combine(ee.Reducer.count(), sharedInputs=True)

    def prep(img):
        qa = img.select(qa_band)
        ok = qa.gte(0).And(qa.lte(qa_max))
        return img.select(["NDVI", "EVI"]).updateMask(ok).multiply(SCALE)

    def per_month(start):
        start = ee.Date(start)
        month_col = col.filterDate(start, start.advance(1, "month"))
        img = month_col.map(prep).mean()
        ndvi, evi = img.select("NDVI"), img.select("EVI")
        stack = ee.Image.cat([
            ndvi.multiply(w).rename("ndvi_w"), w.updateMask(ndvi.mask()).rename("w_ndvi"),
            evi.multiply(w).rename("evi_w"), w.updateMask(evi.mask()).rename("w_evi"),
            w,
        ])
        stats = stack.reduceRegion(reducer, geom, scale=res, crs=proj, maxPixels=1e10, tileScale=4)
        # A month with no composites (e.g. after a product's last image) is reported empty, not filled.
        stats = ee.Algorithms.If(month_col.size().gt(0), stats, ee.Dictionary({}))
        return ee.Feature(None, stats).set("month", start.format("YYYY-MM"),
                                           "composites", month_col.size())

    return per_month


def weight_asset(project, grid):
    return f"projects/{project}/assets/drift_coffee_weight_{grid}_mask{MASK_YEAR}"


def grid_projection(grid):
    """The product grid's projection. MOD13Q1 and MYD13Q1 must share one grid to share a weight."""
    names = [n for n, g in GRID.items() if g == grid]
    projs = [ee.ImageCollection(PRODUCTS[n][0]).first().select("NDVI").projection() for n in names]
    info = [pr.getInfo() for pr in projs]  # interactive: metadata (projections)
    if any(i != info[0] for i in info):
        raise SystemExit(f"{grid}: {', '.join(names)} are not on one grid; build one weight per product")
    return projs[0], info[0]


def export_weight(project, grid, estimate_eecu_s):
    """The coffee weight in the product grid, built once by a batch image export to an asset."""
    from ee_watchdog import run_watched

    proj, p = grid_projection(grid)
    region, geom = state_mask()
    w = coffee_weight(proj, region).toFloat()
    task = ee.batch.Export.image.toAsset(
        image=w, description=f"drift_weight_{grid}", assetId=weight_asset(project, grid),
        crs=p["crs"], crsTransform=p["transform"], region=geom, maxPixels=1e11,
        pyramidingPolicy={"w": "mean"})
    state, used, wall = run_watched(task, estimate_eecu_s)
    print(f"weight {grid}: {state}, {used:,.0f} EECU-seconds, {wall:.0f} s wall")


def fetch(project, name, estimate_eecu_s, first=FIRST, last=LAST):
    """One product's monthly sums as one batch table export under the watchdog."""
    asset, qa_band, qa_max, res = PRODUCTS[name]
    col = ee.ImageCollection(asset)
    proj, _ = grid_projection(GRID[name])
    _, geom = state_mask()
    w = ee.Image(weight_asset(project, GRID[name])).select("w")
    per_month = month_feature(col, qa_band, qa_max, w, geom, proj, res)
    months = pd.date_range(first, last, freq="MS").strftime("%Y-%m-%d").tolist()
    selectors = ["month", "composites"] + [f"{b}_{r}" for b in SUMS for r in ("sum", "count")]
    p = export_and_fetch(ee.FeatureCollection(ee.List(months).map(per_month)),
                         f"drift_provisional_{name}_{months[0][:7]}_{months[-1][:7]}", selectors, estimate_eecu_s)
    # a month with no composites has no sums: reported empty, not filled
    ok_ndvi, ok_evi = p["w_ndvi_sum"].fillna(0) > 0, p["w_evi_sum"].fillna(0) > 0
    return pd.DataFrame({
        "product": name, "month": p["month"], "composites": p["composites"],
        "ndvi": np.where(ok_ndvi, p["ndvi_w_sum"] / p["w_ndvi_sum"], np.nan),
        "evi": np.where(ok_evi, p["evi_w_sum"] / p["w_evi_sum"], np.nan),
        "coffee_pixels": p["w_count"],
        "valid_ndvi_pixels": p["w_ndvi_count"],
        "valid_evi_pixels": p["w_evi_count"],
    })


def anomalies(df):
    df = df.copy()
    df["year"] = df["month"].str[:4].astype(int)
    df["cal_month"] = df["month"].str[5:7].astype(int)
    base = df[df["year"].between(*BASELINE)]
    for index in ("ndvi", "evi"):
        stats = base.groupby(["product", "cal_month"])[index].agg(["mean", "std"])
        df = df.join(stats, on=["product", "cal_month"])
        df[f"{index}_z"] = (df[index] - df["mean"]) / df["std"]
        df = df.drop(columns=["mean", "std"])
    return df


def summarise(df):
    rows = []
    for index in ("ndvi_z", "evi_z"):
        wide = df.pivot(index="month", columns="product", values=index)
        wide = wide[wide.index >= COMPARE_FROM]
        for a, b in PAIRS:
            d = (wide[a] - wide[b]).dropna()
            t = np.arange(len(d)) / 12.0
            slope = np.polyfit(t, d.values, 1)[0] if len(d) > 2 else np.nan
            recent = d[d.index >= TREND_FROM]
            rows.append({
                "index": index, "pair": f"{a} - {b}", "months": len(d),
                "first": d.index.min(), "last": d.index.max(),
                "mean_diff_sd": round(d.mean(), 3),
                "mean_diff_2024_on_sd": round(recent.mean(), 3),
                "mean_abs_diff_2024_on_sd": round(recent.abs().mean(), 3),
                "trend_sd_per_year": round(slope, 3),
            })
    return pd.DataFrame(rows)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--export-weight", choices=sorted(set(GRID.values())))
    a.add_argument("--product", choices=list(PRODUCTS))
    a.add_argument("--first", default=FIRST, help="first month (probe: set --first and --last to one month)")
    a.add_argument("--last", default=LAST)
    a.add_argument("--estimate", type=float, help="cost estimate in EECU-seconds; required for any task")
    args = a.parse_args()
    if args.export_weight or args.product:
        if not args.estimate:
            raise SystemExit("--estimate (EECU-seconds) is required for any Earth Engine task")
        project = init()
        if args.export_weight:
            return export_weight(project, args.export_weight, args.estimate)
        full = (args.first, args.last) == (FIRST, LAST)
        cache = CACHE / (f"_tmp_drift_{args.product}.csv" if full else
                         f"_tmp_drift_{args.product}_probe_{args.first[:7]}_{args.last[:7]}.csv")
        if cache.exists():
            raise SystemExit(f"{cache.name} exists; move it aside to refetch")
        df = fetch(project, args.product, args.estimate, args.first, args.last)
        CACHE.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache, index=False)
        print(df.to_string(index=False) if not full else f"{args.product}: {len(df)} months saved to {cache.name}")
        return
    frames = []
    for name in PRODUCTS:  # no Earth Engine call from here on
        cache = CACHE / f"_tmp_drift_{name}.csv"
        if not cache.exists():
            raise SystemExit(f"{name}: no saved table; run --product {name} --estimate E first")
        frames.append(pd.read_csv(cache, dtype={"month": str}))
    monthly = anomalies(pd.concat(frames, ignore_index=True))
    monthly.to_csv(WEEK0 / "drift_provisional_monthly.csv", index=False)
    summary = summarise(monthly)
    summary.to_csv(WEEK0 / "drift_provisional_summary.csv", index=False)
    print("\nPROVISIONAL: all class-46 pixels in MG and SP; not the formal per-region check.")
    print(monthly.groupby("product")[["coffee_pixels", "valid_ndvi_pixels"]]
          .agg({"coffee_pixels": "max", "valid_ndvi_pixels": ["min", "median"]}))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
