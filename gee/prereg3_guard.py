"""prereg-3 guard (owner, 2026-10-16): no night-LST or onset computation unless the prereg-3
addenda are committed at HEAD.

The addenda are the values prereg-3 fixes after its tag and before any v2 computation
(docs/preregistration.md, prereg-3 section). They live in docs/prereg3_addenda.csv, one row each.
A required row counts only when all of these hold:
  - its value and its source are filled in;
  - the file is committed at HEAD;
  - the working copy is identical to the committed copy (line endings normalised).

Requirements:
  night_lst  h3_lst_false_alarm_max and h4_onset_event (the owner's two addenda), and
             h3_lst_frost_threshold (H3's threshold, fixed before computing)
  onset      h3_lst_false_alarm_max and h4_onset_event

Use it at the top of a v2 script, before any Earth Engine or data call. Take the values from what it
returns, never from constants in the script:
    from prereg3_guard import require
    addenda = require("onset")      # or require("night_lst")

gee/check_prereg3_guard.py fails if a gee/ script that refers to night LST or to onset dates does not
call require().
"""
import csv
import io
import subprocess

from common import ROOT

ADDENDA = "docs/prereg3_addenda.csv"
REQUIRED = {
    "night_lst": ["h3_lst_false_alarm_max", "h4_onset_event", "h3_lst_frost_threshold"],
    "onset": ["h3_lst_false_alarm_max", "h4_onset_event"],
}


def require(kind):
    """Refuse (SystemExit) unless the addenda for `kind` are filled in and committed at HEAD; return
    the committed values {key: value}."""
    if kind not in REQUIRED:
        raise SystemExit(f"prereg-3 guard: unknown computation '{kind}'; expected one of {sorted(REQUIRED)}")
    head = subprocess.run(["git", "show", f"HEAD:{ADDENDA}"], capture_output=True, cwd=ROOT)
    if head.returncode != 0:
        raise SystemExit(f"prereg-3 guard: {ADDENDA} is not committed at HEAD; no {kind} computation")
    committed = head.stdout.replace(b"\r\n", b"\n")
    with open(ROOT / ADDENDA, "rb") as f:
        working = f.read().replace(b"\r\n", b"\n")
    if working != committed:
        raise SystemExit(f"prereg-3 guard: {ADDENDA} differs from HEAD; commit the addenda first; no {kind} computation")
    rows = {r["key"]: r for r in csv.DictReader(io.StringIO(committed.decode("utf-8")))}
    missing = [k for k in REQUIRED[kind]
               if k not in rows or not rows[k]["value"].strip() or not rows[k]["source"].strip()]
    if missing:
        raise SystemExit(f"prereg-3 guard: addenda not fixed at HEAD for {kind}: {', '.join(missing)}; "
                         f"no {kind} computation")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    print(f"prereg-3 guard passed for {kind}: addenda at {sha[:7]}", flush=True)
    return {k: rows[k]["value"].strip() for k in REQUIRED[kind]}
