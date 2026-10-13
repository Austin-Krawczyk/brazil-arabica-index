# Week 0 report

Status: **in progress**, 2026-10-12. Findings are recorded before anything in the spec changes
because of them. Earth Engine checks are pending until `EE_PROJECT` is set in `.env`.

## 1. Dataset verification (§10 checklist)

Two kinds of check per ID: what the provider's documentation says (done), and whether it
resolves and is current in Earth Engine (pending; `gee/week0_verify_ids.py`, results to
`docs/week0/ids.csv`).

| ID | Documentation finding | In Earth Engine |
|---|---|---|
| `MODIS/061/MOD13Q1` | Primary layer; verified in the 2026-10-12 pre-flight. | End date pending |
| `MODIS/061/MYD13Q1` | NDVI, EVI scale factor 0.0001; raw range −2000 to 10000; `SummaryQA` bits 0–1 (0 good, 1 marginal, 2 snow/ice, 3 cloudy). Catalog availability to 2026-09-06. | Pending |
| `NASA/VIIRS/002/VNP13A1` | 500 m, from 2012-01-17. GEE page gives no scale factor. Earthdata: NDVI/EVI int16, fill −15000, valid −10000 to 10000, "scale factor 10000" (read as divide by 10000; to confirm in the V2.1.2 user guide). `pixel_reliability` 0–11. **NASA ends Suomi NPP VIIRS delivery on 2 November 2026**, so it is a drift-check reference only (Amendment 25). | Pending |
| VJ113A1 (fallback candidate a) | NASA's named successor (NOAA-20 VIIRS, 500 m, 16-day). Earth Engine ID unknown. | Catalog search pending |
| HLS: HLSL30 + HLSS30 (fallback candidate b) | 30 m; Landsat from 2013, Sentinel-2 from 2015. Earth Engine IDs to confirm. | Catalog search pending |
| `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad` | Community catalog: pentad, 2015 onward, weekly updates, latency under 5 days. | Pending: resolves? current? |
| CHC prelim files (fallback) | Reachable. Pentad prelim current to 2026.10.2 (6–10 Oct), posted 2026-10-12. Daily `fixed/` prelim current to 2026-10-10, posted 2026-10-12. | Not an Earth Engine asset |
| `USGS/SRTMGL1_003` | Image, band `elevation`, metres, 30 m, 56°S–60°N; voids filled from ASTER GDEM v2, GMTED2010, NED. Vertical datum not stated on the GEE or Earthdata pages. | Pending |
| `COPERNICUS/DEM/GLO30_2024_1` | Replaces the deprecated `COPERNICUS/DEM/GLO30` (Amendment 27). ImageCollection, band `DEM`, EGM2008, surface model. | Pending |
| ERA5-Land soil layers | Confirmed: `volumetric_soil_water_layer_1/2/3` = 0–7, 7–28, 28–100 cm, volume fraction. Weights 0.07/0.21/0.72 (Amendment 28). Catalog availability to 2026-10-07. | Pending |

## 2. CHC daily-prelim day split: not established (Amendment 29)

CHC's readme for the daily prelim, dated 2019-08-22, describes splitting each pentad into days
by cold cloud duration (CCD), with any residual placed on the wettest CFS-Reanalysis day; a
`fixed/` directory holds daily data that sums exactly to the pentad totals. It does not mention
IMERG. The readme is seven years old, so the method is recorded as **not established**. Dry-day
counts from daily prelim are not compared with final-CHIRPS counts until the gap is measured on
overlapping months.

## 3. Terra drift check

### Method, fixed before running (Amendment 26)

Calendar-month anomalies for `MOD13Q1`, `MYD13Q1` and `VNP13A1`, NDVI and EVI, against a common
2013–2025 baseline, each over the product's own pixels within the mask; compared 2018-01 to
2026-10. The provisional run covers all class-46 coffee pixels in MG and SP. The formal run, per
region and for the four-region total, waits for the regional municipality lists; trigger (b) is
evaluated on the formal run only.

### Implementation choices for the provisional run — proposed, to confirm before it runs

These are not in the spec and would otherwise be made silently in code:

1. **State boundaries:** FAO GAUL 2015 level 1 (`FAO/GAUL/2015/level1`) for MG and SP. This is a
   dataset not in §4, used for the provisional run only. The formal run uses IBGE municipal
   boundaries, which the regional lists need anyway.
2. **Mask year:** MapBiomas Collection 10, `classification_2024`, class 46.
3. **QA screening:** MODIS `SummaryQA` 0–1 (good, marginal); VIIRS `pixel_reliability` 0–3
   (excellent to marginal). The two QA scales are not identical; this is the closest match.
4. **"Own pixels within the mask":** each product pixel weighted by its coffee fraction, the mean
   of the 30 m mask within it; pixels with no coffee are dropped.
5. **Month assignment:** a composite belongs to the month its start date falls in. All products
   use the same rule.
6. **Denominators reported:** coffee pixels per product, and valid pixels per month.

### Results

Pending Earth Engine access (`gee/week0_drift_provisional.py`).

## 4. Other Week 0 checklist items, not yet started

Conab granularity (§4c, blocking); Conab's IBGE unit system and municipality lists; INMET route,
daily minima and Jun–Aug 2026 availability; CHIRPS circularity; MapBiomas 2025 collection; Conab
2027 dates; Planet quota; ICE terms.
