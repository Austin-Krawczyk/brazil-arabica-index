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

Run:    .venv/Scripts/python gee/week0_vj113a1_coverage.py --probe --month 2024-01
        .venv/Scripts/python gee/week0_vj113a1_coverage.py
Writes: docs/week0/vj113a1_coverage.csv, docs/week0/profiles/vj113a1_<mode>_<utc>.txt
"""
import argparse
import datetime as dt
import io
import time

import ee
import pandas as pd

from common import WEEK0, init
from week0_hls_test import eecu_seconds

MAPBIOMAS = ("projects/mapbiomas-public/assets/brazil/lulc/collection10/"
             "mapbiomas_brazil_collection10_integration_v1")
STATES = ["Minas Gerais", "São Paulo"]
RAINY = (11, 12, 1, 2, 3)
COVERAGE_MIN, MONTHS_ALLOWED = 0.60, 2


def months():
    every = pd.date_range("2018-01-01", "2025-12-01", freq="MS")
    return [m.strftime("%Y-%m-%d") for m in every if m.month in RAINY]


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--probe", action="store_true")
    a.add_argument("--month", default="2024-01")
    args = a.parse_args()
    project = init()
    col = ee.ImageCollection(f"projects/{project}/assets/vj113a1_mgsp")
    states = (ee.FeatureCollection("FAO/GAUL/2025/level1").filter(ee.Filter.eq("GAUL0_NAME", "Brazil"))
              .filter(ee.Filter.inList("GAUL1_NAME", STATES)))
    proj = col.first().select("pixel_reliability").projection()
    coffee = ee.Image(MAPBIOMAS).select("classification_2024").eq(46).unmask(0)
    w = (coffee.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj)
         .updateMask(ee.Image.constant(1).clipToCollection(states)).rename("w"))
    w = w.updateMask(w.gt(0))
    geom = states.geometry().bounds()

    def per_month(start):
        start = ee.Date(start)
        rel = col.filterDate(start, start.advance(1, "month")).select("pixel_reliability")
        good = rel.map(lambda i: i.gte(0).And(i.lte(3))).max().unmask(0)
        anyobs = rel.map(lambda i: i.mask().gt(0)).max().unmask(0)
        stack = ee.Image.cat([w.multiply(good).rename("w_good"), w.multiply(anyobs).rename("w_any"), w])
        sums = stack.reduceRegion(ee.Reducer.sum(), geom, crs=proj, scale=463.3127, maxPixels=1e10,
                                  tileScale=4)
        return ee.Feature(None, sums).set("month", start.format("YYYY-MM"), "composites", rel.size())

    todo = [f"{args.month}-01"] if args.probe else months()
    buf = io.StringIO()
    rows, t0 = [], time.time()
    with ee.profilePrinting(destination=buf):
        for m in todo:
            f = ee.Feature(per_month(m)).getInfo()["properties"]
            f["coverage_good"] = f["w_good"] / f["w"] if f.get("w") else None
            f["coverage_any"] = f["w_any"] / f["w"] if f.get("w") else None
            rows.append(f)
            print(f"  {f['month']}: {f['composites']} composites, good {f['coverage_good']:.1%}")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    mode = "probe" if args.probe else "full"
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"vj113a1_{mode}_{stamp}.txt").write_text(buf.getvalue(), encoding="utf-8")
    cost = eecu_seconds(buf.getvalue())
    print(f"{mode}: {len(todo)} month(s), {time.time() - t0:.0f} s wall, {cost:,.0f} EECU-seconds")
    if args.probe:
        return
    df = pd.DataFrame(rows)
    df.to_csv(WEEK0 / "vj113a1_coverage.csv", index=False)
    below = df[df["coverage_good"] < COVERAGE_MIN]
    verdict = "FAILS" if len(below) > MONTHS_ALLOWED else "passes"
    print(f"Rainy-season test: {len(below)} of {len(df)} November-March months below "
          f"{COVERAGE_MIN:.0%}; allowed {MONTHS_ALLOWED}. VJ113A1 {verdict}.")


if __name__ == "__main__":
    main()
