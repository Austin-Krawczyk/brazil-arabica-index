# Brazil Arabica Condition Index

A public, reproducible growing-conditions index for Brazil's arabica belt, built from free
satellite and weather data in Google Earth Engine.

**This is a condition index, not a yield forecast.** It answers one question each month: are
growing conditions in each arabica region better, worse or in line with the baseline, and what
does that imply for the crop relative to Conab and the private estimates. It does not predict a
number of bags, and it is not a trading signal.

Scope, method, data sources and the rules this project is built under are in [CLAUDE.md](CLAUDE.md).
Every change of scope, with its reason and date, is in [SPEC_CHANGELOG.md](SPEC_CHANGELOG.md).

Status: **Week 0.** Spec adopted 2026-10-12 after review. Nothing computed yet.

## Known limits, stated up front

- The index tracks conditions, not yield.
- The private trade houses have field crop tours and farm data that this project does not.
- MODIS at 250 m blurs smallholder terrain, so Zona da Mata skill is expected to be the weakest
  of the four regions. Regional skill is reported separately rather than averaged away.
- Frost is anchored on INMET station observations; ERA5-Land fills space between stations and is
  not trusted on its own, because it was the weakest of five products at station minima in a
  previous study by the same author.
