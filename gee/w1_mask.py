"""W1: the per-season coffee mask (§5 step 1; Amendments 16, 16b, 16c).

Product: MapBiomas Collection 11 (Amendment 16c), class 46. Lag S−2: crop S uses mask year S−2.

Steps (run in order; each is a separate batch job whose cost is recorded):

  municipalities   the index municipalities (provisional membership, Amendment 34) as an Earth
                   Engine table, from IBGE's municipal mesh (data/raw/ibge/)
  areas            per municipality and year: class-46 area in that year ("full"), and for each
                   mask year M the area classified 46 in M, M−1 and M−2 ("persistent",
                   Amendment 16b), in hectares, at 30 m. --probe does one mask year only.
  weights          per region: coffee fraction of each MOD13Q1 pixel for each mask year, full and
                   persistent, excluding the municipalities the 30% filter removed for that
                   season. Saved once as a multi-band asset; W1 reads it.

The 30% filter itself and its removal report are computed locally by gee/w1_filter.py from the
areas table and IBGE PAM.

Run:    .venv/Scripts/python gee/w1_mask.py municipalities
        .venv/Scripts/python gee/w1_mask.py areas --probe --year 2024
        .venv/Scripts/python gee/w1_mask.py areas
        .venv/Scripts/python gee/w1_mask.py weights --region "Sul e Centro-Oeste"
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

C11 = ("projects/mapbiomas-public/assets/brazil/lulc/collection11/"
       "mapbiomas_brazil_collection11_coverage_v3")
LAG = 2
SEASONS = range(2000, 2028)          # crop 2000 covers the baseline's first composites (Feb-Apr 2000)
MASK_YEARS = [s - LAG for s in SEASONS]  # 1998-2025
FULL_YEARS = range(min(MASK_YEARS) - 3, max(MASK_YEARS) + 1)  # 1995-2025, for the 3-year change
MUNI_ASSET = "w1_municipios_index"
DERIVED = ROOT / "data" / "derived"


def log_cost(name, cost, extra=""):
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"w1_mask_{name}_{stamp}.txt").write_text(
        f"{name}: {cost:,.0f} EECU-seconds (batch_eecu_usage_seconds){extra}\n", encoding="utf-8")
    print(f"{name}: {cost:,.0f} EECU-seconds{extra}")


def wait(task):
    t0 = time.time()
    while True:
        st = task.status()
        if st["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
            return st, time.time() - t0
        time.sleep(30)


def municipalities(project):
    member = pd.read_csv(WEEK0 / "proposed_region_membership.csv", dtype={"code": str})
    member = member[member.in_index].set_index("code")
    feats = []
    for uf in ("31", "35"):
        mesh = json.loads((ROOT / "data" / "raw" / "ibge" / f"malha_municipios_{uf}_intermediaria.geojson")
                          .read_text(encoding="utf-8"))
        for f in mesh["features"]:
            code = f["properties"]["codarea"]
            if code in member.index:
                feats.append(ee.Feature(ee.Geometry(f["geometry"]), {
                    "code": code, "code_int": int(code), "region": member.at[code, "conab_region"]}))
    print(f"{len(feats)} index municipalities (membership lists {len(member)})")
    task = ee.batch.Export.table.toAsset(collection=ee.FeatureCollection(feats), description=MUNI_ASSET,
                                         assetId=f"projects/{project}/assets/{MUNI_ASSET}")
    task.start()
    st, wall = wait(task)
    log_cost("municipalities", float(st.get("batch_eecu_usage_seconds", 0) or 0),
             f", {st['state']}, {wall:.0f} s wall")


def coffee(year):
    return ee.Image(C11).select(f"classification_{year}").eq(46)


def areas(project, probe_year=None, sample_codes=None):
    munis = ee.FeatureCollection(f"projects/{project}/assets/{MUNI_ASSET}")
    if sample_codes:
        munis = munis.filter(ee.Filter.inList("code", sample_codes))
    ha = ee.Image.pixelArea().divide(1e4)
    if probe_year:
        full_years, mask_years = [probe_year], [probe_year]
    else:
        full_years, mask_years = list(FULL_YEARS), MASK_YEARS
    bands = [coffee(y).multiply(ha).rename(f"full_{y}") for y in full_years]
    bands += [coffee(m).And(coffee(m - 1)).And(coffee(m - 2)).multiply(ha).rename(f"pers_{m}")
              for m in mask_years]
    img = ee.Image.cat(bands)
    out = img.reduceRegions(collection=munis.select(["code", "region"]), reducer=ee.Reducer.sum(),
                            scale=30, crs="EPSG:4326", tileScale=4)
    name = (f"w1_mask_areas_probe_{probe_year}" if probe_year else
            "w1_mask_areas_sample_probe" if sample_codes else "w1_mask_areas")
    df = export_and_fetch(out, name, ["code", "region"] + img.bandNames().getInfo())
    cost = BATCH_COSTS[-1][1]
    log_cost(name, cost, f", {len(df)} municipalities, {len(img.bandNames().getInfo())} bands")
    df.to_csv(DERIVED / f"{name}.csv", index=False)
    return df, cost


def weights(project, region):
    kept = pd.read_csv(WEEK0 / "w1_filter_kept.csv", dtype={"code": str})  # code, mask_year, kept
    munis = ee.FeatureCollection(f"projects/{project}/assets/{MUNI_ASSET}").filter(ee.Filter.eq("region", region))
    codes = ee.Image().int().paint(munis, "code_int").rename("code")
    proj = ee.ImageCollection("MODIS/061/MOD13Q1").first().select("EVI").projection()
    bands = []
    for m in MASK_YEARS:
        keep = [int(c) for c in kept[(kept.mask_year == m) & kept.kept].code]
        ok = codes.remap(keep, [1] * len(keep), 0).eq(1) if keep else ee.Image(0)
        full = coffee(m).And(ok).unmask(0)
        pers = coffee(m).And(coffee(m - 1)).And(coffee(m - 2)).And(ok).unmask(0)
        for kind, img in (("w", full), ("wp", pers)):
            bands.append(img.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj)
                         .rename(f"{kind}_{m}").toFloat())
    img = ee.Image.cat(bands).updateMask(codes.reduceResolution(ee.Reducer.count(), maxPixels=1024)
                                         .reproject(proj).gt(0))
    slug = re.sub(r"[^a-z]+", "_", region.lower()).strip("_")[:20]
    p = proj.getInfo()
    task = ee.batch.Export.image.toAsset(
        image=img, description=f"w1_weights_{slug}", assetId=f"projects/{project}/assets/w1_weights_{slug}",
        crs=p["crs"], crsTransform=p["transform"], region=munis.geometry().bounds(), maxPixels=1e11,
        pyramidingPolicy={".default": "mean"})
    task.start()
    st, wall = wait(task)
    log_cost(f"weights_{slug}", float(st.get("batch_eecu_usage_seconds", 0) or 0),
             f", {st['state']}, {wall:.0f} s wall, {len(bands)} bands"
             + (f" | {st.get('error_message', '')}" if st["state"] != "COMPLETED" else ""))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("step", choices=["municipalities", "areas", "weights"])
    a.add_argument("--probe", action="store_true")
    a.add_argument("--year", type=int, default=2024)
    a.add_argument("--region")
    a.add_argument("--sample", help="file of municipality codes: all bands, those municipalities only")
    args = a.parse_args()
    project = init()
    if args.step == "municipalities":
        municipalities(project)
    elif args.step == "areas":
        codes = open(args.sample).read().split() if args.sample else None
        areas(project, args.year if args.probe and not codes else None, codes)
    else:
        weights(project, args.region)


if __name__ == "__main__":
    main()
