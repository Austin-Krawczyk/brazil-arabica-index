"""Earth Engine compute used this month, from Cloud Monitoring (owner request 2026-10-14).

Metrics (Google Cloud, "Google Cloud metrics: earthengine", read 2026-10-15; both BETA, DELTA,
EECU-seconds):
  project/cpu/usage_time              completed EECU-seconds: usage of successful requests,
                                      reported when a request completes
  project/cpu/in_progress_usage_time  EECU-seconds reported periodically while requests run, so
                                      it also sees requests that are later cancelled or fail
Summed from the first of the month to now, split by compute_type (online, batch, highvolume), and
set against the Contributor tier's 1,000 EECU-hours a month (Google, "Noncommercial tiers", read
2026-10-14). The project ID is never printed.

--enable turns on the Cloud Monitoring API for the project through the Service Usage API (owner
instruction, 2026-10-14). It is a change to the project's settings, made only on request.

Run:    .venv/Scripts/python gee/ee_usage.py [--enable]
"""
import argparse
import datetime as dt
import time

import ee
import requests
from google.auth.transport.requests import Request

from common import init

CAP_EECU_HOURS = 1000
METRICS = ("project/cpu/usage_time", "project/cpu/in_progress_usage_time")


def _token():
    creds = ee.data.get_persistent_credentials()
    creds.refresh(Request())
    return creds.token


def enable(project):
    url = f"https://serviceusage.googleapis.com/v1/projects/{project}/services/monitoring.googleapis.com:enable"
    r = requests.post(url, headers={"Authorization": f"Bearer {_token()}", "x-goog-user-project": project}, timeout=120)
    print(f"enable Cloud Monitoring API: HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:300].replace(project, "<EE_PROJECT>"))
    return r.status_code == 200


def usage(project, metric):
    now = dt.datetime.now(dt.timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    params = {
        "filter": f'metric.type="earthengine.googleapis.com/{metric}"',
        "interval.startTime": start.isoformat().replace("+00:00", "Z"),
        "interval.endTime": now.isoformat().replace("+00:00", "Z"),
        "aggregation.alignmentPeriod": f"{int((now - start).total_seconds()) + 60}s",
        "aggregation.perSeriesAligner": "ALIGN_SUM",
        "aggregation.crossSeriesReducer": "REDUCE_SUM",
        "aggregation.groupByFields": "metric.label.compute_type",
    }
    r = requests.get(f"https://monitoring.googleapis.com/v3/projects/{project}/timeSeries", params=params,
                     headers={"Authorization": f"Bearer {_token()}", "x-goog-user-project": project}, timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200].replace(project, '<EE_PROJECT>')}"
    split = {}
    for series in r.json().get("timeSeries", []):
        kind = series.get("metric", {}).get("labels", {}).get("compute_type", "all")
        split[kind] = sum(float(p["value"].get("doubleValue", p["value"].get("int64Value", 0)))
                          for p in series.get("points", []))
    return split, f"{start:%Y-%m-%d} to {now:%Y-%m-%d %H:%M} UTC"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--enable", action="store_true")
    args = a.parse_args()
    project = init()
    if args.enable and not enable(project):
        return
    for metric in METRICS:
        for attempt in range(6):
            split, info = usage(project, metric)
            if split is not None or "has not been used" not in info:
                break
            time.sleep(30)  # a newly enabled API can take a minute to accept calls
        if split is None:
            print(f"{metric}: {info}")
            continue
        total = sum(split.values())
        parts = ", ".join(f"{k} {v / 3600:,.1f}" for k, v in sorted(split.items()))
        print(f"{metric}, {info}: {total:,.0f} EECU-seconds = {total / 3600:,.1f} EECU-hours "
              f"({total / 3600 / CAP_EECU_HOURS:.1%} of {CAP_EECU_HOURS:,}) [{parts}]")


if __name__ == "__main__":
    main()
