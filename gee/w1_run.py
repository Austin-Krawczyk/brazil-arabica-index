"""W1 driver (owner go-ahead, 2026-10-14): Sul weights, Sul 2021 probe, estimates reset from the
measured costs, then region by region. Every task runs serially through gee/ee_watchdog.py
(60-second poll, cancelled at 2 × its estimate). New tasks stop once the session's measured spend
passes 1.5 × the total W1 estimate. The driver stops at the first cancelled or failed task, or if
the probe's output fails its sanity check.

Estimates:
  weights     a mesoregion's export box (km²) × 28 bands × the rate per km²-band. The rate starts
              at Sul's single-band export (149 EECU-s over a 126,827 km² box) and is reset from
              Sul's two measured mesoregion exports.
  composites  the measured Sul 2021 probe × (region area / Sul area) × 26 years.

Run:    .venv/Scripts/python gee/w1_run.py
Writes: docs/week0/w1_task_costs.csv (one row per task: estimate, cap, measured cost, state),
        data/derived/w1_series_muni_<region>.csv
"""
import datetime as dt
import json
import math

import ee
import pandas as pd

import ee_watchdog as wd
import w1_mask
import w1_modis_evi as evi
from common import ROOT, WEEK0, init

REGIONS = ["Sul e Centro-Oeste", "Triângulo, Alto Paranaíba e Noroeste",
           "Zona da Mata, Rio Doce e Central", "São Paulo (state total)"]
AREA_KM2 = {"Sul e Centro-Oeste": 73816, "Triângulo, Alto Paranaíba e Noroeste": 153432,
            "Zona da Mata, Rio Doce e Central": 161800, "São Paulo (state total)": 248834}
YEARS = 26
BANDS = 28
COSTS = WEEK0 / "w1_task_costs.csv"
_rows = []


def meso_boxes():
    member = w1_mask.meso_table()
    boxes = {}
    for uf in ("31", "35"):
        mesh = json.loads((ROOT / "data" / "raw" / "ibge" / f"malha_municipios_{uf}_intermediaria.geojson")
                          .read_text(encoding="utf-8"))
        meso_of = dict(zip(member.code, member.meso_code))
        for f in mesh["features"]:
            m = meso_of.get(f["properties"]["codarea"])
            if m is None:
                continue
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            xs = [p[0] for poly in polys for p in poly[0]]
            ys = [p[1] for poly in polys for p in poly[0]]
            b = boxes.setdefault(m, [999, 999, -999, -999])
            b[0], b[1], b[2], b[3] = min(b[0], min(xs)), min(b[1], min(ys)), max(b[2], max(xs)), max(b[3], max(ys))
    r = 6371.0088
    return {m: r * r * math.radians(b[2] - b[0]) * (math.sin(math.radians(b[3])) - math.sin(math.radians(b[1])))
            for m, b in boxes.items()}


def record(task, region, estimate, state, used):
    _rows.append(dict(time_utc=f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S}", task=task, region=region,
                      estimate_eecu_s=round(estimate), cancel_at_eecu_s=round(2 * estimate),
                      measured_eecu_s=round(used, 1), state=state))
    pd.DataFrame(_rows).to_csv(COSTS, index=False)
    if state not in ("COMPLETED", "SUCCEEDED"):
        raise SystemExit(f"stopping: {task} ended {state} at {used:,.0f} EECU-s")


def main():
    project = init()
    member = w1_mask.meso_table()
    mesos = {r: sorted(member.query("conab_region == @r").meso_code.unique()) for r in REGIONS}
    box = meso_boxes()
    rate = 149 / 126827
    probe_est = 445.0
    comp_est = {r: probe_est * AREA_KM2[r] / AREA_KM2[REGIONS[0]] * YEARS for r in REGIONS}
    total = sum(box[m] * rate * BANDS for m in box) + probe_est + sum(comp_est.values())
    wd.set_session_cap("W1", 1.5 * total)

    # 1. Sul weights
    sul = REGIONS[0]
    sul_cost = 0.0
    for m in mesos[sul]:
        est = box[m] * rate * BANDS
        state, used = w1_mask.weights(project, m, est)
        record(f"w1_weights_meso_{m}", sul, est, state, used)
        sul_cost += used

    # 2. Sul 2021 probe, with a sanity check
    fc = evi.run_full(project, sul, "2021-01-01", "2022-01-01")
    df, used = wd.export_table_watched(fc, f"w1_full_probe_{evi.slug_of(sul)}_2021", evi.full_selectors(), probe_est)
    record(f"w1_full_probe_{evi.slug_of(sul)}_2021", sul, probe_est, "COMPLETED" if df is not None else "FAILED", used)
    df.to_csv(WEEK0 / f"w1_full_probe_{evi.slug_of(sul)}_2021.csv", index=False)
    ok = (len(df) > 0 and df.composite_start.nunique() == 23 and df.f_q1_EVI_median.between(-0.2, 1.0).all()
          and (df.f_w_total_sum > 0).all())
    wd._log(f"probe check: {len(df)} rows, {df.composite_start.nunique()} composites, "
            f"{df.code.nunique()} municipalities, EVI median range "
            f"{df.f_q1_EVI_median.min():.3f}-{df.f_q1_EVI_median.max():.3f} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("stopping: probe output failed its sanity check")

    # 3. Reset estimates from the measured costs; recompute the session cap
    rate = sul_cost / (sum(box[m] for m in mesos[sul]) * BANDS)
    comp_est = {r: used * AREA_KM2[r] / AREA_KM2[sul] * YEARS for r in REGIONS}
    remaining = sum(box[m] * rate * BANDS for r in REGIONS[1:] for m in mesos[r]) + sum(comp_est.values())
    led = wd._ledger()
    cap = 1.5 * (led["spent"] + remaining)
    led["cap"] = cap
    wd.LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")
    wd._log(f"estimates reset: weights rate {rate:.6f} EECU-s per km²-band; composites "
            + ", ".join(f"{r[:10]} {v:,.0f}" for r, v in comp_est.items())
            + f"; session cap now {cap:,.0f} EECU-s (1.5 × {led['spent'] + remaining:,.0f})")

    # 4. Region by region
    for r in REGIONS:
        if r != sul:
            for m in mesos[r]:
                est = box[m] * rate * BANDS
                state, used = w1_mask.weights(project, m, est)
                record(f"w1_weights_meso_{m}", r, est, state, used)
        name = f"w1_series_muni_{evi.slug_of(r)}"
        df, used = wd.export_table_watched(evi.run_full(project, r), name, evi.full_selectors(), comp_est[r])
        record(name, r, comp_est[r], "COMPLETED" if df is not None else "FAILED", used)
        df.to_csv(ROOT / "data" / "derived" / f"{name}.csv", index=False)
        wd._log(f"{r}: {len(df):,} municipality-composites, {df.code.nunique()} municipalities, "
                f"{df.composite_start.nunique()} composites")
    wd._log(f"W1 done: session spend {wd.session_spent():,.0f} EECU-s")


if __name__ == "__main__":
    main()
