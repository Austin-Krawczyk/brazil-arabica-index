"""Maps and the note 1 chart for the dashboard and the notes (owner, 2026-11-09). Local only; no Earth
Engine. Called by gee/build_dashboard.py.

  reading map   the four regions on MG and SP, each filled by its most recent condition anomaly.
                Zona da Mata is hatched: it failed its backtest pass mark in both versions, and
                MODIS blurs its terrain (Week 0 report §24 (4)).
  frost map     the current winter's counted frost stations as dots, coloured by coldest observed
                night. Unresolved stations are hollow rings. Their 25 km circles are faint, and the
                frozen coffee mask sits behind.
  note 1 chart  coldest observed night per region, each winter from 2008 (crop 2009, the first frost
                window) to 2026. The 2 °C and 0 °C thresholds are drawn as lines.

Counted stations follow gee/w2_frost.py: those qualifying in docs/week0/station_set_frozen.csv,
less any conventional station that shares a site (≤ 1 km in the frozen candidates) with a qualifying
automatic station (Amendment 17d). The coldest night is the registered-rule observed minimum
(Amendment 17b), with unresolved stations kept at their observed values (Amendment 41b).

Inputs, each checked before use:
  - IBGE municipal meshes in data/raw/ibge/, read-only, with SHA-256 checked against
    data/raw/ibge/SOURCE.md;
  - docs/week0/proposed_region_membership.csv;
  - docs/week0/station_candidates_frozen.csv and station_set_frozen.csv;
  - docs/week0/w2_frost_night_rule_alternative.csv (Caldas outside the rule);
  - data/derived/w2_frost_station_season.csv, w2_frost_region_season.csv and
    frozen_mask_pixels.csv, with SHA-256 checked against the W2 manifest.
"""
import hashlib
import html
import json
import math

import numpy as np
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union

from common import ROOT, WEEK0

D = ROOT / "data" / "derived"
IBGE = ROOT / "data" / "raw" / "ibge"
MESH = {"malha_municipios_31_intermediaria.geojson": "6700b0db2c39a9238a47c553fa12020b0bcb0b66fce3416cafa8d3aab4e93ec6",
        "malha_municipios_35_intermediaria.geojson": "a9296e20334db2f4c6d86e74d97dec46842ab0c849f5b93076633c5e8348668d"}
REGIONS = ["Sul e Centro-Oeste", "Triângulo, Alto Paranaíba e Noroeste", "Zona da Mata, Rio Doce e Central",
           "São Paulo (state total)"]
OUTSIDE = "Norte, Jequitinhonha e Mucuri"
TRADE = {REGIONS[0]: "Sul de Minas", REGIONS[1]: "Cerrado Mineiro", REGIONS[2]: "Matas de Minas",
         REGIONS[3]: "São Paulo"}
SHORT = {REGIONS[0]: "Sul e Centro-Oeste", REGIONS[1]: "Triângulo", REGIONS[2]: "Zona da Mata",
         REGIONS[3]: "São Paulo"}
# diverging classes for the condition anomaly, % of the stage-1 expectation (equal steps per arm)
DIV_EDGES = [-20, -10, -3, 3, 10, 20]
DIV_LABELS = ["−20% or lower", "−20 to −10%", "−10 to −3%", "−3 to +3%", "+3 to +10%", "+10 to +20%", "+20% or higher"]
# ordinal classes for the coldest night, °C (colder = further from the surface)
COLD_EDGES = [0, 2, 4, 6, 8]
COLD_LABELS = ["≤ 0 °C", "0–2 °C", "2–4 °C", "4–6 °C", "6–8 °C", "> 8 °C"]

MAP_CSS = """
svg.map,svg.sm{width:100%;height:auto;display:block}svg.map{max-width:520px;margin:4px auto}svg.sm{max-width:640px;margin:4px auto}
.map .rg{stroke:var(--surface);stroke-width:1.2}
.map .out{fill:var(--outside)}
.map .st{fill:none;stroke:var(--axis);stroke-width:1}
.map .rb{fill:none;stroke:var(--ink2);stroke-width:.8;stroke-opacity:.6}
.map .lab{font-size:11.5px;fill:var(--ink);paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.map .lab2{font-size:10.5px;fill:var(--ink2);paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.map .cof{fill:var(--coffee)}
.map .c25{fill:none;stroke:var(--ink2);stroke-width:.6;stroke-opacity:.35}
.map .dot{stroke:var(--surface);stroke-width:2}
.map .ring{fill:var(--surface);stroke-width:2.2}
.map .lead{stroke:var(--ink2);stroke-width:1}
.d0{fill:var(--d0)}.d1{fill:var(--d1)}.d2{fill:var(--d2)}.d3{fill:var(--d3)}.d4{fill:var(--d4)}.d5{fill:var(--d5)}.d6{fill:var(--d6)}
.k0{fill:var(--k0)}.k1{fill:var(--k1)}.k2{fill:var(--k2)}.k3{fill:var(--k3)}.k4{fill:var(--k4)}.k5{fill:var(--k5)}
.r0{stroke:var(--k0)}.r1{stroke:var(--k1)}.r2{stroke:var(--k2)}.r3{stroke:var(--k3)}.r4{stroke:var(--k4)}.r5{stroke:var(--k5)}
.hatch-line{stroke:var(--ink);stroke-width:1.1;stroke-opacity:.55}
.sm .thr{stroke:var(--ink2);stroke-width:1}.sm .thl{font-size:10px;fill:var(--ink2)}
.sm .ln{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.sm .pt{fill:var(--s1);stroke:var(--surface);stroke-width:2}.sm .ptf{fill:var(--ink);stroke:var(--surface);stroke-width:2}
.sm .gl{stroke:var(--grid);stroke-width:1}.sm .tick{fill:var(--muted);font-size:10.5px;font-variant-numeric:tabular-nums}
.sm .ttl{font-size:12px;font-weight:600;fill:var(--ink)}.sm .val{font-size:10.5px;fill:var(--ink);font-weight:600}
[data-tip]{cursor:default}
"""
# light values; the page overrides them for dark mode
VARS_LIGHT = {"--outside": "#ecebe6", "--coffee": "#8a8880",
              "--d0": "#9b2c2b", "--d1": "#e34948", "--d2": "#f3aaa8", "--d3": "#e6e5df", "--d4": "#9ec5f4",
              "--d5": "#3987e5", "--d6": "#1c5cab",
              "--k0": "#0d366b", "--k1": "#184f95", "--k2": "#256abf", "--k3": "#3987e5", "--k4": "#6da7ec",
              "--k5": "#86b6ef"}
VARS_DARK = {"--outside": "#252523", "--coffee": "#8f8d85",
             "--d0": "#e98b89", "--d1": "#e34948", "--d2": "#8a3433", "--d3": "#383835", "--d4": "#1c5cab",
             "--d5": "#3987e5", "--d6": "#86b6ef",
             "--k0": "#cde2fb", "--k1": "#9ec5f4", "--k2": "#6da7ec", "--k3": "#3987e5", "--k4": "#256abf",
             "--k5": "#184f95"}
STANDALONE_BASE = {"--surface": "#fcfcfb", "--ink": "#0b0b0b", "--ink2": "#52514e", "--muted": "#6e6c66",
                   "--grid": "#e1e0d9", "--axis": "#c3c2b7", "--s1": "#2a78d6"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_inputs():
    for name, sha in MESH.items():
        if sha256(IBGE / name) != sha:
            raise SystemExit(f"{name} differs from the SHA-256 in data/raw/ibge/SOURCE.md")
    m = pd.read_csv(D / "w2_inputs_manifest.csv").set_index("path")
    for rel in ("data/derived/w2_frost_station_season.csv", "data/derived/w2_frost_region_season.csv",
                "data/derived/frozen_mask_pixels.csv"):
        if sha256(ROOT / rel) != m.at[rel, "sha256"]:
            raise SystemExit(f"{rel} differs from the W2 manifest; it is frozen")


# ------------------------------------------------------------------ geometry
class Proj:
    """Equirectangular, scaled by cos(-20°), to a width in px."""

    def __init__(self, bounds, width, pad=8):
        self.lon0, self.lat0, self.lon1, self.lat1 = bounds
        self.c = math.cos(math.radians(-20.0))
        self.k = (width - 2 * pad) / ((self.lon1 - self.lon0) * self.c)
        self.pad = pad
        self.w = width
        self.h = int(round((self.lat1 - self.lat0) * self.k + 2 * pad))

    def xy(self, lon, lat):
        return self.pad + (lon - self.lon0) * self.c * self.k, self.pad + (self.lat1 - lat) * self.k

    def km(self, km):
        return km / 111.32 * self.k


def load_geometry():
    memb = pd.read_csv(WEEK0 / "proposed_region_membership.csv", dtype={"code": str}).set_index("code")
    by_region, by_state = {}, {"31": [], "35": []}
    for name in MESH:
        g = json.load(open(IBGE / name, encoding="utf-8"))
        for f in g["features"]:
            code = f["properties"]["codarea"]
            geom = shape(f["geometry"])
            by_state[code[:2]].append(geom)
            by_region.setdefault(memb.at[code, "conab_region"], []).append(geom)
    regions = {r: unary_union(gs).simplify(0.012, preserve_topology=True) for r, gs in by_region.items()}
    states = {s: unary_union(gs).simplify(0.012, preserve_topology=True) for s, gs in by_state.items()}
    return regions, states


def path(geom, proj):
    polys = getattr(geom, "geoms", [geom])
    out = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = [proj.xy(x, y) for x, y in ring.coords]
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def bounds(regions):
    b = unary_union(list(regions.values())).bounds
    return b[0] - 0.1, b[1] - 0.1, b[2] + 0.1, b[3] + 0.1


# ------------------------------------------------------------------ reading map
def div_class(a):
    return int(np.searchsorted(DIV_EDGES, a, side="left"))


def reading_map(geo, values, cid, title, width=560):
    """values: {region: dict(a=pct, label=str)}. Returns SVG markup."""
    regions, states = geo
    proj = Proj(bounds(regions), width)
    p = [f'<svg viewBox="0 0 {proj.w} {proj.h}" class="map" role="img" aria-labelledby="{cid}-t">'
         f'<title id="{cid}-t">{html.escape(title)}</title>'
         f'<defs><pattern id="{cid}-h" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="7" class="hatch-line"/></pattern></defs>']
    p.append(f'<path class="rg out" d="{path(regions[OUTSIDE], proj)}" data-tip="{html.escape(OUTSIDE)}|outside the index"/>')
    for r in REGIONS:
        v = values.get(r)
        cls = f"d{div_class(v['a'])}" if v else "d3"
        tip = f"{SHORT[r]} ({TRADE[r]})|{v['label']}" if v else f"{SHORT[r]}|no reading"
        if r == REGIONS[2]:
            tip += "|hatched: failed its backtest pass mark; MODIS blurs its terrain"
        p.append(f'<path class="rg {cls}" d="{path(regions[r], proj)}" data-tip="{html.escape(tip)}"/>')
    p.append(f'<path d="{path(regions[REGIONS[2]], proj)}" fill="url(#{cid}-h)" pointer-events="none"/>')
    for s in states.values():
        p.append(f'<path class="st" d="{path(s, proj)}" pointer-events="none"/>')
    for r in REGIONS:
        pt = regions[r].representative_point()
        x, y = proj.xy(pt.x, pt.y)
        v = values.get(r)
        p.append(f'<text class="lab" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" pointer-events="none">'
                 f'{html.escape(SHORT[r])}</text>')
        if v:
            p.append(f'<text class="lab2" x="{x:.0f}" y="{y + 13:.0f}" text-anchor="middle" pointer-events="none">'
                     f'{html.escape(v["short"])}</text>')
    p.append("</svg>")
    return "".join(p)


def div_legend():
    items = "".join(f'<span><svg width="14" height="10"><rect class="d{i}" width="14" height="10" rx="2"/></svg>'
                    f"{html.escape(lab)}</span>" for i, lab in enumerate(DIV_LABELS))
    return f'<div class="legend">{items}<span><svg width="14" height="10"><rect width="14" height="10" class="d3"/>' \
           f'<line x1="0" y1="10" x2="10" y2="0" class="hatch-line"/></svg>hatched: Zona da Mata, not reliable</span></div>'


# ------------------------------------------------------------------ frost data
def haversine_km(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(a))


def same_site_pairs():
    """Conventional → automatic within 1 km in the frozen candidates, as gee/w2_frost.py pairs them
    (Amendment 17d). docs/week0/colocated_pairs.csv predates Amendment 39b and is not used here."""
    cand = pd.read_csv(WEEK0 / "station_candidates_frozen.csv", dtype={"code": str})
    au, co = cand[cand.network == "automatic"], cand[cand.network == "conventional"]
    pairs = {}
    for _, c in co.iterrows():
        d = haversine_km(c.lat, c.lon, au.lat.values, au.lon.values)
        if len(d) and d.min() <= 1.0:
            pairs[c.code] = au.code.values[int(d.argmin())]
    return pairs


def counted_stations():
    """(window, region) → set of (network, code) counted, as in gee/w2_frost.py."""
    sset = pd.read_csv(WEEK0 / "station_set_frozen.csv", dtype={"code": str})
    pairs = same_site_pairs()
    out = {}
    for (w, reg), q in sset[sset.qualifies].groupby(["window", "region"]):
        qa = set(q[q.network == "automatic"].code)
        out[(w, reg)] = {(r.network, r.code) for r in q.itertuples()
                         if not (r.network == "conventional" and pairs.get(r.code) in qa)}
    return out


def coldest_series():
    st = pd.read_csv(D / "w2_frost_station_season.csv", dtype={"code": str}).set_index(["network", "code", "window"])
    names = pd.read_csv(WEEK0 / "station_candidates_frozen.csv", dtype={"code": str}).set_index(["network", "code"]).name
    fr = pd.read_csv(D / "w2_frost_region_season.csv")
    rows = []
    for (w, reg), sts in counted_stations().items():
        if reg not in REGIONS:
            continue
        best = None
        for net, code in sts:
            c = st.at[(net, code, w), "coldest_c"] if (net, code, w) in st.index else np.nan
            if pd.notna(c) and (best is None or c < best[0]):
                best = (float(c), net, code)
        f = fr[(fr.window == w) & (fr.region == reg)].iloc[0]
        flag = "severe" if f.flag_severe_with_unresolved else "2 °C" if f.flag_2c_with_unresolved else ""
        rows.append(dict(region=reg, winter=int(w), crop=int(w) + 1, stations=len(sts),
                         coldest_c=best[0] if best else np.nan,
                         station=f"{names.get((best[1], best[2]), best[2]).title()} ({best[2]})" if best else "",
                         flag=flag, unflaggable=bool(f.unflaggable_with_unresolved)))
    return pd.DataFrame(rows).sort_values(["region", "winter"])


def cold_class(c):
    return int(np.searchsorted(COLD_EDGES, c, side="left"))


def frost_map(geo, window, cid, width=560):
    regions, states = geo
    proj = Proj(bounds(regions), width)
    st = pd.read_csv(D / "w2_frost_station_season.csv", dtype={"code": str})
    st = st[st.window == window].set_index(["network", "code"])
    cand = pd.read_csv(WEEK0 / "station_candidates_frozen.csv", dtype={"code": str}).set_index(["network", "code"])
    alt = pd.read_csv(WEEK0 / "w2_frost_night_rule_alternative.csv", dtype={"code": str})
    alt = alt[alt.window == window].set_index("code")
    counted = set().union(*[s for (w, r), s in counted_stations().items() if w == window and r in REGIONS])
    # coffee mask behind: the frozen mask for this window's crop (mask year = window − 1), kept municipalities
    band = f"w_{window - 1}"
    kept = pd.read_csv(WEEK0 / "w1_filter_stable_membership.csv", dtype={"code": str})
    pts = pd.read_csv(D / "frozen_mask_pixels.csv", dtype={"code": str}, usecols=["code", "longitude", "latitude", band])
    pts = pts[(pts[band] > 0) & pts.code.isin(set(kept.loc[kept.kept, "code"]))]
    cell = 0.08  # degrees; the mask is drawn as density cells, one path per class, to keep the page small
    gx, gy = np.floor(pts.longitude / cell), np.floor(pts.latitude / cell)
    cells = pts.groupby([gx, gy])[band].sum()
    q = cells.quantile([0.5, 0.85]).values
    p = [f'<svg viewBox="0 0 {proj.w} {proj.h}" class="map" role="img" aria-labelledby="{cid}-t">'
         f'<title id="{cid}-t">Counted INMET frost stations, June–August {window}, coloured by coldest observed '
         f'night; 25 km circles; coffee mask behind</title>']
    p.append(f'<path class="rg out" d="{path(regions[OUTSIDE], proj)}"/>')
    runs = {0.22: [], 0.42: [], 0.65: []}
    for (cx, cy), wsum in cells.items():
        x0, y0 = proj.xy(cx * cell, (cy + 1) * cell)
        x1, y1 = proj.xy((cx + 1) * cell, cy * cell)
        op = 0.22 if wsum <= q[0] else 0.42 if wsum <= q[1] else 0.65
        runs[op].append(f"M{x0:.0f} {y0:.0f}h{x1 - x0 + .3:.1f}v{y1 - y0 + .3:.1f}h-{x1 - x0 + .3:.1f}z")
    for op, d in runs.items():
        p.append(f'<path class="cof" fill-opacity="{op}" d="{"".join(d)}"/>')
    for r in REGIONS:
        p.append(f'<path class="rb" d="{path(regions[r], proj)}"/>')
    for s in states.values():
        p.append(f'<path class="st" d="{path(s, proj)}"/>')
    rows = []
    for net, code in sorted(counted):
        la, lo = cand.at[(net, code), "lat"], cand.at[(net, code), "lon"]
        x, y = proj.xy(lo, la)
        p.append(f'<circle class="c25" cx="{x:.1f}" cy="{y:.1f}" r="{proj.km(25):.1f}"/>')
        s = st.loc[(net, code)] if (net, code) in st.index else None
        rows.append((net, code, la, lo, x, y, s))
    for net, code, la, lo, x, y, s in sorted(rows, key=lambda r: -(r[6].coldest_c if r[6] is not None else 99)):
        name = cand.at[(net, code), "name"].title()
        if s is None or pd.isna(s.coldest_c):
            continue
        k = cold_class(s.coldest_c)
        unres = bool(s.unresolved)
        tip = (f"{name} ({code}, {net})|coldest observed night {s.coldest_c:.1f} °C|tier {s.tier}"
               + ("|unresolved: missing nights could change its tier" if unres else ""))
        if unres:
            p.append(f'<circle class="ring r{k}" cx="{x:.1f}" cy="{y:.1f}" r="4.2" data-tip="{html.escape(tip)}"/>')
        else:
            p.append(f'<circle class="dot k{k}" cx="{x:.1f}" cy="{y:.1f}" r="5" data-tip="{html.escape(tip)}"/>')
    # Caldas, outside the registered rule (Amendment 40), reported and not scored
    if "A530" in alt.index and ("automatic", "A530") in counted and alt.at["A530", "tier_alt"] != alt.at["A530", "tier"]:
        la, lo = cand.at[("automatic", "A530"), "lat"], cand.at[("automatic", "A530"), "lon"]
        x, y = proj.xy(lo, la)
        tx, ty = x - 70, y + 46
        p.append(f'<line class="lead" x1="{x:.1f}" y1="{y + 5:.1f}" x2="{tx + 4:.1f}" y2="{ty - 11:.1f}"/>')
        p.append(f'<text class="lab2" x="{tx:.0f}" y="{ty:.0f}" text-anchor="middle">Caldas: '
                 f'{alt.at["A530", "coldest_alt"]:.1f} °C on pre-dawn hours,</text>')
        p.append(f'<text class="lab2" x="{tx:.0f}" y="{ty + 12:.0f}" text-anchor="middle">outside the registered '
                 f"night rule; not scored</text>")
    p.append("</svg>")
    table = pd.DataFrame([dict(network=n, code=c, name=cand.at[(n, c), "name"].title(), lat=la, lon=lo,
                               coldest_c=None if s is None else s.coldest_c, tier=None if s is None else s.tier,
                               unresolved=None if s is None else bool(s.unresolved))
                          for n, c, la, lo, x, y, s in rows])
    return "".join(p), table


def cold_legend():
    items = "".join(f'<span><svg width="12" height="12"><circle cx="6" cy="6" r="5" class="k{i}"/></svg>'
                    f"{html.escape(lab)}</span>" for i, lab in enumerate(COLD_LABELS))
    return (f'<div class="legend">{items}<span><svg width="12" height="12"><circle cx="6" cy="6" r="4" '
            f'fill="none" class="r2" stroke-width="2"/></svg>hollow: unresolved</span>'
            f'<span><svg width="12" height="12"><rect width="12" height="12" class="cof" fill-opacity=".42"/></svg>'
            f"coffee mask</span></div>")


# ------------------------------------------------------------------ note 1 chart
def coldest_chart(series, cid):
    pw, ph, gap = 300, 170, 18
    ml, mr, mt, mb = 34, 30, 22, 22
    w0, w1 = int(series.winter.min()), int(series.winter.max())
    lo = math.floor(min(series.coldest_c.min(), 0) / 2) * 2 - 2
    hi = math.ceil(series.coldest_c.max() / 2) * 2
    W, H = 2 * pw + gap, 2 * ph + gap
    p = [f'<svg viewBox="0 0 {W} {H}" class="sm" role="img" aria-labelledby="{cid}-t"><title id="{cid}-t">'
         f"Coldest observed night at counted INMET stations, per region, June–August {w0}–{w1}</title>"]
    for i, reg in enumerate(REGIONS):
        ox, oy = (i % 2) * (pw + gap), (i // 2) * (ph + gap)
        xs = lambda w: ox + ml + (w - w0) / (w1 - w0) * (pw - ml - mr)
        ys = lambda c: oy + mt + (hi - c) / (hi - lo) * (ph - mt - mb)
        p.append(f'<text class="ttl" x="{ox + ml}" y="{oy + 13}">{html.escape(SHORT[reg])}</text>')
        for g in range(lo, hi + 1, 4):
            p.append(f'<line class="gl" x1="{ox + ml}" x2="{ox + pw - mr}" y1="{ys(g):.1f}" y2="{ys(g):.1f}"/>'
                     f'<text class="tick" x="{ox + ml - 5}" y="{ys(g) + 3.5:.1f}" text-anchor="end">{g}°</text>')
        for t, lab in ((2, "2 °C"), (0, "0 °C")):
            p.append(f'<line class="thr" x1="{ox + ml}" x2="{ox + pw - mr}" y1="{ys(t):.1f}" y2="{ys(t):.1f}"/>'
                     f'<text class="thl" x="{ox + pw - mr + 3}" y="{ys(t) + 3.5:.1f}">{lab}</text>')
        for w in (w0, 2014, 2020, w1):
            p.append(f'<text class="tick" x="{xs(w):.1f}" y="{oy + ph - 6}" text-anchor="middle">{w}</text>')
        s = series[(series.region == reg) & series.coldest_c.notna()]
        p.append('<polyline class="ln" points="' + " ".join(f"{xs(r.winter):.1f},{ys(r.coldest_c):.1f}"
                                                             for r in s.itertuples()) + '"/>')
        for r in s.itertuples():
            tip = (f"{SHORT[reg]}, June–August {r.winter} (crop {r.crop})|coldest {r.coldest_c:.1f} °C at {r.station}"
                   f"|{r.stations} counted stations" + (f"|regional flag: {r.flag}" if r.flag else "")
                   + ("|unflaggable: coverage under 15%" if r.unflaggable else ""))
            cls = "ptf" if r.flag else "pt"
            p.append(f'<circle class="{cls}" cx="{xs(r.winter):.1f}" cy="{ys(r.coldest_c):.1f}" r="4" '
                     f'data-tip="{html.escape(tip)}"/>')
            if r.flag:
                p.append(f'<text class="val" x="{xs(r.winter):.1f}" y="{ys(r.coldest_c) + 15:.1f}" '
                         f'text-anchor="middle">flag</text>')
        last = s[s.winter == w1]
        if len(last):
            r = last.iloc[0]
            p.append(f'<text class="val" x="{xs(w1) - 6:.1f}" y="{ys(r.coldest_c) - 8:.1f}" text-anchor="end">'
                     f"{r.coldest_c:.1f}°</text>")
    p.append("</svg>")
    return "".join(p)


def standalone(svg):
    """A light-mode SVG file with its own style, for the notes."""
    vars_ = ";".join(f"{k}:{v}" for k, v in {**STANDALONE_BASE, **VARS_LIGHT}.items())
    style = (f"<style>svg{{{vars_};font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#fcfcfb}}"
             f"{MAP_CSS}</style>")
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    i = svg.index(">") + 1
    return svg[:i] + style + svg[i:]
