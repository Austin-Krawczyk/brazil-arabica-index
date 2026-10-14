# Pre-registration

Every choice that could be tuned, recorded before the results that could tempt a change (§9,
Amendment 15). Two tagged commits fix it:

- **`prereg-1`**, before W2 computes any season-level input.
- **`prereg-2`**, before the first backtest run: values that need data but not results.

Entries are added as they are decided. **Neither tag has been applied yet.** Any change after an
entry's tag is logged in `SPEC_CHANGELOG.md` and listed in the backtest report.

## prereg-1 — to be fixed before W2 (not yet tagged)

| Item | Value | Source | Status |
|---|---|---|---|
| Feature list, windows, standardisation | EVI anomaly; flowering rain deficit (Sep–Nov S−1); dry-season root-zone soil moisture (May–Aug S−1); heat days in flowering. NDVI, dry days and bean-fill rain reported, not fitted | §5 steps 2–6, Amendment 19 | values decided; standardisation details pending |
| EVI as the single vegetation term | EVI, because NDVI saturates in dense coffee canopies | Amendment 19 | decided |
| ERA5-Land soil-layer weights | 0.07 / 0.21 / 0.72 (layers 1–3, by thickness) | Amendment 28 | decided |
| Weighting method; terms counted toward the cap of four | stage-2 ridge on four pooled weights; stage 1 not counted | Amendment 19 | decided |
| Ridge penalty grid | — | §5 step 6 | **pending** |
| Direction pass marks | 18 of 25 (no frost, 2001–2025); 13 of 17 (frost, 2009–2025) | Amendment 19 | decided |
| Frost tier constants (values) | thresholds 2 °C and 0 °C; per-tier yield penalties | Amendments 13, 17 | thresholds decided; **penalty values pending** |

## prereg-2 — to be fixed before the first backtest run (not yet tagged)

| Item | Value | Source | Status |
|---|---|---|---|
| **Region membership** | `docs/week0/proposed_region_membership.csv`: Sul e Centro-Oeste = Sul/Sudoeste + Oeste de Minas (190 municipalities); Triângulo, Alto Paranaíba e Noroeste = Triângulo Mineiro/Alto Paranaíba + Noroeste de Minas (85); Zona da Mata, Rio Doce e Central = Zona da Mata + Vale do Rio Doce + Central Mineira + Campo das Vertentes + Metropolitana de BH (415); São Paulo = all 645 municipalities. Norte, Jequitinhonha e Mucuri (163) outside the index | Conab bulletin, 3rd survey 2026 (1989 mesoregions); Amendment 34 | **registered, provisional.** Campo das Vertentes and Metropolitana de BH by area fit: PAM 2025 against Conab 2025, +3.1% (Sul e Centro-Oeste) and −8.5% (Zona da Mata, Rio Doce e Central), against +7.8% and −16.1% the other way. An answer from Conab's MG office before the tag supersedes this |
| **São Paulo target (§4c)** | São Paulo state total, as the Mogiana target | Conab 3rd survey 2026 table: SP reported only as a state total; Amendment 34 | **registered** |
| Mask lag and masks | full class-46 and persistent-pixel masks | Amendments 16, 16b | pending |
| Station list per region, altitude cut, maximum attainable frost coverage | — | §5 step 4, Amendment 17 | pending (INMET data) |
| Surprise-test pass mark | from Conab's base rate | Amendment 12 | pending (Conab extraction) |
| Base-rate check on the direction pass marks | — | Amendment 19 | pending |
| Frost tier constant sources | — | Amendment 15 | pending |
