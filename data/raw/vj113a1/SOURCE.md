# VJ113A1 (NOAA-20 VIIRS vegetation indices) — raw files from NASA AppEEARS

Files here are gitignored except this note and `manifest.csv`; nothing is modified after download
(§9).

- **Product:** VJ113A1 version 002, "VIIRS/JPSS1 Vegetation Indices 16-Day L3 Global 500m SIN
  Grid", LP DAAC (NASA CMR collection `C2519122065-LPCLOUD`).
- **Request:** NASA AppEEARS area task `145e0b79-00e3-41c2-b1c8-eeea5e7e4d49`, submitted
  2026-10-13 18:36 UTC, completed 22:25 UTC. Layers `500_m_16_days_EVI`, `500_m_16_days_NDVI` and
  `500_m_16_days_pixel_reliability`, over Minas Gerais + São Paulo (GAUL 2025, simplified 500 m,
  buffered 1 km), dates 2018-01-01 to 2026-10-13, GeoTIFF in the native sinusoidal grid. Request
  body: `docs/week0/appeears_vj113a1_request.json`.
- **Delivered:** 1,613 files, 10.62 GB: 401 composites (2018-01-01 to 2026-09-14) × 4 layers, plus
  9 metadata files (lookup tables, QA statistics, granule list). AppEEARS added
  `500_m_16_days_VI_Quality` without it being requested; it is kept here but not ingested.
- **Format:** int16 as published (EVI and NDVI × 0.0001, fill −15000; pixel_reliability 0–11),
  LZW-compressed, sinusoidal at 463.3 m, 2,595 × 2,664 pixels.
- **Downloaded:** 2026-10-14 by `gee/vj113a1_download.py`, one file at a time. `manifest.csv` lists
  every file's AppEEARS file ID, size, SHA-256 and retrieval time (UTC).
- **Use:** the declared vegetation fallback (b) (Amendment 25, revised), subject to the
  Amendment 30 (second revision) acceptance check; baseline 2018–2025, shorter than the other
  products'.
