"""Shared Earth Engine setup.

Reads EE_PROJECT from the environment or from .env in the repo root. The project ID is never
printed, so logs can be committed without it.
"""
import os
from pathlib import Path

import ee

ROOT = Path(__file__).resolve().parents[1]
WEEK0 = ROOT / "docs" / "week0"


def _read_env(path=ROOT / ".env"):
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def init():
    project = os.environ.get("EE_PROJECT") or _read_env().get("EE_PROJECT")
    if not project:
        raise SystemExit("EE_PROJECT is not set. Add EE_PROJECT=<cloud-project-id> to .env.")
    ee.Initialize(project=project)
    WEEK0.mkdir(parents=True, exist_ok=True)
