"""VJ113A1 acceptance check (Amendment 30, second revision): the HLS rainy-season test, applied to
the fallback.

Monthly coverage = the coffee-area-weighted share of VJ113A1 pixels within the mask that have a
"good" pixel reliability (0-3, excellent to marginal, as in the drift check) in at least one
composite starting in the month. Fails if more than 2 of the 40 November-March months in
2018-2025 fall below 60%.

Mask: the same provisional MG/SP coffee mask as the HLS test (MapBiomas Collection 10
classification_2024 == 46 inside GAUL 2025 level 1 Minas Gerais and São Paulo), weighted by the
coffee fraction of each VJ113A1 pixel. "Any" coverage (any non-missing reliability) is reported
beside it. Cost is profiled (Amendment 32).

The coffee weight is the same for every month, and rebuilding it in each month's request was 97%
of the first probe's cost (2026-10-14). It is therefore built once, by a batch export to an asset
in the VJ113A1 grid (owner decision 2026-10-14), and read from there. Same reducers, same weights.

Batch only (owner rule 2026-10-15): the monthly sums, formerly one interactive request per month
(the 2026-10-14 results were measured that way), now run as one batch table export, and the weight
as one batch image export, both under gee/ee_watchdog.py with a required estimate. The measured
costs to estimate from: weight export and 40 months in docs/week0/profiles/vj113a1_*.

Run:    .venv/Scripts/python gee/week0_vj113a1_coverage.py --export-weight --estimate E
        .venv/Scripts/python gee/week0_vj113a1_coverage.py --probe --month 2024-01 --estimate E
        .venv/Scripts/python gee/week0_vj113a1_coverage.py --estimate E
Writes: docs/week0/vj113a1_coverage.csv, docs/week0/profiles/vj113a1_<mode>_<utc>.txt
"""
import argparse
import datetime as dt
import time

import ee
import pandas as pd

from common import WEEK0, init
from vj113a1_ingest import COLLECTION
from week0_hls_test import BATCH_COSTS, export_and_fetch

MAPBIOMAS = ("projects/mapbiomas-public/assets/brazil/lulc/collection10/"
             "mapbiomas_brazil_collection10_integration_v1")
STATES = ["Minas Gerais", "São Paulo"]
RAINY = (11, 12, 1, 2, 3)
COVERAGE_MIN, MONTHS_ALLOWED = 0.60, 2
WEIGHT_ASSET = "vj113a1_coffee_weight_mgsp"


def months():
    every = pd.date_range("2018-01-01", "2025-12-01", freq="MS")
    return [m.strftime("%Y-%m-%d") for m in every if m.month in RAINY]


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--probe", action="store_true")
    a.add_argument("--month", default="2024-01")
    a.add_argument("--export-weight", action="store_true", help="build the coffee weight asset once")
    a.add_argument("--estimate", type=float, required=True, help="cost estimate in EECU-seconds (cancelled at 2 x)")
    args = a.parse_args()
    project = init()
    col = ee.ImageCollection(f"projects/{project}/assets/{COLLECTION}")
    states = (ee.FeatureCollection("FAO/GAUL/2025/level1").filter(ee.Filter.eq("GAUL0_NAME", "Brazil"))
              .filter(ee.Filter.inList("GAUL1_NAME", STATES)))
    proj = col.first().select("pixel_reliability").projection()
    if args.export_weight:
        export_weight(project, proj, states, args.estimate)
        return
    w = ee.Image(f"projects/{project}/assets/{WEIGHT_ASSET}").select("w")

    def per_month(start):
        start = ee.Date(start)
        rel = col.filterDate(start, start.advance(1, "month")).select("pixel_reliability")
        good = rel.map(lambda i: i.gte(0).And(i.lte(3))).max().unmask(0)
        anyobs = rel.map(lambda i: i.mask().gt(0)).max().unmask(0)
        stack = ee.Image.cat([w.multiply(good).rename("w_good"), w.multiply(anyobs).rename("w_any"), w])
        sums = stack.reduceRegion(ee.Reducer.sum(), crs=proj, scale=463.3127, maxPixels=1e10,
                                  tileScale=4)  # over the weight asset's own footprint
        return ee.Feature(None, sums).set("month", start.format("YYYY-MM"), "composites", rel.size())

    todo = [f"{args.month}-01"] if args.probe else months()
    t0 = time.time()
    mode = "probe" if args.probe else "full"
    df = export_and_fetch(ee.FeatureCollection(ee.List(todo).map(per_month)), f"vj113a1_coverage_{mode}",
                          ["month", "composites", "w_good", "w_any", "w"], args.estimate)
    df["coverage_good"] = df["w_good"] / df["w"]
    df["coverage_any"] = df["w_any"] / df["w"]
    for _, f in df.iterrows():
        print(f"  {f['month']}: {f['composites']} composites, good {f['coverage_good']:.1%}")
    cost = BATCH_COSTS[-1][1]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"vj113a1_{mode}_{stamp}.txt").write_text(
        f"batch export vj113a1_coverage_{mode}: {cost:,.0f} EECU-seconds (batch), {len(df)} months, "
        f"{time.time() - t0:.0f} s wall\n", encoding="utf-8")
    print(f"{mode}: {len(todo)} month(s), {time.time() - t0:.0f} s wall, {cost:,.0f} EECU-seconds")
    if args.probe:
        return
    df.to_csv(WEEK0 / "vj113a1_coverage.csv", index=False)
    below = df[df["coverage_good"] < COVERAGE_MIN]
    verdict = "FAILS" if len(below) > MONTHS_ALLOWED else "passes"
    print(f"Rainy-season test: {len(below)} of {len(df)} November-March months below "
          f"{COVERAGE_MIN:.0%}; allowed {MONTHS_ALLOWED}. VJ113A1 {verdict}.")


def export_weight(project, proj, states, estimate_eecu_s):
    """Coffee fraction of each VJ113A1 pixel inside MG/SP, as an asset in the VJ113A1 grid."""
    from ee_watchdog import run_watched

    coffee = ee.Image(MAPBIOMAS).select("classification_2024").eq(46).unmask(0)
    w = (coffee.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj)
         .updateMask(ee.Image.constant(1).clipToCollection(states)).rename("w"))
    w = w.updateMask(w.gt(0)).toFloat()
    p = proj.getInfo()  # interactive: metadata (projection)
    task = ee.batch.Export.image.toAsset(
        image=w, description=WEIGHT_ASSET, assetId=f"projects/{project}/assets/{WEIGHT_ASSET}",
        crs=p["crs"], crsTransform=p["transform"], region=states.geometry().bounds(),
        maxPixels=1e10, pyramidingPolicy={"w": "mean"})
    state, cost, wall = run_watched(task, estimate_eecu_s)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"vj113a1_weight_export_{stamp}.txt").write_text(
        f"batch export {WEIGHT_ASSET}: {state}, {cost:,.0f} EECU-seconds "
        f"(batch_eecu_usage_seconds), {wall:.0f} s wall\n", encoding="utf-8")
    print(f"weight export {state}: {cost:,.0f} EECU-seconds, {wall:.0f} s wall")


if __name__ == "__main__":
    main()
