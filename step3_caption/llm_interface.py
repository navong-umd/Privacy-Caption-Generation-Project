"""
Purpose: Pluggable LLM provider interface for caption generation.
Input:   a prompt string + a structured `evidence` dict (labels + code/taint facts).
Output:  a 4-5 line human-readable privacy caption (GenerationResult: str + token usage).

The default `mock` provider is fully OFFLINE and deterministic (no network, no keys) so the
pipeline and tests always run. Real providers (anthropic/openai/llama/deepseek) import their
SDK lazily and read the API key from an env var; they are never exercised in tests.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional

from pplib.io_utils import get_logger

log = get_logger("llm")

# Human-readable phrasing maps for the deterministic mock.
_PI_PHRASE = {
    "LOCATION_INFORMATION": "location", "UNIQUE_IDENTIFIER": "device identifier",
    "PHONE_INFORMATION": "phone number", "ACCOUNT_INFORMATION": "account information",
    "CONTACT_INFORMATION": "contacts", "CALENDAR_INFORMATION": "calendar",
    "SMS_MMS": "text messages", "BROWSER_INFORMATION": "browsing history",
    "NETWORK_INFORMATION": "network information", "BLUETOOTH_INFORMATION": "Bluetooth data",
    "IMAGE": "photos", "AUDIO": "microphone audio",
}
_SINK_PHRASE = {
    "network": "a remote server over the network", "storage": "local device storage",
    "logging": "the system log", "ipc": "another app component",
    "serialization": "a serialized data stream", "heuristic_unknown": "an external destination",
}
_PURPOSE_PHRASE = {
    "Advertisement": "for advertising", "Analytics": "for analytics and usage measurement",
    "Functionality": "to provide core app functionality", "Other": "for an unspecified purpose",
}


class GenerationResult(str):
    """Generated text plus the token usage the provider reported (0 when unknown).

    A str subclass, so callers that only need the text are unaffected."""

    prompt_tokens: int
    completion_tokens: int

    def __new__(cls, text: str, prompt_tokens: int = 0, completion_tokens: int = 0):
        obj = super().__new__(cls, text)
        obj.prompt_tokens = prompt_tokens
        obj.completion_tokens = completion_tokens
        return obj


class LLMProvider:
    """Base provider: real providers override `generate`."""

    def generate(self, prompt: str, evidence: Dict) -> GenerationResult:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Deterministic, offline caption generator (template over the evidence dict)."""

    def generate(self, prompt: str, evidence: Dict) -> GenerationResult:
        category = evidence.get("pi_category") or evidence.get("category", "")
        pi = _PI_PHRASE.get(category, evidence.get("pi_type") or "personal data")
        practice = evidence.get("practice", [])
        purpose = evidence.get("purpose", [])
        sink = _SINK_PHRASE.get(evidence.get("sink_type", ""), "an external destination")

        verb = "accesses"
        if "Collecting" in practice:
            verb = "collects"
        lines = [f"This app {verb} your {pi}."]
        if "Processing" in practice:
            lines.append(f"It processes the {pi} inside the app.")
        if "Sharing" in practice:
            lines.append(f"The {pi} is sent to {sink}.")
        else:
            lines.append(f"The {pi} is written to {sink}.")
        purps = [_PURPOSE_PHRASE.get(p, "") for p in purpose if p in _PURPOSE_PHRASE]
        if purps:
            lines.append("This is done " + " and ".join(purps) + ".")
        threat = evidence.get("privacy_threat", "")
        if threat:
            lines.append(f"Privacy threat (LINDDUN): {threat}.")
        return GenerationResult("\n".join(lines[:5]))


class _ApiProvider(LLMProvider):
    """Shared logic for real chat providers (key-gated, lazy import)."""

    def __init__(self, name: str, conf: Dict, gen: Dict):
        self.name = name
        self.model = conf.get("model", "")
        self.key = os.environ.get(conf.get("api_key_env", ""), "")
        self.base_url = os.environ.get(conf.get("base_url_env", ""), "") or None
        self.gen = gen
        if not self.key:
            raise RuntimeError(
                f"Provider '{name}' needs env var {conf.get('api_key_env')} (no key set). "
                f"Use provider: mock for offline runs.")

    def generate(self, prompt: str, evidence: Dict) -> GenerationResult:  # pragma: no cover (needs network/key)
        if self.name == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=self.key)
            msg = client.messages.create(
                model=self.model, max_tokens=self.gen.get("max_tokens", 220),
                temperature=self.gen.get("temperature", 0.2),
                messages=[{"role": "user", "content": prompt}])
            return GenerationResult(msg.content[0].text.strip(),
                                    msg.usage.input_tokens, msg.usage.output_tokens)
        # openai-compatible (openai / llama / deepseek via base_url)
        from openai import OpenAI
        client = OpenAI(api_key=self.key, base_url=self.base_url)
        resp = client.chat.completions.create(
            model=self.model, max_tokens=self.gen.get("max_tokens", 220),
            temperature=self.gen.get("temperature", 0.2),
            messages=[{"role": "user", "content": prompt}])
        usage = resp.usage
        return GenerationResult(resp.choices[0].message.content.strip(),
                                getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0))


def get_provider(cfg: Dict) -> LLMProvider:
    """Factory: return the configured provider (mock by default)."""
    name = cfg.get("provider", "mock")
    if name == "mock":
        return MockProvider()
    conf = cfg.get("providers", {}).get(name)
    if not conf:
        raise ValueError(f"Unknown provider '{name}'")
    return _ApiProvider(name, conf, cfg)
