"""Extract Conab arabica area, yield and production for the index regions (§4c), with vintages.

Sources, all in data/raw/conab/ (provenance in its SOURCE.md):
  - survey data tables (sheet "2 Café Arábica"): each gives the survey's own safra and the
    previous safra as revised at that survey. Safras 2023-2025 (1st, 3rd and 4th = final surveys)
    and the 3rd survey of safra 2026.
  - Conab's arabica historical series (cafearabicaseriehist.xls): one vintage, released with the
    September 2026 estimate. Production by region from 2001; area and yield from 2008 only.
  - Conab's arabica + conilon series (cafetotalseriehist.xls): area, yield and production by
    region from 2001. Written with product = "total"; it is NOT arabica and is not substituted
    for it here.

Units out: area in hectares, yield in 60 kg bags per hectare, production in thousand bags. A
survey table states its area unit in its header ("mil ha" or "ha"); it is read, not assumed.
Empty cells stay empty: nothing is filled or estimated.

Run:    .venv/Scripts/python gee/conab_extract.py
Writes: data/derived/conab_regional.csv
"""
import re

import pandas as pd

from common import ROOT

RAW = ROOT / "data" / "raw" / "conab"
REGIONS = {"Sul e Centro-Oeste": "Sul e Centro-Oeste",
           "Triângulo, Alto Paranaiba e Noroeste": "Triângulo, Alto Paranaíba e Noroeste",
           "Zona da Mata, Rio Doce e Central": "Zona da Mata, Rio Doce e Central",
           "SP": "São Paulo (state total)", "MG": "Minas Gerais (state total)"}
SURVEY_DATES = {  # publication month of each survey, from the bulletin titles on Conab's pages
    (2023, 1): "2023-01", (2023, 3): "2023-09", (2023, 4): "2023-12",
    (2024, 1): "2024-01", (2024, 3): "2024-09", (2024, 4): "2025-01",
    (2025, 1): "2025-01", (2025, 3): "2025-09", (2025, 4): "2025-12",
    (2026, 3): "2026-09",
}
SURVEY_FILES = {(s, n): f"conab_cafe_safra{s}_lev{n}.xls" for s in (2023, 2024, 2025) for n in (1, 3, 4)}
SURVEY_FILES[(2026, 3)] = "site_previsao-de-safra-cafe-set-2026.xls"


def label(cell):
    return re.sub(r"\s+", " ", str(cell)).strip()


def survey_rows(safra, n, fname):
    x = pd.ExcelFile(RAW / fname)
    d = pd.read_excel(x, [s for s in x.sheet_names if s.startswith("2 ")][0], header=None)
    head = d.index[d.iloc[:, 0].astype(str).str.contains("REGI")][0]
    area_head = str(d.iloc[head, 1])
    area_scale = 1000.0 if "mil ha" in area_head else 1.0 if "(ha)" in area_head else None
    assert area_scale is not None, area_head
    assert "PRODUTIVIDADE" in str(d.iloc[head, 4]) and "PRODU" in str(d.iloc[head, 7]), d.iloc[head].tolist()
    years = [int(re.search(r"(\d{4})", str(d.iloc[head + 1, c])).group(1)) for c in (1, 2)]
    assert years == [safra - 1, safra], (fname, years)
    out = []
    for i in range(head + 2, len(d)):
        lab = label(d.iloc[i, 0])
        if lab not in REGIONS:
            continue
        for k, yr in enumerate(years):
            area = d.iloc[i, 1 + k]
            out.append(dict(
                safra=yr, region=REGIONS[lab], product="arabica",
                area_ha=None if pd.isna(area) else float(area) * area_scale,
                yield_sc_ha=d.iloc[i, 4 + k], production_kbags=d.iloc[i, 7 + k],
                vintage=f"survey {n} of safra {safra}", vintage_date=SURVEY_DATES[(safra, n)],
                column="current" if yr == safra else "previous safra as revised",
                source=fname))
    return out


def series_rows(fname, product, vintage, vintage_date):
    x = pd.ExcelFile(RAW / fname)
    sheets = {"area_ha": "Área em produção", "yield_sc_ha": "Produtividade", "production_kbags": "Produção"}
    frames = {}
    for var, sheet in sheets.items():
        d = pd.read_excel(x, sheet, header=None)
        head = d.index[d.iloc[:, 0].astype(str).str.startswith("UNIDADE")][0]
        years = [int(re.search(r"(\d{4})", str(y)).group(1)) for y in d.iloc[head, 1:] if re.search(r"\d{4}", str(y))]
        for i in range(head + 1, len(d)):
            lab = label(d.iloc[i, 0])
            if lab in REGIONS:
                for j, yr in enumerate(years):
                    frames.setdefault((REGIONS[lab], yr), {})[var] = d.iloc[i, 1 + j]
    out = []
    for (reg, yr), v in sorted(frames.items()):
        out.append(dict(safra=yr, region=reg, product=product, **{k: v.get(k) for k in sheets},
                        vintage=vintage, vintage_date=vintage_date,
                        column="estimate" if yr == 2026 else "historical series",
                        source=fname))
    return out


def main():
    rows = []
    for (safra, n), fname in sorted(SURVEY_FILES.items()):
        rows += survey_rows(safra, n, fname)
    rows += series_rows("cafearabicaseriehist.xls", "arabica", "historical series (Sept 2026 release)", "2026-09")
    rows += series_rows("cafetotalseriehist.xls", "total", "historical series (Sept 2026 release)", "2026-09")
    df = pd.DataFrame(rows)
    for c in ("area_ha", "yield_sc_ha", "production_kbags"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.sort_values(["product", "region", "safra", "vintage_date", "vintage"])
    df.to_csv(ROOT / "data" / "derived" / "conab_regional.csv", index=False)
    return df


if __name__ == "__main__":
    main()
