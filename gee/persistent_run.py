"""Persistent-pixel sensitivity inputs, computed under the watchdog before the single backtest run
(Amendment 41; the mask of Amendment 16b: pixels classified 46 in the mask year and the two before).

Serial tasks through gee/ee_watchdog.py (60-second poll, cancelled at 2 × the estimate), in order:
  1. weights probe: mesoregion 3505, the cheapest W1 weights export (405 EECU-seconds); estimate
     1.5 × its W1 cost. The ratio of its measured cost to W1's sets the other estimates.
  2. the other 23 mesoregions' persistent weights (`w1_pweights_meso_<code>`, bands `w_M` as in W1):
     estimate = W1's measured cost × the ratio.
  3. EVI probe: Sul e Centro-Oeste, calendar 2021, with W1's sanity check; estimate 1.2 × W1's 257.
  4. the four regions' per-municipality EVI/NDVI series on persistent weights: estimate = W1's
     measured cost × the probe ratio.
The session cap is set at 1.5 × the starting estimate, then reset after the probes to 1.5 × (spent +
remaining), as in gee/w1_run.py. The driver stops at the first cancelled or failed task. --resume
skips tasks already completed in docs/week0/persistent_task_costs.csv.

The rain, soil-moisture and heat exports on persistent weights run afterwards through
gee/w2_exports.py --persistent, each with its probe.

Run:    .venv/Scripts/python gee/persistent_run.py [--resume]
Writes: docs/week0/persistent_task_costs.csv, data/derived/w1p_series_muni_<region>.csv
"""
import datetime as dt
import json
import sys

import pandas as pd

import ee_watchdog as wd
import w1_mask
import w1_modis_evi as evi
from common import ROOT, WEEK0, init
from w1_run import REGIONS, probe_ok

COSTS = WEEK0 / "persistent_task_costs.csv"
PROBE_MESO = "3505"
W1_PROBE = 257.0
PREFIX = "w1_pweights_meso_"
_rows = []


def record(task, region, estimate, state, used):
    _rows.append(dict(time_utc=f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S}", task=task, region=region,
                      estimate_eecu_s=round(estimate), cancel_at_eecu_s=round(2 * estimate),
                      measured_eecu_s=round(used, 1), state=state))
    pd.DataFrame(_rows).to_csv(COSTS, index=False)
    if state not in ("COMPLETED", "SUCCEEDED"):
        raise SystemExit(f"stopping: {task} ended {state} at {used:,.0f} EECU-s")


def main():
    project = init()
    resume = "--resume" in sys.argv
    w1 = pd.read_csv(WEEK0 / "w1_task_costs.csv")
    w1c = dict(zip(w1.task, w1.measured_eecu_s))
    member = w1_mask.meso_table()
    mesos = {r: sorted(member.query("conab_region == @r").meso_code.unique()) for r in REGIONS}
    done = set()
    if resume and COSTS.exists():
        prior = pd.read_csv(COSTS)
        _rows.extend(prior.to_dict("records"))
        done = set(prior[prior.state.isin(["COMPLETED", "SUCCEEDED"])].task)
    else:
        start = 1.5 * sum(v for k, v in w1c.items() if k.startswith("w1_weights_meso")) + \
            sum(v for k, v in w1c.items() if k.startswith("w1_series_muni")) + 1.5 * w1c[f"w1_weights_meso_{PROBE_MESO}"]
        wd.set_session_cap("persistent_pixel", 1.5 * start)

    def done_cost(task):
        return float(pd.DataFrame(_rows).query("task == @task").measured_eecu_s.iloc[-1])

    # 1. weights probe
    t = f"w1_pweights_meso_{PROBE_MESO}"
    if t not in done:
        est = 1.5 * w1c[f"w1_weights_meso_{PROBE_MESO}"]
        state, used = w1_mask.weights(project, PROBE_MESO, est, persistent=True)
        record(t, "São Paulo (state total)", est, state, used)
    ratio_w = done_cost(t) / w1c[f"w1_weights_meso_{PROBE_MESO}"]
    wd._log(f"persistent weights cost ratio to W1: {ratio_w:.2f}")

    # 3. EVI probe (before the other weights would also be possible; run after Sul's weights exist)
    sul = REGIONS[0]
    for m in mesos[sul]:
        t = f"w1_pweights_meso_{m}"
        if t not in done and t != f"w1_pweights_meso_{PROBE_MESO}":
            est = max(50.0, w1c[f"w1_weights_meso_{m}"] * ratio_w)
            state, used = w1_mask.weights(project, m, est, persistent=True)
            record(t, sul, est, state, used)
    probe_name = f"w1p_full_probe_{evi.slug_of(sul)}_2021"
    if probe_name not in done:
        est = 1.2 * W1_PROBE
        fc = evi.run_full(project, sul, "2021-01-01", "2022-01-01", weights_prefix=PREFIX)
        df, used = wd.export_table_watched(fc, probe_name, evi.full_selectors(), est)
        record(probe_name, sul, est, "COMPLETED" if df is not None else "FAILED", used)
        df.to_csv(WEEK0 / f"{probe_name}.csv", index=False)
    df = pd.read_csv(WEEK0 / f"{probe_name}.csv", dtype={"code": str})
    if not probe_ok(df):
        raise SystemExit("stopping: the persistent EVI probe failed its sanity check")
    ratio_c = done_cost(probe_name) / W1_PROBE

    # reset the cap from the measured ratios
    remaining = sum(max(50.0, w1c[f"w1_weights_meso_{m}"] * ratio_w) for r in REGIONS for m in mesos[r]
                    if f"w1_pweights_meso_{m}" not in set(pd.DataFrame(_rows).task))
    remaining += sum(w1c[f"w1_series_muni_{evi.slug_of(r)}"] * ratio_c for r in REGIONS)
    led = wd._ledger()
    led["cap"] = 1.5 * (led.get("spent", 0.0) + remaining)
    wd.LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")
    wd._log(f"estimates reset: weights ratio {ratio_w:.2f}, composites ratio {ratio_c:.2f}; "
            f"session cap {led['cap']:,.0f} EECU-s")

    # 2 and 4. region by region: weights, then the per-municipality series
    for r in REGIONS:
        for m in mesos[r]:
            t = f"w1_pweights_meso_{m}"
            if t in set(pd.DataFrame(_rows).query("state == 'COMPLETED'").task):
                continue
            est = max(50.0, w1c[f"w1_weights_meso_{m}"] * ratio_w)
            state, used = w1_mask.weights(project, m, est, persistent=True)
            record(t, r, est, state, used)
        name = f"w1p_series_muni_{evi.slug_of(r)}"
        if name in done:
            continue
        est = w1c[f"w1_series_muni_{evi.slug_of(r)}"] * ratio_c
        df, used = wd.export_table_watched(evi.run_full(project, r, weights_prefix=PREFIX), name,
                                           evi.full_selectors(), est)
        record(name, r, est, "COMPLETED" if df is not None else "FAILED", used)
        df.to_csv(ROOT / "data" / "derived" / f"{name}.csv", index=False)
        wd._log(f"{r}: {len(df):,} municipality-composites, {df.code.nunique()} municipalities")
    wd._log(f"persistent-pixel inputs done: session spend {wd.session_spent():,.0f} EECU-s")


if __name__ == "__main__":
    main()
