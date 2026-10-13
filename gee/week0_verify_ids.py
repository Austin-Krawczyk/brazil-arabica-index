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
]
IMAGES = [
    ("USGS/SRTMGL1_003", "elevation"),
]
# Public catalog folders searched for the fallback candidates, and the name fragments that count.
SEARCH = {
    "projects/earthengine-public/assets/NASA/VIIRS/002": ("VJ1", "VJ2"),
    "projects/earthengine-public/assets/NASA/HLS": ("HLS",),
}


def _date(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date().isoformat() if ms else ""


def check_collection(asset_id, role):
    row = {"id": asset_id, "role": role, "type": "ImageCollection"}
    try:
        col = ee.ImageCollection(asset_id)
        first = col.limit(1, "system:time_start", True).first()
        last = col.limit(1, "system:time_start", False).first()
        info = ee.Dictionary({
            "first": first.get("system:time_start"),
            "last": last.get("system:time_start"),
            "bands": last.bandNames(),
        }).getInfo()
        row.update(resolves="yes", first=_date(info["first"]), last=_date(info["last"]),
                   bands=" ".join(info["bands"]))
    except Exception as e:  # report the failure as a finding, never hide it
        row.update(resolves="NO", error=str(e)[:200])
    return row


def check_image(asset_id, role):
    row = {"id": asset_id, "role": role, "type": "Image"}
    try:
        bands = ee.Image(asset_id).bandNames().getInfo()
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

    fields = ["id", "role", "type", "resolves", "first", "last", "bands", "error"]
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
