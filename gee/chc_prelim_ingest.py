"""Ingest the clipped CHC prelim files into Earth Engine (Amendment 9, revised).

Each GeoTIFF from data/raw/chc_prelim/ (made by chc_prelim_fetch.py) is uploaded to a Cloud
Storage bucket in the Earth Engine project, then ingested into one of two private collections:

    projects/<EE_PROJECT>/assets/chc_prelim_pentad_mgsp
    projects/<EE_PROJECT>/assets/chc_prelim_daily_mgsp

Configuration, in .env: EE_PROJECT and GCS_BUCKET. The bucket name is a configuration value,
not a secret, and is documented in the README. The bucket is created if missing (private, uniform
access, public access prevented), which needs billing enabled on the project.

Rerunnable: an object already in the bucket with the same SHA-256 is not uploaded again, and an
image already in a collection is not ingested again. --from-scratch deletes every image in both
collections first and needs --yes as well; it never runs by default.

Run:    .venv/Scripts/python gee/chc_prelim_ingest.py [--dry-run] [--from-scratch --yes]
"""
import argparse
import datetime as dt
import hashlib
from pathlib import Path

import ee
import rasterio
from google.cloud import storage

from common import ROOT, init, setting

SOURCE = ROOT / "data" / "raw" / "chc_prelim"
BUCKET_LOCATION = "US-CENTRAL1"
NODATA = -9999.0


def end_of(kind, start):
    if kind == "daily":
        return start + dt.timedelta(days=1)
    if start.day < 26:  # pentads start on days 1, 6, 11, 16, 21 and 26; the sixth runs to month end
        return start + dt.timedelta(days=5)
    return (start.replace(day=1) + dt.timedelta(days=32)).replace(day=1)


def image_id(kind, start):
    if kind == "daily":
        return f"d_{start:%Y_%m_%d}"
    return f"p_{start:%Y_%m}_{(start.day - 1) // 5 + 1}"


def existing_images(collection):
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


def ensure_collection(path, dry_run):
    try:
        ee.data.getAsset(path)
    except ee.EEException:
        print(f"creating collection {path}")
        if not dry_run:
            ee.data.createAsset({"type": "IMAGE_COLLECTION"}, path)


def ensure_bucket(client, name, dry_run):
    bucket = client.lookup_bucket(name)
    if bucket is not None:
        return bucket
    print(f"creating bucket gs://{name} in {BUCKET_LOCATION} (private, uniform access)")
    bucket = client.bucket(name)
    if dry_run:
        return bucket
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    bucket.iam_configuration.public_access_prevention = "enforced"
    return client.create_bucket(bucket, location=BUCKET_LOCATION)


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--dry-run", action="store_true", help="report what would happen; change nothing")
    args.add_argument("--from-scratch", action="store_true", help="delete every image in both collections first")
    args.add_argument("--yes", action="store_true", help="required with --from-scratch")
    args = args.parse_args()
    if args.from_scratch and not args.yes:
        raise SystemExit("--from-scratch deletes ingested images; add --yes to confirm.")

    project = init()
    client = storage.Client(project=project, credentials=ee.data.get_persistent_credentials())
    bucket = ensure_bucket(client, setting("GCS_BUCKET"), args.dry_run)

    files = sorted(SOURCE.glob("*/*.tif"))
    if not files:
        raise SystemExit(f"No files in {SOURCE}; run gee/chc_prelim_fetch.py first.")
    for kind in ("pentad", "daily"):
        counts = {"files": 0, "uploaded": 0, "upload skipped": 0, "ingest started": 0,
                  "already ingested": 0}
        collection = f"projects/{project}/assets/chc_prelim_{kind}_mgsp"
        ensure_collection(collection, args.dry_run)
        done = set() if args.dry_run and not _exists(collection) else existing_images(collection)
        if args.from_scratch:
            print(f"deleting {len(done)} images from {collection}")
            if not args.dry_run:
                for name in done:
                    ee.data.deleteAsset(f"{collection}/{name}")
            done = set()

        for path in (f for f in files if f.parent.name == kind):
            counts["files"] += 1
            with rasterio.open(path) as src:
                tags = src.tags()
            start = dt.date.fromisoformat(tags["start_date"])
            name = image_id(kind, start)
            if name in done:
                counts["already ingested"] += 1
                continue
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            blob = bucket.blob(f"chc_prelim/{kind}/{path.name}")
            current = bucket.get_blob(blob.name) if not args.dry_run else None
            if current is not None and (current.metadata or {}).get("sha256") == sha:
                counts["upload skipped"] += 1
            else:
                if not args.dry_run:
                    blob.metadata = {"sha256": sha}
                    blob.upload_from_filename(str(path), content_type="image/tiff")
                counts["uploaded"] += 1
            manifest = {
                "name": f"{collection}/{name}",
                "tilesets": [{"sources": [{"uris": [f"gs://{bucket.name}/{blob.name}"]}]}],
                "bands": [{"id": "precipitation", "tilesetBandIndex": 0,
                           "missingData": {"values": [NODATA]}}],
                "startTime": f"{start.isoformat()}T00:00:00Z",
                "endTime": f"{end_of(kind, start).isoformat()}T00:00:00Z",
                "properties": {"kind": kind, "units": "mm", "sha256": sha,
                               "source_url": tags.get("source_url", ""),
                               "source_last_modified": tags.get("source_last_modified", ""),
                               "retrieved_utc": tags.get("retrieved_utc", "")},
            }
            if not args.dry_run:
                ee.data.startIngestion(ee.data.newTaskId()[0], manifest)
            counts["ingest started"] += 1
        print(f"{kind}: {counts}")
    print(("DRY RUN, nothing changed. " if args.dry_run else "") +
          "Ingestion tasks run in Earth Engine; check them in the Code Editor Tasks tab or with "
          "`earthengine task list`.")


def _exists(path):
    try:
        ee.data.getAsset(path)
        return True
    except ee.EEException:
        return False


if __name__ == "__main__":
    main()
