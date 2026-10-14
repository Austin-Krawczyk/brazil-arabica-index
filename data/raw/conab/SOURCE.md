# Conab coffee surveys — raw files

The start of the §4c extraction: Conab's survey bulletins and data tables, kept unmodified. Files
are gitignored; this note and its checksums are committed.

| File | Source URL | Retrieved | Bytes | SHA-256 |
|---|---|---|---|---|
| `boletim-de-safras-cafe-set_26.pdf` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2026/boletim-de-safras-cafe-set_26.pdf | 2026-10-13 11:45 PDT | 1,066,462 | `03bd1828fbd0cd8e66b4ddc66b1404ccf77877f82483242012aab829b8427a62` |
| `site_previsao-de-safra-cafe-set-2026.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2026/site_previsao-de-safra-cafe-set-2026.xls | 2026-10-13 11:46 PDT | 526,848 | `708c86c054f62fda4374647a65b6c2ea34ffe549d3af32234fa3fbabb16bdf88` |

**What they are:** the 3rd survey of safra 2026 (Acompanhamento da Safra Brasileira de Café, v.13,
n.3, September 2026), published 24 September 2026. The table's sheet "2 Café Arábica" gives arabica
area in production (ha), yield (sc/ha) and production (thousand bags) for safra 2025 and 2026, by
Minas Gerais region (Sul e Centro-Oeste; Triângulo, Alto Paranaíba e Noroeste; Zona da Mata, Rio
Doce e Central; Norte, Jequitinhonha e Mucuri) and by state, with São Paulo as a state total.

**How they were obtained:** read through the web-fetch tool while checking Conab's regional
definitions on 2026-10-13, which cached the files in the session folder; copied here unchanged on
2026-10-14. The checksums are of the files as cached.

**Survey vintage:** every value extracted from these files is recorded with this vintage (3rd
survey, safra 2026, 24 September 2026), as §4c requires.

## §4c extraction, 2026-10-14: what Conab serves, and what was retrieved

**Where Conab's coffee surveys are, and are not:**

- **gov.br lists Conab's coffee surveys from safra 2023 only:** all four surveys each for
  2023–2025, and surveys 1–3 for 2026. Listing page:
  https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/safra-de-cafe-1
  (two pages). Each survey page links a bulletin (PDF) and a data table (XLS).
- **Safras 2001–2022: not located.**
  - Conab's old portal (`www.conab.gov.br/info-agro/safras/cafe/boletim-da-safra-de-cafe`) now
    redirects to the gov.br home page.
  - The gov.br site search returns no coffee survey before 2023.
  - The Internet Archive's index refused the one query sent (HTTP 429, rate limit) and was not
    queried again. Whether archived copies exist is not established.
  - Whether to use archived copies at all is an owner decision.
- **Historical series:** Conab publishes series by product at
  https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/series-historicas/cafe
  (arabica, conilon, total, coffee-tree park). Each is a single vintage: the latest revised values,
  released with the September 2026 estimate.

**Retrieved 2026-10-14** by script (`gee/conab_fetch.py` for the survey tables, `curl` for the
series), one file at a time:

| File | Source URL | Retrieved (UTC) | Bytes | SHA-256 |
|---|---|---|---|---|
| `cafearabicaseriehist.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/series-historicas/cafe/arabica/cafearabicaseriehist.xls | 2026-10-14 14:14:33 | 59,392 | `d18f5e28f157ae185ab42f291acbf32e6b462f2ef03291999719d17fe7d602be` |
| `cafetotalseriehist.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/series-historicas/cafe/total-arabica-e-conilon/cafetotalseriehist.xls | 2026-10-14 14:15:22 | 69,632 | `6643081b7d7b093b33917b0ab9acde692c02c3683f36faebf3a036dd89a410c0` |
| `conab_cafe_safra2023_lev1.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/1o-levantamento-de-cafe-safra-2023/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:11 | 498,176 | `110fedb5201a36eaffe448dbc5da87c781699d0f61712929a914ab80391bedbf` |
| `conab_cafe_safra2023_lev3.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2023/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:17 | 503,296 | `539f6d71f07fe20fb2c3846aea4b0193314350ce439d55d6f42e4fbab736b1a2` |
| `conab_cafe_safra2023_lev4.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/4o-levantamento-de-cafe-safra-2023/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:23 | 508,928 | `f1e2e095cc2afa1fef210756764cd4828fbde3e0e9ddd1f5d49c897899421a52` |
| `conab_cafe_safra2024_lev1.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/1o-levantamento-de-cafe-safra-2024/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:29 | 498,176 | `ce82f8c47ea66172227abc99c6b84cd74bfd9f15c3cbca8c1f0c30d3b3154851` |
| `conab_cafe_safra2024_lev3.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2024/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:35 | 551,936 | `6b9d088d7c6383898e9188f5107d2c69a28fff08aab82a7d0c0a038806b07e5c` |
| `conab_cafe_safra2024_lev4.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/4o-levantamento-de-cafe-safra-2024/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:41 | 507,392 | `dcfcf3b9bc88bf45202cbfe829e3707d33344feadafec1da32f82e3b01c37cbf` |
| `conab_cafe_safra2025_lev1.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/1o-levantamento-de-cafe-safra-2025/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:47 | 508,416 | `41ebce0819983e393da6a55111cea4fd813dc4be2773ba1c05c5d823d4571cd9` |
| `conab_cafe_safra2025_lev3.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2025/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:19:54 | 513,024 | `759347545251bf471220055560432d8395df378e909ad75b68d83621d237029c` |
| `conab_cafe_safra2025_lev4.xls` | https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/4o-levantamento-de-cafe-safra-2025/tabela-de-dados-estimativas-da-producao-e-colheita | 2026-10-14 14:20:00 | 513,024 | `5f7947d52c7a5973aba0e5513487f59ebaaa27d39e29ab3632e0ed5629b48379` |

- **Survey tables:**
  - The server sends no file name, so each table is named here by safra and survey ("lev" =
    levantamento).
  - A header request gets HTTP 403 from gov.br; a plain GET works.
  - The bulletins (PDFs) on the same pages were located but not downloaded: the tables carry the
    same regional figures.
- **Survey dates:** taken from the bulletin names on Conab's pages:
  - safra 2023: January, September, December 2023;
  - safra 2024: January 2024, September 2024, January 2025;
  - safra 2025: January, September, December 2025.
