"""
Purpose: Generate a human-readable `what_it_does` description for every PPG node, so the
         Neo4j display (and PRCS evidence) shows BOTH the raw code and what it means.
Input:   a PPG node (id + attrs dict). Optionally an LLM provider + a disk cache.
Output:  a one-line semantic description string (+ its provenance: 'rule' or 'llm:<name>').

The default path is fully OFFLINE and deterministic (a template over the node's privacy
facts) so the pipeline and tests need no API key and stay cheap even on million-node real
PPGs. An optional LLM provider (PCapGen-Extractor style) can enrich salient nodes; its
output is cached on disk and tagged 'llm:<provider>' so LLM-derived text is always marked.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from pplib.io_utils import get_logger

log = get_logger("semantics")

# Reused phrasing (kept local so this module has no cross-package import).
_PI_PHRASE = {
    "LOCATION_INFORMATION": "location", "UNIQUE_IDENTIFIER": "device identifier",
    "PHONE_INFORMATION": "phone number", "ACCOUNT_INFORMATION": "account information",
    "CONTACT_INFORMATION": "contacts", "CALENDAR_INFORMATION": "calendar",
    "SMS_MMS": "text messages", "BROWSER_INFORMATION": "browsing history",
    "NETWORK_INFORMATION": "network information", "BLUETOOTH_INFORMATION": "Bluetooth data",
    "DATABASE_INFORMATION": "database records", "SYNCHRONIZATION_DATA": "sync data",
    "AUDIO_INPUT_OUTPUT": "microphone audio", "IMAGE": "photos",
}
_SINK_PHRASE = {
    "network": "a remote server over the network", "storage": "local device storage",
    "logging": "the system log", "ipc": "another app component",
    "serialization": "a serialized data stream", "heuristic_unknown": "an external destination",
}


def _short(sig: str) -> str:
    """Shorten 'pkg.Outer.Class->method' -> 'Class.method'; 'a.b.C' -> 'C'."""
    s = str(sig or "")
    if "->" in s:
        cls, meth = s.split("->", 1)
        return f"{cls.rsplit('.', 1)[-1]}.{meth}"
    return s.rsplit(".", 1)[-1] if "." in s else s


def _pi(pi_type: str) -> str:
    if not pi_type:
        return "personal data"
    return _PI_PHRASE.get(pi_type, pi_type.replace("_", " ").lower())


def describe_node(node_id: str, d: Dict) -> str:
    """Deterministic, offline one-line description of a PPG node from its attributes."""
    label = d.get("label", "")

    if label == "Source" or d.get("is_source"):
        api = _short(d.get("api") or d.get("callee") or "a system API")
        desc = f"Reads the user's {_pi(d.get('pi_type') or d.get('category'))} via {api}"
        perm = d.get("permission")
        if perm:
            desc += f" (requires {_short(perm)})"
        return desc

    if label == "Sink" or d.get("is_sink"):
        api = _short(d.get("api") or d.get("callee") or "an API")
        st = d.get("sink_type", "")
        verb = "Sends data to" if st in ("network", "ipc") else "Writes data to"
        return f"{verb} {_SINK_PHRASE.get(st, 'an external destination')} via {api}"

    if label == "DataItem":
        return f"Personal data item: {_pi(d.get('category'))}"
    if label == "Store":
        return f"Local data store ({d.get('store_label', 'storage')})"
    if label == "Component":
        return f"App component / IPC endpoint ({d.get('component_label', 'component')})"
    if label == "Method":
        return f"Method {_short(d.get('name') or node_id)} of class {_short(d.get('cls', ''))}"
    if label == "Class":
        return f"Application class {_short(node_id)}"

    # Statement (default)
    if d.get("tainted"):
        base = f"Carries tainted {_pi(d.get('pi_type'))}"
    else:
        base = "Executes a code statement"
    callee = d.get("callee")
    if callee:
        base += f" calling {_short(callee)}"
    threat = d.get("privacy_threat")
    if threat:
        base += f" — privacy threat: {threat}"
    return base


class WhatItDoesCache:
    """Tiny JSON-backed cache so (esp. LLM-derived) descriptions are computed once."""

    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path) if path else None
        self._d: Dict[str, str] = {}
        if self.path and self.path.exists():
            try:
                self._d = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:  # corrupt cache is non-fatal
                self._d = {}

    @staticmethod
    def key(node_id: str, d: Dict) -> str:
        facts = "|".join(str(d.get(k, "")) for k in
                         ("label", "callee", "api", "pi_type", "category", "sink_type",
                          "is_source", "is_sink", "tainted", "privacy_threat"))
        return hashlib.sha1(f"{facts}".encode("utf-8")).hexdigest()[:16]

    def get(self, k: str) -> Optional[str]:
        return self._d.get(k)

    def set(self, k: str, v: str) -> None:
        self._d[k] = v

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._d, ensure_ascii=False, indent=0), encoding="utf-8")


def _llm_describe(node_id: str, d: Dict, provider) -> str:  # pragma: no cover (needs key)
    """PCapGen-Extractor-style one-line description via a real LLM provider."""
    prompt = ("In ONE short sentence, say what this Android statement does, focusing on any "
              "personal-data handling. Be concrete and non-speculative.\n"
              f"code: {d.get('code', '')}\ncalls: {d.get('callee', '')}\n"
              f"pi_type: {d.get('pi_type', '')}  sink_type: {d.get('sink_type', '')}")
    return provider.generate(prompt, {"pi_type": d.get("pi_type", ""), "code": d.get("code", "")}).strip()


def describe(node_id: str, d: Dict, provider=None, cache: Optional[WhatItDoesCache] = None,
             llm_for_salient_only: bool = True) -> Tuple[str, str]:
    """Return (what_it_does, provenance). Deterministic unless a real provider is supplied."""
    k = cache.key(node_id, d) if cache else None
    if cache and k in cache._d:
        return cache._d[k], "cache"

    salient = bool(d.get("is_source") or d.get("is_sink") or d.get("tainted"))
    use_llm = provider is not None and getattr(provider, "name", "mock") != "mock" \
        and (salient or not llm_for_salient_only)
    if use_llm:
        try:
            text, src = _llm_describe(node_id, d, provider), f"llm:{getattr(provider, 'name', 'llm')}"
        except Exception as e:  # fall back to deterministic on any LLM failure
            log.warning("LLM describe failed (%s); using rule-based", e)
            text, src = describe_node(node_id, d), "rule"
    else:
        text, src = describe_node(node_id, d), "rule"

    if cache and k:
        cache.set(k, text)
    return text, src


def enrich_graph(G, provider=None, cache: Optional[WhatItDoesCache] = None) -> int:
    """Set `what_it_does` (+ `what_it_does_src`) on every node of a PPG. Returns node count."""
    n = 0
    for nid, d in G.nodes(data=True):
        text, src = describe(nid, d, provider=provider, cache=cache)
        d["what_it_does"] = text
        d["what_it_does_src"] = src
        n += 1
    if cache:
        cache.save()
    return n
