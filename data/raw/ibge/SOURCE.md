# IBGE PAM — raw files

Files here are gitignored except this note; nothing is modified after download (§9).

## PAM table 1613, municipal coffee area, MG and SP, 1998–2025 (for the §5 step 1 filter)

- **Source:** IBGE aggregates API v3, table 1613 ("Área destinada à colheita, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras permanentes"), variable 2313 "Área destinada à colheita" (hectares), classification 82 categories 2723 "Café (em grão) Total" and 31619 "Café (em grão) Arábica", municipalities (N6) in states 31 and 35. Metadata read from https://servicodados.ibge.gov.br/api/v3/agregados/1613/metadados on 2026-10-14 (periods 1974–2025).
- **Retrieved:** 2026-10-14 by `gee/ibge_pam_fetch.py`, one request per year, 2 s apart. Each response saved unchanged.
- **Special values** (IBGE's API documentation, FAQ "Resultado / Significado", read 2026-10-14): `-` numeric value equal to zero, not from rounding; `..` not applicable; `...` numeric value not available; `X` omitted to avoid identifying an informant. Treated as: `-` = 0 ha; `...` = missing.
- **Coverage:** total coffee (2723) for every year 1998–2025; the arabica split (31619) only from 2012 (`...` before).

| File | URL | Retrieved | Bytes | SHA-256 |
|---|---|---|---|---|
| `pam1613_v2313_1998.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/1998/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:22:46 UTC | 362,531 | `cce9b18b5487a54fbc5a3b0a24605ae77c1f07a82338259e2872f20fb10ed9f8` |
| `pam1613_v2313_1999.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/1999/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:22:51 UTC | 362,573 | `22253e051e3a93ee6626440d6dd0396a94867c638343d73b65a406c752848e79` |
| `pam1613_v2313_2000.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2000/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:22:55 UTC | 362,495 | `144ccd980e0fd8c5c0f6ada0a0aa7509b4bdb6554e43a19f9bd31e8eacbc352e` |
| `pam1613_v2313_2001.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2001/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:00 UTC | 362,596 | `984c9cbaaba05a04039da7ee0ce93d0345951d8a7dbd59cee2ee0e35e29d6c1c` |
| `pam1613_v2313_2002.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2002/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:05 UTC | 362,593 | `9e1860a4e82a76bbcaea0b44dad51c9affe86959a18aec50569f2960bf5afab2` |
| `pam1613_v2313_2003.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2003/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:10 UTC | 362,612 | `d1c2fecc7f1f52488a4e9c5d9e16ca9840aa0d257140d968c984babc878822aa` |
| `pam1613_v2313_2004.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2004/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:15 UTC | 362,613 | `0317db6cd9961486a37713ea22a3a3b8991c98f49dd945a70fb622c8fbe91d8f` |
| `pam1613_v2313_2005.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2005/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:20 UTC | 362,587 | `3af72a75477f154b8587245fdddb4741a5734803f850493dcff6985668af77d7` |
| `pam1613_v2313_2006.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2006/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:26 UTC | 362,568 | `069096615bd531f1826c42c45b0856e9f75e187d9f932c81f560da2322ea6fd5` |
| `pam1613_v2313_2007.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2007/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:31 UTC | 362,536 | `1143ad8a26b1838d092dc6cf44d7f414cd1b8626dd75083b5108e5c4b76897b4` |
| `pam1613_v2313_2008.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2008/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:36 UTC | 362,478 | `a5d723cc7110fae37856ab5212c9df231dc98dc0e61c2c2a730dfd91598aaec5` |
| `pam1613_v2313_2009.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2009/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:41 UTC | 362,416 | `46447c986fbcac08db86bc80a9ab44e0294d74d928a74cdc17711a8315628c8c` |
| `pam1613_v2313_2010.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2010/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:46 UTC | 362,446 | `a85820991758592d148571d8e5f49ef908c000e1f7ac1f84c5ecc9427512bae4` |
| `pam1613_v2313_2011.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2011/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:51 UTC | 362,419 | `49e57e9807a2d159fd3f59f64ec1dac3c199a5541c9b6a827d386066f4155892` |
| `pam1613_v2313_2012.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2012/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:23:56 UTC | 361,289 | `40bc4aa43605ad9b8e10b1d60399c6fbcd73d236a663b1d6b7f4a16bccb959fa` |
| `pam1613_v2313_2013.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2013/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:01 UTC | 361,219 | `f4e100b078551edb1dfada66a6ab8a034374f5363b1d2a36e04fb9280009b794` |
| `pam1613_v2313_2014.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2014/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:06 UTC | 361,140 | `4187f4dfa5d5c1068eeab02fd0ac411626b162bbf28ddfa758d66f6f630b2b18` |
| `pam1613_v2313_2015.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2015/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:11 UTC | 360,974 | `8b1d339573eeff5f1333cb1418c89296a61e9c13eb5912f76860e7777e63875f` |
| `pam1613_v2313_2016.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2016/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:16 UTC | 360,994 | `effd994ad99c38f9470af7e018f4031ad4fc5c7e1d28d35cc5c1fbf82d6a93ad` |
| `pam1613_v2313_2017.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2017/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:21 UTC | 360,629 | `b13fdc3564c738eab96f75775c8ad8b0a68e6a6e4b98f1518b33658ba7626e1c` |
| `pam1613_v2313_2018.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2018/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:26 UTC | 360,780 | `c7b6e4ce2cd3e9536d57f709a7a61aada803e60e128911b634bb8b2ce9d105f7` |
| `pam1613_v2313_2019.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2019/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:31 UTC | 360,742 | `3287e5b19284d547543deac1886ddb327c4a5f642a584eb1735d8aba3e9c1e26` |
| `pam1613_v2313_2020.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2020/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:35 UTC | 360,737 | `797d674b4f8f1cad97b708f14450fba790b4245581e0998955c3b47827aab6ee` |
| `pam1613_v2313_2021.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2021/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:41 UTC | 360,727 | `8fecdc78ffe6181d0b5392402869b309044b9d9eef136b3ea042aecc80a5d10c` |
| `pam1613_v2313_2022.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2022/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:46 UTC | 360,711 | `114e43452872b03a87e1033701860231988a4c87774717c8bc647a507848dcae` |
| `pam1613_v2313_2023.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2023/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:51 UTC | 360,714 | `f53b00e54aa2a5bd18d4cfc138627748c005ebd5d497f254361a8d23f1f1e461` |
| `pam1613_v2313_2024.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2024/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:24:55 UTC | 360,696 | `04ce8c23dc0e8e03c86e142b7cfa2a53b738f7baf77037352f94cf9ae4719c28` |
| `pam1613_v2313_2025.json` | https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/2025/variaveis/2313?localidades=N6[N3[31,35]]&classificacao=82[2723,31619] | 2026-10-14 18:25:01 UTC | 360,659 | `108b314ec8e2917d02613777e073585d38a66fa35194feac80ccd27b0d240ffa` |

## Municipal boundaries, MG and SP (for the §5 step 1 filter and the per-municipality mask)

- **Source:** IBGE mesh API v3 (`malhas/estados/{31,35}`, `intrarregiao=municipio`,
  `qualidade=intermediaria`, GeoJSON), the current mesh served on 2026-10-14. The API's metadata
  for each state gives its centroid and area (MG 586,513.983 km², SP 248,219.485 km²) but no mesh
  year. Features carry `codarea`, the IBGE 7-digit municipality code.
- **Features:** MG 853, SP 645 municipalities.
- **Limit:** one current mesh is used for every year. Municipalities created after an early year
  have no PAM value for it (`...`); their land belonged to a parent municipality then.

| File | URL | Retrieved | Bytes | SHA-256 |
|---|---|---|---|---|
| `malha_municipios_31_intermediaria.geojson` | https://servicodados.ibge.gov.br/api/v3/malhas/estados/31?formato=application/vnd.geo%2Bjson&intrarregiao=municipio&qualidade=intermediaria | 2026-10-14 18:26:02 UTC | 1,824,901 | `6700b0db2c39a9238a47c553fa12020b0bcb0b66fce3416cafa8d3aab4e93ec6` |
| `malha_municipios_35_intermediaria.geojson` | https://servicodados.ibge.gov.br/api/v3/malhas/estados/35?formato=application/vnd.geo%2Bjson&intrarregiao=municipio&qualidade=intermediaria | 2026-10-14 18:26:06 UTC | 1,011,746 | `a9296e20334db2f4c6d86e74d97dec46842ab0c849f5b93076633c5e8348668d` |
