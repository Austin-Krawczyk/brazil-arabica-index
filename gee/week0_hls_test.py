"""Week 0: HLS rainy-season coverage test and second drift-check reference (Amendments 30, 31).

PROVISIONAL: a 20,000-pixel sample of the MG/SP coffee mask, not the four Conab regions.

Method, recorded in docs/week0_report.md before this ran:
  sample      MapBiomas Collection 10 classification_2024 == 46 inside GAUL 2025 level 1 Minas Gerais
              and Sao Paulo (owner rule 2026-10-13: later runs use GAUL 2025); stratifiedSample of
              20,000 points at 30 m, seed 20261012
  products    NASA/HLS/HLSS30/v002: coverage, NDVI, EVI. NASA/HLS/HLSL30/v002: coverage only, as
              information
  clear       Fmask bits 1 (cloud), 2 (adjacent to cloud/shadow), 3 (cloud shadow), 4 (snow/ice) all 0
  coverage    share of sample points with at least one clear observation in the month; "any"
              coverage (an observation of any quality) is reported beside it, so archive gaps are
              not mistaken for cloud
  indices     per point, the median of clear observations in the month. NDVI = (B8A - B4) /
              (B8A + B4); EVI = 2.5 (B8A - B4) / (B8A + 6 B4 - 7.5 B2 + 1), values outside -1..1
              screened out. Bands are reflectance already (checked 2026-10-13). Month value = mean
              over points with data
  months      2017-01 to 2026-09. Baseline July 2017 to December 2025; January-June 2017 reported
              as information
  granules    only those containing a sample point (owner decision 2026-10-13)
  cost        ee.profilePrinting for every run, saved under docs/week0/profiles/

Anomalies against a baseline are NOT computed here: the baseline for comparisons with HLS is open
(§10). This script saves the monthly series only.

Option C (owner decision 2026-10-13): 5,000 points, a seeded random subset of the 20,000-point
sample (numpy default_rng(20261012)); HLSS30 for every month, HLSL30 for November-March months
only, as information.

Run:    .venv/Scripts/python gee/week0_hls_test.py --probe [--points N] [--month YYYY-MM]
        .venv/Scripts/python gee/week0_hls_test.py --points 5000
Writes: docs/week0/hls_monthly.csv, docs/week0/hls_coverage_test.csv,
        docs/week0/profiles/hls_<mode>_<utc>.txt
"""
import argparse
import datetime as dt
import io
import re
import time

import ee
import numpy as np
import pandas as pd

from google.cloud import storage

from common import ROOT, WEEK0, init, setting

MAPBIOMAS = ("projects/mapbiomas-public/assets/brazil/lulc/collection10/"
             "mapbiomas_brazil_collection10_integration_v1")
STATES = ["Minas Gerais", "São Paulo"]
SAMPLE, SEED = 20000, 20261012
S30, L30 = "NASA/HLS/HLSS30/v002", "NASA/HLS/HLSL30/v002"
BANDS = {S30: ("B8A", "B4", "B2"), L30: ("B5", "B4", "B2")}  # NIR, red, blue
CLEAR_BITS = 0b11110  # bits 1-4
FIRST, LAST = "2017-01-01", "2026-09-01"
BASELINE = ("2017-07", "2025-12")
RAINY = (11, 12, 1, 2, 3)
COVERAGE_MIN, MONTHS_ALLOWED = 0.60, 2
CACHE = ROOT / "data" / "derived"


def region():
    fc = (ee.FeatureCollection("FAO/GAUL/2025/level1")
          .filter(ee.Filter.eq("GAUL0_NAME", "Brazil"))
          .filter(ee.Filter.inList("GAUL1_NAME", STATES)))
    n = fc.size().getInfo()
    if n != len(STATES):
        raise SystemExit(f"Expected {len(STATES)} state polygons, found {n}.")
    return fc


BATCH_COSTS = []  # (task, EECU-seconds) for batch tasks, which request profiling does not see


def export_and_fetch(fc, name, selectors):
    """Run a table export to the bucket as a batch task (no interactive time limit) and fetch it."""
    bucket = setting("GCS_BUCKET")
    prefix = f"week0/{name}"
    task = ee.batch.Export.table.toCloudStorage(collection=fc, description=name, bucket=bucket,
                                                fileNamePrefix=prefix, fileFormat="CSV",
                                                selectors=selectors)
    task.start()
    print(f"  batch task {name} started")
    while True:
        status = task.status()
        if status["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(30)
    if status["state"] != "COMPLETED":
        raise SystemExit(f"Batch task {name} {status['state']}: {status.get('error_message', '')}")
    BATCH_COSTS.append((name, float(status.get("batch_eecu_usage_seconds", 0) or 0)))
    client = storage.Client(project=setting("EE_PROJECT"),
                            credentials=ee.data.get_persistent_credentials())
    blob = client.bucket(bucket).blob(prefix + ".csv")
    return pd.read_csv(io.BytesIO(blob.download_as_bytes()))


def sample_points(states, n_use):
    """Draw the sample once (a batch export), then reuse its coordinates for every month."""
    cache = CACHE / f"_tmp_hls_sample_{SEED}.csv"
    if cache.exists():
        pts = pd.read_csv(cache)
    else:
        coffee = (ee.Image(MAPBIOMAS).select("classification_2024").eq(46).selfMask()
                  .rename("coffee").clipToCollection(states))
        fc = coffee.stratifiedSample(numPoints=SAMPLE, classBand="coffee",
                                     region=states.geometry().bounds(), scale=30, seed=SEED,
                                     classValues=[1], classPoints=[SAMPLE], geometries=True,
                                     tileScale=16)
        fc = fc.map(lambda f: f.set({"lon": f.geometry().coordinates().get(0),
                                     "lat": f.geometry().coordinates().get(1)}))
        pts = export_and_fetch(fc, f"hls_sample_{SEED}", ["lon", "lat"])
        CACHE.mkdir(parents=True, exist_ok=True)
        pts.to_csv(cache, index=False)
    if n_use < len(pts):  # a seeded random subset of a random sample is itself a random sample
        pts = pts.iloc[np.sort(np.random.default_rng(SEED).choice(len(pts), n_use, replace=False))]
    print(f"sample: {len(pts)} points")
    geom = ee.Geometry.MultiPoint(pts[["lon", "lat"]].values.tolist())
    fc = ee.FeatureCollection(geom.coordinates().map(lambda c: ee.Feature(ee.Geometry.Point(c))))
    return fc, len(pts), geom


def month_stats(asset, points, bounds, with_indices):
    nir_b, red_b, blue_b = BANDS[asset]

    def prep(img):
        fm = img.select("Fmask")
        clear = fm.bitwiseAnd(CLEAR_BITS).eq(0)
        out = [clear.rename("clear"), fm.gte(0).rename("any")]
        if with_indices:
            nir, red, blue = img.select(nir_b), img.select(red_b), img.select(blue_b)
            ndvi = nir.subtract(red).divide(nir.add(red))
            evi = (nir.subtract(red).multiply(2.5)
                   .divide(nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)))
            out += [ndvi.updateMask(clear).rename("ndvi"),
                    evi.updateMask(clear).updateMask(evi.abs().lte(1)).rename("evi")]
        return ee.Image.cat(out)

    def per_month(start):
        start = ee.Date(start)
        col = ee.ImageCollection(asset).filterBounds(bounds).filterDate(start, start.advance(1, "month"))
        stack = col.map(prep)
        bands = [stack.select("clear").sum().rename("n_clear"),
                 stack.select("any").sum().rename("n_any")]
        if with_indices:
            bands += [stack.select("ndvi").median().rename("ndvi"),
                      stack.select("evi").median().rename("evi")]
        vals = ee.Image.cat(bands).reduceRegions(points, ee.Reducer.first(), scale=30, tileScale=4)
        stats = {
            "images": col.size(),
            "points_clear": vals.filter(ee.Filter.gt("n_clear", 0)).size(),
            "points_any": vals.filter(ee.Filter.gt("n_any", 0)).size(),
            "obs_clear": vals.aggregate_sum("n_clear"),
            "obs_any": vals.aggregate_sum("n_any"),
        }
        if with_indices:
            stats["ndvi"] = vals.filter(ee.Filter.notNull(["ndvi"])).aggregate_mean("ndvi")
            stats["evi"] = vals.filter(ee.Filter.notNull(["evi"])).aggregate_mean("evi")
            stats["points_evi"] = vals.filter(ee.Filter.notNull(["evi"])).size()
        return ee.Feature(None, stats).set("month", start.format("YYYY-MM"))

    return per_month


def run(asset, months, points, bounds, with_indices):
    per_month = month_stats(asset, points, bounds, with_indices)
    rows = []
    for i in range(0, len(months), 3):
        chunk = months[i:i + 3]
        for attempt in range(5):
            try:
                fc = ee.FeatureCollection(ee.List(chunk).map(per_month)).getInfo()
                break
            except (ee.EEException, ConnectionError, OSError) as e:
                if attempt == 4:
                    raise
                print(f"  {asset.split('/')[-2]} {chunk[0][:7]}: retry {attempt + 1} after {str(e)[:80]}")
                time.sleep(30 * (attempt + 1))
        rows += [dict(product=asset.split("/")[-2], **f["properties"]) for f in fc["features"]]
        print(f"  {asset.split('/')[-2]}: through {chunk[-1][:7]}")
    return rows


def eecu_seconds(profile_text):
    """Total EECU-seconds from an Earth Engine profile (sum of the per-row EECU-s column)."""
    total = 0.0
    for line in profile_text.splitlines():
        m = re.match(r"\s*([\d.]+)\s+\S+\s+\d+\s+\S", line)
        if m:
            total += float(m.group(1))
    return total


def coverage_test(df, n_points):
    s = df[df["product"] == "HLSS30"].copy()
    s["coverage_clear"] = s["points_clear"] / n_points
    s["coverage_any"] = s["points_any"] / n_points
    base = s[(s["month"] >= BASELINE[0]) & (s["month"] <= BASELINE[1])]
    rainy = base[base["month"].str[5:7].astype(int).isin(RAINY)]
    failing = rainy[rainy["coverage_clear"] < COVERAGE_MIN]
    verdict = "FAILS" if len(failing) > MONTHS_ALLOWED else "passes"
    return rainy, failing, verdict


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--probe", action="store_true", help="one month only, to measure cost")
    args.add_argument("--points", type=int, default=SAMPLE, help="points used (subset of the sample)")
    args.add_argument("--month", default="2025-01", help="probe month, YYYY-MM")
    a = args.parse_args()
    probe = a.probe
    init()
    mode = f"{'probe' if probe else 'full'}_{a.points}pts"
    buf = io.StringIO()
    t0 = time.time()
    with ee.profilePrinting(destination=buf):
        states = region()
        points, n_points, bounds = sample_points(states, a.points)
        # Only granules containing a sample point (owner decision 2026-10-13): a granule without a
        # point contributes nothing to any point value, so results are unchanged and cost falls.
        months = ([f"{a.month}-01"] if probe else
                  pd.date_range(FIRST, LAST, freq="MS").strftime("%Y-%m-%d").tolist())
        l30_months = months if probe else [m for m in months if int(m[5:7]) in RAINY]
        rows = run(S30, months, points, bounds, with_indices=True)
        rows += run(L30, l30_months, points, bounds, with_indices=False)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prof_dir = WEEK0 / "profiles"
    prof_dir.mkdir(parents=True, exist_ok=True)
    (prof_dir / f"hls_{mode}_{stamp}.txt").write_text(buf.getvalue(), encoding="utf-8")
    cost = eecu_seconds(buf.getvalue())
    batch = sum(c for _, c in BATCH_COSTS)
    df = pd.DataFrame(rows)
    print(f"\n{mode}: {len(months)} month(s) x 2 products, {n_points} points, "
          f"{time.time() - t0:.0f} s wall. Interactive: {cost:,.0f} EECU-seconds; "
          f"batch: {batch:,.0f} EECU-seconds {BATCH_COSTS}")
    if probe:
        print(df.to_string(index=False))
        return
    df.to_csv(WEEK0 / "hls_monthly.csv", index=False)
    rainy, failing, verdict = coverage_test(df, n_points)
    rainy.to_csv(WEEK0 / "hls_coverage_test.csv", index=False)
    print(f"Rainy-season coverage test: {len(failing)} of {len(rainy)} November-March baseline months "
          f"below {COVERAGE_MIN:.0%} clear coverage; allowed {MONTHS_ALLOWED}. HLS {verdict}.")


if __name__ == "__main__":
    main()
