"""Freeze the W2 inputs (owner, 2026-10-15: the backtest runs only after every input is frozen and
checksummed). Writes one row per file the backtest reads: path, rows, bytes, SHA-256, whether it is
committed or gitignored (regenerable by the named script), and the code commit at the freeze.

Run:    .venv/Scripts/python gee/w2_manifest.py
Writes: data/derived/w2_inputs_manifest.csv
"""
import glob
import hashlib
import subprocess

import pandas as pd

from common import ROOT

FILES = [
    ("data/derived/w1_series_muni_*.csv", "EVI/NDVI per municipality and composite", "gee/w1_run.py"),
    ("data/derived/w2_rain_muni.csv", "CHIRPS final per municipality, crops 2001-2026", "gee/w2_exports.py rain"),
    ("data/derived/w2_prelim_muni.csv", "CHC prelim pentads per municipality, crops 2016-2026", "gee/w2_exports.py prelim"),
    ("data/derived/w2_soil_muni.csv", "ERA5-Land root-zone soil moisture, crops 2001-2027", "gee/w2_exports.py soil"),
    ("data/derived/w2_heat_muni.csv", "ERA5-Land days above 34 C, crops 2001-2026", "gee/w2_exports.py heat"),
    ("data/derived/w2_frost_station_season.csv", "frost per station and window", "gee/w2_frost.py"),
    ("data/derived/w2_frost_region_season.csv", "frost per region and crop", "gee/w2_frost.py"),
    ("data/derived/w2_season_inputs.csv", "season inputs per region, crop and vintage (full sample)", "gee/w2_season_inputs.py"),
    ("data/derived/conab_regional.csv", "Conab target series", "gee/conab_extract.py"),
    ("data/derived/frozen_mask_pixels.csv", "frozen mask pixel table", "gee/frozen_mask_pixels.py"),
    ("docs/week0/members_by_season.csv", "members per season (Amendment 35)", "gee/w1_reading_coverage.py"),
    ("docs/week0/station_set_frozen.csv", "frost station set", "gee/station_set_frozen.py"),
    ("docs/week0/station_coverage_frozen.csv", "frost observed coverage", "gee/station_set_frozen.py"),
    ("docs/week0/w1_filter_stable_membership.csv", "stable filter decisions (Amendment 16d)", "gee/w1_filter_stable.py"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    rows = []
    for pattern, what, made_by in FILES:
        for p in sorted(glob.glob(str(ROOT / pattern))):
            rel = p.replace(str(ROOT) + "\\", "").replace("\\", "/")
            ignored = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT).returncode == 0
            with open(p, encoding="utf-8") as f:
                n = sum(1 for _ in f) - 1
            rows.append(dict(path=rel, contents=what, made_by=made_by, rows=n, bytes=(ROOT / rel).stat().st_size,
                             sha256=sha256(p), in_git="no (gitignored; regenerate)" if ignored else "yes",
                             code_commit_at_freeze=commit))
    m = pd.DataFrame(rows)
    m.to_csv(ROOT / "data" / "derived" / "w2_inputs_manifest.csv", index=False)
    return m


if __name__ == "__main__":
    m = main()
    print(m[["path", "rows", "bytes", "in_git", "sha256"]].to_string(index=False))
