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

Run:    .venv/Scripts/python gee/week0_drift_provisional.py
Writes: docs/week0/drift_provisional_monthly.csv, docs/week0/drift_provisional_summary.csv
"""
import time

import ee
import numpy as np
import pandas as pd

from common import ROOT, WEEK0, init

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


def state_mask():
    fc = (ee.FeatureCollection("FAO/GAUL/2015/level1")
          .filter(ee.Filter.eq("ADM0_NAME", "Brazil"))
          .filter(ee.Filter.inList("ADM1_NAME", STATES)))
    n = fc.size().getInfo()
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


def fetch(name):
    asset, qa_band, qa_max, res = PRODUCTS[name]
    col = ee.ImageCollection(asset)
    proj = col.first().select("NDVI").projection()
    region, geom = state_mask()
    w = coffee_weight(proj, region)
    per_month = month_feature(col, qa_band, qa_max, w, geom, proj, res)
    months = pd.date_range(FIRST, LAST, freq="MS").strftime("%Y-%m-%d").tolist()
    rows = []
    for i in range(0, len(months), 6):  # small batches keep each request inside time limits
        chunk = months[i:i + 6]
        for attempt in range(5):
            try:
                fc = ee.FeatureCollection(ee.List(chunk).map(per_month)).getInfo()
                break
            except (ee.EEException, ConnectionError, OSError) as e:  # incl. transient DNS failures
                if attempt == 4:
                    raise
                print(f"  {name} {chunk[0]}: retry {attempt + 1} after {type(e).__name__}: {str(e)[:80]}")
                time.sleep(30 * (attempt + 1))
        for f in fc["features"]:
            p = f["properties"]
            rows.append({
                "product": name, "month": p["month"], "composites": p.get("composites"),
                "ndvi": p["ndvi_w_sum"] / p["w_ndvi_sum"] if p.get("w_ndvi_sum") else np.nan,
                "evi": p["evi_w_sum"] / p["w_evi_sum"] if p.get("w_evi_sum") else np.nan,
                "coffee_pixels": p.get("w_count"),
                "valid_ndvi_pixels": p.get("w_ndvi_count"),
                "valid_evi_pixels": p.get("w_evi_count"),
            })
        print(f"  {name}: through {chunk[-1][:7]}")
    return rows


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
    init()
    frames = []
    for name in PRODUCTS:
        cache = CACHE / f"_tmp_drift_{name}.csv"
        if cache.exists():  # a finished product is not refetched after a later failure
            print(f"{name}: using saved results from {cache.name}")
            frames.append(pd.read_csv(cache, dtype={"month": str}))
            continue
        print(f"{name}: fetching monthly coffee-weighted means")
        df = pd.DataFrame(fetch(name))
        CACHE.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache, index=False)
        frames.append(df)
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
