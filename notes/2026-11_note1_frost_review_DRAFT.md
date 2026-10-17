# DRAFT, HELD: Note 1, the Jun–Aug 2026 frost review (crop 2027)

**Status: held, 2026-10-16. Not for publication.** It is drafted from the Week 0 report §19 and the
frozen frost tables. It is held until the BDMEP addendum: the mid-November re-request of the
conventional stations' 2026 daily minima (scheduled for 16 November 2026).

**What the addendum can change:**
- the conventional stations counted for crop 2027 (only one counts now: Formoso, 83334, in
  Triângulo);
- observed coverage, tiers and flags.

**After the addendum:**
1. Rerun `gee/station_set_frozen.py` and `gee/w2_frost.py` locally on the new zip. They make no
   Earth Engine call.
2. Log the result as a `prereg-2` addendum.
3. Update every number in this draft.

**One limit on the addendum:**
- Caldas's conventional station (83681) shares the automatic station's site (0.01 km).
- It is closed, with no data since 2023.
- So the addendum cannot give an independent reading of Caldas's 14 July night.

**Publication:** late November 2026 (§6), with the November-vintage index reading committed to the
repo no later than this note.

---

## Frost and the 2027 Brazilian arabica crop: what the station record shows for June–August 2026

**{publication date}**

**Why this window.** Winter frost damages the trees. The loss shows in the harvest after the next
flowering. So June–August 2026 is the frost window for the 2027 crop, the trade's 2027/28. That
window is over, so this is a review of what happened, not a forecast.

**Coverage.** The four Conab units tracked here held 83.1% of Brazil's arabica production in
Conab's September 2026 estimate for the 2026 crop: 40.1 of 48.2 million bags. {Update if Conab's
final survey for crop 2026 is out.}

### What the stations show

Station observations are INMET's automatic network (hourly) and conventional network (daily
minima). Stations within 25 km of the mapped coffee and below each region's elevation cut, with a
complete June–August record, are counted.

| Region (Conab unit; trade name) | Stations counted | Share of the region's coffee within 25 km of a counted station | Stations at the 2 °C tier / severe tier | Regional flag | Coldest night on the registered rule |
|---|---|---|---|---|---|
| Sul e Centro-Oeste ("Sul de Minas") | 9 automatic | 19.2% | 0 / 0 | none | 2.9 °C (Caldas) |
| Triângulo, Alto Paranaíba e Noroeste ("Cerrado Mineiro") | 10 automatic, 1 conventional | 21.5% | 0 / 0 | none | 4.8 °C (Patrocínio) |
| Zona da Mata, Rio Doce e Central ("Matas de Minas") | 14 automatic | 21.5% | 0 / 0 | none | 3.4 °C (São João del Rei) |
| São Paulo ("Mogiana") | 22 automatic | 25.8% | 0 / 0 | none | 3.2 °C (Itapira) |

**Tiers and flags:**
- A station meets the 2 °C tier with three or more nights at or below 2 °C at screen height, and
  the severe tier with one night at or below 0 °C.
- A region is flagged when stations meeting a tier cover at least 25% of its observed coffee.
- These thresholds are agronomic constants, registered before the frost inputs were computed. They
  were not fitted.

**Result: on the registered rules, no station meets a frost tier and no region is flagged for the
2027 crop.**

### What that result does not show

**It does not establish that there was no frost.**
- **Caldas (A530, Sul de Minas), outside the registered rule and not scored:**
  - The station's 19:00–20:00 local readings are missing on every night from 1 June to 22 July
    2026.
  - Under the registered rule a night counts only when every hour from 18:00 to 09:00 is present,
    so those nights are unobserved.
  - The pre-dawn readings on those nights are complete. They show seven nights at or below 2 °C,
    the coldest **−0.5 °C on the morning of 14 July 2026**: a severe-tier reading.
  - Caldas's 25 km circle holds about 1.5% of Sul de Minas's mapped coffee. Counted as severe, it
    would put the region's severe share near 8%, under the 25% flag. No regional flag changes.
- **Missing nights are common this window.**
  - Most stations have nights missing that could change their tier: 7 of 9 in Sul de Minas, 10 of
    11 in Cerrado Mineiro, 7 of 14 in Matas de Minas and 15 of 22 in São Paulo.
  - On 3 June 2026, 23 stations miss the night together. The coldest of the 28 that reported was
    8.1 °C.
  - The figures above keep those stations at the tier they reached on their observed nights.
  - Leaving them out entirely, the registered alternative, cuts coverage to 8.4%, 3.1%, 1.5% and
    0.5%. That is under the 15% floor, so **every region would be unflaggable for the 2027 crop
    on that reading.**
- **The network sees frost poorly where frost does most damage.**
  - INMET stations sit mostly on plateaus and upper slopes. Radiative frost pools in valley
    bottoms.
  - In July 2021, this station network did not flag the frost in Sul de Minas or São Paulo, the
    frost that cut the 2022 crop. The damage was concentrated in cold pools, which the network
    samples at only a few sites, Caldas among them.
  - "No flag" is a statement about what screen-height stations recorded, not proof that no coffee
    was damaged.

### The public record (attributed; separate from the station data)

{Each statement with its source and date. Do not merge with the station results above.}
- **Cooxupé:** {statement, date, link}
- **Conab, September 2026 bulletin (3rd survey of the 2026 crop):** {what it says about Jun–Aug
  2026 frost, page}
- **Somar Meteorologia:** {statement, date, link}
- **Press reports:** {outlet, date, statement}

### Next

- **The November index reading** for the 2027 crop is in the repo at {commit, date}, made before
  Conab's first survey. The first index note follows in the first week of December.
- **June–August 2027 frost** belongs to the 2028 crop and is monitored from June 2027.

**Limits:**
- The index tracks growing conditions, not yield.
- The private trade houses have field crop tours and farm data that this project does not.

*Method, station list and data: {repo link}. Station data: INMET (automatic network; conventional
network via BDMEP).*

---

## Notes for assembly (not printed)
- **Numbers to recheck after the addendum:**
  - every count, coverage share, tier and flag above;
  - "Stations counted";
  - the coldest night per region;
  - the 8% Caldas figure.
- **Coverage figures:** they are the registered headline, with unresolved stations kept at their
  observed tiers (Amendment 41b). The "left out" figures are the registered sensitivity (§5 step 4).
- **Stations in two regions:** a station whose 25 km circle reaches two regions counts in both,
  for example Itapira, Franca and Sacramento.
- **Same-site pairs:** where an automatic and a conventional station share a site, the automatic
  station governs when complete (Amendment 17d). That is why Franca, Araxá and São Paulo–Mirante's
  conventional stations are not in the counts.
- **Planet:**
  - The backtest is complete, so a 3 m figure, labelled "not an input", may go in the LinkedIn
    post and the repo copy (§4d). Never in the emailed PDF.
  - Check and record the Planet monthly area quota first (§10).
- **Outreach:** log every reply with name, firm, date and what was said (§6).
- **Sources:** Week 0 report §19; `data/derived/w2_frost_region_season.csv`;
  `data/derived/w2_frost_station_season.csv`; `docs/week0/station_set_frozen.csv`;
  `docs/week0/w2_frost_night_rule_alternative.csv`; Conab `site_previsao-de-safra-cafe-set-2026.xls`
  (arabica sheet, Brasil row).
