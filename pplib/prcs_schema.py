"""
Purpose: Versioned schema constants for the PRCS record (Phase 7).
Input:   none (constants only).
Output:  PRCS_SCHEMA_VERSION, PRCS_REQUIRED_FIELDS, PRCS_INDEX_COLUMNS.

Every PRCS JSON written by step2_prcs.extract_prcs carries a `schema_version`
field so downstream consumers (dataset assembly, caption generation, policy
assembly, evaluation) can refuse to load an incompatible record instead of
silently misreading it.

Keep in sync with research/PRCS_SCHEMA.md.
"""
from __future__ import annotations

PRCS_SCHEMA_VERSION = "1.0.0"

# Fields every serialized PRCS JSON MUST have populated. Enforced by
# tests/test_prcs_schema.py against every generated record.
PRCS_REQUIRED_FIELDS = [
    # identity + schema
    "prcs_id",
    "schema_version",
    # provenance: which APK produced this slice
    "app_package",
    "apk_filename",
    # source-code location: which method holds the source statement
    "class_name",
    "method_name",
    "method_signature",
    # privacy semantics (from the KB via PPG)
    "source_api",
    "sink_api",
    "sink_type",
    "sink_label",
    "pi_type",
    "pi_category",
    "permission",
    "privacy_threat",
    # trace: the path from source to sink and how each hop was justified
    "hop_count",
    "taint_path",
    "taint_rules",
    "involved_methods",
    # rendered snippet + structural subgraph
    "code_snippet",
    "subgraph",
]

# Flat index columns written to prcs_index.csv (subgraph + snippet live in the per-PRCS JSON).
PRCS_INDEX_COLUMNS = [
    "prcs_id",
    "schema_version",
    "app_package",
    "apk_filename",
    "class_name",
    "method_name",
    "method_signature",
    "source_api",
    "sink_api",
    "sink_type",
    "pi_type",
    "permission",
    "privacy_threat",
    "hop_count",
    "n_nodes",
    "n_edges",
]
