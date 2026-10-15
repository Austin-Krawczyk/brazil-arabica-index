"""Before prereg-1 (owner, 2026-10-15): how much of each region's PAM coffee area the W1 readings
represent, per region and season, and the W1 rows with an EVI median above 0.9. Local only; no
Earth Engine call.

Definitions (owner decision 1, 2026-10-15):
  region PAM          IBGE PAM total coffee area (table 1613, var 2313) for PAM year S−2, summed
                      over all of the region's index municipalities
  member              kept by the stable filter (Amendment 16d), PAM area > 0, and at least one
                      MODIS pixel of mapped coffee under season S's mask: f_w_total_sum ≥ 1, the
                      sum of per-pixel coffee fractions, i.e. one 250 m pixel's worth (5.37 ha)
  member share        PAM area of members / region PAM, per region and season
  covered fraction    per composite: PAM area of members with an EVI median / PAM area of members.
                      A regional composite is missing when it is under 0.5 (the registered floor)

The shortfall from 1 is split by cause: dropped by the filter; kept, but under one pixel of
mapped coffee (including none); PAM missing (IBGE "...", not counted on either side).

Run:    .venv/Scripts/python gee/w1_reading_coverage.py
Reads:  data/derived/w1_series_muni_<region>.csv, docs/week0/w1_filter_kept.csv,
        docs/week0/w1_filter_stable_membership.csv, docs/week0/proposed_region_membership.csv
Writes: docs/week0/w1_member_share.csv (region × season), docs/week0/w1_covered_fraction.csv
        (region × composite), docs/week0/w1_evi_above_0_9.csv, docs/week0/members_by_season.csv
        (municipality × season: PAM area, mapped coffee in MODIS pixels, kept, member)
"""
import glob

import numpy as np
import pandas as pd

from common import ROOT, WEEK0

MIN_PIXELS = 1.0
FLOOR = 0.5
EVI_HIGH = 0.9


def load():
    series = pd.concat([pd.read_csv(f, dtype={"code": str})
                        for f in sorted(glob.glob(str(ROOT / "data" / "derived" / "w1_series_muni_*.csv")))],
                       ignore_index=True)
    k = pd.read_csv(WEEK0 / "w1_filter_kept.csv", dtype={"code": str})
    stable = pd.read_csv(WEEK0 / "w1_filter_stable_membership.csv", dtype={"code": str})
    names = pd.read_csv(WEEK0 / "proposed_region_membership.csv", dtype={"code": str}).set_index("code")["name"]
    return series, k, set(stable.loc[stable.kept, "code"]), names


def main():
    s, k, kept, names = load()
    # one row per municipality and season: its mapped coffee in pixels (constant within a season)
    px = s.groupby(["code", "season"]).f_w_total_sum.agg(["min", "max"])
    assert np.allclose(px["min"], px["max"], rtol=1e-6), "coffee weight varies within a season"
    px = px["max"].rename("pixels").reset_index()

    pam = k[["code", "region", "mask_year", "pam_ha"]].copy()
    pam["season"] = pam.mask_year + 2
    pam = pam.merge(px, on=["code", "season"], how="left")
    pam["pixels"] = pam.pixels.fillna(0.0)  # no row in W1 = no mapped coffee in that season
    pam["kept"] = pam.code.isin(kept)
    pam["member"] = pam.kept & (pam.pam_ha > 0) & (pam.pixels >= MIN_PIXELS)
    seasons = sorted(s.season.unique())
    pam = pam[pam.season.isin(seasons)]

    rows = []
    for (reg, S), d in pam.groupby(["region", "season"]):
        tot = d.pam_ha.sum()
        rows.append(dict(
            region=reg, season=S, pam_year=S - 2, municipalities=len(d),
            pam_missing=int(d.pam_ha.isna().sum()),
            members=int(d.member.sum()), region_pam_ha=round(tot),
            member_share=d.loc[d.member, "pam_ha"].sum() / tot,
            dropped_by_filter=d.loc[~d.kept, "pam_ha"].sum() / tot,
            under_one_pixel=d.loc[d.kept & (d.pixels < MIN_PIXELS), "pam_ha"].sum() / tot,
        ))
    share = pd.DataFrame(rows)
    # four-region total, by the same rule (regions summed by PAM area)
    tot = (pam.groupby("season").apply(lambda d: pd.Series(dict(
        region="Four-region total", municipalities=len(d), pam_missing=int(d.pam_ha.isna().sum()),
        members=int(d.member.sum()), region_pam_ha=round(d.pam_ha.sum()),
        member_share=d.loc[d.member, "pam_ha"].sum() / d.pam_ha.sum(),
        dropped_by_filter=d.loc[~d.kept, "pam_ha"].sum() / d.pam_ha.sum(),
        under_one_pixel=d.loc[d.kept & (d.pixels < MIN_PIXELS), "pam_ha"].sum() / d.pam_ha.sum())))
        .reset_index())
    tot["pam_year"] = tot.season - 2

    # covered fraction per composite
    m = pam.loc[pam.member, ["code", "season", "pam_ha"]]
    r = s.merge(m, on=["code", "season"], how="inner")
    r["has"] = r.f_q1_EVI_median.notna()
    cov = (r.groupby(["region", "composite_start", "season"])
           .apply(lambda d: pd.Series(dict(members=len(d), with_reading=int(d.has.sum()),
                                           covered_fraction=d.loc[d.has, "pam_ha"].sum() / d.pam_ha.sum())))
           .reset_index())
    # members present in the season but absent from a composite would make the fraction too high
    n_members = pam[pam.member].groupby(["region", "season"]).size().rename("members_season")
    cov = cov.join(n_members, on=["region", "season"])
    assert (cov.members == cov.members_season).all(), "a member is missing from some composite"
    cov = cov.drop(columns="members_season")
    cov["below_floor"] = cov.covered_fraction < FLOOR
    c = cov.groupby(["region", "season"]).covered_fraction.agg(
        composites="size", covered_min="min", covered_median="median",
        below_floor=lambda x: int((x < FLOOR).sum()))
    share = share.join(c, on=["region", "season"])

    # the member table per season (Amendment 35), registered at prereg-2
    pam[["code", "region", "season", "mask_year", "pam_ha", "pixels", "kept", "member"]].sort_values(
        ["region", "code", "season"]).to_csv(WEEK0 / "members_by_season.csv", index=False, float_format="%.4f")
    out = pd.concat([share, tot], ignore_index=True)
    out.to_csv(WEEK0 / "w1_member_share.csv", index=False, float_format="%.4f")
    cov.to_csv(WEEK0 / "w1_covered_fraction.csv", index=False, float_format="%.4f")

    # EVI medians above 0.9
    hi = s[s.f_q1_EVI_median > EVI_HIGH].copy()
    hi["name"] = hi.code.map(names)
    hi = hi.merge(pam[["code", "season", "kept", "member", "pam_ha"]], on=["code", "season"], how="left")
    hi["valid_pixels"] = hi.f_q1_w_valid_sum
    hi = hi[["code", "name", "region", "composite_start", "season", "mask_year", "f_w_total_sum", "valid_pixels",
             "f_q1_EVI_median", "f_q1_EVI_mean", "f_q1_NDVI_median", "kept", "member", "pam_ha"]]
    hi.to_csv(WEEK0 / "w1_evi_above_0_9.csv", index=False, float_format="%.4f")
    return out, cov, hi, s


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    out, cov, hi, s = main()
    for reg, d in out.groupby("region"):
        print(f"\n{reg}: member share {d.member_share.min():.3f}-{d.member_share.max():.3f} "
              f"(median {d.member_share.median():.3f}); dropped by filter "
              f"{d.dropped_by_filter.min():.3f}-{d.dropped_by_filter.max():.3f}; under one pixel "
              f"{d.under_one_pixel.min():.3f}-{d.under_one_pixel.max():.3f}")
        if "composites" in d and d.composites.notna().any():
            print(f"  covered fraction: min {d.covered_min.min():.3f}; composites below {FLOOR:.0%}: "
                  f"{int(d.below_floor.sum())} of {int(d.composites.sum())}")
    print(f"\nEVI median > {EVI_HIGH}: {len(hi)} of {s.f_q1_EVI_median.notna().sum()} non-empty rows")
    print(hi.groupby(["region", "name"]).agg(rows=("code", "size"), pixels=("f_w_total_sum", "median"),
                                             member=("member", "max")).sort_values("rows", ascending=False)
          .head(20).to_string())
