"""Earth Engine compute used this month, from Cloud Monitoring (owner request 2026-10-14).

Reads the metric earthengine.googleapis.com/project/cpu/usage_time (EECU-seconds) for the
project from the first of the month to now, with the Earth Engine credentials. Prints the total
in EECU-hours against the Contributor tier's 1,000 EECU-hours a month (Google, "Noncommercial
tiers", read 2026-10-14). The project ID is never printed.

Run:    .venv/Scripts/python gee/ee_usage.py
"""
import datetime as dt

import ee
import requests
from google.auth.transport.requests import Request

from common import init

CAP_EECU_HOURS = 1000


def main():
    project = init()
    creds = ee.data.get_persistent_credentials()
    creds.refresh(Request())
    now = dt.datetime.now(dt.timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    params = {
        "filter": 'metric.type="earthengine.googleapis.com/project/cpu/usage_time"',
        "interval.startTime": start.isoformat().replace("+00:00", "Z"),
        "interval.endTime": now.isoformat().replace("+00:00", "Z"),
        "aggregation.alignmentPeriod": f"{int((now - start).total_seconds()) + 60}s",
        "aggregation.perSeriesAligner": "ALIGN_SUM",
        "aggregation.crossSeriesReducer": "REDUCE_SUM",
    }
    r = requests.get(f"https://monitoring.googleapis.com/v3/projects/{project}/timeSeries", params=params,
                     headers={"Authorization": f"Bearer {creds.token}"}, timeout=60)
    if r.status_code != 200:
        print(f"Cloud Monitoring returned HTTP {r.status_code}: {r.text[:300].replace(project, '<EE_PROJECT>')}")
        return None
    total = 0.0
    for series in r.json().get("timeSeries", []):
        for pt in series.get("points", []):
            v = pt["value"]
            total += float(v.get("doubleValue", v.get("int64Value", 0)))
    print(f"{start:%Y-%m-%d} to {now:%Y-%m-%d %H:%M} UTC: {total:,.0f} EECU-seconds = {total / 3600:,.1f} "
          f"EECU-hours of {CAP_EECU_HOURS:,} ({total / 3600 / CAP_EECU_HOURS:.1%})")
    return total


if __name__ == "__main__":
    main()
