"""W2 season inputs from Earth Engine, per index municipality, weighted by coffee (prereg-1 B).
The Amendment 35 aggregation (members, municipal climatology, PAM-weighted regional mean,
regional z-score) is done locally from these tables.

Each product is reduced at its own native grid. The coffee weight is the season's frozen mask:
the W1 weight assets (`w1_weights_meso_<code>`, band `w_{S−2}`), averaged from the 250 m MOD13Q1
grid to the product grid. Areas outside the index municipalities count as no coffee. Each
municipality's row holds Σ(value × weight) per band and Σ weight (`w`), with pixels weighted by
the share of their area inside the municipality, so the coffee-weighted mean is band / w.

products (season S = crop S):
  rain     UCSB-CHG/CHIRPS/DAILY, `precipitation` (mm/day), final, crops 2001–2026:
           d_MMDD   daily totals 1 Sep – 30 Nov of S−1 (91 bands; dry days and pentads
                    computed locally)
           p_MMDD   pentad totals 1 Dec of S−1 – 31 Mar of S, labelled by pentad start (24 bands; the
                    last pentad of February ends on the 28th or 29th)
  prelim   CHC prelim pentads (ingested collection `chc_prelim_pentad_mgsp`, Amendment 9), the
           same reduction as `rain`, for the prelim-versus-final check (owner, 2026-10-15),
           crops 2016–2026 (Sep 2015 – Mar 2026). q_MMDD: pentad totals 1 Sep – 31 Mar, labelled by
           pentad start.
  soil     ECMWF/ERA5_LAND/HOURLY, volumetric_soil_water_layer_1–3 (m³/m³), weighted 0.07 / 0.21 /
           0.72 (Amendment 28), mean of every hour 1 May – 31 Aug of S−1 (UTC). Crops 2001–2027.
           One band, `sm`.
  heat     ECMWF/ERA5_LAND/HOURLY, temperature_2m (K): for each day 1 Sep – 30 Nov of S−1, 1 where
           the day's maximum exceeds 34 °C (307.15 K), else 0. Days run 00:00–24:00 at UTC−3
           (03 UTC to 03 UTC; prereg-1 item 8). 91 bands h_MMDD. Crops 2001–2026.

Batch only (Amendment 32b): one table export per run under gee/ee_watchdog.py with a required
estimate, cancelled at 2 × it. --probe runs one season (crop 2022) over Sul e Centro-Oeste only;
its measured cost sets the full run's estimate. --probe --all-regions runs one season over every
region: for ERA5-Land, whose cost follows the number of hourly images read rather than the area,
the Sul probe under-measured (the soil probe reported 1 EECU-second; the full run was cancelled at
1,102, 2026-10-15).

Run:    .venv/Scripts/python gee/w2_exports.py rain --probe --estimate E [--start-session C]
        .venv/Scripts/python gee/w2_exports.py rain --estimate E [--cap C]
Writes: data/derived/w2_<product>_muni[_probe].csv, docs/week0/profiles/w2_<product>_<utc>.txt
"""
import argparse
import datetime as dt
import json
import time

import ee

import ee_watchdog as wd
from common import ROOT, WEEK0, init
from w1_mask import meso_table

CHIRPS = "UCSB-CHG/CHIRPS/DAILY"
ERA5 = "ECMWF/ERA5_LAND/HOURLY"
SCALES = {"chirps": 5565.974539663679, "era5": 11131.949079327358}  # 0.05° and 0.1°, nominal
SEASONS = {"rain": range(2001, 2027), "prelim": range(2016, 2027), "soil": range(2001, 2028),
           "heat": range(2001, 2027)}
PROBE_SEASON, PROBE_REGION = 2022, "Sul e Centro-Oeste"
HEAT_K = 307.15


def days(start, n):
    return [start + dt.timedelta(days=i) for i in range(n)]


def pentads(first, last):
    """CHIRPS pentads (1–5, 6–10, 11–15, 16–20, 21–25, 26–end of month) from first to last month."""
    out, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
        for a, b in ((1, 6), (6, 11), (11, 16), (16, 21), (21, 26), (26, None)):
            out.append((dt.date(y, m, a), dt.date(y, m, b) if b else nxt))
        y, m = nxt.year, nxt.month
    return out


def iso(d):
    return d.isoformat() if isinstance(d, dt.datetime) else d.strftime("%Y-%m-%d")


def coffee_weight(project, mask_year, target_proj, max_pixels):
    mesos = sorted(meso_table().meso_code.unique())
    assets = [ee.Image(f"projects/{project}/assets/w1_weights_meso_{m}") for m in mesos]
    modis = assets[0].select("w_1998").projection()
    w = (ee.ImageCollection([a.select(f"w_{mask_year}") for a in assets]).mosaic()
         .unmask(0).setDefaultProjection(modis))
    return w.reduceResolution(ee.Reducer.mean(), maxPixels=max_pixels).reproject(target_proj).rename("w")


def stack(product, season, project):
    s1 = season - 1
    if product == "rain":
        col = ee.ImageCollection(CHIRPS).select("precipitation")
        bands = [col.filterDate(iso(d), iso(d + dt.timedelta(days=1))).first().rename(f"d_{d:%m%d}")
                 for d in days(dt.date(s1, 9, 1), 91)]
        bands += [col.filterDate(iso(a), iso(b)).sum().rename(f"p_{a:%m%d}")
                  for a, b in pentads(dt.date(s1, 12, 1), dt.date(season, 3, 1))]
        return ee.Image.cat(bands), ee.ImageCollection(CHIRPS).first().projection(), "chirps", 1024
    if product == "prelim":
        col = ee.ImageCollection(f"projects/{project}/assets/chc_prelim_pentad_mgsp").select("precipitation")
        bands = [col.filterDate(iso(a), iso(b)).first().rename(f"q_{a:%m%d}")
                 for a, b in pentads(dt.date(s1, 9, 1), dt.date(season, 3, 1))]
        return ee.Image.cat(bands), ee.ImageCollection(CHIRPS).first().projection(), "chirps", 1024
    col = ee.ImageCollection(ERA5)
    proj = col.first().select("temperature_2m").projection()
    if product == "soil":
        sm = (col.filterDate(f"{s1}-05-01", f"{s1}-09-01")
              .select(["volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2",
                       "volumetric_soil_water_layer_3"])
              .map(lambda i: i.expression("0.07 * b(0) + 0.21 * b(1) + 0.72 * b(2)").rename("sm"))
              .mean())
        return sm, proj, "era5", 4096
    t = col.select("temperature_2m")
    bands = []
    for d in days(dt.date(s1, 9, 1), 91):
        start = dt.datetime(d.year, d.month, d.day, 3)
        bands.append(t.filterDate(iso(start), iso(start + dt.timedelta(days=1))).max()
                     .gt(HEAT_K).rename(f"h_{d:%m%d}"))
    return ee.Image.cat(bands), proj, "era5", 4096


def table(product, project, seasons, region=None):
    munis = ee.FeatureCollection(f"projects/{project}/assets/w1_municipios_index").select(["code", "region"])
    if region:
        munis = munis.filter(ee.Filter.eq("region", region))
    out = []
    for s in seasons:
        img, proj, grid, maxpx = stack(product, s, project)
        w = coffee_weight(project, s - 2, proj, maxpx)
        red = img.multiply(w).addBands(w).reduceRegions(collection=munis, reducer=ee.Reducer.sum(),
                                                        crs=proj, scale=SCALES[grid], tileScale=4)
        out.append(red.filter(ee.Filter.gt("w", 0)).map(lambda f, s=s: f.set("season", s)))
    return ee.FeatureCollection(out).flatten(), img.bandNames()


def main():
    a = argparse.ArgumentParser()
    a.add_argument("product", choices=list(SEASONS))
    a.add_argument("--probe", action="store_true", help=f"crop {PROBE_SEASON}, {PROBE_REGION} only")
    a.add_argument("--all-regions", action="store_true", help="with --probe: every region")
    a.add_argument("--estimate", type=float, required=True, help="cost estimate in EECU-seconds")
    a.add_argument("--start-session", type=float, help="start a new watchdog session with this cap")
    a.add_argument("--cap", type=float, help="set the session cap to this value, keeping the spend")
    args = a.parse_args()
    project = init()
    if args.start_session:
        wd.set_session_cap("w2_inputs", args.start_session)
    elif args.cap:
        led = wd._ledger()
        led["cap"] = args.cap
        wd.LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")
        wd._log(f"session cap {args.cap:,.0f} EECU-s")
    seasons = [PROBE_SEASON] if args.probe else list(SEASONS[args.product])
    fc, names = table(args.product, project, seasons,
                      PROBE_REGION if args.probe and not args.all_regions else None)
    band_names = names.getInfo()  # interactive: metadata (band names)
    name = f"w2_{args.product}_muni" + ("_probe" if args.probe else "") + ("_all" if args.all_regions else "")
    t0 = time.time()
    df, used = wd.export_table_watched(fc, name, ["code", "region", "season", "w"] + band_names,
                                       args.estimate, prefix="w2")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles").mkdir(parents=True, exist_ok=True)
    (WEEK0 / "profiles" / f"{name}_{stamp}.txt").write_text(
        f"batch export {name}: {used:,.0f} EECU-seconds (batch), {0 if df is None else len(df)} rows, "
        f"{len(seasons)} season(s), {time.time() - t0:.0f} s wall\n", encoding="utf-8")
    if df is None:
        raise SystemExit(f"{name}: not completed ({used:,.0f} EECU-seconds)")
    df.to_csv(ROOT / "data" / "derived" / f"{name}.csv", index=False)
    print(f"{name}: {len(df):,} rows, {df.code.nunique()} municipalities, {len(seasons)} season(s), "
          f"{used:,.0f} EECU-seconds")


if __name__ == "__main__":
    main()
