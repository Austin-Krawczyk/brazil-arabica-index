"""Which night a BDMEP conventional daily minimum belongs to: a check against co-located automatic
stations (owner request 2026-10-14, before prereg-2).

The provisional rule (owner, 2026-10-14): the conventional minimum is read at 12 UTC and covers
the preceding 24 hours, so a minimum dated D belongs to the night ending the morning of D.

For each co-located pair, every date D where both stations report is compared three ways. The
conventional minimum dated D is set against the automatic station's minimum over:
  rule       the 24 hours ending 12 UTC on D (hourly values stamped 13 UTC D-1 to 12 UTC D)
  following  the 24 hours ending 12 UTC on D+1
  calendar   the UTC calendar day D (stamped 01 UTC D to 00 UTC D+1)
An automatic window counts only if all 24 hourly values are present. All months are used, not
only June-August. Only agreement statistics are written (count, mean absolute difference, median
difference, share within 0.5 and 1.0 degrees); no temperature or frost night is reported.

Run:    .venv/Scripts/python gee/bdmep_night_check.py <path to BDMEP zip>
Writes: docs/week0/bdmep_night_check.csv
"""
import re
import sys
import zipfile

import numpy as np
import pandas as pd

from bdmep_completeness import read_station
from common import ROOT, WEEK0
from inmet_completeness import RAW, TMIN_COL, YEARS, station_file

PAIRS = [("83630", "A708", "Franca"), ("83692", "A518", "Juiz de Fora"), ("83579", "A505", "Araxá"),
         ("83592", "A554", "Caratinga"), ("83642", "A510", "Viçosa"), ("83726", "A711", "São Carlos")]


def automatic_hourly(code):
    parts = []
    for year in YEARS:
        with zipfile.ZipFile(RAW / f"{year}.zip") as z:
            name = station_file(z.namelist(), code)
            if name is None:
                continue
            lines = z.read(name).decode("latin-1").splitlines()[9:]
        rows = [l.split(";") for l in lines if l.strip()]
        date = pd.Series([r[0] for r in rows]).str.replace("/", "-")
        hour = pd.Series([r[1] for r in rows]).str.replace(" UTC", "").str.replace(":", "").str.zfill(4).str[:2]
        ts = pd.to_datetime(date + " " + hour, format="%Y-%m-%d %H", errors="coerce")
        tmin = pd.to_numeric(pd.Series([r[TMIN_COL] if len(r) > TMIN_COL else "" for r in rows])
                             .str.replace(",", "."), errors="coerce")
        tmin[tmin <= -9999] = np.nan
        parts.append(pd.Series(tmin.values, index=ts))
    s = pd.concat(parts)
    s = s[~s.index.isna()]
    return s[~s.index.duplicated()].sort_index()


def window_min(hourly, ends):
    """Minimum over the 24 hourly values stamped (end - 23 h) .. end, if all 24 are present."""
    full = hourly.reindex(pd.date_range(hourly.index.min().floor("D"), hourly.index.max().ceil("D"), freq="h"))
    roll_min = full.rolling(24, min_periods=24).min()
    return roll_min.reindex(ends).values


def stats(diff):
    d = diff[~np.isnan(diff)]
    return dict(n=len(d), mean_abs_diff=round(float(np.mean(np.abs(d))), 3) if len(d) else None,
                median_diff=round(float(np.median(d)), 3) if len(d) else None,
                share_within_0_5=round(float(np.mean(np.abs(d) <= 0.5)), 3) if len(d) else None,
                share_within_1_0=round(float(np.mean(np.abs(d) <= 1.0)), 3) if len(d) else None)


def main(zpath):
    z = zipfile.ZipFile(zpath)
    names = {re.search(r"dados_(\d+)_D_", n).group(1): n for n in z.namelist() if n.endswith(".csv")}
    out = []
    for conv_code, auto_code, town in PAIRS:
        _, conv, _, _ = read_station(z.read(names[conv_code]))
        conv = conv.dropna()
        hourly = automatic_hourly(auto_code)
        days = conv.index
        alignments = {
            "rule": days + pd.Timedelta(hours=12),
            "following": days + pd.Timedelta(days=1, hours=12),
            "calendar": days + pd.Timedelta(days=1),
        }
        for label, ends in alignments.items():
            auto = window_min(hourly, ends)
            out.append(dict(town=town, conventional=conv_code, automatic=auto_code, alignment=label,
                            **stats(conv.values - auto)))
    df = pd.DataFrame(out)
    df.to_csv(WEEK0 / "bdmep_night_check.csv", index=False)
    return df


if __name__ == "__main__":
    print(main(sys.argv[1]).to_string(index=False))
