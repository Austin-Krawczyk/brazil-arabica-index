"""W1: the one-sided 30% filter with stable membership (owner, 2026-10-14; Amendment 16d draft).

Each municipality is tested once, on its median ratio of persistent-pixel MapBiomas coffee area
(Amendment 16b) to IBGE PAM total coffee area across all mask years 1998–2025, and is dropped for
every season or for none. Reason (owner): season-varying membership puts composition changes into
the anomaly series, and single-season crossings of 1.3 are threshold noise, not over-mapping.

Ratio per mask year:
  PAM > 0                      MapBiomas persistent / PAM
  PAM = 0, MapBiomas > 0       infinite (MapBiomas maps coffee PAM does not record)
  PAM = 0, MapBiomas = 0       not counted (no coffee either side)
  PAM missing ("...")          not counted
A municipality with MapBiomas coffee but no countable year is dropped as untestable (its mapped
area is reported). Dropped when the median ratio exceeds 1.3.

Run:    .venv/Scripts/python gee/w1_filter_stable.py
Reads:  docs/week0/w1_filter_kept.csv (per municipality and mask year: areas and PAM)
Writes: docs/week0/w1_filter_stable_membership.csv, docs/week0/w1_filter_stable_removed.csv,
        docs/week0/w1_retention_stable.csv
"""
import numpy as np
import pandas as pd

from common import WEEK0

THRESHOLD = 1.3


def main():
    k = pd.read_csv(WEEK0 / "w1_filter_kept.csv", dtype={"code": str})
    names = pd.read_csv(WEEK0 / "proposed_region_membership.csv", dtype={"code": str}).set_index("code")["name"]
    ratio = np.where(k.pam_ha > 0, k.mb_pers_ha / k.pam_ha,
                     np.where((k.pam_ha == 0) & (k.mb_pers_ha > 0), np.inf, np.nan))
    k["ratio"] = ratio
    g = k.groupby(["code", "region"])
    m = pd.DataFrame({
        "years_counted": g.ratio.count(),
        "median_ratio": g.ratio.median(),
        "years_over_1_3": g.ratio.apply(lambda r: int((r > THRESHOLD).sum())),
        "mean_mapped_ha": g.mb_full_ha.mean(),
        "mapped_ha_2025": g.apply(lambda d: float(d.loc[d.mask_year == d.mask_year.max(), "mb_full_ha"].sum())),
        "mean_pam_ha": g.pam_ha.mean(),
    }).reset_index()
    m["name"] = m.code.map(names)
    has_coffee = m.mean_mapped_ha > 0
    m["decision"] = np.select(
        [~has_coffee, m.years_counted == 0, m.median_ratio > THRESHOLD],
        ["no mapped coffee", "dropped: untestable (no comparable year)", "dropped: median ratio > 1.3"],
        default="kept")
    m["kept"] = m.decision.isin(["kept", "no mapped coffee"])
    m.to_csv(WEEK0 / "w1_filter_stable_membership.csv", index=False)
    removed = m[~m.kept].sort_values(["region", "mean_mapped_ha"], ascending=[True, False])
    removed.to_csv(WEEK0 / "w1_filter_stable_removed.csv", index=False)

    keep = set(m.loc[m.kept, "code"])
    k["kept_stable"] = k.code.isin(keep)
    rows = []
    for (yr, reg), d in k[k.mb_full_ha > 0].groupby(["mask_year", "region"]):
        rows.append(dict(mask_year=yr, season=yr + 2, region=reg,
                         kept_share=round(d.loc[d.kept_stable, "mb_full_ha"].sum() / d.mb_full_ha.sum(), 4)))
    ret = pd.DataFrame(rows)
    ret.to_csv(WEEK0 / "w1_retention_stable.csv", index=False)
    return m, removed, ret


if __name__ == "__main__":
    m, removed, ret = main()
    pd.set_option("display.width", 250)
    print(m.groupby(["region", "decision"]).size().unstack(fill_value=0).to_string())
    print(ret.groupby("region").kept_share.agg(["min", "max"]).round(3).to_string())
    for reg, d in removed.groupby("region"):
        print(f"\n{reg}: {len(d)} removed; mapped area removed (mean over years) {d.mean_mapped_ha.sum():,.0f} ha")
        print(d.head(10)[["name", "decision", "years_counted", "median_ratio", "years_over_1_3", "mean_mapped_ha", "mean_pam_ha"]]
              .round(2).to_string(index=False))
