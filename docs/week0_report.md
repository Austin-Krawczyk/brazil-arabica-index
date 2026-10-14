# Week 0 report

Status: **in progress**, updated 2026-10-13. Findings are recorded before anything in the spec
changes because of them.

## 1. Dataset verification (§10 checklist)

Two kinds of check per ID: what the provider's documentation says, and whether it resolves and
is current in Earth Engine (`gee/week0_verify_ids.py`, run 2026-10-13, results in
`docs/week0/ids.csv`). Latest dates are the start date of the newest image.

| ID | Documentation finding | In Earth Engine |
|---|---|---|
| `MODIS/061/MOD13Q1` | Primary layer; verified in the 2026-10-12 pre-flight. | Resolves; 612 composites, 2000-02-18 to 2026-09-14. **Still updating** as of 2026-10-13. |
| `MODIS/061/MYD13Q1` | NDVI, EVI scale factor 0.0001; raw range −2000 to 10000; `SummaryQA` bits 0–1 (0 good, 1 marginal, 2 snow/ice, 3 cloudy). Catalog availability to 2026-09-06. | Resolves; 557 composites, 2002-07-04 to 2026-09-06. |
| `NASA/VIIRS/002/VNP13A1` | 500 m, from 2012-01-17. GEE page gives no scale factor. Earthdata: NDVI/EVI int16, fill −15000, valid −10000 to 10000, "scale factor 10000" (read as divide by 10000; to confirm in the V2.1.2 user guide). `pixel_reliability` 0–11. **NASA ends Suomi NPP VIIRS delivery on 2 November 2026**, so it is a drift-check reference only (Amendment 25). | Resolves; 674 composites (8-day cadence), 2012-01-17 to 2026-09-06; `pixel_reliability` and `VI_Quality` present. |
| VJ113A1 (fallback candidate a) | NASA's named successor (NOAA-20 VIIRS, 500 m, 16-day). | **Not in Earth Engine.** `NASA/VIIRS/002` holds only SNPP (`VNP*`) products and a NOAA-20 aerosol product; direct probes of `NASA/VIIRS/002/VJ113A1`, `NASA/VIIRS/001/VJ113A1` and `NOAA/VIIRS/002/VJ113A1` all fail. Two independent methods agree. |
| HLS (fallback candidate b) | 30 m; Landsat from 2013, Sentinel-2 from 2015. | Resolves as `NASA/HLS/HLSS30/v002` (first image at a Sul de Minas point 2015-11-29, latest 2026-09-27) and `NASA/HLS/HLSL30/v002` (2013-04-19 to 2026-10-08). Both carry `Fmask`. The folders also hold `_RAW` and test variants; only `v002` is used. |
| `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad` | Community catalog: pentad, 2015 onward, weekly updates, latency under 5 days. | Resolves and is current (latest pentad 2026-10-06, matching CHC's 2026.10.2). **But the archive starts on 2025-01-01, not 2015:** 128 pentads, none dated before 2025, checked by both `aggregate_min` and a date-filtered count. |
| CHC prelim files (fallback) | Reachable. Pentad prelim current to 2026.10.2 (6–10 Oct), posted 2026-10-12. Daily `fixed/` prelim current to 2026-10-10, posted 2026-10-12. | Not an Earth Engine asset |
| `USGS/SRTMGL1_003` | Image, band `elevation`, metres, 30 m, 56°S–60°N; voids filled from ASTER GDEM v2, GMTED2010, NED. Vertical datum not stated on the GEE or Earthdata pages. | Resolves; band `elevation`. |
| `COPERNICUS/DEM/GLO30_2024_1` | Replaces the deprecated `COPERNICUS/DEM/GLO30` (Amendment 27). ImageCollection, band `DEM`, EGM2008, surface model. | Resolves; 26,475 tiles, band `DEM`. |
| ERA5-Land soil layers | Confirmed: `volumetric_soil_water_layer_1/2/3` = 0–7, 7–28, 28–100 cm, volume fraction. Weights 0.07/0.21/0.72 (Amendment 28). Catalog availability to 2026-10-07. | Resolves; 1950-01-01 to 2026-10-07; soil layers 1–3 and `temperature_2m` present. (The first run reported this as not resolving; that was a bug in the script's date conversion, which fails on Windows for dates before 1970. Fixed and rerun.) |

Also checked: `UCSB-CHG/CHIRPS/DAILY` (final) resolves, 16,679 daily images, 1981-01-01 to
2026-08-31. September's final is not yet in Earth Engine on 2026-10-13, consistent with the rule
that final for month M counts as published from the 1st of M+2.

### What this changes, pending the owner's decision

1. **VJ113A1 is not available in Earth Engine**, so under Amendment 25 the live fallback is HLS,
   subject to the rainy-season coverage test, or else a declared gap.
2. **The CHIRPS-prelim community asset cannot support the sensitivity rerun.** Amendment 9 reruns
   the vintages whose note dates fall inside the prelim archive. With an archive starting in 2025,
   only crop 2026's vintages qualify. CHC's own prelim pentad files go back to 2015. None of the
   declared fallback triggers fired (it resolves, is current and does not lag), so this needs a
   decision rather than an automatic switch. The §4 row's "2015–" is also wrong for this asset.

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

### Implementation choices for the provisional run — confirmed by the owner, 2026-10-12, before it ran

These are not in the spec and would otherwise be made silently in code:

1. **State boundaries:** FAO GAUL 2015 level 1 (`FAO/GAUL/2015/level1`) for MG and SP. This is a
   dataset not in §4, used for the provisional run only. The formal run uses IBGE municipal
   boundaries, which the regional lists need anyway. *Noted at run time:* Earth Engine flags
   `FAO/GAUL/2015/level1` as deprecated, superseded by `FAO/GAUL/2025/level1`. It still runs and is
   kept for this run as confirmed; any later run that needs state lines uses
   `FAO/GAUL/2025/level1` (owner decision, 2026-10-13).
2. **Mask year:** MapBiomas Collection 10, `classification_2024`, class 46.
3. **QA screening:** MODIS `SummaryQA` 0–1 (good, marginal); VIIRS `pixel_reliability` 0–3
   (excellent to marginal). The two QA scales are not identical; this is the closest match.
4. **"Own pixels within the mask":** each product pixel weighted by its coffee fraction, the mean
   of the 30 m mask within it; pixels with no coffee are dropped.
5. **Month assignment:** a composite belongs to the month its start date falls in. All products
   use the same rule.
6. **Denominators reported:** coffee pixels per product, and valid pixels per month.

### Results (provisional, run 2026-10-13)

**Denominators:** 543,194 MODIS pixels (250 m) and 218,967 VIIRS pixels (500 m) contain any
coffee in MG and SP. Valid pixels per month: median 99.8% (Terra), 99.2% (Aqua), 98.2% (VIIRS);
minimum 52.0%, 71.5%, 62.5%. Monthly series run 2013-01 to 2026-09. October 2026 has no composites
yet for any product, so the comparison ends in September rather than October.

Mean monthly difference in anomaly, in standard deviations of each product's 2013–2025 monthly
baseline; signed mean, with the mean absolute difference in brackets:

| Index | Pair | 2018–2023 (72 months) | 2024 to Sep 2026 (33 months) |
|---|---|---|---|
| NDVI | Terra − Aqua | +0.07 (0.37) | +0.01 (0.38) |
| NDVI | Terra − VIIRS | −0.01 (0.34) | **+0.78 (0.83)** |
| NDVI | Aqua − VIIRS | −0.08 (0.27) | **+0.77 (0.84)** |
| EVI | Terra − Aqua | +0.04 (0.58) | −0.17 (0.90) |
| EVI | Terra − VIIRS | +0.13 (0.56) | −0.20 (0.67) |
| EVI | Aqua − VIIRS | +0.09 (0.50) | −0.04 (0.67) |

NDVI by year, Terra − VIIRS: 2023 +0.23, 2024 +0.31, 2025 +0.68, 2026 +1.52. Aqua − VIIRS: −0.11,
+0.35, +0.80, +1.31. Full series: `docs/week0/drift_provisional_monthly.csv` and
`drift_provisional_summary.csv`.

### Recomputed on the July 2017–2025 common baseline (Amendment 26, second revision)

Recomputed from the saved monthly results, with no new Earth Engine compute
(`docs/week0/drift_provisional_baseline_comparison.csv`, monthly z-scores in
`drift_provisional_monthly_jul2017_baseline.csv`). Signed mean, absolute mean in brackets:

| Index | Pair | 2018–2023 | 2024 to Sep 2026 |
|---|---|---|---|
| NDVI | Terra − Aqua | +0.03 (0.43) | +0.08 (0.50) |
| NDVI | Terra − VIIRS | −0.14 (0.42) | **+0.88 (0.95)** |
| NDVI | Aqua − VIIRS | −0.17 (0.32) | **+0.80 (0.88)** |
| EVI | Terra − Aqua | +0.00 (0.66) | −0.22 (1.07) |
| EVI | Terra − VIIRS | +0.10 (0.61) | −0.23 (0.78) |
| EVI | Aqua − VIIRS | +0.10 (0.53) | −0.01 (0.73) |

NDVI by year, Terra − VIIRS: 2023 +0.22, 2024 +0.27, 2025 +0.68, 2026 +1.95.

**The conclusions do not change.** NDVI: Terra and Aqua agree, and both diverge from VIIRS from
2024, slightly more on the shorter baseline. EVI: no systematic divergence. With the shorter
baseline the standard deviations are smaller, so absolute differences rise (EVI 0.53–0.66 in
2018–23), which strengthens the case for the signed average. Against VIIRS alone, Terra's NDVI
exceeds 0.5 and its EVI does not; under Amendment 31 trigger (b) also needs HLS, which is pending.

### Findings (on the original 2013–2025 baseline)

1. **NDVI: Terra and Aqua agree; both diverge from VIIRS from 2024, growing each year.** The
   attribution rule (Terra diverging from both references while they agree) is not met, because
   Terra diverges from VIIRS only. **The cause is not established.** Three explanations fit:
   - (a) a drift shared by Terra and Aqua. Both orbits are drifting away from local noon, Terra
     earlier and Aqua later, so the sun is lower for both and NDVI could shift the same way in
     each;
   - (b) a change specific to Suomi NPP VIIRS near the end of its mission;
   - (c) pixel mixing: VIIRS's 500 m pixels hold more non-coffee cover, which may have responded
     differently to 2024–26 conditions.

   The rule as designed cannot tell (a) from (b), because it treats Aqua as an independent
   reference, and Aqua is drifting too.

   **Owner reading, 2026-10-13: the NDVI drift since 2024 is shared by Terra and Aqua, and its
   cause is unresolved pending HLS.** Amendment 31 makes VIIRS and HLS the references and reports
   Aqua alongside; HLSS30 NDVI and EVI from July 2017 join the HLS test as the second reference.
2. **EVI, the index's vegetation term (Amendment 19), shows no systematic divergence.** Signed
   differences stay within ±0.2 SD in 2024–26 for every pair. EVI disagrees more from month to
   month than NDVI does: absolute differences were already 0.50–0.58 SD in 2018–23, and the
   Terra–Aqua figure rose to 0.90 in 2024–26 (2026 alone, nine months: −0.69 signed).
3. **Provisional reading of trigger (b)** on the MG+SP total, using the signed mean: not met for
   NDVI (Terra − Aqua +0.01) or EVI (−0.17 and −0.20). This is not the formal evaluation.
4. **Trigger (b) does not say signed or absolute.** "Diverges by more than 0.5 SD, averaged over
   2024–2026" can be read either way. Read as an absolute mean, EVI would trip on ordinary
   product noise, which was already 0.50–0.58 SD in 2018–23. A signed mean measures systematic
   drift. To settle before the formal run.
5. **Trigger (b) is now a signed average** (Amendment 26, revised), for the reason in item 4.
6. **Earth Engine compute quota.** During this run the project exceeded its noncommercial quota
   (Community tier, 150 EECU-hours a month) and is in restricted mode: reduced concurrency until
   the quota resets on 1 November (Pacific time). The Contributor tier (1,000 EECU-hours a month)
   needs a billing account, has no charge for noncommercial use, and applies as soon as the tier is
   changed. The owner is moving the project to Contributor. **Compute cost of this run: not
   measured** (it predates Amendment 32); from now on every run's EECU cost is recorded here.

## 4. Live vegetation fallback: VJ113A1 and HLS (Amendments 25 and 30)

Both candidates are tested and reported before one is chosen. VJ113A1: whether it is in the Earth
Engine catalog and current (`gee/week0_verify_ids.py`).

### HLS implementation choices — confirmed by the owner, 2026-10-12, before the test runs

1. **Product and baseline:** HLSS30 only, baseline July 2017 to December 2025 (first rainy season
   2017/18, Sentinel-2 A and B; 2C as A's replacement in 2024–25). HLSL30 coverage is reported
   separately, as information.
2. **Coverage:** the share of mask pixels with at least one clear HLSS30 observation in the month.
   Clear means Fmask flags none of cloud, cloud shadow, adjacent cloud or snow.
3. **Mask:** the provisional MG/SP coffee mask used by the provisional drift check (MapBiomas
   Collection 10, `classification_2024` == 46, inside GAUL level 1 MG and SP), labelled
   provisional.
4. **Sample:** a fixed random sample of 20,000 mask pixels, **seed 20261012**. The sampling margin
   on a share is about ±0.7 percentage points (95%).
5. **Reported as information, outside the baseline:** monthly observation counts for January–March
   2017, so the single-sensor step is visible, and HLSL30 coverage.
6. **Rainy-season test (Amendment 30):** coverage below 60% in more than two of the November–March
   months in the baseline means HLS cannot carry the rainy season; the fallback then falls to
   VJ113A1 or, failing that, a declared gap.

### Further implementation details — set before the run, within the confirmed method; for owner review

7. **State lines:** GAUL 2025 level 1 (`FAO/GAUL/2025/level1`), following the owner's rule that
   later runs use GAUL 2025. The drift check used GAUL 2015, so the two masks can differ slightly
   along state borders.
8. **Bands:** NIR is HLSS30 `B8A` (narrow NIR) and HLSL30 `B5`; red `B4`; blue `B2`. The bands
   are reflectance already (checked on images, 2026-10-13), so no scale factor is applied.
9. **Per-point monthly value:** the median of that point's clear observations in the month,
   robust to leftover cloud. EVI values outside −1 to 1 are screened out. The month's value is
   the mean over points with data.
10. **"Any" coverage** (at least one observation of any quality) is reported beside clear coverage,
    so gaps in Earth Engine's HLS archive are not mistaken for cloud. Earth Engine's catalog page
    says historical HLS ingestion was expected to finish in 2025.
11. **Observation counts** can double-count where Sentinel-2 tiles overlap; coverage (at least one
    observation) is not affected.
12. **The sample is drawn once and its coordinates reused,** so it is not recomputed for every
    month (Amendment 32).
13. **No anomalies yet:** the script saves the monthly series only. The baseline for comparisons
    with HLS is open (§10), so the third-reference comparison waits for that decision.
14. **Cost:** a one-month probe runs first to measure EECU cost before the full run.

### Option C and the scaling probe — rule set before the probe runs (owner decision 2026-10-13)

Option C: 5,000 points, a seeded random subset of the 20,000-point sample (numpy
`default_rng(20261012)`); HLSS30 for every month 2017-01 to 2026-09; HLSL30 for November–March
months only, as information. The scaling probe runs one month at 5,000 points on **February 2025**,
not January, because January's tiles may still be cached from the 20,000-point probe and would
understate the cost. **Pass rule:** cost per granule touched (HLSS30 + HLSL30) at 5,000 points is
at most 35% of the 20,000-point probe's cost per granule (perfect scaling is 25%). If it passes,
option C runs and its actual total is recorded here; if not, the run stops and the numbers are
reported.

### Scaling probe result (2026-10-13): **fails the pass rule; option C not started**

| Probe | Points | Granules touched (HLSS30 + HLSL30) | EECU-seconds | Per granule |
|---|---|---|---|---|
| January 2025 | 20,000 | 1,713 + 1,148 = 2,861 | 22,110 | 7.73 |
| February 2025 | 5,000 | 1,815 + 1,322 = 3,137 | 12,288 | 3.92 |

Cost per granule at 5,000 points is **51%** of the 20,000-point figure; the rule allowed 35%.
Quartering the points only halved the cost, because most of it is per-granule overhead, not
per-point work. At this rate option C would cost about 275 EECU-hours, not 130. Profile:
`docs/week0/profiles/hls_probe_5000pts_20261013T145010Z.txt`. February 2025 values, as
information: HLSS30 clear coverage 93.3% (4,666 of 5,000), NDVI 0.776, EVI 0.579; HLSL30 85.8%.

**Found afterwards (a metadata count with no pixel computation):** the script selects every
granule intersecting the MG/SP bounding box. Only 679 of the 1,815 HLSS30 granules and 471 of the
1,322 HLSL30 granules in February 2025 contain a sample point (37% and 36%). Selecting by the
sample points instead would not change any result, because a granule without a point contributes
nothing, and should cut cost by roughly that factor. Not applied; owner decision.

### Re-probe with the image filter — rule set before it runs (owner decision 2026-10-13)

The script now selects only granules that contain a sample point; results are unchanged by
construction. One month at 5,000 points, **December 2024** (a rainy month not probed before, so no
cached tiles), both products. **Pass rule: at most 1.2 EECU-hours (4,320 EECU-seconds) for the
month, both products together**, which keeps option C under about 150 EECU-hours. If it passes,
option C runs and its actual total is recorded here; if not, the run stops and the project moves
to option D (the coverage test only).

### Re-probe attempt 1 failed to run; HLSS30 date-line granules found (2026-10-13)

- The point-based filter, applied inside the monthly computation, hit Earth Engine's user memory
  limit on all five tries for December 2024. The run was stopped; there is no cost figure for it.
- **Finding: HLSS30 in Earth Engine contains granules with infinite footprints.** They are on
  date-line tiles (UTM zones 01 and 60, e.g. `T01FBF`, footprint bounds ±infinity), so
  `filterBounds` returns them for any point on Earth. At one Varginha point in December 2024,
  56 of the 61 HLSS30 granules returned were these; 5 were from the real tile `T23KMS`. HLSL30 is
  unaffected. Over the MG/SP bounding box in February 2025 they were 80 of 1,815 HLSS30 granules,
  but each one intersects every sample point, so they dominated the per-point work in the earlier
  probes. They hold no data over Brazil, so no value computed so far is affected; only cost was.
- **Fix, within the owner's image-filter decision:** keep granules from UTM zones 21–24 (MG and
  SP lie in 22–24; 21 is a margin because tiles extend past zone edges), and restrict each month
  to the MGRS tiles whose granules contain a sample point, listed once from 2024's granule
  metadata. No geometry test runs inside the monthly computation. February 2025 counts: HLSS30
  1,735 granules in zones 21–24 over the bounding box, 599 on point tiles; HLSL30 471 on point
  tiles.
- **Probe month moves from December 2024 to November 2024**, because December 2024 was partly
  computed in the failed attempts and could be cached. The pass rule is unchanged: at most 1.2
  EECU-hours for the month, both products.
- **Attempt 2 also stopped before the probe:** listing the point tiles from a full year of granules
  in one request exceeded the memory limit. The listing now runs in ten batches of 500 points over
  two dry-season months (July–August 2024), zone filter first. Result: **86 tiles** contain sample
  points, and the HLSS30 and HLSL30 lists are identical, as they should be on the shared HLS
  tiling.

### Re-probe attempt 3 (November 2024): **fails the pass rule; option C not started**

7,891 EECU-seconds for the month (limit 4,320), on 1,017 granules (585 HLSS30, 432 HLSL30). The
one-off tile listing is about 23 of those seconds. The image filter cut granules touched by about
two-thirds but cost by about a third: each remaining granule contains points and does more work,
and Earth Engine overhead is still about 65% of the cost. Option C at this rate would be about 185
EECU-hours. November 2024 values, as information: HLSS30 clear coverage 77.5% (3,875 of 5,000),
NDVI 0.730, EVI 0.540; HLSL30 74.0%. Profile:
`docs/week0/profiles/hls_probe_5000pts_20261013T153040Z.txt`.

**HLSS30 footprint issue filed with Google:** draft in `docs/week0/ee_issue_hlss30_footprints.md`;
issue number to be added here once the owner files it.

### Option D and the reference series — rules set before they run (owner decisions 2026-10-13)

- **HLSL30 dropped.** It was probed at 62–86% clear coverage in three months (January 2025 62.4%,
  February 2025 85.8%, November 2024 74.0%) and not tested further.
- **Option D, the coverage test only:** HLSS30, 5,000 points, no NDVI or EVI, the 42
  November–March months in the July 2017–2025 baseline plus January–March 2017 as information (45
  months). Probe first on **January 2024** (not computed before). **Pass rule: at most 1.0
  EECU-hours (3,600 EECU-seconds) for the month.** If it passes, D runs and its actual total is
  recorded; if not, it stops and is reported.
- **Reference series, sized for the drift question only:** HLSS30 NDVI and EVI at **500 points**,
  a nested subset (the 5,000 drawn with seed 20261012, then 500 of those with **seed 20261013**),
  every month July 2017 to September 2026 (111 months), with the tile filter. Probe first on **June
  2022** (not computed before). **Pass rule: at most 0.15 EECU-hours (540 EECU-seconds) for the
  month**, which keeps the series under about 17 EECU-hours. If it fails, HLS stays out as a
  reference and Amendment 31's NDVI question stays open. The drift comparison is about systematic
  differences between years, not precision at any point, so 500 points is enough.

### Option D result (2026-10-13): **HLS fails the rainy-season coverage test**

- **Gate:** the January 2024 probe cost 3,076 EECU-seconds (limit 3,600): passed.
- **Run:** 45 months, HLSS30, 5,000 points, 56 minutes. **Actual cost 121,910 EECU-seconds
  (33.9 EECU-hours)**; with the probe, option D cost 35.7 EECU-hours. Profile in
  `docs/week0/profiles/`; monthly results in `docs/week0/hls_coverage_5000pts.csv`; the 42 test
  months in `docs/week0/hls_coverage_test.csv`.
- **Result: 7 of the 42 November–March baseline months fall below 60% clear coverage; the rule
  allows 2.** The seven: December 2017 53.9%, November 2018 40.5%, January 2020 54.2%, February
  2020 31.7%, December 2020 55.6%, February 2021 51.9%, December 2022 35.5%. The median month is
  80.1%. **Under Amendment 30, HLS cannot carry the rainy season.**
- **The failures are cloud, not archive gaps:** "any" coverage (an observation of any quality) is
  100% in every baseline month, at 4.3–9.4 observations per point.
- **By season**, mean clear coverage: 2017/18 71.9%, 2018/19 82.0%, 2019/20 64.5%, 2020/21 75.6%,
  2021/22 80.3%, 2022/23 72.8%, 2023/24 87.9%, 2024/25 84.6%, and November–December 2025 95.2%.
- **Information, January–March 2017** (Sentinel-2A only): clear coverage 17.7%, 38.1% and 76.9%,
  at about 2.3 observations per point against 4.3–9.4 in the baseline. The single-sensor step is
  visible, as expected.
- **Consequence (Amendment 25, revised):** the live vegetation fallback moves to (b), VJ113A1
  ingested from NASA as a private asset over the MG/SP window. Not started: it needs the owner's
  go-ahead, including for the download.

### Reference-series gate (2026-10-13): **fails; HLS stays out as a drift reference**

- **Probe:** June 2022, 500 points (nested subset, seed 20261013; 56 tiles contain them), NDVI and
  EVI: **3,025 EECU-seconds against a limit of 540.** The 111-month series was not run.
- **What the probes show about cost:** it barely depends on the number of points. January 2024
  coverage at 5,000 points cost 3,076 EECU-seconds; June 2022 with indices at 500 points cost
  3,025. Almost all of it is per-granule overhead, so fewer points cannot buy a cheaper series. At
  about 0.85 EECU-hours a month the reference series would be about 93 EECU-hours; it is not
  proposed.
- **June 2022 values, as information:** clear coverage 99.4% (497 of 500), NDVI 0.739, EVI 0.455.
- **Consequence (owner rule):** HLS stays out as a reference, and Amendment 31's NDVI question (a
  drift shared by Terra and Aqua, or a VIIRS-specific change) **stays open**. The NDVI caveat of
  Amendment 33 stands.
- **Open, for the owner:** trigger (b) is defined against both references, VIIRS and HLS
  (Amendment 31). With HLS out, it cannot be evaluated as written, and VIIRS delivery ends on
  2 November 2026.

### VJ113A1 ingestion: scoping only, no download (owner request 2026-10-13)

Sources checked: NASA's Common Metadata Repository (public metadata, no login) and the AppEEARS
product API.

- **Product:** VJ113A1 version 002, "VIIRS/JPSS1 Vegetation Indices 16-Day L3 Global 500m SIN
  Grid" (NOAA-20), collection `C2519122065-LPCLOUD`, LP DAAC, **2018-01-01 to present**. The latest
  composite starts 2026-09-14. Composites are 16-day, starting every 8 days, so 46 a year.
- **Layers needed:** `500_m_16_days_EVI`, `500_m_16_days_NDVI` (scale 0.0001, fill −15000, valid
  −1 to 1), and `500_m_16_days_pixel_reliability` (0–11, fill −4).
- **Tiles:** MG and SP coffee lies in sinusoidal tiles h13v10, h13v11, h14v10 and h14v11. A
  bounding-box search also returns h12v10 and h12v11, which touch only the box's corners.
- **Files (route A, whole HDF5 granules):** `VJ113A1.A{YYYYDDD}.h{13,14}v{10,11}.002.{production}.h5`
  from `https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/VJ113A1.002/`: **1,604
  files, 93.9 GB** (median 82 MB; h14v11 is mostly ocean and its files are small). Each would be
  read, the three layers extracted and clipped, and the original deleted. The local raster library
  reads HDF5 (checked). Georeferencing from the tile index has to be built, since GDAL may not
  georeference these files on its own.
- **Files (route B, AppEEARS area subset):** the same three layers for the MG/SP polygon,
  2018-01-01 to present, delivered as GeoTIFFs by NASA. That is roughly 1,200 files for 401
  composites; size is not measurable without submitting a request, but it should be a small
  fraction of route A because only the window and three layers are delivered. Queue time for a
  request this long is unknown, from hours to days.
- **Login:** both routes need a **NASA Earthdata Login** account (free), which only the owner can
  create. Route A then needs an Earthdata bearer token in `.env`; route B needs an AppEEARS session
  token, which the owner obtains by logging in. No password is handled by the scripts.
- **Baseline:** 2018–2025 (owner decision), shorter than the July 2017–2025 baseline of the other
  products; stated wherever VJ113A1 is used. VJ213A1 (NOAA-21) exists but starts 2023-02-10, too
  short for a baseline.
- **Feasibility before the December note: yes, if the Earthdata login is in place by early
  November.** Route B is the lighter route; route A is the fallback if AppEEARS's queue is slow.
  After download the path is the proven one: bucket, ingestion, value check against the source
  files, then the 2018–2025 baseline. Not covered: the rainy-season coverage test was written for
  HLS. VJ113A1's 16-day composites should cover nearly every pixel by design, but its
  pixel-reliability share over the mask should be checked the same way before it is relied on.

### VJ113A1 AppEEARS request (route B), submitted 2026-10-13 18:36 UTC

- **Task ID `145e0b79-00e3-41c2-b1c8-eeea5e7e4d49`**, status *pending* at submission.
- Product VJ113A1.002; layers `500_m_16_days_EVI`, `500_m_16_days_NDVI`,
  `500_m_16_days_pixel_reliability`; dates 2018-01-01 to 2026-10-13; output GeoTIFF in the
  product's **native** sinusoidal grid (no resampling).
- Area: GAUL 2025 level 1 Minas Gerais + São Paulo, simplified at 500 m and buffered by 1 km
  (13,575 vertices). Request body without the token: `docs/week0/appeears_vj113a1_request.json`;
  task record: `docs/week0/appeears_vj113a1_task.json`; script: `gee/vj113a1_appeears.py`.
- **Backup:** if the request is not complete by about 18:36 UTC on 2026-10-16 (three days), switch
  to route A, whole-file download from LP DAAC.
- Downloading the results needs a valid AppEEARS token; the owner's tokens expire about 48 hours
  after issue.

### VJ113A1: download, ingestion and acceptance check — plan and gates, set before they run (2026-10-14)

- **AppEEARS output:** task done 2026-10-13 22:25 UTC; **1,613 files, 10.62 GB**. That is 1,604
  GeoTIFFs (401 composites from 2018-01-01 to 2026-09-14, × 4 layers) and 9 small files (lookup
  tables, QA statistics, granule list). AppEEARS added `VI_Quality` (401 files, 0.43 GB) without
  it being requested; it is downloaded for the record but not ingested.
- **Files:** int16 as published (EVI and NDVI × 0.0001, fill −15000), LZW-compressed, native
  sinusoidal grid at 463.3 m, 2,595 × 2,664 pixels covering the MG/SP box. Uploaded unchanged; no
  re-encoding.
- **Download** (`gee/vj113a1_download.py`): one file at a time, resumable, SHA-256 per file in
  `data/raw/vj113a1/manifest.csv`.
- **Ingestion** (`gee/vj113a1_ingest.py`): one image per composite in
  `projects/<EE_PROJECT>/assets/vj113a1_mgsp`, bands EVI, NDVI and pixel_reliability.
  **Gate 1:** ingest 5 composites, verify them, then the remaining 396.
- **Verification** (`gee/vj113a1_verify.py`): the collection loads with the expected count, dates
  and bands; 15 valid pixels (5 random composites × 3 bands) match the source files, and 15 fill
  pixels are masked.
- **Acceptance check** (`gee/week0_vj113a1_coverage.py`, Amendment 30, second revision): the same
  provisional MG/SP mask as the HLS test, coffee-fraction weighted. **Gate 2:** probe January 2024
  first, at most 0.25 EECU-hours (900 EECU-seconds); then the 40 November–March months of
  2018–2025.
- **Storage:** about 10 GB in the bucket (US multi-region), roughly $0.26 a month. Deleting the
  bucket copies once the Earth Engine assets are verified is the owner's call.

### Compute used on 2026-10-13, measured (Amendment 32)

| Run | EECU-hours |
|---|---|
| HLS sample, batch (20,000 points) | 8.0 |
| HLS probe, January 2025, 20,000 points, both products | 6.1 |
| HLS probe, February 2025, 5,000 points, both products | 3.4 |
| HLS re-probe, November 2024, 5,000 points, both products, tile filter | 2.2 |
| Option D probe (January 2024) and run (45 months) | 35.7 |
| Reference probe, June 2022, 500 points | 0.8 |
| **Total measured** | **56.2** |

Not measured: the provisional drift check and its first attempt, the timed-out sample attempt, the
failed re-probe attempts, the ID checks, and the CHC ingestion (Earth Engine reported no EECU on
the ingestion tasks).

### Probe results (2026-10-13), and the cost of the full run

- **The sample is drawn:** 20,000 points, seed 20261012. Drawing it interactively hit Earth
  Engine's time limit (that attempt's cost was not captured), so it ran as a batch export to the
  bucket: **28,950 EECU-seconds (8.0 EECU-hours)**, one-off. Coordinates are cached locally.
- **One month (January 2025), both products: 22,110 EECU-seconds (6.1 EECU-hours)** interactive,
  17 minutes wall time including the sample. Profile: `docs/week0/profiles/hls_probe_20261013T142120Z.txt`.
  About 60% of it is Earth Engine overhead from the number of images touched (1,713 HLSS30 and
  1,148 HLSL30 granules over the MG/SP bounds in one month), not the arithmetic.
- **January 2025 values:** HLSS30 clear coverage 79.4% (15,887 of 20,000 points), any coverage
  100%; 1.7 clear observations per point (7.7 of any quality, overlaps included); NDVI 0.789,
  EVI 0.604 (mean over points). HLSL30 clear coverage 62.4% (12,473 of 19,995 points with data).
  One rainy-season month above the 60% threshold is not the test; it only shows the method works.
- **Full run as designed:** about 113 months × 6.1 ≈ **690 EECU-hours**, roughly 15 hours of wall
  time. That is about 70% of the Contributor tier's 1,000 EECU-hours for October, on top of what
  the drift check already used. **Not started; owner decision under Amendment 32.**

### Results

Pending Earth Engine access.

## 5. CHC prelim download (Amendment 9, revised)

Scope (owner decision, 2026-10-13): every pentad from 2015; daily for September–November
2015–2025 and from 2026-05-01. In total, 848 pentads and 1,159 days (`gee/chc_prelim_fetch.py`).

- **First attempt blocked.** It used four parallel connections. After 122 pentads (2015-01-1 to
  2016-09-2, all complete files), CHC's server answered 403 to every request from this machine,
  including its directory listing, from about 05:34 PDT on 2026-10-13. The run was stopped at once.
  A single check about 16 minutes later was still refused.
- **Change made:** the script now fetches one file at a time with a 3-second pause, identifies the
  project in its User-Agent, and stops completely on the first 403 or 429.
- **Retry:** not before about 06:00 PDT on 2026-10-14 (owner decision: wait 24 hours). If CHC still
  refuses then, the download stops and the owner contacts CHC.
- **Interim, owner decision 2026-10-13:** until CHC's archive is complete, live-season months not
  yet final use the community-catalog asset `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad`,
  and every note says so. That asset is pentad-only, so dry-day counts for prelim months are
  reported as not yet available until CHC's daily files are in. The 2015–2024 pentads are needed
  only for the backtest-stage sensitivity rerun, so note 1 does not depend on them. Logged as a
  temporary deviation in `SPEC_CHANGELOG.md`.
- **Ingestion** (`gee/chc_prelim_ingest.py`): billing is on and the bucket
  `brazil-arabica-index-ingest` exists (owner-created 2026-10-13; US multi-region, uniform access,
  public access prevented). The first run for the 122 downloaded pentads **stopped before
  uploading anything**: Earth Engine reports that the project's asset folder
  (`projects/<EE_PROJECT>/assets`) does not exist or does not allow this login to create assets,
  so the collection could not be created. Not yet resolved; the bucket is untouched. A dry run
  also exposed a counting bug (totals carried over from pentad to daily), now fixed.
- **Diagnosis, 2026-10-13, after the owner confirmed `GCS_BUCKET` in `.env` and both Google
  accounts as project Owners:**
  - Creating the collection still fails the same way.
  - The Cloud Resource Manager API was enabled on the project (owner-authorised) to test
    permissions directly. The authenticated account **holds every permission involved**:
    `earthengine.assets.create`, `.list` and `.get`, `earthengine.imports.create`,
    `earthengine.exports.create`, `earthengine.computations.create`,
    `serviceusage.services.use`, `resourcemanager.projects.get` and `storage.buckets.create`.
  - The Earth Engine API is enabled, and the project's Earth Engine config reads
    `registrationState: REGISTERED_NOT_COMMERCIALLY`.
  - Called directly on the REST API, both listing the project's root (`projects/<EE_PROJECT>:listAssets`)
    and creating an asset in it return 404, "Asset 'projects/<EE_PROJECT>/assets' does not exist".
  - **What is missing is the project's asset root itself, not a permission.** Batch exports to
    the bucket work, since they need no asset. Fixing the root needs a step outside the API calls
    tried here: selecting the project in the Code Editor's Assets panel, or Earth Engine support.
- **Resolved, 2026-10-13:** the owner created a folder (`assets/test`) under the project in the
  Code Editor, which provisioned the asset root. The API login could then see it, so the
  credential's account was never the problem.
- **Ingestion proven end to end (122 pentads), 2026-10-13:**
  - 122 files uploaded to `gs://brazil-arabica-index-ingest/chc_prelim/pentad/`; 122 ingestion
    tasks, **122 succeeded, 0 failed**, in about 6 minutes. Earth Engine reported no EECU usage on
    the ingestion tasks.
  - The collection `projects/<EE_PROJECT>/assets/chc_prelim_pentad_mgsp` **loads**: 122 images,
    2015-01-01 to 2016-09-06 (the start of pentad 2016.09.2), band `precipitation`, EPSG:4326,
    0.05° (about 5,566 m). The empty daily collection `chc_prelim_daily_mgsp` was created too.
  - **Values:** 15 of 15 land pixels (3 each in 5 random pentads) match the local clipped files to
    within 0.001 mm.
  - **Missing data:** 5 of 5 cells that are −9999 locally (ocean) are masked in Earth Engine.

## 6. Regional municipality lists (§3) — PROPOSAL, not registered

**Which IBGE units Conab uses: the 1989 mesoregions**, not the 2017 intermediate regions. Conab's
September 2026 bulletin (3rd survey, safra 2026, p. 17) describes Minas Gerais coffee "with
prevalence in some *mesorregiões* … such as the Sul e Centro-Oeste mineiro, the Triângulo, the
Alto Paranaíba, the Noroeste, the Zona da Mata, the Vale do Rio Doce and the Zona Central". The
bulletin does not publish a membership list.

**Conab's data table** (`site_previsao-de-safra-cafe-set-2026.xls`, sheet "2 Café Arábica")
reports arabica area in production, yield (sc/ha) and production for the four Minas regions,
and **São Paulo only as a state total**. For §4c, the São Paulo target is therefore the state
total, the spec's fallback. The text names São Paulo's coffee areas (Alta Mogiana, Média
Mogiana, Alta Paulista, Circuito das Águas) but gives no figures for them.

**Proposed membership** (`docs/week0/proposed_region_membership.csv`: every municipality with its
IBGE code, mesoregion, proposed Conab region, whether it is in the index, the basis of the
assignment, and PAM 2025 arabica area):

| Conab region | IBGE mesoregions | Municipalities | In index |
|---|---|---|---|
| Sul e Centro-Oeste | Sul/Sudoeste de Minas, Oeste de Minas | 190 | yes |
| Triângulo, Alto Paranaíba e Noroeste | Triângulo Mineiro/Alto Paranaíba, Noroeste de Minas | 85 | yes |
| Zona da Mata, Rio Doce e Central | Zona da Mata, Vale do Rio Doce, Central Mineira, **Campo das Vertentes**, **Metropolitana de Belo Horizonte** | 415 | yes |
| Norte, Jequitinhonha e Mucuri | Norte de Minas, Jequitinhonha, Vale do Mucuri | 163 | no |
| São Paulo (state total) | all of SP | 645 | yes |

**The two mesoregions the bulletin does not name**, tested by comparing IBGE PAM 2025 arabica
"área destinada à colheita", summed under each assignment, with Conab's 2025 area in production:

| Region | PAM 2025 (ha) | Conab 2025 (ha) | Difference |
|---|---|---|---|
| Sul e Centro-Oeste | 537,951 | 521,815 | +3.1% |
| Triângulo, Alto Paranaíba e Noroeste | 216,208 | 195,941 | +10.3% |
| Zona da Mata, Rio Doce e Central | 292,696 | 319,734 | −8.5% |
| Norte, Jequitinhonha e Mucuri | 31,233 | 29,293 | +6.6% |
| São Paulo | 195,539 | 196,025 | −0.2% |

With Campo das Vertentes (24,559 ha) in Sul e Centro-Oeste instead, the differences become
+7.8% and −16.1%, so the proposal puts it in Zona da Mata, Rio Doce e Central. Metropolitana de
Belo Horizonte has 816 ha and goes with "Central" on geography. **Both are provisional.** PAM and
Conab measure different things (area destined for harvest against Conab's surveyed area in
production), so gaps of around 10% are expected, and the test is suggestive, not proof. The
Triângulo gap (+10.3%) would shrink if Noroeste de Minas were counted elsewhere, but Conab's
region name includes Noroeste, so it stays. A direct answer would come from Conab's Minas Gerais
office.

**Coverage:** the four index units hold 83.4% of Brazil's 2026 arabica area in production and
83.1% of production (Conab). 120 of the 1,498 MG and SP municipalities have no PAM 2025 arabica
figure (suppressed, or no coffee).

## 7. Conab survey timing (Amendment 8, revised 2026-10-14): the 2026 first survey came on 5 February

Conab's page lists the 1st survey of safra 2026 on **5 February 2026** and the 4th survey of
safra 2025 on 4 December 2025. Amendment 8 says first surveys came "between the 18th and 28th
[of January] in recent years"; 2026 broke that. If the first 2027 survey also comes after 31
January, Amendment 22's fallback applies: note 3 goes out on 1 February without the Conab line,
and a scorecard addendum follows the survey. The 2027 dates are still to confirm from Conab's
calendar.

## 8. INMET station set (§5 step 4) — blocked

Both INMET hosts (`portal.inmet.gov.br`, `apitempo.inmet.gov.br`) resolve to 201.57.198.188 and
accept the connection, then reset it as the secure session starts ("Recv failure: Connection was
reset"). This is the server refusing this machine, the same failure the spec recorded in an
earlier sandbox. The station set needs (1) INMET's catalogue of automatic stations (code,
coordinates, altitude, start date) and (2) the annual hourly archives for 2008–2026 for the
completeness rule. Once the catalogue exists, the coffee-area weights within 25 km and the
per-region elevation cut can be computed. The region polygons for the elevation cut can come from
IBGE's mesh API, which is reachable from here, without a file download.

### INMET through the in-app browser (2026-10-14): reachable, read-only check

The desktop app's built-in browser reaches INMET where scripts from this machine are reset.
Nothing was downloaded: the archive sizes come from HEAD requests, and the catalogue counts were
computed on the page.

- **Annual archives** (`https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip`), 2000
  to 2026; the 2026 file runs "até 30/09/2026", so it includes June–August 2026. Needed:
  **2008–2026, 19 files, about 1.90 GB**:

  | Year | Bytes | Last-Modified |
  |---|---|---|
  | 2008 | 75,952,778 | 2020-09-02 |
  | 2009 | 88,288,168 | 2020-09-02 |
  | 2010 | 90,166,397 | 2020-09-02 |
  | 2011 | 92,552,099 | 2020-09-02 |
  | 2012 | 97,765,892 | 2020-09-02 |
  | 2013 | 99,630,718 | 2020-09-02 |
  | 2014 | 98,909,484 | 2020-09-02 |
  | 2015 | 97,967,689 | 2020-09-02 |
  | 2016 | 102,439,056 | 2020-09-02 |
  | 2017 | 109,677,898 | 2020-09-02 |
  | 2018 | 117,898,042 | 2020-09-02 |
  | 2019 | 117,560,201 | 2020-09-02 |
  | 2020 | 103,653,055 | 2021-01-04 |
  | 2021 | 80,571,564 | 2022-02-03 |
  | 2022 | 90,362,801 | 2023-01-05 |
  | 2023 | 107,069,252 | 2024-01-02 |
  | 2024 | 102,772,199 | 2025-01-02 |
  | 2025 | 90,898,634 | 2026-03-20 |
  | 2026 | 136,911,232 | 2026-10-05 |

- **Station catalogue**: `https://portal.inmet.gov.br/paginas/catalogoaut`, an HTML table of
  **636 automatic stations** (name, state, status, latitude, longitude, altitude, installation
  date, code) with a "Download CSV" button.
- **Candidate pool, as information** (catalogue only, before the completeness rule): installed
  before June 2008, as needed for a complete 2008 June–August record, MG 49 (43 operating now)
  and SP 26 (24). Neighbouring states, whose stations may fall within 25 km of the mask: GO 21,
  DF 1, ES 5, RJ 14, PR 21, MS 17, BA 27. The catalogue lists only stations currently registered.
- **Catalogue, saved 2026-10-14: scraped from the page, not downloaded.** The page's "Download
  CSV" button returned nothing for the owner, so the station table was read from the rendered page
  in the in-app browser (read-only, original Portuguese, untranslated) and saved as
  `data/raw/inmet/catalogo_estacoes_automaticas.csv`: 636 stations, 43,473 bytes. Its SHA-256
  (`34d60b08…b739db`) matches the hash computed in the browser on the scraped text, so it is an
  exact copy of what the page displayed. Provenance is in `data/raw/inmet/SOURCE.md`.
- **Next:** the owner downloads the 19 archives into `data/raw/inmet/`, with retrieval dates and
  checksums. The station set, its completeness, coffee-area weights and the
  elevation cut are then computed as a proposal.

## 9. Other Week 0 checklist items, not yet started

Conab granularity (§4c, blocking); Conab's IBGE unit system and municipality lists; INMET route,
daily minima and Jun–Aug 2026 availability; CHIRPS circularity; MapBiomas 2025 collection; Conab
2027 dates; Planet quota; ICE terms.
