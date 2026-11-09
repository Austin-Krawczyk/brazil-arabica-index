# Pre-registration 4: the price test (`prereg-4`)

**Status: registered 2026-11-09, tagged `prereg-4`.** It was registered before any price data
was read.

**Owner decisions (2026-11-09), resolving the draft's two open points:**
1. **Sign:** negative, through the supply channel.
2. **Sample:**
   - **primary:** the four-region total, crops 2009–2025, **17 observations**;
   - **reported comparison:** Sul e Centro-Oeste, crops 2002–2025, **24 observations**.
   - The owner's first wording ("crops 2002–2025, 24 observations") could not hold for the
     four-region total. Its November reading exists only from crop 2009: Zona da Mata's target
     series, and so the total's, begins with crop 2008, and stage 1 needs the previous crop.

## Scope

- **Outside v1.** §3 puts price forecasting and trading strategy out of scope for v1, and §5 leaves
  any translation of the index into a price forecast until v2.
  - This registration changes nothing in the v1 spec, in `prereg-1`, `prereg-2` or `prereg-3`, or
    in any frozen file.
  - It registers one association test. It is not a price forecast, a trading rule, or a pass/fail
    test of the index.
- **Registered before any price data was read.**
  - No price file exists in the repository, and none has been fetched.
  - The owner and the agent have general knowledge of past coffee price moves, for example the 2021
    frost rally. No price series has been read or computed for this test.

## Hypothesis

**H:** the November four-region condition anomaly is **negatively** associated with the subsequent
ICE arabica futures return.

**Channel:** a positive condition anomaly means better growing conditions than the stage-1
expectation, so more coffee and a lower subsequent price.

## Predictor (frozen; not recomputed)

- **x_S:** the November-vintage reading of the four-region total's condition anomaly for crop S,
  without frost (the version scored on every crop it covers).
  - It is in percentage points of the stage-1 expectation.
  - It is the held-out (leave-one-season-out) prediction of the v1 backtest.
- **Source:** `data/derived/backtest_results_v1.csv`, SHA-256
  `a966877dfa60d64dc079d9c7e73dbd29ee66f521e85f6b5c714b9dce0a047ffa` (Week 0 report §23).
  - Rows: `sensitivity` = headline, `model` = full, `version` = no_frost, `vintage` = Nov, `region` =
    Four-region total.
  - Column: `a_pred` × 100.
- **Crops:** 2009–2025, **17 observations** (primary).
- **Timing:** each reading is made as of the November cut, 20 November of S−1. That is before the
  return window opens.

## Outcome (defined before any fetch)

- **Contract:** ICE Futures U.S. Coffee "C" futures (exchange code KC), the **July contract of year
  S**.
- **Why July, not May:** ICE's Coffee "C" rules (Chapter 8, Rule 8.01, definitions 9 and 10; read
  2026-10-18; the rulebook contains no prices) settle it.
  - The Last Notice Day is the seventh business day before the last business day of the delivery
    month.
  - The Last Trading Day is the business day before the Last Notice Day.
  - So the May contract always stops trading before the end of May, and the July contract is the
    nearest contract still trading on the last trading day of May.
  - Contracts are listed up to 59 months ahead (Rule 8.05), so the July contract of year S trades
    throughout the window.
- **Price:** ICE's official daily settlement price for that contract, in US cents per pound.
- **Start:** the settlement on the first ICE Futures U.S. trading day of December of year S−1.
- **End:** the settlement on the last ICE Futures U.S. trading day of May of year S.
- **Return:** r_S = ln(P_end / P_start).
  - Windows do not overlap across crops.
  - Each window opens after that crop's November cut.
- **Source:** ICE Futures U.S. official daily settlement prices (Intercontinental Exchange).
  - The owner retrieves them.
  - The retrieval route, date and SHA-256 go in `data/raw/ice/SOURCE.md` before any return is
    computed.
- **Settlements needed:** two per crop.
  - Crops 2002–2025 for all tests together: 48.
  - The primary test, crops 2009–2025: 34 of them.
- **Missing data:**
  - If the named source cannot supply all 34 settlements for the primary test, the test is not
    run, and that is reported.
  - A comparison runs only if every settlement for its crops is available. Otherwise it is
    reported as not run.
  - No substitute source and no imputation, unless a logged amendment to this registration is
    committed before any price is read.
- **Redistribution (§4):**
  - ICE data stay out of committed files until ICE's redistribution terms are checked. The prices
    live in `data/raw/ice/`, which is gitignored.
  - The committed output is the regression statistics. The per-crop returns are committed only after
    the check.
- **Contract changes:**
  - ICE is phasing out Coffee "C" for a new arabica contract and lists nothing beyond March 2028
    (rulebook notice). This does not affect the registered crops. Any extension to later crops needs
    its own registration.
  - Changes to the contract's deliverable growths and differentials within the registered window are
    not adjusted for.

## Method

- **One ordinary least-squares regression,** with an intercept, over the registered crops:
  r_S = α + β·x_S + ε_S.
- **Reported:**
  - β, in log return per percentage point of condition anomaly;
  - its sign;
  - its 95% confidence interval, from the classical OLS standard error and the t distribution on
    n − 2 degrees of freedom;
  - R²;
  - n;
  - α.
- **Three reported comparisons, unscored, with the same regression and the same statistics:**
  1. **The with-frost version's November reading** for the four-region total (`version` =
     with_frost).
     - Crops 2009–2025, **17 observations**.
     - Crop 2022 is in-sample for the frost version.
  2. **The December-vintage reading without frost** for the four-region total (`vintage` = Dec).
     - Crops 2009–2025, **17 observations**.
     - It is made as of 1 December of S−1. The window opens on the first trading day of December,
       which can be 1 December itself.
  3. **Sul e Centro-Oeste's November reading without frost** (`region` = Sul e Centro-Oeste).
     - Crops 2002–2025, **24 observations**.
     - Same source file, rows and column as the primary predictor.
     - Its returns for crops 2002–2008 come from the same contract rule.
     - Owner decision, 2026-11-09.
- **Nothing else:**
  - no other specification, transformation, lag, control or subsample;
  - no outlier removal and no robustness variant;
  - no optimisation and no trading rule.

## Pass criterion

- **None.** The result is reported whatever it is, in one table, with this document's commit and
  tag.
- **What the table holds:** the primary test (n = 17) and the three comparisons (n = 17, 17 and
  24), each with β, sign, interval, R² and n.
- **Wording of the result:**
  - whether the sign agrees with H (negative);
  - whether the 95% interval excludes zero.
- Nothing more is inferred.

## Guard

- **`gee/prereg4_guard.py`** stops any script from reading price data unless all of these hold:
  - this document is committed at HEAD, with the working copy unchanged;
  - it has no open point left;
  - the tag `prereg-4` exists and is an ancestor of HEAD.
- **`gee/check_prereg4_guard.py`** fails if a `gee/` script that refers to price data does not call
  the guard.

## Not yet

Prices are not fetched until the owner says go (owner, 2026-10-18).
