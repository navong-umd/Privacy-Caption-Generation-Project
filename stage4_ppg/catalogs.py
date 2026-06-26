"""
Purpose: Match APG statements against PI SOURCES and data SINKS.
Input:   ppg config, the SuSi formatted_sources.csv, personal_info_results.csv, sinks.yaml.
Output:  SourceCatalog / SinkCatalog objects exposing classify(callee) -> tag or None.

Sources use 3 tiers: curated known_sources (precision) + SuSi catalog (recall) +
personal_info_results.csv (natural-language pi_type enrichment).
Sinks use the editable rule catalog plus an unknown-sink heuristic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from pplib.io_utils import get_logger, load_yaml

log = get_logger("catalogs")


@dataclass
class SourceHit:
    category: str
    permission: str
    pi_type: str           # natural-language type if known, else the category
    tier: str              # known | susi | susi_method


class SourceCatalog:
    """Decides whether a callee 'class->method' is a personal-information source."""

    def __init__(self, cfg: dict, repo_root: Path):
        self.cfg = cfg
        s = cfg.get("sources", {})
        self.perm_map: Dict[str, str] = cfg.get("permission_map", {})
        self.exclude = set(s.get("exclude_categories", []))
        self.by_method_name = bool(s.get("formatted_match_by_method_name", False))

        # Tier 1: curated public-API signatures.
        self.known: Dict[str, str] = {}
        if s.get("use_known_sources", True):
            for row in cfg.get("known_sources", []):
                self.known[f"{row['class']}->{row['method']}"] = row["category"]

        # Tier 2: SuSi catalog (exact class->method, optional method-name index).
        self.susi: Dict[str, str] = {}
        self.susi_methods: Dict[str, str] = {}
        if s.get("use_formatted_sources", True):
            self._load_susi(repo_root / cfg["paths"]["formatted_sources_csv"])

        # Tier 3: natural-language pi_type enrichment.
        self.pi_nl: Dict[str, str] = {}
        if s.get("use_personal_info", True):
            self._load_personal_info(repo_root / cfg["paths"]["personal_info_csv"])

    def _load_susi(self, path: Path) -> None:
        if not path.exists():
            log.warning("formatted_sources.csv not found at %s", path)
            return
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        for r in df.to_dict("records"):
            cat = r.get("Category", "")
            if not cat or cat in self.exclude:
                continue
            key = f"{r.get('Class Name', '')}->{r.get('Method Name', '')}"
            self.susi[key] = cat
            self.susi_methods.setdefault(r.get("Method Name", ""), cat)
        log.info("Loaded %d SuSi source signatures", len(self.susi))

    def _load_personal_info(self, path: Path) -> None:
        if not path.exists():
            log.warning("personal_info_results.csv not found at %s", path)
            return
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        for r in df.to_dict("records"):
            pi = (r.get("Personal Information", "") or "").strip()
            if pi:
                key = f"{r.get('Classname', '')}->{r.get('Methodname', '')}"
                self.pi_nl[key] = pi

    def classify(self, callee: str) -> Optional[SourceHit]:
        """Return a SourceHit if callee is a PI source, else None."""
        if not callee or "->" not in callee:
            return None
        cat, tier = None, ""
        if callee in self.known:
            cat, tier = self.known[callee], "known"
        elif callee in self.susi:
            cat, tier = self.susi[callee], "susi"
        elif self.by_method_name:
            method = callee.split("->", 1)[1]
            if method in self.susi_methods:
                cat, tier = self.susi_methods[method], "susi_method"
        if cat is None:
            return None
        pi_nl = self.pi_nl.get(callee, cat)
        perm = self.perm_map.get(cat, "")
        return SourceHit(category=cat, permission=perm, pi_type=pi_nl, tier=tier)


@dataclass
class SinkHit:
    sink_type: str
    label: str
    known: bool


class SinkCatalog:
    """Decides whether a callee 'class->method' is a data sink (known or heuristic)."""

    def __init__(self, sinks_yaml: Path):
        data = load_yaml(sinks_yaml)
        self.rules = data.get("rules", [])
        h = data.get("unknown_sink_heuristics", {})
        self.heur_enabled = bool(h.get("enabled", True))
        self.egress_verbs = [v.lower() for v in h.get("egress_verbs", [])]
        self.heur_type = h.get("sink_type", "heuristic_unknown")
        self._compiled = [(r["match"], r["value"], r["sink_type"], r["label"],
                           re.compile(r["value"]) if r["match"] == "regex" else None)
                          for r in self.rules]

    def classify(self, callee: str) -> Optional[SinkHit]:
        """Return a SinkHit from the catalog, else None (heuristic handled separately)."""
        if not callee:
            return None
        for kind, value, stype, label, rx in self._compiled:
            if kind == "exact" and callee == value:
                return SinkHit(stype, label, True)
            if kind == "endswith" and callee.endswith(value):
                return SinkHit(stype, label, True)
            if kind == "regex" and rx.search(callee):
                return SinkHit(stype, label, True)
        return None

    def classify_unknown(self, callee: str, is_internal: bool) -> Optional[SinkHit]:
        """Heuristic: external callee whose method name implies data egress is a likely sink."""
        if not self.heur_enabled or not callee or "->" not in callee or is_internal:
            return None
        method = callee.split("->", 1)[1].lower()
        if any(v in method for v in self.egress_verbs):
            return SinkHit(self.heur_type, f"heuristic:{callee.split('->',1)[1]}", False)
        return None
