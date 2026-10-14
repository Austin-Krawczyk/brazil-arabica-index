# Pre-registration

Every choice that could be tuned, recorded before the results that could tempt a change (§9,
Amendment 15). Two tagged commits fix it:

- **`prereg-1`**, before W2 computes any season-level input.
- **`prereg-2`**, before the first backtest run: values that need data but not results.

Entries are added as they are decided. **Neither tag has been applied yet.** Any change after an
entry's tag is logged in `SPEC_CHANGELOG.md` and listed in the backtest report.

**Status words.** "Decided" means the spec already fixes the value. "**OPEN**" means a decision
the owner has not yet made; nothing here fills one in. Every OPEN item in prereg-1 must be
decided before the tag.

## prereg-1 — to be fixed before W2 (not yet tagged; draft of 2026-10-14)

Amendment 15's list: the feature list, with each input's source, window and standardisation;
the weighting method and the terms counted toward the cap of four; the direction pass marks; the
frost tier constant values.

### A. Seasons and windows (§3a)

| Item | Value | Source | Status |
|---|---|---|---|
| Season label | Season S is the crop harvested in year S (Conab safra S, trade S/S+1) | §3a | decided |
| Pre-flowering dry season | May–Aug of S−1 | §3a | decided |
| Frost exposure | Jun–Aug of S−1 | §3a | decided |
| Flowering | Sep 1–Nov 30 of S−1 | §3a, §5 step 3 | decided |
| Bean fill | Dec 1 of S−1 to Mar 31 of S | §3a, §5 step 3 | decided |
| Harvest rain | May–Sep of S: not an input (falls after every note on crop S) | §5 step 3 | decided |
| Backtest seasons | Without frost: crops 2001–2025. With frost: crops 2009–2025 | §5 step 8 | decided, **but see the §4c finding under G** |
| Note dates per vintage (November, December, January) in the backtest | The calendar date each vintage's inputs are cut at. Production: note 1 late November; index notes in the first week of each month; the post-survey note within five business days of Conab's first survey, or 1 February (§6) | §5 step 8, §6 | **OPEN: fixed calendar dates per vintage** |

### B. The four fitted inputs (stage 2, the cap of four; §5 step 6)

| Input | Source and band | Window | Aggregation | Standardisation | Status |
|---|---|---|---|---|---|
| **EVI anomaly** | `MODIS/061/MOD13Q1`, band `EVI` (× 0.0001), 250 m, 16-day | **OPEN:** which 16-day composites enter a season's reading at each vintage, and how they are combined into one value | Per 16-day window, area-weighted median over the mask, cloud-masked (§5 step 2) | z-score against the same 16-day window across the baseline years (§5 step 2), refitted without the held-out season (§5 step 8) | Source and z-score decided. **OPEN: the composite set per vintage, and the cloud/QA rule (which `SummaryQA` values pass)** |
| **Flowering rain deficit** | `UCSB-CHG/CHIRPS/DAILY` (final) for the backtest; CHC prelim (§4) for current months not yet final | Sep 1–Nov 30 of S−1 | Total over the mask | **OPEN:** z-score of the total, or deficit as a share of normal; and how a window still open at the note date is treated (to-date total against to-date normal?) | Source and window decided. **OPEN: deficit definition and to-date rule** |
| **Dry-season root-zone soil moisture** | `ECMWF/ERA5_LAND/HOURLY`, `volumetric_soil_water_layer_1`–`_3`, weighted **0.07 / 0.21 / 0.72** by layer thickness (0–7, 7–28, 28–100 cm) | May–Aug of S−1 | Over the mask | Anomaly against the same window across the baseline years (§5 step 5). **OPEN: z-score or raw anomaly** | Source, layers, weights and window decided (Amendment 28) |
| **Heat days in flowering** | `ECMWF/ERA5_LAND/HOURLY`, `temperature_2m` | Sep–Nov of S−1 | Days with maximum temperature above **34 °C**, over the mask | **OPEN:** standardisation; the day boundary for the daily maximum (UTC or local) | Threshold and window decided. **OPEN: day boundary; how the count is aggregated over the mask** |

| Item | Value | Source | Status |
|---|---|---|---|
| EVI as the single vegetation term | EVI, because NDVI saturates in dense coffee canopies and EVI was designed for that case | §5 step 6, Amendment 19 | decided |
| Regional aggregation | §5 step 2 says area-weighted median over the mask; §3 says municipality values aggregated to region by IBGE PAM coffee area. These are two different estimators | §3, §5 step 2 | **OPEN: which one, or which applies to which input** |
| Four-region total | Weighted by IBGE PAM harvested area or by production | §10 still-open item 2 | **OPEN** |
| Cerrado irrigation adjustment | If adopted, a fixed multiplier on the rain inputs for Triângulo, not a parameter | §5 step 6, §10 still-open item 4 | **OPEN: adopted or not, and its value** |
| Vegetation product rules | `MOD13Q1` primary. Trigger (a): no composite ending within 32 days of a note date. Trigger (b): signed average EVI divergence from VIIRS above 0.5 SD over 2024–2026 (four-region total or two or more regions), evaluated once in Week 0. Fallback (b), VJ113A1, accepted 2026-10-14, with its anomaly against its own 2018–2025 baseline | §4a; Amendments 25, 26, 30, 31, 33 | decided; trigger (b) awaits the formal per-region drift run |
| Rainfall product rules | Final CHIRPS for the baseline and the whole backtest. CHC prelim only for current-season months not yet final; final for month M counts as published from the 1st of M+2. Sensitivity rerun with prelim substituted | §9, Amendment 9 (revised) | decided |
| Data availability at a note date, besides CHIRPS | Publication lags for `MOD13Q1` composites and ERA5-Land, used to cut each vintage's inputs | §5 step 8 ("only inputs available as of each note date") | **OPEN: the lag for each** |

### C. Computed and reported, not fitted (§5 step 6)

| Item | Value | Status |
|---|---|---|
| NDVI anomaly | As EVI, in the sensitivity report only. The report states the 2024–26 NDVI drift of unresolved cause and that NDVI-based results are unreliable for those years (Amendment 33) | decided |
| Consecutive dry days in flowering | CHIRPS. Daily prelim counts are not compared with final-CHIRPS counts until the gap is measured on overlapping months (Amendment 29) | decided; **OPEN: the dry-day rain threshold (mm)** |
| Bean-fill rain to date | CHIRPS, Dec of S−1 to the note date | decided |

### D. Stage 1, the expectation (§5 steps 6–7)

| Item | Value | Status |
|---|---|---|
| Terms per region | Intercept, linear trend, and a coefficient on crop S−1's yield anomaly. Three per region; not counted toward the cap | decided |
| Crop S−1's anomaly | From Conab's **third survey** of crop S−1, published in September of S−1, so every vintage uses the same value | decided, **but see the §4c finding under G** |
| Index reported relative to | This expectation, so off-years do not read as failures | decided |

### E. Weighting (§5 step 6)

| Item | Value | Status |
|---|---|---|
| Method | Ridge regression of the stage-1 yield anomaly, after the frost offset, on the four standardised inputs in B. One set of weights shared by all four regions | decided |
| Terms counted toward the cap of four | The four stage-2 weights only. Stage 1 and the frost offset do not count | decided |
| Ridge penalty | Chosen by an inner leave-one-year-out loop inside each training set, from a fixed grid | method decided; **OPEN: the grid** |

### F. Frost constants: values (§5 steps 4 and 6; Amendments 13, 17, 17b, 17c)

| Item | Value | Status |
|---|---|---|
| Thresholds (screen-height station minimum) | **2 °C** sensitive tier; **0 °C** severe tier; both reported | decided |
| Station tiers | 2 °C tier: three or more nights ≤ 2 °C in Jun–Aug. Severe tier: one or more nights ≤ 0 °C. Tiers are exclusive | decided |
| Observed night | Automatic stations: every hour 18:00–09:00 local present. Conventional stations: daily minimum present, with the night it belongs to taken from INMET documentation. A missing night is never a non-frost night; a tier that missing nights could change is unresolved | decided; **OPEN: which night a BDMEP daily minimum belongs to (not yet established)** |
| Station completeness per season | Automatic: ≥ 95% of hours, no gap over 48 h. Conventional: ≥ 95% of days (88 of 92), no gap over 3 days | decided |
| Radius and elevation cut | 25 km; stations above the 95th percentile of coffee-mask elevation in the region are left out (cut values at `prereg-2`) | decided |
| Regional flag | Stations meeting a tier cover at least **25% of the region's observed coffee** | decided |
| Coverage floor | **15%** observed coverage; registered at `prereg-2` with its statement | decided (value); registration at `prereg-2` |
| Penalty form | Yield loss on affected area × the tier's share of observed coffee, applied as a fixed offset; assumes unobserved coffee behaves like observed coffee | decided |
| **Penalty values per tier** | Yield loss on affected area for the 2 °C tier and for the severe tier | **OPEN** (values here; sources at `prereg-2`) |
| Frost series | From crop 2009 (the Jun–Aug 2008 window); not filled before | decided |
| Double counting and carryover | The 2022 call is in-sample. Crops 2022 and 2023, and any frost-flagged season, are reported with and without the frost component | decided |

### G. Backtest design and direction pass marks (§5 step 8)

| Item | Value | Status |
|---|---|---|
| Cross-validation | Leave one season out, in all four regions at once. Everything fitted is refitted without it: z-score means and SDs, trend, biennial coefficient, ridge penalty, weights | decided |
| Vintages | November, December, January, each using only inputs available at its note date (dates: OPEN, see A) | decided |
| Targets | Condition direction: the sign of actual yield minus the stage-1 expectation. Yield versus trend: the sign of actual yield minus trend | decided |
| Comparison models | Zero anomaly; biennial only; rain only (expectation plus flowering rain deficit) | decided |
| **Direction pass marks** | Without frost: **18 of 25** (crops 2001–2025, p ≈ 0.02). With frost: **13 of 17** (crops 2009–2025, p ≈ 0.02). If the share of positive anomalies is away from 50%, the mark becomes the larger of these and the count that beats the majority share at p < 0.05 (computed at `prereg-2`) | decided, **but see below** |
| Conab vintage scored against | Final survey of each year, or the latest revised series | **OPEN** (§10 still-open item 1) |
| Crop 2026 | Added as an addendum once Conab's final is out, with and without it; not a clean out-of-sample test | decided |
| Surprise test | Rules decided (§5 step 8): revisions under 1% count as flat and are excluded; skill is measured against the base rate; the pass mark is computed at `prereg-2` | decided |

**§4c finding that bears on G and D (Week 0 report §10, 2026-10-14):**

- **Arabica yield by region exists from safra 2008, not 2001.** Conab's arabica series gives
  regional area and yield from 2008; for 2001–2007 it gives production only. Unless the owner
  accepts the arabica-plus-conilon series for 2001–2007 (identical to arabica in Sul, Triângulo and
  São Paulo wherever both exist), the no-frost backtest has 18 seasons, not 25. The pass mark
  "18 of 25" was set for 25.
- **Third-survey values (D) are on Conab's site only for safras 2023–2025.**

Both need an owner decision before the tag.

## prereg-2 — to be fixed before the first backtest run (not yet tagged)

| Item | Value | Source | Status |
|---|---|---|---|
| **Region membership** | `docs/week0/proposed_region_membership.csv`: Sul e Centro-Oeste = Sul/Sudoeste + Oeste de Minas (190 municipalities); Triângulo, Alto Paranaíba e Noroeste = Triângulo Mineiro/Alto Paranaíba + Noroeste de Minas (85); Zona da Mata, Rio Doce e Central = Zona da Mata + Vale do Rio Doce + Central Mineira + Campo das Vertentes + Metropolitana de BH (415); São Paulo = all 645 municipalities. Norte, Jequitinhonha e Mucuri (163) outside the index | Conab bulletin, 3rd survey 2026 (1989 mesoregions); Amendment 34 | **registered, provisional.** Campo das Vertentes and Metropolitana de BH by area fit: PAM 2025 against Conab 2025, +3.1% (Sul e Centro-Oeste) and −8.5% (Zona da Mata, Rio Doce e Central), against +7.8% and −16.1% the other way. An answer from Conab's MG office before the tag supersedes this |
| **São Paulo target (§4c)** | São Paulo state total, as the Mogiana target | Conab 3rd survey 2026 table: SP reported only as a state total; Amendment 34 | **registered** |
| Mask lag and masks | Full class-46 and persistent-pixel masks | Amendments 16, 16b | pending |
| Station list per region and season, by network; altitude cut; observed coverage per region and season | Proposal computed on the provisional mask: `docs/week0/station_coverage_17c.csv` (automatic and conventional combined; 1 of 76 region-seasons under the floor). Cut on the provisional sample: Sul 1,216 m, São Paulo 1,126 m, Triângulo 1,192 m, Zona da Mata 1,136 m | §5 step 4; Amendments 17, 17c | pending: recompute on the frozen mask |
| Coverage floor statement | 15%, "chosen from coverage information only, before any frost night was counted" | Amendment 17c | to register at the tag |
| Surprise-test pass mark | From Conab's base rate | Amendment 12 | pending: Conab first- and final-survey series (only 2023–2025 located so far) |
| Base-rate check on the direction pass marks | — | Amendment 19 | pending |
| Frost tier constant sources | — | Amendment 15 | pending |
