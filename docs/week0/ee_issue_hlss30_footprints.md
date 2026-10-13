# Draft: Earth Engine dataset issue — NASA/HLS/HLSS30/v002 granules with global (infinite) footprints

*Draft for the owner to file on Google's Earth Engine issue tracker (data catalog / dataset issues).
Issue number to be added to `docs/week0_report.md` once filed.*

---

**Title:** NASA/HLS/HLSS30/v002: date-line granules (UTM zones 01 and 60) have infinite footprints, so
`filterBounds` returns them for any location

**Dataset:** `NASA/HLS/HLSS30/v002`

**Summary.** Some HLSS30 granules on MGRS tiles along the antimeridian (UTM zones 01 and 60) have
footprint geometries whose bounds are ±Infinity. `ImageCollection.filterBounds()` therefore returns
them for any geometry anywhere on Earth. They contain no data at those locations, so pixel values
are not affected, but they inflate collection sizes and the cost of any per-point or per-region
computation. In our case they also contributed to "User memory limit exceeded" errors. HLSL30
(`NASA/HLS/HLSL30/v002`) does not show the problem at the same location.

**Reproduce (Code Editor):**

```js
var pt = ee.Geometry.Point(-45.43, -21.55);  // Varginha, Minas Gerais, Brazil (MGRS tile 23KMS)
var col = ee.ImageCollection('NASA/HLS/HLSS30/v002')
  .filterBounds(pt)
  .filterDate('2024-12-01', '2025-01-01');
print('granules returned', col.size());                 // 61
print('ids', col.aggregate_array('system:index'));       // mostly T01xxx / T60xxx

var bad = ee.ImageCollection('NASA/HLS/HLSS30/v002')
  .filterDate('2024-12-01', '2024-12-02')
  .filter(ee.Filter.stringStartsWith('system:index', 'T01FBF'))
  .first();
print('T01FBF footprint bounds', bad.geometry().bounds());  // [-Infinity, -Infinity, Infinity, Infinity]
```

**Observed (2026-10-13):**
- At the Varginha point, December 2024: 61 HLSS30 granules returned; **56** are from date-line tiles
  (T01FBF, T01KAA, T01KAB, T01KAU, T01KAV, T01LAC, T01LAJ, T01LAK, T01UBS, T01UBT, T60UXB,
  T60UXC); only **5** are from the tile that actually covers the point (T23KMS).
- Over a bounding box of the Brazilian states of Minas Gerais and São Paulo, February 2025: 80 of
  1,815 HLSS30 granules returned are from zones 01 and 60.
- `T01FBF` footprint bounds: `[[-Infinity, -Infinity], [Infinity, -Infinity], [Infinity, Infinity], [-Infinity, Infinity]]`.
- HLSL30 at the same point and month returns 3 granules, all from T23KMS.
- Separately, `MGRS_TILE_ID` on the returned T01FBF granules reads `01FBF`, consistent with their
  tile, so the problem appears to be the footprint geometry rather than the tile assignment.

**Expected:** footprints bounded to each granule's MGRS tile, so `filterBounds` returns only
granules that intersect the query geometry.

**Workaround we use:** filter on `system:index` to the UTM zones of the study area before
`filterBounds`.

**Impact:** silent cost and memory inflation for any HLSS30 workflow using `filterBounds`, worst
for point-sampling workflows, because each broken granule intersects every point.
