"""Backtest by note date (§5 steps 6–8; prereg-1 and prereg-2 as amended, Amendments 35–40).
One run writes one results file. Inputs do not change after the run; a corrected run after an input
bug is a second, labelled result (owner, 2026-10-15).

Reads only files listed in data/derived/w2_inputs_manifest.csv, after checking each SHA-256; every
pandas read in this process is checked against the manifest.

Folds (§5 step 8): leave one crop out, in all four regions at once. For each held-out crop S,
everything fitted is refitted without S:
  - the input climatologies and z-scores, municipal and regional (gee/w2_season_inputs.py with
    exclude=S: municipal means, regional means and standard deviations);
  - stage 1 per region and for the four-region total: the linear trend without S, then the
    coefficient of detrended yield on the previous crop's detrended yield, no intercept, leaving
    out every pair that involves S (Amendment 38);
  - the column standardisation of the pooled inputs, the ridge penalty (inner leave-one-crop-out
    over the training crops, grid of prereg-1 item 13, lowest mean squared error, ties to the
    larger λ) and the four weights.
  Inner-loop simplification (stated, not registered): the inner loop that chooses λ reuses the
  outer fold's inputs and stage-1 anomalies; it does not refit climatologies per inner crop. The
  held-out crop S never enters it.

Model (§5 step 6):
  condition anomaly   a = actual / expectation − 1 (a share of the stage-1 expectation)
  frost offset        p = the region's frost penalty for the crop (w2_frost_region_season.csv,
                      unresolved stations at their observed tiers), a share of yield
  stage 2             ridge of (a + p) on the four inputs, pooled over the four regions, one set
                      of weights; prediction â = −p + b0 + w·x. Without frost, p = 0.
  inputs              evi, rain_flowering, soil_moisture, heat_days: the registered season values
                      for the vintage (EVI from 1 May of S−1; 1 September is a sensitivity)
  four-region total   its own stage 1 on the total's yields; predicted with the pooled weights from
                      its own inputs; not a training row

Versions (§5 step 4, Amendment 38):
  no_frost    trained on every region-crop with an expectation; scored on crops 2002–2025 for Sul,
              Triângulo and São Paulo, 2009–2025 for Zona da Mata and the total
  with_frost  trained and scored on crops 2009–2025 (frost is not filled before crop 2009)

Comparison models (same folds and seasons): zero anomaly (â = 0: the MAE baseline; equals the
biennial-only model, whose yield-versus-trend call is the sign of expectation minus trend);
rain only (the expectation plus flowering rain alone, same ridge machinery).

Sensitivities, reported beside the headline, not scored against pass marks:
  evi_from_sep              EVI composites from 1 Sep of S−1 (prereg-1 item 2)
  ndvi                      NDVI in place of EVI (§5 step 6; unreliable 2024–26, Amendment 33)
  no_filter                 members without the stable filter (Amendment 16d)
  mapped_area               regions aggregated by mapped coffee area (Amendment 16d)
  chirps_prelim             held-out crops 2016–2025: CHC prelim for flowering months not yet final
                            at the cut (final for month M from the 1st of M+2), spread evenly over
                            each pentad's days (§9, Amendment 9)
  frost_without_unresolved  frost penalty without unresolved stations (Amendment 17b)
  third_survey              crops 2024–2025: crop S−1's anomaly from Conab's third survey of S−1
                            (§5 step 7), applied to the held-out expectation only
Not run in this file, because their inputs are not in the manifest: the persistent-pixel mask and
the VJ113A1 vegetation rerun (prereg-2 addenda). The pre-dawn night rule (Amendment 40) leaves the
frost input for crops 2009–2026 unchanged (Week 0 report §19), so it needs no rerun.

Also recorded per row: the prediction without the frost offset (double-counting check, §5 step 6),
the surprise-test call for safras 2023–2025 (reported, not scored, Amendment 19b), and the fitted
λ, intercept and weights.

Run:    .venv/Scripts/python gee/backtest.py
Writes: data/derived/backtest_results_v1.csv (one row per sensitivity × version × model × vintage
        × region × held-out crop)
"""
import hashlib
from math import comb

import numpy as np
import pandas as pd

import w2_season_inputs as wi
from base_rate_check import series as conab_series
from common import ROOT

RUN_LABEL = "v1"
D = ROOT / "data" / "derived"
MANIFEST = D / "w2_inputs_manifest.csv"
OUT = D / f"backtest_results_{RUN_LABEL}.csv"

REGIONS = ["Sul e Centro-Oeste", "Triângulo, Alto Paranaíba e Noroeste", "Zona da Mata, Rio Doce e Central",
           "São Paulo (state total)"]
TOTAL = wi.TOTAL
INPUTS = ["evi", "rain_flowering", "soil_moisture", "heat_days"]
VINTAGES = ["Nov", "Dec", "Jan"]
LAMBDAS = [0.0] + [float(10 ** k) for k in np.arange(-2.0, 3.0001, 0.25)]  # prereg-1 item 13
FROST_FROM = 2009
SCORED = {
    "no_frost": {REGIONS[0]: range(2002, 2026), REGIONS[1]: range(2002, 2026), REGIONS[3]: range(2002, 2026),
                 REGIONS[2]: range(2009, 2026), TOTAL: range(2009, 2026)},
    "with_frost": {r: range(2009, 2026) for r in REGIONS + [TOTAL]},
}
# §5 step 8 (Amendment 38): (mark, seasons, registered share of positive condition anomalies)
PASS_MARKS = {
    ("no_frost", REGIONS[0]): (17, 24, 0.500), ("no_frost", REGIONS[1]): (19, 24, 0.417),
    ("no_frost", REGIONS[3]): (18, 24, 0.458), ("no_frost", REGIONS[2]): (14, 17, 0.412),
    ("no_frost", TOTAL): (13, 17, 0.471),
    ("with_frost", REGIONS[0]): (13, 17, 0.471), ("with_frost", REGIONS[1]): (13, 17, 0.529),
    ("with_frost", REGIONS[3]): (13, 17, 0.529), ("with_frost", REGIONS[2]): (14, 17, 0.412),
    ("with_frost", TOTAL): (13, 17, 0.471),
}
SENSITIVITIES = ["headline", "evi_from_sep", "ndvi", "no_filter", "mapped_area", "chirps_prelim",
                 "frost_without_unresolved"]
PRELIM_CROPS = range(2016, 2026)


# ------------------------------------------------------------------ manifest guard
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def guard_reads():
    """Check every manifest file's SHA-256, then let pandas read only those files in this process."""
    from pathlib import Path

    m = pd.read_csv(MANIFEST)
    allowed = {str((ROOT / p).resolve()).lower() for p in m.path}
    for r in m.itertuples():
        if sha256(ROOT / r.path) != r.sha256:
            raise SystemExit(f"checksum mismatch: {r.path}; inputs are frozen")
    original = pd.read_csv

    def checked(path, *a, **k):
        if str(Path(path).resolve()).lower() not in allowed:
            raise SystemExit(f"read outside the manifest: {path}")
        return original(path, *a, **k)

    pd.read_csv = checked  # the pandas module is shared, so this covers gee/w2_season_inputs.py too
    return m


# ------------------------------------------------------------------ targets and stage 1
def yields():
    s = conab_series()  # Amendment 19b series, as in the registered base-rate check
    return {r: s[r]["y"] for r in REGIONS + [TOTAL]}


def survey_yields(survey, safra):
    """Conab survey `survey` (1 or 3) of `safra`, 'current' column: yield per region and the total."""
    d = pd.read_csv(D / "conab_regional.csv")
    x = d[(d.vintage == f"survey {survey} of safra {safra}") & (d.column == "current") & (d["product"] == "arabica")]
    x = x[x.region.isin(REGIONS)].set_index("region")
    out = {r: x.at[r, "production_kbags"] * 1000 / x.at[r, "area_ha"] for r in REGIONS}
    out[TOTAL] = x.production_kbags.sum() * 1000 / x.area_ha.sum()
    return out


def stage1(y, exclude):
    """Two-step stage 1 (Amendment 38) without crop `exclude`. Returns expectation, trend, coefficient."""
    tr = [t for t in y.index if t != exclude]
    b = np.polyfit(tr, y.loc[tr].values, 1)
    trend = pd.Series(np.polyval(b, y.index.values), index=y.index)
    resid = y - trend
    pairs = [t for t in y.index if t - 1 in y.index and t != exclude and t - 1 != exclude]
    x0, x1 = resid.loc[[t - 1 for t in pairs]].values, resid.loc[pairs].values
    coef = float(x0 @ x1 / (x0 @ x0))
    exp = pd.Series({t: trend[t] + coef * resid[t - 1] for t in y.index if t - 1 in y.index})
    return exp, trend, coef, b


def check_base_rates(ys):
    """The registered shares of positive condition anomalies must be reproduced by this stage 1."""
    for (version, reg), (_, n, share) in PASS_MARKS.items():
        crops = list(SCORED[version][reg])
        pos = 0
        for s in crops:
            e, _, _, _ = stage1(ys[reg], s)
            pos += ys[reg][s] - e[s] > 0
        if len(crops) != n or round(pos / n, 3) != share:
            raise SystemExit(f"stage 1 does not reproduce the registered base rate: {version} {reg} {pos}/{n}")


# ------------------------------------------------------------------ inputs per fold
def prelim_table(crop, vintage):
    """The rain table with crop `crop`'s flowering months not final at the cut replaced by CHC prelim
    pentads spread evenly over the pentad's days (values stored as value × w, like the export)."""
    import datetime as dt
    rain = pd.read_csv(D / "w2_rain_muni.csv", dtype={"code": str})
    pre = pd.read_csv(D / "w2_prelim_muni.csv", dtype={"code": str})
    cut = wi.cut_date(crop, vintage)
    months = [m for m in (9, 10, 11) if cut < dt.date(crop - 1 + (m + 2 > 12), (m + 2 - 1) % 12 + 1, 1)]
    if not months:
        return None, 0
    pre = pre[pre.season == crop].set_index("code")
    idx = rain.index[rain.season == crop]
    replaced = 0
    for i in idx:
        code = rain.at[i, "code"]
        if code not in pre.index:
            continue
        for m in months:
            for a in (1, 6, 11, 16, 21, 26):
                start = dt.date(crop - 1, m, a)
                end = (dt.date(crop - 1, m, a + 5) if a < 26 else
                       dt.date(crop - 1 + (m == 12), m % 12 + 1, 1))
                days = pd.date_range(start, end - dt.timedelta(days=1)).date
                q = pre.at[code, f"q_{start:%m%d}"] / pre.at[code, "w"]
                for d in days:
                    rain.at[i, f"d_{d:%m%d}"] = q / len(days) * rain.at[i, "w"]
        replaced += 1
    return rain, replaced


COLS = ["region", "crop", "vintage", "input", "value"]


def fold_inputs(S, sens, cache):
    """The four inputs for every region, crop and vintage, every fit without crop S. Components that a
    sensitivity does not change are shared with the headline through `cache` (one fold)."""
    mkey = sens if sens in ("no_filter", "mapped_area") else "pam"
    mcfg = {"no_filter": {"filter_rule": False}, "mapped_area": {"weight": "pixels"}}.get(mkey, {})

    def part(name, fn):
        if name not in cache:
            cache[name] = fn()[COLS]
        return cache[name]

    vkey = sens if sens in ("evi_from_sep", "ndvi") else "evi"
    veg = part(("veg", vkey, mkey), lambda: wi.evi(exclude=S, start_month=9 if vkey == "evi_from_sep" else 5,
                                                   index="NDVI" if vkey == "ndvi" else "EVI", mcfg=mcfg)
               .assign(input="evi"))
    if sens == "chirps_prelim":
        def prelim_rain():
            out = []
            for v in VINTAGES:
                table, _ = prelim_table(S, v)
                out.append(wi.windowed("rain", wi.rain_total, "rain_flowering", exclude=S,
                                       vintages={v: wi.VINTAGES[v]}, mcfg=mcfg, table=table))
            return pd.concat(out, ignore_index=True)
        rain = part(("rain", "prelim", mkey), prelim_rain)
    else:
        rain = part(("rain", "final", mkey), lambda: wi.windowed("rain", wi.rain_total, "rain_flowering",
                                                                 exclude=S, mcfg=mcfg))
    soil = part(("soil", mkey), lambda: wi.soil(exclude=S, mcfg=mcfg))
    heat = part(("heat", mkey), lambda: wi.windowed("heat", wi.heat_days, "heat_days", exclude=S, sd_floor=1.0,
                                                    mcfg=mcfg))
    x = pd.concat([veg, rain, soil, heat], ignore_index=True)
    return x.pivot_table(index=["region", "crop", "vintage"], columns="input", values="value")[INPUTS]


# ------------------------------------------------------------------ ridge
def ridge_fit(X, y, lam):
    xm, ym = X.mean(axis=0), y.mean()
    Xc, yc = X - xm, y - ym
    w = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ yc)
    return ym - xm @ w, w


def choose_lambda(X, y, groups):
    best_lam, best_mse = None, np.inf
    for lam in LAMBDAS:
        errs = []
        for g in np.unique(groups):
            tr = groups != g
            b0, w = ridge_fit(X[tr], y[tr], lam)
            errs.append(y[~tr] - b0 - X[~tr] @ w)
        mse = float(np.mean(np.concatenate(errs) ** 2))
        if mse < best_mse - 1e-15 or (abs(mse - best_mse) <= 1e-15 and lam > best_lam):
            best_lam, best_mse = lam, mse
    return best_lam


def fit_predict(train, pred, cols):
    """Standardise columns on training rows, choose λ by inner leave-one-crop-out, fit, predict."""
    mu, sd = train[cols].mean(), train[cols].std(ddof=0)
    Xt = ((train[cols] - mu) / sd).values
    y = (train.a + train.p).values
    lam = choose_lambda(Xt, y, train.crop.values)
    b0, w = ridge_fit(Xt, y, lam)
    Xp = ((pred[cols] - mu) / sd).values
    core = b0 + Xp @ w
    return core, lam, b0, w / sd.values  # weights per unit of the registered input


# ------------------------------------------------------------------ main loop
def run():
    guard_reads()
    ys = yields()
    check_base_rates(ys)
    frost = pd.read_csv(D / "w2_frost_region_season.csv")
    pen = {"with": frost.set_index(["region", "crop"]).penalty_with_unresolved,
           "without": frost.set_index(["region", "crop"]).penalty_without_unresolved}
    third = {s: survey_yields(3, s - 1) for s in (2024, 2025)}
    first = {s: survey_yields(1, s) for s in (2023, 2024, 2025)}
    folds = sorted(set().union(*[set(c) for v in SCORED.values() for c in v.values()]))
    rows = []
    for S in folds:
        st1 = {r: stage1(ys[r], S) for r in REGIONS + [TOTAL]}
        cache = {}
        for sens in SENSITIVITIES:
            if sens == "chirps_prelim" and S not in PRELIM_CROPS:
                continue  # the prelim rerun covers held-out crops whose cuts fall in CHC's archive
            X = fold_inputs(S, "headline" if sens == "frost_without_unresolved" else sens, cache)
            for version in ("no_frost", "with_frost"):
                if version == "no_frost" and sens == "frost_without_unresolved":
                    continue
                pens = pen["without" if sens == "frost_without_unresolved" else "with"]
                for v in VINTAGES:
                    recs = []
                    for r in REGIONS + [TOTAL]:
                        e, trend, _, _ = st1[r]
                        for c in e.index:
                            if (r, c, v) not in X.index:
                                continue
                            if version == "with_frost" and c < FROST_FROM:
                                continue
                            p = float(pens.get((r, c), np.nan)) if version == "with_frost" else 0.0
                            recs.append(dict(region=r, crop=c, a=ys[r][c] / e[c] - 1, p=p, E=e[c], T=trend[c],
                                             y=ys[r][c], **X.loc[(r, c, v)].to_dict()))
                    d = pd.DataFrame(recs).dropna(subset=INPUTS + ["p"])
                    train = d[(d.crop != S) & d.region.isin(REGIONS)]
                    pred = d[d.crop == S]
                    if pred.empty:
                        continue
                    for model, cols in (("full", INPUTS), ("rain_only", ["rain_flowering"])):
                        core, lam, b0, w = fit_predict(train, pred, cols)
                        weights = dict(zip(cols, w))
                        for (_, q), c0 in zip(pred.iterrows(), core):
                            rows.append(dict(
                                run=RUN_LABEL, sensitivity=sens, version=version, model=model, vintage=v,
                                region=q.region, crop=S, scored=S in SCORED[version][q.region],
                                y=q.y, E=q.E, T=q["T"], a_actual=q.a, a_pred=c0 - q.p, a_pred_no_frost=c0,
                                penalty=q.p, lam=lam, intercept=b0, n_train=len(train),
                                **{f"w_{k}": weights.get(k, np.nan) for k in INPUTS},
                                **{f"x_{k}": q[k] for k in INPUTS}))
                    if sens == "headline":
                        for _, q in pred.iterrows():
                            rows.append(dict(run=RUN_LABEL, sensitivity="headline", version=version, model="zero",
                                             vintage=v, region=q.region, crop=S,
                                             scored=S in SCORED[version][q.region], y=q.y, E=q.E, T=q["T"],
                                             a_actual=q.a, a_pred=0.0, a_pred_no_frost=0.0, penalty=q.p))
        print(f"fold {S} done", flush=True)
    res = pd.DataFrame(rows)
    # third-survey sensitivity: the held-out expectation from Conab's third survey of S−1
    extra = []
    for S, y3 in third.items():
        for r in REGIONS + [TOTAL]:
            _, trend, coef, _ = stage1(ys[r], S)
            e3 = trend[S] + coef * (y3[r] - trend[S - 1])
            h = res[(res.sensitivity == "headline") & (res.crop == S) & (res.region == r) & res.model.isin(["full", "zero"])]
            for _, q in h.iterrows():
                q = q.copy()
                q["sensitivity"], q["E"], q["a_actual"] = "third_survey", e3, ys[r][S] / e3 - 1
                extra.append(q)
    res = pd.concat([res, pd.DataFrame(extra)], ignore_index=True)
    # surprise test, safras 2023–2025: reported, not scored
    res["y_first"] = np.nan
    res["surprise_pred"] = np.nan
    res["surprise_actual"] = np.nan
    for S, y1 in first.items():
        m = (res.crop == S) & (res.sensitivity == "headline") & (res.model == "full")
        for i in res.index[m]:
            r = res.at[i, "region"]
            a_first = y1[r] / res.at[i, "E"] - 1
            res.at[i, "y_first"] = y1[r]
            res.at[i, "surprise_pred"] = np.sign(res.at[i, "a_pred"] - a_first)
            rev = ys[r][S] - y1[r]
            res.at[i, "surprise_actual"] = 0.0 if abs(rev) < 0.01 * y1[r] else np.sign(rev)
    res["hit_condition"] = np.sign(res.a_pred) == np.sign(res.a_actual)
    res["yvt_actual"] = np.sign(res.y - res["T"])
    res["yvt_pred"] = np.sign(res.E * (1 + res.a_pred) - res["T"])
    res["hit_yield_vs_trend"] = res.yvt_pred == res.yvt_actual
    res.to_csv(OUT, index=False, float_format="%.6f")
    return res


# ------------------------------------------------------------------ summaries (from the results file)
def tail(k, n, q):
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def summary(res):
    """Per sensitivity, version, model, vintage and region, over the scored crops: condition-direction
    hits (not for the zero model, whose call is no direction), mean absolute error of the condition
    anomaly in percentage points of the expectation, and yield-versus-trend hits. For the headline
    full model, the registered pass mark, pass or fail, and both exact p-values (Amendment 38)."""
    rows = []
    keys = ["sensitivity", "version", "model", "vintage", "region"]
    for k, x in res[res.scored].groupby(keys):
        rec = dict(zip(keys, k))
        rec.update(n=len(x), crops=f"{x.crop.min()}-{x.crop.max()}",
                   hits_condition=np.nan if rec["model"] == "zero" else int(x.hit_condition.sum()),
                   mae_pct=100 * (x.a_pred - x.a_actual).abs().mean(),
                   hits_yield_vs_trend=int(x.hit_yield_vs_trend.sum()))
        mk = PASS_MARKS.get((rec["version"], rec["region"]))
        if rec["sensitivity"] == "headline" and rec["model"] == "full" and mk:
            h = int(rec["hits_condition"])
            rec.update(mark=f"{mk[0]}/{mk[1]}", passed=h >= mk[0] and len(x) == mk[1],
                       p_coin=tail(h, len(x), 0.5), p_majority=tail(h, len(x), max(mk[2], 1 - mk[2])))
        rows.append(rec)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    res = run()
    print(summary(res).to_string())
