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


def setting(name):
    """A configuration value from the environment or .env; exits with a clear message if unset."""
    value = os.environ.get(name) or _read_env().get(name)
    if not value:
        raise SystemExit(f"{name} is not set. Add {name}=<value> to .env (see README, Configuration).")
    return value


def init():
    project = setting("EE_PROJECT")
    ee.Initialize(project=project)
    WEEK0.mkdir(parents=True, exist_ok=True)
    return project
