"""Download IBGE PAM municipal coffee area for Minas Gerais and São Paulo (§5 step 1, 30% filter).

Table 1613 (lavouras permanentes), variable 2313 "Área destinada à colheita" (hectares), product
classification 82, categories 2723 "Café (em grão) Total" and 31619 "Café (em grão) Arábica".
Municipalities (N6) in states 31 and 35, one request per year, 2 s apart. Each response is saved
unchanged as data/raw/ibge/pam1613_v2313_<year>.json; a file already on disk is skipped.

Run:    .venv/Scripts/python gee/ibge_pam_fetch.py
"""
import datetime as dt
import hashlib
import time

import requests

from common import ROOT

OUT = ROOT / "data" / "raw" / "ibge"
URL = ("https://servicodados.ibge.gov.br/api/v3/agregados/1613/periodos/{year}/variaveis/2313"
       "?localidades=N6[N3[31,35]]&classificacao=82[2723,31619]")
HEADERS = {"User-Agent": "brazil-arabica-index (github.com/Austin-Krawczyk/brazil-arabica-index)"}
YEARS = range(1998, 2026)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        path = OUT / f"pam1613_v2313_{year}.json"
        if path.exists():
            continue
        r = requests.get(URL.format(year=year), headers=HEADERS, timeout=120)
        if r.status_code != 200:
            print(f"FAILED {year}: HTTP {r.status_code}")
            break
        path.write_bytes(r.content)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"| `{path.name}` | {URL.format(year=year)} | {stamp} | {len(r.content):,} | "
              f"`{hashlib.sha256(r.content).hexdigest()}` |", flush=True)
        time.sleep(2)


if __name__ == "__main__":
    main()
