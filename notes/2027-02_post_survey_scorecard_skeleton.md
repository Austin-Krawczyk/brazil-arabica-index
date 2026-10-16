# Skeleton: note 3, the post-survey note and first scorecard (crop 2027, the trade's 2027/28)

**Status.** Draft skeleton, 2026-10-16. It is drawn from the Week 0 report §24, and its fixed text
blocks cite their source there. `{braces}` are placeholders. Everything outside braces is fixed
wording, to be changed only by a logged decision.

**When it goes out (§6).** Within five business days of Conab's first survey of crop 2027, which is
expected late January or early February 2027; confirm the date from Conab's calendar. If Conab has
not published by 31 January, it goes out on the first business day of February without the Conab
lines, marked [FALLBACK] below, and a scorecard addendum follows the survey.

**Format.** One page, PDF and LinkedIn. The emailed PDF carries no Planet-derived material (§4d).

---

## Brazil arabica growing conditions: crop 2027 scorecard, {date}

**Condition index, not a yield forecast.**

### Headline
- **Four-region condition index:** {value, z}, {better / worse / in line with} the baseline.
  Readings as of {cut date}.
- **Coverage:** the four Conab units in the index are {share}% of Brazil's arabica (Conab,
  {survey and date}). Every comparison with a Brazil-wide figure is on that coverage.
- **Direction against the expectation:** {direction}, against trend and an expected {on / off}-year
  (stage 1, §5 step 7).
  - In Sul de Minas the expectation carries almost no on/off-year term; its biennial coefficient is
    near zero (§24 (5)).

### Scorecard: the readings made before Conab's survey, beside Conab's first number

| | November reading | December reading | Conab first survey [FALLBACK: not yet published] |
|---|---|---|---|
| Made as of | 20 Nov 2026 | 1 Dec 2026 | {survey date} |
| Published in the repo | {commit, date} | {commit, date} | — |
| Four-region condition anomaly against the expectation | {+/−x.x%} | {+/−x.x%} | {+/−x.x%} (Conab first-survey yield against the same expectation) |
| Direction | {up / down / within the prelim margin} | {…} | {up / down} |
| Sul de Minas · Cerrado Mineiro · Matas de Minas · São Paulo | {…} | {…} | {…} |
| Vegetation product | {MOD13Q1 / VJ113A1} | {…} | — |
| Rain months on CHIRPS-prelim | Oct, Nov 2026 | Nov 2026 | — |

- **Surprise-test call, stated now and scored at Conab's final:** the index points to Conab
  revising crop 2027 **{up / down}** between its first and final surveys. The call is the sign of
  the index-implied anomaly minus Conab's first-survey anomaly, both against the same expectation
  (§5 step 8).
  - Conab's final is expected in December 2027 or January 2028.
  - [FALLBACK: stated in the addendum once the survey is out.]
- **This test's record so far: reported, not scored.**
  - Only three safras have both surveys on record (2023–2025).
  - Four-region total, November calls: 1 of 3. December calls: 2 of 3 (§24; report A4).
- **What is not scored here:** the agreement between the readings and Conab's first number. The
  scored target is Conab's final survey.

### Chart
Index by region against the baseline band, crops 2002–2026 and the 2027 readings to date.

### Regions

| Region | Index | Flowering rain against normal | Frost, Jun–Aug 2026 (note 1) | Comment |
|---|---|---|---|---|
| Sul de Minas | {z} | {%} | {tier, share of observed coffee, coverage} | {one line} |
| Cerrado Mineiro | {z} | {%} | {…} | {one line} |
| Matas de Minas | {z} | {%} | {…} | **Failed its backtest pass mark in both versions (§24 (4)).** {one line} |
| São Paulo | {z} | {%} | {…} | {one line} |

### Benchmark
- **Conab 2027, first survey:** {production, area, yield for the four units} [FALLBACK: "Conab has
  not yet published its first survey of crop 2027. No Conab estimate for the 2027 crop exists yet."]
- **Private 2027/28 estimates, arabica component only:** {house, figure, publication date} for each
  house that publishes an arabica figure. If none has published: "versus trend and an expected
  off-year".
  - A total-Brazil figure includes conilon and is not a benchmark.
- **If a number of bags is asked for:** the answer is a range, never a point. It is relative to
  Conab's first 2027 survey, and to trend and the expected off-year before that (§1).

### Track record (fixed text from §24 (1)–(3); revised only by a logged decision)

The backtest is pre-registered, leave-one-season-out, scored by note date against Conab's final
arabica yields.
- **November vintage, the scored one:**
  - Without the frost component, the index met its pass mark in **1 of 5** units (Sul de Minas,
    18 of 24 seasons).
  - With it, the index met its pass mark in **4 of 5** (Sul de Minas, Cerrado Mineiro, São Paulo
    and the four-region total; 13–14 of 17 seasons, 2009–2025).
  - Crop 2022, the July 2021 frost, is in-sample.
  - Matas de Minas failed in both versions.
- **Against a zero-anomaly baseline,** the index's error is lower in four of five units (all but
  Matas de Minas).
- **Not scored:** December and January vintages.
- **Full table:** {repo link to docs/backtest_v1_results.md}.

### Market context
- **ICE:** Coffee C front month {¢/lb}; Jul/Dec spread {}; ICE certified stocks {bags}. ICE figures
  appear in the note text only, never in committed data files (§4).
- **CFTC:** managed-money net, Commitments of Traders {date}: {contracts}.

### The view
{One paragraph. One stated lean. What would change it.}

### Method and caveats
1. **Condition index, not a yield forecast.** It tracks conditions. The private trade houses have
   field crop tours and farm data that this project does not.
2. **Matas de Minas:**
   - {MODIS at 250 m / VJ113A1 at 500 m} blurs its steep smallholder terrain.
   - The mask under-represents its smallholder and shaded coffee.
   - It failed its backtest pass mark.
3. **Inputs:**
   - Rain for {months} is CHIRPS-prelim. A reading within about 1 pp of zero is stated as "within
     the prelim margin" (proposed in §24 (6), not registered).
   - Vegetation: {product} for each reading.
   - Frost: INMET station observations, {coverage} of observed coffee.

---

## Notes for assembly (not printed)
- **Readings to cite:** the November reading must be in the repo no later than note 1, and the
  December reading before the survey. Cite both commits (§6).
- **Terra:** check trigger (a) at the note date (§4a). If no `MOD13Q1` composite ends within 32 days
  of it, this and later readings use VJ113A1, and the table says which product each reading used.
- **Unflaggable regions:** any region-season unflaggable for frost (coverage under 15%) is said so
  in the region table.
- **Planet:** a 3 m figure, labelled "not an input", may go in the LinkedIn post and the repo copy
  only, never in the emailed PDF (§4d).
- **"Within the prelim margin":** this wording is a proposal from §24 (6). It needs the owner's
  decision before it is used.
- **Outreach:** log every reply with name, firm, date and what was said (§6).
