# Brazil Arabica Condition Index

A public, reproducible growing-conditions index for Brazil's arabica belt, built from free
satellite and weather data in Google Earth Engine.

**This is a condition index, not a yield forecast.** It answers one question each month: are
growing conditions in each arabica region better, worse or in line with the baseline, and what
does that imply for the crop relative to Conab and the private estimates. It does not predict a
number of bags, and it is not a trading signal.

Scope, method, data sources and the rules this project is built under are in [CLAUDE.md](CLAUDE.md).
Every change of scope, with its reason and date, is in [SPEC_CHANGELOG.md](SPEC_CHANGELOG.md).

Status: **Week 0.** Spec adopted 2026-10-12 after review. Week 0 checks in progress; see
[docs/week0_report.md](docs/week0_report.md).

## Known limits, stated up front

- The index tracks conditions, not yield.
- The private trade houses have field crop tours and farm data that this project does not.
- MODIS at 250 m blurs smallholder terrain, so Zona da Mata skill is expected to be the weakest
  of the four regions. Regional skill is reported separately rather than averaged away.
- Frost comes from INMET station observations only. ERA5-Land is not used for frost, because it
  was the weakest of five products at station minima in a previous study by the same author.

## Configuration

Settings live in a `.env` file in the repo root, which is gitignored. Copy the keys below and fill
in your own values.

| Key | What it is | Value used by this project |
|---|---|---|
| `EE_PROJECT` | Google Cloud project registered for Earth Engine | Your own project ID |
| `GCS_BUCKET` | Cloud Storage bucket for ingesting CHC prelim files into Earth Engine (`gee/chc_prelim_ingest.py`). A configuration value, not a secret | `brazil-arabica-index-ingest` (proposed) |

Earth Engine authentication uses the standard `earthengine authenticate` credentials. The ingestion
script reuses them for Cloud Storage, so they need the `devstorage` scope (the default). Creating
the bucket needs billing enabled on the project; the data held there is a few hundred MB.

Python environment: `python -m venv .venv`, then install `requirements.txt`.
