"""Spending cap for paid LLM calls: never start a call that could cross the limit."""
from __future__ import annotations

import pytest

from step3_caption.budget import FRAMING_TOKENS, Budget, generate_within_budget
from step3_caption.llm_interface import GenerationResult


class _PricedProvider:
    """Fake paid provider that reports whatever usage it is told to."""

    def __init__(self, prompt_tokens: int, completion_tokens: int):
        self.usage = (prompt_tokens, completion_tokens)
        self.calls = 0

    def generate(self, prompt, evidence):
        self.calls += 1
        return GenerationResult("caption", *self.usage)


def test_second_call_that_would_cross_the_limit_is_never_made():
    # $1 per 1k input / output tokens; 100-byte prompt -> bound (100+64) in + 100 out = $0.264
    budget = Budget(limit_usd=0.4, price_in_per_mtok=1000, price_out_per_mtok=1000, max_tokens=100)
    provider = _PricedProvider(prompt_tokens=150, completion_tokens=100)
    prompt = "x" * 100
    assert generate_within_budget(provider, prompt, {}, budget) is not None
    assert generate_within_budget(provider, prompt, {}, budget) is None
    assert provider.calls == 1
    s = budget.summary()
    assert s["stopped_by_budget"] is True and s["spent_usd"] <= 0.4 and s["calls"] == 1


def test_bound_holds_when_tokenizer_splits_finer_than_len_over_4():
    budget = Budget(limit_usd=10, price_in_per_mtok=1000, price_out_per_mtok=1000, max_tokens=50)
    prompt = "é" * 200                                   # 400 UTF-8 bytes; len/4 would guess 50 tokens
    reported = 380                                       # far above len/4, still within the byte bound
    assert reported <= len(prompt.encode("utf-8")) + FRAMING_TOKENS
    bound = budget.upper_bound_usd(prompt)
    result = generate_within_budget(_PricedProvider(reported, 50), prompt, {}, budget)
    assert result is not None and budget.spent_usd <= bound


def test_missing_usage_is_charged_at_the_reservation():
    budget = Budget(limit_usd=10, price_in_per_mtok=1000, price_out_per_mtok=1000, max_tokens=10)

    class _NoUsage:
        def generate(self, prompt, evidence):
            return "plain string, no usage"

    generate_within_budget(_NoUsage(), "abc", {}, budget)
    assert budget.spent_usd == pytest.approx(budget.upper_bound_usd("abc"))


def test_failed_call_is_charged_conservatively():
    budget = Budget(limit_usd=10, price_in_per_mtok=1000, price_out_per_mtok=1000, max_tokens=10)

    class _Boom:
        def generate(self, prompt, evidence):
            raise RuntimeError("timeout")

    with pytest.raises(RuntimeError):
        generate_within_budget(_Boom(), "abc", {}, budget)
    assert budget.spent_usd == pytest.approx(budget.upper_bound_usd("abc")) and budget.calls == 1


def test_from_config_reads_prices_and_max_tokens_for_a_paid_provider():
    cfg = {"provider": "anthropic", "max_tokens": 220,
           "providers": {"anthropic": {"model": "m", "price_in_per_mtok": 3, "price_out_per_mtok": 15}}}
    budget = Budget.from_config(cfg, 5.0)
    prompt = "x" * 1000
    expected = (1000 + FRAMING_TOKENS) * 3 / 1e6 + 220 * 15 / 1e6
    assert budget.upper_bound_usd(prompt) == pytest.approx(expected) and budget.limit_usd == 5.0


def test_mock_is_free_and_paid_provider_needs_prices():
    assert Budget.from_config({"provider": "mock"}, 0.0).upper_bound_usd("anything") == 0.0
    cfg = {"provider": "anthropic", "providers": {"anthropic": {"model": "m", "price_in_per_mtok": None}}}
    with pytest.raises(ValueError, match="price_in_per_mtok"):
        Budget.from_config(cfg, 5.0)
