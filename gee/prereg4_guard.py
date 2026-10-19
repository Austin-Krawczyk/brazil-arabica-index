"""prereg-4 guard (owner, 2026-10-18): no script reads price data unless the price-test registration
(docs/preregistration_4.md) is committed at HEAD and tagged.

The guard refuses unless all of these hold:
  - docs/preregistration_4.md is committed at HEAD;
  - the working copy is identical to the committed copy (line endings normalised);
  - the committed document has no "OPEN POINT" left;
  - the tag prereg-4 exists and is an ancestor of HEAD.

Use it at the top of any script that reads price data, before the read:
    from prereg4_guard import require
    require()

gee/check_prereg4_guard.py fails if a gee/ script that refers to price data does not call require().
Prices are not fetched until the owner says go (owner, 2026-10-18).
"""
import subprocess

from common import ROOT

DOC = "docs/preregistration_4.md"


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, cwd=ROOT)


def require():
    """Refuse (SystemExit) unless prereg-4 is registered at HEAD; return the HEAD commit."""
    head = _git("show", f"HEAD:{DOC}")
    if head.returncode != 0:
        raise SystemExit(f"prereg-4 guard: {DOC} is not committed at HEAD; no price data may be read")
    committed = head.stdout.replace(b"\r\n", b"\n")
    with open(ROOT / DOC, "rb") as f:
        if f.read().replace(b"\r\n", b"\n") != committed:
            raise SystemExit(f"prereg-4 guard: {DOC} differs from HEAD; no price data may be read")
    if b"OPEN POINT" in committed:
        raise SystemExit("prereg-4 guard: the registration still has open points; no price data may be read")
    if _git("rev-parse", "--verify", "--quiet", "refs/tags/prereg-4").returncode != 0:
        raise SystemExit("prereg-4 guard: the tag prereg-4 does not exist; no price data may be read")
    if _git("merge-base", "--is-ancestor", "prereg-4", "HEAD").returncode != 0:
        raise SystemExit("prereg-4 guard: prereg-4 is not an ancestor of HEAD; no price data may be read")
    sha = _git("rev-parse", "HEAD").stdout.decode().strip()
    print(f"prereg-4 guard passed at {sha[:7]}", flush=True)
    return sha
