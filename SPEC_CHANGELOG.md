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
