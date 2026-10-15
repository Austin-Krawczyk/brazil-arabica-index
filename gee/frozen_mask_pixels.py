"""prereg-2: the frozen mask as a pixel table, for the frost station set, the elevation cut and
observed coverage (§5 step 4, Amendment 17c).

Replaces gee/frozen_mask_sample.py, whose one-year probe (a 30 m stratified sample over the MG/SP
index area) was cancelled by the watchdog at 2,268 EECU-seconds, past its 1,800 limit
(2026-10-15). This script reads the coffee weights W1 already saved instead.

Source: the 24 mesoregion assets `w1_weights_meso_<code>` (prereg-2, registered 2026-10-15): the
Collection 11 class-46 fraction of each MOD13Q1 pixel, band `w_M` for mask year M. These are the
frozen mask itself, the same weights the index uses.

Table: every MOD13Q1 pixel with coffee in at least one mask year 2007–2025 (frost windows
Jun–Aug 2008–2026, crops 2009–2027), with:
  w_2007 … w_2025   coffee fraction per mask year (coffee area = fraction × pixel area)
  code, region_id   municipality and region at the pixel centre (IBGE mesh asset)
  elev_m            SRTM (`USGS/SRTMGL1_003`) at the pixel centre, nearest 30 m cell; an
                    approximation to the elevation of the coffee inside the pixel
  longitude, latitude of the pixel centre
The stable filter is applied locally from `code`.

Batch only (Amendment 32b): one table export under gee/ee_watchdog.py with a required estimate,
cancelled at 2 × it. --probe does one mesoregion first.

Run:    .venv/Scripts/python gee/frozen_mask_pixels.py --probe --meso 3109 --estimate 300
        .venv/Scripts/python gee/frozen_mask_pixels.py --estimate E
Writes: data/derived/frozen_mask_pixels[_probe_<meso>].csv (gitignored),
        docs/week0/profiles/frozen_mask_pixels_<utc>.txt
"""
import argparse
import datetime as dt
import json
import time

import ee

import ee_watchdog as wd
from common import ROOT, WEEK0, init
from w1_mask import meso_table

REGION_ID = {"Sul e Centro-Oeste": 1, "Triângulo, Alto Paranaíba e Noroeste": 2,
             "Zona da Mata, Rio Doce e Central": 3, "São Paulo (state total)": 4}
MASK_YEARS = range(2007, 2026)
BANDS = [f"w_{m}" for m in MASK_YEARS]
SCALE = 231.65635826395828  # MOD13Q1 nominal pixel size (m)


def pixel_table(project, mesos):
    member = meso_table()
    codes = member[member.meso_code.isin(mesos)].code.tolist()
    munis = (ee.FeatureCollection(f"projects/{project}/assets/w1_municipios_index")
             .filter(ee.Filter.inList("code", codes))
             .map(lambda f: f.set("region_id", ee.Dictionary(REGION_ID).get(f.get("region")))))
    assets = [ee.Image(f"projects/{project}/assets/w1_weights_meso_{m}") for m in mesos]
    proj = assets[0].select(BANDS[0]).projection()
    w = ee.ImageCollection(assets).mosaic().select(BANDS)
    img = ee.Image.cat([
        w,
        ee.Image().int().paint(munis, "code_int").rename("code"),
        ee.Image().int().paint(munis, "region_id").rename("region_id"),
        ee.Image("USGS/SRTMGL1_003").select("elevation").rename("elev_m"),
        ee.Image.pixelLonLat(),
    ]).updateMask(w.reduce(ee.Reducer.max()).gt(0))
    return img.sample(region=munis.geometry().bounds(), projection=proj, scale=SCALE,
                      dropNulls=True, tileScale=4, geometries=False)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--probe", action="store_true", help="one mesoregion only")
    a.add_argument("--meso", default="3109")
    a.add_argument("--estimate", type=float, required=True, help="cost estimate in EECU-seconds")
    args = a.parse_args()
    project = init()
    mesos = [args.meso] if args.probe else sorted(meso_table().meso_code.unique())
    name = f"frozen_mask_pixels_probe_{args.meso}" if args.probe else "frozen_mask_pixels"
    if args.probe:
        wd.set_session_cap("prereg2_frozen_pixels", 1.5 * 2 * args.estimate)
    else:  # keep the probe's spend; cap at 1.5 x (spent + this estimate), as in gee/w1_run.py
        led = wd._ledger()
        led["cap"] = 1.5 * (led.get("spent", 0.0) + args.estimate)
        wd.LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")
        wd._log(f"session cap {led['cap']:,.0f} EECU-s")
    t0 = time.time()
    selectors = ["code", "region_id", "elev_m", "longitude", "latitude"] + BANDS
    df, used = wd.export_table_watched(pixel_table(project, mesos), name, selectors, args.estimate,
                                       prefix="week0")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"{name}_{stamp}.txt").write_text(
        f"batch export {name}: {used:,.0f} EECU-seconds (batch), {0 if df is None else len(df)} pixels, "
        f"{len(mesos)} mesoregion(s), {time.time() - t0:.0f} s wall\n", encoding="utf-8")
    if df is None:
        raise SystemExit(f"{name}: not completed ({used:,.0f} EECU-seconds)")
    df.to_csv(ROOT / "data" / "derived" / f"{name}.csv", index=False)
    print(f"{name}: {len(df):,} pixels, {used:,.0f} EECU-seconds, {len(mesos)} mesoregion(s)")
    print(df.groupby("region_id")[BANDS[-1]].agg(["size", "sum"]).to_string())


if __name__ == "__main__":
    main()
