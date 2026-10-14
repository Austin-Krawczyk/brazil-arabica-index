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

- **Source:** `https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip` ("Dados Históricos",
  automatic stations). The 2026 archive runs to 30 September 2026.
- **Downloaded** by the owner on 2026-10-14, from their own browser. The times below are the files'
  modification times, as a proxy for download time.
- **Checked 2026-10-14:** every file's size matches the `Content-Length` INMET's server reported
  that day (`docs/week0_report.md` §8); every archive passes a full zip integrity test (each member
  read and its CRC checked).

| File | Bytes | SHA-256 | Station CSVs | Zip test | File time (download) |
|---|---|---|---|---|---|
| `2008.zip` | 75,952,778 | `51335b3d39558534cd873e5bade879ad289373876b9e8d633989479ef42ebf8b` | 417 | OK | 2026-10-14 08:40 UTC |
| `2009.zip` | 88,288,168 | `55ed08f3cb319488049e69860b89b5c05a8089b73ed196172fa1307ce10880c6` | 434 | OK | 2026-10-14 08:43 UTC |
| `2010.zip` | 90,166,397 | `a665f207d0c95bcbf352fe6c91a52f8466ac12220a4f354c23e6a7835a8bac58` | 446 | OK | 2026-10-14 08:42 UTC |
| `2011.zip` | 92,552,099 | `420a488a5d3b63bbbd2e28580747e62e529db63223cbc39e25dcf19490c9c57d` | 456 | OK | 2026-10-14 08:44 UTC |
| `2012.zip` | 97,765,892 | `ec846d42e949ad10667648f53686d5071335cc5e5c98094cc998e37304d42e9d` | 468 | OK | 2026-10-14 08:44 UTC |
| `2013.zip` | 99,630,718 | `8fe490c521e1fd5c3c4b6b710558a8f3075cdd7c34501d9d9aa0e8a8a36ffde4` | 473 | OK | 2026-10-14 08:44 UTC |
| `2014.zip` | 98,909,484 | `ead543e4669b54fd7587ad7f0bfccc883a91d26e5eb62067650ddff9388281ac` | 475 | OK | 2026-10-14 09:34 UTC |
| `2015.zip` | 97,967,689 | `93ea17021cf7dc17fea5faccad30f1da1f97805acf502415e7246737cb325e91` | 484 | OK | 2026-10-14 09:34 UTC |
| `2016.zip` | 102,439,056 | `62a88787f1d976d7898dba2acbf5874f79cd486816e6d9531c53966557eb20a6` | 529 | OK | 2026-10-14 09:34 UTC |
| `2017.zip` | 109,677,898 | `0f620edffe32a9df55e2c0619f5f9d2fe9965ffe2fa03bfa48abac4a4a34c061` | 563 | OK | 2026-10-14 09:35 UTC |
| `2018.zip` | 117,898,042 | `ca44308b336e72d830ab1daedef45a59debc2f52bfda1a8be02c1e3d948861bb` | 596 | OK | 2026-10-14 09:35 UTC |
| `2019.zip` | 117,560,201 | `f09fa1f4314330be69093f574e7b273954881a5dcb24fc3eca9782545136af49` | 589 | OK | 2026-10-14 09:35 UTC |
| `2020.zip` | 103,653,055 | `e6cf2016dd3b78d7180dac8cbd482e5f549b227dc87a9dff642ecb7bb9e5ba0b` | 589 | OK | 2026-10-14 09:36 UTC |
| `2021.zip` | 80,571,564 | `360e53e612cf30473371d76b520585f8cd34e61d0d2185e3afe1206ce949433b` | 588 | OK | 2026-10-14 09:36 UTC |
| `2022.zip` | 90,362,801 | `292d997e0589486404827055f887327732f11d0bed9b5507952e6cad9bea286b` | 567 | OK | 2026-10-14 09:36 UTC |
| `2023.zip` | 107,069,252 | `b17391392cc1219151977cc2c46a7ab24368d821fd780311da9fff62a627bfd8` | 567 | OK | 2026-10-14 09:36 UTC |
| `2024.zip` | 102,772,199 | `0a7f89de57427f79b6f82943b2f7f2e932202d9253e34bf25629ed088d108ae7` | 565 | OK | 2026-10-14 09:37 UTC |
| `2025.zip` | 90,898,634 | `14988d0b736ba969b48881589f602f3a6d7e97b95bd1de934456851fdac2cb89` | 594 | OK | 2026-10-14 09:37 UTC |
| `2026.zip` | 136,911,232 | `62c3301ddbaa815bd523a34528ab3ded4f1b2ad26189abd6a7ee82d98ded60d4` | 1276 | OK | 2026-10-14 09:38 UTC |

## Conventional-station list from BDMEP: `bdmep_estacoes_convencionais.csv` — API response, reduced

- **Source:** BDMEP's own station API, the list its request form loads
  (`https://apibdmep.inmet.gov.br/M/R/{SU,S,CO}`: conventional stations, Southeast, South and
  Centre-West). Unlike the portal's conventional catalogue (`/paginas/catalogoman`, 87 stations,
  all "Operante"), it includes closed stations ("Desativada", "Fechada") with operating dates.
- **Retrieved:** 2026-10-14 10:00:09 UTC, through the Claude desktop app's built-in browser (the
  API host resets connections from scripts on this machine). Read-only GET requests, as the page
  itself makes.
- **Reduced, not altered:** the three responses held 454 stations. Kept: the stations whose
  operating period overlaps 1 June 2008 – 31 August 2026 (start before the end of that range, and
  end date empty or after its start), plus any station with no dates: **190 stations**. Kept
  fields, values unchanged as text: `CD_ESTACAO; DC_NOME; SG_ESTADO; CD_SITUACAO; VL_LATITUDE;
  VL_LONGITUDE; VL_ALTITUDE; DT_INICIO_OPERACAO; DT_FIM_OPERACAO`. Dropped fields: `SG_REGIAO`,
  `CD_OSCAR`, `FL_CAPITAL`, `CD_WSI`, `CD_DISTRITO`, `SG_ENTIDADE`, `TP_ESTACAO` (all
  "Convencional"). Joined with `;` (no value contains `;`, `"` or a line break, checked in the
  browser), LF line endings, trailing newline.
- **Size:** 191 lines (header plus 190 stations), 20,960 bytes.
- **SHA-256:** `75ef7f9e3d98f74bb4279d9ced771b753e7fe3599922719344d75c19a0a1fe71`, computed in the
  browser on the text and on the saved file; they match.
