"""
Purpose: Central schema constants shared across the PPG / PRCS / ADPPG / ConvGNN code.
Input:   none (constants only).
Output:  node labels, edge types, PAcT taxonomy, and banner strings used everywhere.

Keeping these in one place means the APG->PPG->PRCS->PyG contract is defined once.
"""
from __future__ import annotations

# --- APG schema produced by Stage 2 (verified against androguard_analysis_APG_*.py) ---
APG_NODE_COLUMNS = ["id", "label", "type", "code", "callee", "app_id"]
APG_EDGE_COLUMNS = ["start_id", "end_id", "type", "app_id"]

# APG node labels / edge types that already exist upstream.
APG_NODE_LABELS = ["Class", "Method", "Statement"]
APG_EDGE_TYPES = ["HAS_METHOD", "HAS_STATEMENT", "CALLS", "ICFG_NEXT", "DATA_DEPENDS"]

# --- PPG overlay (Stage 4) adds these on top of the APG ---
PPG_NODE_LABELS = APG_NODE_LABELS + ["DataItem", "Source", "Sink", "Store", "Component"]
PPG_EDGE_TYPES = APG_EDGE_TYPES + ["TAINT_FLOW", "PRIVACY_RELATION"]

# Extra Statement properties written by the privacy overlay.
PPG_STATEMENT_PROPS = [
    "is_source", "is_sink", "pi_type", "permission", "sink_type",
    "privacy_threat", "tainted", "sdk", "sdk_purpose",
]

# PPG CSV columns mirror the APG style plus the overlay props + the semantic description.
# `what_it_does` is a human-readable, per-node explanation (Neo4j display + PRCS evidence).
PPG_NODE_COLUMNS = APG_NODE_COLUMNS + PPG_STATEMENT_PROPS + ["what_it_does"]
# `taint_rule` (Phase 5) is per-edge provenance for TAINT_FLOW edges: which rule
# (ddg | icfg | call_arg | call_ret) produced this edge. Empty for non-TAINT_FLOW
# edges. Any reviewer inspecting a privacy relationship can answer "why does this
# edge exist?" from this column alone.
PPG_EDGE_COLUMNS = ["start_id", "end_id", "type", "app_id", "pi_type",
                    "privacy_threat", "taint_rule"]

# --- PAcT taxonomy (both heads multi-label) ---
PRACTICE_LABELS = ["Processing", "Collecting", "Sharing", "Other"]
PURPOSE_LABELS = ["Functionality", "Advertisement", "Analytics", "Other"]

# --- LINDDUN GO threat categories (canonical short names) ---
LINDDUN_CATEGORIES = [
    "Linking", "Identifying", "Non-repudiation", "Detecting",
    "Data Disclosure", "Unawareness", "Non-compliance",
]

# --- Banners: any artifact derived from heuristic/synthetic data MUST carry one ---
BANNER_BOOTSTRAP = "BOOTSTRAP — not a real result (computed on WEAK/SYNTHETIC labels)"
BANNER_WEAK = "WEAK — not ground truth (heuristic auto-label, awaits human Codr annotation)"
BANNER_SYNTHETIC = "SYNTHETIC — generated fixture, not from a real APK"
