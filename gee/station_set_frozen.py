"""prereg-2: the frost station set, elevation cut and observed coverage on the frozen mask
(§5 step 4; Amendments 17, 17b, 17c, 17d). The committed script the Week 0 report §8 promised;
it replaces the provisional tables computed on the Collection 10 (2024) sample. No temperature is
read: only whether observations are present. No frost night is counted.

Inputs:
  data/derived/frozen_mask_pixels.csv   gee/frozen_mask_pixels.py: every MOD13Q1 pixel with coffee
                                        in some mask year 2007–2025, with its coffee fraction per
                                        mask year (the registered W1 weights), municipality code
                                        and SRTM elevation at the pixel centre
  w1_filter_stable_membership.csv       the stable filter (Amendment 16d): pixels in dropped
                                        municipalities are left out (the frozen mask); the
                                        no-filter coverage is reported beside it
  data/raw/inmet/catalogo_estacoes_automaticas.csv, bdmep_estacoes_convencionais.csv
                                        every automatic and conventional station, any state
  data/raw/inmet/{2008..2026}.zip       automatic completeness (gee/inmet_completeness.py rule)
  docs/week0/bdmep_completeness.csv     conventional completeness, for the stations whose BDMEP
                                        data were requested

Rules, per frost window Jun–Aug of year y (crop y+1, mask year y−1):
  coffee area      pixel coffee fraction for the window's mask year; every share below is
                   coffee-area weighted (pixel centres within 25 km of a station count as inside)
  candidate        a station with frozen-mask coffee within 25 km in some mask year
  elevation cut    per region and mask year: the coffee-area-weighted 95th percentile of SRTM
                   elevation; a station is tested against the cut of each region whose coffee its
                   circle holds
  qualifies        complete window (automatic ≥95% of hours, no gap > 48 h; conventional ≥88 of 92
                   days, no gap > 3 days), at or below the cut, and some of the region's coffee in
                   its circle that year
  same site        a conventional and an automatic station within 1 km: where both qualify, the
                   automatic governs and the conventional is left out of the union (17d)
  coverage         share of the region's coffee area inside the union of qualifying circles,
                   overlaps counted once; unflaggable when the combined coverage is under 15% (17c)

Run:    .venv/Scripts/python gee/station_set_frozen.py
Writes: docs/week0/station_candidates_frozen.csv, docs/week0/inmet_completeness_frozen.csv,
        docs/week0/station_set_frozen.csv (station × region × window),
        docs/week0/station_coverage_frozen.csv (region × window), docs/week0/elevation_cut_frozen.csv
"""
import zipfile

import numpy as np
import pandas as pd

import inmet_completeness as ic
from bdmep_candidates import within
from common import ROOT, WEEK0

RAW = ROOT / "data" / "raw" / "inmet"
REGIONS = {1: "Sul e Centro-Oeste", 2: "Triângulo, Alto Paranaíba e Noroeste",
           3: "Zona da Mata, Rio Doce e Central", 4: "São Paulo (state total)"}
WINDOWS = range(2008, 2027)
FLOOR = 15.0
SAME_SITE_KM = 1.0


def stations():
    a = pd.read_csv(RAW / "catalogo_estacoes_automaticas.csv", sep=";", dtype=str)
    auto = pd.DataFrame({
        "code": a["Código"], "name": a["Nome"], "uf": a["UF"], "status": a["Situação"],
        "lat": pd.to_numeric(a["Latitude"].str.replace(",", "."), errors="coerce"),
        "lon": pd.to_numeric(a["Longitude"].str.replace(",", "."), errors="coerce"),
        "altitude": pd.to_numeric(a["Altitude"].str.replace(",", "."), errors="coerce"),
        "network": "automatic"})
    c = pd.read_csv(RAW / "bdmep_estacoes_convencionais.csv", sep=";", dtype=str)
    num = lambda s: pd.to_numeric(s.str.replace(",", "."), errors="coerce")  # noqa: E731
    conv = pd.DataFrame({
        "code": c["CD_ESTACAO"], "name": c["DC_NOME"], "uf": c["SG_ESTADO"], "status": c["CD_SITUACAO"],
        "lat": num(c["VL_LATITUDE"]), "lon": num(c["VL_LONGITUDE"]), "altitude": num(c["VL_ALTITUDE"]),
        "network": "conventional"})
    return pd.concat([auto, conv], ignore_index=True)


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def automatic_windows(codes):
    have = pd.read_csv(WEEK0 / "inmet_completeness.csv", dtype={"code": str})
    todo = [c for c in codes if c not in set(have.code)]
    rows = []
    for year in ic.YEARS:
        if not todo:
            break
        with zipfile.ZipFile(RAW / f"{year}.zip") as z:
            names = z.namelist()
            for code in todo:
                f = ic.station_file(names, code)
                valid, gap = ic.window_stats(z.read(f), year) if f else (0, ic.HOURS)
                rows.append(dict(code=code, year=year, file=f or "", valid_hours=valid,
                                 share=round(valid / ic.HOURS, 4), max_gap_h=gap))
    new = pd.DataFrame(rows, columns=["code", "year", "file", "valid_hours", "share", "max_gap_h"])
    if len(new):
        new["window_ok"] = (new.share >= ic.MIN_SHARE) & (new.max_gap_h <= ic.MAX_GAP)
    out = pd.concat([have[have.code.isin(codes)], new], ignore_index=True)
    out.to_csv(WEEK0 / "inmet_completeness_frozen.csv", index=False)
    return out, todo


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(x[o][np.searchsorted(c, q * c[-1])])


def main():
    pts = (pd.read_csv(ROOT / "data" / "derived" / "frozen_mask_pixels.csv", dtype={"code": str})
           .rename(columns={"latitude": "lat", "longitude": "lon"}))
    pts["region"] = pts.region_id.map(REGIONS)
    kept = pd.read_csv(WEEK0 / "w1_filter_stable_membership.csv", dtype={"code": str})
    pts["kept"] = pts.code.isin(set(kept.loc[kept.kept, "code"]))
    st = stations().dropna(subset=["lat", "lon"]).reset_index(drop=True)

    # candidates: frozen-mask coffee within 25 km in some mask year
    fro = pts[pts.kept & (pts[[f"w_{m}" for m in range(2007, 2026)]].max(axis=1) > 0)]
    # only stations within half a degree of the mask's extent can hold coffee within 25 km
    box = (st.lat.between(fro.lat.min() - 0.5, fro.lat.max() + 0.5)
           & st.lon.between(fro.lon.min() - 0.5, fro.lon.max() + 0.5))
    st = st[box].reset_index(drop=True)
    st["frozen_pixels_25km"] = [int(within(fro, r.lat, r.lon).sum()) for r in st.itertuples()]
    cand = st[st.frozen_pixels_25km > 0].copy()
    auto_win, computed = automatic_windows(cand.loc[cand.network == "automatic", "code"].tolist())
    conv_win = pd.read_csv(WEEK0 / "bdmep_completeness.csv", dtype={"code": str})
    cand["windows_source"] = np.where(
        cand.network == "automatic", np.where(cand.code.isin(computed), "computed now", "inmet_completeness.csv"),
        np.where(cand.code.isin(set(conv_win.code)), "bdmep_completeness.csv", "no BDMEP data requested"))
    cand.to_csv(WEEK0 / "station_candidates_frozen.csv", index=False)
    ok = {("automatic", r.code, r.year): bool(r.window_ok) for r in auto_win.itertuples()}
    ok.update({("conventional", r.code, r.year): bool(r.window_ok) for r in conv_win.itertuples()})

    # same-site pairs (17d), recomputed from the catalogues for the candidates
    au, co = cand[cand.network == "automatic"], cand[cand.network == "conventional"]
    pairs = {}
    for _, c in co.iterrows():
        d = haversine_km(c.lat, c.lon, au.lat.values, au.lon.values)
        if len(d) and d.min() <= SAME_SITE_KM:
            pairs[c.code] = au.code.values[int(d.argmin())]

    cuts, rows, cov = [], [], []
    for y in WINDOWS:
        m_year = y - 1
        band = f"w_{m_year}"
        for rid, reg in REGIONS.items():
            p = fro[(fro[band] > 0) & (fro.region_id == rid)]
            pu = pts[(pts[band] > 0) & (pts.region_id == rid)]
            w, wu = p[band].values, pu[band].values
            cut = wquantile(p.elev_m.values.astype(float), w, 0.95)
            cuts.append(dict(window=y, crop=y + 1, mask_year=m_year, region=reg, pixels=len(p),
                             coffee_pixel_equivalents=round(w.sum()), elev_cut_m=round(cut, 1)))
            qual = {"automatic": {}, "conventional": {}}
            for i, s in cand.iterrows():
                inside = within(p, s.lat, s.lon)
                if not inside.any():
                    continue
                complete = ok.get((s.network, s.code, y))
                below = bool(s.altitude <= cut) if pd.notna(s.altitude) else False
                q = bool(complete) and below
                rows.append(dict(window=y, crop=y + 1, region=reg, network=s.network, code=s.code,
                                 name=s["name"], uf=s.uf, altitude=s.altitude, elev_cut_m=round(cut, 1),
                                 above_cut=not below, within_50m_of_cut=abs(s.altitude - cut) <= 50 if pd.notna(s.altitude) else None,
                                 window_complete=complete, qualifies=q,
                                 coffee_share_25km=round(w[inside].sum() / w.sum(), 4)))
                if q:
                    qual[s.network][s.code] = inside
            # 17d: a conventional station sharing a site with a qualifying automatic is left out
            left_out = [c for c in qual["conventional"] if pairs.get(c) in qual["automatic"]]
            union_a = np.any(list(qual["automatic"].values()), axis=0) if qual["automatic"] else np.zeros(len(p), bool)
            conv_used = {c: v for c, v in qual["conventional"].items() if c not in left_out}
            union_c = np.any(list(qual["conventional"].values()), axis=0) if qual["conventional"] else np.zeros(len(p), bool)
            union = union_a | (np.any(list(conv_used.values()), axis=0) if conv_used else np.zeros(len(p), bool))
            # no-filter sensitivity: the same stations, all points
            uni_u = np.zeros(len(pu), bool)
            for net in ("automatic", "conventional"):
                for code in (qual[net] if net == "automatic" else conv_used):
                    s = cand[(cand.network == net) & (cand.code == code)].iloc[0]
                    uni_u |= within(pu, s.lat, s.lon)
            share = lambda m, ww: 100 * ww[m].sum() / ww.sum()  # noqa: E731
            cov.append(dict(window=y, crop=y + 1, region=reg, coffee_pixel_equivalents=round(w.sum()),
                            automatic_stations=len(qual["automatic"]), conventional_stations=len(conv_used),
                            conventional_left_out_same_site=len(left_out),
                            automatic_coverage=round(share(union_a, w), 1),
                            conventional_coverage=round(share(union_c, w), 1),
                            combined_coverage=round(share(union, w), 1),
                            unflaggable=share(union, w) < FLOOR,
                            combined_coverage_no_filter=round(share(uni_u, wu), 1)))
    pd.DataFrame(cuts).to_csv(WEEK0 / "elevation_cut_frozen.csv", index=False)
    pd.DataFrame(rows).to_csv(WEEK0 / "station_set_frozen.csv", index=False)
    cov = pd.DataFrame(cov)
    cov.to_csv(WEEK0 / "station_coverage_frozen.csv", index=False)
    return cand, pd.DataFrame(cuts), pd.DataFrame(rows), cov, pairs


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    cand, cuts, rows, cov, pairs = main()
    print(cand.groupby(["network", "windows_source"]).size().to_string())
    print(cuts.pivot(index="crop", columns="region", values="elev_cut_m").to_string())
    print(cov.pivot(index="crop", columns="region", values="combined_coverage").to_string())
    print("unflaggable:", cov[cov.unflaggable][["crop", "region", "combined_coverage"]].to_string(index=False))
    print("same-site pairs:", pairs)
