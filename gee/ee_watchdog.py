"""Earth Engine task watchdog (owner, 2026-10-14).

Every batch task this project starts goes through run_watched(), which refuses to start a task
without a cost estimate, records the estimate, then polls the task every POLL_SECONDS and cancels
it once its EECU use passes CANCEL_FACTOR × the estimate. The standalone mode (--watch) polls
every running or pending Earth Engine task in the project the same way: a task with a recorded
estimate is cancelled past CANCEL_FACTOR × its estimate, and one without an estimate past
UNREGISTERED_LIMIT EECU-seconds (the project's 0.5 EECU-hour probe gate).

Session cap (owner, 2026-10-14): run_watched() also refuses to start a task once the session's
cumulative measured spend has passed the cap set with set_session_cap() — for W1, 1.5 × the total
W1 estimate. Each finished or cancelled task's measured cost is added to the session ledger.

Tasks run serially: run_watched() starts one task and blocks until it ends; the next starts only
after. sweep_once() starts nothing; it is a separate check on whatever is running.

No interactive reductions (owner rule, 2026-10-15): nothing larger than a few pixels is reduced
through an interactive request (getInfo, evaluate, computeValue). The watchdog sees only batch
tasks, and the 2026-10-13 provisional drift check spent about 356 EECU-hours interactively, unseen.
Every reduction over an area runs as a batch export through run_watched() or
export_table_watched(), with an estimate. Interactive calls left in gee/ are metadata (asset
properties, band names, feature counts, projections) or single-pixel point reads, each tagged
"# interactive:" with its reason; gee/check_interactive.py fails on any untagged call.

Estimates, the session ledger and every cancellation are logged in docs/week0/ee_task_estimates.json,
docs/week0/ee_session_ledger.json and docs/week0/ee_watchdog_log.txt.

Run (standalone): .venv/Scripts/python gee/ee_watchdog.py --watch [--poll 60]
"""
import argparse
import datetime as dt
import json
import time

import ee

from common import WEEK0, init

POLL_SECONDS = 60            # every minute (owner, 2026-10-14; was five minutes)
CANCEL_FACTOR = 2.0          # cancel at 2 × the probe estimate (owner)
UNREGISTERED_LIMIT = 1800.0  # EECU-seconds, for a running task with no recorded estimate
REGISTRY = WEEK0 / "ee_task_estimates.json"
LOG = WEEK0 / "ee_watchdog_log.txt"
LEDGER = WEEK0 / "ee_session_ledger.json"


def _log(msg):
    line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC  {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}


def register(description, estimate_eecu_s):
    reg = _registry()
    reg[description] = float(estimate_eecu_s)
    REGISTRY.write_text(json.dumps(reg, indent=1, sort_keys=True), encoding="utf-8")


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"cap": None, "spent": 0.0, "tasks": []}


def set_session_cap(name, cap_eecu_s):
    """Start (or reset) a session: no new task starts once measured spend passes the cap."""
    LEDGER.write_text(json.dumps({"session": name, "cap": float(cap_eecu_s), "spent": 0.0, "tasks": []},
                                 indent=1), encoding="utf-8")
    _log(f"session {name}: cap {cap_eecu_s:,.0f} EECU-s")


def session_spent():
    return _ledger()["spent"]


def _record(desc, state, used):
    led = _ledger()
    led["spent"] = led.get("spent", 0.0) + used
    led.setdefault("tasks", []).append({"task": desc, "state": state, "eecu_s": round(used, 1)})
    LEDGER.write_text(json.dumps(led, indent=1), encoding="utf-8")


def _eecu(op):
    return float(op.get("metadata", {}).get("batchEecuUsageSeconds", 0) or 0)


def run_watched(task, estimate_eecu_s, poll=POLL_SECONDS):
    """Start a batch task under the watchdog. Returns (state, EECU-seconds, wall seconds)."""
    if not estimate_eecu_s or estimate_eecu_s <= 0:
        raise SystemExit(f"{task.config.get('description', 'task')}: no cost estimate, not started")
    desc = task.config.get("description", "task")
    led = _ledger()
    if led.get("cap") is not None and led.get("spent", 0.0) > led["cap"]:
        raise SystemExit(f"{desc}: session spend {led['spent']:,.0f} EECU-s has passed the cap "
                         f"{led['cap']:,.0f}; not started")
    limit = CANCEL_FACTOR * estimate_eecu_s
    register(desc, estimate_eecu_s)
    task.start()
    _log(f"started {desc}: estimate {estimate_eecu_s:,.0f}, cancel above {limit:,.0f} EECU-s, poll {poll} s")
    t0 = time.time()
    while True:
        time.sleep(poll)
        op = ee.data.getOperation(task.operation_name) if getattr(task, "operation_name", None) else None
        st = task.status()
        used = _eecu(op) if op else float(st.get("batch_eecu_usage_seconds", 0) or 0)
        state = st["state"]
        if state in ("COMPLETED", "FAILED", "CANCELLED", "SUCCEEDED"):
            _log(f"{state.lower()} {desc}: {used:,.0f} EECU-s, {time.time() - t0:.0f} s wall")
            _record(desc, state, used)
            return state, used, time.time() - t0
        if used > limit:
            task.cancel()
            _log(f"CANCELLED {desc}: {used:,.0f} EECU-s passed {limit:,.0f} (2 × estimate)")
            _record(desc, "CANCELLED", used)
            return "CANCELLED", used, time.time() - t0
        _log(f"running {desc}: {used:,.0f} of {limit:,.0f} EECU-s")


def export_table_watched(fc, name, selectors, estimate_eecu_s, prefix="w1"):
    """Batch table export to the project bucket under the watchdog; returns (DataFrame or None, cost)."""
    import io

    import pandas as pd
    from google.cloud import storage

    from common import setting

    bucket = setting("GCS_BUCKET")
    task = ee.batch.Export.table.toCloudStorage(collection=fc, description=name, bucket=bucket,
                                                fileNamePrefix=f"{prefix}/{name}", fileFormat="CSV",
                                                selectors=selectors)
    state, used, _ = run_watched(task, estimate_eecu_s)
    if state not in ("COMPLETED", "SUCCEEDED"):
        return None, used
    client = storage.Client(project=setting("EE_PROJECT"), credentials=ee.data.get_persistent_credentials())
    return pd.read_csv(io.BytesIO(client.bucket(bucket).blob(f"{prefix}/{name}.csv").download_as_bytes())), used


def sweep_once():
    """Check every running or pending task once; cancel any over its limit. Returns how many run."""
    reg, running = _registry(), 0
    for op in ee.data.listOperations():
        md = op.get("metadata", {})
        if md.get("state") not in ("RUNNING", "PENDING"):
            continue
        running += 1
        desc, used = md.get("description", ""), _eecu(op)
        limit = CANCEL_FACTOR * reg[desc] if desc in reg else UNREGISTERED_LIMIT
        if used > limit:
            ee.data.cancelOperation(op["name"])
            _log(f"CANCELLED {desc}: {used:,.0f} EECU-s passed {limit:,.0f}"
                 + ("" if desc in reg else " (no recorded estimate)"))
        else:
            _log(f"ok {desc}: {used:,.0f} of {limit:,.0f} EECU-s")
    return running


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--watch", action="store_true")
    a.add_argument("--poll", type=int, default=POLL_SECONDS)
    args = a.parse_args()
    init()
    if not args.watch:
        print(f"{sweep_once()} running or pending task(s) checked")
        return
    idle = 0
    while idle < 2:  # stop after two consecutive polls with nothing running
        idle = idle + 1 if sweep_once() == 0 else 0
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
