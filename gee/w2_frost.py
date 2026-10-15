"""W2 frost input (§5 steps 4 and 6; Amendments 17, 17b, 17c, 17d, 36, 39), crops 2009–2027
(Jun–Aug windows 2008–2026). Local only: INMET hourly archives, the BDMEP zip, the registered
station set and the frozen-mask pixel table. No Earth Engine call. Run after `prereg-2`.

Nights (one per morning D, 1 June to 31 August, 92 per window):
  automatic     the minimum of "TEMPERATURA MÍNIMA NA HORA ANT. (AUT)" over the hourly stamps
                21 UTC on D−1 to 12 UTC on D (18:00–09:00 local, UTC−3). Observed only if all 16
                stamps are present (Amendment 17b).
  conventional  BDMEP's daily minimum dated D: the night ending the morning of D (Amendment 17d).
                Observed if present.
  A missing night is never a non-frost night.

Station tiers per window: the 2 °C tier with three or more observed nights ≤ 2 °C; the severe tier
with one or more ≤ 0 °C. A tier is unresolved when missing nights could change it (2 °C: fewer
than three observed but enough missing nights to reach three; severe: none observed and at least
one missing night). T is the station's coldest observed night.

Regions, per window (stations qualifying in `station_set_frozen.csv`, fixed elevation cuts; the
same-site rule of 17d; coffee = pixel coffee fraction for mask year S−2, filtered municipalities):
  observed coffee   coffee inside the union of qualifying stations' 25 km circles
  coverage          observed coffee / region coffee; no flag under 15% (unflaggable)
  tier shares       coffee inside the circles of stations meeting a tier / observed coffee. The
                    2 °C share counts every station meeting the 2 °C tier; for the penalty, tiers
                    are exclusive (severe first)
  flags             a tier's share ≥ 25% of observed coffee
  loss              per pixel, 140.3445·exp(−½((T+2.958)/1.7701)²) %, capped at 76.1% (the value at
                    −1 °C), zero above 2 °C, where T is the coldest minimum among the covering
                    stations that meet a tier (Amendment 36)
  penalty           for each flagged tier: the loss summed over the coffee in that tier's exclusive
                    share, divided by observed coffee. As a fraction of yield.
  17d flag          the region's flags differ when computed from automatic stations alone
Every figure is given twice: with unresolved stations at their observed tiers, and without them
(left out of the union and the tiers). The four-region total of the penalty is the PAM-weighted
mean of the regional penalties (PAM year S−2, members; prereg-1 item 10).

Run:    .venv/Scripts/python gee/w2_frost.py <path to BDMEP zip>
Writes: data/derived/w2_frost_station_season.csv, data/derived/w2_frost_region_season.csv
"""
import re
import sys
import zipfile

import numpy as np
import pandas as pd

import inmet_completeness as ic
from bdmep_candidates import within
from bdmep_completeness import read_station
from common import ROOT, WEEK0
from station_set_frozen import REGIONS, haversine_km

RAW = ROOT / "data" / "raw" / "inmet"
OUT = ROOT / "data" / "derived"
WINDOWS = range(2008, 2027)
A1, B1, C1, CAP_T = 140.3445, -2.9580, 1.7701, -1.0
FLAG, FLOOR = 0.25, 0.15


def loss(t):
    t = np.asarray(t, float)
    f = A1 * np.exp(-0.5 * ((np.maximum(t, CAP_T) - B1) / C1) ** 2) / 100.0
    return np.where(t <= 2.0, f, 0.0)


def automatic_nights(raw, year):
    rows = [l.split(";") for l in raw.decode("latin-1").splitlines()[9:] if l.strip()]
    if not rows:
        return pd.Series(dtype=float)
    date = pd.Series([r[0] for r in rows]).str.replace("/", "-")
    hour = pd.Series([r[1] for r in rows]).str.replace(" UTC", "").str.replace(":", "").str.zfill(4).str[:2]
    ts = pd.to_datetime(date + " " + hour, format="%Y-%m-%d %H", errors="coerce")
    v = pd.to_numeric(pd.Series([r[ic.TMIN_COL] if len(r) > ic.TMIN_COL else "" for r in rows])
                      .str.replace(",", "."), errors="coerce")
    v[v <= -9999] = np.nan
    s = pd.Series(v.values, index=ts).groupby(level=0).first()
    out = {}
    for d in pd.date_range(f"{year}-06-01", f"{year}-08-31", freq="D"):
        stamps = pd.date_range(d - pd.Timedelta(hours=3), d + pd.Timedelta(hours=12), freq="h")
        vals = s.reindex(stamps)
        out[d] = vals.min() if vals.notna().all() else np.nan
    return pd.Series(out)


def station_stats(nights):
    obs = nights.dropna()
    miss = int(nights.isna().sum())
    le2, le0 = int((obs <= 2.0).sum()), int((obs <= 0.0).sum())
    meets2, meets0 = le2 >= 3, le0 >= 1
    unres2 = (not meets2) and (le2 + miss >= 3)
    unres0 = (not meets0) and miss >= 1
    return dict(observed_nights=len(obs), missing_nights=miss, nights_le2=le2, nights_le0=le0,
                coldest_c=float(obs.min()) if len(obs) else np.nan,
                meets_2c=meets2, meets_severe=meets0, unresolved=bool(unres2 or unres0),
                tier="severe" if meets0 else ("2C" if meets2 else "none"))


def all_station_seasons(cand, bdmep_zip):
    rows = []
    auto = cand[cand.network == "automatic"].code.tolist()
    for y in WINDOWS:
        with zipfile.ZipFile(RAW / f"{y}.zip") as z:
            names = z.namelist()
            for code in auto:
                f = ic.station_file(names, code)
                n = automatic_nights(z.read(f), y) if f else pd.Series(
                    np.nan, index=pd.date_range(f"{y}-06-01", f"{y}-08-31", freq="D"))
                rows.append(dict(network="automatic", code=code, window=y, crop=y + 1, **station_stats(n)))
    z = zipfile.ZipFile(bdmep_zip)
    files = {re.search(r"dados_(\d+)_D_", n).group(1): n for n in z.namelist() if n.endswith(".csv")}
    for code in cand[cand.network == "conventional"].code:
        if code not in files:
            continue
        try:
            _, s, _, _ = read_station(z.read(files[code]))
        except AssertionError:  # no minimum-temperature column (Amendment 39b)
            continue
        s = s[~s.index.duplicated()]
        for y in WINDOWS:
            n = s.reindex(pd.date_range(f"{y}-06-01", f"{y}-08-31", freq="D"))
            rows.append(dict(network="conventional", code=code, window=y, crop=y + 1, **station_stats(n)))
    return pd.DataFrame(rows)


def region_figures(p, w, stations, stats):
    """Coverage, tier shares, flags and penalties for one region-window and one station set."""
    tot = w.sum()
    obs_mask = np.zeros(len(p), bool)
    t_pix = np.full(len(p), np.inf)
    sev = np.zeros(len(p), bool)
    c2 = np.zeros(len(p), bool)
    for (net, code), inside in stations.items():
        st = stats.get((net, code))
        obs_mask |= inside
        if st is None or st["tier"] == "none":
            continue
        t_pix[inside] = np.minimum(t_pix[inside], st["coldest_c"])
        if st["meets_severe"]:
            sev |= inside
        if st["meets_2c"]:
            c2 |= inside
    obs = w[obs_mask].sum()
    cov = obs / tot if tot else 0.0
    out = dict(coverage=cov, unflaggable=cov < FLOOR, observed_coffee=obs)
    if obs == 0:
        return {**out, "severe_share": 0.0, "share_2c": 0.0, "flag_severe": False, "flag_2c": False,
                "penalty_severe": 0.0, "penalty_2c": 0.0, "penalty": 0.0}
    lp = loss(np.where(np.isfinite(t_pix), t_pix, 99.0))
    excl2 = c2 & ~sev
    out.update(severe_share=w[sev].sum() / obs, share_2c=w[c2].sum() / obs)
    out["flag_severe"] = (not out["unflaggable"]) and out["severe_share"] >= FLAG
    out["flag_2c"] = (not out["unflaggable"]) and out["share_2c"] >= FLAG
    out["penalty_severe"] = (w[sev] * lp[sev]).sum() / obs if out["flag_severe"] else 0.0
    out["penalty_2c"] = (w[excl2] * lp[excl2]).sum() / obs if out["flag_2c"] else 0.0
    out["penalty"] = out["penalty_severe"] + out["penalty_2c"]
    return out


def main(bdmep_zip):
    cand = pd.read_csv(WEEK0 / "station_candidates_frozen.csv", dtype={"code": str})
    sset = pd.read_csv(WEEK0 / "station_set_frozen.csv", dtype={"code": str})
    ss = all_station_seasons(cand, bdmep_zip)
    ss.to_csv(OUT / "w2_frost_station_season.csv", index=False)
    stats = {(r.network, r.code, r.window): r._asdict() for r in ss.itertuples()}

    au, co = cand[cand.network == "automatic"], cand[cand.network == "conventional"]
    pairs = {}
    for _, c in co.iterrows():
        d = haversine_km(c.lat, c.lon, au.lat.values, au.lon.values)
        if len(d) and d.min() <= 1.0:
            pairs[c.code] = au.code.values[int(d.argmin())]
    loc = cand.set_index(["network", "code"])[["lat", "lon"]]

    pts = (pd.read_csv(OUT / "frozen_mask_pixels.csv", dtype={"code": str})
           .rename(columns={"latitude": "lat", "longitude": "lon"}))
    kept = pd.read_csv(WEEK0 / "w1_filter_stable_membership.csv", dtype={"code": str})
    pts = pts[pts.code.isin(set(kept.loc[kept.kept, "code"]))]
    members = pd.read_csv(WEEK0 / "members_by_season.csv", dtype={"code": str})

    rows = []
    for y in WINDOWS:
        band = f"w_{y - 1}"
        st_y = {k[:2]: v for k, v in stats.items() if k[2] == y}
        for rid, reg in REGIONS.items():
            p = pts[(pts[band] > 0) & (pts.region_id == rid)]
            w = p[band].values
            q = sset[(sset.window == y) & (sset.region == reg) & sset.qualifies]
            qa = set(q[q.network == "automatic"].code)
            chosen = {}
            for r in q.itertuples():
                if r.network == "conventional" and pairs.get(r.code) in qa:
                    continue  # 17d: the same-site automatic station governs
                la, lo = loc.loc[(r.network, r.code)]
                chosen[(r.network, r.code)] = within(p, la, lo)
            unres = {k for k in chosen if st_y.get(k, {}).get("unresolved")}
            base = dict(window=y, crop=y + 1, region=reg,
                        automatic_stations=sum(k[0] == "automatic" for k in chosen),
                        conventional_stations=sum(k[0] == "conventional" for k in chosen),
                        unresolved_stations=len(unres))
            for label, sel in (("with", chosen), ("without", {k: v for k, v in chosen.items() if k not in unres})):
                f = region_figures(p, w, sel, st_y)
                base.update({f"{k}_{label}_unresolved": v for k, v in f.items()})
            auto_only = region_figures(p, w, {k: v for k, v in chosen.items() if k[0] == "automatic"}, st_y)
            base["flag_17d"] = ((auto_only["flag_severe"] != base["flag_severe_with_unresolved"])
                                or (auto_only["flag_2c"] != base["flag_2c_with_unresolved"]))
            rows.append(base)
    reg = pd.DataFrame(rows)
    # four-region total: PAM-weighted mean of regional penalties (PAM year S−2, members)
    pam = (members[members.member].groupby(["season", "region"]).pam_ha.sum().rename("pam_ha").reset_index()
           .rename(columns={"season": "crop"}))
    reg = reg.merge(pam, on=["crop", "region"], how="left")
    tot = []
    for crop, d in reg.groupby("crop"):
        row = dict(window=crop - 1, crop=crop, region="Four-region total")
        if d.pam_ha.notna().all():
            for label in ("with", "without"):
                row[f"penalty_{label}_unresolved"] = float(np.average(d[f"penalty_{label}_unresolved"], weights=d.pam_ha))
        tot.append(row)
    reg = pd.concat([reg, pd.DataFrame(tot)], ignore_index=True)
    reg.to_csv(OUT / "w2_frost_region_season.csv", index=False, float_format="%.5f")
    return ss, reg


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    ss, reg = main(sys.argv[1])
    print(ss.groupby(["network", "tier"]).size().unstack(fill_value=0).to_string())
    print("unresolved station-windows:", int(ss.unresolved.sum()), "of", len(ss))
    r = reg[reg.region != "Four-region total"]
    print(r.pivot(index="crop", columns="region", values="penalty_with_unresolved").round(3).to_string())
