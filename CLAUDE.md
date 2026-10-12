# Project spec: Brazil arabica growing-conditions index

Read this file at the start of every session. It is the source of truth for scope.
If a task would take the work outside this spec, stop and ask.

## 1. The question

Each month: **are growing conditions in each arabica region better, worse or in line with the
baseline, and what does that imply for the 2027 crop relative to Conab and the private estimates?**

**Benchmark (AMENDED 2026-10-12).** The trade labels crops by marketing year: "2026/27" is the crop
harvested in 2026, so the 2027 crop is **2027/28**. The 2027 crop is benchmarked against the
**arabica component** of the private 2027/28 estimates once they are published. The first are
expected from around December; confirm each publication date rather than assuming it. Use only
houses that publish an arabica figure: a total-Brazil figure includes conilon and is not a
benchmark for an arabica-only index. **Until those estimates exist, notes state the comparison as
"versus trend and an expected off-year"** (§5 step 7).

For reference only, not a benchmark: the figures in the original draft (StoneX 75.3M bags,
Sucafina 75.4M, Marex 75.9M) are for **2026/27, the 2026 harvest, total Brazil including conilon**.

**Conab timing (AMENDED 2026-10-12).** Conab publishes four coffee surveys a year. A crop's first
survey comes in January (between the 18th and 28th in recent years) and its final survey in
December or the following January. **No Conab estimate for the 2027 crop exists before its first
survey, expected late January 2027. Any note published before that survey says so explicitly.**
Confirm the 2027 dates from Conab's published calendar rather than assuming them.

**Design principle, fixed: this is a condition index, not a yield forecast.** Every note says so.
If someone asks for a number of bags, the answer is a range, never a point: relative to Conab's
latest 2027 estimate once one exists, and relative to trend and the expected off-year before that.

**The project exists to open conversations** with softs analysts and desks. A working model with a
checkable track record is the credential. **Explicitly not a goal:** beating Conab or the trade
houses on the point estimate.

### 1a What the credential actually is, until Conab's final 2027 survey

A live record on the 2027 crop does not exist until Conab's final 2027 survey (December 2027 or
January 2028). **Until then the backtest *is* the product.** That raises the stakes on §5 step 8
considerably: a thin or flattering backtest is worse than no backtest, because the audience can
check it.

## 2. Success criteria

By **late January 2027** (revised — see SPEC_CHANGELOG, the original "late November" was
inconsistent with shipping notes in December and January):

1. Public GitHub repo, `brazil-arabica-index`, with a reproducible Earth Engine + Python pipeline,
   rerunnable in an afternoon.
2. A backtest table against Conab final arabica production, **by note date** (§5 step 8), with
   crop 2022 (July 2021 frost; declared in-sample, §5 step 6) and crop 2025 (2024 drought)
   reported explicitly, whichever way they come out.
3. Three monthly notes published (November, December, January), each with one chart and one view.
4. Sent to at least 20 named people in softs, with replies logged.

## 3. Scope

Arabica only, Brazil only, four regions. Robusta (Espírito Santo, Rondônia) is out: different crop
calendar, different exchange, and it would double the mask work for a market not being pitched.

| Region | State | Why it matters | Dominant risk |
|---|---|---|---|
| Sul de Minas | MG | Largest arabica area; rain-fed, hilly | Drought at flowering, frost |
| Cerrado Mineiro | MG | Flat, mechanised, partly irrigated; highest yields | Drought (irrigation masks it), heat |
| Zona da Mata / Matas de Minas | MG | Steep smallholder terrain, lower yields | Rain at harvest, disease (neither is an index input) |
| Mogiana | SP | Historic frost zone (1975, 1994, 2021) | Frost, drought |

**Spatial unit:** municipality, aggregated to region by IBGE PAM coffee area.
**Temporal unit:** 16-day composites for the index; daily for frost and rainfall events.

**Out of scope for v1:** price forecasting, trading strategy, robusta, Colombia or Vietnam,
field-level output, any paid data.

### 3a The crop calendar, corrected (AMENDED 2026-10-12)

**The original spec assigned the wrong frost window to the 2027 crop.** Brazilian winter frost
damages the trees; the loss appears in the next harvest after the following flowering.

- **The 2027 crop** was set by **Sep–Nov 2026 flowering**, on trees that lived through
  **Jun–Aug 2026 frost**. That frost exposure **has already happened** and is knowable now.
- **Jun–Aug 2027 frost is a 2028 signal**, not a 2027 one. It stays in the monitoring plan, labelled
  as the first 2028 signal.

**Season convention (AMENDED 2026-10-12).** Season S is the crop harvested in year S: Conab's safra
S, and the trade's S/S+1, so 2026/27 is season 2026. Its windows:

| Window | Months |
|---|---|
| Frost exposure | Jun–Aug of S−1 |
| Flowering | Sep–Nov of S−1 |
| Bean fill | Dec of S−1 to Mar of S |
| Harvest | May–Sep of S |

**Every year label in this spec, the backtest table and the notes is a crop year S**, unless it
explicitly names a weather window or event. For example, "the July 2021 frost" belongs to crop
2022.

**Consequence for note 1:** it carries a **backward-looking Jun–Aug 2026 frost assessment as settled
fact**, not a forward risk. This is an advantage, not merely a correction — the frost question for
the crop being tracked is already answerable.

## 4. Data sources

Every ID below was verified to resolve in Earth Engine on 2026-10-12 (see SPEC_CHANGELOG), except
where a row says otherwise.
**Do not substitute an ID. If one is dead, stop and report it.**

| Layer | Source | Resolution / cadence | Use |
|---|---|---|---|
| **Baseline vegetation — PRIMARY** | `MODIS/061/MOD13Q1` | 250 m, 16-day, 2000– | NDVI/EVI anomalies; the backtest baseline (§4a). Terra is at end of mission and its orbit is drifting: continuity check, trigger and fallback in §4a |
| Drift check only | `MODIS/061/MYD13Q1` (Aqua) | 250 m, 16-day, 2002– | Week 0 Terra drift check (§4a). **Not yet verified to resolve.** |
| Vegetation fallback — declared, not active | `NASA/VIIRS/002/VNP13A1` | 500 m, 16-day composites, 2012– | Used only if the §4a trigger fires; second reference in the Week 0 drift check. **Not yet verified to resolve.** |
| Rainfall — final | `UCSB-CHG/CHIRPS/DAILY` | 5 km, daily | Baseline and the whole backtest; current season once a month is final (§9). Flowering deficit, bean-fill cumulative |
| Rainfall — current season | `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad` (CHIRPS-prelim, community catalog, curated by Climate Engine) | 5 km, pentad, 2015– | Current-season months not yet published as final (§9). **Not yet verified to resolve or to be current: verify before the first run.**<br>**Fallback, declared now:** CHC's own CHIRPS-prelim files (daily and pentad) from chc.ucsb.edu, ingested as a private GEE asset, used if the community asset does not resolve, is not current, or lags the provider by more than two pentads. Verify both sources in Week 0 before choosing. |
| Heat days | `ECMWF/ERA5_LAND/HOURLY` | 9 km, hourly | Heat days above 34 °C. **No frost role** (§4b) |
| Elevation | `USGS/SRTMGL1_003` | 30 m, static | 95th percentile of coffee-mask elevation per region, for the frost station cut (§5 step 4). **Not yet verified to resolve.** Declared fallback: `COPERNICUS/DEM/GLO30` |
| Soil moisture | `ECMWF/ERA5_LAND/HOURLY` vol. layer 1, or `NASA/SMAP/SPL4SMGP/007` | 9 km | Drought persistence through the dry season |
| Short-range forecast | `NOAA/GFS0P25` | 0.25°, 6-hourly, 16 days | Forward frost-risk flag |
| Coffee mask | MapBiomas Collection 10, **class 46 = Coffee** | 30 m, annual **1985–2024** | Where to compute the indices |

MapBiomas asset, verified:
`projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v1`
40 annual bands `classification_1985` … `classification_2024`. Class 46 is 6.55% of a Sul de Minas
test box. **Open question 1 in the original spec is closed:** no fallback to a generic cropland mask
is needed, and the mask supports the full MODIS-era backtest.

**Non-GEE data (download manually, store in `data/raw/`, never modify):**

- **INMET automatic station data** — annual ZIP archives, **2000 through 2026**, from
  `portal.inmet.gov.br/dadoshistoricos`. **This host is not reachable from the project sandbox**
  (curl returns 000 while control hosts return 200), so it is a manual download, like DWR and CIMIS
  in the earlier studies. Record retrieval date and checksum in `data/raw/inmet/SOURCE.md`.
  Confirm on first download that daily minimum temperature is present for automatic stations.
- **Conab coffee surveys** — the benchmark and backtest target. Conab has monitored coffee since
  **2001**, which bounds the backtest. Bulletins are PDFs; the regional series must be extracted
  from them. See §4c.
- **IBGE PAM** municipal coffee area and production; **IBGE Censo Agropecuário** irrigation share.
- **USDA FAS GAIN Brazil Coffee**, ICO Coffee Market Report, Cecafé monthly exports, Cooxupé.
- **Market data:** ICE Coffee C settlement, calendar spreads, certified stocks; CFTC COT.

### 4a Baseline: MODIS era, not Sentinel-2 era (AMENDED 2026-10-12)

**The backtest and baseline run on MODIS, 2000–2025.** Sentinel-2 is out of v1 entirely: it is not
an index input and does not appear in the note (Amendment 5).

Only Sentinel-2 starts in 2017. MapBiomas runs from 1985, MODIS from 2000, CHIRPS from 1981,
ERA5-Land from 1950, and Conab coffee from 2001. Fitting four parameters plus a biennial term on
nine seasons is roughly two observations per parameter and about 4.5 biennial cycles — an anecdote.
The MODIS era gives roughly **25 seasons**, puts 2014 and the 2000s in the sample, and stops the
2021 frost and the 2024 drought from *defining* a nine-year baseline that they distort.

**Caveat to carry in every note and the README: MODIS at 250 m blurs smallholder terrain, so expect
Zona da Mata skill to be the weakest of the four regions.** Report regional skill separately so this
is visible rather than averaged away.

**Terra continuity (AMENDED 2026-10-12).** `MOD13Q1` comes from Terra, which stopped orbit
maintenance in 2022. Its morning overpass is drifting from about 10:30 toward 8:30 by late 2026,
and NASA's 2023 mission status put end of science at February 2027. The current season is the
most drift-affected, and it is the season every note reports.

- **Week 0 drift check.** Per region, over the mask, compare `MOD13Q1` NDVI and EVI anomalies
  with `MYD13Q1` (Aqua) and `VNP13A1` (VIIRS) for 2018–2026. Compare anomalies, not levels: the
  products differ in resolution and overpass time. Report the difference series and its trend per
  region. Divergence of Terra from both references while they agree is attributed to Terra.
- **Trigger, fixed before the check runs.** Switch the current-season vegetation input to the
  fallback if either (a) `MOD13Q1` is not current at a note date, meaning no composite ends within
  32 days of the note date; or (b) Terra's anomaly diverges from both references by more than 0.5
  baseline standard deviations, averaged over 2024–2026, in the coffee-area-weighted Brazil total
  or in two or more regions. Per-region differences are reported either way.
- **Fallback, declared now: `NASA/VIIRS/002/VNP13A1`** (500 m, from 2012).
  - If triggered, the current-season anomaly is computed against VNP13A1's own 2012–2025
    baseline, never against MODIS's.
  - The headline backtest stays on MODIS. The vegetation component is rerun on VNP13A1 for crops
    2013–2026, and the change in skill is reported beside the headline, as for CHIRPS-prelim (§9).
  - At 500 m, VNP13A1 blurs smallholder terrain more than MODIS does, so the Zona da Mata caveat
    is stronger under the fallback, and the note says so.
  - **Mid-season rule.** Trigger (b) is evaluated once, in Week 0, and binds for the whole season.
    Trigger (a) is evaluated at each note date; if it fires, the fallback applies to that note and
    every later note for the crop, and each note states which product each reading used. Prior
    notes are not reissued. No reading within a note mixes products.
- **Confirm the current `MOD13Q1` end date** in Earth Engine as soon as a client is available.

### 4b Frost: INMET stations only (AMENDED 2026-10-12)

**The original spec had ERA5-Land as the primary frost input. ERA5-Land now has no frost role.**

Direct evidence from the completed almond-frost study: over 2,532 matched frost station-nights,
**ERA5-Land was the worst of five products at predicting station minima** — median absolute error
1.41 °C, the largest of all, with the widest central 90% of its error distribution — and that was
over *flat valley floor with 63 calibration stations*. Brazil's arabica is hilly.

- **Frost comes from INMET station minima only** (§5 step 4).
- **ERA5-Land has no frost role.** Its remaining roles are soil moisture and heat days.
- Frost is reported as a **regional flag with its coffee-area coverage share**, never as a
  precise area.
- **The calibration requirement applies to gridded products matched to stations, not to station
  observations.** The station thresholds are the agronomic constants in §5 step 4, neither
  fitted nor calibrated.

**Check for circularity before using INMET to validate anything.** CHIRPS blends satellite estimates
with station data. If Brazilian stations feed CHIRPS, validating CHIRPS against INMET is circular —
the same trap as PRISM ingesting CIMIS in the almond study, which reframed that study's headline
result. Establish this before the validation is run, not after.

### 4c Conab granularity — RESOLVE FIRST (open, blocking)

Step 6 regresses on Conab's **regional** yield anomaly. Conab reports by state, and the Minas
regional split does appear in the bulletins — the 2020 first survey quotes Sul de Minas 17.03–17.79M
bags, Cerrado Mineiro 5.82–6.07M and Zona da Mata Mineira 7.21–7.53M. **Mogiana is not known to be a
Conab reporting unit.**

**Resolution order, in Week 0, before any fitting:**

1. Check a recent Conab coffee bulletin PDF for a São Paulo regional split.
2. If there is none, **use São Paulo state total as the Mogiana target** — São Paulo arabica is
   dominated by Mogiana, so the state total is usable.
3. **Only if that proves too noisy in the backtest**, cut to three regions.

**Do not cut Mogiana pre-emptively.** It is the frost region, and losing it weakens the component
with the most distinctive story.

Also to settle in Week 0: the bulletins are PDFs, so building a ~25-season regional target series is
extraction work. Budget for it, and record which survey vintage each value came from.

## 5. Method

A set of regional anomalies against the MODIS-era baseline, combined into one condition index per
region and scored against Conab. **Keep it simple enough to explain in a 15-minute call.**

1. **Mask.** Clip MapBiomas class 46 to the four regions; drop municipalities whose MapBiomas area
   differs from IBGE PAM coffee area by more than 30%. **Freeze the mask for the season.**
   **Report what the filter removed and whether the removed municipalities differ from the kept**
   (§9) — the 30% trigger very likely correlates with steep smallholder terrain, so it may
   preferentially delete Zona da Mata, the region the mask is least reliable in.

   **Mask year by season (AMENDED 2026-10-12).**
   - Each backtest season uses the mask production would have had at its note date. Every season
     uses Collection 10's classifications, so all seasons are on the same product. Older
     collections are not used: they differ in method, and some predate class 46.
   - The mask year is the crop year minus a fixed lag, set to the live lag for crop 2027:
     - S−2 if a collection covering 2025 is published and verified before note 1;
     - otherwise S−3, since Collection 10's last year is 2024.
   - The lag is applied unchanged to every season and recorded at `prereg-2`.
   - The 30% filter runs per season, against IBGE PAM for the mask year.

   **Bearing-area mismatch.**
   - IBGE PAM counts area intended for harvest. That leaves out young plantings that aren't yet
     bearing and, very likely, area pruned back after a frost. MapBiomas class 46 includes both.
   - Wherever coffee is expanding or recovering, MapBiomas exceeds PAM, so the 30% filter is
     biased toward removing:
     - the Cerrado's expanding frontier;
     - frost-hit municipalities in the seasons after a frost, which is exactly where the frost
       signal is.
   - The removal report splits removed and kept municipalities by their MapBiomas area change
     over the three preceding years, so the bias is visible.

   **Persistent-pixel comparison for the filter (Amendment 16b).**
   - For the 30% filter only, MapBiomas area is counted on pixels classified as coffee in the mask
     year and each of the two years before it. Arabica does not bear until roughly its third
     year, and bearing area is what PAM counts.
   - This removes the young-planting part of the mismatch, not the post-frost pruning part:
     pruned trees stay class 46. The removal-report split above still applies.
   - The index itself stays on the full class-46 mask in v1. The backtest is reported once more
     on the persistent-pixel mask, as a sensitivity beside the headline, like CHIRPS-prelim and
     VIIRS.
   - Both masks are registered at `prereg-2`.
2. **Vegetation anomalies.** Per 16-day window, area-weighted median NDVI and NDMI over the mask,
   cloud-masked. Express as a z-score against the same window across the baseline years.
3. **Rainfall windows.** CHIRPS totals for flowering (Sep 1–Nov 30) and bean fill (Dec 1–Mar 31).
   Harvest-window rain (May–Sep of S) is not an index input: it falls after every note about the
   crop it affects. This removes the harvest window of year S only. May–Aug of S−1, the
   dry season before flowering, falls before every note about crop S and is not affected; it is the
   window of the dry-season soil-moisture input (§4). **Flowering deficit is the single most
   predictive input;** weight it accordingly.
4. **Frost events (AMENDED 2026-10-12).** Station observations only (§4b). **Assign each frost
   window to the crop it actually affects (§3a).**
   - **Stations.** INMET automatic stations with complete Jun–Aug records from 2008, inside or
     within 25 km of the coffee mask. A record is complete when at least 95% of hourly
     observations are present in every Jun–Aug window from 2008, with no gap longer than 48
     consecutive hours. Record each station's coffee area within that radius. Leave out of the
     weighting any station above the 95th percentile of coffee-mask elevation in its region (DEM,
     §4; station elevation from INMET metadata). Register the resulting station list per region,
     with its count, and the elevation cut at `prereg-2`, and report every station within 50 m of
     the cut.
   - **Coverage share.** For a set of stations, the coffee area inside the union of their 25 km
     circles, with overlaps counted once, divided by the region's coffee area.
   - **Thresholds: agronomic, not fitted.** Coffee leaf damage starts around −2 to −3 °C at leaf
     level. On radiative-cooling nights, screen-height readings run roughly 3–4 °C warmer than
     the leaf. So first damage corresponds to a screen-height minimum of 0 to 2 °C. **2 °C is the
     sensitive tier and 0 °C the severe tier, and both are reported.** Values are registered at
     `prereg-1` and their sources at `prereg-2` (§9):
     - leaf damage: Embrapa, IAC or peer-reviewed frost-physiology work;
     - the offset: a published screen-versus-leaf or screen-versus-ground study.
     If no clean source exists for the offset, say so here and mark it provisional.
   - **Station tiers.** A station meets the 2 °C tier with three or more nights ≤ 2 °C in
     Jun–Aug, and the severe tier with one or more nights ≤ 0 °C.
   - **Regional flag.** A region is flagged for a tier when stations meeting that tier cover at
     least 25% of its coffee area. Reaching the flag triggers an out-of-cycle note at that point,
     not at the end of the window.
   - **Minimum coverage.** If the qualifying stations cover less than 25% of a region's coffee
     area, that region cannot be frost-flagged at all, and every note says so. Report the maximum
     attainable coverage per region at `prereg-2`, so an unreachable flag is known before the
     first run.
   - **Series.** The frost component starts with crop 2009 (the Jun–Aug 2008 frost window) and
     is not filled for 2001–2008. The index is scored in two versions, each with its own pass
     mark, and the two are compared only on the seasons they share: without frost, on every
     season; with frost, from crop 2009.
5. **Heat and dry-season stress.** Days above 34 °C and consecutive dry days during flowering.
6. **Condition index.** Weighted sum of standardised inputs, weights fitted by regressing Conab's
   regional yield anomaly on the inputs. **Do not fit anything with more than four parameters.**
   Use ridge or fixed agronomic weights.
   **Frost is not fitted (AMENDED 2026-10-12).** The backtest window holds one major frost (July
   2021, crop 2022). A fitted frost weight would be set by that one season, and leaving that
   season out would remove the only evidence for it.
   - Frost enters as a **fixed yield penalty for each frost tier** in each flagged region. The
     tiers and the flag are defined in step 4. Each tier's penalty is the yield loss on affected
     area, multiplied by the share of the region's coffee area under stations meeting that tier
     (the same weights as the step-4 flag). The step-4 trigger at 25% therefore sets the floor,
     and the penalty grows with coverage. Tiers are exclusive: the severe-tier penalty applies to
     the share meeting the severe tier, and the 2 °C penalty to the share meeting the 2 °C tier
     but not the severe tier. Penalty values are registered at `prereg-1` and their sources at
     `prereg-2` (§9): Embrapa, IAC or peer-reviewed frost-damage work. Where no clean source
     exists, say so and mark the value provisional.
   - In the regression, the frost penalty is a fixed offset. The fitted weights are estimated on
     the yield anomaly that remains after it.
   - **The crop 2022 call is in-sample.** The constants are being set by someone who knows what
     the July 2021 frost did, so the 2022 call is not evidence of skill. Say so wherever 2022
     appears: the backtest table, the notes and the README.
   - **Double-counting check.** After a frost, the damage also shows up in the vegetation
     anomaly. Report the 2022 prediction, and that of any other frost-flagged season, with and
     without the frost component.
   - **Carryover is not modelled in v1.** Severe frost also cuts the following crop through
     pruning and recovery (crop 2023 after July 2021). Crop 2023 is added to the with-and-without
     report, and the backtest table states that 2023 may carry 2021 frost effects the model does
     not represent.
7. **Biennial adjustment.** Arabica alternates on and off years. Detrend with a two-year cycle term
   before fitting, and report the index **relative to the expected on/off year**, or every off-year
   reads as a crop failure.
8. **Backtest by note date (AMENDED 2026-10-12).** Leave-one-year-out, **using only inputs available
   as of each note date.** For each season × each of November, December and January, fit on the
   other seasons and predict direction and rough size. **Report hit rate and mean absolute error
   separately for the November, December and January vintages.**
   **Expect November to be the weakest, and publish that number anyway** — it is the only skill
   figure a desk will take seriously, and a full-season backtest would flatter the model by scoring
   it with information it will not have in production. Call out crops 2022 and 2025 explicitly.

   **Surprise test (AMENDED 2026-10-12).** For each season and each vintage, score whether the
   index predicted the direction of Conab's revision from its first survey of the crop to its
   final survey.
   - **Predicted direction** = sign of (the index-implied yield anomaly as of the note date minus
     Conab's first-survey yield anomaly), both measured against the same trend and expected
     on/off year. The mapping from index to yield anomaly is the leave-one-year-out fit for that
     season, the same fit the direction backtest uses, so the index value compared with Conab's
     first survey was never fit on that season's Conab final. Where Conab gives a range, use its
     midpoint. The November and December readings come before the first survey and are compared
     with it once it is published, as the post-survey note does in production (§6). No reading
     uses information later than its own note date.
   - **Actual direction** = sign of (final minus first), in yield. Revisions smaller than 1% of
     the first estimate count as flat. They are left out of the hit rate, and their count is
     reported (§9).
   - **Report the base rate**: the share of seasons Conab revised upward. The comparison model
     always predicts the majority direction. Skill is the hit rate above that, not above 50%.
     The pass mark is the number of hits that beats the base rate at p<0.05 (one-sided). It is
     computed once the Conab series has been extracted, and fixed before the first backtest run.
   - Score the Brazil arabica total as the headline and each region separately. Report how many
     seasons have both a first and a final survey on record.
9. **Output.** Index per region and a Brazil-weighted total, every 16 days; frost and flowering-
   deficit flags daily.

**Leave out until v2:** machine-learning yield models, Planet imagery, Sentinel-2 imagery,
field-level analysis, any translation of the index into a price forecast.

## 6. Outputs

1. **Monthly crop note** (one page, PDF and LinkedIn), first week of each month from November 2026.
   Fixed layout so readers learn where to look: headline with the Brazil-weighted index and its
   direction; chart of index by region against the baseline band; region table (index, flowering
   rain vs normal, frost nights, one-line comment); benchmark line against Conab's 2027 estimate, or
   a statement that none exists yet (§1), and the arabica component of the 2027/28 private estimates,
   or "versus trend and an expected off-year" until those are published (§1); market context
   (Coffee C front month, Jul/Dec spread, ICE certified
   stocks, managed-money net from COT); **the view** — one paragraph, one stated lean, and what
   would change it; method and caveats in three lines, always including **"condition index, not a
   yield forecast"**, the Zona da Mata resolution caveat, and which months used CHIRPS-prelim.
2. **GitHub repo** (`brazil-arabica-index`). Public, MIT licence, README that lets someone rerun
   it in an afternoon. GEE scripts, the notebook that builds index and backtest, the mask rule and
   the live season's frozen mask, the backtest table, every note as PDF plus its chart data as CSV.
3. **Dashboard (optional, v1.5).** Only after three notes are out. Polish, not credibility.

**Distribution per note:** LinkedIn post with the chart and three lines; direct email with the PDF;
optionally a thread in r/commodities or the FIC Slack. Log every reply with name, firm, date and
what they said.

## 7. Pipeline

GEE does masking, cloud filtering, compositing and regional aggregation, and exports small CSVs.
**The Python notebook never touches raw imagery.** Scheduled run on a 16-day cadence; the note is
assembled by hand from the notebook's charts and tables.

## 8. Timeline

**Week 0 (blocking, before anything else):** resolve §4c Conab granularity; confirm INMET download
route and that daily minimum temperature is present; check whether CHIRPS ingests Brazilian stations.
Run the Terra drift check and confirm the current `MOD13Q1` end date (§4a).

Then: **W1** frozen mask and first regional NDVI series (check: mask area within 30% of IBGE per
municipality, with the removal report). **W2** anomalies and rainfall windows for every MODIS-era
season (check: report each season's rank on every input, per region and for the Brazil total; if
crops 2022 and 2025 are not the worst, that is a finding, and nothing is changed to make them so).
**W3–W4** backtest by note date (check:
direction right in a stated majority of seasons, reported per vintage). **W4** note template on
October–November 2026 data (check: a friend outside ag can read it in two minutes). **W5** scheduled
run and README (check: a clean clone reproduces the index). **W6** note 1 published and sent.

**Honest scope note:** six weeks part-time alongside a job search, for mask + IBGE reconciliation +
four regions × five layers + a by-note-date backtest + template + publication + outreach. The mask
and backtest are realistically four of the six weeks. If something has to give, **it is not the
backtest** (§1a) — it is the fourth region, the dashboard, or a note slipping a week.

## 9. Rules for the agent

- Stop at every checkpoint. Print results, wait.
- **Never substitute a dataset.** If an ID is dead, stop and ask.
- **Verify before use.** Dataset IDs, band units, scale factors and flag semantics come from the
  provider's own documentation, never from memory or from the plausibility of the result.
- **Every filter reports what it removed and whether what it removed differs from what it kept** —
  the distribution, not the count alone. A filter whose trigger correlates with the signal biases
  the result, and the direction is usually knowable in advance.
- **No two products or seasons are ever compared except on identical observations.** Comparing on
  each product's own available sample measures availability as well as skill.
- **Any result of zero, none or empty is verified by an independent method before it is accepted**,
  especially where zero is the expected answer.
- **Never score a model with information it will not have in production.** See §5 step 8.
- **CHIRPS product split, decided 2026-10-12 before the first run.**
  - Final CHIRPS for the baseline and the whole backtest, so every season is scored on the same
    product. CHIRPS-prelim only for current-season months whose final is not yet published.
  - Final for month M counts as published from the 1st of month M+2. That matches the provider's
    ~3-week latency (final appears after about the 20th of the following month).
  - Production will use prelim where the backtest uses final, so the backtest is optimistic on
    exactly those months. **Quantify it:** rerun every vintage whose note date falls inside the
    prelim archive (2015 onward), with prelim substituted for the months not yet final. Report the
    change in hit rate and mean absolute error beside the headline figures, and the
    prelim-minus-final difference in window totals over the mask. Do not correct for it.
  - The community-catalog prelim asset is pentad-only, so under it consecutive dry days for months
    still in prelim are reported as not yet available, not estimated. If the declared fallback
    (CHC's own prelim files, §4) is used instead, consecutive dry days for prelim months are
    computed from its daily files.
- **Every checkpoint report carries its denominator** — how many municipalities, seasons,
  station-nights were examined, not only how many passed.
- Never modify anything in `data/raw/`.
- Secrets stay in `.env` (gitignored). Never print or commit a key.
- Log every spec deviation in `SPEC_CHANGELOG.md` with the reason, at the time it happens.
- **Report negative and inconclusive results as findings.** Do not retune to rescue a result. Say
  "inconclusive" or "not established" when that is the answer, and give the reason.
- **Pre-registration, in two tagged commits (decided 2026-10-12).** Record every choice that could
  be tuned in `docs/preregistration.md`, and commit it at two points:
  - **Tag `prereg-1`, before W2 computes any season-level input.** It records:
    - the feature list: each input, its source, window and standardisation
    - the weighting method, and which terms count toward the cap of four
    - the direction pass marks
    - the frost tier constants
  - **Tag `prereg-2`, before the first backtest run.** It records the values that need data but
    not results:
    - the mask lag and both masks: full class 46 and persistent-pixel (§5 step 1)
    - the station list per region with its count, the altitude cut, and the maximum attainable
      frost coverage per region (§5 step 4)
    - the surprise-test pass mark computed from Conab's base rate
    - the sources for the frost tier constants, or "provisional, no clean source". A constant
      whose source changes between `prereg-1` and `prereg-2` is logged like any other change. If
      a source supports a different value, the registered value stands; the backtest is also
      reported with the source's value, and the discrepancy is logged.
  - Any later change goes in SPEC_CHANGELOG with its date and reason. The backtest report lists
    every change made after `prereg-1`. Changing a registered item because of a backtest result
    is the retuning this section forbids.
- When a result looks surprisingly good, flag it and check the subsetting before reporting it.
- Commit at each checkpoint. **Do not push without asking.**

## 10. Open items

1. **§4c Conab granularity** — blocking, Week 0. São Paulo regional split; fallback to state total.
2. **Conab vintage** — backtest against the final survey of each year, or the following year's
   revised series? Record which vintage every value came from either way.
3. **Region weights** — IBGE PAM harvested area or production? Production weights favour the Cerrado.
4. **Does USDA FAS GAIN give regional splits** usable as a second benchmark?
5. **Irrigation share in the Cerrado** from IBGE Censo Agro, to down-weight rainfall deficit there.
6. **Planet education or research licence** for a later field-scale check. (In the strawberry study
   the key authenticated and searched but held no asset entitlement — assume the same until shown
   otherwise.)
7. **First five names on the outreach list**, and which note goes to them first.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Overclaiming | Condition index framing in every note; range not point; §1a |
| Biennial bearing | Two-year cycle term; report relative to expected on/off year |
| Irrigation in the Cerrado | Separate weighting; flag irrigation share from Censo Agro |
| Short fitting sample | MODIS era, ~25 seasons (§4a); ridge or fixed weights; LOYO by note date |
| ERA5-Land misses valley frost | INMET stations only; ERA5-Land has no frost role (§4b) |
| MODIS blurs smallholder terrain | Expect weakest skill in Zona da Mata; report regional skill separately |
| Mask errors | IBGE cross-check with a removal report (§5 step 1) |
| Cloud in Nov–Mar | 16-day composites; CHIRPS and ERA5 carry the signal when optical is thin |
| Flowering is sub-pixel and brief | Use flowering-window rainfall and temperature as the proxy, not NDVI |
| Conab revisions | Use a stated vintage; record it |
| Time | §8 scope note; the backtest is the last thing to cut |

**Two limits stated in every note:** the index tracks conditions, not yield; and the private trade
houses have field crop tours and farm data that this project does not.
