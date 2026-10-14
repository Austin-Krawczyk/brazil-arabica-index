"""Download the VJ113A1 AppEEARS results (task in docs/week0/appeears_vj113a1_task.json).

One file at a time. A file already on disk with the size AppEEARS lists is skipped, so a rerun
resumes. Each file is written to a temporary name and renamed when complete. The manifest records
every file's AppEEARS file ID, size, SHA-256 and retrieval time. Files are never modified after
download (§9). The token comes from APPEEARS_TOKEN in .env and is never printed.

Run:    .venv/Scripts/python gee/vj113a1_download.py
Writes: data/raw/vj113a1/<files> (gitignored), data/raw/vj113a1/manifest.csv
"""
import csv
import datetime as dt
import hashlib
import json
import time

import requests

from common import ROOT, WEEK0, setting

API = "https://appeears.earthdatacloud.nasa.gov/api"
OUT = ROOT / "data" / "raw" / "vj113a1"


def main():
    task = json.loads((WEEK0 / "appeears_vj113a1_task.json").read_text(encoding="utf-8"))["task_id"]
    headers = {"Authorization": f"Bearer {setting('APPEEARS_TOKEN')}"}
    files = requests.get(f"{API}/bundle/{task}", headers=headers, timeout=120).json()["files"]
    print(f"{len(files)} files, {sum(f['file_size'] for f in files) / 1e9:.2f} GB in the bundle")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / "manifest.csv"
    done = {}
    if manifest.exists():
        with manifest.open(encoding="utf-8") as fh:
            done = {row["file_id"]: row for row in csv.DictReader(fh)}
    fields = ["file_id", "file_name", "bytes", "sha256", "retrieved_utc", "task_id"]
    new_file = not manifest.exists()
    with manifest.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        if new_file:
            writer.writeheader()
        for i, f in enumerate(files, 1):
            path = OUT / f["file_name"]
            if f["file_id"] in done and path.exists() and path.stat().st_size == f["file_size"]:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".part")
            for attempt in range(5):
                try:
                    with requests.get(f"{API}/bundle/{task}/{f['file_id']}", headers=headers,
                                      stream=True, timeout=300) as r:
                        r.raise_for_status()
                        h = hashlib.sha256()
                        with tmp.open("wb") as out:
                            for chunk in r.iter_content(1 << 20):
                                out.write(chunk)
                                h.update(chunk)
                    if tmp.stat().st_size != f["file_size"]:
                        raise IOError(f"size {tmp.stat().st_size} != listed {f['file_size']}")
                    break
                except (requests.RequestException, IOError) as e:
                    if attempt == 4:
                        raise
                    print(f"  {f['file_name']}: retry {attempt + 1} after {str(e)[:80]}")
                    time.sleep(30 * (attempt + 1))
            tmp.replace(path)
            writer.writerow(dict(file_id=f["file_id"], file_name=f["file_name"], bytes=f["file_size"],
                                 sha256=h.hexdigest(), task_id=task,
                                 retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")))
            fh.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(files)}")
    print("download complete")


if __name__ == "__main__":
    main()
