"""Enforce the prereg-3 guard (owner, 2026-10-16) on gee/*.py.

A script that refers to night land-surface temperature (MOD11A1, MYD11A1, LST_Night) must call
require("night_lst"). A script that refers to onset or first-rain dates must call require("onset")
or require("night_lst"). The call must be on a line that is not a comment. The guard itself
(gee/prereg3_guard.py) refuses unless the prereg-3 addenda are committed at HEAD. Exits 1 and lists
every script that is missing its call.

Run:    .venv/Scripts/python gee/check_prereg3_guard.py
"""
import re
import sys
from pathlib import Path

GEE = Path(__file__).resolve().parent
SKIP = {"prereg3_guard.py", Path(__file__).name}
LST = re.compile(r"MOD11A1|MYD11A1|LST_Night", re.I)
ONSET = re.compile(r"onset|first[_ -]rain", re.I)
CALL = re.compile(r"""^[^#]*\brequire\(\s*["'](night_lst|onset)["']\s*\)""")


def main():
    bad, checked = [], 0
    for f in sorted(GEE.glob("*.py")):
        if f.name in SKIP:
            continue
        text = f.read_text(encoding="utf-8")
        needs = (["night_lst"] if LST.search(text) else []) + (["onset"] if ONSET.search(text) else [])
        if not needs:
            continue
        checked += 1
        calls = {m.group(1) for line in text.splitlines() for m in [CALL.search(line)] if m}
        if "night_lst" in needs and "night_lst" not in calls:
            bad.append(f"{f.name}: refers to night LST but does not call require('night_lst')")
        if "onset" in needs and not calls & {"onset", "night_lst"}:
            bad.append(f"{f.name}: refers to onset dates but does not call require('onset')")
    print(f"{checked} script(s) refer to night LST or onset; {len(bad)} missing the prereg-3 guard")
    for b in bad:
        print("  MISSING", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
