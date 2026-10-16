# Backtest v1: results

Run commit `796dd10035fe9569ccd5b7b1b1c5cb815373aeaa`; manifest SHA-256 `124cce22fdafdc9b8304cab6da3239333b5f63fbf9cebf81a4e4b262e406d4b6`; run 2026-10-16T01:23:44Z; headline frost: unresolved stations kept at their observed tiers; 8,679 rows. Numbers and pass/fail only.

Hits are condition-direction hits (sign of actual minus the stage-1 expectation). MAE is the mean absolute error of the condition anomaly in percentage points of the expectation. p-values are exact one-sided binomial tails at the observed hits, against a coin flip and against the registered majority share.

## 1. November verdicts against the pass marks (without frost)

| Region | Crops | Hits | Mark | Verdict | p (coin) | p (majority) | Registered share positive | MAE (pp) | Yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2002-2025 | 18 of 24 | 17 of 24 | pass | 0.0113 | 0.0113 | 0.500 | 15.5 | 18 of 24 |
| Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 18 of 24 | 19 of 24 | fail | 0.0113 | 0.0705 | 0.417 | 12.3 | 21 of 24 |
| Zona da Mata, Rio Doce e Central | 2009-2025 | 12 of 17 | 14 of 17 | fail | 0.0717 | 0.2320 | 0.412 | 10.3 | 12 of 17 |
| São Paulo | 2002-2025 | 17 of 24 | 18 of 24 | fail | 0.0320 | 0.0746 | 0.458 | 12.2 | 21 of 24 |
| Four-region total | 2009-2025 | 12 of 17 | 13 of 17 | fail | 0.0717 | 0.1107 | 0.471 | 10.5 | 13 of 17 |

## 2. The frost version: November verdicts with frost (crops 2009–2025)

| Region | Crops | Hits | Mark | Verdict | p (coin) | p (majority) | MAE (pp) | Without frost, same crops: hits | Without frost, same crops: MAE (pp) |
|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2009-2025 | 13 of 17 | 13 of 17 | pass | 0.0245 | 0.0418 | 14.8 | 14 of 17 | 13.6 |
| Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 14 of 17 | 13 of 17 | pass | 0.0064 | 0.0120 | 13.1 | 14 of 17 | 13.1 |
| Zona da Mata, Rio Doce e Central | 2009-2025 | 10 of 17 | 14 of 17 | fail | 0.3145 | 0.6015 | 10.8 | 12 of 17 | 10.3 |
| São Paulo | 2009-2025 | 14 of 17 | 13 of 17 | pass | 0.0064 | 0.0120 | 11.1 | 12 of 17 | 10.6 |
| Four-region total | 2009-2025 | 13 of 17 | 13 of 17 | pass | 0.0245 | 0.0418 | 10.5 | 12 of 17 | 10.5 |

- Crop 2022 is in-sample: the frost constants were set knowing what the July 2021 frost did (§5 step 6).
- Crop 2023 may carry 2021 frost effects the model does not represent (§5 step 6).

## 3. The three comparison models on identical seasons (November)

Zero anomaly: the condition anomaly predicted as 0 (the MAE baseline). Biennial only: the stage-1 expectation alone, scored on yield versus trend. Rain only: the expectation plus flowering rain alone. Every model is scored on the same region-crops as the full model.

### Without frost

| Region | Crops | Identical crops | Full: hits | Full: MAE | Full: yield vs trend | Zero anomaly: MAE | Biennial only: yield vs trend | Rain only: hits | Rain only: MAE | Rain only: yield vs trend |
|---|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2002-2025 | yes | 18 of 24 | 15.5 | 18 of 24 | 19.6 | 7 of 24 | 13 of 24 | 19.4 | 9 of 24 |
| Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | yes | 18 of 24 | 12.3 | 21 of 24 | 17.6 | 19 of 24 | 13 of 24 | 17.7 | 19 of 24 |
| Zona da Mata, Rio Doce e Central | 2009-2025 | yes | 12 of 17 | 10.3 | 12 of 17 | 9.9 | 10 of 17 | 8 of 17 | 10.0 | 10 of 17 |
| São Paulo | 2002-2025 | yes | 17 of 24 | 12.2 | 21 of 24 | 15.9 | 19 of 24 | 14 of 24 | 15.8 | 19 of 24 |
| Four-region total | 2009-2025 | yes | 12 of 17 | 10.5 | 13 of 17 | 12.7 | 12 of 17 | 9 of 17 | 12.8 | 11 of 17 |

### With frost

| Region | Crops | Identical crops | Full: hits | Full: MAE | Full: yield vs trend | Zero anomaly: MAE | Biennial only: yield vs trend | Rain only: hits | Rain only: MAE | Rain only: yield vs trend |
|---|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2009-2025 | yes | 13 of 17 | 14.8 | 13 of 17 | 17.9 | 5 of 17 | 7 of 17 | 19.1 | 7 of 17 |
| Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | yes | 14 of 17 | 13.1 | 15 of 17 | 18.6 | 13 of 17 | 10 of 17 | 17.0 | 13 of 17 |
| Zona da Mata, Rio Doce e Central | 2009-2025 | yes | 10 of 17 | 10.8 | 11 of 17 | 9.9 | 10 of 17 | 7 of 17 | 11.0 | 12 of 17 |
| São Paulo | 2009-2025 | yes | 14 of 17 | 11.1 | 12 of 17 | 14.1 | 13 of 17 | 9 of 17 | 14.2 | 13 of 17 |
| Four-region total | 2009-2025 | yes | 13 of 17 | 10.5 | 13 of 17 | 12.7 | 12 of 17 | 8 of 17 | 13.4 | 9 of 17 |

## 4. Each sensitivity against the headline on the same crops (November, full model)

Each row compares the sensitivity with the headline on exactly the sensitivity's region-crops. Third survey: the full model and the biennial-only model, because it changes the expectation.

### evi_from_sep

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2002-2025 | 24 | 24 | 16 | 18 | 17.8 | 15.5 | 15 | 18 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 24 | 24 | 16 | 18 | 16.1 | 12.3 | 21 | 21 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 9 | 12 | 11.6 | 10.3 | 12 | 12 |
| without frost | full | São Paulo | 2002-2025 | 24 | 24 | 19 | 17 | 14.3 | 12.2 | 20 | 21 |
| without frost | full | Four-region total | 2009-2025 | 17 | 17 | 12 | 12 | 11.4 | 10.5 | 11 | 13 |
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 13 | 13 | 15.7 | 14.8 | 13 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 13 | 14 | 14.7 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 11 | 10 | 11.4 | 10.8 | 11 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 13 | 14 | 12.9 | 11.1 | 12 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 12 | 13 | 10.4 | 10.5 | 13 | 13 |

### ndvi

- The NDVI series carries a 2024–26 drift of unresolved cause (Week 0 drift check); any NDVI-based result is unreliable for those years (Amendment 33).

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2002-2025 | 24 | 24 | 16 | 18 | 16.0 | 15.5 | 17 | 18 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 24 | 24 | 16 | 18 | 14.3 | 12.3 | 22 | 21 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 12 | 12 | 10.7 | 10.3 | 12 | 12 |
| without frost | full | São Paulo | 2002-2025 | 24 | 24 | 19 | 17 | 12.7 | 12.2 | 21 | 21 |
| without frost | full | Four-region total | 2009-2025 | 17 | 17 | 14 | 12 | 10.9 | 10.5 | 12 | 13 |
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 12 | 13 | 14.9 | 14.8 | 12 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 11 | 14 | 14.6 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 10 | 10 | 10.7 | 10.8 | 10 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 13 | 14 | 11.5 | 11.1 | 13 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 12 | 13 | 10.6 | 10.5 | 12 | 13 |

### no_filter

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2002-2025 | 24 | 24 | 18 | 18 | 15.5 | 15.5 | 18 | 18 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 24 | 24 | 18 | 18 | 12.3 | 12.3 | 21 | 21 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 12 | 12 | 10.3 | 10.3 | 12 | 12 |
| without frost | full | São Paulo | 2002-2025 | 24 | 24 | 18 | 17 | 12.1 | 12.2 | 21 | 21 |
| without frost | full | Four-region total | 2009-2025 | 17 | 17 | 12 | 12 | 10.5 | 10.5 | 13 | 13 |
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 13 | 13 | 14.7 | 14.8 | 13 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 14 | 14 | 13.1 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 10 | 10 | 10.8 | 10.8 | 11 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 14 | 14 | 11.0 | 11.1 | 12 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 13 | 13 | 10.5 | 10.5 | 13 | 13 |

### mapped_area

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2002-2025 | 24 | 24 | 18 | 18 | 15.7 | 15.5 | 18 | 18 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 24 | 24 | 18 | 18 | 12.2 | 12.3 | 21 | 21 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 13 | 12 | 10.0 | 10.3 | 12 | 12 |
| without frost | full | São Paulo | 2002-2025 | 24 | 24 | 18 | 17 | 12.0 | 12.2 | 21 | 21 |
| without frost | full | Four-region total | 2009-2025 | 17 | 17 | 12 | 12 | 10.5 | 10.5 | 13 | 13 |
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 13 | 13 | 14.8 | 14.8 | 13 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 14 | 14 | 13.0 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 11 | 10 | 10.5 | 10.8 | 12 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 13 | 14 | 11.2 | 11.1 | 12 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 13 | 13 | 10.5 | 10.5 | 13 | 13 |

### persistent_pixel

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2002-2025 | 24 | 24 | 18 | 18 | 15.1 | 15.5 | 18 | 18 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2002-2025 | 24 | 24 | 19 | 18 | 11.8 | 12.3 | 21 | 21 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 13 | 12 | 10.3 | 10.3 | 12 | 12 |
| without frost | full | São Paulo | 2002-2025 | 24 | 24 | 17 | 17 | 12.4 | 12.2 | 21 | 21 |
| without frost | full | Four-region total | 2009-2025 | 17 | 17 | 13 | 12 | 10.6 | 10.5 | 13 | 13 |
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 13 | 13 | 14.6 | 14.8 | 13 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 14 | 14 | 13.0 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 10 | 10 | 10.8 | 10.8 | 11 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 14 | 14 | 11.1 | 11.1 | 12 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 13 | 13 | 10.6 | 10.5 | 13 | 13 |

### chirps_prelim

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2016-2025 | 10 | 10 | 10 | 10 | 13.9 | 14.1 | 10 | 10 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2016-2025 | 10 | 10 | 8 | 9 | 13.2 | 13.6 | 10 | 10 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2016-2025 | 10 | 10 | 8 | 8 | 10.2 | 9.7 | 7 | 7 |
| without frost | full | São Paulo | 2016-2025 | 10 | 10 | 8 | 7 | 8.0 | 7.5 | 8 | 9 |
| without frost | full | Four-region total | 2016-2025 | 10 | 10 | 8 | 8 | 8.1 | 8.2 | 8 | 9 |
| with frost | full | Sul e Centro-Oeste | 2016-2025 | 10 | 10 | 10 | 10 | 14.3 | 14.5 | 10 | 10 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2016-2025 | 10 | 10 | 9 | 9 | 12.1 | 12.7 | 10 | 10 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2016-2025 | 10 | 10 | 8 | 8 | 9.9 | 9.3 | 7 | 7 |
| with frost | full | São Paulo | 2016-2025 | 10 | 10 | 9 | 9 | 8.3 | 7.6 | 8 | 8 |
| with frost | full | Four-region total | 2016-2025 | 10 | 10 | 9 | 9 | 7.2 | 7.3 | 9 | 9 |

### frost_without_unresolved

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| with frost | full | Sul e Centro-Oeste | 2009-2025 | 17 | 17 | 11 | 13 | 16.0 | 14.8 | 11 | 13 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2009-2025 | 17 | 17 | 14 | 14 | 13.8 | 13.1 | 15 | 15 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2009-2025 | 17 | 17 | 10 | 10 | 10.8 | 10.8 | 11 | 11 |
| with frost | full | São Paulo | 2009-2025 | 17 | 17 | 13 | 14 | 10.9 | 11.1 | 13 | 12 |
| with frost | full | Four-region total | 2009-2025 | 17 | 17 | 13 | 13 | 10.8 | 10.5 | 13 | 13 |

### third_survey

| Version | Model | Region | Crops | n | Headline n | Hits | Headline hits | MAE (pp) | Headline MAE (pp) | Yield vs trend hits | Headline yield vs trend hits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| without frost | full | Sul e Centro-Oeste | 2024-2025 | 2 | 2 | 2 | 2 | 10.7 | 10.7 | 2 | 2 |
| without frost | full | Triângulo, Alto Paranaíba e Noroeste | 2024-2025 | 2 | 2 | 1 | 2 | 13.0 | 10.1 | 1 | 2 |
| without frost | full | Zona da Mata, Rio Doce e Central | 2024-2025 | 2 | 2 | 2 | 2 | 10.4 | 11.6 | 2 | 2 |
| without frost | full | São Paulo | 2024-2025 | 2 | 2 | 2 | 2 | 14.4 | 14.4 | 1 | 1 |
| without frost | full | Four-region total | 2024-2025 | 2 | 2 | 1 | 1 | 6.5 | 6.3 | 1 | 1 |
| without frost | biennial only | Sul e Centro-Oeste | 2024-2025 | 2 | 2 |  |  | 18.9 | 18.9 | 1 | 1 |
| without frost | biennial only | Triângulo, Alto Paranaíba e Noroeste | 2024-2025 | 2 | 2 |  |  | 16.8 | 14.9 | 1 | 1 |
| without frost | biennial only | Zona da Mata, Rio Doce e Central | 2024-2025 | 2 | 2 |  |  | 1.8 | 0.5 | 2 | 2 |
| without frost | biennial only | São Paulo | 2024-2025 | 2 | 2 |  |  | 11.8 | 11.8 | 1 | 1 |
| without frost | biennial only | Four-region total | 2024-2025 | 2 | 2 |  |  | 8.8 | 8.4 | 0 | 1 |
| with frost | full | Sul e Centro-Oeste | 2024-2025 | 2 | 2 | 2 | 2 | 11.2 | 11.2 | 2 | 2 |
| with frost | full | Triângulo, Alto Paranaíba e Noroeste | 2024-2025 | 2 | 2 | 1 | 2 | 13.7 | 10.9 | 1 | 2 |
| with frost | full | Zona da Mata, Rio Doce e Central | 2024-2025 | 2 | 2 | 2 | 2 | 9.0 | 10.2 | 2 | 2 |
| with frost | full | São Paulo | 2024-2025 | 2 | 2 | 2 | 2 | 13.0 | 13.0 | 1 | 1 |
| with frost | full | Four-region total | 2024-2025 | 2 | 2 | 1 | 1 | 5.6 | 5.4 | 1 | 1 |
| with frost | biennial only | Sul e Centro-Oeste | 2024-2025 | 2 | 2 |  |  | 18.9 | 18.9 | 1 | 1 |
| with frost | biennial only | Triângulo, Alto Paranaíba e Noroeste | 2024-2025 | 2 | 2 |  |  | 16.8 | 14.9 | 1 | 1 |
| with frost | biennial only | Zona da Mata, Rio Doce e Central | 2024-2025 | 2 | 2 |  |  | 1.8 | 0.5 | 2 | 2 |
| with frost | biennial only | São Paulo | 2024-2025 | 2 | 2 |  |  | 11.8 | 11.8 | 1 | 1 |
| with frost | biennial only | Four-region total | 2024-2025 | 2 | 2 |  |  | 8.8 | 8.4 | 0 | 1 |

## 5. December and January beside November (headline, full model)

November decides pass or fail (Amendment 41). December and January are reported against the same marks and are not scored.

### Without frost

| Region | Mark | Nov: hits | Nov: MAE | Nov: p (coin / majority) | Nov: verdict | Dec: hits | Dec: MAE | Dec: p (coin / majority) | Dec: verdict | Jan: hits | Jan: MAE | Jan: p (coin / majority) | Jan: verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 17 of 24 | 18 of 24 | 15.5 | 0.0113 / 0.0113 | pass | 18 of 24 | 15.9 | 0.0113 / 0.0113 | not scored | 18 of 24 | 15.8 | 0.0113 / 0.0113 | not scored |
| Triângulo, Alto Paranaíba e Noroeste | 19 of 24 | 18 of 24 | 12.3 | 0.0113 / 0.0705 | fail | 20 of 24 | 12.8 | 0.0008 / 0.0088 | not scored | 19 of 24 | 12.5 | 0.0033 / 0.0277 | not scored |
| Zona da Mata, Rio Doce e Central | 14 of 17 | 12 of 17 | 10.3 | 0.0717 / 0.2320 | fail | 11 of 17 | 10.6 | 0.1662 / 0.4078 | not scored | 12 of 17 | 9.8 | 0.0717 / 0.2320 | not scored |
| São Paulo | 18 of 24 | 17 of 24 | 12.2 | 0.0320 / 0.0746 | fail | 18 of 24 | 12.3 | 0.0113 / 0.0306 | not scored | 18 of 24 | 11.8 | 0.0113 / 0.0306 | not scored |
| Four-region total | 13 of 17 | 12 of 17 | 10.5 | 0.0717 / 0.1107 | fail | 13 of 17 | 10.7 | 0.0245 / 0.0418 | not scored | 13 of 17 | 10.1 | 0.0245 / 0.0418 | not scored |

### With frost

| Region | Mark | Nov: hits | Nov: MAE | Nov: p (coin / majority) | Nov: verdict | Dec: hits | Dec: MAE | Dec: p (coin / majority) | Dec: verdict | Jan: hits | Jan: MAE | Jan: p (coin / majority) | Jan: verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 13 of 17 | 13 of 17 | 14.8 | 0.0245 / 0.0418 | pass | 13 of 17 | 15.0 | 0.0245 / 0.0418 | not scored | 13 of 17 | 15.3 | 0.0245 / 0.0418 | not scored |
| Triângulo, Alto Paranaíba e Noroeste | 13 of 17 | 14 of 17 | 13.1 | 0.0064 / 0.0120 | pass | 14 of 17 | 13.0 | 0.0064 / 0.0120 | not scored | 15 of 17 | 12.4 | 0.0012 / 0.0025 | not scored |
| Zona da Mata, Rio Doce e Central | 14 of 17 | 10 of 17 | 10.8 | 0.3145 / 0.6015 | fail | 10 of 17 | 10.8 | 0.3145 / 0.6015 | not scored | 9 of 17 | 10.3 | 0.5000 / 0.7710 | not scored |
| São Paulo | 13 of 17 | 14 of 17 | 11.1 | 0.0064 / 0.0120 | pass | 14 of 17 | 10.6 | 0.0064 / 0.0120 | not scored | 14 of 17 | 10.1 | 0.0064 / 0.0120 | not scored |
| Four-region total | 13 of 17 | 13 of 17 | 10.5 | 0.0245 / 0.0418 | pass | 12 of 17 | 11.0 | 0.0717 / 0.1107 | not scored | 12 of 17 | 10.7 | 0.0717 / 0.1107 | not scored |

## 6. Appendix

### A1. Per-region residuals under the pooled weights (headline, full model; actual minus predicted)

| Version | Vintage | Region | n | Mean signed residual (pp) | Mean absolute residual (pp) |
|---|---|---|---|---|---|
| without frost | Nov | Sul e Centro-Oeste | 24 | -0.1 | 15.5 |
| without frost | Nov | Triângulo, Alto Paranaíba e Noroeste | 24 | 1.4 | 12.3 |
| without frost | Nov | Zona da Mata, Rio Doce e Central | 17 | -3.0 | 10.3 |
| without frost | Nov | São Paulo | 24 | 0.7 | 12.2 |
| without frost | Nov | Four-region total | 17 | -3.1 | 10.5 |
| without frost | Dec | Sul e Centro-Oeste | 24 | -0.1 | 15.9 |
| without frost | Dec | Triângulo, Alto Paranaíba e Noroeste | 24 | 1.6 | 12.8 |
| without frost | Dec | Zona da Mata, Rio Doce e Central | 17 | -2.7 | 10.6 |
| without frost | Dec | São Paulo | 24 | 0.8 | 12.3 |
| without frost | Dec | Four-region total | 17 | -3.1 | 10.7 |
| without frost | Jan | Sul e Centro-Oeste | 24 | -0.0 | 15.8 |
| without frost | Jan | Triângulo, Alto Paranaíba e Noroeste | 24 | 1.6 | 12.5 |
| without frost | Jan | Zona da Mata, Rio Doce e Central | 17 | -2.8 | 9.8 |
| without frost | Jan | São Paulo | 24 | 0.7 | 11.8 |
| without frost | Jan | Four-region total | 17 | -3.2 | 10.1 |
| with frost | Nov | Sul e Centro-Oeste | 17 | 0.2 | 14.8 |
| with frost | Nov | Triângulo, Alto Paranaíba e Noroeste | 17 | 4.1 | 13.1 |
| with frost | Nov | Zona da Mata, Rio Doce e Central | 17 | -3.8 | 10.8 |
| with frost | Nov | São Paulo | 17 | 0.7 | 11.1 |
| with frost | Nov | Four-region total | 17 | -2.9 | 10.5 |
| with frost | Dec | Sul e Centro-Oeste | 17 | -0.1 | 15.0 |
| with frost | Dec | Triângulo, Alto Paranaíba e Noroeste | 17 | 4.4 | 13.0 |
| with frost | Dec | Zona da Mata, Rio Doce e Central | 17 | -3.7 | 10.8 |
| with frost | Dec | São Paulo | 17 | 0.6 | 10.6 |
| with frost | Dec | Four-region total | 17 | -3.1 | 11.0 |
| with frost | Jan | Sul e Centro-Oeste | 17 | -0.2 | 15.3 |
| with frost | Jan | Triângulo, Alto Paranaíba e Noroeste | 17 | 4.3 | 12.4 |
| with frost | Jan | Zona da Mata, Rio Doce e Central | 17 | -3.6 | 10.3 |
| with frost | Jan | São Paulo | 17 | 0.2 | 10.1 |
| with frost | Jan | Four-region total | 17 | -3.2 | 10.7 |

### A2. Crops 2022 and 2025 (headline, full model; condition anomaly in % of the expectation)

- Crop 2022 is in-sample: the frost constants were set knowing what the July 2021 frost did (§5 step 6).

| Crop | Version | Region | Actual (%) | Nov: predicted (%) | Nov: hit | Dec: predicted (%) | Dec: hit | Jan: predicted (%) | Jan: hit |
|---|---|---|---|---|---|---|---|---|---|
| 2022 | without frost | Sul e Centro-Oeste | -32.5 | -16.6 | yes | -13.4 | yes | -16.2 | yes |
| 2022 | without frost | Triângulo, Alto Paranaíba e Noroeste | -31.4 | -10.1 | yes | -8.2 | yes | -9.7 | yes |
| 2022 | without frost | Zona da Mata, Rio Doce e Central | -17.2 | -12.1 | yes | -6.2 | yes | -8.5 | yes |
| 2022 | without frost | São Paulo | -30.0 | -15.6 | yes | -13.2 | yes | -16.6 | yes |
| 2022 | without frost | Four-region total | -25.6 | -17.0 | yes | -12.9 | yes | -16.4 | yes |
| 2022 | with frost | Sul e Centro-Oeste | -32.5 | -13.9 | yes | -11.8 | yes | -13.2 | yes |
| 2022 | with frost | Triângulo, Alto Paranaíba e Noroeste | -31.4 | -41.0 | yes | -38.7 | yes | -39.3 | yes |
| 2022 | with frost | Zona da Mata, Rio Doce e Central | -17.2 | -10.7 | yes | -5.4 | yes | -6.3 | yes |
| 2022 | with frost | São Paulo | -30.0 | -13.7 | yes | -12.0 | yes | -14.4 | yes |
| 2022 | with frost | Four-region total | -25.6 | -21.2 | yes | -17.6 | yes | -19.3 | yes |
| 2025 | without frost | Sul e Centro-Oeste | -22.7 | -15.7 | yes | -12.8 | yes | -10.4 | yes |
| 2025 | without frost | Triângulo, Alto Paranaíba e Noroeste | -28.9 | -16.6 | yes | -14.7 | yes | -14.9 | yes |
| 2025 | without frost | Zona da Mata, Rio Doce e Central | -0.7 | -13.1 | yes | -8.7 | yes | -3.7 | yes |
| 2025 | without frost | São Paulo | -8.5 | -25.0 | yes | -21.8 | yes | -19.0 | yes |
| 2025 | without frost | Four-region total | -14.8 | -19.3 | yes | -15.6 | yes | -12.8 | yes |
| 2025 | with frost | Sul e Centro-Oeste | -22.7 | -14.5 | yes | -12.5 | yes | -9.8 | yes |
| 2025 | with frost | Triângulo, Alto Paranaíba e Noroeste | -28.9 | -15.3 | yes | -14.3 | yes | -13.7 | yes |
| 2025 | with frost | Zona da Mata, Rio Doce e Central | -0.7 | -11.2 | yes | -7.9 | yes | -3.7 | yes |
| 2025 | with frost | São Paulo | -8.5 | -22.7 | yes | -21.1 | yes | -18.1 | yes |
| 2025 | with frost | Four-region total | -14.8 | -17.8 | yes | -15.2 | yes | -12.2 | yes |

### A3. Double-counting check: frost-flagged region-crops, and crops 2022 and 2023 (with-frost version)

- Crop 2022 is in-sample: the frost constants were set knowing what the July 2021 frost did (§5 step 6).
- Crop 2023 may carry 2021 frost effects the model does not represent (§5 step 6).
- Sul e Centro-Oeste crop 2012's flag depends on conventional stations; whether their minima were available by the cut is not established (§9; owner, Amendment 41 item 7).

| Region | Crop | Vintage | Frost penalty (%) | Actual (%) | Predicted with frost (%) | Predicted without the frost component (%) |
|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2012 | Nov | 12.8 | 19.6 | -7.9 | 4.9 |
| Sul e Centro-Oeste | 2012 | Dec | 12.8 | 19.6 | -8.8 | 4.0 |
| Sul e Centro-Oeste | 2012 | Jan | 12.8 | 19.6 | -8.2 | 4.6 |
| Four-region total | 2012 | Nov | 5.6 | 8.3 | 1.0 | 6.6 |
| Four-region total | 2012 | Dec | 5.6 | 8.3 | -0.7 | 4.9 |
| Four-region total | 2012 | Jan | 5.6 | 8.3 | -1.0 | 4.6 |
| Sul e Centro-Oeste | 2022 | Nov | 0.0 | -32.5 | -13.9 | -13.9 |
| Sul e Centro-Oeste | 2022 | Dec | 0.0 | -32.5 | -11.8 | -11.8 |
| Sul e Centro-Oeste | 2022 | Jan | 0.0 | -32.5 | -13.2 | -13.2 |
| Triângulo, Alto Paranaíba e Noroeste | 2022 | Nov | 29.5 | -31.4 | -41.0 | -11.5 |
| Triângulo, Alto Paranaíba e Noroeste | 2022 | Dec | 29.5 | -31.4 | -38.7 | -9.3 |
| Triângulo, Alto Paranaíba e Noroeste | 2022 | Jan | 29.5 | -31.4 | -39.3 | -9.8 |
| Zona da Mata, Rio Doce e Central | 2022 | Nov | 0.0 | -17.2 | -10.7 | -10.7 |
| Zona da Mata, Rio Doce e Central | 2022 | Dec | 0.0 | -17.2 | -5.4 | -5.4 |
| Zona da Mata, Rio Doce e Central | 2022 | Jan | 0.0 | -17.2 | -6.3 | -6.3 |
| São Paulo | 2022 | Nov | 0.0 | -30.0 | -13.7 | -13.7 |
| São Paulo | 2022 | Dec | 0.0 | -30.0 | -12.0 | -12.0 |
| São Paulo | 2022 | Jan | 0.0 | -30.0 | -14.4 | -14.4 |
| Four-region total | 2022 | Nov | 5.1 | -25.6 | -21.2 | -16.0 |
| Four-region total | 2022 | Dec | 5.1 | -25.6 | -17.6 | -12.5 |
| Four-region total | 2022 | Jan | 5.1 | -25.6 | -19.3 | -14.2 |
| Sul e Centro-Oeste | 2023 | Nov | 0.0 | -10.3 | -2.4 | -2.4 |
| Sul e Centro-Oeste | 2023 | Dec | 0.0 | -10.3 | -2.1 | -2.1 |
| Sul e Centro-Oeste | 2023 | Jan | 0.0 | -10.3 | -1.6 | -1.6 |
| Triângulo, Alto Paranaíba e Noroeste | 2023 | Nov | 0.0 | 19.5 | 2.6 | 2.6 |
| Triângulo, Alto Paranaíba e Noroeste | 2023 | Dec | 0.0 | 19.5 | 0.5 | 0.5 |
| Triângulo, Alto Paranaíba e Noroeste | 2023 | Jan | 0.0 | 19.5 | 2.5 | 2.5 |
| Zona da Mata, Rio Doce e Central | 2023 | Nov | 0.0 | -11.9 | -13.5 | -13.5 |
| Zona da Mata, Rio Doce e Central | 2023 | Dec | 0.0 | -11.9 | -13.5 | -13.5 |
| Zona da Mata, Rio Doce e Central | 2023 | Jan | 0.0 | -11.9 | -14.4 | -14.4 |
| São Paulo | 2023 | Nov | 0.0 | -4.6 | 5.3 | 5.3 |
| São Paulo | 2023 | Dec | 0.0 | -4.6 | 3.7 | 3.7 |
| São Paulo | 2023 | Jan | 0.0 | -4.6 | 3.8 | 3.8 |
| Four-region total | 2023 | Nov | 0.0 | -2.1 | -2.9 | -2.9 |
| Four-region total | 2023 | Dec | 0.0 | -2.1 | -3.6 | -3.6 |
| Four-region total | 2023 | Jan | 0.0 | -2.1 | -3.0 | -3.0 |

### A4. Surprise test, safras 2023–2025 (reported, not scored; Amendment 19b)

Region-crops with both a first and a final survey: 15; revised up: 9; down: 3; flat (under 1%): 3. Revision signs: +1 up, −1 down, 0 flat.

| Version | Region | Crop | Vintage | First survey yield | Final yield | Predicted revision | Actual revision | Hit |
|---|---|---|---|---|---|---|---|---|
| without frost | Sul e Centro-Oeste | 2023 | Nov | 24.01 | 25.34 | 1 | 1 | yes |
| without frost | Sul e Centro-Oeste | 2023 | Dec | 24.01 | 25.34 | 1 | 1 | yes |
| without frost | Sul e Centro-Oeste | 2023 | Jan | 24.01 | 25.34 | 1 | 1 | yes |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Nov | 31.28 | 38.04 | 1 | 1 | yes |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Dec | 31.28 | 38.04 | 1 | 1 | yes |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Jan | 31.28 | 38.04 | 1 | 1 | yes |
| without frost | Zona da Mata, Rio Doce e Central | 2023 | Nov | 21.41 | 21.50 | -1 | 0 | flat |
| without frost | Zona da Mata, Rio Doce e Central | 2023 | Dec | 21.41 | 21.50 | -1 | 0 | flat |
| without frost | Zona da Mata, Rio Doce e Central | 2023 | Jan | 21.41 | 21.50 | -1 | 0 | flat |
| without frost | São Paulo | 2023 | Nov | 26.86 | 27.71 | 1 | 1 | yes |
| without frost | São Paulo | 2023 | Dec | 26.86 | 27.71 | 1 | 1 | yes |
| without frost | São Paulo | 2023 | Jan | 26.86 | 27.71 | 1 | 1 | yes |
| without frost | Four-region total | 2023 | Nov | 24.90 | 26.77 | 1 | 1 | yes |
| without frost | Four-region total | 2023 | Dec | 24.90 | 26.77 | 1 | 1 | yes |
| without frost | Four-region total | 2023 | Jan | 24.90 | 26.77 | 1 | 1 | yes |
| without frost | Sul e Centro-Oeste | 2024 | Nov | 26.66 | 24.66 | 1 | -1 | no |
| without frost | Sul e Centro-Oeste | 2024 | Dec | 26.66 | 24.66 | 1 | -1 | no |
| without frost | Sul e Centro-Oeste | 2024 | Jan | 26.66 | 24.66 | 1 | -1 | no |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Nov | 27.18 | 27.43 | 1 | 0 | flat |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Dec | 27.18 | 27.43 | 1 | 0 | flat |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Jan | 27.18 | 27.43 | 1 | 0 | flat |
| without frost | Zona da Mata, Rio Doce e Central | 2024 | Nov | 23.55 | 24.93 | 1 | 1 | yes |
| without frost | Zona da Mata, Rio Doce e Central | 2024 | Dec | 23.55 | 24.93 | 1 | 1 | yes |
| without frost | Zona da Mata, Rio Doce e Central | 2024 | Jan | 23.55 | 24.93 | 1 | 1 | yes |
| without frost | São Paulo | 2024 | Nov | 29.02 | 29.25 | -1 | 0 | flat |
| without frost | São Paulo | 2024 | Dec | 29.02 | 29.25 | -1 | 0 | flat |
| without frost | São Paulo | 2024 | Jan | 29.02 | 29.25 | -1 | 0 | flat |
| without frost | Four-region total | 2024 | Nov | 26.29 | 25.84 | 1 | -1 | no |
| without frost | Four-region total | 2024 | Dec | 26.29 | 25.84 | 1 | -1 | no |
| without frost | Four-region total | 2024 | Jan | 26.29 | 25.84 | 1 | -1 | no |
| without frost | Sul e Centro-Oeste | 2025 | Nov | 22.33 | 23.11 | 1 | 1 | yes |
| without frost | Sul e Centro-Oeste | 2025 | Dec | 22.33 | 23.11 | 1 | 1 | yes |
| without frost | Sul e Centro-Oeste | 2025 | Jan | 22.33 | 23.11 | 1 | 1 | yes |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Nov | 24.60 | 24.35 | 1 | -1 | no |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Dec | 24.60 | 24.35 | 1 | -1 | no |
| without frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Jan | 24.60 | 24.35 | 1 | -1 | no |
| without frost | Zona da Mata, Rio Doce e Central | 2025 | Nov | 21.90 | 23.36 | -1 | 1 | no |
| without frost | Zona da Mata, Rio Doce e Central | 2025 | Dec | 21.90 | 23.36 | -1 | 1 | no |
| without frost | Zona da Mata, Rio Doce e Central | 2025 | Jan | 21.90 | 23.36 | 1 | 1 | yes |
| without frost | São Paulo | 2025 | Nov | 23.52 | 24.18 | -1 | 1 | no |
| without frost | São Paulo | 2025 | Dec | 23.52 | 24.18 | -1 | 1 | no |
| without frost | São Paulo | 2025 | Jan | 23.52 | 24.18 | -1 | 1 | no |
| without frost | Four-region total | 2025 | Nov | 22.76 | 23.54 | -1 | 1 | no |
| without frost | Four-region total | 2025 | Dec | 22.76 | 23.54 | 1 | 1 | yes |
| without frost | Four-region total | 2025 | Jan | 22.76 | 23.54 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2023 | Nov | 24.01 | 25.34 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2023 | Dec | 24.01 | 25.34 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2023 | Jan | 24.01 | 25.34 | 1 | 1 | yes |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Nov | 31.28 | 38.04 | 1 | 1 | yes |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Dec | 31.28 | 38.04 | 1 | 1 | yes |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2023 | Jan | 31.28 | 38.04 | 1 | 1 | yes |
| with frost | Zona da Mata, Rio Doce e Central | 2023 | Nov | 21.41 | 21.50 | -1 | 0 | flat |
| with frost | Zona da Mata, Rio Doce e Central | 2023 | Dec | 21.41 | 21.50 | -1 | 0 | flat |
| with frost | Zona da Mata, Rio Doce e Central | 2023 | Jan | 21.41 | 21.50 | -1 | 0 | flat |
| with frost | São Paulo | 2023 | Nov | 26.86 | 27.71 | 1 | 1 | yes |
| with frost | São Paulo | 2023 | Dec | 26.86 | 27.71 | 1 | 1 | yes |
| with frost | São Paulo | 2023 | Jan | 26.86 | 27.71 | 1 | 1 | yes |
| with frost | Four-region total | 2023 | Nov | 24.90 | 26.77 | 1 | 1 | yes |
| with frost | Four-region total | 2023 | Dec | 24.90 | 26.77 | 1 | 1 | yes |
| with frost | Four-region total | 2023 | Jan | 24.90 | 26.77 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2024 | Nov | 26.66 | 24.66 | 1 | -1 | no |
| with frost | Sul e Centro-Oeste | 2024 | Dec | 26.66 | 24.66 | 1 | -1 | no |
| with frost | Sul e Centro-Oeste | 2024 | Jan | 26.66 | 24.66 | 1 | -1 | no |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Nov | 27.18 | 27.43 | 1 | 0 | flat |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Dec | 27.18 | 27.43 | 1 | 0 | flat |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2024 | Jan | 27.18 | 27.43 | 1 | 0 | flat |
| with frost | Zona da Mata, Rio Doce e Central | 2024 | Nov | 23.55 | 24.93 | 1 | 1 | yes |
| with frost | Zona da Mata, Rio Doce e Central | 2024 | Dec | 23.55 | 24.93 | 1 | 1 | yes |
| with frost | Zona da Mata, Rio Doce e Central | 2024 | Jan | 23.55 | 24.93 | 1 | 1 | yes |
| with frost | São Paulo | 2024 | Nov | 29.02 | 29.25 | -1 | 0 | flat |
| with frost | São Paulo | 2024 | Dec | 29.02 | 29.25 | -1 | 0 | flat |
| with frost | São Paulo | 2024 | Jan | 29.02 | 29.25 | -1 | 0 | flat |
| with frost | Four-region total | 2024 | Nov | 26.29 | 25.84 | 1 | -1 | no |
| with frost | Four-region total | 2024 | Dec | 26.29 | 25.84 | 1 | -1 | no |
| with frost | Four-region total | 2024 | Jan | 26.29 | 25.84 | 1 | -1 | no |
| with frost | Sul e Centro-Oeste | 2025 | Nov | 22.33 | 23.11 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2025 | Dec | 22.33 | 23.11 | 1 | 1 | yes |
| with frost | Sul e Centro-Oeste | 2025 | Jan | 22.33 | 23.11 | 1 | 1 | yes |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Nov | 24.60 | 24.35 | 1 | -1 | no |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Dec | 24.60 | 24.35 | 1 | -1 | no |
| with frost | Triângulo, Alto Paranaíba e Noroeste | 2025 | Jan | 24.60 | 24.35 | 1 | -1 | no |
| with frost | Zona da Mata, Rio Doce e Central | 2025 | Nov | 21.90 | 23.36 | -1 | 1 | no |
| with frost | Zona da Mata, Rio Doce e Central | 2025 | Dec | 21.90 | 23.36 | -1 | 1 | no |
| with frost | Zona da Mata, Rio Doce e Central | 2025 | Jan | 21.90 | 23.36 | 1 | 1 | yes |
| with frost | São Paulo | 2025 | Nov | 23.52 | 24.18 | -1 | 1 | no |
| with frost | São Paulo | 2025 | Dec | 23.52 | 24.18 | -1 | 1 | no |
| with frost | São Paulo | 2025 | Jan | 23.52 | 24.18 | -1 | 1 | no |
| with frost | Four-region total | 2025 | Nov | 22.76 | 23.54 | -1 | 1 | no |
| with frost | Four-region total | 2025 | Dec | 22.76 | 23.54 | 1 | 1 | yes |
| with frost | Four-region total | 2025 | Jan | 22.76 | 23.54 | 1 | 1 | yes |

### A5. Frost stations, observed coverage and penalty per region and crop (§5 step 4)

| Region | Crop | Automatic | Conventional | Unresolved | Observed coverage, headline (%) | Unflaggable, headline | Observed coverage, other variant (%) | Unflaggable, other variant | Penalty (%) |
|---|---|---|---|---|---|---|---|---|---|
| Sul e Centro-Oeste | 2009 | 7 | 6 | 6 | 22.8 | False | 11.5 | True | 0.0 |
| Sul e Centro-Oeste | 2010 | 6 | 8 | 2 | 22.8 | False | 21.7 | False | 0.0 |
| Sul e Centro-Oeste | 2011 | 6 | 8 | 2 | 30.8 | False | 29.8 | False | 0.0 |
| Sul e Centro-Oeste | 2012 | 7 | 7 | 2 | 29.1 | False | 28.3 | False | 12.8 |
| Sul e Centro-Oeste | 2013 | 6 | 5 | 3 | 23.8 | False | 22.3 | False | 0.0 |
| Sul e Centro-Oeste | 2014 | 7 | 7 | 4 | 25.4 | False | 14.3 | True | 0.0 |
| Sul e Centro-Oeste | 2015 | 7 | 7 | 1 | 25.2 | False | 24.5 | False | 0.0 |
| Sul e Centro-Oeste | 2016 | 6 | 7 | 3 | 24.5 | False | 23.9 | False | 0.0 |
| Sul e Centro-Oeste | 2017 | 6 | 7 | 1 | 18.4 | False | 18.2 | False | 0.0 |
| Sul e Centro-Oeste | 2018 | 8 | 5 | 6 | 26.7 | False | 12.1 | True | 0.0 |
| Sul e Centro-Oeste | 2019 | 11 | 4 | 4 | 29.3 | False | 19.3 | False | 0.0 |
| Sul e Centro-Oeste | 2020 | 9 | 3 | 2 | 28.1 | False | 19.0 | False | 0.0 |
| Sul e Centro-Oeste | 2021 | 10 | 2 | 2 | 28.1 | False | 27.9 | False | 0.0 |
| Sul e Centro-Oeste | 2022 | 9 | 2 | 2 | 23.7 | False | 23.3 | False | 0.0 |
| Sul e Centro-Oeste | 2023 | 10 | 1 | 5 | 22.2 | False | 11.9 | True | 0.0 |
| Sul e Centro-Oeste | 2024 | 11 | 2 | 6 | 28.7 | False | 18.4 | False | 0.0 |
| Sul e Centro-Oeste | 2025 | 10 | 3 | 5 | 28.1 | False | 18.8 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2009 | 8 | 3 | 8 | 23.4 | False | 3.9 | True | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2010 | 9 | 3 | 1 | 23.6 | False | 23.1 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2011 | 9 | 4 | 5 | 23.5 | False | 21.1 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2012 | 8 | 4 | 4 | 23.7 | False | 20.4 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2013 | 8 | 4 | 3 | 24.6 | False | 21.3 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2014 | 8 | 4 | 2 | 24.4 | False | 21.4 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2015 | 8 | 4 | 1 | 24.6 | False | 21.6 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2016 | 7 | 4 | 0 | 24.3 | False | 24.3 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2017 | 6 | 2 | 2 | 21.2 | False | 17.8 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2018 | 8 | 1 | 4 | 7.6 | True | 0.6 | True | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2019 | 9 | 1 | 4 | 24.9 | False | 18.1 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2020 | 11 | 1 | 6 | 25.2 | False | 18.0 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2021 | 9 | 1 | 2 | 21.4 | False | 18.3 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2022 | 6 | 1 | 3 | 24.6 | False | 18.0 | False | 29.5 |
| Triângulo, Alto Paranaíba e Noroeste | 2023 | 8 | 0 | 5 | 24.9 | False | 18.1 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2024 | 8 | 1 | 3 | 24.8 | False | 21.4 | False | 0.0 |
| Triângulo, Alto Paranaíba e Noroeste | 2025 | 11 | 1 | 4 | 25.1 | False | 21.8 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2009 | 12 | 7 | 14 | 35.7 | False | 26.0 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2010 | 12 | 8 | 5 | 35.8 | False | 34.5 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2011 | 11 | 10 | 5 | 35.5 | False | 27.0 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2012 | 12 | 9 | 4 | 35.2 | False | 35.2 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2013 | 14 | 7 | 10 | 52.2 | False | 42.8 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2014 | 15 | 7 | 4 | 51.6 | False | 34.4 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2015 | 13 | 9 | 2 | 50.7 | False | 50.6 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2016 | 16 | 10 | 4 | 51.1 | False | 51.0 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2017 | 15 | 9 | 8 | 50.6 | False | 13.3 | True | 0.0 |
| Zona da Mata, Rio Doce e Central | 2018 | 12 | 6 | 6 | 33.6 | False | 33.4 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2019 | 13 | 8 | 2 | 50.3 | False | 50.3 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2020 | 14 | 3 | 4 | 33.4 | False | 33.0 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2021 | 11 | 6 | 2 | 49.1 | False | 49.1 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2022 | 12 | 4 | 4 | 48.9 | False | 48.5 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2023 | 12 | 3 | 1 | 44.1 | False | 27.8 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2024 | 16 | 3 | 2 | 48.9 | False | 48.4 | False | 0.0 |
| Zona da Mata, Rio Doce e Central | 2025 | 16 | 3 | 6 | 48.7 | False | 5.0 | True | 0.0 |
| São Paulo | 2009 | 13 | 7 | 13 | 21.1 | False | 2.9 | True | 0.0 |
| São Paulo | 2010 | 12 | 9 | 6 | 21.4 | False | 17.1 | False | 0.0 |
| São Paulo | 2011 | 13 | 9 | 6 | 24.7 | False | 23.3 | False | 0.0 |
| São Paulo | 2012 | 14 | 5 | 7 | 23.1 | False | 18.4 | False | 0.0 |
| São Paulo | 2013 | 16 | 2 | 6 | 18.8 | False | 1.6 | True | 0.0 |
| São Paulo | 2014 | 17 | 1 | 6 | 23.3 | False | 5.8 | True | 0.0 |
| São Paulo | 2015 | 18 | 2 | 6 | 22.9 | False | 19.1 | False | 0.0 |
| São Paulo | 2016 | 16 | 2 | 3 | 21.6 | False | 20.5 | False | 0.0 |
| São Paulo | 2017 | 21 | 1 | 3 | 27.7 | False | 11.3 | True | 0.0 |
| São Paulo | 2018 | 23 | 1 | 11 | 31.9 | False | 3.1 | True | 0.0 |
| São Paulo | 2019 | 19 | 2 | 3 | 29.9 | False | 14.9 | True | 0.0 |
| São Paulo | 2020 | 22 | 1 | 2 | 28.0 | False | 27.8 | False | 0.0 |
| São Paulo | 2021 | 20 | 0 | 3 | 27.0 | False | 11.9 | True | 0.0 |
| São Paulo | 2022 | 13 | 0 | 5 | 20.9 | False | 4.8 | True | 0.0 |
| São Paulo | 2023 | 20 | 1 | 8 | 27.6 | False | 7.4 | True | 0.0 |
| São Paulo | 2024 | 25 | 1 | 9 | 30.7 | False | 10.8 | True | 0.0 |
| São Paulo | 2025 | 21 | 1 | 11 | 31.7 | False | 19.4 | False | 0.0 |
| Four-region total | 2009 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2010 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2011 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2012 |  |  |  |  |  |  |  | 5.6 |
| Four-region total | 2013 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2014 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2015 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2016 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2017 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2018 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2019 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2020 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2021 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2022 |  |  |  |  |  |  |  | 5.1 |
| Four-region total | 2023 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2024 |  |  |  |  |  |  |  | 0.0 |
| Four-region total | 2025 |  |  |  |  |  |  |  | 0.0 |

### A6. Fitted λ, intercept and weights per fold (headline, full model, November)

Weights are per unit of each registered input as stored in the season inputs.

| Version | Held-out crop | λ | Intercept | Training rows | w evi | w rain_flowering | w soil_moisture | w heat_days |
|---|---|---|---|---|---|---|---|---|
| without frost | 2002 | 0.1 | 0.0167 | 83 | 0.1733 | -0.0509 | -0.0177 | -0.0460 |
| without frost | 2003 | 1.77828 | 0.0018 | 83 | 0.1640 | -0.0277 | -0.0214 | -0.0281 |
| without frost | 2004 | 5.62341 | 0.0186 | 83 | 0.1171 | -0.0295 | 0.0219 | -0.0386 |
| without frost | 2005 | 3.16228 | 0.0022 | 83 | 0.1335 | -0.0369 | 0.0088 | -0.0341 |
| without frost | 2006 | 3.16228 | 0.0180 | 83 | 0.1385 | -0.0315 | -0.0052 | -0.0436 |
| without frost | 2007 | 1.77828 | 0.0045 | 83 | 0.1503 | -0.0320 | -0.0121 | -0.0364 |
| without frost | 2008 | 3.16228 | 0.0134 | 82 | 0.1466 | -0.0344 | -0.0013 | -0.0392 |
| without frost | 2009 | 1.77828 | -0.0019 | 81 | 0.1620 | -0.0302 | -0.0085 | -0.0391 |
| without frost | 2010 | 3.16228 | 0.0106 | 81 | 0.1469 | -0.0333 | -0.0059 | -0.0414 |
| without frost | 2011 | 3.16228 | -0.0070 | 81 | 0.1530 | -0.0349 | -0.0060 | -0.0323 |
| without frost | 2012 | 3.16228 | 0.0003 | 81 | 0.1406 | -0.0339 | -0.0069 | -0.0369 |
| without frost | 2013 | 1.77828 | 0.0012 | 81 | 0.1582 | -0.0409 | -0.0054 | -0.0459 |
| without frost | 2014 | 1.77828 | 0.0070 | 81 | 0.1635 | -0.0423 | -0.0047 | -0.0418 |
| without frost | 2015 | 0 | -0.0053 | 81 | 0.1619 | -0.0406 | -0.0242 | -0.0445 |
| without frost | 2016 | 0.177828 | 0.0092 | 81 | 0.1645 | -0.0408 | -0.0279 | -0.0475 |
| without frost | 2017 | 1.77828 | -0.0116 | 81 | 0.1521 | -0.0307 | -0.0072 | -0.0315 |
| without frost | 2018 | 1.77828 | 0.0113 | 81 | 0.1617 | -0.0318 | -0.0082 | -0.0282 |
| without frost | 2019 | 3.16228 | -0.0097 | 81 | 0.1452 | -0.0320 | -0.0040 | -0.0402 |
| without frost | 2020 | 1.77828 | 0.0167 | 81 | 0.1626 | -0.0343 | -0.0189 | -0.0310 |
| without frost | 2021 | 5.62341 | 0.0118 | 81 | 0.1276 | -0.0212 | -0.0011 | -0.0231 |
| without frost | 2022 | 5.62341 | 0.0122 | 81 | 0.1198 | -0.0215 | 0.0045 | -0.0303 |
| without frost | 2023 | 1.77828 | 0.0096 | 81 | 0.1677 | -0.0376 | -0.0114 | -0.0325 |
| without frost | 2024 | 0.177828 | 0.0115 | 81 | 0.1687 | -0.0380 | -0.0140 | -0.0376 |
| without frost | 2025 | 1.77828 | 0.0027 | 85 | 0.1453 | -0.0351 | -0.0001 | -0.0401 |
| with frost | 2009 | 5.62341 | 0.0330 | 60 | 0.0842 | -0.0324 | 0.0258 | -0.0398 |
| with frost | 2010 | 10 | 0.0393 | 60 | 0.0885 | -0.0319 | 0.0194 | -0.0380 |
| with frost | 2011 | 10 | 0.0237 | 60 | 0.0975 | -0.0283 | 0.0189 | -0.0279 |
| with frost | 2012 | 10 | 0.0242 | 60 | 0.0974 | -0.0280 | 0.0111 | -0.0313 |
| with frost | 2013 | 3.16228 | 0.0336 | 60 | 0.1090 | -0.0462 | 0.0181 | -0.0517 |
| with frost | 2014 | 3.16228 | 0.0418 | 60 | 0.1142 | -0.0456 | 0.0194 | -0.0437 |
| with frost | 2015 | 1.77828 | 0.0265 | 60 | 0.1148 | -0.0412 | -0.0048 | -0.0436 |
| with frost | 2016 | 3.16228 | 0.0411 | 60 | 0.1194 | -0.0393 | -0.0109 | -0.0467 |
| with frost | 2017 | 5.62341 | 0.0181 | 60 | 0.1149 | -0.0259 | 0.0106 | -0.0274 |
| with frost | 2018 | 5.62341 | 0.0472 | 60 | 0.1130 | -0.0291 | 0.0147 | -0.0271 |
| with frost | 2019 | 5.62341 | 0.0208 | 60 | 0.0954 | -0.0305 | 0.0191 | -0.0402 |
| with frost | 2020 | 10 | 0.0551 | 60 | 0.0892 | -0.0303 | 0.0124 | -0.0271 |
| with frost | 2021 | 10 | 0.0427 | 60 | 0.0816 | -0.0253 | 0.0213 | -0.0270 |
| with frost | 2022 | 10 | 0.0438 | 60 | 0.0688 | -0.0266 | 0.0279 | -0.0369 |
| with frost | 2023 | 5.62341 | 0.0473 | 60 | 0.1164 | -0.0358 | 0.0094 | -0.0331 |
| with frost | 2024 | 0.562341 | 0.0492 | 60 | 0.1410 | -0.0390 | -0.0030 | -0.0371 |
| with frost | 2025 | 1.77828 | 0.0314 | 64 | 0.1212 | -0.0344 | 0.0120 | -0.0376 |

### A7. CHIRPS prelim rerun: municipality-seasons substituted per held-out crop and vintage

| Held-out crop | Vintage | Municipalities on prelim | Left on final (no prelim row) |
|---|---|---|---|
| 2016 | Nov | 930 | 0 |
| 2016 | Dec | 930 | 0 |
| 2016 | Jan | 0 | 0 |
| 2017 | Nov | 930 | 0 |
| 2017 | Dec | 930 | 0 |
| 2017 | Jan | 0 | 0 |
| 2018 | Nov | 931 | 0 |
| 2018 | Dec | 931 | 0 |
| 2018 | Jan | 0 | 0 |
| 2019 | Nov | 936 | 0 |
| 2019 | Dec | 936 | 0 |
| 2019 | Jan | 0 | 0 |
| 2020 | Nov | 941 | 0 |
| 2020 | Dec | 941 | 0 |
| 2020 | Jan | 0 | 0 |
| 2021 | Nov | 941 | 0 |
| 2021 | Dec | 941 | 0 |
| 2021 | Jan | 0 | 0 |
| 2022 | Nov | 942 | 0 |
| 2022 | Dec | 942 | 0 |
| 2022 | Jan | 0 | 0 |
| 2023 | Nov | 954 | 0 |
| 2023 | Dec | 954 | 0 |
| 2023 | Jan | 0 | 0 |
| 2024 | Nov | 955 | 0 |
| 2024 | Dec | 955 | 0 |
| 2024 | Jan | 0 | 0 |
| 2025 | Nov | 957 | 0 |
| 2025 | Dec | 957 | 0 |
| 2025 | Jan | 0 | 0 |

### A8. Changes after `prereg-1` (§9): SPEC_CHANGELOG headings

- 2026-10-15: AMENDMENT 37: §10 still-open items 2 and 4 closed, as decided at `prereg-1`.
- 2026-10-15: AMENDMENT 38: scorable season sets, the two-step stage-1 fit, and the registered direction pass marks.
- 2026-10-15: AMENDMENT 39: elevation cut fixed once per region; night rule cited in part; three stations added to the BDMEP re-request.
- 2026-10-15: AMENDMENT 39b (correction after `prereg-2`): the conventional stations already in the BDMEP zip were left untested.
- 2026-10-15: AMENDMENT 40: frost night-rule sensitivity; note 1 reports readings outside the rule; the Planet frost case study first; MODIS night LST for v2.
- 2026-10-15: AMENDMENT 41: backtest decisions before the single run.
- 2026-10-15: AMENDMENT 41b: headline frost reversed to "unresolved stations kept at their observed tiers"; "left out" is the registered sensitivity.
