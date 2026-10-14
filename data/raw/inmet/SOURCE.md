# INMET automatic-station data — raw files

Files here are gitignored except this note; nothing in this folder is modified after it lands
(§9).

## Station catalogue: `catalogo_estacoes_automaticas.csv` — scraped, not downloaded

- **Source page:** https://portal.inmet.gov.br/paginas/catalogoaut ("Catálogo de Estações
  Automáticas").
- **Retrieved:** 2026-10-14 08:28:10 UTC, through the Claude desktop app's built-in browser. Scripts
  from this machine cannot reach INMET (connections are reset), and the page's "Download CSV"
  button returned nothing for the owner.
- **How:** the page's HTML table was **read from the rendered page (scraped), not downloaded as a
  file.** Each cell's displayed text was taken as-is, in the original Portuguese, untranslated
  and unconverted: comma decimals, DD/MM/YYYY dates, "Pane"/"Operante", and one altitude shown as
  "NaN" on the page. Columns, in page order: `Nome;UF;Situação;Latitude;Longitude;Altitude;Data de
  Instalação;Código`. Joined with `;` (no cell contains `;` or `"`, checked on the page), LF line
  endings, UTF-8 without BOM, trailing newline.
- **Size:** 637 lines (header plus 636 stations), 43,473 bytes.
- **SHA-256:** `34d60b087faabaaf43e160049955c2775e3fe4c5d6e95a302fa39f31e4b739db`. The same hash
  was computed in the browser on the scraped text and on the saved file, so the file is an exact
  copy of what the page displayed.
- **Limits:** the catalogue lists only stations currently registered, with their present status;
  stations closed in the past may be missing.

## Annual hourly archives `{2008…2026}.zip` — downloaded by the owner

Source: `https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip` ("Dados Históricos",
automatic stations). Sizes and Last-Modified headers as listed on 2026-10-14 are in
`docs/week0_report.md` §8. Retrieval dates and SHA-256 checksums to be added here when the files
land.
