"""
Purpose: Unified Android privacy knowledge-base lookup (Phase 4).
Input:   configs/ppg.yaml + configs/sinks.yaml + configs/sdk_catalog.yaml + the two
         Document Analysis Module CSVs (personal_info_results.csv, formatted_sources.csv).
Output:  A single `KnowledgeBase.lookup(callee)` call returning everything the KB knows
         about a given API — its source classification (with tier + provenance), its sink
         classification, the associated Android permission, and the SDK purpose bucket
         (advertisement / analytics / functionality).

Wraps the existing `stage4_ppg/catalogs.py::SourceCatalog` and `SinkCatalog` so the
knowledge-base contract has one entry point. Every lookup carries the source tier
(known / susi / susi_method) so consumers can filter by precision, per the plan's
"Never silently invent the meaning of an Android API" requirement.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from pplib.io_utils import REPO_ROOT, load_yaml, get_logger

log = get_logger("knowledge")


@dataclass
class KnowledgeHit:
    """Everything the knowledge base can say about one API callee, with provenance."""

    callee: str
    # Source classification (populated only if the callee is a PI source)
    is_source: bool = False
    pi_category: str = ""
    pi_type: str = ""
    permission: str = ""
    source_tier: str = ""            # known | susi | susi_method
    source_provenance: str = ""       # human-readable citation
    # Sink classification (populated only if the callee is a data sink)
    is_sink: bool = False
    sink_type: str = ""               # network | storage | logging | ipc | serialization | heuristic_unknown
    sink_label: str = ""
    sink_known: bool = False          # False when only the egress-verb heuristic fired
    # Third-party SDK classification (from configs/sdk_catalog.yaml)
    sdk_purpose: str = ""             # advertisement | analytics | functionality | ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Human-readable provenance strings, keyed by the tier tag emitted by SourceCatalog.
# Kept here so consumers do not have to grep source code to know where a mapping came from.
_SOURCE_PROVENANCE = {
    "known": "configs/ppg.yaml::known_sources (hand-curated public-API allowlist)",
    "susi":  "Document Analysis Module/output/formatted_sources.csv "
             "(SuSi 17,801-signature catalog; Arzt et al. 2014)",
    "susi_method": "SuSi method-name-only match (opt-in via "
                   "configs/ppg.yaml::sources.formatted_match_by_method_name; recall mode, noisy)",
}


class KnowledgeBase:
    """Single-entry-point Android privacy knowledge base.

    Instantiate once per session and reuse — loading SuSi's 17,801 signatures on every
    call would be wasteful. Constructor loads:
      - ppg.yaml               known_sources + permission_map + source-tier settings
      - formatted_sources.csv  SuSi source catalog (Tier 2)
      - personal_info_results.csv  NL-derived PI type strings (enrichment on hits)
      - sinks.yaml             sink rule catalog + unknown-sink heuristic
      - sdk_catalog.yaml       third-party SDK package prefixes -> purpose

    All paths are read from configs/ppg.yaml relative to the repo root, matching the
    existing convention in stage4_ppg/build_ppg.py.
    """

    def __init__(
        self,
        ppg_config_path: str | Path = None,
        sinks_config_path: str | Path = None,
        sdk_catalog_path: str | Path = None,
        repo_root: Path = REPO_ROOT,
    ):
        # Lazy import so tests that don't need catalogs can still import this module.
        from stage4_ppg.catalogs import SourceCatalog, SinkCatalog

        ppg_config_path = Path(ppg_config_path) if ppg_config_path else repo_root / "configs" / "ppg.yaml"
        sinks_config_path = Path(sinks_config_path) if sinks_config_path else repo_root / "configs" / "sinks.yaml"
        sdk_catalog_path = Path(sdk_catalog_path) if sdk_catalog_path else repo_root / "configs" / "sdk_catalog.yaml"

        self.ppg_config = load_yaml(ppg_config_path)
        self.sources = SourceCatalog(self.ppg_config, repo_root)
        self.sinks = SinkCatalog(sinks_config_path)
        self.sdk_catalog = load_yaml(sdk_catalog_path)

        # Flatten sdk_catalog into a prefix -> purpose map, sorted by longest prefix first
        # so a match against com.google.android.gms.analytics wins over com.google.
        self._sdk_prefixes: list[tuple[str, str]] = []
        for purpose in ("advertisement", "analytics", "functionality_hint"):
            purpose_name = "functionality" if purpose == "functionality_hint" else purpose
            for prefix in self.sdk_catalog.get(purpose, []) or []:
                self._sdk_prefixes.append((prefix, purpose_name))
        self._sdk_prefixes.sort(key=lambda t: -len(t[0]))

        log.info(
            "KnowledgeBase loaded: %d curated sources, %d SuSi sources, %d SDK prefixes",
            len(self.sources.known), len(self.sources.susi), len(self._sdk_prefixes),
        )

    def lookup(self, callee: str, is_internal: bool = False) -> KnowledgeHit:
        """Return everything the knowledge base knows about one callee.

        callee: 'pkg.Class->method' (the same string produced by
                adapters.run_apg_csv._parse_callee and stored on Statement.callee).
        is_internal: True if the callee resolves to a method within the app being analysed
                     (skips the unknown-sink egress-verb heuristic, which is external-only).

        The returned KnowledgeHit is always populated for the callee field; every other
        field is populated only when the corresponding classifier fired. An unmatched
        callee comes back with is_source=False and is_sink=False.
        """
        hit = KnowledgeHit(callee=callee)
        if not callee or "->" not in callee:
            return hit

        # --- Source (with provenance tier) ---
        src = self.sources.classify(callee)
        if src is not None:
            hit.is_source = True
            hit.pi_category = src.category
            hit.pi_type = src.pi_type
            hit.permission = src.permission
            hit.source_tier = src.tier
            hit.source_provenance = _SOURCE_PROVENANCE.get(src.tier, src.tier)

        # --- Sink (catalog first, then heuristic for external unknowns) ---
        snk = self.sinks.classify(callee)
        if snk is None:
            snk = self.sinks.classify_unknown(callee, is_internal=is_internal)
        if snk is not None:
            hit.is_sink = True
            hit.sink_type = snk.sink_type
            hit.sink_label = snk.label
            hit.sink_known = snk.known

        # --- Third-party SDK purpose ---
        cls = callee.split("->", 1)[0]
        for prefix, purpose in self._sdk_prefixes:
            if cls.startswith(prefix):
                hit.sdk_purpose = purpose
                break

        return hit

    def stats(self) -> Dict[str, int]:
        """Counts for QA / doc consumers."""
        return {
            "curated_sources": len(self.sources.known),
            "susi_sources": len(self.sources.susi),
            "susi_method_index": len(self.sources.susi_methods),
            "personal_info_nl_enrichments": len(self.sources.pi_nl),
            "sink_rules": len(self.sinks.rules),
            "sdk_prefixes": len(self._sdk_prefixes),
            "permission_map_entries": len(self.sources.perm_map),
        }
