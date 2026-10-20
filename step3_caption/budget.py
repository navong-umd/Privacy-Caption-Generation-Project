"""
Purpose: Hard spending cap for paid LLM calls.
Input:   configs/llm.yaml (provider, per-model prices, max_tokens) + a USD limit.
Output:  Budget.reserve() refuses any call whose upper-bound cost would push spend past the limit;
         Budget.charge() records actual usage; callers record Budget.summary() with their outputs.

The input-token bound is the UTF-8 byte length of the request plus a fixed allowance for message
framing: byte-level tokenizers never emit more tokens than bytes, so the reservation cannot be
undercut by a tokenizer that splits text more finely than expected. The output bound is max_tokens.
"""
from __future__ import annotations

from typing import Dict, Optional

from step3_caption.llm_interface import GenerationResult

FRAMING_TOKENS = 64


class Budget:
    def __init__(self, limit_usd: float, price_in_per_mtok: float, price_out_per_mtok: float,
                 max_tokens: int):
        self.limit_usd = limit_usd
        self.price_in = price_in_per_mtok / 1e6
        self.price_out = price_out_per_mtok / 1e6
        self.max_tokens = max_tokens
        self.spent_usd = 0.0
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.stopped = False
        self._reserved = 0.0

    @classmethod
    def from_config(cls, cfg: Dict, limit_usd: float) -> "Budget":
        """Build from configs/llm.yaml. The offline mock is free; a paid provider needs both prices."""
        max_tokens = cfg.get("max_tokens", 220)
        name = cfg.get("provider", "mock")
        if name == "mock":
            return cls(limit_usd, 0.0, 0.0, max_tokens)
        conf = cfg.get("providers", {}).get(name, {})
        pin, pout = conf.get("price_in_per_mtok"), conf.get("price_out_per_mtok")
        if pin is None or pout is None:
            raise ValueError(f"configs/llm.yaml: set price_in_per_mtok and price_out_per_mtok for "
                             f"provider '{name}' before a budgeted run")
        return cls(limit_usd, float(pin), float(pout), max_tokens)

    def upper_bound_usd(self, request_text: str) -> float:
        input_bound = len(request_text.encode("utf-8")) + FRAMING_TOKENS
        return input_bound * self.price_in + self.max_tokens * self.price_out

    def reserve(self, request_text: str) -> bool:
        """True if a call with this request fits the remaining budget; False stops the run."""
        bound = self.upper_bound_usd(request_text)
        if self.spent_usd + bound > self.limit_usd:
            self.stopped = True
            return False
        self._reserved = bound
        return True

    def charge(self, result: Optional[str]) -> None:
        """Record one finished call; charges the reservation when the provider reported no usage."""
        pt = getattr(result, "prompt_tokens", 0) or 0
        ct = getattr(result, "completion_tokens", 0) or 0
        actual = pt * self.price_in + ct * self.price_out if (pt or ct) else self._reserved
        self.spent_usd += actual
        self.calls += 1
        self.prompt_tokens += pt
        self.completion_tokens += ct
        self._reserved = 0.0

    def summary(self) -> Dict:
        return {"limit_usd": self.limit_usd, "spent_usd": round(self.spent_usd, 6), "calls": self.calls,
                "prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens,
                "stopped_by_budget": self.stopped}


def generate_within_budget(provider, prompt: str, evidence: Dict,
                           budget: Budget) -> Optional[GenerationResult]:
    """Call provider.generate unless the budget refuses it; returns None when refused."""
    if not budget.reserve(prompt):
        return None
    try:
        result = provider.generate(prompt, evidence)
    except Exception:
        budget.charge(None)        # a failed call may still have been billed
        raise
    budget.charge(result)
    return result
