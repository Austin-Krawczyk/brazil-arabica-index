"""Enforce the prereg-4 guard (owner, 2026-10-18) on gee/*.py.

A script that refers to price data must call require() from gee/prereg4_guard.py, on a line that is
not a comment. Price data here means any of these:
  - the raw price folder (data/raw/ice);
  - an ICE Coffee "C" contract code (KC plus a month letter and year, for example KCN25);
  - the words "settlement price";
  - Coffee "C".
Exits 1 and lists every script that is missing its call.

Run:    .venv/Scripts/python gee/check_prereg4_guard.py
"""
import re
import sys
from pathlib import Path

GEE = Path(__file__).resolve().parent
SKIP = {"prereg4_guard.py", Path(__file__).name}
PRICE = re.compile(r"data/raw/ice|\bKC[FHKNUZ]\d{2}\b|settlement price|coffee[ _-]?\"?c\"?\b", re.I)
CALL = re.compile(r"^[^#]*\brequire\(\s*\)")
IMPORT = re.compile(r"^[^#]*\bfrom\s+prereg4_guard\s+import\s+require\b|^[^#]*\bimport\s+prereg4_guard\b")


def main():
    bad, checked = [], 0
    for f in sorted(GEE.glob("*.py")):
        if f.name in SKIP:
            continue
        text = f.read_text(encoding="utf-8")
        if not PRICE.search(text):
            continue
        checked += 1
        lines = text.splitlines()
        if not (any(IMPORT.search(x) for x in lines) and any(CALL.search(x) for x in lines)):
            bad.append(f"{f.name}: refers to price data but does not call prereg4_guard.require()")
    print(f"{checked} script(s) refer to price data; {len(bad)} missing the prereg-4 guard")
    for b in bad:
        print("  MISSING", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
