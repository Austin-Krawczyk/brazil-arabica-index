"""Enforce the no-interactive-reductions rule (owner, 2026-10-15) on gee/*.py.

Every call that makes Earth Engine compute interactively (getInfo, evaluate, computeValue,
computePixels, computeFeatures, download and thumbnail URLs) must carry a tag on the same line,
"# interactive: <reason>", with a reason from ALLOWED: metadata, a single-pixel read, or a vector
geometry with no pixels. Anything else (a reduction over an area) must run as a batch export
through gee/ee_watchdog.py with an estimate. Exits 1 and lists every untagged call.

Run:    .venv/Scripts/python gee/check_interactive.py
"""
import re
import sys
from pathlib import Path

GEE = Path(__file__).resolve().parent
CALLS = re.compile(r"\.(getInfo|evaluate|computeValue|computePixels|computeFeatures|"
                   r"getDownloadURL|getDownloadUrl|getThumbURL|getThumbUrl|getMapId)\(")
TAG = re.compile(r"#\s*interactive:\s*(.+)$")
ALLOWED = ("metadata", "one pixel", "vector geometry, no pixels")


def main():
    bad, ok = [], 0
    for f in sorted(GEE.glob("*.py")):
        if f.name == Path(__file__).name:
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not CALLS.search(line):
                continue
            tag = TAG.search(line)
            if tag and tag.group(1).strip().startswith(ALLOWED):
                ok += 1
            else:
                bad.append(f"{f.name}:{i}: {line.strip()}")
    print(f"{ok} tagged interactive call(s), {len(bad)} untagged")
    for b in bad:
        print("  UNTAGGED", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
