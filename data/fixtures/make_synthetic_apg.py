"""
Purpose: Generate a SYNTHETIC App Property Graph (APG CSVs) so the whole pipeline runs
         end-to-end with no real APK. Output mirrors the exact Stage 2 CSV schema.
Input:   --sources (the SuSi formatted_sources.csv, to borrow real source signatures),
         --apps N, --out DIR.
Output:  {AST,MCG,ICFG,DDG}_{nodes,edges}.csv under --out, for one or more synthetic apps.

EVERYTHING here is SYNTHETIC — flows are hand-constructed to exercise every code path
(source types, sink types, third-party SDKs, inter-procedural taint). Not a real APK.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd  # noqa: E402

from pplib.apg_model import APG, write_apg  # noqa: E402
from pplib.schema import BANNER_SYNTHETIC  # noqa: E402

# Representative SuSi source signatures (class->method) with their category.
# These are looked up in formatted_sources.csv at runtime to keep them realistic;
# the fallbacks here are used if a signature is absent from the catalog.
SOURCE_TEMPLATES = [
    ("android.location.LocationManager", "getLastKnownLocation", "LOCATION_INFORMATION"),
    ("android.telephony.TelephonyManager", "getDeviceId", "UNIQUE_IDENTIFIER"),
    ("android.telephony.TelephonyManager", "getSubscriberId", "UNIQUE_IDENTIFIER"),
    ("android.accounts.AccountManager", "getAccounts", "ACCOUNT_INFORMATION"),
    ("android.content.ContentResolver", "query", "CONTACT_INFORMATION"),
]

# (enclosing_class_suffix, sink_callee, sink_label, inter_procedural?)
SINK_TEMPLATES = [
    ("com.google.ads.AdRequestHelper", "okhttp3.RealCall->execute", "OkHttp", False),
    ("com.flurry.sdk.AnalyticsAgent", "java.net.HttpURLConnection->getOutputStream", "HttpURLConnection", False),
    ("ContactStore", "android.content.SharedPreferences$Editor->putString", "SharedPreferences", False),
    ("DebugLogger", "android.util.Log->d", "Log", False),
    ("LocationSharer", "android.content.Intent->putExtra", "Intent.extra", False),
    ("com.appsflyer.Sender", "java.net.URL->openConnection", "URL.openConnection", True),
]


def load_real_signatures(sources_csv: Path) -> Dict[Tuple[str, str], str]:
    """Map (class, method) -> category from the SuSi source catalog, if available."""
    if not sources_csv.exists():
        return {}
    df = pd.read_csv(sources_csv, dtype=str, keep_default_na=False)
    out: Dict[Tuple[str, str], str] = {}
    for r in df.to_dict("records"):
        out[(r.get("Class Name", ""), r.get("Method Name", ""))] = r.get("Category", "")
    return out


class _Builder:
    """Accumulates statements/edges for one method with a linear DDG+ICFG chain."""

    def __init__(self, apg: APG, method_id: str):
        self.apg = apg
        self.mid = method_id
        self.n = 0
        apg.methods[method_id] = {
            "id": method_id, "class": method_id.split("->")[0],
            "name": method_id.split("->")[1], "app_id": apg.app_id,
        }

    def add(self, mnemonic: str, code: str, callee: str = "") -> str:
        """Append a statement; chain it to the previous one via ICFG and DDG."""
        sid = f"{self.mid}_stmt_{self.n}"
        self.apg.statements[sid] = {
            "id": sid, "code": code, "type": mnemonic, "callee": callee,
            "method_id": self.mid, "app_id": self.apg.app_id,
        }
        self.apg.has_statement.append((self.mid, sid))
        if self.n > 0:
            prev = f"{self.mid}_stmt_{self.n - 1}"
            self.apg.icfg_next.append((prev, sid))
            self.apg.data_depends.append((prev, sid))  # linear data dependence
        self.n += 1
        return sid


def build_app(app_index: int, real_sigs: Dict[Tuple[str, str], str]) -> Tuple[APG, List[dict]]:
    """Build one synthetic app with several source->sink flows. Returns (apg, flow_specs)."""
    pkg = f"com.synthetic.app{app_index}"
    apg = APG(app_id=f"{pkg}@app{app_index}.apk")
    specs: List[dict] = []

    for fi, (sink_cls, sink_callee, sink_label, inter) in enumerate(SINK_TEMPLATES):
        src_cls, src_method, src_cat = SOURCE_TEMPLATES[fi % len(SOURCE_TEMPLATES)]
        src_cat = real_sigs.get((src_cls, src_method), src_cat)
        src_callee = f"{src_cls}->{src_method}"
        # Enclosing class: SDK classes keep their package prefix but get a per-app suffix
        # (so prefix-based SDK detection still works AND ids stay unique across apps).
        enc_cls = f"{sink_cls}{app_index}" if "." in sink_cls else f"{pkg}.{sink_cls}"

        if not inter:
            mid = f"{enc_cls}->flow{fi}"
            b = _Builder(apg, mid)
            b.add("invoke-virtual", f"invoke-virtual ..., {src_callee}", src_callee)
            b.add("move-result-object", "move-result-object v0")
            b.add("invoke-virtual", f"invoke-virtual v0, ..., {sink_callee}", sink_callee)
            specs.append({"source_callee": src_callee, "sink_callee": sink_callee,
                          "method_id": mid, "category": src_cat})
        else:
            # inter-procedural: getter holds source, caller invokes a sender that sinks it.
            getter = f"{pkg}.IdProvider->getId{fi}"
            sender = f"{enc_cls}->send{fi}"
            gb = _Builder(apg, getter)
            gb.add("invoke-virtual", f"invoke-virtual ..., {src_callee}", src_callee)
            gb.add("return-object", "return-object v0")
            sb = _Builder(apg, sender)
            sb.add("invoke-virtual", f"invoke-virtual ..., {getter}", getter)  # calls getter
            sb.add("move-result-object", "move-result-object v0")
            sb.add("invoke-virtual", f"invoke-virtual v0, ..., {sink_callee}", sink_callee)
            apg.calls.append((sender, getter))
            specs.append({"source_callee": src_callee, "sink_callee": sink_callee,
                          "method_id": sender, "category": src_cat})

    # rebuild classes/has_method from methods
    seen = set()
    for mid, m in apg.methods.items():
        cls = m["class"]
        apg.classes.setdefault(cls, {"name": cls, "app_id": apg.app_id})
        if (cls, mid) not in seen:
            apg.has_method.append((cls, mid))
            seen.add((cls, mid))
    return apg, specs


def merge_apgs(apgs: List[APG]) -> APG:
    """Merge several single-app APGs into one multi-app APG (uses first app_id as label)."""
    merged = APG(app_id="SYNTHETIC@multi.apk")
    for a in apgs:
        merged.classes.update(a.classes)
        merged.methods.update(a.methods)
        merged.statements.update(a.statements)
        merged.has_method += a.has_method
        merged.has_statement += a.has_statement
        merged.calls += a.calls
        merged.icfg_next += a.icfg_next
        merged.data_depends += a.data_depends
    return merged


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a SYNTHETIC APG fixture.")
    ap.add_argument("--sources", default=str(
        REPO_ROOT / "Document Analysis Module" / "output" / "formatted_sources.csv"))
    ap.add_argument("--apps", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--merge", action="store_true",
                    help="merge all apps into one APG dir (default writes per-app subdirs)")
    args = ap.parse_args()

    print(f"[{BANNER_SYNTHETIC}]")
    real_sigs = load_real_signatures(Path(args.sources))
    out = Path(args.out)
    apgs = [build_app(i, real_sigs)[0] for i in range(args.apps)]

    if args.merge:
        write_apg(merge_apgs(apgs), out)
        print(f"[+] Wrote merged synthetic APG ({args.apps} apps) -> {out}")
    else:
        write_apg(merge_apgs(apgs), out)  # default: single dir, multiple apps inside
        print(f"[+] Wrote synthetic APG with {args.apps} apps -> {out}")


if __name__ == "__main__":
    main()
