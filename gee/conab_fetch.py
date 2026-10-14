"""Download Conab's coffee survey data tables that gov.br serves (§4c extraction).

gov.br lists Conab's coffee surveys from safra 2023 onward. For each safra 2023-2025 this fetches
the data table of the 1st, 3rd and 4th (final) surveys. The server sends no file name, so each
file is saved as conab_cafe_safra<YYYY>_lev<N>.xls. One file at a time, 3 s apart; a file already
on disk is skipped, never rewritten (§9).

Run:    .venv/Scripts/python gee/conab_fetch.py
Writes: data/raw/conab/conab_cafe_safra*_lev*.xls; prints one manifest line per file
"""
import datetime as dt
import hashlib
import time

import requests

from common import ROOT

OUT = ROOT / "data" / "raw" / "conab"
BASE = "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/"
HEADERS = {"User-Agent": "brazil-arabica-index (github.com/Austin-Krawczyk/brazil-arabica-index)"}
SURVEYS = [(safra, n) for safra in (2023, 2024, 2025) for n in (1, 3, 4)]


def main():
    for safra, n in SURVEYS:
        path = OUT / f"conab_cafe_safra{safra}_lev{n}.xls"
        url = f"{BASE}{n}o-levantamento-de-cafe-safra-{safra}/tabela-de-dados-estimativas-da-producao-e-colheita"
        if path.exists():
            print(f"skip {path.name}")
            continue
        r = requests.get(url, headers=HEADERS, timeout=(30, 240))
        kind = r.headers.get("Content-Type", "")
        if r.status_code != 200 or "html" in kind:
            print(f"FAILED {safra} survey {n}: HTTP {r.status_code}, {kind}")
            if r.status_code in (403, 429):
                break
            continue
        path.write_bytes(r.content)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"| `{path.name}` | {url} | {stamp} | {len(r.content):,} | "
              f"`{hashlib.sha256(r.content).hexdigest()}` |")
        time.sleep(3)


if __name__ == "__main__":
    main()
