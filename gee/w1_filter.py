"""W1: the 30% filter against IBGE PAM, per season, and its removal report (§5 step 1;
Amendments 16, 16b, 16c).

For each mask year M (crop S = M + 2), a municipality is kept when its persistent-pixel
MapBiomas coffee area (class 46 in M, M−1 and M−2; Amendment 16b) is within 30% of IBGE PAM's
coffee area for M: |MapBiomas − PAM| / PAM ≤ 0.30. No minimum area (owner, 2026-10-14).

  comparator   PAM table 1613, variable 2313 (area intended for harvest), category 2723 "Café
               (em grão) Total": MapBiomas class 46 does not separate species, and PAM's arabica
               split (category 31619) starts only in 2012 (owner, 2026-10-14)
  PAM = 0      with MapBiomas coffee: removed ("PAM zero"). With none: no coffee either side.
  PAM missing  ("...", or the municipality absent from PAM) with MapBiomas coffee: removed as not
               comparable, counted separately (agent's handling, flagged for the owner)

Removal report, per mask year and region: municipalities with coffee, removed and kept; the
coffee area removed (MapBiomas full and PAM); and how removed and kept differ in distribution:
size, the direction of the mismatch, and the three-year MapBiomas area change (Amendment 16)
from M−3 to M.

Run:    .venv/Scripts/python gee/w1_filter.py
Reads:  data/derived/w1_mask_areas.csv, data/raw/ibge/pam1613_v2313_*.json
Writes: docs/week0/w1_filter_kept.csv, docs/week0/w1_removal_report.csv
"""
import json

import numpy as np
import pandas as pd

from common import ROOT, WEEK0
from w1_mask import LAG, MASK_YEARS

THRESHOLD = 0.30
CHANGE_BANDS = (-0.10, 0.10)  # three-year change: contracting below -10%, expanding above +10%


def pam_total():
    rows = []
    for year in MASK_YEARS:
        j = json.loads((ROOT / "data" / "raw" / "ibge" / f"pam1613_v2313_{year}.json").read_text(encoding="utf-8"))
        for res in j[0]["resultados"]:
            if "2723" not in res["classificacoes"][0]["categoria"]:
                continue
            for s in res["series"]:
                raw = s["serie"][str(year)]
                ha = 0.0 if raw == "-" else (np.nan if raw in ("...", "..", "X") else float(raw))
                rows.append(dict(code=s["localidade"]["id"], mask_year=year, pam_ha=ha, pam_raw=raw))
    return pd.DataFrame(rows)


def main():
    areas = pd.read_csv(ROOT / "data" / "derived" / "w1_mask_areas.csv", dtype={"code": str})
    pam = pam_total()
    out = []
    for m in MASK_YEARS:
        a = areas[["code", "region", f"pers_{m}", f"full_{m}", f"full_{m - 3}"]].rename(
            columns={f"pers_{m}": "mb_pers_ha", f"full_{m}": "mb_full_ha", f"full_{m - 3}": "mb_full_m3_ha"})
        a = a.merge(pam[pam.mask_year == m][["code", "pam_ha", "pam_raw"]], on="code", how="left")
        a["mask_year"], a["season"] = m, m + LAG
        has_mb = a.mb_pers_ha > 0
        rel = (a.mb_pers_ha - a.pam_ha).abs() / a.pam_ha
        a["rel_diff"] = rel.where(a.pam_ha > 0)
        a["reason"] = np.select(
            [~has_mb & ~(a.pam_ha > 0), a.pam_ha.isna() & has_mb, (a.pam_ha == 0) & has_mb,
             a.rel_diff > THRESHOLD],
            ["no coffee", "PAM missing", "PAM zero", "differs > 30%"], default="kept")
        a["kept"] = a.reason.isin(["kept", "no coffee"])
        a["mb_over_pam"] = a.mb_pers_ha > a.pam_ha
        chg = (a.mb_full_ha - a.mb_full_m3_ha) / a.mb_full_m3_ha
        a["change_3y"] = np.where(a.mb_full_m3_ha > 0, chg, np.where(a.mb_full_ha > 0, np.inf, np.nan))
        a["change_class"] = pd.cut(a.change_3y, [-np.inf, CHANGE_BANDS[0], CHANGE_BANDS[1], np.inf],
                                   labels=["contracting", "stable", "expanding"])
        out.append(a)
    df = pd.concat(out, ignore_index=True)
    df.to_csv(WEEK0 / "w1_filter_kept.csv", index=False)

    rep = []
    coffee = df[df.reason != "no coffee"]
    for (m, reg), g in coffee.groupby(["mask_year", "region"]):
        rem, kep = g[~g.kept], g[g.kept]
        row = dict(mask_year=m, season=m + LAG, region=reg, municipalities=len(g), removed=len(rem),
                   removed_pam_missing=int((rem.reason == "PAM missing").sum()),
                   removed_pam_zero=int((rem.reason == "PAM zero").sum()),
                   removed_over_30=int((rem.reason == "differs > 30%").sum()),
                   mb_full_ha=round(g.mb_full_ha.sum()), mb_full_removed_share=round(rem.mb_full_ha.sum() / g.mb_full_ha.sum(), 4),
                   pam_ha=round(g.pam_ha.sum()), pam_removed_share=round(rem.pam_ha.sum() / g.pam_ha.sum(), 4) if g.pam_ha.sum() else np.nan,
                   median_mb_ha_removed=round(rem.mb_full_ha.median(), 1) if len(rem) else np.nan,
                   median_mb_ha_kept=round(kep.mb_full_ha.median(), 1) if len(kep) else np.nan,
                   removed_mb_over_pam_share=round(rem.mb_over_pam.mean(), 3) if len(rem) else np.nan)
        for cls in ("contracting", "stable", "expanding"):
            row[f"removed_share_{cls}"] = round((rem.change_class == cls).mean(), 3) if len(rem) else np.nan
            row[f"kept_share_{cls}"] = round((kep.change_class == cls).mean(), 3) if len(kep) else np.nan
        rep.append(row)
    rep = pd.DataFrame(rep)
    rep.to_csv(WEEK0 / "w1_removal_report.csv", index=False)
    return df, rep


if __name__ == "__main__":
    df, rep = main()
    pd.set_option("display.width", 250)
    print(rep.groupby("region")[["municipalities", "removed", "mb_full_removed_share", "pam_removed_share"]].mean().round(3))
