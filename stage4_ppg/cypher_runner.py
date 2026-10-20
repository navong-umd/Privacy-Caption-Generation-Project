"""
Purpose: Thin runner for the PPG Cypher query library (configs/queries.cypher).
Input:   the .cypher library + a query name + params (--app-id/--source-id/--sink-id/--node-id).
Output:  OFFLINE: prints the named (optionally param-substituted) Cypher — no DB needed.
         ONLINE:  with --run + a reachable Neo4j, executes it and prints the records.

Lets you (and the demo/tests) list, inspect, and render queries with NO database, while
still being the one place that executes them against a live Neo4j for the display.

Run: python -m stage4_ppg.cypher_runner --list
     python -m stage4_ppg.cypher_runner --show app_ppg_overlay --app-id "com.x@x.apk"
     python -m stage4_ppg.cypher_runner --run list_sources --app-id "com.x@x.apk"
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from pplib.io_utils import get_logger, load_yaml
from stage4_ppg.neo4j_loader import connection_settings

log = get_logger("cypher_runner")
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LIB = REPO_ROOT / "configs" / "queries.cypher"
DEFAULT_CONFIG = REPO_ROOT / "configs" / "ppg.yaml"
_NAME_RE = re.compile(r"^//\s*name:\s*(\S+)\s*$")
_DESTRUCTIVE = {"clear_app"}


@dataclass
class CypherQuery:
    name: str
    description: str
    cypher: str
    destructive: bool = False

    def params(self) -> List[str]:
        """Parameter names ($foo) referenced by the query."""
        return sorted(set(re.findall(r"\$(\w+)", self.cypher)))

    def render(self, **values) -> str:
        """Substitute $param with quoted literals for offline display (unset params kept)."""
        out = self.cypher
        for k, v in values.items():
            if v is None:
                continue
            lit = v if isinstance(v, (int, float)) else f"'{v}'"
            out = re.sub(rf"\${k}\b", str(lit), out)
        return out


def load_library(path: str | Path = DEFAULT_LIB) -> Dict[str, CypherQuery]:
    """Parse the .cypher library into {name: CypherQuery}."""
    text = Path(path).read_text(encoding="utf-8")
    queries: Dict[str, CypherQuery] = {}
    name: Optional[str] = None
    desc: List[str] = []
    body: List[str] = []

    def flush():
        if name and body:
            queries[name] = CypherQuery(
                name=name, description=" ".join(desc).strip(),
                cypher="\n".join(body).strip(), destructive=name in _DESTRUCTIVE)

    for line in text.splitlines():
        m = _NAME_RE.match(line)
        if m:
            flush()
            name, desc, body = m.group(1), [], []
            continue
        if name is None:
            continue  # header/banner before the first query
        if line.strip().startswith("//"):
            desc.append(line.strip().lstrip("/").strip())
        elif line.strip():
            body.append(line)
    flush()
    return queries


def run_query(q: CypherQuery, params: Dict, neo4j_cfg: Dict) -> List[Dict]:
    """Execute a query against Neo4j and return rows as dicts. Requires neo4j + a server."""
    try:
        from neo4j import GraphDatabase
    except ImportError as e:  # offline-safe: clear guidance instead of a crash
        raise RuntimeError("The 'neo4j' package is not installed — use --show for offline "
                           "rendering, or `pip install neo4j` and start a server to --run.") from e
    conf = connection_settings(neo4j_cfg)
    driver = GraphDatabase.driver(conf["uri"], auth=(conf["user"], conf["password"]))
    try:
        with driver.session() as s:
            return [r.data() for r in s.run(q.cypher, params or {})]
    finally:
        driver.close()


def _collect_params(args) -> Dict:
    p = {}
    for key, val in (("app_id", args.app_id), ("source_id", args.source_id),
                     ("sink_id", args.sink_id), ("node_id", args.node_id)):
        if val is not None:
            p[key] = val
    return p


def main() -> None:
    ap = argparse.ArgumentParser(description="Render/run the PPG Cypher query library.")
    ap.add_argument("--library", default=str(DEFAULT_LIB))
    ap.add_argument("--config", default=str(DEFAULT_CONFIG), help="config with the neo4j: uri/user block")
    ap.add_argument("--list", action="store_true", help="list query names + descriptions")
    ap.add_argument("--show", metavar="NAME", help="print the (rendered) Cypher, offline")
    ap.add_argument("--run", metavar="NAME", help="execute against Neo4j (needs server)")
    ap.add_argument("--app-id")
    ap.add_argument("--source-id")
    ap.add_argument("--sink-id")
    ap.add_argument("--node-id")
    args = ap.parse_args()

    lib = load_library(args.library)

    if args.list or not (args.show or args.run):
        print(f"\n{len(lib)} queries in {args.library}:\n")
        for q in lib.values():
            flag = "  [DESTRUCTIVE]" if q.destructive else ""
            print(f"  {q.name:<20} params={q.params()}{flag}\n      {q.description}")
        return

    name = args.show or args.run
    if name not in lib:
        raise SystemExit(f"No such query '{name}'. Use --list.")
    q = lib[name]
    params = _collect_params(args)

    if args.show:
        print(q.render(**params))
        return

    if q.destructive:
        log.warning("Refusing to auto-run DESTRUCTIVE query '%s'. Run it manually in Neo4j Browser.", name)
        return
    rows = run_query(q, params, load_yaml(args.config).get("neo4j", {}))
    print(f"[{len(rows)} rows]")
    for r in rows[:50]:
        print(r)


if __name__ == "__main__":
    main()
