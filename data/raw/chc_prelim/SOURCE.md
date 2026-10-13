# CHC CHIRPS-prelim, clipped to the MG/SP window

**Source:** Climate Hazards Center, UC Santa Barbara, CHIRPS v2.0 preliminary product.
- Pentad: `https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_pentad/` (`cogs/` to
  2021.10.6, `tifs/` after).
- Daily: `https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_daily/fixed/tifs/`, the
  "fixed" daily prelim, which sums exactly to the pentad totals (CHC readme, 2019-08-22).

**Why this source:** Amendment 9 (revised, 2026-10-13) in `SPEC_CHANGELOG.md`.

**Scope:** every pentad from 2015-01; daily for September–November 2015–2025 and from
2026-05-01 onward.

**Processing at download:** each file is clipped to the window W −53.5, S −25.5, E −39.5,
N −14.0 (MG and SP with a 0.25° margin) and written as a GeoTIFF: float32, EPSG:4326, 0.05°,
LZW, nodata −9999 (present in the source files but not declared in their metadata). Units are mm
per pentad or per day. Nothing else is changed.

**Provenance:** `manifest.csv` lists every file with its source URL, the source's
`Last-Modified` header, the retrieval time (UTC) and the SHA-256 of the clipped file. The same
values are stored as tags inside each GeoTIFF. Files are written once and never modified; prelim
values that CHC later revises are not picked up unless a file is deliberately removed and
refetched, which would show in the manifest.

**Licence:** CHIRPS is placed in the public domain by CHC (copyright waived by Pete Peterson).

**Reproduce:** `.venv/Scripts/python gee/chc_prelim_fetch.py`
