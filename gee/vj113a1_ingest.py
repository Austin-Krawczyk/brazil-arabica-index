"""Ingest the VJ113A1 AppEEARS GeoTIFFs into Earth Engine (Amendments 25 revised, 30 second revision).

One image per 16-day composite, bands EVI, NDVI and pixel_reliability, each from its own AppEEARS
GeoTIFF (int16/int8 as delivered; EVI and NDVI scale 0.0001, fill -15000; pixel_reliability fill
-4), in the product's native sinusoidal grid. VI_Quality was delivered by AppEEARS without being
requested and is not ingested; it stays in data/raw/vj113a1/. Files are uploaded unchanged to the
bucket, then ingested into:

    projects/<EE_PROJECT>/assets/vj113a1_mgsp

Rerunnable: a bucket object with the same SHA-256 is not uploaded again, and a composite already in
the collection is not ingested again. No deletion option: removing assets is left to the owner.

Run:    .venv/Scripts/python gee/vj113a1_ingest.py [--dry-run] [--limit N]
"""
import argparse
import csv
import datetime as dt
import re

import ee
import rasterio
from google.cloud import storage

from common import ROOT, init, setting

SOURCE = ROOT / "data" / "raw" / "vj113a1"
LAYERS = {"EVI": "500_m_16_days_EVI", "NDVI": "500_m_16_days_NDVI",
          "pixel_reliability": "500_m_16_days_pixel_reliability"}


def composites():
    """{doy string: {band: path}} for composites with all three layers on disk."""
    by_date = {}
    for path in SOURCE.glob("*/*.tif"):
        m = re.search(r"VJ113A1\.002_(500_m_16_days_\w+?)_doy(\d{7})", path.name)
        if not m:
            continue
        for band, layer in LAYERS.items():
            if m.group(1) == layer:
                by_date.setdefault(m.group(2), {})[band] = path
    return {d: v for d, v in sorted(by_date.items()) if len(v) == len(LAYERS)}


def existing(collection):
    names, token = set(), None
    while True:
        params = {"parent": collection, "pageSize": 1000}
        if token:
            params["pageToken"] = token
        page = ee.data.listAssets(params)
        names |= {a["id"].split("/")[-1] for a in page.get("assets", [])}
        token = page.get("nextPageToken")
        if not token:
            return names


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--limit", type=int, default=None, help="ingest at most N composites (a gate run)")
    args = a.parse_args()
    project = init()
    client = storage.Client(project=project, credentials=ee.data.get_persistent_credentials())
    bucket = client.bucket(setting("GCS_BUCKET"))
    collection = f"projects/{project}/assets/vj113a1_mgsp"
    try:
        ee.data.getAsset(collection)
    except ee.EEException:
        print(f"creating collection {collection}")
        if not args.dry_run:
            ee.data.createAsset({"type": "IMAGE_COLLECTION"}, collection)
    done = set() if args.dry_run else existing(collection)
    sha = {}
    with (SOURCE / "manifest.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sha[row["file_name"].split("/")[-1]] = row["sha256"]

    todo = [(d, f) for d, f in composites().items() if f"c_{d}" not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(composites())} complete composites on disk; {len(done)} already ingested; "
          f"{len(todo)} to ingest")
    for doy, files in todo:
        start = dt.datetime.strptime(doy, "%Y%j").date()
        tilesets, bands = [], []
        for band, path in files.items():
            blob = bucket.blob(f"vj113a1/{path.name}")
            if not args.dry_run:
                current = bucket.get_blob(blob.name)
                if current is None or (current.metadata or {}).get("sha256") != sha[path.name]:
                    blob.metadata = {"sha256": sha[path.name]}
                    blob.upload_from_filename(str(path), content_type="image/tiff")
            with rasterio.open(path) as src:
                fill = src.nodata
            tilesets.append({"id": band, "sources": [{"uris": [f"gs://{bucket.name}/{blob.name}"]}]})
            bands.append({"id": band, "tilesetId": band, "tilesetBandIndex": 0,
                          "missingData": {"values": [fill]}})
        manifest = {
            "name": f"{collection}/c_{doy}",
            "tilesets": tilesets,
            "bands": bands,
            "startTime": f"{start.isoformat()}T00:00:00Z",
            "endTime": f"{(start + dt.timedelta(days=16)).isoformat()}T00:00:00Z",
            "properties": {"product": "VJ113A1.002", "composite_doy": doy, "vi_scale_factor": 0.0001,
                           "source": "NASA AppEEARS task 145e0b79-00e3-41c2-b1c8-eeea5e7e4d49",
                           **{f"sha256_{b}": sha[p.name] for b, p in files.items()}},
        }
        if not args.dry_run:
            ee.data.startIngestion(ee.data.newTaskId()[0], manifest)
    print(("DRY RUN: nothing changed. " if args.dry_run else "") + f"{len(todo)} ingestion tasks "
          f"{'would start' if args.dry_run else 'started'}.")


if __name__ == "__main__":
    main()
