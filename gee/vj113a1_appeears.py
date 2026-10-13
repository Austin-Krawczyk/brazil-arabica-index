"""VJ113A1 via NASA AppEEARS (route B; Amendment 25 revised, Amendment 30 second revision).

Submits one area request for the three layers needed over Minas Gerais and São Paulo, 2018-01-01
to the submission date, in the product's native sinusoidal grid (no resampling), as GeoTIFF; or
checks an existing request's status.

The area is GAUL 2025 level 1 Minas Gerais + São Paulo, simplified (500 m tolerance) to keep the
request small and buffered by 1 km so simplification never drops a border pixel.

The token comes from APPEEARS_TOKEN in .env and is never printed or saved. The request body
(without the token) and the task ID are saved under docs/week0/ for the record.

Run:    .venv/Scripts/python gee/vj113a1_appeears.py submit
        .venv/Scripts/python gee/vj113a1_appeears.py status
"""
import datetime as dt
import json
import sys

import ee
import requests

from common import WEEK0, init, setting

API = "https://appeears.earthdatacloud.nasa.gov/api"
PRODUCT = "VJ113A1.002"
LAYERS = ["500_m_16_days_EVI", "500_m_16_days_NDVI", "500_m_16_days_pixel_reliability"]
START = "01-01-2018"  # AppEEARS dates are MM-DD-YYYY
REQUEST_FILE = WEEK0 / "appeears_vj113a1_request.json"
TASK_FILE = WEEK0 / "appeears_vj113a1_task.json"


def area_geojson():
    states = (ee.FeatureCollection("FAO/GAUL/2025/level1")
              .filter(ee.Filter.eq("GAUL0_NAME", "Brazil"))
              .filter(ee.Filter.inList("GAUL1_NAME", ["Minas Gerais", "São Paulo"])))
    if states.size().getInfo() != 2:
        raise SystemExit("Expected 2 state polygons from GAUL 2025.")
    geom = states.geometry().simplify(maxError=500).buffer(1000, maxError=100)
    return {"type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {"name": "MG+SP"},
                          "geometry": geom.getInfo()}]}


def headers():
    return {"Authorization": f"Bearer {setting('APPEEARS_TOKEN')}"}


def submit():
    if TASK_FILE.exists():
        raise SystemExit(f"A task is already recorded in {TASK_FILE.name}; not submitting twice.")
    init()
    end = dt.date.today().strftime("%m-%d-%Y")
    body = {
        "task_type": "area",
        "task_name": "brazil-arabica-index VJ113A1 MG+SP 2018-present",
        "params": {
            "dates": [{"startDate": START, "endDate": end}],
            "layers": [{"product": PRODUCT, "layer": layer} for layer in LAYERS],
            "geo": area_geojson(),
            "output": {"format": {"type": "geotiff"}, "projection": "native"},
        },
    }
    n_vertices = sum(len(ring) for ring in _rings(body["params"]["geo"]))
    REQUEST_FILE.write_text(json.dumps(body, indent=1), encoding="utf-8")
    print(f"request saved to {REQUEST_FILE.name} ({n_vertices} polygon vertices); submitting")
    r = requests.post(f"{API}/task", json=body, headers=headers(), timeout=120)
    if not r.ok:
        raise SystemExit(f"AppEEARS refused the request: {r.status_code} {r.text[:300]}")
    task = r.json()
    task["submitted_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    TASK_FILE.write_text(json.dumps(task, indent=1), encoding="utf-8")
    print(f"task_id {task.get('task_id')} | status {task.get('status')}")


def status():
    task = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    r = requests.get(f"{API}/task/{task['task_id']}", headers=headers(), timeout=60)
    r.raise_for_status()
    s = r.json()
    print(f"task_id {s.get('task_id')} | status {s.get('status')} | created {s.get('created')} | "
          f"updated {s.get('updated')} | progress {s.get('progress', {}).get('summary', '')}")
    return s


def _rings(fc):
    for f in fc["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            yield from poly


if __name__ == "__main__":
    {"submit": submit, "status": status}[sys.argv[1]]()
