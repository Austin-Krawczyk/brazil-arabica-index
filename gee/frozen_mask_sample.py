"""SUPERSEDED by gee/frozen_mask_pixels.py. Its one-year probe (mask year 2025) was cancelled by the
watchdog at 2,268 EECU-seconds, past its 1,800 limit (2026-10-15): a 30 m stratified sample over
the MG/SP index area costs too much to repeat for 19 mask years. Kept as the record of that run.

prereg-2: a coffee point sample on the frozen mask, for the frost station set, the elevation cut
and observed coverage (§5 step 4, Amendment 17c). The provisional figures used a 20,000-point
sample of Collection 10 (2024); the registered set is recomputed on the frozen mask (Week 0 report
§8).

Frozen mask (prereg-2, registered 2026-10-15): MapBiomas Collection 11, class 46, mask year
M = S−2, in the index municipalities. The stable filter (Amendment 16d) is applied afterwards,
locally, from each point's municipality code, so the no-filter sensitivity uses the same sample.

Sample: for each mask year M = 2007–2025 (frost windows Jun–Aug 2008–2026, crops 2009–2027),
N points per region drawn uniformly over class-46 pixels at 30 m (stratifiedSample, with the
region as the stratum; seed 20261015 + M). Each point carries its longitude and latitude, its
municipality code and region, and SRTM elevation (`USGS/SRTMGL1_003`, as in the provisional cut).

Batch only (Amendment 32b): one table export under gee/ee_watchdog.py with a required estimate,
cancelled at 2 × it. --probe draws one mask year first, and its measured cost sets the full
run's estimate.

Run:    .venv/Scripts/python gee/frozen_mask_sample.py --probe --year 2025 --estimate 900
        .venv/Scripts/python gee/frozen_mask_sample.py --estimate E
Writes: data/derived/frozen_mask_sample.csv (or _probe_<year>.csv; gitignored),
        docs/week0/profiles/frozen_mask_sample_<utc>.txt
"""
import argparse
import datetime as dt
import json
import time

import ee

import ee_watchdog as wd
from common import ROOT, WEEK0, init

C11 = ("projects/mapbiomas-public/assets/brazil/lulc/collection11/"
       "mapbiomas_brazil_collection11_coverage_v3")
REGION_ID = {"Sul e Centro-Oeste": 1, "Triângulo, Alto Paranaíba e Noroeste": 2,
             "Zona da Mata, Rio Doce e Central": 3, "São Paulo (state total)": 4}
N_PER_REGION = 10000
YEARS = range(2007, 2026)
SEED = 20261015
SELECTORS = ["mask_year", "region_id", "code", "elev_m", "longitude", "latitude"]


def sample_year(munis, year):
    fc = munis.map(lambda f: f.set("region_id", ee.Dictionary(REGION_ID).get(f.get("region"))))
    rid = ee.Image().int().paint(fc, "region_id").rename("region_id")
    code = ee.Image().int().paint(fc, "code_int").rename("code")
    elev = ee.Image("USGS/SRTMGL1_003").select("elevation").rename("elev_m")
    coffee = ee.Image(C11).select(f"classification_{year}").eq(46)
    img = ee.Image.cat([rid.updateMask(coffee), code, elev, ee.Image.pixelLonLat()])
    pts = img.stratifiedSample(numPoints=0, classBand="region_id", classValues=[1, 2, 3, 4],
                               classPoints=[N_PER_REGION] * 4, region=munis.geometry().bounds(),
                               scale=30, projection=ee.Image(C11).projection(), seed=SEED + year,
                               dropNulls=True, tileScale=16, geometries=False)
    return pts.map(lambda f: f.set("mask_year", year))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--probe", action="store_true", help="one mask year only")
    a.add_argument("--year", type=int, default=2025)
    a.add_argument("--estimate", type=float, required=True, help="cost estimate in EECU-seconds")
    args = a.parse_args()
    project = init()
    munis = ee.FeatureCollection(f"projects/{project}/assets/w1_municipios_index")
    years = [args.year] if args.probe else list(YEARS)
    name = f"frozen_mask_sample_probe_{args.year}" if args.probe else "frozen_mask_sample"
    if args.probe:
        wd.set_session_cap("prereg2_frozen_sample", 1.5 * 2 * args.estimate)
    else:  # keep the probe's spend; cap at 1.5 x (spent + this estimate), as in gee/w1_run.py
        led = wd._ledger()
        led["cap"] = 1.5 * (led.get("spent", 0.0) + args.estimate)
        wd.LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")
        wd._log(f"session cap {led['cap']:,.0f} EECU-s")
    fc = ee.FeatureCollection([sample_year(munis, y) for y in years]).flatten()
    t0 = time.time()
    df, used = wd.export_table_watched(fc, name, SELECTORS, args.estimate, prefix="week0")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"{name}_{stamp}.txt").write_text(
        f"batch export {name}: {used:,.0f} EECU-seconds (batch), "
        f"{0 if df is None else len(df)} points, {len(years)} mask year(s), {time.time() - t0:.0f} s wall\n",
        encoding="utf-8")
    if df is None:
        raise SystemExit(f"{name}: not completed ({used:,.0f} EECU-seconds)")
    df.to_csv(ROOT / "data" / "derived" / f"{name}.csv", index=False)
    per = df.groupby(["mask_year", "region_id"]).size().unstack()
    print(f"{name}: {len(df):,} points, {used:,.0f} EECU-seconds\n{per.to_string()}")


if __name__ == "__main__":
    main()
