"""Cost probe for W1's per-municipality reduction (Amendment 16d), using the single-band Sul coffee
weight already saved (w1_coffee_weight_sul_e_centro_oeste_mask2024). The same stack as the full
run (two mask variants × two QA candidates × EVI and NDVI, plus weights), reduced per municipality
for one calendar year of composites. Measures cost only: both mask variants use the one weight.

Batch under gee/ee_watchdog.py with a required estimate (owner rule 2026-10-15).

Run:    .venv/Scripts/python gee/w1_muni_probe.py --year 2021 --estimate E
"""
import argparse
import datetime as dt
import time

import ee

from common import WEEK0, init
from w1_modis_evi import SCALE, full_selectors
from week0_hls_test import BATCH_COSTS, export_and_fetch


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--year", type=int, default=2021)
    a.add_argument("--estimate", type=float, required=True, help="cost estimate in EECU-seconds")
    args = a.parse_args()
    project = init()
    col = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate(f"{args.year}-01-01", f"{args.year + 1}-01-01")
    proj = col.first().select("EVI").projection()
    munis = (ee.FeatureCollection(f"projects/{project}/assets/w1_municipios_index")
             .filter(ee.Filter.eq("region", "Sul e Centro-Oeste")).select(["code", "region"]))
    w0 = ee.Image(f"projects/{project}/assets/w1_coffee_weight_sul_e_centro_oeste_mask2024").select("w")
    reducer = (ee.Reducer.median().combine(ee.Reducer.mean(), sharedInputs=True)
               .combine(ee.Reducer.sum(), sharedInputs=True))

    def per_image(img):
        d = img.date()
        qa = img.select("SummaryQA")
        vi = img.select(["EVI", "NDVI"]).multiply(SCALE)
        bands = []
        for v in ("f", "p"):
            w = w0.updateMask(w0.gt(0))
            bands.append(w.rename(f"{v}_w_total"))
            for q, qmax in (("q0", 0), ("q1", 1)):
                ok = qa.gte(0).And(qa.lte(qmax))
                bands += [vi.updateMask(ok).updateMask(w).rename([f"{v}_{q}_EVI", f"{v}_{q}_NDVI"]),
                          w.updateMask(ok).rename(f"{v}_{q}_w_valid")]
        per = ee.Image.cat(bands).reduceRegions(collection=munis, reducer=reducer, crs=proj,
                                                scale=231.656, tileScale=4)
        return (per.filter(ee.Filter.gt("f_w_total_sum", 0))
                .map(lambda f: f.set("composite_start", d.format("YYYY-MM-dd"), "season", 0, "mask_year", 0)))

    t0 = time.time()
    name = f"w1_muni_probe_sul_{args.year}"
    df = export_and_fetch(ee.FeatureCollection(col.map(per_image)).flatten(), name, full_selectors(),
                          args.estimate)
    cost = BATCH_COSTS[-1][1]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / "profiles" / f"{name}_{stamp}.txt").write_text(
        f"batch export {name}: {cost:,.0f} EECU-seconds (batch_eecu_usage_seconds), {len(df)} rows, "
        f"{time.time() - t0:.0f} s wall\n", encoding="utf-8")
    print(f"{name}: {len(df)} municipality-composites, {cost:,.0f} EECU-seconds")


if __name__ == "__main__":
    main()
