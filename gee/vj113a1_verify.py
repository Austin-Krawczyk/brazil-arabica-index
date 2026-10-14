"""Verify the VJ113A1 ingestion: tasks finished, collection loads, values match the source files.

Independent checks against the unchanged AppEEARS GeoTIFFs in data/raw/vj113a1/:
  - 15 valid pixels: 5 random composites x 3 bands x 1 random valid pixel;
  - 15 fill pixels (same composites and bands) must be masked in Earth Engine.

Run:    .venv/Scripts/python gee/vj113a1_verify.py [--wait]
Writes: docs/week0/vj113a1_verify.txt
"""
import argparse
import datetime as dt
import random
import time

import ee
import rasterio
from rasterio.warp import transform

from common import WEEK0, init
from vj113a1_ingest import composites

SEED = 20261014


def wait_for_tasks():
    while True:
        ops = [o for o in ee.data.listOperations()
               if o.get("metadata", {}).get("type") == "INGEST_IMAGE"
               and "vj113a1_mgsp" in o.get("metadata", {}).get("description", "")]
        states = {}
        for o in ops:
            s = o["metadata"].get("state", "?")
            states[s] = states.get(s, 0) + 1
        print(f"ingestion tasks: {states}", flush=True)
        if not any(k in states for k in ("PENDING", "RUNNING")):
            return ops
        time.sleep(60)


def value_at(img, band, lon, lat):
    return (img.select(band).reduceRegion(ee.Reducer.first(), ee.Geometry.Point(lon, lat),
                                          crs=img.select(band).projection(), scale=463.3127)
            .get(band).getInfo())


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--wait", action="store_true", help="wait for ingestion tasks first")
    args = a.parse_args()
    project = init()
    lines = []
    say = lambda s: (print(s), lines.append(s))
    if args.wait:
        ops = wait_for_tasks()
        failed = [o for o in ops if o["metadata"].get("state") == "FAILED"]
        say(f"tasks: {len(ops)} found, {len(failed)} failed")
        for o in failed[:5]:
            say(f"  FAILED {o['metadata'].get('description')}: {o.get('error', {}).get('message', '')[:150]}")
    col = ee.ImageCollection(f"projects/{project}/assets/vj113a1_mgsp")
    info = ee.Dictionary({"n": col.size(), "first": col.aggregate_min("system:time_start"),
                          "last": col.aggregate_max("system:time_start"),
                          "bands": col.first().bandNames()}).getInfo()
    day = lambda ms: (dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=ms)).date()
    say(f"collection loads: {info['n']} images, {day(info['first'])} to {day(info['last'])}, "
        f"bands {info['bands']}")

    random.seed(SEED)
    comps = composites()
    picks = random.sample(sorted(comps), 5)
    ok = bad = masked_ok = masked_bad = 0
    for doy in picks:
        img = ee.Image(f"projects/{project}/assets/vj113a1_mgsp/c_{doy}")
        for band, path in comps[doy].items():
            with rasterio.open(path) as src:
                arr = src.read(1)
                valid = [(r, c) for r, c in zip(*((arr != src.nodata).nonzero()))]
                fill = [(r, c) for r, c in zip(*((arr == src.nodata).nonzero()))]
                for r, c in random.sample(valid, 1):
                    x, y = src.xy(r, c)
                    lon, lat = transform(src.crs, "EPSG:4326", [x], [y])
                    v = value_at(img, band, lon[0], lat[0])
                    match = v is not None and abs(v - float(arr[r, c])) < 0.5
                    ok += match
                    bad += not match
                    say(f"  {doy} {band} ({lon[0]:.3f},{lat[0]:.3f}): file {arr[r, c]} | EE {v}")
                for r, c in random.sample(fill, min(1, len(fill))):
                    x, y = src.xy(r, c)
                    lon, lat = transform(src.crs, "EPSG:4326", [x], [y])
                    v = value_at(img, band, lon[0], lat[0])
                    masked_ok += v is None
                    masked_bad += v is not None
    say(f"value check: {ok} of {ok + bad} match; fill cells masked: {masked_ok} of {masked_ok + masked_bad}")
    (WEEK0 / "vj113a1_verify.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
