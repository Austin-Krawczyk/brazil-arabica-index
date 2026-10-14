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

## Download completed 2026-10-14

- **The throttled retry** sent one test request at 13:07:10 UTC; CHC answered 200. The
  sequential fetch (3 s between files) then ran to the end without a 403 or 429.
- **2,007 files in scope:**
  - 848 pentads, 2015-01-01 to 2026-10-06, with none missing from the sequence;
  - 1,159 days: September–November 2015–2025, plus 2026-05-01 to 2026-10-10.
- **122 pentads** were already on disk from 2026-10-13 and were skipped. **1,885 files** were
  fetched on 2026-10-14.
- **Checksums:** the SHA-256 of every file, recomputed after the run, matches `manifest.csv`
  (2,007 of 2,007). The 122 earlier files are byte-identical to the manifest committed on
  2026-10-13.
- **Every file opens:** 230 × 280 cells, EPSG:4326, float32, fill −9999, and its `kind` and
  `start_date` tags match its file name.
- **Five days are missing at the source:** 2026-05-11 to 2026-05-15, one whole pentad's days. CHC's
  `global_daily/fixed/tifs/2026/` listing, rechecked on 2026-10-14, jumps from 2026-05-10 to
  2026-05-16. They are not filled; the pentad file 2026.05.3 covering those days is present.
