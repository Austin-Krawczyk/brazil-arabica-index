"""Verify a CHC prelim ingestion batch: tasks finished, and values match the source files.

Takes the list written by `chc_prelim_ingest.py --limit N` (kind, image name, source file per
line). For every image in it: 3 random valid pixels must match the local GeoTIFF (float32 mm,
tolerance 0.001), and 1 random fill pixel (-9999) must be masked in Earth Engine.

Run:    .venv/Scripts/python gee/chc_prelim_verify.py docs/week0/chc_ingest_started_<utc>.txt [--wait]
Writes: docs/week0/chc_verify_<utc>.txt
"""
import argparse
import datetime as dt
import random
import time

import ee
import numpy as np
import rasterio

from common import ROOT, WEEK0, init

SEED = 20261014
VALID_PER_IMAGE = 3


def wait_for(names):
    while True:
        states = {}
        for o in ee.data.listOperations():
            m = o.get("metadata", {})
            if m.get("type") == "INGEST_IMAGE" and any(f"/{n}\"" in m.get("description", "") for n in names):
                states[m.get("state")] = states.get(m.get("state"), 0) + 1
        print(f"ingestion tasks: {states}", flush=True)
        if states and not any(k in states for k in ("PENDING", "RUNNING")):
            return states
        time.sleep(30)


def value_at(img, lon, lat):
    return (img.reduceRegion(ee.Reducer.first(), ee.Geometry.Point(lon, lat), crs="EPSG:4326",
                             scale=5565.97).get("precipitation").getInfo())


def main():
    a = argparse.ArgumentParser()
    a.add_argument("started")
    a.add_argument("--wait", action="store_true")
    args = a.parse_args()
    project = init()
    entries = [l.split("\t") for l in open(args.started, encoding="utf-8").read().splitlines() if l]
    lines = []
    say = lambda s: (print(s), lines.append(s))
    if args.wait:
        say(f"tasks: {wait_for([n for _, n, _ in entries])}")
    random.seed(SEED)
    ok = bad = masked_ok = masked_bad = 0
    for kind, name, rel in entries:
        img = ee.Image(f"projects/{project}/assets/chc_prelim_{kind}_mgsp/{name}").select("precipitation")
        with rasterio.open(ROOT / rel) as src:
            arr = src.read(1)
            valid = list(zip(*np.nonzero(arr != src.nodata if src.nodata is not None else arr != -9999.0)))
            fill = list(zip(*np.nonzero(arr == -9999.0)))
            for r, c in random.sample(valid, VALID_PER_IMAGE):
                lon, lat = src.xy(r, c)
                v = value_at(img, lon, lat)
                match = v is not None and abs(v - float(arr[r, c])) < 1e-3
                ok += match
                bad += not match
                say(f"  {kind} {name} ({lon:.3f},{lat:.3f}): file {arr[r, c]:.3f} | EE {v}")
            for r, c in random.sample(fill, min(1, len(fill))):
                lon, lat = src.xy(r, c)
                v = value_at(img, lon, lat)
                masked_ok += v is None
                masked_bad += v is not None
    say(f"value check: {ok} of {ok + bad} match; fill cells masked: {masked_ok} of {masked_ok + masked_bad}")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (WEEK0 / f"chc_verify_{stamp}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
