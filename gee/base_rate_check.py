"""Base-rate check on the direction pass marks (§5 step 8; prereg-2), run before any season-level
index input exists. Uses Conab yields only; no Earth Engine call.

Condition direction is the sign of actual yield minus the stage-1 expectation. Stage 1 per region:
intercept, linear trend, and a coefficient on crop S−1's yield anomaly (§5 steps 6–7; prereg-1 D),
fitted leave-one-season-out. With a free linear trend, a coefficient on S−1's anomaly from a
linear trend equals a coefficient on S−1's yield, so stage 1 is fitted as OLS of y_S on
(1, S, y_{S−1}).

Stage-1 details not fixed at prereg-1 are run as variants, to show whether the base rate depends
on them:
  joint_drop_S      OLS of y_S on (1, S, y_{S−1}) without season S's row
  joint_drop_S_S1   as above, also without season S+1's row (where y_S is the lagged regressor)
  twostep_drop_S    linear trend on y, then the residual on the lagged residual (no intercept),
                    without season S
  in_sample         all seasons (reference only)

Pass-mark rule (§5 step 8): if the share of positive condition anomalies is away from 50%, each
mark becomes the larger of its registered value and the smallest count k with
P(X ≥ k | n, q) < 0.05, where q is the majority share.

Series (Amendment 19b): Sul e Centro-Oeste, Triângulo and São Paulo from the arabica-plus-conilon
series for 2001–2007 and arabica from 2008; Zona da Mata arabica from 2008; the four-region total
as four-unit production over four-unit area, from 2008 (Amendment 37).

Run:    .venv/Scripts/python gee/base_rate_check.py
Writes: docs/week0/base_rate_check.csv, docs/week0/stage1_seasons.csv
"""
from math import comb

import numpy as np
import pandas as pd

from common import ROOT, WEEK0

REGIONS = ["Sul e Centro-Oeste", "Triângulo, Alto Paranaíba e Noroeste", "São Paulo (state total)",
           "Zona da Mata, Rio Doce e Central"]
TOTAL = "Four-region total"
REGISTERED = {  # (first, last, registered mark, n registered)
    "without frost, Sul/Tri/SP": ((2001, 2025), 18, 25),
    "without frost, ZM and total": ((2008, 2025), 13, 18),
    "with frost": ((2009, 2025), 13, 17),
}


def series():
    d = pd.read_csv(ROOT / "data" / "derived" / "conab_regional.csv")
    h = d[d.vintage.str.startswith("historical") & (d.column == "historical series")]
    out = {}
    for r in REGIONS:
        a = h[(h.region == r) & (h["product"] == "arabica")].set_index("safra")
        t = h[(h.region == r) & (h["product"] == "total")].set_index("safra")
        rows = []
        for s in range(2001, 2026):
            src = a if s >= 2008 else (t if r != REGIONS[3] else None)
            if src is None or s not in src.index or pd.isna(src.at[s, "area_ha"]):
                continue
            rows.append((s, src.at[s, "area_ha"], src.at[s, "production_kbags"]))
        out[r] = pd.DataFrame(rows, columns=["safra", "area", "prod"]).set_index("safra")
    tot = sum(out[r].loc[2008:2025] for r in REGIONS)
    out[TOTAL] = tot.dropna()
    for r, df in out.items():
        df["y"] = df["prod"] * 1000 / df["area"]
    return out


def fit_predict(y, s, variant):
    """Condition anomaly (actual minus stage-1 expectation) for season s."""
    years = [t for t in y.index if t - 1 in y.index]
    if s not in years:
        return np.nan
    drop = {s, s + 1} if variant == "joint_drop_S_S1" else ({s} if variant != "in_sample" else set())
    if variant == "twostep_drop_S":
        tr = [t for t in y.index if t != s]
        b = np.polyfit(tr, y.loc[tr].values, 1)
        resid = y - np.polyval(b, y.index.values)
        rows = [t for t in years if t != s and t - 1 != s]
        c = np.dot(resid.loc[[t - 1 for t in rows]].values, resid.loc[rows].values) / np.dot(
            resid.loc[[t - 1 for t in rows]].values, resid.loc[[t - 1 for t in rows]].values)
        return y.at[s] - (np.polyval(b, s) + c * resid.at[s - 1])
    rows = [t for t in years if t not in drop]
    X = np.column_stack([np.ones(len(rows)), rows, y.loc[[t - 1 for t in rows]].values])
    beta = np.linalg.lstsq(X, y.loc[rows].values, rcond=None)[0]
    return y.at[s] - beta @ np.array([1.0, s, y.at[s - 1]])


def tail(k, n, q):
    """P(X >= k) for X ~ Binomial(n, q), exact."""
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def mark(n, q):
    """Smallest k with P(X >= k | n, q) < 0.05."""
    for k in range(n + 1):
        if tail(k, n, q) < 0.05:
            return k, tail(k, n, q)
    return None, None


def main():
    ys = series()
    variants = ["joint_drop_S", "joint_drop_S_S1", "twostep_drop_S", "in_sample"]
    seasons, rows = [], []
    for r, df in ys.items():
        for s in df.index:
            seasons.append(dict(region=r, safra=s, yield_sc_ha=round(df.at[s, "y"], 2),
                                **{v: fit_predict(df["y"], s, v) for v in variants}))
    sdf = pd.DataFrame(seasons)
    sdf.to_csv(WEEK0 / "stage1_seasons.csv", index=False, float_format="%.3f")
    for name, ((a, b), reg_mark, reg_n) in REGISTERED.items():
        regs = (["Sul e Centro-Oeste", "Triângulo, Alto Paranaíba e Noroeste", "São Paulo (state total)"]
                if "Sul/Tri/SP" in name else [REGIONS[3], TOTAL] if "ZM" in name else REGIONS + [TOTAL])
        for r in regs:
            d = sdf[(sdf.region == r) & sdf.safra.between(a, b)]
            for v in variants:
                x = d[v].dropna()
                n, pos = len(x), int((x > 0).sum())
                q = max(pos, n - pos) / n
                k_maj, p_maj = mark(n, q)
                k_coin, p_coin = mark(n, 0.5)
                rows.append(dict(pass_mark=name, region=r, variant=v, seasons_registered=reg_n,
                                 seasons_computable=n, first=int(x.index.size and d.loc[x.index, "safra"].min()),
                                 positive=pos, share_positive=round(pos / n, 3),
                                 registered_mark=f"{reg_mark}/{reg_n}",
                                 coin_mark=f"{k_coin}/{n}", coin_p=round(p_coin, 4),
                                 majority_mark=f"{k_maj}/{n}", majority_p=round(p_maj, 4),
                                 mark_under_rule=f"{max(k_coin, k_maj)}/{n}"))
    out = pd.DataFrame(rows)
    out.to_csv(WEEK0 / "base_rate_check.csv", index=False)
    return out, sdf


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    out, sdf = main()
    print(out[out.variant != "in_sample"].to_string(index=False))
