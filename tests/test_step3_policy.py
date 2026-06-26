"""Integration tests for Step 3 policy/notice assembly + GDPR/CCPA mapping."""
from __future__ import annotations

from pathlib import Path

from pplib.io_utils import load_json
from step3_caption.generate import generate_captions
from step3_policy.assemble import assemble


def _run(dataset_dir: Path, tmp_path: Path):
    cap = tmp_path / "cap"
    generate_captions(str(dataset_dir), str(cap))
    out = tmp_path / "policy"
    summary = assemble(str(dataset_dir), str(cap), str(out))
    return summary, out


def test_assemble_produces_per_app_docs(dataset_dir, tmp_path):
    summary, out = _run(dataset_dir, tmp_path)
    assert summary["apps"], "expected at least one app policy"
    for pkg in summary["apps"]:
        app_dir = out / pkg.replace("/", "_")
        assert (app_dir / "notice.md").exists()
        assert (app_dir / "policy.md").exists()
    assert (out / "policy.json").exists()


def test_policy_has_gdpr_ccpa_mapping(dataset_dir, tmp_path):
    summary, out = _run(dataset_dir, tmp_path)
    any_pkg = next(iter(summary["apps"]))
    reqs = summary["apps"][any_pkg]["requirements"]
    # synthetic flows include sharing + ad/analytics -> both regimes triggered
    assert reqs["gdpr"] and reqs["ccpa"]
    policy_md = (out / any_pkg.replace("/", "_") / "policy.md").read_text(encoding="utf-8")
    assert "GDPR" in policy_md and "CCPA" in policy_md


def test_weak_inputs_yield_draft_banner(dataset_dir, tmp_path):
    summary, out = _run(dataset_dir, tmp_path)
    any_pkg = next(iter(summary["apps"]))
    assert summary["apps"][any_pkg]["weak"] is True
    notice = (out / any_pkg.replace("/", "_") / "notice.md").read_text(encoding="utf-8")
    assert "DRAFT" in notice


def test_sharing_section_lists_recipients(dataset_dir, tmp_path):
    summary, _ = _run(dataset_dir, tmp_path)
    any_pkg = next(iter(summary["apps"]))
    shared = summary["apps"][any_pkg]["sections"]["shared_with"]
    assert shared, "expected non-empty recipients for sharing flows"
