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
