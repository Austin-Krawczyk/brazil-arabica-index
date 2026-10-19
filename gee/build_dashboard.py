"""Build the public dashboard, docs/index.html, from frozen files only (owner, 2026-10-18).
Local; no Earth Engine; no price data.

Sources, each checked before use:
  data/derived/backtest_results_v1.csv     the v1 backtest (SHA-256 recorded in Week 0 report §23)
  data/derived/w2_frost_region_season.csv  frozen W2 frost input (SHA-256 from w2_inputs_manifest.csv)
  docs/week0_report.md §24                  the interpretation the page states
  data/derived/production_readings_crop2027.csv
      Optional. Written by the crop-2027 production run. Until it exists, the page shows
      "crop 2027: pending November production run".
      Columns: region, version, vintage, a_pred (share of the stage-1 expectation),
      rain_includes_prelim (True/False), made_as_of (date).

Every number on the page carries its file and the commit that last changed that file.

Readings:
  - A backtest reading is the held-out condition anomaly (a_pred) for a crop and vintage: the
    leave-one-season-out prediction, as a % of the stage-1 expectation (§5 steps 6–8).
  - Crop 2026 has no reading. It is not in the backtest: Conab's final is pending (§5 step 8).
  - Direction follows Amendment 42. A reading whose rain input includes CHIRPS-prelim months, and
    whose anomaly is 1 pp or less from zero, is "flat, within the preliminary-data margin".
  - Backtest readings use final CHIRPS, so the margin never applies to them.

The December note updates the page by running this script after the production file exists.

Run:    .venv/Scripts/python gee/build_dashboard.py
Writes: docs/index.html, docs/.nojekyll
"""
import hashlib
import html
import json
import math
import subprocess

import numpy as np
import pandas as pd

import backtest as bt
from common import ROOT

REPO = "https://github.com/Austin-Krawczyk/brazil-arabica-index"
D = ROOT / "data" / "derived"
RESULTS = D / "backtest_results_v1.csv"
RESULTS_SHA = "a966877dfa60d64dc079d9c7e73dbd29ee66f521e85f6b5c714b9dce0a047ffa"  # Week 0 report §23
FROST = D / "w2_frost_region_season.csv"
MANIFEST = D / "w2_inputs_manifest.csv"
REPORT = ROOT / "docs" / "week0_report.md"
PRODUCTION = D / "production_readings_crop2027.csv"
OUT = ROOT / "docs" / "index.html"

UNITS = [bt.REGIONS[0], bt.REGIONS[1], bt.REGIONS[2], bt.REGIONS[3], bt.TOTAL]
NAME = {bt.REGIONS[0]: ("Sul e Centro-Oeste", "Sul de Minas"),
        bt.REGIONS[1]: ("Triângulo, Alto Paranaíba e Noroeste", "Cerrado Mineiro"),
        bt.REGIONS[2]: ("Zona da Mata, Rio Doce e Central", "Matas de Minas"),
        bt.REGIONS[3]: ("São Paulo", "Mogiana"),
        bt.TOTAL: ("Four-region total", "PAM-weighted")}
VERSIONS = {"no_frost": "Without frost", "with_frost": "With frost"}
VINT = ["Nov", "Dec", "Jan"]
VLABEL = {"Nov": "November", "Dec": "December", "Jan": "January"}
S24 = ["### (1) The registered verdict", "### (3) The comparison models",
       "### (4) Zona da Mata, Rio Doce e Central: a failure", "### (2) What the frost version changes"]


# ------------------------------------------------------------------ provenance
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def commit_of(path):
    rel = path.relative_to(ROOT).as_posix()
    full = subprocess.run(["git", "log", "-1", "--format=%H", "--", rel], capture_output=True, text=True,
                          cwd=ROOT).stdout.strip()
    if not full:
        raise SystemExit(f"{rel} is not committed; the dashboard cites committed files only")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    if dirty:
        raise SystemExit(f"{rel} has uncommitted changes; the dashboard cites committed files only")
    return full


def check_frozen():
    if sha256(RESULTS) != RESULTS_SHA:
        raise SystemExit("backtest_results_v1.csv differs from the SHA-256 recorded in §23; it is frozen")
    m = pd.read_csv(MANIFEST).set_index("path")
    if sha256(FROST) != m.at["data/derived/w2_frost_region_season.csv", "sha256"]:
        raise SystemExit("w2_frost_region_season.csv differs from the W2 manifest; it is frozen")
    text = REPORT.read_text(encoding="utf-8")
    for h in S24:
        if h not in text:
            raise SystemExit(f"Week 0 report §24 heading not found: {h}")


def src(key):
    s = SOURCES[key]
    return (f'<a class="src" href="{REPO}/blob/{s["commit"]}/{s["path"]}">'
            f'{html.escape(s["label"])} @{s["commit"][:7]}</a>')


# ------------------------------------------------------------------ formatting
def pct(x, d=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    s = f"{abs(x):.{d}f}%"
    return ("+" if x > 0 else "−" if x < 0 else "") + s


def pp(x):
    s = f"{abs(x):.1f} pp"
    return ("+" if x > 0 else "−" if x < 0 else "±") + s


def direction(a_pct, rain_includes_prelim):
    """Amendment 42: the margin applies only to readings with CHIRPS-prelim months in their rain input."""
    if rain_includes_prelim and abs(a_pct) <= 1.0:
        return "flat, within the preliminary-data margin"
    return "above the expectation" if a_pct > 0 else "below the expectation" if a_pct < 0 else "at the expectation"


def status(verdict):
    ok = verdict == "pass"
    return (f'<span class="st"><span class="st-i {"good" if ok else "bad"}" aria-hidden="true">'
            f'{"✓" if ok else "✕"}</span>{verdict}</span>')


# ------------------------------------------------------------------ data
def series(res):
    h = res[(res.sensitivity == "headline") & (res.model == "full") & res.scored]
    out = {}
    for ver in VERSIONS:
        for u in UNITS:
            x = h[(h.version == ver) & (h.region == u)]
            crops = sorted(x.crop.unique())
            row = {"crops": [int(c) for c in crops]}
            for v in VINT:
                y = x[x.vintage == v].set_index("crop")
                row[v] = [round(100 * float(y.at[c, "a_pred"]), 2) for c in crops]
                row[v + "_hit"] = [bool(y.at[c, "hit_condition"]) for c in crops]
            y = x[x.vintage == "Nov"].set_index("crop")
            row["actual"] = [round(100 * float(y.at[c, "a_actual"]), 2) for c in crops]
            out[(ver, u)] = row
    return out


def reliability(res):
    s = bt.summary(res)
    out = {}
    for ver in VERSIONS:
        for u in UNITS:
            f = s[(s.sensitivity == "headline") & (s.version == ver) & (s.model == "full") & (s.vintage == "Nov")
                  & (s.region == u)].iloc[0]
            z = s[(s.sensitivity == "headline") & (s.version == ver) & (s.model == "zero") & (s.vintage == "Nov")
                  & (s.region == u)].iloc[0]
            mk = bt.PASS_MARKS[(ver, u)]
            out[(ver, u)] = dict(hits=int(f.hits_condition), n=int(f.n), mark=mk[0], verdict=f.verdict,
                                 crops=f.crops, mae=float(f.mae_pct), mae_zero=float(z.mae_pct))
    return out


def frost_now():
    f = pd.read_csv(FROST)
    c = f[f.crop == 2027].set_index("region")
    out = {}
    for u in bt.REGIONS:
        r = c.loc[u]
        tier = ("severe" if r.flag_severe_with_unresolved else "2 °C" if r.flag_2c_with_unresolved else "none")
        out[u] = dict(auto=int(r.automatic_stations), conv=int(r.conventional_stations),
                      unresolved=int(r.unresolved_stations), cov=100 * float(r.coverage_with_unresolved),
                      cov_alt=100 * float(r.coverage_without_unresolved),
                      unflag=bool(r.unflaggable_with_unresolved), unflag_alt=bool(r.unflaggable_without_unresolved),
                      severe=100 * float(r.severe_share_with_unresolved), c2=100 * float(r.share_2c_with_unresolved),
                      flag=tier)
    return out


def production():
    if not PRODUCTION.exists():
        return None
    p = pd.read_csv(PRODUCTION)
    need = {"region", "version", "vintage", "a_pred", "rain_includes_prelim", "made_as_of"}
    if need - set(p.columns):
        raise SystemExit(f"{PRODUCTION.name} lacks columns {sorted(need - set(p.columns))}")
    return p


def latest_production(prod, ver, u):
    """The latest crop-2027 reading for a unit and version, its change from the previous vintage, and
    whether its rain input includes CHIRPS-prelim months (for Amendment 42)."""
    if prod is None:
        return None
    x = prod[(prod.version == ver) & (prod.region == u)].copy()
    if x.empty:
        return None
    x["o"] = x.vintage.map({v: i for i, v in enumerate(VINT)})
    x = x.sort_values("o")
    cur = x.iloc[-1]
    a = 100 * float(cur.a_pred)
    if len(x) > 1:
        change = f"change from {VLABEL[x.iloc[-2].vintage]} {pp(a - 100 * float(x.iloc[-2].a_pred))}"
    else:
        change = "the crop's first reading, no previous vintage"
    prelim = str(cur.rain_includes_prelim).strip().lower() in ("true", "1", "yes")
    return dict(vintage=cur.vintage, a=a, change=change, prelim=prelim, asof=str(cur.made_as_of))


# ------------------------------------------------------------------ chart (inline SVG)
W, H = 520, 210
ML, MR, MT, MB = 44, 14, 12, 30
X0, X1 = 2002, 2025


def chart(row, ymax, cid, title):
    xs = lambda c: ML + (c - X0) / (X1 - X0) * (W - ML - MR)
    ys = lambda v: MT + (ymax - v) / (2 * ymax) * (H - MT - MB)
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="{cid}-t" class="chart" '
             f'tabindex="0" data-chart="{cid}"><title id="{cid}-t">{html.escape(title)}</title>']
    step = 20 if ymax > 30 else 10
    for g in range(-int(ymax // step) * step, int(ymax) + 1, step):
        y = ys(g)
        parts.append(f'<line class="{"base" if g == 0 else "gl"}" x1="{ML}" x2="{W - MR}" y1="{y:.1f}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{ML - 6}" y="{y + 3.5:.1f}" text-anchor="end">'
                     f'{"+" if g > 0 else "−" if g < 0 else ""}{abs(g)}%</text>')
    for c in range(X0, X1 + 1, 4 if X1 - X0 > 12 else 2):
        parts.append(f'<text class="tick" x="{xs(c):.1f}" y="{H - 10}" text-anchor="middle">{c}</text>')
    crops = row["crops"]
    for v, cls in (("Jan", "s3"), ("Dec", "s2"), ("Nov", "s1")):
        pts = " ".join(f"{xs(c):.1f},{ys(val):.1f}" for c, val in zip(crops, row[v]))
        parts.append(f'<polyline class="ln {cls}" points="{pts}"/>')
    for c, val in zip(crops, row["actual"]):
        parts.append(f'<circle class="act" cx="{xs(c):.1f}" cy="{ys(val):.1f}" r="4"/>')
    parts.append(f'<line class="xh" x1="0" x2="0" y1="{MT}" y2="{H - MB}" visibility="hidden"/>')
    parts.append(f'<rect class="hit" x="{ML}" y="{MT}" width="{W - ML - MR}" height="{H - MT - MB}"/>')
    parts.append("</svg>")
    geo = dict(ml=ML, mr=MR, w=W, x0=X0, x1=X1)
    data = {k: row[k] for k in ["crops", "Nov", "Dec", "Jan", "actual", "Nov_hit", "Dec_hit", "Jan_hit"]}
    return "".join(parts) + (f'<script type="application/json" id="{cid}-d">'
                             f'{json.dumps(dict(geo=geo, **data))}</script>')


def table(row):
    head = "<tr><th>Crop</th><th>November</th><th>December</th><th>January</th><th>Actual</th></tr>"
    body = []
    for i, c in enumerate(row["crops"]):
        cells = "".join(f'<td>{pct(row[v][i])} {"✓" if row[v + "_hit"][i] else "✕"}</td>' for v in VINT)
        body.append(f"<tr><td>{c}{'*' if c == 2022 else ''}</td>{cells}<td>{pct(row['actual'][i])}</td></tr>")
    return f'<table class="tv"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table>'


# ------------------------------------------------------------------ page
CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#6e6c66;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--good:#0ca30c;--bad:#d03b3b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a29b;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a29b;
--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1120px;margin:0 auto;padding:20px 16px 48px}
h1{font-size:22px;margin:0 0 2px}h2{font-size:16px;margin:28px 0 8px}h3{font-size:15px;margin:0}
.sub{color:var(--ink2);margin:0 0 14px}.muted{color:var(--muted);font-size:12.5px}
.banner{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:12px 14px;margin:14px 0}
.banner b{font-size:16px}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px}
.cards{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{font-weight:600;color:var(--ink2);font-size:13px}td.num,th.num{font-variant-numeric:tabular-nums}
.st{white-space:nowrap}.st-i{display:inline-block;width:1.2em;font-weight:700}.st-i.good{color:var(--good)}.st-i.bad{color:var(--bad)}
.ctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:18px 0 10px}
.ctl button{font:inherit;padding:6px 12px;border-radius:8px;border:1px solid var(--axis);background:var(--surface);color:var(--ink);cursor:pointer}
.ctl button[aria-pressed="true"]{border-color:var(--ink);font-weight:600}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--ink2);margin:6px 0}
.key{display:inline-block;width:16px;height:2px;vertical-align:middle;margin-right:5px;border-radius:1px}
.k1{background:var(--s1)}.k2{background:var(--s2)}.k3{background:var(--s3)}
.kd{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--ink);vertical-align:middle;margin-right:5px}
.chart{width:100%;height:auto;display:block;outline:none}.chart:focus-visible{outline:2px solid var(--s1);outline-offset:2px;border-radius:4px}
.chart .gl{stroke:var(--grid);stroke-width:1}.chart .base{stroke:var(--axis);stroke-width:1}
.chart .tick{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.chart .ln{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.chart .s1{stroke:var(--s1)}.chart .s2{stroke:var(--s2)}.chart .s3{stroke:var(--s3)}
.chart .act{fill:var(--ink);stroke:var(--surface);stroke-width:2}
.chart .xh{stroke:var(--ink2);stroke-width:1}.chart .hit{fill:transparent;cursor:crosshair}
.facts{margin:10px 0 0;padding:0;list-style:none;font-size:13.5px}.facts li{margin:4px 0}
.facts .lab{color:var(--ink2)}
a.src{color:var(--muted);font-size:11.5px;text-decoration:underline;text-decoration-color:var(--axis)}
details{margin-top:8px}summary{cursor:pointer;color:var(--ink2);font-size:13px}
.tv td,.tv th{padding:3px 6px;font-size:12.5px;font-variant-numeric:tabular-nums}
#tip{position:fixed;pointer-events:none;background:var(--surface);color:var(--ink);border:1px solid var(--axis);border-radius:8px;
padding:8px 10px;font-size:12.5px;box-shadow:0 4px 14px rgba(0,0,0,.12);display:none;z-index:9;min-width:170px}
#tip .r{display:flex;align-items:center;gap:6px;margin:2px 0}#tip .v{font-weight:600;margin-left:auto;font-variant-numeric:tabular-nums}
#tip .h{color:var(--ink2);font-weight:600;margin-bottom:4px}
[data-v]{display:none}body[data-version="no_frost"] [data-v="no_frost"],body[data-version="with_frost"] [data-v="with_frost"]{display:block}
ul.notes{padding-left:18px;margin:6px 0}ul.notes li{margin:3px 0}
@media (max-width:560px){th,td{padding:5px 4px;font-size:13px}main{padding:16px 16px 40px}}
"""

JS = r"""
(function(){
  const tip=document.getElementById('tip');
  function setVersion(v){document.body.dataset.version=v;
    document.querySelectorAll('.ctl button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.ver===v)));
    try{localStorage.setItem('bai-version',v);}catch(e){}}
  document.querySelectorAll('.ctl button').forEach(b=>b.addEventListener('click',()=>setVersion(b.dataset.ver)));
  try{const s=localStorage.getItem('bai-version');if(s==='no_frost'||s==='with_frost')setVersion(s);}catch(e){}
  function fmt(x){if(x===null||x===undefined)return '–';const a=Math.abs(x).toFixed(1)+'%';return x>0?'+'+a:x<0?'−'+a:a;}
  function row(cls,label,val,hit){const r=document.createElement('div');r.className='r';
    const k=document.createElement('span');
    if(cls==='kd'){k.className='kd';}else{k.className='key '+cls;}
    const l=document.createElement('span');l.textContent=label;
    const v=document.createElement('span');v.className='v';v.textContent=val+(hit===undefined?'':(hit?'  ✓':'  ✕'));
    r.append(k,l,v);return r;}
  document.querySelectorAll('svg.chart').forEach(svg=>{
    const d=JSON.parse(document.getElementById(svg.dataset.chart+'-d').textContent);
    const xh=svg.querySelector('.xh');let idx=-1;
    const xOf=c=>d.geo.ml+(c-d.geo.x0)/(d.geo.x1-d.geo.x0)*(d.geo.w-d.geo.ml-d.geo.mr);
    function show(i,cx,cy){idx=i;const c=d.crops[i];const x=xOf(c);
      xh.setAttribute('x1',x);xh.setAttribute('x2',x);xh.setAttribute('visibility','visible');
      tip.replaceChildren();const h=document.createElement('div');h.className='h';
      h.textContent='Crop '+c+(c===2022?' (in-sample)':'');tip.append(h);
      tip.append(row('kd','Actual',fmt(d.actual[i])));
      tip.append(row('k1','November',fmt(d.Nov[i]),d.Nov_hit[i]));
      tip.append(row('k2','December',fmt(d.Dec[i]),d.Dec_hit[i]));
      tip.append(row('k3','January',fmt(d.Jan[i]),d.Jan_hit[i]));
      tip.style.display='block';
      const r=tip.getBoundingClientRect();let left=cx+14,top=cy+14;
      if(left+r.width>innerWidth-8)left=cx-r.width-14;if(top+r.height>innerHeight-8)top=cy-r.height-14;
      tip.style.left=Math.max(8,left)+'px';tip.style.top=Math.max(8,top)+'px';}
    function hide(){tip.style.display='none';xh.setAttribute('visibility','hidden');}
    function nearest(clientX){const b=svg.getBoundingClientRect();const sx=(clientX-b.left)/b.width*d.geo.w;
      let best=0,bd=1e9;d.crops.forEach((c,i)=>{const dd=Math.abs(xOf(c)-sx);if(dd<bd){bd=dd;best=i;}});return best;}
    svg.addEventListener('pointermove',e=>show(nearest(e.clientX),e.clientX,e.clientY));
    svg.addEventListener('pointerleave',hide);
    svg.addEventListener('blur',hide);
    svg.addEventListener('keydown',e=>{if(e.key==='Escape'){hide();return;}
      if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();
      let i=idx<0?d.crops.length-1:idx+(e.key==='ArrowRight'?1:-1);i=Math.max(0,Math.min(d.crops.length-1,i));
      const b=svg.getBoundingClientRect();const x=b.left+xOf(d.crops[i])/d.geo.w*b.width;show(i,x,b.top+b.height*0.3);});
  });
})();
"""


def build():
    check_frozen()
    res = pd.read_csv(RESULTS)
    ser, rel, fr, prod = series(res), reliability(res), frost_now(), production()
    ft = pd.read_csv(FROST)
    ft = ft[ft.crop == 2027]
    fr_total = dict(flags=int((ft[ft.region.isin(bt.REGIONS)][["flag_severe_with_unresolved",
                                                                "flag_2c_with_unresolved"]].any(axis=1)).sum()),
                    penalty=float(ft[ft.region == bt.TOTAL].penalty_with_unresolved.fillna(0).iloc[0]))
    for k, p in (("results", RESULTS), ("frost", FROST), ("report", REPORT)):
        SOURCES[k]["commit"] = commit_of(p)
    if prod is not None:
        SOURCES["production"] = dict(path=PRODUCTION.relative_to(ROOT).as_posix(), label=PRODUCTION.name,
                                     what="crop-2027 production readings", commit=commit_of(PRODUCTION))
    vals = [v for r in ser.values() for k in ("Nov", "Dec", "Jan", "actual") for v in r[k]]
    ymax = math.ceil(max(abs(v) for v in vals) / 10) * 10

    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           "<title>Brazil Arabica Condition Index</title>",
           '<meta name="description" content="Growing-condition index for four Brazilian arabica regions: '
           'backtest readings, their registered reliability, and current frost status. Condition index, not a '
           'yield forecast.">', f"<style>{CSS}</style></head>", '<body data-version="no_frost"><main>']
    out.append("<h1>Brazil arabica growing-condition index</h1>")
    out.append('<p class="sub">Four Conab arabica units in Minas Gerais and São Paulo. <b>A condition index, '
               "not a yield forecast.</b> No price data.</p>")

    # current state
    if prod is None:
        out.append('<div class="banner"><b>Crop 2027 (2027/28): pending the November production run.</b><br>'
                   "No crop-2027 reading exists yet. The readings below are the backtest's held-out readings, "
                   "crops 2002–2025.</div>")
    else:
        asof = ", ".join(sorted(prod.made_as_of.astype(str).unique()))
        out.append('<div class="banner"><b>Crop 2027 (2027/28): readings made as of ' + html.escape(asof) +
                   ".</b> Each unit's latest reading is in its card below, with its change from the previous "
                   "vintage. The chart and table show the backtest. " + src("production") + "</div>")

    # reliability strip
    out.append("<h2>How reliable it has been: the registered backtest, November vintage</h2>")
    out.append('<p class="muted" style="margin-top:0">The November vintage decides pass or fail. A hit means '
               "the index called the sign of the actual yield against the stage-1 expectation. MAE is mean "
               "absolute error in percentage points, against the zero-anomaly baseline. Each version has its "
               "own registered marks, and there is no combined verdict.</p>")
    out.append('<div class="card"><table><thead><tr><th>Unit</th><th>Without frost</th><th class="num">MAE vs zero</th>'
               '<th>With frost (crops 2009–2025)</th><th class="num">MAE vs zero</th></tr></thead><tbody>')
    for u in UNITS:
        a, b = rel[("no_frost", u)], rel[("with_frost", u)]
        out.append(f"<tr><td><b>{html.escape(NAME[u][0])}</b><br><span class='muted'>{html.escape(NAME[u][1])}</span></td>"
                   f"<td>{status(a['verdict'])} {a['hits']} of {a['n']} <span class='muted'>(mark {a['mark']}; "
                   f"{a['crops']})</span></td><td class='num'>{a['mae']:.1f} vs {a['mae_zero']:.1f}</td>"
                   f"<td>{status(b['verdict'])} {b['hits']} of {b['n']} <span class='muted'>(mark {b['mark']})</span></td>"
                   f"<td class='num'>{b['mae']:.1f} vs {b['mae_zero']:.1f}</td></tr>")
    out.append("</tbody></table>")
    out.append('<ul class="notes muted">'
               "<li>Crop 2022 (the July 2021 frost) is in-sample for the frost version. The frost constants "
               "were set knowing what that frost did.</li>"
               "<li>Zona da Mata fails both versions. Mask representativeness is the stated candidate "
               "explanation, and it is untested.</li>"
               "<li>São Paulo's and the total's extra hits in the frost version come from its refit on crops "
               "with zero frost penalty, not from frost. The frost penalty turned Sul's crop 2012 from a hit "
               "into a miss.</li></ul>")
    out.append(f'<p class="muted">Hits, marks and MAE: {src("results")}. Statements: {src("report")} '
               "(Week 0 report §24).</p></div>")

    # version control
    out.append('<div class="ctl" role="group" aria-label="Model version"><span class="muted">Version:</span>'
               '<button data-ver="no_frost" aria-pressed="true">Without frost</button>'
               '<button data-ver="with_frost" aria-pressed="false">With frost</button></div>')
    out.append('<div class="legend"><span><span class="key k1"></span>November reading (scored)</span>'
               '<span><span class="key k2"></span>December reading</span><span><span class="key k3"></span>'
               'January reading</span><span><span class="kd"></span>Actual condition anomaly</span></div>')
    out.append('<p class="muted" style="margin:0 0 10px">Readings are held-out predictions of the condition '
               "anomaly, as a % of the stage-1 expectation (trend plus the previous crop's carry-over). "
               "Crop 2026 has no reading: it is not in the backtest, because Conab's final is pending.</p>")

    out.append('<div class="cards">')
    for i, u in enumerate(UNITS):
        out.append(f'<section class="card" aria-label="{html.escape(NAME[u][0])}"><h3>{html.escape(NAME[u][0])}'
                   f' <span class="muted">· {html.escape(NAME[u][1])}</span></h3>')
        for ver in VERSIONS:
            r, s = ser[(ver, u)], rel[(ver, u)]
            out.append(f'<div data-v="{ver}">')
            out.append(f'<p class="muted" style="margin:4px 0 6px">{status(s["verdict"])} {s["hits"]} of {s["n"]} '
                       f'November hits (mark {s["mark"]}) · MAE {s["mae"]:.1f} pp against {s["mae_zero"]:.1f} '
                       f"for zero anomaly · {VERSIONS[ver].lower()} · {src('results')}</p>")
            out.append(chart(r, ymax, f"c{i}{ver}", f"{NAME[u][0]}, {VERSIONS[ver].lower()}: condition-anomaly "
                                                    f"readings and actuals, crops {r['crops'][0]}–{r['crops'][-1]}"))
            last = r["crops"][-1]
            jan, dec = r["Jan"][-1], r["Dec"][-1]
            out.append('<ul class="facts">')
            lp = latest_production(prod, ver, u)
            if lp:
                out.append(f'<li><span class="lab">Most recent reading:</span> crop 2027, {VLABEL[lp["vintage"]]} '
                           f'(as of {html.escape(lp["asof"])}): <b>{pct(lp["a"])}</b>, {direction(lp["a"], lp["prelim"])}; '
                           f'{lp["change"]}. {src("production")}</li>')
            out.append(f'<li><span class="lab">{"Most recent backtest" if lp else "Most recent"} reading:</span> '
                       f"crop {last}, January: <b>{pct(jan)}</b>, {direction(jan, False)}; change from December "
                       f"{pp(jan - dec)}. Actual {pct(r['actual'][-1])}. Final CHIRPS, so the preliminary-data "
                       f"margin (Amendment 42) does not apply. {src('results')}</li>")
            if u in fr:
                f = fr[u]
                stations = f"{f['auto']} automatic" + (f", {f['conv']} conventional" if f["conv"] else "")
                tiers = ("no station meets a tier" if f["severe"] == 0 and f["c2"] == 0 else
                         f"stations at the severe tier cover {f['severe']:.1f}% and at the 2 °C tier {f['c2']:.1f}% "
                         "of observed coffee")
                extra = " Note 1 (held) covers a station reading outside the registered rule." if u == bt.REGIONS[0] else ""
                out.append(f'<li><span class="lab">Frost, Jun–Aug 2026 (crop 2027):</span> {tiers}; '
                           f"flag <b>{f['flag']}</b>{' (unflaggable)' if f['unflag'] else ''}. Observed coverage "
                           f"{f['cov']:.1f}% ({stations}; {f['unresolved']} unresolved). With unresolved stations "
                           f"left out: {f['cov_alt']:.1f}%, {'unflaggable' if f['unflag_alt'] else 'flaggable'}."
                           f"{extra} {src('frost')}</li>")
            else:
                out.append('<li><span class="lab">Frost, Jun–Aug 2026 (crop 2027):</span> '
                           f"{'no region is flagged' if fr_total['flags'] == 0 else str(fr_total['flags']) + ' region(s) flagged'}; "
                           f"four-region penalty {100 * fr_total['penalty']:.1f}%. {src('frost')}</li>")
            out.append("</ul>")
            out.append(f"<details><summary>Table view ({len(r['crops'])} crops)</summary>{table(r)}"
                       f'<p class="muted">✓ hit, ✕ miss. * In-sample (frost version). {src("results")}</p></details>')
            out.append("</div>")
        out.append("</section>")
    out.append("</div>")

    out.append("<h2>Limits</h2><ul class='notes'>"
               "<li>The index tracks growing conditions, not yield.</li>"
               "<li>The private trade houses have field crop tours and farm data that this project does not.</li>"
               "<li>MODIS at 250 m blurs Zona da Mata's steep smallholder terrain. The coffee mask "
               "under-represents its smallholder and shaded coffee.</li>"
               "<li>Frost comes from INMET screen-height stations, which sample cold-air pools poorly. They "
               "did not flag the July 2021 frost in Sul de Minas or São Paulo.</li></ul>")
    out.append("<h2>Sources</h2><ul class='notes muted'>")
    for k, s in SOURCES.items():
        if "commit" in s:
            out.append(f"<li>{src(k)}: {html.escape(s['what'])}. SHA-256 {sha256(ROOT / s['path'])[:16]}…</li>")
    out.append("</ul><p class='muted'>Built by <code>gee/build_dashboard.py</code> from the files above. "
               f'Method, pre-registration and code: <a class="src" href="{REPO}">{REPO}</a>.</p>')
    out.append(f'</main><div id="tip" role="status" aria-live="polite"></div><script>{JS}</script></body></html>')
    OUT.write_text("\n".join(out), encoding="utf-8")
    (ROOT / "docs" / ".nojekyll").write_text("", encoding="utf-8")
    return OUT


SOURCES = {
    "results": dict(path="data/derived/backtest_results_v1.csv", label="backtest_results_v1.csv",
                    what="the v1 backtest, one run (Week 0 report §23)"),
    "frost": dict(path="data/derived/w2_frost_region_season.csv", label="w2_frost_region_season.csv",
                  what="frozen W2 frost input; headline with unresolved stations kept at their observed tiers"),
    "report": dict(path="docs/week0_report.md", label="week0_report.md §24",
                   what="the interpretation of the backtest"),
}

if __name__ == "__main__":
    print(build())
