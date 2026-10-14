"""INMET conventional stations (BDMEP daily minima): per-season completeness and the station-set
coverage under Amendment 17c.

Completeness (Amendment 17c): a station counts in a season when at least 95% of its June-August
days (88 of 92) have a daily minimum and no gap is longer than 3 consecutive missing days. A date
with no row, an empty or "null" value, or a placeholder outside -60..60 degrees counts as missing.
Nothing here reports a temperature: values are parsed only to decide whether they are present.

Coverage (Amendment 17c): per region and season, observed coverage is the share of the region's
coffee sample inside the union of the 25 km circles of that season's qualifying stations, below
the region's elevation cut. Computed for the automatic network alone, the conventional network
alone, and both combined (overlaps counted once).

Reads the BDMEP zip without extracting it.

Run:    .venv/Scripts/python gee/bdmep_completeness.py <path to BDMEP zip>
Writes: docs/week0/bdmep_completeness.csv, docs/week0/bdmep_station_check.csv,
        docs/week0/station_coverage_17c.csv
"""
import re
import sys
import zipfile

import numpy as np
import pandas as pd

from bdmep_candidates import POINTS, within
from common import WEEK0

YEARS = range(2008, 2027)
DAYS = 92
MIN_DAYS, MAX_GAP_DAYS = int(np.ceil(0.95 * DAYS)), 3


def read_station(raw):
    lines = raw.decode("latin-1").splitlines()
    meta = dict(l.split(": ", 1) for l in lines[:9] if ": " in l)
    header = lines[10].split(";")
    assert header[0] == "Data Medicao" and header[1].startswith("TEMPERATURA MINIMA, DIARIA"), header
    rows = [l.split(";") for l in lines[11:] if l.strip()]
    dates = pd.to_datetime([r[0] for r in rows], format="%Y-%m-%d")
    tokens = pd.Series([r[1].strip() if len(r) > 1 else "" for r in rows])
    values = pd.to_numeric(tokens, errors="coerce")
    kinds = {"numeric": int(values.notna().sum()),
             "empty": int((tokens == "").sum()),
             "other_text": int((values.isna() & (tokens != "")).sum()),
             "outside_-60_60": int(((values < -60) | (values > 60)).sum())}
    values[(values < -60) | (values > 60)] = np.nan
    s = pd.Series(values.values, index=dates)
    return meta, s, kinds, int(dates.duplicated().sum())


def window(s, year):
    days = pd.date_range(f"{year}-06-01", f"{year}-08-31", freq="D")
    present = s[~s.index.duplicated()].reindex(days).notna().values
    gap = run = 0
    for ok in present:
        run = 0 if ok else run + 1
        gap = max(gap, run)
    return int(present.sum()), gap


def main(zpath):
    cand = pd.read_csv(WEEK0 / "bdmep_candidates.csv", dtype={"code": str})
    cand = cand[cand.can_count].set_index("code")
    z = zipfile.ZipFile(zpath)
    names = {re.search(r"dados_(\d+)_D_", n).group(1): n for n in z.namelist() if n.endswith(".csv")}

    checks, comp = [], []
    for code, c in cand.iterrows():
        meta, s, kinds, dups = read_station(z.read(names[code]))
        valid_dates = s.dropna().index
        checks.append(dict(
            code=code, name=c["name"], file=names[code].split("/")[-1],
            code_matches=meta.get("Codigo Estacao") == code,
            lat_matches=abs(float(meta["Latitude"]) - c.lat) < 1e-4,
            lon_matches=abs(float(meta["Longitude"]) - c.lon) < 1e-4,
            alt_matches=abs(float(meta["Altitude"]) - c.altitude) < 0.01,
            situacao=meta.get("Situacao"), data_inicial=meta.get("Data Inicial"),
            data_final=meta.get("Data Final"), list_status=c["status"], list_end=c["end"],
            rows=len(s), duplicate_dates=dups, **kinds,
            first_value=valid_dates.min().date() if len(valid_dates) else "",
            last_value=valid_dates.max().date() if len(valid_dates) else ""))
        for y in YEARS:
            valid, gap = window(s, y)
            comp.append(dict(code=code, year=y, valid_days=valid, max_gap_days=gap,
                             window_ok=(valid >= MIN_DAYS) and (gap <= MAX_GAP_DAYS)))
    checks, comp = pd.DataFrame(checks), pd.DataFrame(comp)
    checks.to_csv(WEEK0 / "bdmep_station_check.csv", index=False)
    comp.to_csv(WEEK0 / "bdmep_completeness.csv", index=False)

    # Coverage under Amendment 17c, per region and season
    pts = pd.read_csv(POINTS)
    cut = pts.groupby("region").elev_m.quantile(0.95)
    pts = pts[pts.region.isin(cut.index)].reset_index(drop=True)
    auto = pd.read_csv(WEEK0 / "proposed_station_set.csv", dtype={"code": str})
    auto_win = pd.read_csv(WEEK0 / "inmet_completeness.csv")
    nets = {"automatic": (auto.set_index("code"), auto_win),
            "conventional": (cand.reset_index().set_index("code"), comp)}
    circles = {(net, code): within(pts, r.lat, r.lon)
               for net, (tab, _) in nets.items() for code, r in tab.iterrows()}
    rows = []
    for y in YEARS:
        for reg in cut.index:
            sel = (pts.region == reg).values
            row = dict(window=y, crop=y + 1, region=reg)
            union = np.zeros(sel.sum(), bool)
            for net, (tab, win) in nets.items():
                ok = set(win[(win.year == y) & win.window_ok].code.astype(str))
                cov = np.zeros(sel.sum(), bool)
                n = 0
                for code, r in tab.iterrows():
                    if code in ok and r.altitude <= cut[reg]:
                        m = circles[(net, code)][sel]
                        if m.any():
                            n += 1
                            cov |= m
                row[f"{net}_stations"] = n
                row[f"{net}_coverage"] = round(100 * cov.mean(), 1)
                union |= cov
            row["combined_coverage"] = round(100 * union.mean(), 1)
            rows.append(row)
    cov = pd.DataFrame(rows)
    cov.to_csv(WEEK0 / "station_coverage_17c.csv", index=False)
    return checks, comp, cov


if __name__ == "__main__":
    main(sys.argv[1])
