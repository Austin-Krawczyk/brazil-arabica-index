"""Download CHC's own CHIRPS-prelim files, clipped to the MG/SP window (Amendment 9, revised).

Scope (owner decision, 2026-10-13):
  pentad  every pentad from 2015-01 to the latest published
  daily   September-November of 2015-2025, and 1 May 2026 onward (the "fixed" daily prelim, which
          sums exactly to the pentad totals)

Pentads up to 2021.10.6 are read from CHC's cloud-optimised GeoTIFFs and later ones from its plain
GeoTIFFs, in both cases reading only the window. Daily files are gzipped, so each is downloaded
whole, clipped in memory and discarded.

Rerunnable: files already on disk are skipped, never rewritten (§9: data/raw is never modified).
The manifest is rebuilt from the files' own tags on every run.

Polite by design: one file at a time with a pause between files, and the run stops on the first
403 or 429 instead of continuing. The first run used four parallel workers and CHC's server
blocked this machine after about 120 files (2026-10-13).

Run:    .venv/Scripts/python gee/chc_prelim_fetch.py
Writes: data/raw/chc_prelim/{pentad,daily}/*.tif (gitignored), data/raw/chc_prelim/manifest.csv
"""
import csv
import datetime as dt
import gzip
import hashlib
import re
import time
from pathlib import Path

import rasterio
import requests
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "chc_prelim"
BASE = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/"
BOX = (-53.5, -25.5, -39.5, -14.0)  # west, south, east, north: MG + SP with a 0.25-degree margin
NODATA = -9999.0  # present in the source files but not declared in their metadata
LAST_COG = (2021, 10, 6)  # CHC's cogs/ directory stops at pentad 2021.10.6
DAILY_YEARS = range(2015, 2026)
DAILY_MONTHS = (9, 10, 11)
LIVE_DAILY_FROM = dt.date(2026, 5, 1)
GDAL_ENV = dict(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.cog", GDAL_HTTP_MAX_RETRY="2",
                GDAL_HTTP_RETRY_DELAY="30")
PAUSE_SECONDS = 3.0  # between files
HEADERS = {"User-Agent": "brazil-arabica-index (github.com/Austin-Krawczyk/brazil-arabica-index)"}


class Refused(Exception):
    """The server answered 403 or 429: stop the whole run and try again later."""

def listing(url, pattern):
    r = requests.get(url, timeout=120, headers=HEADERS)
    if r.status_code in (403, 429):
        raise Refused(f"{r.status_code} on {url}")
    r.raise_for_status()
    return sorted(set(re.findall(pattern, r.text)))


def pentad_jobs():
    published = listing(BASE + "global_pentad/tifs/", r"chirps-v2\.0\.(\d{4})\.(\d{2})\.(\d)\.tif\"")
    jobs = []
    for y, m, p in published:
        y, m, p = int(y), int(m), int(p)
        if y < 2015:
            continue
        name = f"chirps-v2.0.{y}.{m:02d}.{p}"
        url = (BASE + f"global_pentad/cogs/{name}.cog" if (y, m, p) <= LAST_COG
               else BASE + f"global_pentad/tifs/{name}.tif")
        start = dt.date(y, m, 1 + 5 * (p - 1))
        jobs.append(("pentad", start, url, OUT / "pentad" / f"{name}.tif"))
    return jobs


def daily_jobs():
    days = [dt.date(y, m, 1) + dt.timedelta(days=i)
            for y in DAILY_YEARS for m in DAILY_MONTHS for i in range(31)]
    days = [d for d in days if d.month in DAILY_MONTHS]
    live = [hit for year in range(LIVE_DAILY_FROM.year, dt.date.today().year + 1)
            for hit in listing(BASE + f"global_daily/fixed/tifs/{year}/",
                               r"chirps-v2\.0\.(\d{4})\.(\d{2})\.(\d{2})\.tif\.gz")]
    days += [d for d in (dt.date(int(y), int(m), int(dd)) for y, m, dd in live) if d >= LIVE_DAILY_FROM]
    jobs = []
    for d in sorted(set(days)):
        name = f"chirps-v2.0.{d:%Y.%m.%d}"
        url = BASE + f"global_daily/fixed/tifs/{d.year}/{name}.tif.gz"
        jobs.append(("daily", d, url, OUT / "daily" / f"{name}.tif"))
    return jobs


def write(out, array, transform, tags):
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part")
    profile = dict(driver="GTiff", height=array.shape[0], width=array.shape[1], count=1,
                   dtype="float32", crs="EPSG:4326", transform=transform, nodata=NODATA,
                   compress="lzw")
    with rasterio.open(tmp, "w", **profile) as dst:
        dst.write(array, 1)
        dst.update_tags(**tags)
    tmp.replace(out)  # a file only appears once complete, so a rerun never trusts a partial write


def fetch(job):
    kind, start, url, out = job
    if out.exists():
        return "skipped"
    head = requests.head(url, timeout=60, headers=HEADERS)
    if head.status_code in (403, 429):
        raise Refused(f"{head.status_code} on {url}")
    if head.status_code != 200:
        return f"missing ({head.status_code})"
    tags = dict(source_url=url, source_last_modified=head.headers.get("Last-Modified", ""),
                retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                kind=kind, start_date=start.isoformat(), units="mm",
                window_wsen=",".join(str(v) for v in BOX))
    if kind == "pentad":
        with rasterio.Env(**GDAL_ENV), rasterio.open("/vsicurl/" + url) as src:
            w = from_bounds(*BOX, transform=src.transform).round_offsets().round_lengths()
            write(out, src.read(1, window=w), src.window_transform(w), tags)
    else:
        r = requests.get(url, timeout=300, headers=HEADERS)
        if r.status_code in (403, 429):
            raise Refused(f"{r.status_code} on {url}")
        r.raise_for_status()
        raw = gzip.decompress(r.content)
        with rasterio.MemoryFile(raw) as mf, mf.open() as src:
            w = from_bounds(*BOX, transform=src.transform).round_offsets().round_lengths()
            write(out, src.read(1, window=w), src.window_transform(w), tags)
    return "fetched"


def rebuild_manifest():
    rows = []
    for path in sorted(OUT.glob("*/*.tif")):
        with rasterio.open(path) as src:
            tags = src.tags()
        rows.append(dict(kind=tags.get("kind"), start_date=tags.get("start_date"), file=path.name,
                         source_url=tags.get("source_url"),
                         source_last_modified=tags.get("source_last_modified"),
                         retrieved_utc=tags.get("retrieved_utc"),
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         bytes=path.stat().st_size))
    with (OUT / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["file"])
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    jobs = pentad_jobs() + daily_jobs()
    print(f"{sum(j[0] == 'pentad' for j in jobs)} pentads and {sum(j[0] == 'daily' for j in jobs)} "
          f"days in scope")
    counts = {}
    try:
        for i, job in enumerate(jobs, 1):
            kind, start, url, _ = job
            try:
                status = fetch(job)
            except Refused:
                raise
            except Exception as e:  # report and carry on; a rerun picks the file up
                status = "failed"
                print(f"  {kind} {start}: FAILED {type(e).__name__}: {str(e)[:100]}")
            counts[status] = counts.get(status, 0) + 1
            if status.startswith("missing"):
                print(f"  {kind} {start}: {status} at {url}")
            if i % 100 == 0:
                print(f"  {i}/{len(jobs)} done: {counts}")
            if status != "skipped":
                time.sleep(PAUSE_SECONDS)
    except Refused as e:
        print(f"\nSTOPPED: the server refused a request ({e}). Nothing more was requested. "
              f"Rerun later; files already saved are kept.")
    rows = rebuild_manifest()
    print(f"\nFinished: {counts}. Manifest lists {len(rows)} files.")


if __name__ == "__main__":
    main()
