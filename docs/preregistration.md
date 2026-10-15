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

## prereg-1 — to be fixed before W2 (not yet tagged; draft of 2026-10-15)

Amendment 15's list: the feature list, with each input's source, window and standardisation;
the weighting method and the terms counted toward the cap of four; the direction pass marks; the
frost tier constant values.

**Status, 2026-10-15: two items OPEN.** The frost penalty values per tier (F) and the citation for
the 34 °C heat threshold (B). The owner tags `prereg-1` only when both are closed.

### A. Seasons, windows and note dates (§3a)

| Item | Value | Source | Status |
|---|---|---|---|
| Season label | Season S is the crop harvested in year S (Conab safra S, trade S/S+1) | §3a | decided |
| Pre-flowering dry season | May–Aug of S−1 | §3a | decided |
| Frost exposure | Jun–Aug of S−1 | §3a | decided |
| Flowering | Sep 1–Nov 30 of S−1 | §3a, §5 step 3 | decided |
| Bean fill | Dec 1 of S−1 to Mar 31 of S | §3a, §5 step 3 | decided |
| Harvest rain | May–Sep of S: not an input (falls after every note on crop S) | §5 step 3 | decided |
| Backtest seasons | Without frost: Sul e Centro-Oeste, Triângulo and São Paulo, crops 2001–2025; Zona da Mata and the four-region total, crops 2008–2025. With frost: crops 2009–2025 | §5 step 8, Amendment 19b | decided |
| **Backtest cut dates per vintage** | Inputs are cut at: **November vintage, 20 November of S−1; December vintage, 1 December of S−1; January vintage, 1 January of S.** Production publishes within the first week after each cut, and note 1 in late November (§6) | §5 step 8, §6 | **decided 2026-10-15** (owner, item 1) |

### B. The four fitted inputs (stage 2, the cap of four; §5 step 6)

**Aggregation, all four inputs (Amendment 35; item 9).**
- **Members:** in season S, the municipalities that are kept by the filter (Amendment 16d), have
  PAM coffee area for PAM year S−2, and have at least one MODIS pixel of mapped coffee under season
  S's mask. PAM weights are renormalised once per season over the members.
- **Municipal value:** over the municipality's coffee-mask pixels.
- **Municipal anomaly:** the value minus the municipality's own mean for the same window, in the
  input's units. The mean comes from 2000–2025, in member seasons only, with at least 10 years;
  otherwise the municipality has no anomaly. It is refitted without the held-out season in the
  backtest.
- **Regional anomaly:** the PAM-weighted mean of members' anomalies.
- **Regional z-score:** against the same window across the baseline years, refitted without the
  held-out season. This is the stage-2 input.
- **EVI only:** cloud rules apply.
  - A reading counts only with at least one pixel of cloud-free coffee.
  - A regional composite is missing when members with an anomaly hold under 50% of the season's
    member PAM weight.
  - The covered-weight fraction is reported for every composite.
- **Four-region total (item 10):** the PAM-weighted mean of all members' anomalies across the four
  regions, z-scored the same way. Regions are weighted by their member PAM area (year S−2), not by
  production. The four-region yield target that follows is Conab's four-unit production over
  four-unit area.

| Input | Source and band | Window, and what is available at a cut | Municipal value | Status |
|---|---|---|---|---|
| **EVI anomaly** | `MODIS/061/MOD13Q1`, band `EVI` (× 0.0001), 250 m, 16-day. **QA: `SummaryQA` 0–1** (registered 2026-10-14) | Every composite from **1 May of S−1** that is available at the cut. A composite is available if it **ended at least 14 days before the cut** (item 3: 76 of 86 composites in 2023–2026 were published within 14 days of their end; four December–January composites took 35–48 days). The season value is the **unweighted mean of those composites' regional z-scores**, with missing composites skipped and their count reported (item 2). **Sensitivity:** composites from 1 Sep of S−1 only | Coffee-weighted median per composite (Amendment 35) | **decided** (Amendment 35; items 2 and 3) |
| **Flowering rain deficit** | `UCSB-CHG/CHIRPS/DAILY` (final) for the backtest; CHC prelim (§4) for current months not yet final, as in Amendment 9 | **From 1 Sep of S−1 to the earlier of 30 Nov and the end of the last pentad ending at least 5 days before the cut** (item 5). Pentads end on the 5th, 10th, 15th, 20th, 25th and last day of each month. At the 20 November cut that is 1 Sep–15 Nov; the December and January cuts see the whole window | To-date rainfall total; anomaly against the same calendar span. Standardised as a **z-score of the to-date total**, not a share of normal (item 6) | **decided** (items 5 and 6) |
| **Dry-season root-zone soil moisture** | `ECMWF/ERA5_LAND/HOURLY`, `volumetric_soil_water_layer_1`–`_3`, weighted **0.07 / 0.21 / 0.72** by layer thickness | May–Aug of S−1. Closed before every cut | Mean of the layer-weighted moisture over the window. **z-score** (item 7) | **decided** (Amendment 28; item 7) |
| **Heat days in flowering** | `ECMWF/ERA5_LAND/HOURLY`, `temperature_2m` | From 1 Sep of S−1 to the earlier of 30 Nov and 10 days before the cut (ERA5-Land availability, item 4) | Count of days whose maximum temperature exceeds **34 °C**. Each day is 00:00–24:00 at **UTC−3**, Brazil's standard time, in every year; daylight saving is ignored. Standardised as a **z-score with the standard deviation floored at 1 day**, because the count is mostly zero at coffee altitudes (item 8) | **decided, except the 34 °C citation: OPEN.** It must be cited to the same standard as the frost constants (owner, item 8). **Caveat recorded:** ERA5-Land's 9 km grid smooths the terrain, so in the hilly Sul e Centro-Oeste and Zona da Mata, Rio Doce e Central the grid-cell elevation can differ from the coffee fields' by hundreds of metres. Its 2 m temperature, and the count above 34 °C, may be biased there; no lapse-rate correction is applied, the bias is not measured, and it is stated beside heat-day results for those regions |

| Item | Value | Source | Status |
|---|---|---|---|
| EVI as the single vegetation term | EVI, because NDVI saturates in dense coffee canopies and EVI was designed for that case | §5 step 6, Amendment 19 | decided |
| Regional aggregation | As above: municipal anomalies against each municipality's own climatology, PAM-weighted, then a regional z-score | Amendment 35; item 9 | **decided 2026-10-15** |
| Four-region total | PAM area (year S−2), as above | §10 still-open item 2; item 10 | **decided 2026-10-15** |
| Cerrado irrigation adjustment | **Not adopted in v1.** It would be the only region-specific term and needs a Censo Agro value not yet obtained. Triângulo's rain-only skill is reported separately | §5 step 6, §10 still-open item 4; item 11 | **decided 2026-10-15** |
| Vegetation product rules | `MOD13Q1` primary. Trigger (a): no composite ending within 32 days of a note date. Trigger (b): signed average EVI divergence from VIIRS above 0.5 SD over 2024–2026 (four-region total or two or more regions), evaluated once in Week 0. Fallback (b), VJ113A1, accepted 2026-10-14, with its anomaly against its own 2018–2025 baseline | §4a; Amendments 25, 26, 30, 31, 33 | decided; trigger (b) awaits the formal per-region drift run |
| Rainfall product rules | Final CHIRPS for the baseline and the whole backtest. CHC prelim only for current-season months not yet final; final for month M counts as published from the 1st of M+2. Sensitivity rerun with prelim substituted | §9, Amendment 9 (revised) | decided |
| Data availability at a cut, besides CHIRPS | `MOD13Q1`: a composite is available if it ended at least 14 days before the cut. ERA5-Land: data through 10 days before the cut. Measured 2026-10-15 (Week 0 report §14) | §5 step 8; items 3 and 4 | **decided 2026-10-15** |

### C. Computed and reported, not fitted (§5 step 6)

| Item | Value | Status |
|---|---|---|
| NDVI anomaly | As EVI, in the sensitivity report only. The report states the 2024–26 NDVI drift of unresolved cause and that NDVI-based results are unreliable for those years (Amendment 33) | decided |
| Consecutive dry days in flowering | CHIRPS. **A dry day has under 1 mm** (the ETCCDI consecutive-dry-days definition; item 12). Daily prelim counts are not compared with final-CHIRPS counts until the gap is measured on overlapping months (Amendment 29) | **decided 2026-10-15** |
| Bean-fill rain to date | CHIRPS, Dec of S−1 to the cut, under the same pentad rule as flowering rain | decided |

### D. Stage 1, the expectation (§5 steps 6–7)

| Item | Value | Status |
|---|---|---|
| Terms per region | Intercept, linear trend, and a coefficient on crop S−1's yield anomaly. Three per region; not counted toward the cap | decided |
| Crop S−1's anomaly | Conab's **final figure** for crop S−1 in the current historical series (downloaded 2026-10-14). A declared leak: production at a November note has only the third survey. Third-to-final yield revisions for 2023–2025 average 1.9% in absolute size, with a largest of 8.4%. Sensitivity: recomputed from the third survey where one is on record (S−1 = 2023–2025), reported beside the headline | decided (Amendment 19b) |
| Index reported relative to | This expectation, so off-years do not read as failures | decided |

### E. Weighting (§5 step 6)

| Item | Value | Status |
|---|---|---|
| Method | Ridge regression of the stage-1 yield anomaly, after the frost offset, on the four standardised inputs in B. One set of weights shared by all four regions | decided |
| Terms counted toward the cap of four | The four stage-2 weights only. Stage 1 and the frost offset do not count | decided |
| **Ridge grid** | λ ∈ {0} ∪ {10^k : k = −2, −1.75, …, 3}: zero plus 21 log-spaced values from 0.01 to 1,000. Inputs standardised; intercept not penalised. The inner leave-one-year-out loop picks the λ with the lowest mean squared error; ties go to the larger λ (item 13) | **decided 2026-10-15** |

### F. Frost constants: values (§5 steps 4 and 6; Amendments 13, 17, 17b, 17c)

| Item | Value | Status |
|---|---|---|
| Thresholds (screen-height station minimum) | **2 °C** sensitive tier; **0 °C** severe tier; both reported | decided |
| Station tiers | 2 °C tier: three or more nights ≤ 2 °C in Jun–Aug. Severe tier: one or more nights ≤ 0 °C. Tiers are exclusive | decided |
| Observed night | Automatic stations: every hour 18:00–09:00 local present. Conventional stations: daily minimum present; a minimum dated D belongs to the night ending the morning of D (read at 12 UTC, covering the preceding 24 hours). A missing night is never a non-frost night; a tier that missing nights could change is unresolved | decided. The conventional rule is **provisional until INMET's documentation is cited** (Amendment 17d); it was checked against six same-site pairs |
| Stations sharing a site | Within 1 km in INMET's catalogues. Where both have complete records for a season, the automatic station governs the tier and the conventional is left out of the union; the conventional fills only seasons where the automatic is incomplete. Offsets are recorded in `docs/week0/colocated_pairs.csv` and never applied. Any season in which a conventional station alone would change a region's tier is flagged | decided (Amendment 17d) |
| Station completeness per season | Automatic: ≥ 95% of hours, no gap over 48 h. Conventional: ≥ 95% of days (88 of 92), no gap over 3 days | decided |
| Radius and elevation cut | 25 km; stations above the 95th percentile of coffee-mask elevation in the region are left out (cut values at `prereg-2`) | decided |
| Regional flag | Stations meeting a tier cover at least **25% of the region's observed coffee** | decided |
| Coverage floor | **15%** observed coverage; registered at `prereg-2` with its statement | decided (value); registration at `prereg-2` |
| Penalty form | Yield loss on affected area × the tier's share of observed coffee, applied as a fixed offset; assumes unobserved coffee behaves like observed coffee | decided |
| **Penalty values per tier** | Yield loss on affected area for the 2 °C tier and for the severe tier | **OPEN.** Owner, 2026-10-15: two or three candidate values per tier from Embrapa, IAC and peer-reviewed work, with citations, for the owner to choose before the tag. Values set from what the July 2021 frost did to crop 2022 would be in-sample (values here; sources at `prereg-2`) |
| Frost series | From crop 2009 (the Jun–Aug 2008 window); not filled before | decided |
| Double counting and carryover | The 2022 call is in-sample. Crops 2022 and 2023, and any frost-flagged season, are reported with and without the frost component | decided |

### G. Backtest design and direction pass marks (§5 step 8)

| Item | Value | Status |
|---|---|---|
| Cross-validation | Leave one season out, in all four regions at once. Everything fitted is refitted without it: z-score means and SDs, trend, biennial coefficient, ridge penalty, weights | decided |
| Vintages | November, December, January, each using only inputs available at its cut date (A: 20 November, 1 December, 1 January) | decided |
| Targets | Condition direction: the sign of actual yield minus the stage-1 expectation. Yield versus trend: the sign of actual yield minus trend | decided |
| Comparison models | Zero anomaly; biennial only; rain only (expectation plus flowering rain deficit) | decided |
| **Direction pass marks** | Rule: p < 0.05, one-sided; the exact p-value is reported beside every mark. Without frost: Sul, Triângulo and São Paulo, crops 2001–2025, **18 of 25** (p = 0.0216); Zona da Mata and the four-region total, crops 2008–2025, **13 of 18** (p = 0.0481). With frost, crops 2009–2025: **13 of 17** (p = 0.0245). If the share of positive anomalies is away from 50%, each mark becomes the larger of its value and the count that beats the majority share at p < 0.05 (computed at `prereg-2`) | decided (Amendment 19b) |
| Target series | Conab's final figure for each safra in the current historical series, downloaded 2026-10-14. For 2001–2007, Sul, Triângulo and São Paulo take area, yield and production from the arabica-plus-conilon series (identical to arabica there in 2008–2025); Zona da Mata starts in 2008 | decided (Amendment 19b) |
| Crop 2026 | Added as an addendum once Conab's final is out, with and without it; not a clean out-of-sample test | decided |
| Surprise test | Rules as in §5 step 8 (revisions under 1% count as flat; skill against the base rate). **Reported for safras 2023–2025, not scored against a pass mark, until earlier vintages are found** | decided (Amendment 19b) |

## prereg-2 — to be fixed before the first backtest run (not yet tagged)

| Item | Value | Source | Status |
|---|---|---|---|
| **Region membership** | `docs/week0/proposed_region_membership.csv`: Sul e Centro-Oeste = Sul/Sudoeste + Oeste de Minas (190 municipalities); Triângulo, Alto Paranaíba e Noroeste = Triângulo Mineiro/Alto Paranaíba + Noroeste de Minas (85); Zona da Mata, Rio Doce e Central = Zona da Mata + Vale do Rio Doce + Central Mineira + Campo das Vertentes + Metropolitana de BH (415); São Paulo = all 645 municipalities. Norte, Jequitinhonha e Mucuri (163) outside the index | Conab bulletin, 3rd survey 2026 (1989 mesoregions); Amendment 34 | **registered, provisional.** Campo das Vertentes and Metropolitana de BH by area fit: PAM 2025 against Conab 2025, +3.1% (Sul e Centro-Oeste) and −8.5% (Zona da Mata, Rio Doce e Central), against +7.8% and −16.1% the other way. An answer from Conab's MG office before the tag supersedes this |
| **São Paulo target (§4c)** | São Paulo state total, as the Mogiana target | Conab 3rd survey 2026 table: SP reported only as a state total; Amendment 34 | **registered** |
| Mask lag and masks | Full class-46 and persistent-pixel masks | Amendments 16, 16b | pending |
| Station list per region and season, by network; altitude cut; observed coverage per region and season | Proposal computed on the provisional mask: `docs/week0/station_coverage_17c.csv` (automatic and conventional combined; 1 of 76 region-seasons under the floor). Cut on the provisional sample: Sul 1,216 m, São Paulo 1,126 m, Triângulo 1,192 m, Zona da Mata 1,136 m. Stations sharing a site and their offsets: `docs/week0/colocated_pairs.csv` (19 pairs) | §5 step 4; Amendments 17, 17c, 17d | pending: recompute on the frozen mask, and the 2026 windows after the mid-November BDMEP re-request |
| INMET citation for the conventional night rule | — | Amendment 17d | pending |
| Coverage floor statement | 15%, "chosen from coverage information only, before any frost night was counted" | Amendment 17c | to register at the tag |
| Surprise-test pass mark | From Conab's base rate, once vintages beyond 2023–2025 exist; until then, the statement that the test is reported, not scored | Amendments 12, 19b | not computable yet |
| Base-rate check on the direction pass marks | — | Amendment 19 | pending |
| Frost tier constant sources | — | Amendment 15 | pending |
