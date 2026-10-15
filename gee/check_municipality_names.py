"""Assert that every index municipality's code matches IBGE's name and PAM's name (owner, 2026-10-14).

Sources:
  membership  docs/week0/proposed_region_membership.csv (the 1,335 index municipalities)
  IBGE        IBGE localities API v1, municipalities of MG (31) and SP (35), fetched fresh and saved
              unchanged as data/raw/ibge/localidades_municipios_{31,35}.json
  mesh        data/raw/ibge/malha_municipios_{31,35}_intermediaria.geojson (codes only)
  PAM         data/raw/ibge/pam1613_v2313_*.json (localidade id and nome, every year)
Names are compared exactly, and again after normalising case, accents, apostrophes and hyphens,
so that a spelling difference is shown separately from a different municipality.

Run:    .venv/Scripts/python gee/check_municipality_names.py
"""
import datetime as dt
import hashlib
import json
import re
import time
import unicodedata

import pandas as pd
import requests

from common import ROOT, WEEK0

RAW = ROOT / "data" / "raw" / "ibge"
HEADERS = {"User-Agent": "brazil-arabica-index (github.com/Austin-Krawczyk/brazil-arabica-index)"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def ibge_names():
    out = {}
    for uf in ("31", "35"):
        path = RAW / f"localidades_municipios_{uf}.json"
        if not path.exists():
            url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
            r = requests.get(url, headers=HEADERS, timeout=120)
            r.raise_for_status()
            path.write_bytes(r.content)
            print(f"| `{path.name}` | {url} | {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC | "
                  f"{len(r.content):,} | `{hashlib.sha256(r.content).hexdigest()}` |")
            time.sleep(2)
        for m in json.loads(path.read_text(encoding="utf-8")):
            out[str(m["id"])] = m["nome"]
    return out


def pam_names():
    out = {}
    for f in sorted(RAW.glob("pam1613_v2313_*.json")):
        for var in json.loads(f.read_text(encoding="utf-8")):
            for res in var["resultados"]:
                for s in res["series"]:
                    nome = re.sub(r"\s*[-(]\s*(MG|SP)\)?\s*$", "", s["localidade"]["nome"])
                    out.setdefault(s["localidade"]["id"], set()).add(nome)
    return out


def main():
    member = pd.read_csv(WEEK0 / "proposed_region_membership.csv", dtype={"code": str})
    member = member[member.in_index]
    ibge, pam = ibge_names(), pam_names()
    mesh = set()
    for uf in ("31", "35"):
        mesh |= {f["properties"]["codarea"] for f in json.loads(
            (RAW / f"malha_municipios_{uf}_intermediaria.geojson").read_text(encoding="utf-8"))["features"]}
    rows = []
    for r in member.itertuples():
        i, p = ibge.get(r.code), pam.get(r.code, set())
        rows.append(dict(code=r.code, membership=r.name, ibge=i, pam="; ".join(sorted(p)),
                         in_mesh=r.code in mesh, in_ibge=i is not None, in_pam=bool(p),
                         ibge_exact=i == r.name, ibge_normalised=i is not None and norm(i) == norm(r.name),
                         pam_exact=r.name in p, pam_normalised=any(norm(x) == norm(r.name) for x in p),
                         pam_names_over_years=len(p)))
    df = pd.DataFrame(rows)
    df.to_csv(WEEK0 / "municipality_name_check.csv", index=False)
    print(f"index municipalities: {len(df)}")
    for col in ("in_mesh", "in_ibge", "ibge_exact", "ibge_normalised", "in_pam", "pam_exact", "pam_normalised"):
        print(f"  {col}: {int(df[col].sum())} of {len(df)}")
    bad = df[~df.in_mesh | ~df.in_ibge | ~df.ibge_exact | ~df.in_pam | ~df.pam_exact]
    print(f"mismatches: {len(bad)}")
    if len(bad):
        print(bad[["code", "membership", "ibge", "pam", "in_mesh", "ibge_exact", "pam_exact", "pam_normalised"]]
              .to_string(index=False))
    return df


if __name__ == "__main__":
    main()
