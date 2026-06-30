"""
Purpose: STAGE 8 - the Privacy Nutrition Facts APP. Renders an app's Privacy Elements
         (nutrition-facts label + practice/purpose breakdown + captions + a Neo4j graph
         link) as a self-contained static site.
Input:   --dataset + --captions (and optional --ppg for the exact Neo4j app_id).
Output:  data/app/index.html (app picker) + data/app/<package>.html per app.

Stack choice: a STDLIB-ONLY static HTML generator (no Flask/JS build, no server, no network).
Rationale — the repo is offline-first and test-without-keys; a static generator is the
lightest thing that runs locally with one command and needs zero new deps. Open index.html
in any browser. (Swap in a server later if interactivity is needed; the data is plain JSON.)

Run: python -m step4_app.build_app --dataset data/dataset --captions data/captions --out data/app
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Dict

from pplib.io_utils import ensure_dir, get_logger
from stage4_ppg.cypher_runner import load_library
from step4_app.nutrition import build_nutrition

log = get_logger("app")
REPO_ROOT = Path(__file__).resolve().parent.parent
_RISK_COLOR = {"Low": "#2e9e5b", "Medium": "#c98a00", "High": "#d23b3b"}


def _e(s) -> str:
    return html.escape(str(s))


def _bars(counts: Dict[str, int], palette: Dict[str, str]) -> str:
    total = max(1, sum(counts.values()))
    rows = []
    for k, v in counts.items():
        if not v:
            continue
        pct = round(100 * v / total)
        color = palette.get(k, "#6b7a99")
        rows.append(
            f'<div class="bar"><span class="bl">{_e(k)}</span>'
            f'<span class="bt"><i style="width:{pct}%;background:{color}"></i></span>'
            f'<span class="bv">{v}</span></div>')
    return "".join(rows) or '<div class="muted">none</div>'


def _app_page(label: dict, app_id: str, overlay_cypher: str) -> str:
    r = label["security_risk"]
    rc = _RISK_COLOR.get(r["level"], "#6b7a99")
    pkg = label["app_package"]
    weak_banner = (f'<div class="banner">⚠ {_e(label["banner"])}</div>' if label["weak"] else "")

    collected = "".join(
        f'<li><b>{_e(d["category"])}</b> <span class="muted">×{d["count"]}</span></li>'
        for d in label["data_collected"]) or '<li class="muted">none detected</li>'
    shared = "".join(
        f'<li><b>{_e(d["category"])}</b> → {_e(", ".join(d["recipients"]))}</li>'
        for d in label["data_shared_offdevice"]) or '<li class="muted">nothing leaves the device</li>'
    third = "".join(f"<li>{_e(t)}</li>" for t in label["third_parties"]) or '<li class="muted">none</li>'
    threats = ", ".join(label["security_risk"]["linddun_threats"]) or "none detected"
    caps = "".join(f"<li>{_e(c)}</li>" for c in label["captions"]) or '<li class="muted">—</li>'
    purpose_bars = _bars(label["purposes"],
                         {"Functionality": "#4c8eda", "Advertisement": "#d23b3b",
                          "Analytics": "#c98a00", "Other": "#6b7a99"})
    practice_bars = _bars(label["practices"],
                          {"Collecting": "#57c7e3", "Processing": "#8dcc93",
                           "Sharing": "#f16667", "Other": "#6b7a99"})
    factors = "; ".join(r["factors"]) or "no elevated-risk signals detected"

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Nutrition Facts — {_e(pkg)}</title>{_CSS}</head><body>
<div class="wrap">
<a class="back" href="index.html">← all apps</a>
<h1>Privacy Nutrition Facts</h1>
<div class="pkg">{_e(pkg)}</div>
{weak_banner}
<div class="grid">
  <section class="facts">
    <div class="risk" style="border-color:{rc}">
      <div class="risk-l" style="color:{rc}">{_e(r['level'])} risk</div>
      <div class="risk-s">{r['score']}<small>/100</small></div>
      <div class="muted">heuristic indicator — not a security audit</div>
      <div class="why">{_e(factors)}.</div>
    </div>
    <div class="rule"></div>
    <h2>Data collected</h2><ul>{collected}</ul>
    <div class="thin"></div>
    <h2>Data shared off-device</h2><ul>{shared}</ul>
    <div class="thin"></div>
    <h2>Third parties (ad / analytics)</h2><ul>{third}</ul>
    <div class="thin"></div>
    <h2>LINDDUN threats</h2><div class="muted">{_e(threats)}</div>
  </section>
  <section class="side">
    <h2>Practices</h2><div class="bars">{practice_bars}</div>
    <h2>Purposes</h2><div class="bars">{purpose_bars}</div>
    <div class="thin"></div>
    <h2>In plain language</h2><ul class="caps">{caps}</ul>
    <div class="thin"></div>
    <h2>See the graph in Neo4j</h2>
    <div class="muted">app_id <code>{_e(app_id)}</code> — paste into Neo4j Browser:</div>
    <pre class="cy">{_e(overlay_cypher)}</pre>
    <div class="muted">or: <code>python -m stage4_ppg.cypher_runner --run app_ppg_overlay --app-id "{_e(app_id)}"</code></div>
  </section>
</div>
<div class="foot">Based on {label['n_prcs']} permission-requiring code segment(s). Generated by the Privacy Nutrition Facts app (Stage 8).</div>
</div></body></html>"""


def _index_page(index: dict, app_ids: Dict[str, str]) -> str:
    banner = (f'<div class="banner">⚠ {_e(index["banner"])}</div>' if index.get("banner") else "")
    cards = []
    for pkg, info in sorted(index["apps"].items(), key=lambda kv: -kv[1]["risk_score"]):
        rc = _RISK_COLOR.get(info["risk_level"], "#6b7a99")
        href = _e(pkg.replace("/", "_")) + ".html"
        weak = ' <span class="tag">WEAK</span>' if info["weak"] else ""
        cards.append(
            f'<a class="card" href="{href}">'
            f'<div class="cscore" style="color:{rc}">{info["risk_score"]}<small>/100</small></div>'
            f'<div class="cmid"><div class="cpkg">{_e(pkg)}{weak}</div>'
            f'<div class="muted">{info["n_prcs"]} PRCS · {_e(info["risk_level"])} risk</div></div>'
            f'<div class="carrow" style="color:{rc}">›</div></a>')
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Nutrition Facts</title>{_CSS}</head><body>
<div class="wrap">
<h1>Privacy Nutrition Facts</h1>
<div class="pkg">{len(index['apps'])} app(s) analysed · APK → static analysis → PPG → ConvGNN → privacy elements</div>
{banner}
<div class="cards">{''.join(cards)}</div>
<div class="foot">Click an app for its full label, breakdown, captions, and graph link.</div>
</div></body></html>"""


def build_app(dataset_dir: str, captions_dir: str | None, out_dir: str,
              ppg_dir: str | None = None, cmap_path: str | None = None) -> dict:
    """Generate the static Privacy Nutrition Facts site. Returns the index summary."""
    out = ensure_dir(out_dir)
    index = build_nutrition(dataset_dir, captions_dir, str(out / "_data"), cmap_path)

    # Reconstruct the exact Neo4j app_id (package@apk) from the dataset records.
    app_ids: Dict[str, str] = {}
    for line in (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        app_ids.setdefault(r["app_package"], f"{r['app_package']}@{r.get('apk_filename', '')}")

    overlay = load_library().get("app_ppg_overlay")
    for pkg in index["apps"]:
        label = json.loads((out / "_data" / pkg.replace("/", "_") / "nutrition.json").read_text("utf-8"))
        app_id = app_ids.get(pkg, pkg)
        cy = overlay.render(app_id=app_id) if overlay else ""
        (out / (pkg.replace("/", "_") + ".html")).write_text(
            _app_page(label, app_id, cy), encoding="utf-8")
    (out / "index.html").write_text(_index_page(index, app_ids), encoding="utf-8")
    log.info("Built Privacy Nutrition Facts app for %d app(s) -> %s/index.html",
             len(index["apps"]), out)
    return index


_CSS = """<style>
:root{--bg:#0f1320;--panel:#171c2c;--line:#2a3147;--ink:#e8eefc;--muted:#93a1bd}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;padding:28px 18px 60px}
.wrap{max-width:1000px;margin:0 auto}h1{font-size:26px;margin:0 0 2px;letter-spacing:-.02em}
.pkg{color:var(--muted);margin-bottom:16px}.back{color:#60a5fa;text-decoration:none;font-size:13px}
.banner{background:#3a2a06;border:1px solid #8a6512;color:#fde9bf;padding:10px 14px;border-radius:10px;margin:10px 0}
.grid{display:grid;grid-template-columns:1.05fr .95fr;gap:18px}@media(max-width:760px){.grid{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}
.facts{border-width:2px}h2{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:14px 0 8px}
.facts h2:first-of-type{margin-top:0}ul{margin:0;padding-left:18px}li{margin:3px 0}.muted{color:var(--muted)}
.rule{height:6px;background:var(--ink);opacity:.85;margin:14px 0;border-radius:3px}
.thin{height:1px;background:var(--line);margin:14px 0}
.risk{border:2px solid;border-radius:12px;padding:14px;text-align:center}
.risk-l{font-weight:800;letter-spacing:.04em;text-transform:uppercase;font-size:13px}
.risk-s{font-size:40px;font-weight:800;line-height:1}.risk-s small{font-size:15px;color:var(--muted)}
.why{margin-top:8px;color:var(--muted);font-size:13px}
.bars{display:flex;flex-direction:column;gap:7px}.bar{display:grid;grid-template-columns:96px 1fr 28px;gap:9px;align-items:center;font-size:13px}
.bl{color:var(--muted);text-align:right}.bt{height:14px;background:#0f1320;border:1px solid var(--line);border-radius:5px;overflow:hidden}
.bt i{display:block;height:100%}.bv{font-weight:700;text-align:right}
.caps li{margin:6px 0}.cy{background:#0f1320;border:1px solid var(--line);border-radius:8px;padding:10px;overflow:auto;font-size:12px;white-space:pre-wrap}
code{background:#0f1320;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:12px}
.foot{color:var(--muted);font-size:12px;margin-top:22px;border-top:1px solid var(--line);padding-top:14px}
.cards{display:flex;flex-direction:column;gap:10px}
.card{display:grid;grid-template-columns:70px 1fr 24px;gap:14px;align-items:center;text-decoration:none;color:var(--ink);
background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card:hover{border-color:#60a5fa}.cscore{font-size:28px;font-weight:800;text-align:center}.cscore small{font-size:12px;color:var(--muted)}
.cpkg{font-weight:600}.carrow{font-size:24px;text-align:center}.tag{font-size:10px;background:#3a2a06;color:#fbbf24;border:1px solid #8a6512;border-radius:6px;padding:1px 5px}
</style>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the Privacy Nutrition Facts app (Stage 8).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--ppg", default=None, help="(optional) PPG dir — only used for context")
    ap.add_argument("--out", default="data/app")
    ap.add_argument("--map", default="configs/gdpr_ccpa_map.yaml")
    args = ap.parse_args()
    idx = build_app(args.dataset, args.captions, args.out, args.ppg, args.map)
    print(f"\n=== Privacy Nutrition Facts app -> {args.out}/index.html ===")
    for pkg, info in idx["apps"].items():
        print(f"  {pkg}: {info['risk_level']} ({info['risk_score']}/100)")


if __name__ == "__main__":
    main()
