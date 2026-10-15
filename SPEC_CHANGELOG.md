# Spec changelog

Every change to scope, dated, with the reason. Newest at the bottom.

- 2026-10-12 — **Project opened.** Spec drafted by the project owner, reviewed before any code was
  written, and amended on four points below before being adopted as `CLAUDE.md`.

- 2026-10-12 — **Pre-flight verification of every dataset ID, before adoption.** All resolve in
  Earth Engine: `COPERNICUS/S2_SR_HARMONIZED`, `MODIS/061/MOD13Q1`, `UCSB-CHG/CHIRPS/DAILY`,
  `ECMWF/ERA5_LAND/HOURLY`, `NOAA/GFS0P25`, `NASA/SMAP/SPL4SMGP/007`. **Specify `MODIS/061/MOD13Q1`
  explicitly** — `MODIS/006/MOD13Q1` still resolves but is the decommissioned version, and the spec
  named only "MOD13Q1".

- 2026-10-12 — **Original open question 1 is closed, better than assumed.** MapBiomas Collection 10
  exists as a public Earth Engine asset,
  `projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v1`,
  with **40 annual bands, `classification_1985` through `classification_2024`**, and **class 46 =
  Coffee**, measured at 6.55% of a Sul de Minas test box. No fallback to a generic cropland mask is
  needed, and the mask covers the full MODIS-era backtest period.

- 2026-10-12 — **AMENDMENT 1: the crop calendar was wrong, and the frost window belonged to the
  wrong crop.** The draft tracked the 2027 crop "through the frost window (June–August 2027)".
  Brazilian winter frost damages the trees and the loss appears in the next harvest after the
  following flowering — which is why the July 2021 frost hit the 2022 crop. **The 2027 crop was set
  by Sep–Nov 2026 flowering on trees that lived through Jun–Aug 2026 frost, so that is the frost
  exposure that matters for 2027, and it has already happened.** Jun–Aug 2027 frost is a **2028**
  signal and stays in the plan labelled as such. **Note 1 therefore carries a backward-looking
  Jun–Aug 2026 frost assessment as settled fact**, which is an advantage rather than only a
  correction. Approved by owner.

- 2026-10-12 — **AMENDMENT 1b, arising from it: frost flips to INMET primary, ERA5-Land gap-fill
  only.** The draft had ERA5-Land as the primary frost input. Evidence from the completed
  almond-frost study: over 2,532 matched frost station-nights, **ERA5-Land was the worst of five
  products at predicting station minima — median absolute error 1.41 °C, the largest, with the
  widest central 90% of its error distribution** — and that was over flat valley floor with 63
  calibration stations. Brazil's arabica is hilly. Frost is now anchored on **INMET station minima**,
  with ERA5-Land only filling space between stations, reported as a regional flag and probability.
  **The 2 °C threshold is no longer assumed:** it is calibrated against the 2021 event and INMET
  observations, with sensitivity reported at 0 °C and 2 °C. Approved by owner.

- 2026-10-12 — **AMENDMENT 2: the baseline moves to the MODIS era, 2000–2025; Sentinel-2 is demoted
  to a current-season detail layer.** Nine Sentinel-2 seasons against four parameters plus a
  biennial term is roughly two observations per parameter and about 4.5 biennial cycles. Only
  Sentinel-2 is limited to 2017+; MapBiomas runs from 1985, MODIS from 2000, CHIRPS from 1981,
  ERA5-Land from 1950, and Conab coffee from 2001. The MODIS era gives roughly **25 seasons**, brings
  2014 and the 2000s into the sample, and stops 2021 and 2024 from *defining* a nine-year baseline
  they distort. **Caveat written into the spec and every note: MODIS at 250 m blurs smallholder
  terrain, so Zona da Mata skill is expected to be the weakest of the four regions, and regional
  skill is reported separately so this is visible.** Approved by owner.

- 2026-10-12 — **AMENDMENT 3: the backtest is run by note date, not on the full season.** The draft
  fitted weights on full-season inputs while the notes publish in November, December and January —
  so a leave-one-year-out backtest would have measured a model that cannot be run in November, and
  would have flattered it. Each season is now predicted using **only inputs available as of each
  note date**, with **hit rate and mean absolute error reported separately for the November,
  December and January vintages**. **November is expected to be the weakest and is published anyway**
  — it is the only skill number a desk will take seriously. This is the same error class as the
  matched-subset problem in the almond study: scoring with information production will not have.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 4: Conab granularity is a blocking Week 0 task with a concrete fallback,
  and Mogiana is not cut pre-emptively.** Step 6 regresses on Conab's *regional* yield anomaly, and
  the regression target may not exist at the unit of analysis. Evidence found: the Minas regional
  split does appear in Conab bulletins — the 2020 first survey quotes Sul de Minas 17.03–17.79M bags,
  Cerrado Mineiro 5.82–6.07M, Zona da Mata Mineira 7.21–7.53M — but **Mogiana is not known to be a
  Conab reporting unit.** Resolution order: check a recent bulletin for a São Paulo regional split;
  if none, **use São Paulo state total as the Mogiana target**, since São Paulo arabica is dominated
  by Mogiana; cut to three regions **only** if that proves too noisy in the backtest. **Mogiana is
  the frost region and losing it weakens the component with the most distinctive story.** Also noted:
  Conab has monitored coffee only since **2001**, which bounds the backtest and happens to align with
  the MODIS era; and the bulletins are PDFs, so building a ~25-season regional target series is
  extraction work that must be budgeted and vintage-stamped. Approved by owner.

- 2026-10-12 — **INMET access verified as far as this environment allows, and the limit recorded.**
  INMET publishes annual automatic-station archives covering **2000 through 2026** at
  `portal.inmet.gov.br/dadoshistoricos`. **The host is not reachable from the project sandbox** —
  curl returns 000 for `apitempo.inmet.gov.br`, `portal.inmet.gov.br` and `bdmep.inmet.gov.br` while
  a control host returns 200 — so INMET is a **manual download**, following the same pattern as the
  DWR geodatabases and CIMIS in the earlier studies. Still to confirm on first download: that daily
  minimum temperature is present for automatic stations. Recorded rather than assumed because frost
  is now anchored on this source (Amendment 1b).

- 2026-10-12 — **Circularity check added before the frost validation runs.** CHIRPS blends satellite
  estimates with station data. If Brazilian stations feed CHIRPS, validating CHIRPS against INMET is
  circular — the same trap as PRISM ingesting CIMIS in the almond study, which reframed that study's
  headline result once discovered. §4b requires this to be established **before** the validation,
  not after.

- 2026-10-12 — **Success criteria date corrected.** The draft said "done means, by late November
  2026" while listing three notes for November, December and January. Revised to **late January
  2027**. Also recorded in §1a: a live record on the 2027 crop does not exist until Conab's final
  2027 survey, so **until mid-2027 the backtest is the product** — which is why §8 names the
  backtest as the last thing to cut.

- 2026-10-12 — **§9 rules carried over from the two completed studies**, each earned by an error that
  nearly shipped: verify IDs, units, scale factors and flags against provider documentation; every
  filter reports what it removed and whether it differs from what was kept; never compare on
  non-identical observations; verify any zero by an independent method; never score a model with
  information it will not have in production; every checkpoint carries its denominator.

- 2026-10-12 — **AMENDMENT 5: Sentinel-2 is removed from v1 entirely, out of the index and out of
  the note.** Amendment 2 demoted it to a current-season detail layer, but it feeds neither the
  index nor the backtest. Showing a 10 m current-season layer beside a 250 m MODIS index invites
  comparing two products on different observations, which §9 forbids. `COPERNICUS/S2_SR_HARMONIZED`
  is dropped from the §4 data table and added to "Leave out until v2". Decisions 1, 3 and 4 of the
  review were reconfirmed unchanged. Approved by owner.

- 2026-10-12 — **AMENDMENT 6: repo name set, `brazil-arabica-index`.** Named in §2 criterion 1 and
  §6 output 2. README title changed from "Brazil Arabica Crop Monitor" to "Brazil Arabica Condition
  Index" so the name carries the "condition index, not a yield forecast" framing. No GitHub remote
  exists yet, and the local folder keeps its name. Approved by owner.

- 2026-10-12 — **AMENDMENT 7: the benchmark was for the wrong crop and included robusta.** The
  draft benchmarked the 2027 crop against StoneX 75.3M, Sucafina 75.4M and Marex 75.9M "for
  2026/27". In trade convention 2026/27 is the 2026 harvest, and figures near 75M bags are total
  Brazil including conilon; Brazil's arabica alone has never been near that. The 2027 crop
  (2027/28) is now benchmarked against the arabica component of the private 2027/28 estimates,
  once published, from houses that publish an arabica figure. Until then notes state the comparison
  as "versus trend and an expected off-year". The original figures stay in §1, labelled as
  reference only. Approved by owner.

- 2026-10-12 — **AMENDMENT 8: no Conab estimate for the 2027 crop exists until late January
  2027.** Conab's first survey of a crop comes in January and its final survey in December or the
  following January. The spec framed every note as "relative to Conab", but no Conab 2027 figure
  exists before the first survey. Any note published before that survey now says so explicitly,
  and the §1 "range relative to Conab" rule applies only once a Conab 2027 estimate exists; before
  that, the range is relative to trend and the expected off-year. §1a's heading said "before
  mid-2027" while its text said "until Conab's final 2027 survey"; the heading now matches the text.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 9: CHIRPS-prelim for the current season, final CHIRPS for the
  backtest.** Final CHIRPS lands about three weeks after month-end, so a first-week-of-November
  note would have final rainfall only through September, one-third of the flowering window.
  Current-season months not yet final now use CHIRPS-prelim
  (`projects/climate-engine-pro/assets/ce-chirps-prelim-pentad`, community catalog, pentad,
  2015–), added to §4 as unverified until checked. The baseline and backtest stay on final CHIRPS
  so every season is scored on one product. Because that scores the backtest on better data than
  production will have, a sensitivity rerun with prelim substitution, for note dates inside the
  prelim archive, is reported beside the headline. Final for month M counts as published from the
  1st of M+2. Every note discloses which months used prelim. **Fallback declared now**, because the
  community asset is a single-maintainer dependency: if it does not resolve, is not current, or
  lags the provider by more than two pentads, use CHC's own prelim files from chc.ucsb.edu,
  ingested as a private GEE asset; both sources are verified in Week 0 before choosing. Under the
  community asset, consecutive dry days for prelim months are not available; under the CHC
  fallback they are computed from its daily files. Recorded in §9 as a decision made before the
  first run. Approved by owner.

- 2026-10-12 — **AMENDMENT 10: harvest-window rain removed from the index.** Rain in May–Aug of
  year S falls after every note about crop S (November S−1 to early February S), so it can never
  be an input at any note date. Removed from §5 step 3 and the §4 CHIRPS row. §5 step 3 now states
  that only May–Aug of S is removed: May–Aug of S−1, the dry season before flowering, falls before
  every note and remains the window of the dry-season soil-moisture input. The §3 table now marks
  Zona da Mata's two dominant risks, harvest rain and disease, as outside the index; together with
  the MODIS resolution caveat, that is why Zona da Mata skill is expected to be weakest. Approved by
  owner.

- 2026-10-12 — **AMENDMENT 11: Terra continuity check, trigger and VIIRS fallback.** `MOD13Q1` is
  the primary vegetation layer, but Terra stopped orbit maintenance in 2022, its overpass is
  drifting from about 10:30 toward 8:30, and NASA's 2023 status put end of science at February
  2027. The current season, which every note reports, is the most affected. Week 0 now compares
  Terra anomalies with Aqua (`MYD13Q1`) and VIIRS (`VNP13A1`) over the mask for 2018–2026; two
  references are used because Aqua is also drifting, so a Terra–Aqua gap alone cannot be
  attributed. A trigger is fixed before the check runs: (a) `MOD13Q1` not current at a note date
  (no composite ending within 32 days), or (b) Terra diverging from both references by more than
  0.5 baseline SD, averaged over 2024–2026, in the coffee-area-weighted Brazil total or in two or
  more regions. Trigger (b) is not "any region", so noise in one region (most likely Zona da Mata)
  cannot switch the product for all four; per-region differences are reported either way. The
  declared fallback is `NASA/VIIRS/002/VNP13A1` (500 m, 2012–). Under it, the current-season
  anomaly uses VNP13A1's own 2012–2025 baseline, the headline backtest stays on MODIS, and a
  VNP13A1 rerun for crops 2013–2026 is reported beside it. Mid-season rule: (b) is evaluated once
  in Week 0 and binds for the season; (a) is evaluated at each note date and, if it fires, applies
  to that note and every later note for the crop, with no reissue of prior notes and no mixing of
  products within a reading. Both new IDs are unverified until a client is available. Approved by
  owner.

- 2026-10-12 — **AMENDMENT 12: surprise test added to the backtest.** Getting the direction right
  against the baseline is something a desk can already read from Conab. The question a desk asks is
  whether the index saw the surprise coming. Each vintage is now also scored on the direction of
  Conab's first-to-final revision: predicted direction is the sign of the index-implied yield
  anomaly minus Conab's first-survey anomaly, and actual direction is the sign of final minus
  first. The index-to-yield mapping is the same leave-one-year-out fit the direction backtest uses,
  so no season's index value was fit on its own Conab final. Revisions under 1% count as flat, are
  left out of the hit rate and are reported. The base rate of upward revisions is reported, and
  skill is measured against an always-majority model, not 50%, so an always-up model does not
  score as skill. The pass mark is computed from the base rate at p<0.05 and fixed before the first
  backtest run. The Brazil arabica total is the headline; regions are reported separately.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 13: the frost component is fixed from agronomy, not fitted.** The
  backtest window holds one major frost (July 2021, crop 2022): a fitted weight would be set by
  one season, and leave-one-year-out on that season removes the only evidence for it. Frost now
  enters as a fixed yield penalty for each tier in each flagged region, from cited agronomic
  sources, pre-registered before the first backtest run and marked provisional where no clean
  source exists. Each tier's penalty is scaled by the coffee-area share under stations meeting that
  tier, so a region at the 25% flag floor is not penalised like one at 90%; tiers are exclusive so
  severe-frost area is not penalised twice. In the regression it is a fixed offset, so the fitted
  weights are estimated on the remainder. The crop 2022 call is declared in-sample wherever it
  appears, because the constants are set with knowledge of the 2021 outcome. Because frost damage
  also shows up in the vegetation anomaly, frost-flagged seasons are reported with and without the
  frost component. Carryover into the following crop is not modelled in v1; crop 2023 joins the
  with-and-without report, and the backtest table states it may carry unmodelled 2021 frost
  effects. Approved by owner.

- 2026-10-12 — **AMENDMENT 14: one season convention, and crop-year labels throughout.** After
  Amendment 1 moved the frost window, the spec still mixed weather years and crop years ("the 2021
  frost year", "the 2024 drought year", "2021 and 2024 show as the worst years"). Season S is now
  defined once in §3a as the crop harvested in year S (Conab safra S, trade S/S+1), with frost
  Jun–Aug S−1, flowering Sep–Nov S−1, bean fill Dec S−1–Mar S and harvest May–Sep S. Every year
  label is a crop year unless it names a weather event. Success criterion 2, §5 step 8 and the W2
  check now name crops 2022 (July 2021 frost) and 2025 (2024 drought). Criterion 2 now requires
  both to be reported explicitly, whichever way they come out, rather than called correctly: 2022
  is in-sample (Amendment 13), and a required result invites retuning. §5 step 3's harvest window
  is aligned to May–Sep. **Cross-reference fix:** §1a and criterion 2 pointed to "§6 step 8" for
  the backtest; both now point to §5 step 8. Approved by owner.

- 2026-10-12 — **AMENDMENT 15: the W2 check reports ranks, and tunable choices are pre-registered.**
  The W2 check "crops 2022 and 2025 show as the worst" was a check on the result. It invited
  adjusting inputs until it passed, which §9 forbids. W2 now reports each season's rank on every
  input; if 2022 and 2025 are not the worst, that is a finding. Every tunable choice is recorded
  in `docs/preregistration.md` and committed in two tagged steps. `prereg-1` comes before W2
  computes any season-level input, because the outcome years are already known and an open
  feature list could be shaped by them. It covers features, windows, standardisation, weighting
  method, the terms counted toward the cap, direction pass marks and frost constant values.
  `prereg-2` comes before the first backtest run and covers values that need data but not
  results: the mask, the station set and altitude cut, the surprise-test pass mark, and the
  sources for the frost constants (or "provisional, no clean source"), since the citation search
  may not finish by W2. If a source found after `prereg-1` supports a different value, the
  registered value stands and the backtest is also reported with the source's value; §5 step 6
  now says values are registered first and sourced second. Every change after `prereg-1` is
  logged and listed in the backtest report. Approved by owner.

- 2026-10-12 — **AMENDMENT 16: mask year follows the publication lag, and the bearing-area bias is
  reported.** A single 2024 mask applied to every season uses future information. It keeps only
  land still in coffee in 2024, which drops farms abandoned after the 2014 drought or the 2021
  frost and adds 2024 coffee that was pasture earlier, so past damage looks smaller. Each backtest
  season now uses Collection 10's classification for the crop year minus a fixed lag equal to the
  live lag for crop 2027: S−2 if a collection covering 2025 is published and verified before note
  1, otherwise S−3. The lag is recorded at `prereg-2`. The owner's original wording, "the latest
  MapBiomas year published before each note date", was not used literally: older collections
  differ in method and some lack class 46, so every season stays on Collection 10. The 30% filter
  runs per season against PAM for the mask year. IBGE PAM excludes non-bearing young plantings,
  and very likely post-frost pruned area, while MapBiomas includes them. The filter is therefore
  biased toward removing expanding Cerrado areas and recovering frost-hit municipalities. The
  removal report splits removed and kept municipalities by three-year MapBiomas area change.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 16b: persistent-pixel comparison for the 30% filter.** To reduce the
  bearing-area bias rather than only report it, the filter now compares PAM with MapBiomas pixels
  classified as coffee in the mask year and each of the two years before it, since arabica does not
  bear until roughly its third year. This addresses young plantings but not post-frost pruning, so
  the removal-report split still applies. The index stays on the full class-46 mask in v1; the
  backtest is also reported on the persistent-pixel mask as a sensitivity beside the headline.
  Both masks are registered at `prereg-2`. Approved by owner.

- 2026-10-12 — **AMENDMENT 17: frost from INMET stations only, with agronomic thresholds and an
  area-weighted regional flag.** The automatic station network grew through the 2000s, so a frost
  feature over a changing station set would compare seasons on different observations (§9).
  Stations are now restricted to those with complete Jun–Aug records from 2008 (at least 95% of
  hourly observations in every window, no gap over 48 consecutive hours), within 25 km of the
  mask, weighted by coffee area within that radius, with overlapping circles counted once.
  Stations above the 95th percentile of coffee-mask elevation per region are excluded, using
  `USGS/SRTMGL1_003` (fallback `COPERNICUS/DEM/GLO30`). Thresholds are agronomic, not fitted:
  leaf damage at −2 to −3 °C and a 3–4 °C screen-to-leaf offset put first damage at a screen
  reading of 0–2 °C, so 2 °C is the sensitive tier and 0 °C the severe tier, both reported, with
  values registered at `prereg-1` and sources at `prereg-2`. A station meets the 2 °C tier with
  three or more nights ≤ 2 °C, and the severe tier with one night ≤ 0 °C. A region is flagged
  when stations meeting a tier cover 25% of its coffee area. That replaces "any night below 0 °C",
  which would fire every winter at high-altitude stations. If qualifying stations cannot reach 25%
  coverage in a region, that region cannot be frost-flagged and every note says so; the maximum
  attainable coverage per region and the station list with counts are registered at `prereg-2`,
  so an unreachable flag is known before the first run. §4b now says calibration applies to
  gridded products matched to stations, not to station observations, so the two sections no
  longer conflict. ERA5-Land has no frost role. The frost series starts with crop 2009 and is not
  filled; the index is scored with and without frost, each version against its own pass mark,
  compared only on shared seasons. Approved by owner.

- 2026-10-12 — **AMENDMENT 17b: missing station nights are never counted as non-frost.** The
  completeness rule allows gaps of up to 48 hours, so a station can miss a frost night. Without a
  rule the count would treat it as a non-frost night, understating frost and breaking §9's rule
  that a zero is verified. A night is observed only if every hour 18:00–09:00 local is present.
  Where missing nights could change a station's tier for a season, that tier is reported as
  unresolved and the regional coverage share is reported with and without the station. Approved
  by owner.

- 2026-10-12 — **AMENDMENT 18: vegetation inputs are NDVI and EVI; soil moisture is ERA5-Land
  root zone over an explicit dry-season window.** §4 listed NDVI/EVI while §5 listed NDVI/NDMI.
  `MOD13Q1` has no 1.6 µm band, so the standard NDMI cannot be computed from the primary product;
  the vegetation inputs are NDVI and EVI. SMAP L4 (`NASA/SMAP/SPL4SMGP/007`) starts in 2015 and
  cannot support a 2001–2025 backtest, so soil moisture is ERA5-Land only. It now uses layers 1–3
  (0–100 cm), depth-weighted, rather than layer 1 (0–7 cm), which tracks recent rain rather than
  root-zone drought: arabica's feeder roots sit mostly in the top 60 cm with a taproot below, and
  layer 4 moves too slowly within one dry season. The pre-flowering dry season, May–Aug of S−1,
  is now an explicit window in §3a and the soil-moisture input in §5 step 5, which makes §5 step
  3's statement about that window true. Approved by owner.

- 2026-10-12 — **AMENDMENT 19: parameter budget, biennial term, comparison models and pass
  marks.** The cap of four now counts the stage-2 condition weights only, pooled across regions:
  EVI anomaly, flowering rain deficit, dry-season root-zone soil moisture and heat days in
  flowering. Stage 1 (intercept, trend and biennial coefficient per region) does not count. EVI
  is the single vegetation term because NDVI saturates in dense coffee canopies; NDVI, dry days
  and bean-fill rain are reported, not fitted. Frost is a fixed offset, and any Cerrado irrigation
  adjustment would be a fixed multiplier. The biennial term is a coefficient on crop S−1's yield
  anomaly, taken from Conab's third survey of S−1 (published before every note), so a shock such
  as the July 2021 frost resets the phase instead of breaking a fixed alternation. A season is
  held out in all regions at once, and the z-scores, trend, biennial coefficient, ridge penalty
  and weights are all refitted without it. Two targets are scored: condition direction, with
  pass marks 18 of 25 (no frost, 2001–2025) and 13 of 17 (frost, 2009–2025), raised if the base
  rate is away from 50%; and yield versus trend, against a biennial-only model. Zero-anomaly,
  biennial-only and rain-only comparison models are reported on the same seasons. Crop 2026 is
  added as an addendum once Conab's final exists and is declared not cleanly out of sample.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 20: score on yield, and regions follow Conab's units.** Success
  criterion 2 said production while §5 regressed on yield; the index tracks conditions, which
  act on yield, and production also moves with area (for example, area pruned after a frost), so
  scoring is on yield. Region boundaries now follow Conab's groupings: Sul e Centro-Oeste de
  Minas; Triângulo, Alto Paranaíba e Noroeste; Zona da Mata, Rio Doce e Central; and São Paulo
  (or its Mogiana split, if Conab publishes one). They do not follow origin designations, because
  the scoring target is defined on Conab's units. The municipality list per region and the IBGE
  unit system Conab uses are confirmed in Week 0. Because Conab's Norte, Jequitinhonha e Mucuri
  unit and arabica outside MG and SP fall outside the index, "Brazil-weighted total" is renamed
  "four-region total" throughout, and every note states the four units' share of Brazil arabica.
  Approved by owner.

- 2026-10-12 — **AMENDMENT 21: cuts — the GFS frost flag moves to June 2027, and ICE data stays
  out of the repo until its terms are checked.** Frost is not a risk in November–January, so a
  forward frost flag adds nothing to the notes on the 2027 crop; `NOAA/GFS0P25` stays in §4 but is
  not used before June 2027, when it serves the Jun–Aug 2027 window, the first 2028 signal. ICE
  settlement, spread and certified-stocks data may carry redistribution restrictions, so they are
  referenced in note text only and kept out of committed data files until ICE's terms are checked;
  CFTC COT is a public-domain US government work (Data.gov lists the COT dataset as a "U.S.
  Government Work": https://catalog.data.gov/dataset/commitment-of-traders-cot) and sits outside
  the ICE check. (The other cuts
  from the review, Sentinel-2 and harvest-window rain, are Amendments 5 and 10.) Revised after
  review the same day to state CFTC COT's public-domain status explicitly. Approved by owner.

- 2026-10-12 — **AMENDMENT 22: timeline — note 1 is the frost review, note 3 follows Conab's first
  survey, and the success date moves to the first week of February 2027.** Six part-time weeks
  from 12 October reach about 23 November, so a first-week-of-November index note was not
  achievable. Note 1 is now the Jun–Aug 2026 frost review, published in late November; it needs the
  station set and frost constants but not the backtest, and carries no index reading. The
  November-vintage reading is computed as of the November note date and published in the repo no
  later than note 1, so it can be cited later as made before Conab's survey. The first index note
  is the first week of December. The note after Conab's first 2027 survey publishes within five
  business days of it and is the first scorecard: the November and December readings beside
  Conab's first number, with the surprise-test revision call stated explicitly. If Conab has not
  published by 31 January, that note goes out on the first business day of February without the
  Conab line, and a scorecard addendum follows the survey. The §6 rule becomes "first week of each
  month, except the note that follows Conab's first survey of the crop". A success date of "late
  January" could be missed by design under that rule, so §2 now reads the first week of February
  2027, and criterion 3 names the three notes. Approved by owner.

- 2026-10-12 — **AMENDMENT 23: Planet as three bounded v1.5 tasks, never an index input.** The
  owner has Planet Education & Research access, which closes original open item 6. Planet stays
  out of the index and the backtest. Three bounded v1.5 tasks, in order: mask validation of the
  municipalities failing the 30% filter; a one-time 2021 frost case study over Mogiana and Sul de
  Minas; and one illustrative 3 m figure per public note, labelled as not an input. The Education &
  Research terms are non-commercial, so Planet-derived material appears only in the repo and
  public posts, never in the note emailed to desks; no raw scenes are committed, and the README
  states the source and programme. The product is PlanetScope surface reflectance harmonised to
  Sentinel-2. The monthly area quota is to be read from the dashboard and recorded. Planet is
  removed from "Leave out until v2" except as an index input. Start rule, added after review the
  same day: the tasks begin once the backtest is complete, in the order given, so they never take
  time from it; the figure per public note starts with the first note after the backtest is
  complete. Approved by owner.

- 2026-10-12 — **AMENDMENT 24: §10 becomes a checklist before the first run, plus a consistency
  sweep.** §10 now holds one table of everything to confirm, each with when it is needed: Conab
  granularity and the usability of the Minas split (first, third and final surveys); Conab's IBGE
  unit system; INMET route, daily minima and Jun–Aug 2026 availability; CHIRPS circularity; every
  unverified ID; how CHC's daily prelim is disaggregated to days (reported as IMERG-based; if
  confirmed, its dry-day counts are not comparable to final-CHIRPS counts without measuring the
  gap first); the Terra drift check and `MOD13Q1` end date; whether a 2025 MapBiomas collection
  exists; exact Conab 2027 dates; the Planet quota; and ICE terms. §8 Week 0 now points to the
  checklist instead of repeating it. Remaining open questions (Conab vintage for the scoring
  target, region weights, USDA splits, Cerrado irrigation, outreach names) are listed separately,
  and closed items are recorded. Consistency edits that follow from earlier amendments: §11's
  biennial and sample-size rows now describe Amendment 19's design; the W3–W4 check points to the
  fixed pass marks instead of "a stated majority"; W1 names the EVI series. Revised after review
  the same day: §4c Conab granularity had been listed under "Closed" while still blocking; it is
  now marked as a blocking row in the checklist and removed from "Closed". Approved by owner.

- 2026-10-12 — **AMENDMENT 25: VIIRS VNP13A1 is removed as the live vegetation fallback.** NASA's
  Earthdata record for VNP13A1 v002 states that delivery of Suomi NPP VIIRS science data products
  will cease on 2 November 2026 (https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp13a1-002),
  before note 1. VNP13A1 stays only as the second reference in the Week 0 drift check, 2018 to
  October 2026. The live fallback, in order of preference: (a) VJ113A1 (NOAA-20 VIIRS, 500 m), the
  successor NASA names, if it is in the Earth Engine catalog and current; (b) otherwise NASA HLS
  (HLSL30 + HLSS30, 30 m; Landsat from 2013, Sentinel-2 from 2015), aggregated to monthly EVI over
  the mask. Both are tested once Earth Engine is available and reported before one is chosen; HLS
  has no end-of-mission risk through 2027, so it is the safer choice on continuity even if VJ113A1
  exists. The rules that applied to VNP13A1 now apply to whichever fallback is chosen: its own
  baseline, a rerun of the vegetation component over the crops its record covers, the resolution
  caveat for Zona da Mata, and the mid-season rule. Approved by owner.

- 2026-10-12 — **AMENDMENT 26: drift-check method fixed before it runs.** The three products
  composite on different windows (Terra and Aqua are offset by 8 days; VIIRS runs on an 8-day
  cadence) and start in different years, so comparing them as specified would compare
  non-identical observations (§9). All three are now reduced to calendar-month anomalies against
  a common 2013–2025 baseline, each over its own pixels within the mask. Trigger (b)'s "baseline
  standard deviation" is now that of the same 2013–2025 monthly baseline, so the trigger and the
  check use one scale. A provisional run over all class-46 coffee pixels in MG and SP runs now,
  labelled provisional; the formal run, per region and for the four-region total, waits for the
  regional municipality lists, and trigger (b) is evaluated on the formal run only. Both go in the
  Week 0 report. The comparison window ends in October 2026 because VNP13A1 delivery ends on
  2 November (Amendment 25). Approved by owner.

- 2026-10-12 — **AMENDMENT 27: the elevation fallback moves to `COPERNICUS/DEM/GLO30_2024_1`.**
  The Earth Engine catalog marks `COPERNICUS/DEM/GLO30` as deprecated and superseded by
  `COPERNICUS/DEM/GLO30_2024_1` (an ImageCollection, band `DEM`, EGM2008 datum). The §4 table now
  names the new ID and notes that both SRTM and the Copernicus DEM are surface models that include
  canopy, which does not matter for a station altitude cut at the 95th percentile of coffee-mask
  elevation. Approved by owner.

- 2026-10-12 — **AMENDMENT 28: ERA5-Land soil-layer weights confirmed and registered.** The Earth
  Engine catalog confirms the band names `volumetric_soil_water_layer_1`, `_2` and `_3` with
  depths 0–7, 7–28 and 28–100 cm, in volume fraction. The 0–100 cm root-zone value is weighted by
  layer thickness, 0.07 / 0.21 / 0.72, and the weights are registered at `prereg-1`. The §4 row's
  "verify band names and depths" note is replaced by the confirmed values. Approved by owner.

- 2026-10-12 — **AMENDMENT 29: CHC daily-prelim day split recorded as not established.** A
  second-hand source described CHC's daily prelim as IMERG-based. CHC's own readme for the daily
  prelim (https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_daily/aaa.readme.txt, dated
  2019-08-22) describes splitting each pentad into days by cold cloud duration, with residuals
  placed on the wettest CFS-Reanalysis day, and a `fixed/` version that sums exactly to the pentad
  totals; it does not mention IMERG. Because the readme is seven years old, the method is recorded
  as not established rather than confirmed. The rule no longer depends on it: dry-day counts from
  daily prelim are not compared with final-CHIRPS counts until the gap is measured on overlapping
  months, now stated in §9 and the §10 checklist. Approved by owner.

- 2026-10-12 — **AMENDMENT 30: how HLS is evaluated as the vegetation fallback.** HLS's
  observation density changes over its record (Landsat 8 only to 2015, Sentinel-2A from late 2015,
  2B from 2017, Landsat 9 from 2021, Sentinel-2C from 2024), so a baseline across those years would
  mix data availability with signal (§9). HLS is now evaluated on HLSS30 only, with a 2017–2025
  baseline, so the sensor set is Sentinel-2 A/B throughout, with 2C treated as A's replacement in
  2024–25; the per-month observation count is reported so any step shows. HLSL30 is left out of
  the baseline and its coverage reported separately as information. Rainy-season test: if the
  share of mask pixels with at least one clear HLSS30 observation falls below 60% in more than two
  months of the November–March baseline period, HLS is recorded as unable to carry the rainy
  season, and the fallback falls to VJ113A1 or, failing that, a declared gap with no vegetation
  reading, stated in the note. Revised before the first run, the same day: the baseline starts in
  July 2017, so its first rainy season (2017/18) has both Sentinel-2 A and B; January–March 2017
  counts are still reported, as information, so the single-sensor step is visible. Approved by
  owner.

- 2026-10-13 — **AMENDMENT 25 (revised): the vegetation fallback order is HLS, then VJ113A1
  ingested privately, then a declared gap.** Week 0 found that VJ113A1 is not in Earth Engine
  (the `NASA/VIIRS/002` folder listing and three direct ID probes agree) and that
  `NASA/HLS/HLSS30/v002` resolves. The order is now: (a) HLS, if it passes the Amendment 30
  rainy-season coverage test; (b) if it fails, VJ113A1 ingested from NASA as a private Earth
  Engine asset over the MG/SP window only, built the same way as the CHC prelim ingestion; (c) a
  declared gap only if both fail. The VJ113A1 ingestion does not start unless HLS fails. The
  original entry above records the 2026-10-12 decision unchanged. Approved by owner.

- 2026-10-13 — **AMENDMENT 9 (revised): CHC's own prelim files replace the community-catalog
  asset as the single prelim product.** Week 0 found that the community asset
  (`projects/climate-engine-pro/assets/ce-chirps-prelim-pentad`) resolves and is current, but its
  archive starts on 2025-01-01, not 2015 as its catalog page says; the sensitivity rerun could
  then cover only crop 2026's vintages. CHC's own prelim archive runs from 2015, pentad and daily.
  **The declared fallback triggers did not fire** (the asset resolves, is current and does not
  lag); the switch is an owner decision made on archive length. CHC's pentad and daily prelim are
  now the single prelim product for live notes and for the sensitivity rerun, ingested as private
  Earth Engine assets over the MG/SP window, and the rerun covers vintages from 2015. Daily prelim
  restores consecutive dry days for prelim months, subject to Amendment 29's gap measurement on
  overlapping months. The community asset is no longer a source and is kept only as a weekly
  cross-check that the ingestion matches. The §4 row is corrected. The original entry above
  records the 2026-10-12 decision unchanged. Approved by owner.

- 2026-10-13 — **Temporary deviation from Amendment 9 (revised): the community-catalog asset
  supplies live-season prelim until CHC's archive is complete.** The first CHC download used four
  parallel connections, and CHC's server blocked this machine after 122 of 2,007 files (about
  05:34 PDT). The download is now sequential with a 3-second pause and stops on the first refusal;
  the retry waits 24 hours, and if CHC still refuses, the owner contacts CHC. Until CHC's archive
  is complete, live-season months not yet final use
  `projects/climate-engine-pro/assets/ce-chirps-prelim-pentad`, and every note says so. That asset
  is pentad-only, so dry-day counts for prelim months are reported as not yet available until
  CHC's daily files are in. The 2015–2024 pentads are needed only for the backtest-stage rerun, so
  note 1 is not affected. Owner decision; the deviation ends when the CHC archive is complete and
  ingested.

- 2026-10-13 — **AMENDMENT 26 (revised): trigger (b) uses the signed average.** Trigger (b) said
  "diverges ... by more than 0.5 standard deviations, averaged over 2024–2026" without saying
  signed or absolute. The provisional drift run showed that the absolute month-to-month difference
  in EVI anomaly between products was already 0.50–0.58 SD in 2018–23, before any drift concern,
  so an absolute average would fire on noise. A signed average measures systematic drift, which is
  what the trigger is for. The original entry above records the 2026-10-12 method unchanged.
  Approved by owner.

- 2026-10-13 — **AMENDMENT 31: the drift check's references are VIIRS and HLS; Aqua is no longer
  a reference.** The provisional run showed Terra and Aqua agreeing on NDVI (+0.01 SD signed,
  2024 to Sep 2026) while both diverged from VIIRS (+0.78). Aqua's orbit is drifting too, so it is
  not independent of Terra, and the original rule (Terra diverging from both references while
  they agree) could not separate a shared MODIS drift from a VIIRS-specific change. HLSS30 NDVI and
  EVI monthly anomalies from July 2017, on the HLS test's 20,000-pixel sample, become the second
  reference. Terra divergence is attributed to Terra only when VIIRS and HLS agree with each other;
  trigger (b) is read against VIIRS and HLS; Aqua is reported alongside but does not count. Open:
  HLS starts in July 2017, so it cannot share Amendment 26's 2013–2025 baseline; the baseline for
  comparisons with HLS is to be settled before the HLS test runs (§10). Approved by owner.

- 2026-10-13 — **AMENDMENT 32: lean Earth Engine runs, with each run's compute cost recorded.**
  The provisional drift check, three products at native resolution over all coffee in MG and SP
  plus a first attempt lost to a network failure, took the project past the Community tier's
  150 EECU-hours a month and into restricted mode. The owner is moving the project to the
  Contributor tier (1,000 EECU-hours a month). Regardless of tier, §9 now requires samples wherever
  a sample answers the question, no repeated full-resolution pass over the study area without a
  recorded reason, and each run's compute cost recorded in the report, measured with Earth
  Engine's request profiling. The cost of the runs before this rule was not measured. Approved by
  owner.

- 2026-10-13 — **AMENDMENT 26 (second revision): the drift check's common baseline is July
  2017–2025 for every product.** HLS became a reference in Amendment 31 and starts in July 2017,
  so it could not share the 2013–2025 baseline; giving HLS its own baseline would compare products
  on different years (§9). Every product in the drift check now uses one baseline, July 2017 to
  December 2025, and trigger (b)'s standard deviation is that baseline's. The provisional reading
  was recomputed on it from the saved monthly results, with no new Earth Engine compute: the
  conclusions do not change. NDVI: Terra and Aqua still agree (+0.08 SD signed, 2024 to Sep
  2026) and both still diverge from VIIRS (+0.88 and +0.80). EVI: no systematic divergence (signed
  −0.23 to −0.01). The §10 checklist row for this decision is closed. Approved by owner.

- 2026-10-13 — **AMENDMENT 33: trigger (b) is evaluated on EVI; NDVI results for 2024–26 carry a
  drift caveat.** Trigger (b) did not say which index it applies to. It is now evaluated on EVI,
  the index's vegetation input (Amendment 19); NDVI is reported alongside but does not trigger. The
  provisional drift check found that Terra and Aqua NDVI diverge from VIIRS from 2024 (+0.88 and
  +0.80 SD signed on the July 2017–2025 baseline), cause unresolved pending HLS, while EVI shows no
  systematic divergence. NDVI appears only in the sensitivity report, which must now state that
  the NDVI series carries a 2024–26 drift of unresolved cause and that any NDVI-based result is
  unreliable for those years. Approved by owner.

- 2026-10-13 — **AMENDMENT 31 (revised): HLS is not a drift reference; trigger (b) is evaluated
  on EVI against VIIRS alone and cannot attribute cause.** Amendment 31 made VIIRS and HLS the two
  references. HLS then failed both gates: its rainy-season coverage test (7 of 42 November–March
  baseline months below 60% clear coverage, against 2 allowed), and the cost gate for the
  500-point reference series (3,025 EECU-seconds for one month, against a limit of 540; the cost
  is per-granule overhead and barely depends on the number of points). With HLS out, trigger (b)
  could not be evaluated as written. It is now evaluated in the formal run on Terra's EVI against
  VIIRS alone, with the statement that a single reference cannot attribute cause: a divergence may
  come from Terra or from VIIRS. Aqua is still reported alongside and is still not a reference.
  Amendment 31's NDVI question stays open. Approved by owner.

- 2026-10-13 — **AMENDMENT 30 (second revision): VJ113A1 is held to the same rainy-season
  coverage test as HLS.** HLS failed Amendment 30's test (7 of 42 November–March baseline months
  below 60% clear coverage, against 2 allowed), and the fallback moved to VJ113A1. So the fallback
  is not accepted on an easier standard than the product it replaces, VJ113A1 must pass the same
  rule before it is relied on: monthly coverage is the coffee-area-weighted share of its pixels
  within the mask with a "good" pixel reliability (0–3, the range used in the drift check) in at
  least one composite starting in the month, and no more than two of the 40 November–March months
  in its 2018–2025 baseline may fall below 60%. If it fails, the fallback moves to a declared gap.
  The check is probe-gated: one month first, at most 0.25 EECU-hours, keeping the 40 months under
  about 10 EECU-hours. Ingestion is by NASA AppEEARS (route B), with whole-file download from LP
  DAAC as the backup if AppEEARS's queue exceeds three days; nothing is submitted until the
  owner's AppEEARS token is in `.env`. Approved by owner.

- 2026-10-14 — **AMENDMENT 8 (revised): Conab's first survey has fallen as late as 5 February.**
  Amendment 8 said a crop's first survey comes "between the 18th and 28th [of January] in recent
  years". Conab's coffee page lists the 1st survey of safra 2026 on **5 February 2026** and the
  4th survey of safra 2025 on 4 December 2025, so §1 now reads "between late January and 5
  February", with the known dates: first surveys on 21 January 2021, 18 January 2022, 28 January
  2025 and 5 February 2026; final surveys on 15 December 2022, 21 January 2025 (2024 crop) and
  4 December 2025 (2025 crop). The 2021, 2022 and 2025 dates come from press reports of Conab's
  calendars; the 2026 and December 2025 dates from Conab's own page. **Amendment 22 already handles
  a February survey:** if Conab has not published by 31 January, note 3 goes out on the first
  business day of February without the Conab line, and a scorecard addendum follows the survey, so
  the first-week-of-February success date still holds. The original entry above records the
  2026-10-12 wording unchanged. Approved by owner.

- 2026-10-14 — **AMENDMENT 34: São Paulo state total is the Mogiana target, and the regional
  membership is registered as provisional.** Conab's 3rd survey of safra 2026 (bulletin and data
  table, stored with checksums in `data/raw/conab/`) reports São Paulo only as a state total, so
  under §4c's resolution order the state total is the Mogiana target; cutting to three regions
  stays available only if the backtest shows it too noisy. The bulletin describes the Minas
  regions by IBGE 1989 mesoregions without publishing a membership list. The proposed membership
  (`docs/week0/proposed_region_membership.csv`) is registered at `prereg-2` as provisional:
  Campo das Vertentes and Metropolitana de Belo Horizonte go to Zona da Mata, Rio Doce e Central on
  an area fit (PAM 2025 against Conab 2025, +3.1% and −8.5%, against +7.8% and −16.1% the other
  way) and on geography. The owner is asking Conab's Minas Gerais office; an answer before
  `prereg-2` supersedes the test. The §4c checklist row now tracks only the historical extraction.
  Approved by owner.

- 2026-10-14 — **AMENDMENT 17c: the frost station set is per season, and the flag and penalty are
  measured on observed coffee.** Amends Amendments 17 and 17b. **Reason, the Week 0 station-set
  result** (`docs/week0_report.md` §8). Coverage figures are shares of each region's MapBiomas 2024
  coffee sample, for INMET automatic stations within 25 km and below the elevation cut:

  | Station set | Sul | São Paulo | Triângulo | Zona da Mata |
  |---|---|---|---|---|
  | As specified: complete in all 19 Jun–Aug windows 2008–2026 (1 station) | 0.0% | 0.0% | 0.0% | 0.1% |
  | Every candidate, whatever its record (64 stations) | 25.8% | 29.6% | 25.1% | 29.9% |
  | Complete in the Jun–Aug 2021 window (crop 2022) | 20.7% | 16.8% | 24.6% | 29.5% |
  | Complete in the Jun–Aug 2026 window (crop 2027) | 18.5% | 22.8% | 21.7% | 20.4% |

  Under Amendment 17 no region could be flagged in any season, so the frost component could never
  fire. Even every candidate station reaches only 25.1–29.9%, so the binding limit is network
  density at 25 km, not completeness alone. And because the penalty was scaled by the share of
  *total* coffee under stations meeting a tier, a frost hitting every station in a region would
  still have carried at most about 25–30% of the per-area loss.

  Changes:
  1. **Per-season membership.** A station counts in every season whose Jun–Aug record meets the
     completeness rule (95% of hours, no gap over 48 h); Amendment 17b still handles missing
     nights one at a time. This is a **declared exception to §9's identical-observations rule**,
     because the alternative is a component that can never fire. The backtest table reports the
     station count, by network, and the observed coverage per region and season.
  2. **Flag and penalty on observed coffee.** Observed coffee is the union of the season's
     qualifying stations' circles. A region is flagged for a tier when stations meeting it cover
     at least 25% of observed coffee. No flag in a region-season whose observed coverage is under
     15% of the region's coffee. The penalty is scaled by the tier's share of observed coffee,
     and the spec states the assumption this makes: unobserved coffee behaves like observed
     coffee. **The 15% floor was chosen from coverage information only, before any frost night
     was counted**, and is registered at `prereg-2` with that statement. With automatic stations
     alone, 19 of 76 region-seasons fall under it: Sul 2008–2016, São Paulo 2009, 2019 and 2025,
     Triângulo 2017, Zona da Mata 2008–2011, 2017 and 2019 (Jun–Aug window years). 2021 and 2026
     are above it in every region.
  3. **INMET conventional stations evaluated before registration**: BDMEP daily minima, the same
     radius and elevation cut, complete in a season with at least 95% of Jun–Aug days and no
     gap longer than 3 consecutive missing days, the daily analogue of the 48-hour rule; a longer
     gap fails that station-season, and Amendment 17b's missing-night rule applies to the
     remaining missing days. If they
     lift observed coverage, the networks are combined with the network recorded per station;
     otherwise the automatic network stands alone. Upper bound before any data, assuming every
     conventional station complete whenever it operated: 1 of 76 region-seasons under the floor
     (Triângulo 2017).
  4. **Note 1** uses the stations with complete 2026 records, as station observations with their
     coverage shares, alongside the public record (Cooxupé, Conab's September bulletin, Somar,
     press), with sources distinguished.
  5. **§5 step 1** records the MapBiomas-against-PAM finding beside the 30% filter.

  **Where the text goes beyond the owner's wording, for review:**
  - Note 1 also keeps the regional flags, since under the new rule every region is above the 15%
    floor in 2026 (18.5–22.8%) and a flag can be computed.
  - The §5 step 1 finding names São Paulo as well as Zona da Mata: São Paulo's ratio of MapBiomas
    sample share to PAM area share (0.77) is as low as Zona da Mata's (0.80), against 1.15 for Sul
    and 1.11 for Triângulo.
  - "Lift observed coverage" is taken literally: any region-season whose observed coverage rises.
  - Overlaps between the two networks follow the same union rule as overlaps within one.
  - Which night a conventional daily minimum belongs to is taken from INMET's documentation, not
    assumed.

  Approved by owner with one change: the daily rule also caps gaps at 3 consecutive missing days
  within a window (the draft had no gap limit).

- 2026-10-14 — **Fact update, not an amendment: VJ113A1 accepted; the elevation IDs resolve.**
  No rule changes. §4 and §4a recorded VJ113A1 as "Not started". It is now ingested
  (`vj113a1_mgsp_v2`, 401 composites, CRS declared as SR-ORG:6974) and passed the Amendment 30
  (second revision) acceptance check: 0 of 40 November–March months below 60%, lowest 69.4%
  (December 2021), confirmed by an independent recount. So the live vegetation fallback is (b),
  VJ113A1. The first probe exceeded the 0.25 EECU-hour gate (0.71) because it rebuilt the coffee
  weight in each request. Saving the weight once as an asset, on the owner's decision, brought
  the re-probe to 0.01 EECU-hours, within the gate. §4 also marked `USGS/SRTMGL1_003` as "Not yet
  verified to resolve". It and its declared fallback, `COPERNICUS/DEM/GLO30_2024_1`, resolved in
  the Week 0 ID check (2026-10-13), and SRTM was used for the provisional station elevation cut.
  The §10 checklist row records both. Requested by owner.

- 2026-10-14 — **AMENDMENT 19b: the target series, regional seasons and pass marks; the biennial
  term uses the final figure; the surprise test is reported, not scored, until more vintages
  exist.** Amends Amendments 19 and 12.

  **Reason: the §4c extraction** (Week 0 report §10).
  - Conab's arabica series gives regional area and yield only from safra 2008.
  - Its arabica-plus-conilon series is identical to it in area and production for Sul e
    Centro-Oeste, Triângulo and São Paulo in all 18 safras 2008–2025.
  - First- and final-survey tables were located only for safras 2023–2025. The Internet Archive
    refused the index query twice (HTTP 429, 2026-10-14), and per the owner's instruction was not
    tried again.

  Changes:
  1. **Target:** Conab's final figure for each safra as it stands in the current historical
     series, with the series download date recorded (2026-10-14). This closes §10 still-open
     item 1.
  2. **2001–2007:** Sul, Triângulo and São Paulo take area, yield and production from the
     arabica-plus-conilon series, justified by the identity in 2008–2025. Zona da Mata, which
     carries conilon, starts in 2008.
     - **Findings, recorded and not corrected:** Conab's arabica series writes the missing 2004
       regional production as 0 (Sul, Triângulo, Zona da Mata). In 2002 and 2006 its Sul figure
       exceeds the arabica-plus-conilon total.
  3. **Pass marks, with exact one-sided p-values beside each:**
     - the three long regions, crops 2001–2025: 18 of 25 (p = 0.0216);
     - Zona da Mata and the four-region total, crops 2008–2025: 13 of 18 (p = 0.0481);
     - with frost, crops 2009–2025: 13 of 17 (p = 0.0245).
     The owner kept 13 of 18 rather than raise it: the registered rule is p < 0.05, and raising
     the bar after seeing the season count is the adjustment the rule exists to prevent.
  4. **Biennial term (§5 step 7):** crop S−1's anomaly uses the final figure throughout, a
     declared leak.
     - Sized: third-to-final yield revisions for 2023–2025 averaged 1.9% in absolute size, with a
       largest of 8.4%.
     - A sensitivity recomputes the term from the third survey where one is on record
       (S−1 = 2023–2025), reported beside the headline.
     - Survey vintage tables are otherwise used only for the surprise test.
  5. **Surprise test:** reported for 2023–2025 with no pass mark until earlier vintages exist.
     Archived copies qualify as sources if the archive URL, capture date and checksum are
     recorded.

  Approved by owner.

- 2026-10-14 — **AMENDMENT 17d: night rule for conventional minima, provisional; stations sharing a
  site; 2026 re-request scheduled.** Amends Amendment 17c, which left the night a BDMEP daily
  minimum belongs to to be taken from INMET documentation that had not been found.
  1. **Night rule (owner):** INMET reads the conventional minimum at 12 UTC, covering the
     preceding 24 hours, so a minimum dated D belongs to the night ending the morning of D.
     Provisional until INMET's documentation is cited.
     - **Checked before `prereg-2`, on 2026-10-14** (`gee/bdmep_night_check.py`): six same-site
       pairs (Franca, Juiz de Fora, Araxá, Caratinga, Viçosa, São Carlos), all months 2008–2026,
       3,482–6,253 dates per pair. Only agreement statistics were computed; no frost night was
       counted.
     - The night ending the morning of D beats the night ending the morning of D+1 in all six.
       For the four without an offset: mean absolute difference 0.38–0.50 °C against
       1.10–1.46 °C, and 91–95% within 1 °C against 48–60%.
     - The UTC calendar day agrees as well as the 12 UTC window, so the exact boundary is not
       resolved.
  2. **Stations sharing a site (owner):**
     - Where a conventional and an automatic station share a site and both have complete records
       for a season, the automatic station governs the tier and the conventional station is left
       out of the union. The conventional station fills only seasons where the automatic record
       is incomplete.
     - Each pair's offset is recorded in the station table, `docs/week0/colocated_pairs.csv`. No
       correction is applied.
     - Any season in which a conventional station alone would change a region's tier is flagged.
     - Same-site circles are the same circle, so the rule changes which station's tier counts,
       not the observed coverage.
  3. **Scheduled (owner):** re-request BDMEP's 2026 conventional data in mid-November 2026,
     before note 1, and record whether the short 2026 windows (Caparaó, Lavras, Juiz de Fora)
     filled in. It is in the §10 checklist, and a reminder is set for 16 November 2026.

  **Where the text goes beyond the owner's wording:**
  - **"Share a site" is defined as within 1 km in INMET's catalogues.** That gives 19 pairs; 16
    have overlapping data. Passa Quatro (1.5 km) and Barbacena (1.9 km) fall outside.
  - **The station table records more offsets than the two the owner named:**
    - Caratinga −1.9 °C;
    - São Simão −0.9 °C (only 49% of dates within 1 °C);
    - Machado −0.6 °C (mean absolute difference 1.6 °C);
    - Viçosa +0.6 °C;
    - Caldas +0.6 °C;
    - the other 11 pairs within ±0.3 °C.
    Viçosa's offset is +0.6 °C on the rule window and +0.7 °C on the other two windows; the table
    records the rule-window value.

  Approved by owner.

- 2026-10-14 — **AMENDMENT 16c: the coffee mask moves to MapBiomas Collection 11; the mask lag is
  S−2.** Amends Amendment 16.
  - **What triggered it:** Amendment 16 set the lag at S−2 if a collection covering 2025 was
    published and verified before note 1.
    - **Published:** MapBiomas launched Collection 11 on 12 August 2026.
    - **Asset:** its coverage asset,
      `projects/mapbiomas-public/assets/brazil/lulc/collection11/mapbiomas_brazil_collection11_coverage_v3`,
      is listed on MapBiomas's own Earth Engine asset page and carries 41 bands, 1985–2025.
    - **Legend:** its legend file gives class 46 as "Café".
  - **Why every season moves, not only the live one:** Amendment 16 keeps all seasons on one
    product, and mask year 2025 exists only in Collection 11. So every season now uses Collection
    11, and Collection 10 is no longer used. Crops 2001–2027 use mask years 1999–2025.
  - **Why the switch is safe:** a Sul de Minas test box (W −45.9, S −21.9, E −45.1, N −21.3),
    checked at 30 m on 2026-10-14 for 14 EECU-seconds:
    - class 46 covers 16.4% in Collection 10 (2024), and 17.1% in Collection 11 for both 2024
      and 2025;
    - 98% of Collection 10's coffee pixels are also coffee in Collection 11.
  - **What is now stale:** Week 0 results computed on the provisional Collection 10 mask (the HLS
    and VJ113A1 tests, the drift check, the station-coverage proposal) used Collection 10's 2024
    classification. They are not rerun for this amendment; the station coverage is recomputed on
    the frozen mask before `prereg-2`, as already planned.

  Approved by owner.

- 2026-10-14 — **Pre-registration, `prereg-1` item closed: the MODIS cloud/QA rule is
  `SummaryQA` 0–1 (good or marginal).**
  - **Reason (owner): rainy-season coverage.** Keeping marginal pixels keeps the November–March
    composites usable; the strict variant (`SummaryQA` 0 only) is not computed.
  - **Not an amendment:** the spec says "cloud-masked" (§5 step 2) without fixing the rule.
  - **W1 scope set at the same time (option iii):** the full class-46 mask only; the
    persistent-pixel sensitivity is deferred, not dropped (still registered, §5 step 1); weights
    are exported per IBGE 1989 mesoregion.
  - **Recorded in** `docs/preregistration.md`. Owner decision.

- 2026-10-14 — **AMENDMENT 16d: one-sided 30% filter with stable membership, applied at
  aggregation; registered sensitivities; representativeness caveat.** Amends §5 step 1 and
  Amendments 16 and 16b.

  **Reason** (Week 0 report §12):
  - The original two-sided rule assumed that MapBiomas and PAM roughly agree. Inspection
    disproved it.
  - Collection 11 maps 0.19–0.63 of PAM's coffee area in São Paulo and Zona da Mata, and about
    half in every region in the early years. Only 18% of municipality-years agree within 30%.
  - The two-sided rule kept 4–19% of São Paulo's mapped coffee.
  - **Draft 1** (a one-sided test season by season) was not approved. Season-varying membership
    puts composition changes into the anomaly series, and single-season crossings of the
    threshold are noise, not over-mapping: Campos Gerais exceeded 1.3 in only 7 of 28 years
    (median ratio 0.88), and Três Pontas in 6 (median 0.98).

  **Changes:**
  1. **Stable, one-sided rule.** Each municipality is dropped for every season or for none: when
     the median, across mask years 1998–2025, of its persistent-pixel MapBiomas area over PAM
     total coffee exceeds 1.3. PAM zero with mapped coffee counts as an infinite ratio. Years with
     no coffee on either side, and years PAM marks missing, are not counted.
  2. **Untestable municipalities dropped:** 5 have mapped coffee but no comparable year, holding
     about 553 ha in total.
  3. **What it removes:** Sul 55, São Paulo 144, Triângulo 18 and Zona da Mata 84 municipalities.
     Share of mapped coffee kept: Sul 0.79–0.95, São Paulo 0.79–0.84, Triângulo 0.997–0.999, Zona
     da Mata 0.89–0.97.
  4. **Applied at aggregation.** Regions are aggregated by IBGE PAM coffee area, as registered in
     §3, which is unchanged. The PAM year for season S is S−2, the same lag as the mask and the
     latest available at the note date. A municipality with no PAM value gets zero weight.
     Registered sensitivities: no filter, and aggregation by mapped coffee area.
  5. **Representativeness caveat added to §5 step 1 and §11.**
  6. **Chosen after inspecting what the original rule removed.** That is mask information, not
     yield or frost outcomes; it is registered at `prereg-2` with that statement.

  Approved by owner with one change. Draft 2 proposed making mapped-area aggregation primary and
  changing §3; that was refused. PAM-area aggregation stays primary as registered, and
  mapped-area aggregation is the sensitivity.

- 2026-10-15 — **AMENDMENT 32b: no interactive reductions.** Adds a §9 rule beside Amendment 32.

  **Reason:**
  - The watchdog (`gee/ee_watchdog.py`) sees only batch tasks.
  - Cloud Monitoring shows about 356 EECU-hours of interactive use in the four hours of the
    2026-10-13 provisional drift check (Week 0 report §12 addendum), which no measurement
    recorded at the time.

  **Change:** a new §9 bullet.
  - Nothing larger than a few pixels is reduced through an interactive request.
  - Every reduction over an area runs as a batch export through the watchdog, with an estimate
    from a probe, and is cancelled at twice the estimate.
  - Interactive calls are allowed only for metadata, single-pixel reads and vector geometry.
    Each is tagged in the code, and `gee/check_interactive.py` enforces the rule.
  - Cost is recorded from each batch task's reported EECU use.

  **Already applied in code** on the owner's instruction, before the text was approved (commit
  1ce4985):
  - three scripts' interactive reductions converted to batch exports;
  - six unwatched batch tasks routed through the watchdog;
  - 16 remaining interactive calls tagged.

  The converted scripts stay unrun until each has a watched probe (owner, 2026-10-15).

  Approved by owner as written.

- 2026-10-15 — **AMENDMENT 35: vegetation anomalies computed per municipality, then aggregated by
  PAM area.** Amends §5 step 2. Owner decisions 1 and 2 on the W1 aggregation, taken after W1
  (Week 0 report §13, §14).

  **Reason:**
  - W1 reduces every composite per municipality (Amendment 16d).
  - Under PAM-area weighting a municipality can hold PAM area with no reading: fully cloud-masked,
    or under one MODIS pixel of mapped coffee.
  - The original step 2 (an area-weighted median over the mask, z-scored per window at region
    level) did not say how municipal values combine, and `prereg-1` held that as OPEN.

  **Changes:**
  1. **Membership per season:** kept by the filter, with PAM area for year S−2, and at least one
     MODIS pixel of mapped coffee under season S's mask. PAM weights are renormalised once per
     season over the members.
  2. **Municipal anomaly:** each counted reading minus the municipality's own mean for the same
     16-day period, in EVI units (owner choice (a)).
     - The mean comes from composites dated 2000–2025, in member seasons only (b).
     - At least 10 years are needed, or there is no anomaly (c).
     - A reading counts only with at least one pixel of cloud-free coffee (d).
     - The mean is refitted without the held-out season in the backtest.
  3. **Regional anomaly:** the PAM-weighted mean of members' anomalies (owner decision 2: a
     PAM-weighted mean of municipal medians, applied to their anomalies). Anomalies are
     aggregated, not raw EVI.
  4. **Cloud floor:** the regional composite is missing when members with an anomaly hold under 50%
     of the season's member PAM weight. The covered-weight fraction is reported for every
     composite.
  5. **The regional z-score stays** as the final standardisation, against the same 16-day period
     across baseline years, refitted without the held-out season.

  **What the W1 data show** (Week 0 report §14, read before the decision):
  - Member share of PAM area: 0.74–1.00 by region and season.
  - With rule (d), one composite falls under the floor: Zona da Mata, 2005-12-03, at 0.478.
  - Municipality-periods with fewer than 10 years hold at most 0.18% of member PAM weight in any
    region.
  - Rule (d) removes 3,640 member readings (1.32%).

  **Deviation from the owner's wording, recorded:** the owner's floor counts "municipalities with
  readings". The text counts members **with an anomaly**, because rule (c) leaves a reading
  without an anomaly where the climatology is under 10 years. Counting such a reading as covered
  would raise the covered fraction by weight that cannot enter the regional mean.

  **Consequence for `prereg-1`:** the regional-aggregation item is decided for EVI. Item 9 of the
  same day's `prereg-1` decisions applies the same aggregation to rain, soil moisture and heat
  days.

  Approved by owner with choices (a) to (d) as listed.

- 2026-10-15 — **AMENDMENT 36: frost loss on affected area fixed by formula; screen-to-leaf
  offset provisional.** Amends §5 steps 4 and 6.

  **Reason:**
  - §5 step 6 required the loss on affected area per tier to be registered at `prereg-1`, from
    Embrapa, IAC or peer-reviewed work.
  - A literature search (Week 0 report §15) found one source keyed to shelter temperature:
    Santos & Camargo (2006), *Bragantia* 65(1):173–183. It parameterises the Gaussian of
    Camargo et al. (2003), giving the percentage of trees damaged from the year's absolute
    minimum shelter temperature below 2 °C, applied as a cut to the next crop.
  - Vasconcellos et al. (2012) found the same IAC model's 100% loss overstated observed yields
    after −2.8 °C minima at São Sebastião do Paraíso, MG.
  - No source keys yield loss to a count of nights.

  **Changes:**
  1. **§5 step 6:** the loss on affected area is the Santos & Camargo (2006) damage fraction at
     T, the coldest observed Jun–Aug shelter minimum of the station whose 25 km circle covers the
     coffee. It is zero above 2 °C and capped at the formula's value at −1 °C (76.1%), citing
     Vasconcellos et al. (2012). It is fixed by formula, not fitted.
  2. **Per station, not per tier** (owner choice (b)). This is how the source applied it, it
     matches the registered 25 km circle design, and it keeps one anomalous station from setting
     the loss for a whole region.
     - **Overlap rule:** where circles overlap, the colder applies, consistent with severe over
       sensitive.
     - **The arithmetic that follows:** a tier's penalty is the sum of loss over the coffee in
       that tier's share, divided by observed coffee. Only stations meeting a tier contribute;
       coffee covered only by stations meeting no tier has no penalty.
  3. **Tiers, flag, shares and exclusivity are unchanged.** The three-night rule is marked
     provisional.
  4. **For transparency, the fixed constants that would otherwise have applied:** 11.5%
     (sensitive; the formula at 1 °C) and 54% (severe; its average from 0 to −1 °C).
  5. **§5 step 4: the screen-to-leaf offset is marked provisional,** as that step requires when no
     clean source exists.
     - The sources measure shelter minus grass: 4.1 °C (Sentelhas, Ortolani & Pezzopane 1995) and
       5.6 °C (via Astolpho, Camargo & Bardin 2004).
     - The 3–4 °C screen-to-leaf figure is an interpolation.

  **Equation, disclosed:**
  - The equation's layout in the source PDF is garbled. The form used,
    140.3445 × exp(−½((T − b1)/c1)²) with b1 = −2.9580 and c1 = 1.7701, is a reconstruction.
  - It was verified against the paper's tabulated values. 0.0 °C gives 34.7% and −2.0 °C gives
    100% (capped), both checked in the text. The literature search reproduced all eight values in
    the paper's Tables 2–3.
  - The owner checked the anchors 2.78% at 2 °C, 34.7% at 0 °C and 76.1% at −1 °C.
  - The alternative reading, with c1 not squared, gives 11.9% at 0 °C and does not reproduce the
    table.

  **In-sample check:** no value derives from the July 2021 frost.

  Approved by owner as written, with choice (b).

- 2026-10-15 — **AMENDMENT 37: §10 still-open items 2 and 4 closed, as decided at `prereg-1`.**
  Amends §5 step 6, §10 and §11.

  **Reason:** the owner's `prereg-1` decisions of 2026-10-15 (items 10 and 11) settled both, and
  the spec still listed them as open.

  **Changes:**
  1. **Item 2, region weights:** closed.
     - The four-region total is weighted by IBGE PAM coffee area for PAM year S−2, the same
       weights as within regions, not by production.
     - Its yield target is Conab's four-unit production over four-unit area.
  2. **Item 4, irrigation:** closed. No irrigation adjustment in v1; Triângulo's rain-only skill
     is reported separately.
  3. **§5 step 6:** the conditional sentence on the irrigation multiplier now states that it is
     not adopted. It had also pointed to "§10 item 5"; the item was 4.
  4. **§11 risk table:** the irrigation row now gives the v1 treatment.

  Drafted and committed on the owner's instruction (2026-10-15).

- 2026-10-15 — **AMENDMENT 38: scorable season sets, the two-step stage-1 fit, and the registered
  direction pass marks.** Amends §5 steps 7 and 8. **A change to items registered at `prereg-1`**,
  listed in the backtest report as such.

  **Reason** (Week 0 report §16, the base-rate check run on Conab yields only, before any
  season-level input):
  1. **The registered season sets cannot be scored.** The biennial term for crop S needs crop
     S−1. Conab's series starts at crop 2001, and Zona da Mata and the four-region total at 2008,
     so crops 2001 and 2008 respectively have no stage-1 expectation. The marks 18 of 25 and
     13 of 18 counted one season too many. This is arithmetic, not a result.
  2. **The marks depend on how stage 1 is fitted,** which `prereg-1` did not fix.

  **Changes:**
  1. **Season sets:**
     - without frost, Sul, Triângulo and São Paulo, crops 2002–2025 (24 seasons);
     - without frost, Zona da Mata and the total, crops 2009–2025 (17);
     - with frost unchanged, 2009–2025 (17).
  2. **Stage-1 fit (owner's choice):** two steps, each refitted without the held-out season.
     - First a linear trend.
     - Then the coefficient on the previous crop's detrended yield, with no intercept, leaving out
       every pair involving the held-out season.
     - The held-out yield enters no fit.
     - It reads §5 step 7 literally: a coefficient on crop S−1's anomaly from trend.
     - It defines the trend the yield-versus-trend target needs.
  3. **The rule** is p < 0.05, one-sided, against both a coin flip and the majority share,
     whichever needs more, with both exact p-values reported.
  4. **The registered marks** are the table in §5 step 8, with the base rates computed on
     2026-10-15. Two marks rise above the coin-flip mark: Triângulo without frost (19 of 24) and
     Zona da Mata (14 of 17).

  **Disclosure:** the fitting method was chosen on principle **with the base rates, and so the
  marks, visible.** Under the alternatives, a mark moves by at most one season, in either direction
  depending on region:
  - one-step OLS of y_S on (1, S, y_{S−1}) without row S;
  - the same without rows S and S+1.

  All three variants are in `docs/week0/base_rate_check.csv`.

  Approved by owner (2026-10-15).

- 2026-10-15 — **AMENDMENT 39: elevation cut fixed once per region; night rule cited in part;
  three stations added to the BDMEP re-request.** Amends §5 step 4 and §10. Owner decisions on
  the frozen-mask station set (Week 0 report §§17–18).

  **Changes:**
  1. **Elevation cut fixed once per region.** It is the median, over mask years 2007–2025, of the
     region's coffee-weighted 95th percentile of SRTM elevation at MOD13Q1 pixel centres on the
     frozen mask.
     - **Values:** Sul 1,176 m, São Paulo 1,121 m, Triângulo 1,194 m, Zona da Mata 1,140 m.
     - **Why fixed:** the owner chose a fixed cut over a per-season one for the same stability
       reason as Amendment 16d.
     - **Why the median:** the owner offered the persistent-pixel mask or the median across mask
       years. The median was used because the persistent-pixel mask is a 30 m construct not yet
       computed.
     - **Pixel-centre elevation accepted** (owner).
     - Completeness stays per season.
     - **Effect against per-season cuts:** three station-seasons change. Barbacena A502 is above
       the Zona da Mata cut in crops 2009–2011, holding under 0.01% of the region's coffee.
       Coverage is unchanged to one decimal.
  2. **Night rule: INMET documentation cited in part.**
     - The 12 UTC reading is cited: INMET (2022), p. 22; Diniz, Ramos & Rebello (2018), p. 140.
     - The reset time, the window and the date convention are not documented.
     - Accepted for `prereg-2` by the owner. Detail from INMET's observer manual, which the owner
       is obtaining, is an addendum.
  3. **The mid-November BDMEP re-request adds three operating conventional stations** with
     frozen-mask coffee within 25 km and no BDMEP data yet: Formoso (83334), Santo Antônio de
     Pádua (83805) and São Paulo Mirante de Santana (83781). The 2026 windows are a `prereg-2`
     addendum, not a blocker.

  Approved by owner (2026-10-15).

- 2026-10-15 — **AMENDMENT 39b (correction after `prereg-2`): the conventional stations already in
  the BDMEP zip were left untested.** Corrects the registered station set and Amendment 39 item 3.
  An error in the computation; the registered rules are unchanged. Listed in the backtest report as
  a change after `prereg-2`.

  **What happened:**
  - `gee/station_set_frozen.py` took conventional completeness only from
    `bdmep_completeness.csv`, which covers the 37 candidates requested on 2026-10-14.
  - The owner's BDMEP zip of that date holds 105 stations of the Sudeste request.
  - So 15 of the 19 frozen-mask conventional candidates labelled "no BDMEP data requested" had data
    in hand and were never tested. That includes the three stations Amendment 39 added to the
    November re-request "with no BDMEP data yet". That phrase was false.
  - Found while computing the W2 frost input, which reads the zip directly.

  **Correction:**
  - Completeness is now computed from the zip for every candidate, by the same rule
    (`bdmep_completeness_frozen.csv`). It reproduces all 665 windows of the 37 original candidates
    exactly.
  - 47 conventional candidates have data; 7 have none: six files have no values and one has no
    minimum-temperature column.

  **Effect on the registered station set:**
  - 12 stations newly qualify in 94 station-region-seasons, each holding at most 0.02% of its
    region's coffee.
  - Observed coverage changes by at most 0.1 point in any region-season. Triângulo crop 2018 moves
    from 7.5% to 7.6% and is still the only unflaggable region-season.
  - Elevation cuts are unchanged.

  **Spec text:** the §10 checklist row now says the three stations already have data, and the
  re-request refreshes their 2026 windows with the others'.
