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
The index covers four Conab units, not all of Brazil's arabica, so every comparison with a
Brazil-wide arabica estimate states that coverage (§3).

**Conab timing (AMENDED 2026-10-12; revised 2026-10-14).** Conab publishes four coffee surveys a
year. A crop's first survey has fallen between late January and 5 February in recent years
(21 January 2021, 18 January 2022, 28 January 2025, **5 February 2026**), and its final survey in
December or the following January (15 December 2022; 21 January 2025 for the 2024 crop;
4 December 2025 for the 2025 crop). **No Conab estimate for the 2027 crop exists before its first
survey, expected late January or early February 2027. Any note published before that survey says
so explicitly.** A February survey is already covered by the §6 fallback: note 3 goes out on the
first business day of February without the Conab line, and a scorecard addendum follows the
survey. Confirm the 2027 dates from Conab's published calendar rather than assuming them.

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

By **the first week of February 2027** (revised twice — see SPEC_CHANGELOG: the original "late
November" was inconsistent with shipping notes in December and January, and "late January" could
be missed by design once note 3 was timed to follow Conab's first survey):

1. Public GitHub repo, `brazil-arabica-index`, with a reproducible Earth Engine + Python pipeline,
   rerunnable in an afternoon.
2. A backtest table against Conab final arabica yield, **by note date** (§5 step 8), with
   crop 2022 (July 2021 frost; declared in-sample, §5 step 6) and crop 2025 (2024 drought)
   reported explicitly, whichever way they come out.
3. Three notes published, each with one chart and one view: the Jun–Aug 2026 frost review (late
   November), the first index note (first week of December), and the post-survey note (within
   five business days of Conab's first 2027 survey, or 1 February under the fallback; §6).
4. Sent to at least 20 named people in softs, with replies logged.

## 3. Scope

Arabica only, Brazil only, four regions. Robusta (Espírito Santo, Rondônia) is out: different crop
calendar, different exchange, and it would double the mask work for a market not being pitched.

| Region (Conab unit; trade name) | State | Why it matters | Dominant risk |
|---|---|---|---|
| Sul e Centro-Oeste de Minas; "Sul de Minas" | MG | Largest arabica area; rain-fed, hilly | Drought at flowering, frost |
| Triângulo, Alto Paranaíba e Noroeste; "Cerrado Mineiro" | MG | Flat, mechanised, partly irrigated; highest yields | Drought (irrigation masks it), heat |
| Zona da Mata, Rio Doce e Central; "Matas de Minas" | MG | Steep smallholder terrain, lower yields | Rain at harvest, disease (neither is an index input) |
| São Paulo, or its Mogiana split if Conab publishes one (§4c); "Mogiana" | SP | Historic frost zone (1975, 1994, 2021) | Frost, drought |

**Region boundaries (AMENDED 2026-10-12)** follow Conab's own groupings, not origin or marketing
boundaries such as the Cerrado Mineiro designation.
- In Week 0, confirm from Conab's methodology which IBGE units each grouping is built from (the
  older mesoregions or the 2017 intermediate regions). Record the municipality list per region
  with its source. **Done 2026-10-13 (Amendment 34):** Conab's September 2026 bulletin describes
  the Minas regions by IBGE 1989 mesoregions. The proposed membership
  (`docs/week0/proposed_region_membership.csv`) is registered at `prereg-2` as provisional:
  Campo das Vertentes and Metropolitana de Belo Horizonte are placed in Zona da Mata, Rio Doce e
  Central on an area fit (PAM 2025 against Conab 2025: +3.1% Sul e Centro-Oeste, −8.5% Zona da
  Mata, Rio Doce e Central, against +7.8% and −16.1% the other way) and on geography. If Conab's
  Minas Gerais office answers before `prereg-2`, its answer supersedes the test.
- **Outside the index:** Conab's fourth Minas unit (Norte, Jequitinhonha e Mucuri), and arabica
  outside MG and SP, such as Espírito Santo, Bahia and Paraná.
- The four units' share of Brazil's arabica is computed from Conab and stated in every note.

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
  as the first 2028 signal. The GFS forward frost-risk flag is built for that window, from June
  2027; it plays no part in the notes on the 2027 crop.

**Season convention (AMENDED 2026-10-12).** Season S is the crop harvested in year S: Conab's safra
S, and the trade's S/S+1, so 2026/27 is season 2026. Its windows:

| Window | Months |
|---|---|
| Pre-flowering dry season | May–Aug of S−1 |
| Frost exposure | Jun–Aug of S−1 |
| Flowering | Sep–Nov of S−1 |
| Bean fill | Dec of S−1 to Mar of S |
| Harvest | May–Sep of S |

**Every year label in this spec, the backtest table and the notes is a crop year S**, unless it
explicitly names a weather window or event. For example, "the July 2021 frost" belongs to crop
2022.

**Consequence for note 1:** note 1 is the **Jun–Aug 2026 frost review**, published in late
November. It carries that **backward-looking frost assessment as settled fact**, not a forward
risk. This is an advantage, not merely a correction — the frost question for
the crop being tracked is already answerable.

## 4. Data sources

Every ID below was verified to resolve in Earth Engine on 2026-10-12 (see SPEC_CHANGELOG), except
where a row says otherwise.
**Do not substitute an ID. If one is dead, stop and report it.**

| Layer | Source | Resolution / cadence | Use |
|---|---|---|---|
| **Baseline vegetation — PRIMARY** | `MODIS/061/MOD13Q1` | 250 m, 16-day, 2000– | NDVI/EVI anomalies; the backtest baseline (§4a). Terra is at end of mission and its orbit is drifting: continuity check, trigger and fallback in §4a |
| Drift check only | `MODIS/061/MYD13Q1` (Aqua) | 250 m, 16-day, 2002– | Week 0 Terra drift check (§4a). **Not yet verified to resolve.** |
| Drift-check reference only | `NASA/VIIRS/002/VNP13A1` | 500 m, 16-day composites, 2012– | Second reference in the Week 0 drift check, 2018 to October 2026 only. **Not a fallback:** NASA ends Suomi NPP VIIRS delivery on 2 November 2026 (§4a). **Not yet verified to resolve.** |
| Vegetation fallback, candidate (a) | `NASA/HLS/HLSS30/v002` (HLS, Sentinel-2 only) | 30 m; baseline July 2017 to 2025 | Live fallback as monthly EVI over the mask, if it passes the rainy-season coverage test (§4a). `NASA/HLS/HLSL30/v002` coverage reported as information only. Both resolve (Week 0 report) |
| Vegetation fallback, candidate (b) | VJ113A1 (NOAA-20 VIIRS). **Not in Earth Engine**; ingested from NASA as a private asset over the MG/SP window, only if HLS fails the coverage test | 500 m, 16-day composites | §4a. **Ingested** as `vj113a1_mgsp_v2`: 401 composites, 2018-01-01 to 2026-09-14, CRS declared as SR-ORG:6974. **Passed the acceptance check on 2026-10-14**, 0 of 40 months below 60% (Week 0 report) |
| Rainfall — final | `UCSB-CHG/CHIRPS/DAILY` | 5 km, daily | Baseline and the whole backtest; current season once a month is final (§9). Flowering deficit, bean-fill cumulative |
| Rainfall — current season | CHC's own CHIRPS-prelim files (chc.ucsb.edu), **pentad and daily**, ingested as private Earth Engine assets over the MG/SP window | 5 km; pentad and daily; archive from 2015 | Current-season months not yet published as final, and the sensitivity rerun (§9). **Ingestion not yet built.** The community-catalog asset `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad` (archive from 2025 only) is no longer a source; it is kept as a weekly cross-check that the ingestion matches |
| Heat days | `ECMWF/ERA5_LAND/HOURLY` | 9 km, hourly | Heat days above 34 °C. **No frost role** (§4b) |
| Elevation | `USGS/SRTMGL1_003` | 30 m, static | 95th percentile of coffee-mask elevation per region, for the frost station cut (§5 step 4). Resolves (Week 0 report §1, 2026-10-13) and was used for the provisional station cut on 2026-10-14. Declared fallback: `COPERNICUS/DEM/GLO30_2024_1`, which also resolves (the earlier `COPERNICUS/DEM/GLO30` is deprecated). Both are surface models that include canopy, which does not matter for a station altitude cut at the 95th percentile |
| Soil moisture | `ECMWF/ERA5_LAND/HOURLY`, `volumetric_soil_water_layer_1`–`_3` (0–7, 7–28, 28–100 cm; volume fraction), weighted 0.07 / 0.21 / 0.72 by layer thickness | 9 km, hourly | Root-zone moisture through the pre-flowering dry season, May–Aug of S−1 (§5 step 5). Band names and depths confirmed from the Earth Engine catalog; weights registered at `prereg-1` |
| Short-range forecast | `NOAA/GFS0P25` | 0.25°, 6-hourly, 16 days | **Not used before June 2027.** Forward frost-risk flag for the Jun–Aug 2027 window, the first 2028 signal (§3a) |
| Coffee mask | MapBiomas **Collection 11** (Amendment 16c), **class 46 = Coffee** | 30 m, annual **1985–2025** | Where to compute the indices |
| Planet — v1.5 only, never an input | PlanetScope surface reflectance harmonised to Sentinel-2, via Planet Education & Research access | 3 m | The three bounded tasks in §4d. Not in the index or the backtest. Verify the product name and harmonisation against Planet's documentation |

MapBiomas asset, verified (Amendment 16c, 2026-10-14):
`projects/mapbiomas-public/assets/brazil/lulc/collection11/mapbiomas_brazil_collection11_coverage_v3`
41 annual bands `classification_1985` … `classification_2025`.
- **Release and legend:** Collection 11 was launched on 12 August 2026, and this is the coverage
  asset named on MapBiomas's own Earth Engine asset page. Its legend (`legend_code_mapbiomas_brazil_collection_11.csv`)
  gives class 46 as "Café".
- **It replaces Collection 10**
  (`projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v1`,
  1985–2024), which is no longer used.
- **Agreement check:** in a Sul de Minas test box (W −45.9, S −21.9, E −45.1, N −21.3), class 46
  covers 16.4% in Collection 10 (2024), and 17.1% in Collection 11 for both 2024 and 2025. 98% of
  Collection 10's coffee pixels are coffee in Collection 11.
- **Open question 1 in the original spec is closed:** no fallback to a generic cropland mask is
  needed, and the mask supports the full MODIS-era backtest.

**Non-GEE data (download manually, store in `data/raw/`, never modify):**

- **INMET automatic station data** — annual ZIP archives, **2000 through 2026**, from
  `portal.inmet.gov.br/dadoshistoricos`. **This host is not reachable from the project sandbox**
  (curl returns 000 while control hosts return 200), so it is a manual download, like DWR and CIMIS
  in the earlier studies. Record retrieval date and checksum in `data/raw/inmet/SOURCE.md`.
  Confirm on first download that daily minimum temperature is present for automatic stations.
- **INMET conventional station daily minima** — **under evaluation as a second frost network**
  (§5 step 4, Amendment 17c). Daily "TEMPERATURA MINIMA, DIARIA" from BDMEP
  (`bdmep.inmet.gov.br`), requested by the owner through BDMEP's e-mail form and stored in
  `data/raw/inmet/bdmep/` with retrieval date and checksum. The station list comes from BDMEP's
  own station API, which, unlike the portal's catalogue, includes closed stations.
- **Conab coffee surveys** — the benchmark and backtest target. Conab has monitored coffee since
  **2001**, which bounds the backtest. Bulletins are PDFs; the regional series must be extracted
  from them. See §4c.
- **IBGE PAM** municipal coffee area and production; **IBGE Censo Agropecuário** irrigation share.
- **USDA FAS GAIN Brazil Coffee**, ICO Coffee Market Report, Cecafé monthly exports, Cooxupé.
- **Market data:** ICE Coffee C settlement, calendar spreads, certified stocks; CFTC COT.
  **Check ICE's redistribution terms before any ICE settlement, spread or certified-stocks data
  goes into the public repo.** Until then, ICE figures appear in the note text only, never in
  committed data files. **CFTC COT data are a public-domain US government work** and sit outside
  the ICE check.

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

- **Week 0 drift check (method fixed before it runs, Amendment 26).** Compare `MOD13Q1` NDVI and
  EVI anomalies with the reference, `VNP13A1` (VIIRS), 2018 to October 2026. HLS is **not** a
  reference: it failed its cost gate (Amendment 31, revised). `MYD13Q1` (Aqua) is reported
  alongside but is not a reference: its orbit is drifting too, so it is not independent of Terra.
  Compare anomalies, not levels: the products differ in resolution and overpass time.
  - **Anomalies** are calendar-month anomalies for every product, against a common July
    2017–2025 baseline (Amendment 26, second revision), each computed over the product's own
    pixels within the mask. Monthly aggregation removes the offset between the products'
    compositing windows; the common baseline puts every product on the same years.
  - **Provisional run, now:** over all class-46 coffee pixels in MG and SP, labelled provisional.
    **Formal run:** per region and for the four-region total, once the regional municipality
    lists exist (§3). Trigger (b) is evaluated on the formal run only. Both go in the Week 0
    report.
  - Report the difference series and its trend. **With a single reference, the check cannot
    attribute cause:** a divergence between Terra and VIIRS may come from either, and the report
    says so (Amendment 31, revised).
- **Trigger, fixed before the check runs.** Switch the current-season vegetation input to the
  fallback if either (a) `MOD13Q1` is not current at a note date, meaning no composite ends within
  32 days of the note date; or (b) Terra's **EVI** anomaly diverges from VIIRS (Amendment 31,
  revised) by a **signed** average of more than 0.5 standard deviations of the July 2017–2025
  monthly baseline over 2024–2026, in the coffee-area-weighted four-region total or in two or
  more regions. Signed, not absolute: an absolute average fires on ordinary month-to-month noise
  between products (Amendment 26, revised). EVI because it is the index's vegetation input
  (§5 step 6); NDVI is reported alongside but does not trigger (Amendment 33). Per-region
  differences are reported either way.
- **Fallback (Amendment 25, revised 2026-10-13).** `VNP13A1` is no longer the live fallback:
  NASA ends delivery of Suomi NPP VIIRS science data on 2 November 2026 (Earthdata, VNP13A1
  v002). It stays only as the drift check's reference, 2018 to October 2026. The live
  fallback, in order:
  - (a) **HLS**, `NASA/HLS/HLSS30/v002`, aggregated to monthly EVI over the mask, if it passes the
    rainy-season coverage test below;
  - (b) if HLS fails, **VJ113A1** (NOAA-20 VIIRS, 500 m). It is not in the Earth Engine catalog,
    so it is ingested from NASA as a private Earth Engine asset over the MG/SP window only, built
    the same way as the CHC prelim ingestion (§4). The ingestion does not start unless HLS fails;
  - (c) a declared gap, only if both fail: no vegetation reading, stated in the note.
  - **HLS evaluation (Amendment 30).** HLSS30 only, with a baseline from July 2017 to 2025, so
    the first rainy season in it is 2017/18 and the sensor set is Sentinel-2 A/B throughout;
    Sentinel-2C is treated as A's replacement in 2024–25. The per-month observation count is
    reported so any step in the record shows, including January–March 2017, as information.
    HLSL30 stays out of the baseline; its coverage is reported separately, as information. HLS
    was also to be the second drift-check reference (Amendment 31); it failed that cost gate and
    is not a reference (Amendment 31, revised).
  - **Rainy-season coverage test.** Monthly coverage is the share of mask pixels with at least
    one clear HLSS30 observation in the month. If it falls below 60% in more than two months of
    the November–March baseline period, record that HLS cannot carry the rainy season, and the
    fallback moves to (b). **Result (2026-10-13): HLS failed, 7 of 42 months** (Week 0 report).
  - **VJ113A1 acceptance check (Amendment 30, second revision).** The fallback is held to the same
    test as the one that failed. Before VJ113A1 is relied on, for every 16-day composite in its
    2018–2025 baseline: monthly coverage is the coffee-area-weighted share of VJ113A1 pixels within
    the mask that have a "good" pixel reliability (0–3, excellent to marginal, as in the drift
    check) in at least one composite starting in that month. If it falls below 60% in more than two
    of the 40 November–March months in 2018–2025, record that VJ113A1 cannot carry the rainy
    season, and the fallback moves to (c). The check is probe-gated: one month first, at most 0.25
    EECU-hours, which keeps the 40 months under about 10 EECU-hours. **Result (2026-10-14):
    VJ113A1 passed, 0 of 40 months below 60%**; the lowest was 69.4%, in December 2021, and an
    independent recount from the local files agreed within 0.4 points (Week 0 report). The first
    probe cost 0.71 EECU-hours, over the gate, because it rebuilt the coffee weight in every
    request. With the weight saved once as an asset, the re-probe cost 0.01 EECU-hours and the 40
    months 0.45. **The live vegetation fallback is therefore (b), VJ113A1.**
  - If triggered, the current-season anomaly is computed against the fallback's own baseline,
    never against MODIS's.
  - The headline backtest stays on MODIS. The vegetation component is rerun on the fallback for
    the crops its record covers, and the change in skill is reported beside the headline, as for
    CHIRPS-prelim (§9).
  - Resolution changes the Zona da Mata caveat: VJ113A1 at 500 m blurs smallholder terrain more
    than MODIS does, HLS at 30 m less. The note says which applies.
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
- Frost is reported as a **regional flag with its observed coverage share** (§5 step 4), never
  as a precise area.
- **The calibration requirement applies to gridded products matched to stations, not to station
  observations.** The station thresholds are the agronomic constants in §5 step 4, neither
  fitted nor calibrated.

**Check for circularity before using INMET to validate anything.** CHIRPS blends satellite estimates
with station data. If Brazilian stations feed CHIRPS, validating CHIRPS against INMET is circular —
the same trap as PRISM ingesting CIMIS in the almond study, which reframed that study's headline
result. Establish this before the validation is run, not after.

### 4c Conab granularity — São Paulo resolved; historical extraction open

Step 6 regresses on Conab's **regional** yield anomaly. Conab reports by state, and the Minas
regional split does appear in the bulletins — the 2020 first survey quotes Sul de Minas 17.03–17.79M
bags, Cerrado Mineiro 5.82–6.07M and Zona da Mata Mineira 7.21–7.53M. **Mogiana is not known to be a
Conab reporting unit.**

**Resolution order, in Week 0, before any fitting:**

1. Check a recent Conab coffee bulletin PDF for a São Paulo regional split.
2. If there is none, **use São Paulo state total as the Mogiana target** — São Paulo arabica is
   dominated by Mogiana, so the state total is usable.
3. **Only if that proves too noisy in the backtest**, cut to three regions.

**Resolved for São Paulo, 2026-10-13 (Amendment 34):** Conab's 3rd survey of safra 2026 (bulletin
and data table, stored in `data/raw/conab/`) reports São Paulo only as a state total; the bulletin
names Alta Mogiana, Média Mogiana, Alta Paulista and Circuito das Águas in its text but gives no
figures for them. **The São Paulo state total is the Mogiana target.** The same table splits Minas
Gerais into its four regions with area, yield and production; whether earlier surveys carry the
split back to 2001 in usable form is the extraction work still open.

**Do not cut Mogiana pre-emptively.** It is the frost region, and losing it weakens the component
with the most distinctive story.

Also to settle in Week 0: the bulletins are PDFs, so building a ~25-season regional target series is
extraction work. Budget for it, and record which survey vintage each value came from.

**Target series, decided 2026-10-14 (Amendment 19b).**
- **The backtest target is Conab's final figure for each safra as it stands in the current
  historical series.** Conab's arabica series (`cafearabicaseriehist.xls`) was downloaded on
  2026-10-14, with SHA-256 in `data/raw/conab/SOURCE.md`; any later download is a new vintage
  and is logged.
- **Arabica area and yield by region begin with safra 2008.**
- **For 2001–2007, Sul e Centro-Oeste, Triângulo, Alto Paranaíba e Noroeste, and São Paulo take
  area, yield and production from Conab's arabica-plus-conilon series** (`cafetotalseriehist.xls`).
  The justification: in all 18 safras 2008–2025 the two series are identical in both area and
  production in these three regions.
- **Zona da Mata, Rio Doce e Central, which carries conilon, starts in 2008.**
- **Survey vintage tables** (first, third and final surveys) are used only for the surprise test
  and for the biennial-term sensitivity (§5 steps 7 and 8).
- **Findings on Conab's arabica series for 2001–2007,** recorded, not corrected; this is why the
  early years come wholly from the other series:
  - it records 2004 regional production as 0 for Sul, Triângulo and Zona da Mata, a missing value
    written as zero;
  - in 2002 and 2006 its Sul production exceeds the arabica-plus-conilon total (13,200 against
    11,633, and 12,043 against 11,633 thousand bags);
  - which series is right for Sul in those two years is not established.

### 4d Planet: bounded v1.5 tasks, never an input (AMENDED 2026-10-12)

Planet Education & Research access is confirmed. **Planet stays out of the index and the
backtest.**

Three bounded v1.5 tasks, in this order:
1. **Mask validation** of the municipalities that fail the 30% filter (§5 step 1).
2. **A one-time 2021 frost case study** over Mogiana and Sul de Minas.
3. **One illustrative 3 m figure per public note**, labelled as not an input.

**Start rule.** The tasks begin once the backtest is complete, in the order above, so they never take
time from it (§8). The figure per public note starts with the first note after the backtest is
complete.

**Licence and handling.**
- The Education & Research terms are non-commercial. Planet-derived material appears only in the
  repo and public posts, **never in the note emailed to desks**.
- No raw scenes are committed to the repo. The README states the data source and the programme.
- Check the current monthly area quota in the Planet dashboard and record it (§10).
- Use the surface-reflectance product harmonised to Sentinel-2.

## 5. Method

A set of regional anomalies against the MODIS-era baseline, combined into one condition index per
region and scored against Conab. **Keep it simple enough to explain in a 15-minute call.**

1. **Mask.** Clip MapBiomas class 46 to the four regions; drop municipalities whose MapBiomas area
   typically **exceeds** IBGE PAM coffee area by more than 30% (one-sided, stable membership,
   Amendment 16d; below). **Freeze the mask for the season.**
   **Report what the filter removed and whether the removed municipalities differ from the kept**
   (§9) — the 30% trigger very likely correlates with steep smallholder terrain, so it may
   preferentially delete Zona da Mata, the region the mask is least reliable in.

   **The filter rule (AMENDED 2026-10-14, Amendment 16d).**
   - **Why it changed:** the original two-sided rule assumed that MapBiomas and PAM roughly
     agree. Inspection disproved that (Week 0 report §12).
     - Collection 11 maps 0.19–0.63 of PAM's coffee area in São Paulo and Zona da Mata, and about
       half in every region in the early years.
     - Only 18% of municipality-years agree within 30%.
     - The two-sided rule kept 4–19% of São Paulo's mapped coffee in every season.
   - **One-sided:** MapBiomas below PAM is omission, and the pixels MapBiomas does map are kept.
     MapBiomas above PAM is the over-mapping risk the filter was written for (bearing-area
     mismatch, below).
   - **Stable membership:** each municipality is tested once and kept or dropped for every
     season. Season-by-season membership would put composition changes into the anomaly series,
     and single-season crossings of the threshold are noise, not over-mapping. Under a
     season-by-season test, Campos Gerais exceeded 1.3 in only 7 of 28 years (median ratio 0.88),
     and Três Pontas in 6 (median 0.98).
   - **The test:** a municipality's ratio in each mask year M (1998–2025) is its persistent-pixel
     MapBiomas area (Amendment 16b) over PAM's coffee area for M.
     - PAM recording zero where MapBiomas maps coffee counts as an infinite ratio.
     - Years with no coffee on either side, and years PAM marks missing (`...`), are not counted.
     - **The municipality is dropped when the median of its ratios exceeds 1.3.**
   - **Comparator:** PAM table 1613, variable 2313 (area intended for harvest), "Café (em grão)
     Total". MapBiomas class 46 does not separate species, and PAM's arabica split exists only
     from 2012.
   - **Municipalities with mapped coffee but no comparable year** are dropped as untestable. There
     are 5, holding about 553 ha of mapped coffee, 550 of it in Santa Rita de Ibitipoca.
   - **What it removes** (`docs/week0/w1_filter_stable_removed.csv`): 55 municipalities in Sul, 144
     in São Paulo, 18 in Triângulo and 84 in Zona da Mata. Most are municipalities where PAM
     records little or no coffee but MapBiomas maps some. The largest is Jacuí (Sul, mean 4,700
     ha mapped), above 1.3 in all 28 years with a median of 1.88. Campos Gerais, Três Pontas and
     Boa Esperança are kept.
   - **Retention:** share of mapped coffee kept, over mask years 1998–2025
     (`docs/week0/w1_retention_stable.csv`):

     | Region | Two-sided rule, per season (replaced) | One-sided rule, stable membership (registered) |
     |---|---|---|
     | Sul e Centro-Oeste | 0.15–0.83 | 0.79–0.95 |
     | São Paulo | 0.04–0.19 | 0.79–0.84 |
     | Triângulo, Alto Paranaíba e Noroeste | 0.07–0.96 | 0.997–0.999 |
     | Zona da Mata, Rio Doce e Central | 0.15–0.48 | 0.89–0.97 |

   - **Applied at aggregation.** W1 reduces every composite per municipality, and the filter is
     applied when municipal values are combined into regions.
   - **Aggregation weights.** Regions are aggregated by IBGE PAM coffee area, as registered in §3.
     - **PAM year:** for season S it is S−2, the same lag as the mask. That is the latest PAM
       available at the note date: PAM 2025 was available on 2026-10-14, for crop 2027.
     - **No PAM value:** a municipality with no PAM value for that year gets zero weight.
   - **Registered sensitivities,** reported beside the headline like the persistent-pixel mask:
     - no filter (the full class-46 mask);
     - regions aggregated by mapped coffee area (MapBiomas) instead of PAM coffee area.
   - **Chosen after inspection.** The rule was chosen after seeing what the original filter
     removed. That is mask information, not yield or frost outcomes; it is registered at
     `prereg-2` with this statement.

   **Representativeness caveat (Amendment 16d).** The index's vegetation signal comes from the
   coffee MapBiomas detects. That coffee is biased toward large, sun-grown fields, and the bias is
   worst in Zona da Mata and São Paulo, where MapBiomas maps barely half of PAM's coffee area. The
   smallholder and shaded coffee it misses is under-represented in the index.

   **Week 0 finding (2026-10-14, Amendment 17c).** In a 20,000-point random sample of MapBiomas
   class 46 (2024), each region's share of the index's points divided by its share of IBGE PAM
   2025 arabica area is 0.80 for Zona da Mata, Rio Doce e Central and 0.77 for São Paulo, against
   1.15 for Sul e Centro-Oeste and 1.11 for Triângulo, Alto Paranaíba e Noroeste. MapBiomas finds
   relatively less coffee than PAM records in Zona da Mata and in São Paulo. For Zona da Mata that
   fits under-detection of steep smallholder coffee; for São Paulo the cause is not established.
   Either way the 30% filter is expected to remove these two regions' municipalities more often
   than the others', and the removal report is read with that in mind.

   **Mask year by season (AMENDED 2026-10-12; Collection and lag set 2026-10-14, Amendment 16c).**
   - Each backtest season uses the mask production would have had at its note date. Every season
     uses **Collection 11's** classifications, so all seasons are on the same product. Older
     collections are not used: they differ in method, and some predate class 46.
   - The mask year is the crop year minus a fixed lag, set to the live lag for crop 2027.
     **The lag is S−2**, because a collection covering 2025 (Collection 11) was published and
     verified before note 1. Crops 2001–2027 therefore use mask years 1999–2025.
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
   - Both masks are registered at `prereg-2`, with the filter rule and its sensitivities
     (Amendment 16d).
2. **Vegetation anomalies (AMENDED 2026-10-15, Amendment 35).** From `MOD13Q1`, per 16-day
   composite, with `SummaryQA` 0–1 (good or marginal) as the cloud mask. NDVI, for the
   sensitivity report, is computed the same way as EVI.
   - **Municipal reading:** the coffee-weighted median EVI over the municipality's mask pixels. A
     reading counts only if at least one MODIS pixel's worth of cloud-free coffee remains in that
     composite (summed coffee fraction of valid pixels ≥ 1).
   - **Members:** in season S, the municipalities that meet all of the following:
     - kept by the filter (step 1);
     - have PAM coffee area for PAM year S−2;
     - have at least one MODIS pixel of mapped coffee under season S's mask (summed coffee
       fraction ≥ 1, about 5.4 ha).
     PAM weights are renormalised once per season over the members.
   - **Municipal anomaly:** the reading minus the municipality's own mean for the same 16-day
     period, in EVI units.
     - The mean is taken over composites dated 2000–2025, from the municipality's counted readings
       in the seasons in which it is a member.
     - A municipality-period with fewer than 10 years of readings has no anomaly.
     - In the backtest the mean is refitted without the held-out season (step 8).
   - **Regional anomaly:** the PAM-weighted mean of the members' anomalies (PAM year S−2), over
     the members with an anomaly in that composite. Anomalies are aggregated, not raw EVI, so a
     change in which municipalities have a reading does not move the regional value through their
     EVI level.
   - **Cloud floor:** a regional composite is missing when the members with an anomaly hold under
     50% of the season's member PAM weight. The covered-weight fraction is reported for every
     composite.
   - **Standardisation:** the regional anomaly is expressed as a z-score against the same 16-day
     period across the baseline years, refitted without the held-out season.
   - `MOD13Q1` has no 1.6 µm band, so the standard NDMI cannot be computed from it and is not an
     input.
3. **Rainfall windows.** CHIRPS totals for flowering (Sep 1–Nov 30) and bean fill (Dec 1–Mar 31).
   Harvest-window rain (May–Sep of S) is not an index input: it falls after every note about the
   crop it affects. This removes the harvest window of year S only. May–Aug of S−1, the
   dry season before flowering, falls before every note about crop S and is not affected; it is the
   window of the dry-season soil-moisture input (step 5). **Flowering deficit is the single most
   predictive input;** weight it accordingly.
4. **Frost events (AMENDED 2026-10-12).** Station observations only (§4b). **Assign each frost
   window to the crop it actually affects (§3a).**
   - **Stations: per-season membership (Amendment 17c).** INMET automatic stations inside or
     within 25 km of the coffee mask. A station counts in a season when its Jun–Aug record for
     that season is complete: at least 95% of hourly observations present, with no gap longer
     than 48 consecutive hours. Membership therefore changes from season to season, a declared
     exception to §9's identical-observations rule. Record each station's coffee area within that
     radius. Leave out of the weighting any station above the 95th percentile of coffee-mask
     elevation in its region (DEM, §4; station elevation from INMET metadata). Register the
     station list per region and season, with counts, and the elevation cut at `prereg-2`, and
     report every station within 50 m of the cut.
   - **Conventional network (Amendment 17c, under evaluation).** Before `prereg-2`, INMET's
     conventional stations are evaluated as a second source: daily minimum temperature from BDMEP
     (§4), the same 25 km radius and elevation cut, and a station counts in a season when at
     least 95% of its Jun–Aug days have a daily minimum, with no gap longer than 3 consecutive
     missing days (the daily analogue of the 48-hour rule). A window with a longer gap fails for
     that station-season, and Amendment 17b's missing-night rule applies to the remaining
     missing days. If they lift observed coverage, the two
     networks are combined, with the network recorded per station; if they don't, the automatic
     network is used alone. For a conventional station a night is observed when its daily minimum
     is present.
   - **Night rule for conventional stations (Amendment 17d), provisional until INMET's
     documentation is cited.** INMET reads the conventional minimum at 12 UTC, covering the
     preceding 24 hours, so a minimum dated D belongs to the night ending the morning of D.
     - **Checked 2026-10-14 against six same-site automatic stations,** all months 2008–2026: the
       night ending the morning of D agrees far better than the night ending the morning of D+1
       in all six. For the four pairs without an offset, the mean absolute difference is
       0.38–0.50 °C against 1.10–1.46 °C.
     - **The check does not resolve the exact 24-hour boundary** (12 UTC or the UTC calendar
       day). Both place the minimum on the morning of D.
   - **Stations sharing a site (Amendment 17d).** A conventional and an automatic station share a
     site when they lie within 1 km of each other in INMET's catalogues.
     - **Which station counts:** where both have complete records for a season, the automatic
       station governs the tier for that season, and the conventional station is left out of the
       union. The conventional station fills only seasons where the automatic record is
       incomplete.
     - **Offsets:** each pair's offset (median, conventional minus automatic, over the
       rule-window minimum) is recorded in the station table, `docs/week0/colocated_pairs.csv`.
       No correction is applied.
     - **Flag:** any season in which a conventional station alone would change a region's tier is
       flagged.
   - **Observed coverage (Amendment 17c).** A region's observed coffee in a season is the coffee
     area inside the union of the 25 km circles of that season's qualifying stations, with
     overlaps counted once, including overlaps between networks. Observed coverage is observed
     coffee divided by the region's coffee area. A tier's share is the observed coffee inside the
     circles of stations meeting that tier, divided by observed coffee.
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
   - **Missing nights (Amendment 17b).** A night counts as observed only if every hour from
     18:00 to 09:00 local time is present (INMET timestamps are UTC). A missing night is never
     counted as a non-frost night. If a station's missing nights could change its tier for a
     season, its tier for that season is reported as unresolved, and the region's tier shares
     are reported with and without it.
   - **Regional flag (Amendment 17c).** A region is flagged for a tier in a season when stations
     meeting that tier cover at least 25% of its observed coffee. Reaching the flag triggers an
     out-of-cycle note at that point, not at the end of the window.
   - **Coverage floor (Amendment 17c).** No flag in a region-season whose observed coverage is
     under 15%. Such a region-season is reported as unflaggable, and every note covering it says
     so. **The 15% floor was chosen from coverage information only, before any frost night was
     counted**, and is registered at `prereg-2` with that statement. Observed coverage per region
     and season is reported at `prereg-2`, so every unflaggable region-season is known before the
     first run.
   - **Series.** The frost component starts with crop 2009 (the Jun–Aug 2008 frost window) and
     is not filled for 2001–2008. The index is scored in two versions, each with its own pass
     mark, and the two are compared only on the seasons they share: without frost, on every
     season; with frost, from crop 2009. The backtest table reports, per region and season, the
     station count by network and the observed coverage.
5. **Heat and dry-season stress (AMENDED 2026-10-12).**
   - During flowering (Sep–Nov of S−1): days above 34 °C (ERA5-Land) and consecutive dry days
     (CHIRPS).
   - Through the pre-flowering dry season (May–Aug of S−1): root-zone soil moisture (ERA5-Land,
     §4), as an anomaly against the same window across the baseline years.
6. **Condition index (AMENDED 2026-10-12).** Two stages.
   - **Stage 1, expectation.** For each region: an intercept, a linear trend and a biennial
     coefficient (step 7). That is three parameters per region, and they do not count toward
     the cap.
   - **Stage 2, condition weights.** A ridge regression of the stage-1 yield anomaly, after the
     frost offset, on four standardised inputs, with one set of weights shared by all four
     regions:
     - EVI anomaly
     - flowering rain deficit
     - dry-season root-zone soil moisture
     - heat days during flowering
     **These four weights are the cap of four.**
   - **EVI is the single vegetation term.** Coffee canopies are dense, NDVI saturates in them,
     and EVI was designed for that case. NDVI appears only in the sensitivity report. This is
     registered at `prereg-1` with that reason. **The sensitivity report states that the NDVI
     series carries a 2024–26 drift of unresolved cause (Week 0 drift check) and that any
     NDVI-based result is unreliable for those years** (Amendment 33).
   - **Computed and reported, but not fitted:** NDVI, consecutive dry days, and bean-fill rain
     to date. Frost enters as a fixed offset (below) and does not count. If the Cerrado
     irrigation adjustment (§10 item 5) is adopted, it is a fixed multiplier, not a parameter.
   - **The ridge penalty** is chosen by an inner leave-one-year-out loop inside each training
     set, from a grid fixed at `prereg-1`.
   **Frost is not fitted (AMENDED 2026-10-12).** The backtest window holds one major frost (July
   2021, crop 2022). A fitted frost weight would be set by that one season, and leaving that
   season out would remove the only evidence for it.
   - Frost enters as a **fixed yield penalty for each frost tier** in each flagged region. The
     tiers and the flag are defined in step 4. Each tier's penalty is the yield loss on affected
     area, multiplied by that tier's share of the region's observed coffee (step 4), the same
     share as the flag. **This assumes that unobserved coffee behaves like observed coffee**
     (Amendment 17c). The 25% flag therefore sets the floor, and the penalty grows with the
     tier's share. Tiers are exclusive: the severe-tier penalty applies to
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
7. **Biennial adjustment (AMENDED 2026-10-12).** Arabica alternates on and off years, but shocks
   reset the cycle. The July 2021 frost cut crop 2022, which was an on-year. A fixed alternating
   term assumes the phase never moves.
   - Instead, the expectation for crop S includes a coefficient on crop S−1's yield anomaly.
     A low year then predicts a rebound and a high year a dip, whatever the calendar phase.
   - **Crop S−1's anomaly (AMENDED 2026-10-14, Amendment 19b)** uses Conab's final figure for that
     crop in the current historical series, the same series as the backtest target. Every vintage
     therefore uses the same value.
     - **This is a declared leak.** At a November note, production has only the third survey of
       crop S−1, published in September of S−1, and uses it. Third-to-final yield revisions for
       safras 2023–2025 averaged 1.9% in absolute size, with a largest of 8.4% (Triângulo 2023).
     - **Sensitivity, reported beside the headline:** for the crops whose previous crop has a
       third survey on record (S−1 = 2023–2025), the biennial term is recomputed from the third
       survey. That measures the effect of the leak where it can be measured.
   - Report the index **relative to this expectation**, or every off-year reads as a crop
     failure.
8. **Backtest by note date (AMENDED 2026-10-12).** Leave-one-year-out, **using only inputs available
   as of each note date.** For each season × each of November, December and January, fit on the
   other seasons and predict direction and rough size. **Report hit rate and mean absolute error
   separately for the November, December and January vintages.**
   **Expect November to be the weakest, and publish that number anyway** — it is the only skill
   figure a desk will take seriously, and a full-season backtest would flatter the model by scoring
   it with information it will not have in production. Call out crops 2022 and 2025 explicitly.

   **Leave-one-season-out, across regions (AMENDED 2026-10-12).** A season is held out in all
   four regions at once, because the regions share weather. Everything fitted is refitted
   without the held-out season: the z-score means and standard deviations, the trend, the
   biennial coefficient, the ridge penalty and the weights.

   **Two targets.**
   - **Condition direction:** the sign of actual yield minus the stage-1 expectation. This is
     what the index claims to predict.
   - **Yield versus trend:** the sign of actual yield minus trend. The full model predicts it as
     the expectation plus the index.

   **Comparison models, scored on the same seasons:**
   - **Zero anomaly** (actual equals the expectation): the mean-absolute-error baseline for the
     condition anomaly.
   - **Biennial only** (the expectation with no index): the baseline for yield versus trend.
     The index adds skill only if the full model beats it.
   - **Rain only** (the expectation plus flowering rain deficit alone): shows whether EVI, soil
     moisture and heat days add anything beyond rain.

   **Pass marks, fixed in advance, on condition direction (AMENDED 2026-10-14, Amendment 19b).**
   The rule is p < 0.05, one-sided against a coin flip, and **the exact p-value is reported beside
   every pass mark:**
   - Without frost, Sul e Centro-Oeste, Triângulo, Alto Paranaíba e Noroeste, and São Paulo,
     crops 2001–2025: **18 of 25** (p = 0.0216).
   - Without frost, Zona da Mata, Rio Doce e Central and the four-region total, crops
     2008–2025: **13 of 18** (p = 0.0481).
   - With frost, every region and the four-region total, crops 2009–2025: **13 of 17**
     (p = 0.0245).
   If the share of positive condition anomalies is away from 50%, each pass mark becomes the
   larger of its own value and the count that beats the majority share at p<0.05. That is
   computed at `prereg-2`.

   **Crop 2026** is added when Conab publishes its final, as an addendum reported with and
   without it. The pass marks above don't change. It is not a clean out-of-sample test, because
   Conab's third survey of crop 2026 was public when the features were registered.

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
   - **Until more vintages exist, the surprise test is reported, not scored (Amendment 19b).**
     First- and final-survey figures have been located only for safras 2023–2025 (§4c). So the
     test is reported for those three safras, with no pass mark, until earlier vintages are
     found. Archived copies count as sources if the archive URL, capture date and checksum are
     recorded.
   - Score the four-region total as the headline and each region separately. Report how many
     seasons have both a first and a final survey on record.
9. **Output.** Index per region and a four-region total, every 16 days; frost and flowering-
   deficit flags daily.

**Leave out until v2:** machine-learning yield models, Planet imagery as an index input (v1.5
tasks only, §4d), Sentinel-2 imagery,
field-level analysis, any translation of the index into a price forecast.

## 6. Outputs

1. **Crop notes** (one page, PDF and LinkedIn). **(AMENDED 2026-10-12)**
   - **Note 1, late November 2026: the Jun–Aug 2026 frost review** (§3a). It uses the stations
     with complete Jun–Aug 2026 records, reported as station observations, each with its tier and
     coverage share, and the regional flags they produce for crop 2027 (§5 step 4). Beside them
     goes the public record — Cooxupé, Conab's September bulletin, Somar and press reports — with
     every statement attributed to its source and kept distinct from the station data (Amendment
     17c). It carries no index reading, so it does not use the fixed layout below. The November-vintage index reading is computed as of
     the November note date and published in the repo no later than note 1, so the post-survey
     scorecard can cite it as made before Conab's survey.
   - **Index notes** publish in the first week of each month from December 2026, except the note
     that follows Conab's first survey of the crop.
   - **The post-survey note** publishes within five business days of Conab's first survey of the
     crop. It is the first scorecard: the November and December index readings beside Conab's
     first number, with the surprise-test call stated explicitly (the predicted direction of
     Conab's first-to-final revision, §5 step 8). If Conab has not published by 31 January, the
     note goes out on the first business day of February without the Conab line, and a scorecard
     addendum follows the survey.

   Fixed layout for index notes, so readers learn where to look: headline with the four-region
   index, its share of Brazil arabica, and its direction; chart of index by region against the
   baseline band; region table (index, flowering rain vs normal, frost nights, one-line comment);
   benchmark line against Conab's 2027 estimate, or a statement that none exists yet (§1), and the
   arabica component of the 2027/28 private estimates, or "versus trend and an expected off-year"
   until those are published (§1); market context (Coffee C front month, Jul/Dec spread, ICE
   certified stocks, managed-money net from COT); **the view** — one paragraph, one stated lean,
   and what would change it; method and caveats in three lines, always including **"condition
   index, not a yield forecast"**, the Zona da Mata resolution caveat, and which months used
   CHIRPS-prelim.
2. **GitHub repo** (`brazil-arabica-index`). Public, MIT licence, README that lets someone rerun
   it in an afternoon. GEE scripts, the notebook that builds index and backtest, the mask rule and
   the live season's frozen mask, the backtest table, every note as PDF plus its chart data as CSV
   (no ICE data files until the check in §4 is done).
3. **Dashboard (optional, v1.5).** Only after three notes are out. Polish, not credibility.

**Distribution per note:** LinkedIn post with the chart and three lines; direct email with the PDF;
optionally a thread in r/commodities or the FIC Slack. Planet-derived figures go in the LinkedIn
post and the repo copy only, never in the emailed PDF (§4d). Log every reply with name, firm, date
and what they said.

## 7. Pipeline

GEE does masking, cloud filtering, compositing and regional aggregation, and exports small CSVs.
**The Python notebook never touches raw imagery.** Scheduled run on a 16-day cadence; the note is
assembled by hand from the notebook's charts and tables.

## 8. Timeline

**Week 0 (blocking, before anything else):** every item marked "Week 0" in the §10 checklist,
including §4c Conab granularity, the INMET checks, the CHIRPS circularity check, the unverified IDs
and the Terra drift check.

Then: **W1** frozen mask and first regional EVI and NDVI series (check: the one-sided, stable 30%
filter against IBGE per municipality, with the removal report; Amendment 16d). **W2** anomalies and rainfall windows for every
MODIS-era season (check: report each season's rank on every input, per region and for the
four-region total; if crops 2022 and 2025 are not the worst, that is a finding, and nothing is
changed to make them so). **W3–W4** backtest by note date (check: against the pass marks fixed in
§5 step 8, reported per vintage). **W4** note template on October–November 2026 data (check: a
friend outside ag can read it in two minutes). **W5** scheduled run and README (check: a clean
clone reproduces the index). **W6** note 1, the Jun–Aug 2026 frost review, published and sent in
late November; it needs the station set and frost constants, not the backtest. The first index
note follows in the first week of December.

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
  **Declared exception (Amendment 17c): the frost station set changes by season** (§5 step 4).
  The alternative, a fixed set complete in every season, covers 0.0–0.1% of each region's coffee
  and gives a frost component that can never fire. Station counts and observed coverage per
  region and season are reported in the backtest table, so the changing sample stays visible.
- **Any result of zero, none or empty is verified by an independent method before it is accepted**,
  especially where zero is the expected answer.
- **Never score a model with information it will not have in production.** See §5 step 8.
- **CHIRPS product split, decided 2026-10-12 before the first run; prelim source revised
  2026-10-13 (Amendment 9, revised).**
  - Final CHIRPS for the baseline and the whole backtest, so every season is scored on the same
    product. CHIRPS-prelim, from CHC's own pentad and daily files (§4), only for current-season
    months whose final is not yet published.
  - Final for month M counts as published from the 1st of month M+2. That matches the provider's
    ~3-week latency (final appears after about the 20th of the following month).
  - Production will use prelim where the backtest uses final, so the backtest is optimistic on
    exactly those months. **Quantify it:** rerun every vintage whose note date falls inside CHC's
    prelim archive (from 2015), with prelim substituted for the months not yet final. Report the
    change in hit rate and mean absolute error beside the headline figures, and the
    prelim-minus-final difference in window totals over the mask. Do not correct for it.
  - CHC's daily prelim restores consecutive dry days for months still in prelim. They are not
    compared with final-CHIRPS dry-day counts until the gap has been measured on overlapping
    months (Amendment 29).
- **Every checkpoint report carries its denominator** — how many municipalities, seasons,
  station-nights were examined, not only how many passed.
- Never modify anything in `data/raw/`.
- Secrets stay in `.env` (gitignored). Never print or commit a key.
- Log every spec deviation in `SPEC_CHANGELOG.md` with the reason, at the time it happens.
- **Report negative and inconclusive results as findings.** Do not retune to rescue a result. Say
  "inconclusive" or "not established" when that is the answer, and give the reason.
- **Lean Earth Engine runs (decided 2026-10-13, Amendment 32).** Use a sample wherever a sample
  answers the question. Never repeat a full-resolution pass over the study area without a recorded
  reason. Record each run's compute cost in EECU-seconds in the report, measured with Earth
  Engine's request profiling (`ee.profilePrinting`). This holds whatever the project's quota
  tier.
- **No interactive reductions (decided 2026-10-15, Amendment 32b).** Nothing larger than a few
  pixels is reduced through an interactive request. Every reduction over an area runs as a batch
  export through `gee/ee_watchdog.py`, with a cost estimate from a probe, and is cancelled at twice
  the estimate. Interactive calls are allowed only for metadata, single-pixel reads and vector
  geometry, each tagged in the code, and `gee/check_interactive.py` enforces this. Cost is
  recorded from each batch task's reported EECU use. Reason: the watchdog cannot see interactive
  use, and the 2026-10-13 provisional drift check spent about 356 EECU-hours that way.
- **Pre-registration, in two tagged commits (decided 2026-10-12).** Record every choice that could
  be tuned in `docs/preregistration.md`, and commit it at two points:
  - **Tag `prereg-1`, before W2 computes any season-level input.** It records:
    - the feature list: each input, its source, window and standardisation
    - the weighting method, and which terms count toward the cap of four
    - the direction pass marks
    - the frost tier constants
  - **Tag `prereg-2`, before the first backtest run.** It records the values that need data but
    not results:
    - the mask lag and both masks: full class 46 and persistent-pixel; the one-sided,
      stable-membership filter rule and the list of municipalities it drops, with the statement
      that the rule was chosen after inspecting what the original rule removed; and the registered
      sensitivities, no filter and mapped-area aggregation (§5 step 1, Amendment 16d)
    - the station list per region and season with counts and network, the altitude cut, the
      observed coverage per region and season, and the 15% coverage floor with the statement
      that it was chosen from coverage information only, before any frost night was counted
      (§5 step 4)
    - the surprise-test pass mark computed from Conab's base rate, once vintages beyond
      2023–2025 exist; until then, the statement that the test is reported, not scored
    - the base-rate check on the direction pass marks (§5 step 8)
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

### Checklist before the first run (AMENDED 2026-10-12)

| Item | Needed by | Where |
|---|---|---|
| **§4c Conab granularity:** São Paulo resolved (state total, Amendment 34). Still open: whether surveys back to 2001 carry the Minas regional split (first, third and final surveys) in usable form | Week 0 | §4c, §5 step 7 |
| Which IBGE units Conab's regional groupings are built from; municipality list per region | Week 0 | §3 |
| INMET download route; daily minimum present for automatic stations; the 2026 archive includes Jun–Aug 2026 | Week 0; Jun–Aug 2026 by note 1 | §4, §5 step 4 |
| INMET conventional network (BDMEP daily minima): completeness per season and observed-coverage lift (done 2026-10-14); the night rule's INMET citation (rule set provisionally, Amendment 17d) | `prereg-2` | §4, §5 step 4 |
| Re-request BDMEP's 2026 conventional daily minima, and record whether the short 2026 windows filled in (Caparaó, Lavras, Juiz de Fora) | Mid-November 2026, before note 1 | §5 step 4 |
| Whether CHIRPS ingests Brazilian stations (circularity) | Week 0 | §4b |
| Build and check the CHC prelim ingestion (pentad and daily, MG/SP window) against the community asset; verify the unverified IDs: `MODIS/061/MYD13Q1`; `NASA/VIIRS/002/VNP13A1`; the live-fallback candidates VJ113A1 and HLS (HLSL30 + HLSS30); `USGS/SRTMGL1_003` and `COPERNICUS/DEM/GLO30_2024_1`. **Done:** VJ113A1 ingested and accepted (2026-10-14); `USGS/SRTMGL1_003` and `COPERNICUS/DEM/GLO30_2024_1` resolve (Week 0 report §1) | Week 0 | §4 |
| CHC daily-prelim day split: **not established.** CHC's readme (dated 2019-08-22) describes splitting each pentad into days by cold cloud duration (CCD), with residuals placed on the wettest CFS-Reanalysis day; it does not mention IMERG. Either way, dry-day counts from daily prelim are not compared with final-CHIRPS counts until the gap is measured on overlapping months | Week 0 | §4, §9 |
| Terra drift check; current `MOD13Q1` end date in Earth Engine | Week 0 | §4a |
| Whether a MapBiomas collection covering 2025 is published (sets the mask lag): **yes, Collection 11; lag S−2** (Amendment 16c, 2026-10-14) | `prereg-2` | §5 step 1 |
| Exact Conab 2027 survey dates, and whether crop 2026's final survey comes in December or January | Before the December note | §1, §6 |
| Planet monthly area quota, from the dashboard | Before any Planet task | §4d |
| ICE redistribution terms | Before any ICE data file is committed | §4 |

### Still open

1. **Conab vintage** — closed 2026-10-14; see Closed.
2. **Region weights** for the four-region total — IBGE PAM harvested area or production?
   Production weights favour the Cerrado.
3. **Does USDA FAS GAIN give regional splits** usable as a second benchmark?
4. **Irrigation share in the Cerrado** from IBGE Censo Agro, to down-weight rainfall deficit there.
   If adopted, it is a fixed multiplier, not a parameter (§5 step 6).
5. **First five names on the outreach list**, and which note goes to them first.

### Closed

- **Coffee mask** (original open question 1) — MapBiomas class 46 (SPEC_CHANGELOG, 2026-10-12),
  now from Collection 11 (Amendment 16c).
- **Planet access** — Education & Research access confirmed (§4d). The quota is in the checklist.
- **Conab vintage** (still-open item 1) — the backtest target, and the biennial term, use Conab's
  final figure for each safra in the current historical series, with its download date recorded
  (§4c, §5 step 7, Amendment 19b).

## 11. Risks

| Risk | Mitigation |
|---|---|
| Overclaiming | Condition index framing in every note; range not point; §1a |
| Biennial bearing | Coefficient on crop S−1's anomaly, so shocks reset the phase (§5 step 7); final figure used, a declared and sized leak with a third-survey sensitivity; report relative to the expectation |
| Irrigation in the Cerrado | Separate weighting; flag irrigation share from Censo Agro |
| Short fitting sample | MODIS era, ~25 seasons (§4a); four pooled ridge weights, frost fixed (§5 step 6); leave-one-season-out by note date |
| ERA5-Land misses valley frost | INMET stations only; ERA5-Land has no frost role (§4b) |
| MODIS blurs smallholder terrain | Expect weakest skill in Zona da Mata; report regional skill separately |
| Mask errors | IBGE cross-check with a removal report (§5 step 1); one-sided, stable-membership filter, with no-filter and mapped-area-weighted sensitivities (Amendment 16d) |
| Mask representativeness | The signal comes from coffee MapBiomas detects, biased toward large sun-grown fields, worst in Zona da Mata and São Paulo (§5 step 1); stated beside regional results |
| Cloud in Nov–Mar | 16-day composites; CHIRPS and ERA5 carry the signal when optical is thin |
| Flowering is sub-pixel and brief | Use flowering-window rainfall and temperature as the proxy, not NDVI |
| Conab revisions | Use a stated vintage; record it |
| Time | §8 scope note; the backtest is the last thing to cut |

**Two limits stated in every note:** the index tracks conditions, not yield; and the private trade
houses have field crop tours and farm data that this project does not.
