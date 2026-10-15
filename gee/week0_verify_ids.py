"""Week 0: does every ID the spec marks unverified resolve in Earth Engine, and how current is it?

Also searches the public catalog folders for the live-fallback candidates (VJ113A1, HLS), whose
Earth Engine IDs are not yet known (Amendment 25).

Run:    .venv/Scripts/python gee/week0_verify_ids.py
Writes: docs/week0/ids.csv
"""
import csv
import datetime as dt

import ee

from common import WEEK0, init

COLLECTIONS = [
    ("MODIS/061/MOD13Q1", "primary vegetation (Terra)"),
    ("MODIS/061/MYD13Q1", "drift-check reference (Aqua)"),
    ("NASA/VIIRS/002/VNP13A1", "drift-check reference (SNPP VIIRS)"),
    ("projects/climate-engine-pro/assets/ce-chirps-prelim-pentad", "CHIRPS-prelim, community catalog"),
    ("UCSB-CHG/CHIRPS/DAILY", "CHIRPS final"),
    ("ECMWF/ERA5_LAND/HOURLY", "heat days, soil moisture"),
    ("COPERNICUS/DEM/GLO30_2024_1", "elevation fallback"),
    ("NASA/HLS/HLSS30/v002", "fallback candidate (b), HLS Sentinel-2"),
    ("NASA/HLS/HLSL30/v002", "HLS Landsat, coverage as information only"),
]
# Very large collections are queried inside date windows near each end, at a point in Sul de
# Minas, instead of sorting the whole collection (which stalls on ERA5-Land's ~670,000 images).
WINDOWS = {
    "ECMWF/ERA5_LAND/HOURLY": (("1950-01-01", "1950-01-03"), ("2026-09-01", "2026-10-14")),
    "NASA/HLS/HLSS30/v002": (("2015-06-01", "2016-06-01"), ("2026-09-01", "2026-10-14")),
    "NASA/HLS/HLSL30/v002": (("2013-03-01", "2014-03-01"), ("2026-09-01", "2026-10-14")),
}
PROBE_LONLAT = (-45.43, -21.55)  # Varginha, Sul de Minas
# VJ113A1 IDs probed directly, as an independent check on the folder search.
VJ113A1_PROBES = ["NASA/VIIRS/002/VJ113A1", "NASA/VIIRS/001/VJ113A1", "NOAA/VIIRS/002/VJ113A1"]
IMAGES = [
    ("USGS/SRTMGL1_003", "elevation"),
]
# Public catalog folders searched for the fallback candidates, and the name fragments that count.
SEARCH = {
    "projects/earthengine-public/assets/NASA/VIIRS/002": ("VJ1", "VJ2"),
}


def _date(ms):
    # Epoch arithmetic rather than fromtimestamp, which fails on Windows before 1970 (ERA5-Land).
    if ms is None:
        return ""
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    return (epoch + dt.timedelta(milliseconds=ms)).date().isoformat()


def check_collection(asset_id, role):
    row = {"id": asset_id, "role": role, "type": "ImageCollection"}
    try:
        col = ee.ImageCollection(asset_id)
        if asset_id in WINDOWS:
            (f0, f1), (l0, l1) = WINDOWS[asset_id]
            point = ee.Geometry.Point(*PROBE_LONLAT)
            first = col.filterBounds(point).filterDate(f0, f1).limit(1, "system:time_start", True).first()
            last = col.filterBounds(point).filterDate(l0, l1).limit(1, "system:time_start", False).first()
            n = ee.Number(-1)  # not counted for very large collections
        else:
            first = col.limit(1, "system:time_start", True).first()
            last = col.limit(1, "system:time_start", False).first()
            n = col.size()
        info = ee.Dictionary({
            "first": first.get("system:time_start"),
            "last": last.get("system:time_start"),
            "bands": last.bandNames(),
            "n": n,
        }).getInfo()  # interactive: metadata (dates, band names, image count)
        row.update(resolves="yes", first=_date(info["first"]), last=_date(info["last"]),
                   bands=" ".join(info["bands"]), n="" if info["n"] < 0 else info["n"],
                   note="ends found inside date windows at a Sul de Minas point" if asset_id in WINDOWS else "")
    except Exception as e:  # report the failure as a finding, never hide it
        row.update(resolves="NO", error=str(e)[:200])
    return row


def check_image(asset_id, role):
    row = {"id": asset_id, "role": role, "type": "Image"}
    try:
        bands = ee.Image(asset_id).bandNames().getInfo()  # interactive: metadata
        row.update(resolves="yes", bands=" ".join(bands))
    except Exception as e:
        row.update(resolves="NO", error=str(e)[:200])
    return row


def search_folder(parent, fragments):
    rows = []
    try:
        assets = ee.data.listAssets({"parent": parent}).get("assets", [])
    except Exception as e:
        return [{"id": parent, "role": "catalog search", "resolves": "NO", "error": str(e)[:200]}]
    hits = [a for a in assets if any(f in a["id"].split("/")[-1] for f in fragments)]
    if not hits:
        rows.append({"id": parent, "role": "catalog search", "resolves": "no match",
                     "error": "searched for " + ", ".join(fragments)})
    for a in hits:
        asset_id = a["id"].replace("projects/earthengine-public/assets/", "")
        if a.get("type") == "IMAGE_COLLECTION":
            rows.append(check_collection(asset_id, "fallback candidate (found by search)"))
        else:
            rows.append({"id": asset_id, "role": "fallback candidate (found by search)",
                         "type": a.get("type", ""), "resolves": "listed"})
    return rows


def main():
    init()
    rows = [check_collection(i, r) for i, r in COLLECTIONS]
    rows += [check_image(i, r) for i, r in IMAGES]
    for parent, fragments in SEARCH.items():
        rows += search_folder(parent, fragments)
    for cand in VJ113A1_PROBES:
        try:
            ee.ImageCollection(cand).limit(1).size().getInfo()  # interactive: metadata
            rows.append({"id": cand, "role": "VJ113A1 direct probe", "resolves": "yes"})
        except Exception as e:
            rows.append({"id": cand, "role": "VJ113A1 direct probe", "resolves": "NO", "error": str(e)[:120]})

    fields = ["id", "role", "type", "resolves", "first", "last", "n", "bands", "note", "error"]
    out = WEEK0 / "ids.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    for r in rows:
        print(f"{r.get('resolves', ''):9} {r['id']:62} {r.get('first', ''):10} {r.get('last', ''):10} "
              f"{r.get('error', '')}")
    print(f"\n{len(rows)} rows written to {out}")


if __name__ == "__main__":
    main()
