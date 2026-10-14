"""INMET station completeness for §5 step 4 (Amendment 17): June-August 2008-2026.

A station's record is complete when, in every June-August window from 2008 to 2026, at least 95% of
hourly observations of "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)" are present and no gap exceeds
48 consecutive hours. Windows are taken in UTC (INMET timestamps are UTC): 1 June 00:00 to 31
August 23:00, 2,208 hours. A missing row, an empty cell and -9999 all count as missing.

Reads the annual archives in data/raw/inmet/ without extracting them. The 2026 archive holds two
cumulative snapshots per station (to 31 August and to 30 September); the later one is used.

Run:    .venv/Scripts/python gee/inmet_completeness.py data/derived/_tmp_station_candidates.csv
Writes: docs/week0/inmet_completeness.csv (one row per station and year)
"""
import io
import re
import sys
import zipfile

import numpy as np
import pandas as pd

from common import ROOT, WEEK0

RAW = ROOT / "data" / "raw" / "inmet"
YEARS = range(2008, 2027)
TMIN_COL = 10
HOURS = 92 * 24
MIN_SHARE, MAX_GAP = 0.95, 48


def station_file(names, code):
    hits = [n for n in names if re.search(rf"_{code}_", n) and n.upper().endswith(".CSV")]
    if not hits:
        return None
    # the latest end date wins (2026 holds cumulative snapshots)
    return max(hits, key=lambda n: re.search(r"_A_(\d\d)-(\d\d)-(\d{4})", n).group(3, 2, 1))


def window_stats(raw, year):
    lines = raw.decode("latin-1").splitlines()[9:]
    rows = [l.split(";") for l in lines if l.strip()]
    if not rows:
        return 0, HOURS
    date = pd.Series([r[0] for r in rows]).str.replace("/", "-")
    hour = pd.Series([r[1] for r in rows]).str.replace(" UTC", "").str.replace(":", "").str.zfill(4).str[:2]
    ts = pd.to_datetime(date + " " + hour, format="%Y-%m-%d %H", errors="coerce")
    tmin = pd.to_numeric(pd.Series([r[TMIN_COL] if len(r) > TMIN_COL else "" for r in rows])
                         .str.replace(",", "."), errors="coerce")
    tmin[tmin <= -9999] = np.nan
    s = pd.Series(tmin.values, index=ts).groupby(level=0).first()
    window = pd.date_range(f"{year}-06-01 00:00", f"{year}-08-31 23:00", freq="h")
    present = s.reindex(window).notna().values
    valid = int(present.sum())
    gap = run = 0
    for ok in present:
        run = 0 if ok else run + 1
        gap = max(gap, run)
    return valid, gap


def main(candidates_csv):
    cand = pd.read_csv(candidates_csv)
    out = []
    for year in YEARS:
        with zipfile.ZipFile(RAW / f"{year}.zip") as z:
            names = z.namelist()
            for code in cand["code"]:
                f = station_file(names, code)
                if f is None:
                    out.append(dict(code=code, year=year, file="", valid_hours=0, share=0.0, max_gap_h=HOURS))
                    continue
                valid, gap = window_stats(z.read(f), year)
                out.append(dict(code=code, year=year, file=f, valid_hours=valid,
                                share=round(valid / HOURS, 4), max_gap_h=gap))
        print(f"  {year} done", flush=True)
    df = pd.DataFrame(out)
    df["window_ok"] = (df["share"] >= MIN_SHARE) & (df["max_gap_h"] <= MAX_GAP)
    df.to_csv(WEEK0 / "inmet_completeness.csv", index=False)
    summary = df.groupby("code").agg(windows_ok=("window_ok", "sum"), min_share=("share", "min"),
                                     max_gap_h=("max_gap_h", "max"))
    summary["complete"] = summary["windows_ok"] == len(YEARS)
    print(f"{int(summary['complete'].sum())} of {len(summary)} candidate stations complete in all "
          f"{len(YEARS)} June-August windows")
    return summary


if __name__ == "__main__":
    main(sys.argv[1])
