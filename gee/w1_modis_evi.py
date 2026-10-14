"""W1: regional MOD13Q1 EVI (and NDVI) series over the coffee mask, one region at a time.

For each region and each MOD13Q1 composite, the coffee-weighted median and mean of EVI and NDVI
over the mask, plus the coffee weight with a valid value and the total coffee weight (so the
valid share is visible for every composite).

  regions   the provisional membership (Amendment 34) as unions of IBGE 1989 mesoregions; São
            Paulo is the whole state. Geometry: IBGE malhas, cached in
            data/derived/_tmp_ibge_malhas.json
  weight    coffee fraction of each MOD13Q1 pixel, from MapBiomas Collection 10 class 46 at 30 m
  values    EVI and NDVI × 0.0001
  median    weighted by the coffee fraction (the fraction is the pixel's mask value)

PROVISIONAL, for the cost probe only, and not prereg-1 values:
  - mask year: classification_2024 for every composite. The mask year by season (S−2 or S−3) is
    set at prereg-2.
  - QA: SummaryQA 0-1 (good, marginal), the drift check's rule. The cloud/QA rule is an OPEN
    prereg-1 item.

Probe-gated (owner, 2026-10-14): the probe is one region and one calendar year of composites,
and must stay within 0.5 EECU-hours (1,800 EECU-seconds). Only the probe is run.

The per-composite statistics run as one batch table export to the bucket: an interactive request
over a year of composites hit Earth Engine's limit on concurrent aggregations (2026-10-14). The
batch task reports its own EECU cost.

Coffee weight saved once (owner decision 2026-10-14, after the first probe failed at 3,635
EECU-seconds by rebuilding the weight per composite): --export-weight writes the region's weight
as an asset in the MOD13Q1 grid, w1_coffee_weight_<region>_mask<year>, by one batch export. The
probe then reads it. Same reducers, same weights.

Run:    .venv/Scripts/python gee/w1_modis_evi.py --export-weight --region "Sul e Centro-Oeste"
        .venv/Scripts/python gee/w1_modis_evi.py --probe --region "Sul e Centro-Oeste" --year 2021
Writes: docs/week0/w1_probe_<region>_<year>.csv, docs/week0/profiles/w1_probe_<utc>.txt
"""
import argparse
import datetime as dt
import json
import re
import time

import ee
import pandas as pd

from common import ROOT, WEEK0, init
from week0_hls_test import BATCH_COSTS, export_and_fetch

MAPBIOMAS = ("projects/mapbiomas-public/assets/brazil/lulc/collection10/"
             "mapbiomas_brazil_collection10_integration_v1")
MASK_YEAR = 2024  # provisional; see the docstring
QA_MAX = 1  # provisional; see the docstring
SCALE = 0.0001
REGIONS = {  # IBGE 1989 mesoregion codes (MG), or the state code (SP)
    "Sul e Centro-Oeste": ("mg_meso", ["3109", "3110"]),
    "Triângulo, Alto Paranaíba e Noroeste": ("mg_meso", ["3101", "3105"]),
    "Zona da Mata, Rio Doce e Central": ("mg_meso", ["3106", "3107", "3108", "3111", "3112"]),
    "São Paulo (state total)": ("sp", ["35"]),
}
PROBE_LIMIT = 1800  # EECU-seconds


def region_geometry(name):
    layer, codes = REGIONS[name]
    malhas = json.loads((ROOT / "data" / "derived" / "_tmp_ibge_malhas.json").read_text(encoding="utf-8"))
    feats = [f for f in malhas[layer]["features"] if f["properties"]["codarea"] in codes]
    assert len(feats) == len(codes), (name, len(feats))
    return ee.FeatureCollection([ee.Feature(ee.Geometry(f["geometry"])) for f in feats]).geometry()


def slug_of(region):
    return re.sub(r"[^a-z]+", "_", region.lower()).strip("_")[:20]


def weight_asset(project, region):
    return f"projects/{project}/assets/w1_coffee_weight_{slug_of(region)}_mask{MASK_YEAR}"


def export_weight(project, region):
    """Coffee fraction of each MOD13Q1 pixel inside the region, saved once as an asset."""
    proj = ee.ImageCollection("MODIS/061/MOD13Q1").first().select("EVI").projection()
    geom = region_geometry(region)
    coffee = ee.Image(MAPBIOMAS).select(f"classification_{MASK_YEAR}").eq(46).unmask(0)
    w = (coffee.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj)
         .clip(geom).rename("w"))
    w = w.updateMask(w.gt(0)).toFloat()
    p = proj.getInfo()
    task = ee.batch.Export.image.toAsset(
        image=w, description=f"w1_weight_{slug_of(region)}", assetId=weight_asset(project, region),
        crs=p["crs"], crsTransform=p["transform"], region=geom.bounds(), maxPixels=1e10,
        pyramidingPolicy={"w": "mean"})
    task.start()
    t0 = time.time()
    while True:
        status = task.status()
        if status["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(30)
    cost = float(status.get("batch_eecu_usage_seconds", 0) or 0)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles" / f"w1_weight_export_{stamp}.txt").write_text(
        f"batch export w1 weight {region}, mask {MASK_YEAR}: {status['state']}, {cost:,.0f} "
        f"EECU-seconds (batch_eecu_usage_seconds), {time.time() - t0:.0f} s wall\n", encoding="utf-8")
    print(f"weight export {status['state']}: {cost:,.0f} EECU-seconds, {time.time() - t0:.0f} s wall"
          + (f" | {status.get('error_message', '')}" if status["state"] != "COMPLETED" else ""))


def run(project, region, start, end):
    col = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate(start, end)
    proj = col.first().select("EVI").projection()
    w = ee.Image(weight_asset(project, region)).select("w")
    # one aggregation per composite: median, mean and sum of every band (the sum of a weight band
    # is the weight; the median and mean of a weight band are not used)
    reducer = (ee.Reducer.median().combine(ee.Reducer.mean(), sharedInputs=True)
               .combine(ee.Reducer.sum(), sharedInputs=True))

    def per_image(img):
        qa = img.select("SummaryQA")
        ok = qa.gte(0).And(qa.lte(QA_MAX))
        vi = img.select(["EVI", "NDVI"]).multiply(SCALE).updateMask(ok).updateMask(w)
        stack = ee.Image.cat([vi, w.updateMask(ok).rename("w_valid"), w.rename("w_total")])
        stats = stack.reduceRegion(reducer, crs=proj, scale=231.656, maxPixels=1e10,
                                   tileScale=4)  # over the weight asset's footprint
        return ee.Feature(None, stats).set("composite_start", img.date().format("YYYY-MM-dd"))

    return ee.FeatureCollection(col.map(per_image)), col.size()


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--probe", action="store_true", help="only the probe is run")
    a.add_argument("--export-weight", action="store_true", help="save the region's coffee weight once")
    a.add_argument("--region", default="Sul e Centro-Oeste", choices=list(REGIONS))
    a.add_argument("--year", type=int, default=2021)
    args = a.parse_args()
    project = init()
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    if args.export_weight:
        return export_weight(project, args.region)
    if not args.probe:
        raise SystemExit("Only --export-weight or --probe; the full run is not started from here.")
    t0 = time.time()
    slug = slug_of(args.region)
    fc, n = run(project, args.region, f"{args.year}-01-01", f"{args.year + 1}-01-01")
    selectors = ["composite_start"] + [f"{b}_{r}" for b in ("EVI", "NDVI") for r in ("median", "mean")] + [
        "w_valid_sum", "w_total_sum"]
    df = export_and_fetch(fc, f"w1_probe_{slug}_{args.year}", selectors)
    cost = BATCH_COSTS[-1][1]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"w1_probe_{stamp}.txt").write_text(
        f"batch export w1_probe_{slug}_{args.year}: {cost:,.0f} EECU-seconds (batch_eecu_usage_seconds), "
        f"{time.time() - t0:.0f} s wall\n", encoding="utf-8")
    df["valid_share"] = df["w_valid_sum"] / df["w_total_sum"]
    df.to_csv(WEEK0 / f"w1_probe_{slug}_{args.year}.csv", index=False)
    print(f"probe: {args.region}, {args.year}: {len(df)} composites, {time.time() - t0:.0f} s wall, "
          f"{cost:,.0f} EECU-seconds (limit {PROBE_LIMIT}) -> {'PASS' if cost <= PROBE_LIMIT else 'FAIL'}")
    return df, cost


if __name__ == "__main__":
    main()
