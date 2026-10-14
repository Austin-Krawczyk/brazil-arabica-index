"""INMET conventional stations as an extra frost source (owner decision 2026-10-14): candidates and
the most coverage they could add.

Candidates: conventional stations from BDMEP's station list (data/raw/inmet/
bdmep_estacoes_convencionais.csv) within 25 km of a coffee sample point in an index region, whose
operating period overlaps June 2008 - August 2026. A station "operates through" a June-August
window if it started before 1 June and its end date, if any, is after 31 August of that year.

The coverage added is an upper bound: it assumes every conventional station is complete in every
window it operates through. Completeness can only be tested on the downloaded daily data. Nothing
here reads a temperature.

Same coffee sample, regions, 25 km radius and elevation cut as the automatic-network proposal
(docs/week0_report.md §8).

Run:    .venv/Scripts/python gee/bdmep_candidates.py
Writes: docs/week0/bdmep_candidates.csv, docs/week0/bdmep_coverage_upper_bound.csv
"""
import numpy as np
import pandas as pd

from common import ROOT, WEEK0

RAW = ROOT / "data" / "raw" / "inmet" / "bdmep_estacoes_convencionais.csv"
POINTS = ROOT / "data" / "derived" / "_tmp_sample_regions_elev.csv"
AUTO = WEEK0 / "proposed_station_set.csv"
AUTO_WINDOWS = WEEK0 / "inmet_completeness.csv"
RADIUS_KM, R_EARTH = 25, 6371.0088
YEARS = range(2008, 2027)


def within(pts, lat, lon):
    p1, p2 = np.radians(pts.lat.values), np.radians(lat)
    a = (np.sin((p2 - p1) / 2) ** 2
         + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon - pts.lon.values) / 2) ** 2)
    return 2 * R_EARTH * np.arcsin(np.sqrt(a)) <= RADIUS_KM


def main():
    pts = pd.read_csv(POINTS)
    cut = pts.groupby("region").elev_m.quantile(0.95)
    pts = pts[pts.region.isin(cut.index)].reset_index(drop=True)
    conv = pd.read_csv(RAW, sep=";", dtype=str)
    for c in ("VL_LATITUDE", "VL_LONGITUDE", "VL_ALTITUDE"):
        conv[c] = conv[c].astype(float)
    conv["start"] = pd.to_datetime(conv.DT_INICIO_OPERACAO.str[:10])
    conv["end"] = pd.to_datetime(conv.DT_FIM_OPERACAO.str[:10])

    near = {r.CD_ESTACAO: within(pts, r.VL_LATITUDE, r.VL_LONGITUDE) for r in conv.itertuples()}
    conv["pts_25km"] = conv.CD_ESTACAO.map(lambda c: int(near[c].sum()))
    cand = conv[conv.pts_25km > 0].copy()

    def operates(r, y):
        if pd.isna(r.start):
            return None  # no dates in BDMEP's list
        return r.start <= pd.Timestamp(f"{y}-06-01") and (pd.isna(r.end) or r.end >= pd.Timestamp(f"{y}-08-31"))

    rows = []
    for r in cand.itertuples():
        ops = [y for y in YEARS if operates(r, y)]
        regions = pts.region[near[r.CD_ESTACAO]].value_counts()
        row = dict(code=r.CD_ESTACAO, name=r.DC_NOME, uf=r.SG_ESTADO, status=r.CD_SITUACAO,
                   lat=r.VL_LATITUDE, lon=r.VL_LONGITUDE, altitude=r.VL_ALTITUDE,
                   start=r.DT_INICIO_OPERACAO[:10] if isinstance(r.DT_INICIO_OPERACAO, str) else "",
                   end=r.DT_FIM_OPERACAO[:10] if isinstance(r.DT_FIM_OPERACAO, str) else "",
                   end_missing_but_not_operating=(r.CD_SITUACAO != "Operante" and pd.isna(r.end)),
                   main_region=regions.index[0], pts_25km=r.pts_25km,
                   windows_operating=len(ops), first_window=min(ops) if ops else "",
                   last_window=max(ops) if ops else "")
        for reg in cut.index:
            sel = (pts.region == reg).values
            row[f"coffee_share_25km_{reg[:10]}"] = round(near[r.CD_ESTACAO][sel].mean(), 4)
            row[f"above_cut_{reg[:10]}"] = bool(r.VL_ALTITUDE > cut[reg])
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["main_region", "code"])
    out = out[out.windows_operating > 0]
    out.to_csv(WEEK0 / "bdmep_candidates.csv", index=False)

    # Upper bound on coverage, per window: automatic stations complete that season, plus every
    # conventional candidate operating through the window (assumed complete), below each region's cut.
    auto = pd.read_csv(AUTO, dtype={"code": str})
    win = pd.read_csv(AUTO_WINDOWS)
    auto_near = {c: within(pts, la, lo) for c, la, lo in zip(auto.code, auto.lat, auto.lon)}
    cov = []
    for y in YEARS:
        auto_ok = set(win[(win.year == y) & win.window_ok].code)
        conv_ok = [r for r in out.itertuples() if r.first_window != "" and r.first_window <= y <= r.last_window]
        for reg in cut.index:
            sel = (pts.region == reg).values
            a = np.zeros(sel.sum(), bool)
            for r in auto.itertuples():
                if r.code in auto_ok and r.altitude <= cut[reg]:
                    a |= auto_near[r.code][sel]
            b = a.copy()
            n_conv = 0
            for r in conv_ok:
                if r.altitude <= cut[reg]:
                    m = near[r.code][sel]
                    n_conv += int(m.any())
                    b |= m
            cov.append(dict(window=y, crop=y + 1, region=reg, automatic=round(100 * a.mean(), 1),
                            with_conventional_upper=round(100 * b.mean(), 1), conventional_stations=n_conv))
    cov = pd.DataFrame(cov)
    cov.to_csv(WEEK0 / "bdmep_coverage_upper_bound.csv", index=False)
    print(f"{len(conv)} conventional stations listed; {len(out)} within {RADIUS_KM} km of index coffee "
          f"and operating through at least one June-August window 2008-2026")
    return out, cov


if __name__ == "__main__":
    main()
