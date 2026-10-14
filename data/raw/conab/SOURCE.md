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
