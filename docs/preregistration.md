# Pre-registration

Every choice that could be tuned, recorded before the results that could tempt a change (§9,
Amendment 15). Two tagged commits fix it:

- **`prereg-1`**, before W2 computes any season-level input.
- **`prereg-2`**, before the first backtest run: values that need data but not results.

Entries are added as they are decided. **Both tags were applied on 2026-10-15: `prereg-1` and `prereg-2`.** Any change after an
entry's tag is logged in `SPEC_CHANGELOG.md` and listed in the backtest report.

**Status words.** "Decided" means the spec already fixes the value. "**OPEN**" means a decision
the owner has not yet made; nothing here fills one in. Every OPEN item in prereg-1 must be
decided before the tag.

## prereg-1 — fixed before W2 (tagged `prereg-1`, 2026-10-15)

Amendment 15's list: the feature list, with each input's source, window and standardisation;
the weighting method and the terms counted toward the cap of four; the direction pass marks; the
frost tier constant values.

**Status, 2026-10-15: no item OPEN; tagged `prereg-1`.** The frost loss on affected area (F) is
fixed by formula (Amendment 36). The 34 °C citation (B) is closed, provisional. Any change after
this tag is logged in `SPEC_CHANGELOG.md` and listed in the backtest report.

### A. Seasons, windows and note dates (§3a)

| Item | Value | Source | Status |
|---|---|---|---|
| Season label | Season S is the crop harvested in year S (Conab safra S, trade S/S+1) | §3a | decided |
| Pre-flowering dry season | May–Aug of S−1 | §3a | decided |
| Frost exposure | Jun–Aug of S−1 | §3a | decided |
| Flowering | Sep 1–Nov 30 of S−1 | §3a, §5 step 3 | decided |
| Bean fill | Dec 1 of S−1 to Mar 31 of S | §3a, §5 step 3 | decided |
| Harvest rain | May–Sep of S: not an input (falls after every note on crop S) | §5 step 3 | decided |
| Backtest seasons | **Changed after the tag (Amendment 38, 2026-10-15):** without frost, Sul e Centro-Oeste, Triângulo and São Paulo, crops 2002–2025; Zona da Mata and the four-region total, crops 2009–2025; with frost, crops 2009–2025. The biennial term needs crop S−1, so each series' first season has no stage-1 expectation. *Registered at `prereg-1`:* 2001–2025 and 2008–2025 | §5 step 8, Amendments 19b, 38 | decided; changed after `prereg-1` |
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
| **Flowering rain deficit** | `UCSB-CHG/CHIRPS/DAILY` (final) for the backtest; CHC prelim (§4) for current months not yet final, as in Amendment 9 | **From 1 Sep of S−1 to the earlier of 30 Nov and the end of the last pentad ending at least 5 days before the cut** (item 5). Pentads end on the 5th, 10th, 15th, 20th, 25th and last day of each month. At the 20 November cut that is 1 Sep–15 Nov; at the 1 December cut 1 Sep–25 Nov; the January cut sees the whole window (*text corrected after the tag, Amendment 41; it read "the December and January cuts see the whole window", which contradicted the rule in the same cell*) | To-date rainfall total; anomaly against the same calendar span. Standardised as a **z-score of the to-date total**, not a share of normal (item 6) | **decided** (items 5 and 6) |
| **Dry-season root-zone soil moisture** | `ECMWF/ERA5_LAND/HOURLY`, `volumetric_soil_water_layer_1`–`_3`, weighted **0.07 / 0.21 / 0.72** by layer thickness | May–Aug of S−1. Closed before every cut | Mean of the layer-weighted moisture over the window. **z-score** (item 7) | **decided** (Amendment 28; item 7) |
| **Heat days in flowering** | `ECMWF/ERA5_LAND/HOURLY`, `temperature_2m` | From 1 Sep of S−1 to the earlier of 30 Nov and 10 days before the cut (ERA5-Land availability, item 4) | Count of days whose maximum temperature exceeds **34 °C**. Each day is 00:00–24:00 at **UTC−3**, Brazil's standard time, in every year; daylight saving is ignored. Standardised as a **z-score with the standard deviation floored at 1 day**, because the count is mostly zero at coffee altitudes (item 8) | **decided.** **34 °C: cited to Assad, Pinto, Zullo & Ávila (2004),** *Pesquisa Agropecuária Brasileira* 39(11):1057–1064, p. 1058 (frequent maxima above 34 °C cause flower abortion). **Provisional, no clean primary source** (owner, 2026-10-15): every statement found is secondary; the number traces to Nunes, Bierhuizen & Ploegman (1968), a dry-matter extrapolation with no flowering measurement, and the flower link to Camargo (1985), not found (Week 0 report §15). **Caveats recorded:** (1) the IAC yield model that uses 34 °C (Santos & Camargo 2006) applies it only to the 30 days after full flowering, narrower than this window; (2) IAC work (Camargo & Camargo 2001) and DaMatta & Ramalho (2006) tie heat damage at flowering to a concurrent water deficit, while v1 enters heat days and flowering rain as independent inputs; (3) ERA5-Land's 9 km grid smooths the terrain: its 2 m temperature is lapse-rate adjusted only to its own 9 km orography, and relief within a grid cell is not corrected (Muñoz-Sabater et al. 2021, *Earth System Science Data* 13:4349–4383, Sect. 2.3). In the hilly Sul e Centro-Oeste and Zona da Mata, Rio Doce e Central the grid-cell elevation can differ from the coffee fields' by hundreds of metres, so the count above 34 °C may be biased there. No correction is applied, the bias is not measured, and the caveat is stated beside heat-day results for those regions |

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
| Terms per region | Intercept, linear trend, and a coefficient on crop S−1's yield anomaly. Three per region; not counted toward the cap Fitted in two steps, each without the held-out season: a linear trend, then the coefficient of detrended yield on the previous crop's detrended yield, no intercept, leaving out every pair involving the held-out season (**added after the tag, Amendment 38**) | decided; estimation added after `prereg-1` |
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
| Penalty form | For each tier, the loss on affected area summed over the coffee in that tier's share, divided by observed coffee; applied as a fixed offset in each flagged region (§5 step 6). Assumes unobserved coffee behaves like observed coffee. Tiers exclusive, severe over sensitive | decided (Amendments 17c, 36) |
| **Loss on affected area** | **Fixed by formula, not fitted (Amendment 36).** Santos & Camargo (2006), *Bragantia* 65(1):173–183 (the Gaussian of Camargo et al. 2003): loss = 140.3445 × exp(−½((T + 2.9580)/1.7701)²) %, where T is the coldest observed Jun–Aug shelter minimum of the **station** whose 25 km circle covers the coffee; where circles overlap, the colder applies. **Zero above 2 °C; capped at 76.1%**, the formula's value at −1 °C (Vasconcellos et al. 2012: the uncapped formula overstated observed yields after −2.8 °C frosts). Sensitive tier 2.8–34.7%; severe tier 34.7–76.1%. **Provisional:** the three-night rule (no source keys loss to a count of nights) and the coefficients' calibration (not established). Equation reconstructed from a garbled PDF and verified against the paper's tabulated values. For transparency, the fixed constants that would otherwise have applied: 11.5% sensitive, 54% severe. Unresolved stations (Amendment 17b): reported with and without | **decided 2026-10-15** (owner; sources at `prereg-2`) |
| Frost series | From crop 2009 (the Jun–Aug 2008 window); not filled before | decided |
| Double counting and carryover | The 2022 call is in-sample. Crops 2022 and 2023, and any frost-flagged season, are reported with and without the frost component | decided |

### G. Backtest design and direction pass marks (§5 step 8)

| Item | Value | Status |
|---|---|---|
| Cross-validation | Leave one season out, in all four regions at once. Everything fitted is refitted without it: z-score means and SDs, trend, biennial coefficient, ridge penalty, weights | decided |
| Vintages | November, December, January, each using only inputs available at its cut date (A: 20 November, 1 December, 1 January) | decided |
| Targets | Condition direction: the sign of actual yield minus the stage-1 expectation. Yield versus trend: the sign of actual yield minus trend | decided |
| Comparison models | Zero anomaly; biennial only; rain only (expectation plus flowering rain deficit) | decided |
| **Direction pass marks** | **Changed after the tag (Amendment 38, 2026-10-15).** p < 0.05, one-sided, against both a coin flip and the majority share of positive condition anomalies, whichever needs more; both exact p-values reported. Without frost: Sul 17/24, Triângulo 19/24, São Paulo 18/24 (crops 2002–2025); Zona da Mata 14/17, four-region total 13/17 (crops 2009–2025). With frost (crops 2009–2025): Sul 13/17, Triângulo 13/17, São Paulo 13/17, Zona da Mata 14/17, total 13/17. p-values and base rates in §5 step 8. *Registered at `prereg-1`:* 18 of 25, 13 of 18 and 13 of 17, with the majority-share rule to be applied at `prereg-2` | decided (Amendments 19b, 38); changed after `prereg-1` |
| Target series | Conab's final figure for each safra in the current historical series, downloaded 2026-10-14. For 2001–2007, Sul, Triângulo and São Paulo take area, yield and production from the arabica-plus-conilon series (identical to arabica there in 2008–2025); Zona da Mata starts in 2008 | decided (Amendment 19b) |
| Crop 2026 | Added as an addendum once Conab's final is out, with and without it; not a clean out-of-sample test | decided |
| Surprise test | Rules as in §5 step 8 (revisions under 1% count as flat; skill against the base rate). **Reported for safras 2023–2025, not scored against a pass mark, until earlier vintages are found** | decided (Amendment 19b) |

## prereg-2 — fixed before the first backtest run (tagged `prereg-2`, 2026-10-15)

**Addenda after this tag, each logged with its date and reported with and without it where it
changes a figure:** (1) the 2026 conventional windows from the mid-November BDMEP re-request,
including the three stations named in Amendment 39, which already have data (Amendment 39b), for crop 2027's station set and coverage;
(2) any reset-time, window or date detail from INMET's observer manual (Amendment 39); (3) the
persistent-pixel index sensitivity, defined here and computed, with a watched probe, before the
backtest's sensitivity runs; (4) crop 2027's members, by the registered rule, from its first
composite under mask year 2025; (5) **frost night-rule sensitivity (Amendment 40), reported, not scored:** a night is also observed when its 00:00–09:00 local hours are complete (`docs/week0/w2_frost_night_rule_alternative.csv`); scoring keeps 17b.

| Item | Value | Source | Status |
|---|---|---|---|
| **Region membership** | `docs/week0/proposed_region_membership.csv`: Sul e Centro-Oeste = Sul/Sudoeste + Oeste de Minas (190 municipalities); Triângulo, Alto Paranaíba e Noroeste = Triângulo Mineiro/Alto Paranaíba + Noroeste de Minas (85); Zona da Mata, Rio Doce e Central = Zona da Mata + Vale do Rio Doce + Central Mineira + Campo das Vertentes + Metropolitana de BH (415); São Paulo = all 645 municipalities. Norte, Jequitinhonha e Mucuri (163) outside the index | Conab bulletin, 3rd survey 2026 (1989 mesoregions); Amendment 34 | **registered, provisional.** Campo das Vertentes and Metropolitana de BH by area fit: PAM 2025 against Conab 2025, +3.1% (Sul e Centro-Oeste) and −8.5% (Zona da Mata, Rio Doce e Central), against +7.8% and −16.1% the other way. An answer from Conab's MG office before the tag supersedes this |
| **São Paulo target (§4c)** | São Paulo state total, as the Mogiana target | Conab 3rd survey 2026 table: SP reported only as a state total; Amendment 34 | **registered** |
| **Mask product and lag** | MapBiomas **Collection 11** (`projects/mapbiomas-public/assets/brazil/lulc/collection11/mapbiomas_brazil_collection11_coverage_v3`), class 46. **Mask year = S−2** for every season, unchanged: crops 2001–2027 use mask years 1999–2025, and crop 2027 (the live season) uses 2025 | Amendment 16c (2026-10-14) | **registered 2026-10-15** |
| **Full class-46 mask** (the index) | Per season, class 46 in mask year S−2, as the coffee fraction of each MOD13Q1 pixel (mean of the 30 m class-46 indicator). Saved once as 24 assets, one per IBGE 1989 mesoregion, `<EE_PROJECT>/w1_weights_meso_<code>` with bands `w_1998` … `w_2025` (Sul 3109, 3110; Triângulo 3101, 3105; Zona da Mata 3106, 3107, 3108, 3111, 3112; São Paulo 3501–3515). Unfiltered in the asset: the filter is applied at aggregation | Amendments 16c, 16d; Week 0 report §13 | **registered 2026-10-15** |
| **Persistent-pixel mask** (sensitivity, and the filter's comparator) | Pixels classified 46 in mask year M and in M−1 and M−2. Used now for the 30% filter's comparison with PAM. As an index sensitivity it is **defined but not yet computed** (W1 option iii deferred it); it is computed, with a watched probe, before the backtest's sensitivity runs | Amendments 16b, 16d | **registered 2026-10-15** (definition) |
| **Filter rule and the municipalities it drops** | One-sided, stable membership: a municipality is dropped for every season when the median, over mask years 1998–2025, of its persistent-pixel MapBiomas area over PAM total coffee area exceeds 1.3; untestable municipalities with mapped coffee are dropped. **Drops 301 municipalities** (Sul 55, São Paulo 144, Triângulo 18, Zona da Mata 84, including the 5 untestable): `docs/week0/w1_filter_stable_removed.csv`, SHA-256 `ba2e5f15ba67edb6cc1ce8c4c2aa978d8cca3dd953e9e599965fc26e5fb99185`; every municipality's decision in `docs/week0/w1_filter_stable_membership.csv`, SHA-256 `3ddf08ab051151420ba14d86330dbe48c351c07a6e8758fa21460899852d66dc`. **Statement: the rule was chosen after inspecting what the original rule removed. That is mask information, not yield or frost outcomes** | §5 step 1; Amendment 16d | **registered 2026-10-15** |
| **Members per season** | Kept by the filter, PAM area for year S−2, and at least one MODIS pixel of mapped coffee under season S's mask (Amendment 35). Seasons 2000–2026, from the W1 series: `docs/week0/members_by_season.csv`, SHA-256 `da284b467d9b982003c6d903e42cc0696445381d3693aa6b3304619f5633f8e6` (436–484 members a season). Crop 2027's members follow by the same rule from its first composite under mask year 2025, and are recorded when computed | Amendment 35; Week 0 report §14 | **registered 2026-10-15** |
| **Registered sensitivities, mask and aggregation** | (1) no filter: the full class-46 mask in every index municipality; (2) regions aggregated by mapped coffee area (MapBiomas) instead of PAM area; (3) the persistent-pixel mask. Each reported beside the headline | Amendments 16b, 16d | **registered 2026-10-15** |
| **W1 series used by the index** | Per-municipality MOD13Q1 EVI/NDVI tables, composites 2000-02-18 to 2025-12-19, with their SHA-256 values in Week 0 report §13 | Week 0 report §13 | **registered 2026-10-15** |
| **Station list per region and season, by network; altitude cut; observed coverage** | Recomputed on the frozen mask by `gee/station_set_frozen.py` from the pixel table of `gee/frozen_mask_pixels.py` (the registered W1 weights; Week 0 report §17). **Corrected after the tag (Amendment 39b):** conventional completeness now read from the BDMEP zip for every candidate. Candidates: 75 automatic, 54 conventional (47 with data); 69 automatic and 43 conventional stations qualify in at least one region-season. **Elevation cut, fixed once per region (Amendment 39):** the median over mask years 2007–2025 of the coffee-weighted 95th percentile of SRTM at pixel centres: **Sul 1,176 m, São Paulo 1,121 m, Triângulo 1,194 m, Zona da Mata 1,140 m** (per-year values in `elevation_cut_frozen.csv`). Completeness per season. Stations within 50 m of the cut: Barbacena A502 (automatic, 1,169 m; above the cut in every season) and 83689 (conventional, 1,128 m; below), Zona da Mata, each 0.01% of the region's coffee. **Unflaggable:** Triângulo crop 2018 (7.6%; 7.5% as tagged) only. Same-site pairs: 24. Files and SHA-256: `station_set_frozen.csv` `36a641b8f9c62baf95b741d669826c959ee296dec1dfe8d446c53e707433fe1e`; `station_coverage_frozen.csv` `a3bb61301fe8dd7cae17eb415f8272fa601d84edb1b2e5bb68106bd51a92af0d`; `elevation_cut_frozen.csv` `ff548fa59b0cc13bcaf0b53f2058d738f3eff61e9fdd42e7101e11cae2e96dfc`; `station_candidates_frozen.csv` `3340f1deab4ed5ad264ee47011450fc58a37b92c20242193ade0cfffab85a7d6`; `bdmep_completeness_frozen.csv` `f590f6cef8b728f10df9f037ae4e2b60af22db1d6e106c658ea690a24839a33d`; `inmet_completeness_frozen.csv` `d26cb6c0e05574655cd0482831024f8bd25d7d3582f568e23d4a7d56e73bd7e6`; pixel table (gitignored) `71a70aa6f5b6f1188148ef6bf1a4cde2479bbba54a1d384a69ec3ba63f292faa`. **Crop 2027's conventional windows** are an addendum after the mid-November BDMEP re-request, not a blocker (owner, 2026-10-15); on automatic stations alone its coverage is 19.2–25.8% | §5 step 4; Amendments 17, 17b, 17c, 17d, 39, 39b | **registered 2026-10-15; corrected after the tag (Amendment 39b)**; crop 2027's conventional windows: addendum |
| INMET citation for the conventional night rule | **Cited in part.** INMET (2022), *Normais Climatológicas do Brasil 1991–2020*, p. 22, and Diniz, Ramos & Rebello (2018), *Pesquisa Agropecuária Brasileira* 53(2), p. 140 (INMET authors): the minimum thermometer is read usually at 12 UTC. Not documented: the reset time, the window, and the date the minimum is filed under. Every reading consistent with the sources (12–12 UTC, 00–24 UTC, or reset at 24 UTC) puts the pre-dawn minimum of the night ending the morning of D on date D, which is the rule; the co-located check supports it (Week 0 report §18) | Amendments 17d, 39 | **registered 2026-10-15: cited in part** (owner); detail from INMET's observer manual: addendum |
| Coverage floor statement | **15%. The floor was chosen from coverage information only, before any frost night was counted.** No frost night has been counted at any station to this tag; the night-rule check (Amendment 17d) compared same-site minima for agreement and counted no frost nights | Amendment 17c | **registered 2026-10-15** |
| Surprise-test pass mark | **The surprise test is reported, not scored,** until first- and final-survey figures beyond safras 2023–2025 are found. The pass mark is then computed from Conab's base rate and fixed before it is used | Amendments 12, 19b | **registered 2026-10-15** (the statement) |
| Base-rate check on the direction pass marks | Run 2026-10-15 on Conab yields only, before any season-level input (Week 0 report §16; `docs/week0/base_rate_check.csv`). Two findings: the without-frost sets can be scored on 24 seasons (2002–2025) and 17 (2009–2025), not 25 and 18; and the marks depend on the stage-1 estimation detail, which `prereg-1` did not fix. **Resolved by Amendment 38:** seasons 2002–2025 and 2009–2025; two-step stage-1 fit; the registered marks are the table in §5 step 8 | Amendment 19 | **registered 2026-10-15** (Amendment 38) |
| Frost tier constant sources | **Loss on affected area:** Santos & Camargo (2006), *Bragantia* 65(1):173–183, with the cap from Vasconcellos et al. (2012), XVII Congresso Brasileiro de Meteorologia (Amendment 36). **Leaf damage:** Camargo & Salati (1966), *Bragantia* 25(2), Nota 14: damage from −2 °C, general below −3 °C. **Screen-to-leaf gap: provisional, no direct measurement** (owner, 2026-10-15). Sentelhas, Ortolani & Pezzopane (1995), *Bragantia* 54(2):437–445: shelter minus grass 4.1 °C on average (3.3–5.7) over 226 frost nights, and the 2 °C shelter minimum cited as coffee's damage onset. Astolpho, Camargo & Bardin (2004), *Bragantia* 63(1):141–147: shelter 2 °C and 1 °C ≈ leaf −3.6 °C and −4.6 °C. Both measure shelter minus grass, not shelter minus leaf | Amendment 15; Week 0 report §15 | **registered 2026-10-15** |

## Decided before the single backtest run, after both tags (Amendment 41, 2026-10-15)

Owner decisions after an independent review of the scoring code, before any backtest result:

| Item | Decision |
|---|---|
| Persistent-pixel mask | Inputs computed under the watchdog and frozen before the run; a sensitivity in the run |
| VJ113A1 | Concordance check, not a scored sensitivity: anomalies against its own climatology (five-year minimum), correlation and sign agreement with the MODIS inputs on overlapping crops per region; a later labelled run |
| Headline frost penalty | **Reversed by Amendment 41b:** unresolved stations kept at their observed tiers, the coverage registered at `prereg-2` (Triângulo crop 2018 the only unflaggable region-season). Registered sensitivity: unresolved stations left out, which flags Sul crop 2020 severe (consistent with the July 2019 frost) and makes 18 of 68 region-seasons unflaggable. Both outcomes were visible before each choice |
| Pass marks | The November vintage decides pass or fail; December and January reported against the same marks, not scored |
| EVI availability | Composite end = Earth Engine's end date (start + 16 days), as in the lag measurement; confirmed |
| Units | Condition anomaly as a share of the stage-1 expectation; frost penalty as a share of yield |
| Standardisation | Pooled inputs re-standardised within each fold on its training rows |
| Inner λ loop | Reuses the outer fold's inputs; leaves out crops k and k+1; scores crop k |
| Four-region total | Own stage 1; predicted from its own inputs with the pooled weights; never a training row |
| Mapped-area sensitivity | Same members, weights changed only |
| Third-survey sensitivity | Changes only the held-out expectation |
| No-filter and mapped-area sensitivities | Keep the registered frost penalty |
| Conventional-station availability | Assumed available at every cut; not established; caveat beside the Sul crop-2012 result |
| Fixed in code from the review | Crop S+1 left out of training in fold S (its expectation carries crop S's yield); one-shot run; identical-crop comparisons |

## prereg-3 (v2): hypotheses registered 2026-10-16, after the v1 backtest (tagged `prereg-3`, 2026-10-16)

**Status.** Registered on the owner's instruction after the v1 results were read (Week 0 report
§24). Nothing in v1 changes: the marks, inputs and verdicts stand.
- **Tag:** `prereg-3` was applied on 2026-10-16, before any v2 computation. Three values are fixed
  later, before any v2 computation, each as a logged prereg-3 addendum:
  - H3's night-LST frost threshold;
  - H3's false-alarm number;
  - H4's flowering-trigger rain event.
  Any other change after the tag is logged in `SPEC_CHANGELOG.md`.
- **Approval (owner, 2026-10-16):**
  - H1–H3 are approved as drafted.
  - H4 was added the same day on the owner's statement of the hypothesis and prediction. Its
    test details are a draft.
- **Testing rule (owner, 2026-10-16):** every hypothesis is marked in-sample. It is tested only on
  crops 2027 onward and on held-out (leave-one-season-out) reruns of history.
  - The hypotheses were formed after the v1 results were seen. So every result on crops 2002–2026
    is labelled in-sample, whatever the fold structure.
  - Crops 2027 onward are the only out-of-sample test.
- **Spec status:** the spec's §9 defines `prereg-1` and `prereg-2` only. Defining `prereg-3` in the
  spec is an amendment, drafted when v2 starts.

### H1. Conab 2001–2007 series quality

| Field | Entry |
|---|---|
| Hypothesis | The target values for crops 2001–2007 in Sul e Centro-Oeste, Triângulo, Alto Paranaíba e Noroeste and São Paulo, taken from Conab's arabica-plus-conilon series (Amendment 19b), differ from Conab's arabica figures for those safras by enough to change stage 1 (the trend and the biennial coefficient) and the no-frost scores in those regions |
| v1 facts behind it (Week 0 report §24 (5); §4c) | Sul's biennial coefficient is +0.076, against −0.25 to −0.66 in the other units. Biennial-only gets 7 of 24 on yield versus trend in Sul. Amendment 19b recorded these findings in the arabica series: 2004 regional production written as 0; Sul production above the arabica-plus-conilon total in 2002 and 2006 |
| Planned test (approved 2026-10-16) | (a) Extract Conab's arabica regional area, yield and production for safras 2001–2007 from final-survey bulletins, archived copies included. Record the URL, capture date and SHA-256 for each. (b) Compare them value by value with the series v1 used. (c) Refit stage 1 on the corrected series. (d) Report beside v1: the biennial coefficient per region, and the no-frost condition hits on crops 2002–2025 |
| Registered prediction (approved 2026-10-16) | On the corrected series, Sul's biennial coefficient is negative |
| Testing | A held-out rerun on the corrected series, labelled in-sample. There is no out-of-sample test: this is a data-quality check on history. A changed target series is a new labelled backtest, not a rescore of v1 |

### H2. Zona da Mata mask representativeness

| Field | Entry |
|---|---|
| Hypothesis | Zona da Mata, Rio Doce e Central fails because the mask under-represents its smallholder and shaded coffee. The vegetation signal tracks yield better where MapBiomas maps a larger share of the coffee area IBGE PAM records |
| v1 facts behind it (Week 0 report §24 (4); §5 step 1) | Zona da Mata fails both versions (12 and 10 of 17, against 14). Its MAE is above zero anomaly's (10.3 and 10.8 against 9.9). Its mean signed residual is −3.0 and −3.8 pp. Its points-to-PAM-area ratio is 0.80. MapBiomas maps 0.19–0.63 of PAM's coffee area in Zona da Mata and São Paulo |
| Planned test (approved 2026-10-16) | Within Zona da Mata, with São Paulo as the second region: correlate each municipality's season EVI anomaly (the v1 municipal input, frozen mask) with its IBGE PAM yield anomaly. Report by tercile of the municipality's MapBiomas-to-PAM area ratio. PAM's arabica split exists only from 2012, so use arabica yield for 2012 onward and the total-coffee yield before, reported separately. Planet's mask validation (§4d task 2) gives the omission estimate beside it |
| Registered prediction (approved 2026-10-16) | The municipal correlation rises from the lowest to the highest coverage tercile |
| Testing | On history, held-out reruns only, labelled in-sample: the municipal relation was not examined in v1, but Zona da Mata's failure is known. Out of sample: crops 2027 onward |

### H3. Cold-pool frost detection

| Field | Entry |
|---|---|
| Hypothesis | The screen-height station network misses frost that forms in cold-air pools on coffee land. MODIS night land-surface temperature over the coffee mask detects frost the stations miss, including the July 2021 frost in Sul e Centro-Oeste and São Paulo |
| v1 facts behind it (Week 0 report §19, §24 (2); Amendment 40) | The station component did not flag the July 2021 frost in Sul or São Paulo: their crop-2022 penalty is zero. With frost, crop 2022 is predicted −13.9% and −13.7%, against actual −32.5% and −30.0%. Caldas (A530) read −0.5 °C on 14 July 2026 outside the registered night rule |
| Planned test (approved 2026-10-16) | Night LST for Jun–Aug of S−1, crops 2009–2026, on the frozen mask. Product IDs are verified in Earth Engine before use (§9); the candidates are `MODIS/061/MOD11A1` and `MODIS/061/MYD11A1`, not yet verified. A night-LST frost threshold is fixed from a published LST-versus-screen or LST-versus-leaf study before computing. Report the region-seasons LST flags against the station flags |
| Registered prediction (approved 2026-10-16) | (a) LST flags Sul and São Paulo for crop 2022. (b) LST flags no more than a number of region-seasons without a station flag or a public-record frost; that number is fixed before any v2 computation, as a logged prereg-3 addendum |
| Testing | On history, held-out reruns only, labelled in-sample. The July 2021 frost is known, so (a) is in-sample by construction, and the Planet 2021 case study (§4d task 1) is the independent check. Out of sample: crops 2027 onward. For crop 2027 (the Jun–Aug 2026 window), the station readings, Caldas included, were known when H3 was formed; the LST values and the crop's yield were not. Terra and Aqua are at end of mission, so the product's availability for each window is checked first |

### H4. Flowering rain: timing and volume

| Field | Entry |
|---|---|
| Hypothesis | The v1 flowering-rain input, a z-score of the to-date rainfall total, mixes two effects of opposite sign: when the first flowering rain falls, and how much rain falls in total. Split into the two, the timing term carries the expected sign and the volume term keeps the negative sign |
| v1 facts behind it (Week 0 report §24 (3)) | In the full model the rain weight is negative in every fold and vintage: −0.021 to −0.051 per standard deviation in the November fits, −0.018 to −0.055 across all three vintages. More flowering rain predicts a lower condition anomaly, the opposite of the sign §5 step 3 anticipates. In the rain-only model the weight shrinks to near zero (at most 0.012 in absolute value) |
| Registered prediction (owner, 2026-10-16) | (a) Timing has the expected sign: a later first-rain date predicts a lower condition anomaly. (b) Volume keeps the negative sign: with timing in the model, more to-date flowering rain still predicts a lower condition anomaly |
| Planned test (the agent's draft, registered at the tag) | Replace the v1 rain input with two inputs, both standardised as in prereg-1. **(i) First-rain date:** the first day after 1 Sep of S−1 that ends a flowering-trigger rain event, from daily CHIRPS. The event (an amount over a number of consecutive days) is fixed from a published coffee-flowering source before any v2 computation, as a logged prereg-3 addendum. A cut that comes before any event takes the cut date, and the count of such censored region-crops is reported. **(ii) Volume:** the v1 to-date total, unchanged. Fit the five-input diagnostic variant with v1's folds, vintages and ridge machinery, and report each weight's sign per fold |
| Decided (owner, 2026-10-16) | (1) **The cap of four (§5 step 6) is unchanged for the v2 headline.** H4 is a five-input diagnostic variant reported beside it. The v2 pre-registration chooses the headline's four inputs before any v2 result. (2) **Production onset dates come from the ingested CHC prelim daily product.** Where a day in a season's window is missing, onset is undefined for that season and is reported as such. Amendment 29's rule still applies: onset from daily prelim is not compared with onset from final until the gap is measured on overlapping months |
| Testing | On history, held-out reruns only, labelled in-sample. Out of sample: crops 2027 onward |
