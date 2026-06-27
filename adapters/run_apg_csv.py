"""
Purpose: ADAPTER - generate Stage 2 APG CSVs from a real .apk WITHOUT Neo4j.
Input:   --apk path/to/app.apk, --out data/apg.
Output:  {AST,MCG,ICFG,DDG}_{nodes,edges}.csv (identical schema to the Stage 2 script).

FLAGGED ADAPTER: the canonical Stage 2 script
(`Static Code Analysis Module/.../androguard_analysis_APG_III_Update1Fixed_14.py`) hard-codes
foreign paths and requires a running Neo4j, so it cannot run as-is here. This mirrors its
graph-building logic (same AST/MCG/ICFG/DDG construction) and writes the same CSVs via
`pplib.apg_model.write_apg`, leaving the original script untouched. androguard is imported
lazily so the rest of the pipeline/tests never require it.

Run: python -m adapters.run_apg_csv --apk "Static Code Analysis Module/input/APK/sample.apk" --out data/apg
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional

from pplib.apg_model import APG, write_apg
from pplib.io_utils import get_logger

log = get_logger("run_apg_csv")


def _cls_dots(raw: str) -> str:
    return raw.strip("L;").replace("/", ".")


def _parse_callee(output: str) -> str:
    """Same invoke-callee parsing as Stage 2 (returns 'pkg.Class->method')."""
    if "->" not in output:
        return ""
    tokens = [t.strip() for t in output.split(",")]
    part = next((t for t in reversed(tokens) if "->" in t), tokens[-1])
    try:
        klass, rest = part.split("->", 1)
        return f"{_cls_dots(klass)}->{rest.split('(')[0]}"
    except Exception:
        return part


def _written_var(insn) -> Optional[str]:
    name = insn.get_name()
    try:
        out = insn.get_output()
    except Exception:
        out = ""
    if out and name.startswith(("move", "iput", "aput", "sput", "astore", "istore")):
        return out.split(",")[0].strip()
    return None


def _read_vars(insn) -> List[str]:
    try:
        args = insn.get_output().split(",")
    except Exception:
        return []
    return [a.strip() for a in args[1:] if a.strip()] if len(args) > 1 else []


def run_apg_csv(apk_path: str, out_dir: str | None, write: bool = True) -> APG:
    """Disassemble an APK with androguard and (optionally) write APG CSVs (mirrors Stage 2).

    write=False returns the in-memory APG without touching disk (used by the corpus runner to
    avoid writing ~1 GB of APG CSVs per app on a disk-constrained machine).
    """
    # Silence androguard's loguru DEBUG spam (a line PER method -> gigabytes of logs on real APKs).
    try:
        from loguru import logger as _loguru
        _loguru.remove()
    except Exception:
        pass
    from androguard.misc import AnalyzeAPK  # lazy: only needed for real APKs

    log.info("Analyzing APK: %s", apk_path)
    a, _, dx = AnalyzeAPK(apk_path)
    app_id = f"{a.get_package()}@{Path(apk_path).name}"
    apg = APG(app_id=app_id)

    for method in dx.get_methods():
        if method.is_external():
            continue
        cls = _cls_dots(method.class_name)
        mid = f"{cls}->{method.name}"
        apg.methods.setdefault(mid, {"id": mid, "class": cls, "name": method.name, "app_id": app_id})
        apg.classes.setdefault(cls, {"name": cls, "app_id": app_id})
        apg.has_method.append((cls, mid))

        for _, call, _ in method.get_xref_to():
            callee = f"{_cls_dots(call.class_name)}->{call.name}"
            apg.calls.append((mid, callee))

        m = method.get_method()
        if not m:
            continue
        defs: Dict[str, str] = {}
        for i, ins in enumerate(m.get_instructions()):
            sid = f"{mid}_stmt_{i}"
            mnem = ins.get_name()
            code = ins.get_output() or ""
            callee = _parse_callee(code) if mnem.startswith("invoke") else ""
            apg.statements[sid] = {"id": sid, "code": code, "type": mnem, "callee": callee,
                                   "method_id": mid, "app_id": app_id}
            apg.has_statement.append((mid, sid))
            if i > 0:
                apg.icfg_next.append((f"{mid}_stmt_{i-1}", sid))
            w = _written_var(ins)
            for v in _read_vars(ins):
                if v in defs:
                    apg.data_depends.append((defs[v], sid))
            if w:
                defs[w] = sid

    if write and out_dir:
        write_apg(apg, out_dir)
        log.info("Wrote APG CSVs: %s", apg.summary())
    else:
        log.info("Built APG in memory: %s", apg.summary())
    return apg


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate APG CSVs from an APK (adapter).")
    ap.add_argument("--apk", required=True)
    ap.add_argument("--out", default="data/apg")
    args = ap.parse_args()
    apg = run_apg_csv(args.apk, args.out)
    print(f"[+] APG CSVs written to {args.out} ({apg.summary()})")


if __name__ == "__main__":
    main()
