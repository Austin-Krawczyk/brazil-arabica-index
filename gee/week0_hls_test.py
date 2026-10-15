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
  granules    only those on MGRS tiles (UTM zones 21-24) containing a sample point; excludes
              HLSS30's date-line granules with infinite footprints (owner decision 2026-10-13)
  cost        ee.profilePrinting for every run, saved under docs/week0/profiles/

Anomalies against a baseline are NOT computed here: the baseline for comparisons with HLS is open
(§10). This script saves the monthly series only.

Option C (owner decision 2026-10-13): 5,000 points, a seeded random subset of the 20,000-point
sample (numpy default_rng(20261012)); HLSS30 for every month, HLSL30 for November-March months
only, as information.

Batch only (owner rule 2026-10-15): the monthly statistics, formerly one interactive request per
month, now run as one batch table export under gee/ee_watchdog.py with a required estimate. The
interactive calls left are metadata (state count, granule IDs).

Run:    .venv/Scripts/python gee/week0_hls_test.py --mode coverage --probe --estimate E [--month YYYY-MM]
        .venv/Scripts/python gee/week0_hls_test.py --mode coverage --points 5000 --estimate E
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

from common import ROOT, WEEK0, init

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
# HLSS30 in Earth Engine holds granules from date-line tiles (UTM zones 01 and 60) whose footprints
# are infinite, so filterBounds returns them everywhere (found 2026-10-13). MG and SP lie in UTM
# zones 22-24; 21 is kept as a margin because tiles extend past zone edges.
ZONES = (21, 22, 23, 24)
TILE_WINDOW = ("2024-07-01", "2024-09-01")  # two dry-season months of granules, to list the tiles


def region():
    fc = (ee.FeatureCollection("FAO/GAUL/2025/level1")
          .filter(ee.Filter.eq("GAUL0_NAME", "Brazil"))
          .filter(ee.Filter.inList("GAUL1_NAME", STATES)))
    n = fc.size().getInfo()  # interactive: metadata (feature count of a filtered table)
    if n != len(STATES):
        raise SystemExit(f"Expected {len(STATES)} state polygons, found {n}.")
    return fc


BATCH_COSTS = []  # (task, EECU-seconds) for batch tasks, which request profiling does not see


def export_and_fetch(fc, name, selectors, estimate_eecu_s):
    """Run a table export to the bucket as a batch task under the watchdog (gee/ee_watchdog.py: a
    cost estimate is required, and the task is cancelled at 2 x it) and fetch the result. Owner
    rule 2026-10-15: no interactive reductions; every area reduction goes through here or through
    export_table_watched()."""
    from ee_watchdog import export_table_watched

    df, used = export_table_watched(fc, name, selectors, estimate_eecu_s, prefix="week0")
    BATCH_COSTS.append((name, used))
    if df is None:
        raise SystemExit(f"Batch task {name} did not complete ({used:,.0f} EECU-seconds); see the watchdog log")
    return df


SUBSET_SEED = 20261013  # draws the 500-point subset from the 5,000 (owner decision 2026-10-13)


def sample_points(states, n_use, subset_of=None, estimate_eecu_s=None):
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
        pts = export_and_fetch(fc, f"hls_sample_{SEED}", ["lon", "lat"], estimate_eecu_s)
        CACHE.mkdir(parents=True, exist_ok=True)
        pts.to_csv(cache, index=False)
    # A seeded random subset of a random sample is itself a random sample. With subset_of, the
    # subset is nested: first the subset_of points (seed SEED), then n_use of those (SUBSET_SEED).
    first = subset_of if subset_of else n_use
    if first < len(pts):
        pts = pts.iloc[np.sort(np.random.default_rng(SEED).choice(len(pts), first, replace=False))]
    if subset_of and n_use < len(pts):
        pts = pts.iloc[np.sort(np.random.default_rng(SUBSET_SEED).choice(len(pts), n_use, replace=False))]
    print(f"sample: {len(pts)} points")
    geom = ee.Geometry.MultiPoint(pts[["lon", "lat"]].values.tolist())
    fc = ee.FeatureCollection(geom.coordinates().map(lambda c: ee.Feature(ee.Geometry.Point(c))))
    return fc, len(pts), pts[["lon", "lat"]].values


def point_tiles(asset, coords):
    """MGRS tiles (in zones 21-24) whose granules contain at least one sample point, listed once
    from two months of granule metadata, so no geometry test runs inside the monthly computation.
    Done in batches of points: one request over all points and a year of granules exceeded Earth
    Engine's memory limit. Every tile is imaged several times a month, so two months list them all."""
    zones = ee.Filter.Or(*[ee.Filter.stringStartsWith("system:index", f"T{z}") for z in ZONES])
    col = ee.ImageCollection(asset).filterDate(*TILE_WINDOW).filter(zones)
    tiles = set()
    for batch in np.array_split(coords, 10):
        mp = ee.Geometry.MultiPoint(batch.tolist())
        ids = col.filterBounds(mp).aggregate_array("system:index").getInfo()  # interactive: metadata (granule IDs)
        tiles |= {i.split("_")[0] for i in ids}
    print(f"  {asset.split('/')[-2]}: {len(tiles)} tiles contain sample points")
    return sorted(tiles)


def month_stats(asset, points, bounds, with_indices, tiles):
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
        col = (ee.ImageCollection(asset).filterBounds(bounds).filterDate(start, start.advance(1, "month"))
               .map(lambda i: i.set("tile", ee.String(i.get("system:index")).split("_").get(0)))
               .filter(ee.Filter.inList("tile", tiles)))
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


def run(asset, months, points, bounds, with_indices, tiles, name, estimate_eecu_s):
    """Every requested month in one batch table export under the watchdog (owner rule 2026-10-15:
    no interactive reductions; until then this was one interactive request per month)."""
    product = asset.split("/")[-2]
    per_month = month_stats(asset, points, bounds, with_indices, tiles)
    selectors = ["month", "images", "points_clear", "points_any", "obs_clear", "obs_any"]
    if with_indices:
        selectors += ["ndvi", "evi", "points_evi"]
    df = export_and_fetch(ee.FeatureCollection(ee.List(months).map(per_month)), name, selectors, estimate_eecu_s)
    df.insert(0, "product", product)
    return df.to_dict("records")


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


def months_for(mode):
    """Option D (coverage): the November-March months inside the July 2017-December 2025 baseline,
    plus January-March 2017 as information. Reference: every month July 2017-September 2026."""
    every = pd.date_range(FIRST, LAST, freq="MS").strftime("%Y-%m-%d").tolist()
    if mode == "coverage":
        rainy = [m for m in every if int(m[5:7]) in RAINY]
        return ([m for m in rainy if "2017-01" <= m[:7] <= "2017-03"]
                + [m for m in rainy if BASELINE[0] <= m[:7] <= BASELINE[1]])
    return [m for m in every if m[:7] >= "2017-07"]


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--mode", choices=["coverage", "reference"], required=True,
                      help="coverage: option D; reference: NDVI/EVI series for the drift check")
    args.add_argument("--probe", action="store_true", help="one month only, to measure cost")
    args.add_argument("--points", type=int, default=5000, help="points used")
    args.add_argument("--subset-of", type=int, default=None, help="draw --points from this subset")
    args.add_argument("--month", default="2024-01", help="probe month, YYYY-MM")
    args.add_argument("--estimate", type=float, required=True,
                      help="cost estimate in EECU-seconds for the monthly table (cancelled at 2 x)")
    args.add_argument("--sample-estimate", type=float,
                      help="cost estimate for drawing the sample, needed only if it is not cached")
    a = args.parse_args()
    init()
    tag = f"{a.mode}_{'probe' if a.probe else 'full'}_{a.points}pts"
    with_indices = a.mode == "reference"
    buf = io.StringIO()
    t0 = time.time()
    with ee.profilePrinting(destination=buf):
        states = region()
        points, n_points, coords = sample_points(states, a.points, a.subset_of, a.sample_estimate)
        bounds = states.geometry().bounds()
        # Only granules on tiles containing a sample point (owner decision 2026-10-13): a granule
        # without a point contributes nothing to any point value, so results are unchanged.
        # HLSL30 dropped (owner decision 2026-10-13).
        tiles = point_tiles(S30, coords)
        months = [f"{a.month}-01"] if a.probe else months_for(a.mode)
        rows = run(S30, months, points, bounds, with_indices=with_indices, tiles=tiles,
                   name=f"hls_{tag}", estimate_eecu_s=a.estimate)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prof_dir = WEEK0 / "profiles"
    prof_dir.mkdir(parents=True, exist_ok=True)
    (prof_dir / f"hls_{tag}_{stamp}.txt").write_text(buf.getvalue(), encoding="utf-8")
    cost = eecu_seconds(buf.getvalue())
    batch = sum(c for _, c in BATCH_COSTS)
    df = pd.DataFrame(rows)
    print(f"\n{tag}: {len(months)} month(s), HLSS30, {n_points} points, {time.time() - t0:.0f} s wall. "
          f"Interactive: {cost:,.0f} EECU-seconds; batch: {batch:,.0f} EECU-seconds {BATCH_COSTS}")
    if a.probe:
        print(df.to_string(index=False))
        return
    out = WEEK0 / f"hls_{a.mode}_{a.points}pts.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} months written to {out.name}")
    if a.mode == "coverage":
        rainy, failing, verdict = coverage_test(df, n_points)
        rainy.to_csv(WEEK0 / "hls_coverage_test.csv", index=False)
        print(f"Rainy-season coverage test: {len(failing)} of {len(rainy)} November-March baseline "
              f"months below {COVERAGE_MIN:.0%} clear coverage; allowed {MONTHS_ALLOWED}. HLS {verdict}.")


if __name__ == "__main__":
    main()
