"""Backtest report in the owner's fixed order (2026-10-15). Numbers and pass/fail only; no
interpretation. Written before the run, from the results file's columns.

Order:
  1. The five November verdicts against the pass marks (no-frost version)
  2. The frost version: the five November verdicts with frost (crops 2009–2025), beside the no-frost
     version on the same crops
  3. The three comparison models on identical seasons (November)
  4. Each sensitivity against the headline on the same crops (November)
  5. December and January beside November, not scored
  6. Appendix tables

Run:    .venv/Scripts/python gee/backtest_report.py [label]
Reads:  data/derived/backtest_results_<label>.csv, SPEC_CHANGELOG.md (headings after prereg-1)
Writes: docs/backtest_<label>_results.md
"""
import re
import subprocess
import sys

import numpy as np
import pandas as pd

import backtest as bt
from common import ROOT

ORDER = bt.REGIONS + [bt.TOTAL]
SHORT = {bt.REGIONS[0]: "Sul e Centro-Oeste", bt.REGIONS[1]: "Triângulo, Alto Paranaíba e Noroeste",
         bt.REGIONS[2]: "Zona da Mata, Rio Doce e Central", bt.REGIONS[3]: "São Paulo", bt.TOTAL: "Four-region total"}
SENS_ORDER = ["evi_from_sep", "ndvi", "no_filter", "mapped_area", "persistent_pixel", "chirps_prelim",
              bt.FROST_ALT, "third_survey"]
VERSION = {"no_frost": "without frost", "with_frost": "with frost"}
# Registered statements carried beside the tables (spec §5 steps 6 and 1, Amendment 33; owner)
LABEL_2022 = "Crop 2022 is in-sample: the frost constants were set knowing what the July 2021 frost did (§5 step 6)."
LABEL_2023 = "Crop 2023 may carry 2021 frost effects the model does not represent (§5 step 6)."
LABEL_NDVI = ("The NDVI series carries a 2024–26 drift of unresolved cause (Week 0 drift check); any NDVI-based "
              "result is unreliable for those years (Amendment 33).")
LABEL_SUL2012 = ("Sul e Centro-Oeste crop 2012's flag depends on conventional stations; whether their minima were "
                 "available by the cut is not established (§9; owner, Amendment 41 item 7).")


def f(x, d=1):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def p(x):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.4f}"


def table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def cell(s, **k):
    x = s
    for a, b in k.items():
        x = x[x[a] == b]
    assert len(x) <= 1, k
    return None if x.empty else x.iloc[0]


def vsort(x, by):
    """Sort with vintages in note order and regions in the report order."""
    key = {**{v: i for i, v in enumerate(bt.VINTAGES)}, **{v: i for i, v in enumerate(ORDER)},
           "no_frost": 0, "with_frost": 1}
    return x.sort_values(by, key=lambda c: c if pd.api.types.is_numeric_dtype(c) else c.map(lambda v: key.get(v, 99)))


def scored(res, **k):
    x = res[res.scored]
    for a, b in k.items():
        x = x[x[a] == b]
    return x


def verdicts(s, version, vintage):
    rows = []
    for r in ORDER:
        c = cell(s, sensitivity="headline", version=version, model="full", vintage=vintage, region=r)
        mk = bt.PASS_MARKS[(version, r)]
        rows.append({"Region": SHORT[r], "Crops": c.crops, "Hits": f"{int(c.hits_condition)} of {c.n}",
                     "Mark": f"{mk[0]} of {mk[1]}", "Verdict": c.verdict, "p (coin)": p(c.p_coin),
                     "p (majority)": p(c.p_majority), "Registered share positive": f"{mk[2]:.3f}",
                     "MAE (pp)": f(c.mae_pct), "Yield vs trend hits": f"{int(c.hits_yield_vs_trend)} of {c.n}"})
    return rows


def changes_after_prereg1(commit):
    """SPEC_CHANGELOG entries added between the prereg-1 tag and `commit`: date and bold heading, verbatim."""
    diff = subprocess.run(["git", "diff", "prereg-1", commit, "--", "SPEC_CHANGELOG.md"], capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT).stdout
    entries, cur = [], None
    for line in diff.splitlines():
        if line.startswith("+- 20"):
            if cur:
                entries.append(cur)
            cur = line[1:]
        elif cur is not None and line.startswith("+") and line[1:].strip():
            cur += " " + line[1:].strip()
        elif cur is not None:
            entries.append(cur)
            cur = None
    if cur:
        entries.append(cur)
    heads = []
    for e in entries:
        m = re.match(r"- (\S+) — \*\*(.+?)\*\*", re.sub(r"\s+", " ", e))
        heads.append(f"{m.group(1)}: {m.group(2)}" if m else e[:200])
    return heads


def main(label="v1"):
    res = pd.read_csv(ROOT / "data" / "derived" / f"backtest_results_{label}.csv")
    s = bt.summary(res)
    meta = res.iloc[0]
    L = [f"# Backtest {label}: results", "",
         f"Run commit `{meta.run_commit}`; manifest SHA-256 `{meta.manifest_sha256}`; run {meta.run_utc}; "
         f"headline frost: unresolved stations {'kept at their observed tiers' if meta.headline_frost == 'with' else 'left out'}; "
         f"{len(res):,} rows. Numbers and pass/fail only.", "",
         "Hits are condition-direction hits (sign of actual minus the stage-1 expectation). MAE is the mean absolute "
         "error of the condition anomaly in percentage points of the expectation. p-values are exact one-sided "
         "binomial tails at the observed hits, against a coin flip and against the registered majority share.", ""]

    # 1
    L += ["## 1. November verdicts against the pass marks (without frost)", "",
          table(verdicts(s, "no_frost", "Nov"), ["Region", "Crops", "Hits", "Mark", "Verdict", "p (coin)",
                                                 "p (majority)", "Registered share positive", "MAE (pp)",
                                                 "Yield vs trend hits"]), ""]

    # 2
    rows = verdicts(s, "with_frost", "Nov")
    for row, r in zip(rows, ORDER):
        c = cell(s, sensitivity="headline", version="with_frost", model="full", vintage="Nov", region=r)
        row["Without frost, same crops: hits"] = f"{int(c.comparator_hits_condition)} of {int(c.comparator_n)}"
        row["Without frost, same crops: MAE (pp)"] = f(c.comparator_mae_pct)
    L += ["## 2. The frost version: November verdicts with frost (crops 2009–2025)", "",
          table(rows, ["Region", "Crops", "Hits", "Mark", "Verdict", "p (coin)", "p (majority)", "MAE (pp)",
                       "Without frost, same crops: hits", "Without frost, same crops: MAE (pp)"]), "",
          f"- {LABEL_2022}", f"- {LABEL_2023}", ""]

    # 3
    L += ["## 3. The three comparison models on identical seasons (November)", "",
          "Zero anomaly: the condition anomaly predicted as 0 (the MAE baseline). Biennial only: the stage-1 "
          "expectation alone, scored on yield versus trend. Rain only: the expectation plus flowering rain alone. "
          "Every model is scored on the same region-crops as the full model.", ""]
    for version in ("no_frost", "with_frost"):
        rows = []
        for r in ORDER:
            g = {m: scored(res, sensitivity="headline", version=version, model=m, vintage="Nov", region=r)
                 for m in ("full", "zero", "rain_only")}
            same = all(sorted(g[m].crop) == sorted(g["full"].crop) for m in g)
            c = {m: cell(s, sensitivity="headline", version=version, model=m, vintage="Nov", region=r) for m in g}
            n = c["full"].n
            rows.append({"Region": SHORT[r], "Crops": c["full"].crops, "Identical crops": "yes" if same else "NO",
                         "Full: hits": f"{int(c['full'].hits_condition)} of {n}", "Full: MAE": f(c["full"].mae_pct),
                         "Full: yield vs trend": f"{int(c['full'].hits_yield_vs_trend)} of {n}",
                         "Zero anomaly: MAE": f(c["zero"].mae_pct),
                         "Biennial only: yield vs trend": f"{int(c['zero'].hits_yield_vs_trend)} of {n}",
                         "Rain only: hits": f"{int(c['rain_only'].hits_condition)} of {n}",
                         "Rain only: MAE": f(c["rain_only"].mae_pct),
                         "Rain only: yield vs trend": f"{int(c['rain_only'].hits_yield_vs_trend)} of {n}"})
        L += [f"### {VERSION[version].capitalize()}", "",
              table(rows, ["Region", "Crops", "Identical crops", "Full: hits", "Full: MAE", "Full: yield vs trend",
                           "Zero anomaly: MAE", "Biennial only: yield vs trend", "Rain only: hits", "Rain only: MAE",
                           "Rain only: yield vs trend"]), ""]

    # 4
    L += ["## 4. Each sensitivity against the headline on the same crops (November, full model)", "",
          "Each row compares the sensitivity with the headline on exactly the sensitivity's region-crops. "
          "Third survey: the full model and the biennial-only model, because it changes the expectation.", ""]
    for sens in SENS_ORDER:
        rows = []
        for version in ("no_frost", "with_frost"):
            for model in (("full", "zero") if sens == "third_survey" else ("full",)):
                for r in ORDER:
                    c = cell(s, sensitivity=sens, version=version, model=model, vintage="Nov", region=r)
                    if c is None:
                        continue
                    rows.append({"Version": VERSION[version], "Model": "biennial only" if model == "zero" else model,
                                 "Region": SHORT[r], "Crops": c.crops, "n": c.n,
                                 "Hits": "" if model == "zero" else f"{int(c.hits_condition)}",
                                 "Headline hits": "" if model == "zero" else f"{int(c.comparator_hits_condition)}",
                                 "MAE (pp)": f(c.mae_pct), "Headline MAE (pp)": f(c.comparator_mae_pct),
                                 "Yield vs trend hits": int(c.hits_yield_vs_trend),
                                 "Headline yield vs trend hits": int(c.comparator_hits_yield_vs_trend),
                                 "Headline n": int(c.comparator_n)})
        L += [f"### {sens}", ""]
        if sens == "ndvi":
            L += [f"- {LABEL_NDVI}", ""]
        if not rows:
            L += ["No scored rows.", ""]
            continue
        L += [table(rows, ["Version", "Model", "Region", "Crops", "n", "Headline n", "Hits", "Headline hits",
                           "MAE (pp)", "Headline MAE (pp)", "Yield vs trend hits", "Headline yield vs trend hits"]), ""]

    # 5
    L += ["## 5. December and January beside November (headline, full model)", "",
          "November decides pass or fail (Amendment 41). December and January are reported against the same "
          "marks and are not scored.", ""]
    for version in ("no_frost", "with_frost"):
        rows = []
        for r in ORDER:
            mk = bt.PASS_MARKS[(version, r)]
            row = {"Region": SHORT[r], "Mark": f"{mk[0]} of {mk[1]}"}
            for v in bt.VINTAGES:
                c = cell(s, sensitivity="headline", version=version, model="full", vintage=v, region=r)
                row[f"{v}: hits"] = f"{int(c.hits_condition)} of {c.n}"
                row[f"{v}: MAE"] = f(c.mae_pct)
                row[f"{v}: p (coin / majority)"] = f"{p(c.p_coin)} / {p(c.p_majority)}"
                row[f"{v}: verdict"] = c.verdict if v == bt.GOVERNING_VINTAGE else "not scored"
            rows.append(row)
        cols = ["Region", "Mark"] + [f"{v}: {k}" for v in bt.VINTAGES for k in ("hits", "MAE", "p (coin / majority)",
                                                                              "verdict")]
        L += [f"### {VERSION[version].capitalize()}", "", table(rows, cols), ""]

    # 6 Appendix
    L += ["## 6. Appendix", ""]
    # A1 residuals
    rz = bt.residuals(res)
    rows = [{"Version": VERSION[q.version], "Vintage": q.vintage, "Region": SHORT[q.region], "n": q.n,
             "Mean signed residual (pp)": f(q.mean_signed), "Mean absolute residual (pp)": f(q.mean_abs)}
            for q in rz.sort_values(["version", "vintage", "region"],
                                    key=lambda c: c.map({**{v: i for i, v in enumerate(["no_frost", "with_frost"])},
                                                         **{v: i for i, v in enumerate(bt.VINTAGES)},
                                                         **{v: i for i, v in enumerate(ORDER)}})).itertuples()]
    L += ["### A1. Per-region residuals under the pooled weights (headline, full model; actual minus predicted)", "",
          table(rows, ["Version", "Vintage", "Region", "n", "Mean signed residual (pp)",
                       "Mean absolute residual (pp)"]), ""]
    # A2 crops 2022 and 2025
    rows = []
    for crop in (2022, 2025):
        for version in ("no_frost", "with_frost"):
            for r in ORDER:
                row = {"Crop": crop, "Version": VERSION[version], "Region": SHORT[r]}
                for v in bt.VINTAGES:
                    q = cell(res, sensitivity="headline", version=version, model="full", vintage=v, region=r, crop=crop)
                    if q is None:
                        continue
                    row["Actual (%)"] = f(100 * q.a_actual)
                    row[f"{v}: predicted (%)"] = f(100 * q.a_pred)
                    row[f"{v}: hit"] = "yes" if q.hit_condition else "no"
                rows.append(row)
    L += ["### A2. Crops 2022 and 2025 (headline, full model; condition anomaly in % of the expectation)", "",
          f"- {LABEL_2022}", "",
          table(rows, ["Crop", "Version", "Region", "Actual (%)"] + [f"{v}: {k}" for v in bt.VINTAGES
                                                                   for k in ("predicted (%)", "hit")]), ""]
    # A3 double counting
    h = res[(res.sensitivity == "headline") & (res.model == "full") & (res.version == "with_frost")]
    sel = h[(h.penalty > 0) | h.crop.isin([2022, 2023])]
    rows = [{"Region": SHORT[q.region], "Crop": int(q.crop), "Vintage": q.vintage, "Frost penalty (%)": f(100 * q.penalty),
             "Actual (%)": f(100 * q.a_actual), "Predicted with frost (%)": f(100 * q.a_pred),
             "Predicted without the frost component (%)": f(100 * q.a_pred_no_frost)}
            for q in vsort(sel, ["crop", "region", "vintage"]).itertuples()]
    L += ["### A3. Double-counting check: frost-flagged region-crops, and crops 2022 and 2023 (with-frost version)", "",
          f"- {LABEL_2022}", f"- {LABEL_2023}", f"- {LABEL_SUL2012}", "",
          table(rows, ["Region", "Crop", "Vintage", "Frost penalty (%)", "Actual (%)", "Predicted with frost (%)",
                       "Predicted without the frost component (%)"]), ""]
    # A4 surprise test
    sv = res[res.surprise_pred.notna()].copy()
    rows = [{"Version": VERSION[q.version], "Region": SHORT[q.region], "Crop": int(q.crop), "Vintage": q.vintage,
             "First survey yield": f(q.y_first, 2), "Final yield": f(q.y, 2), "Predicted revision": int(q.surprise_pred),
             "Actual revision": int(q.surprise_actual),
             "Hit": "flat" if q.surprise_actual == 0 else ("yes" if q.surprise_pred == q.surprise_actual else "no")}
            for q in vsort(sv, ["version", "crop", "region", "vintage"]).itertuples()]
    base = sv.drop_duplicates(["region", "crop"])
    L += ["### A4. Surprise test, safras 2023–2025 (reported, not scored; Amendment 19b)", "",
          f"Region-crops with both a first and a final survey: {len(base)}; revised up: "
          f"{int((base.surprise_actual > 0).sum())}; down: {int((base.surprise_actual < 0).sum())}; "
          f"flat (under 1%): {int((base.surprise_actual == 0).sum())}. Revision signs: +1 up, −1 down, 0 flat.", "",
          table(rows, ["Version", "Region", "Crop", "Vintage", "First survey yield", "Final yield",
                       "Predicted revision", "Actual revision", "Hit"]), ""]
    # A5 frost coverage
    fr = res[(res.sensitivity == "headline") & (res.model == "full") & (res.version == "with_frost")
             & (res.vintage == "Nov")].drop_duplicates(["region", "crop"])
    rows = [{"Region": SHORT[q.region], "Crop": int(q.crop), "Automatic": f(q.automatic_stations, 0),
             "Conventional": f(q.conventional_stations, 0), "Unresolved": f(q.unresolved_stations, 0),
             "Observed coverage, headline (%)": f(100 * q.observed_coverage, 1),
             "Unflaggable, headline": "" if pd.isna(q.unflaggable) else q.unflaggable,
             "Observed coverage, other variant (%)": f(100 * q.observed_coverage_alt, 1),
             "Unflaggable, other variant": "" if pd.isna(q.unflaggable_alt) else q.unflaggable_alt, "Penalty (%)": f(100 * q.penalty)}
            for q in fr.sort_values(["region", "crop"], key=lambda c: c.map({v: i for i, v in enumerate(ORDER)})
                                    if c.name == "region" else c).itertuples()]
    L += ["### A5. Frost stations, observed coverage and penalty per region and crop (§5 step 4)", "",
          table(rows, ["Region", "Crop", "Automatic", "Conventional", "Unresolved", "Observed coverage, headline (%)",
                       "Unflaggable, headline", "Observed coverage, other variant (%)", "Unflaggable, other variant",
                       "Penalty (%)"]), ""]
    # A6 lambda and weights
    w = res[(res.sensitivity == "headline") & (res.model == "full") & (res.vintage == "Nov")
            & (res.region == bt.REGIONS[0])].sort_values(["version", "crop"])
    rows = [{"Version": VERSION[q.version], "Held-out crop": int(q.crop), "λ": f"{q.lam:g}", "Intercept": f(q.intercept, 4),
             "Training rows": int(q.n_train), **{f"w {k}": f(getattr(q, f"w_{k}"), 4) for k in bt.INPUTS}}
            for q in w.itertuples()]
    L += ["### A6. Fitted λ, intercept and weights per fold (headline, full model, November)", "",
          "Weights are per unit of each registered input as stored in the season inputs.", "",
          table(rows, ["Version", "Held-out crop", "λ", "Intercept", "Training rows"] + [f"w {k}" for k in bt.INPUTS]),
          ""]
    # A7 prelim substitution counts
    pr = res[(res.sensitivity == "chirps_prelim") & (res.model == "full") & (res.version == "no_frost")
             & (res.region == bt.REGIONS[0])].sort_values(["crop", "vintage"])
    rows = [{"Held-out crop": int(q.crop), "Vintage": q.vintage, "Municipalities on prelim": f(q.n_prelim_substituted, 0),
             "Left on final (no prelim row)": f(q.n_prelim_left_final, 0)} for q in vsort(pr, ["crop", "vintage"]).itertuples()]
    L += ["### A7. CHIRPS prelim rerun: municipality-seasons substituted per held-out crop and vintage", "",
          table(rows, ["Held-out crop", "Vintage", "Municipalities on prelim", "Left on final (no prelim row)"]), ""]
    # A8 changes after prereg-1 (§9), the changelog headings verbatim
    heads = changes_after_prereg1(meta.run_commit)
    L += ["### A8. Changes after `prereg-1` (§9): SPEC_CHANGELOG headings", ""] + [f"- {x}" for x in heads] + [""]
    out = ROOT / "docs" / f"backtest_{label}_results.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(main(*(sys.argv[1:] or ["v1"])))
