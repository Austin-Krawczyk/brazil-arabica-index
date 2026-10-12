# Project spec: Brazil arabica growing-conditions index

Read this file at the start of every session. It is the source of truth for scope.
If a task would take the work outside this spec, stop and ask.

## 1. The question

Each month: **are growing conditions in each arabica region better, worse or in line with the
baseline, and what does that imply for the 2027 crop relative to Conab and the private estimates?**
(StoneX 75.3M bags, Sucafina 75.4M, Marex 75.9M for 2026/27.)

**Design principle, fixed: this is a condition index, not a yield forecast.** Every note says so.
If someone asks for a number of bags, the answer is a range relative to Conab, never a point.

**The project exists to open conversations** with softs analysts and desks. A working model with a
checkable track record is the credential. **Explicitly not a goal:** beating Conab or the trade
houses on the point estimate.

### 1a What the credential actually is, before mid-2027

A live record on the 2027 crop does not exist until Conab's final 2027 survey. **Until then the
backtest *is* the product.** That raises the stakes on §6 step 8 considerably: a thin or flattering
backtest is worse than no backtest, because the audience can check it.

## 2. Success criteria

By **late January 2027** (revised — see SPEC_CHANGELOG, the original "late November" was
inconsistent with shipping notes in December and January):

1. Public GitHub repo with a reproducible Earth Engine + Python pipeline, rerunnable in an afternoon.
2. A backtest table against Conab final arabica production, **by note date** (§6 step 8), with the
   2021 frost year and the 2024 drought year called correctly in direction.
3. Three monthly notes published (November, December, January), each with one chart and one view.
4. Sent to at least 20 named people in softs, with replies logged.

## 3. Scope

Arabica only, Brazil only, four regions. Robusta (Espírito Santo, Rondônia) is out: different crop
calendar, different exchange, and it would double the mask work for a market not being pitched.

| Region | State | Why it matters | Dominant risk |
|---|---|---|---|
| Sul de Minas | MG | Largest arabica area; rain-fed, hilly | Drought at flowering, frost |
| Cerrado Mineiro | MG | Flat, mechanised, partly irrigated; highest yields | Drought (irrigation masks it), heat |
| Zona da Mata / Matas de Minas | MG | Steep smallholder terrain, lower yields | Rain at harvest, disease |
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

**Consequence for note 1:** it carries a **backward-looking Jun–Aug 2026 frost assessment as settled
fact**, not a forward risk. This is an advantage, not merely a correction — the frost question for
the crop being tracked is already answerable.

## 4. Data sources

Every ID below was verified to resolve in Earth Engine on 2026-10-12 (see SPEC_CHANGELOG).
**Do not substitute an ID. If one is dead, stop and report it.**

| Layer | Source | Resolution / cadence | Use |
|---|---|---|---|
| **Baseline vegetation — PRIMARY** | `MODIS/061/MOD13Q1` | 250 m, 16-day, 2000– | NDVI/EVI anomalies; the backtest baseline (§4a) |
| Rainfall | `UCSB-CHG/CHIRPS/DAILY` | 5 km, daily | Flowering deficit, bean-fill cumulative, harvest rain |
| Frost — spatial gap-fill only | `ECMWF/ERA5_LAND/HOURLY` | 9 km, hourly | **Not primary** (§4b); heat days above 34 °C |
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
The MODIS era gives roughly **25 seasons**, puts 2014 and the 2000s in the sample, and stops 2021
and 2024 from *defining* a nine-year baseline that they distort.

**Caveat to carry in every note and the README: MODIS at 250 m blurs smallholder terrain, so expect
Zona da Mata skill to be the weakest of the four regions.** Report regional skill separately so this
is visible rather than averaged away.

### 4b Frost: INMET primary, ERA5-Land as gap-filler (AMENDED 2026-10-12)

**The original spec had ERA5-Land as the primary frost input. That is flipped.**

Direct evidence from the completed almond-frost study: over 2,532 matched frost station-nights,
**ERA5-Land was the worst of five products at predicting station minima** — median absolute error
1.41 °C, the largest of all, with the widest central 90% of its error distribution — and that was
over *flat valley floor with 63 calibration stations*. Brazil's arabica is hilly.

- **Frost is anchored on INMET station minima.**
- **ERA5-Land is a spatial gap-filler only**, between and around stations.
- Frost is reported as a **regional flag and probability**, never as a precise area.
- **The 2 °C threshold is not assumed.** Calibrate it against the 2021 event and against INMET
  observations before using it; report the sensitivity at 0 °C and 2 °C.

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
2. **Vegetation anomalies.** Per 16-day window, area-weighted median NDVI and NDMI over the mask,
   cloud-masked. Express as a z-score against the same window across the baseline years.
3. **Rainfall windows.** CHIRPS totals for flowering (Sep 1–Nov 30), bean fill (Dec 1–Mar 31) and
   harvest (May 1–Aug 31). **Flowering deficit is the single most predictive input;** weight it
   accordingly.
4. **Frost events.** Per §4b: INMET station minima primary, ERA5-Land gap-filling. Count nights
   below the calibrated threshold in the Jun–Aug window, and the share of masked area affected on
   the worst night. **Assign each frost window to the crop it actually affects (§3a).** Any night
   below 0 °C triggers an out-of-cycle note.
5. **Heat and dry-season stress.** Days above 34 °C and consecutive dry days during flowering.
6. **Condition index.** Weighted sum of standardised inputs, weights fitted by regressing Conab's
   regional yield anomaly on the inputs. **Do not fit anything with more than four parameters.**
   Use ridge or fixed agronomic weights.
7. **Biennial adjustment.** Arabica alternates on and off years. Detrend with a two-year cycle term
   before fitting, and report the index **relative to the expected on/off year**, or every off-year
   reads as a crop failure.
8. **Backtest by note date (AMENDED 2026-10-12).** Leave-one-year-out, **using only inputs available
   as of each note date.** For each season × each of November, December and January, fit on the
   other seasons and predict direction and rough size. **Report hit rate and mean absolute error
   separately for the November, December and January vintages.**
   **Expect November to be the weakest, and publish that number anyway** — it is the only skill
   figure a desk will take seriously, and a full-season backtest would flatter the model by scoring
   it with information it will not have in production. Call out 2021 and 2024 explicitly.
9. **Output.** Index per region and a Brazil-weighted total, every 16 days; frost and flowering-
   deficit flags daily.

**Leave out until v2:** machine-learning yield models, Planet imagery, Sentinel-2 imagery,
field-level analysis, any translation of the index into a price forecast.

## 6. Outputs

1. **Monthly crop note** (one page, PDF and LinkedIn), first week of each month from November 2026.
   Fixed layout so readers learn where to look: headline with the Brazil-weighted index and its
   direction; chart of index by region against the baseline band; region table (index, flowering
   rain vs normal, frost nights, one-line comment); benchmark line against Conab and
   StoneX/Sucafina/Marex; market context (Coffee C front month, Jul/Dec spread, ICE certified
   stocks, managed-money net from COT); **the view** — one paragraph, one stated lean, and what
   would change it; method and caveats in three lines, always including **"condition index, not a
   yield forecast"** and the Zona da Mata resolution caveat.
2. **GitHub repo.** Public, MIT licence, README that lets someone rerun it in an afternoon. GEE
   scripts, the notebook that builds index and backtest, the frozen mask, the backtest table, every
   note as PDF plus its chart data as CSV.
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

Then: **W1** frozen mask and first regional NDVI series (check: mask area within 30% of IBGE per
municipality, with the removal report). **W2** anomalies and rainfall windows for every MODIS-era
season (check: 2021 and 2024 show as the worst years). **W3–W4** backtest by note date (check:
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
- **Every checkpoint report carries its denominator** — how many municipalities, seasons,
  station-nights were examined, not only how many passed.
- Never modify anything in `data/raw/`.
- Secrets stay in `.env` (gitignored). Never print or commit a key.
- Log every spec deviation in `SPEC_CHANGELOG.md` with the reason, at the time it happens.
- **Report negative and inconclusive results as findings.** Do not retune to rescue a result. Say
  "inconclusive" or "not established" when that is the answer, and give the reason.
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
| ERA5-Land misses valley frost | INMET primary, ERA5-Land gap-fill only (§4b) |
| MODIS blurs smallholder terrain | Expect weakest skill in Zona da Mata; report regional skill separately |
| Mask errors | IBGE cross-check with a removal report (§5 step 1) |
| Cloud in Nov–Mar | 16-day composites; CHIRPS and ERA5 carry the signal when optical is thin |
| Flowering is sub-pixel and brief | Use flowering-window rainfall and temperature as the proxy, not NDVI |
| Conab revisions | Use a stated vintage; record it |
| Time | §8 scope note; the backtest is the last thing to cut |

**Two limits stated in every note:** the index tracks conditions, not yield; and the private trade
houses have field crop tours and farm data that this project does not.
