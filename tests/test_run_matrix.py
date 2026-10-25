"""The matrix runner: ten manifests, resumable arms, condition G on predictions, budget stops,
and the test-set lock."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

pytest.importorskip("torch")
pytest.importorskip("torch_geometric")

from pplib.experiment import load_experiment
from pplib.experiment_matrix import CAPTION_ARMS, EXP_ID, FINAL_ARMS, SEEDS
from pplib.matrix_stats import label_matrix, score
from pplib.run_matrix import RATING_SAMPLE_FILENAME, run_matrix
from pplib.schema import BANNER_BOOTSTRAP
from pplib.testset import (TestSetLockError, check_test_set, digest_test_set, lock_test_set)
from step3_caption.llm_interface import GenerationResult, MockProvider


class CountingMock(MockProvider):
    def __init__(self):
        self.calls = 0

    def generate(self, prompt, evidence):
        self.calls += 1
        return super().generate(prompt, evidence)


class PricedProvider(CountingMock):
    name = "priced"
    model = "priced-1"

    def generate(self, prompt, evidence):
        self.calls += 1
        return GenerationResult("caption", prompt_tokens=1000, completion_tokens=100)


def fake_trainer(config, dataset_dir, out_dir, epochs=None, seed=None, **flags):
    """Predicts Other/Other for every test item, which never matches the weak gold labels."""
    records = {json.loads(l)["prcs_id"]: json.loads(l)
               for l in (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()}
    ids = json.loads((Path(dataset_dir) / "splits.json").read_text())["test"]
    preds = [{"prcs_id": i, "practice": ["Other"], "purpose": ["Other"]} for i in ids]
    gold = label_matrix(ids, {i: records[i]["labels"] for i in ids})
    test = score(gold, label_matrix(ids, {p["prcs_id"]: p for p in preds}))
    fake_trainer.calls += 1
    return {"test": test, "is_weak": True, "best_val_macro_f1": 0.0, "predictions": preds}


fake_trainer.calls = 0


def _copy_dataset(src: Path, dst: Path) -> Path:
    dst.mkdir(parents=True)
    for n in ("adppg.jsonl", "splits.json"):
        shutil.copy(src / n, dst / n)
    return dst


@pytest.fixture(scope="module")
def dry_run(dataset_dir, tmp_path_factory):
    """One real dry run of all ten arms on the fixture (1 epoch per seed)."""
    base = tmp_path_factory.mktemp("matrix")
    scratch, real = base / "scratch", base / "experiments"
    provider = CountingMock()
    summary = run_matrix(dataset_dir, experiments_root=real, dry_run=True, epochs=1,
                         provider=provider, scratch_root=scratch)
    return {"summary": summary, "scratch": scratch, "real": real, "provider": provider,
            "dataset": dataset_dir}


def test_dry_run_writes_ten_manifests_to_the_scratch_root_only(dry_run):
    scratch = dry_run["scratch"]
    assert dry_run["summary"]["status"] == {a: "ran" for a in FINAL_ARMS}
    assert sorted(p.parent.name for p in scratch.glob("EXP*/manifest.json")) == sorted(EXP_ID.values())
    index = [json.loads(l) for l in (scratch / "index.jsonl").read_text().splitlines()]
    assert len(index) == 10
    assert not dry_run["real"].exists()
    for arm in FINAL_ARMS:
        assert load_experiment(scratch, EXP_ID[arm])["banner"] == BANNER_BOOTSTRAP


def test_classification_manifest_has_seeds_interval_and_bootstrap(dry_run):
    m = load_experiment(dry_run["scratch"], EXP_ID["apg"])
    assert m["seeds"] == list(SEEDS)
    assert set(m["metrics"]["per_seed"]) == {str(s) for s in SEEDS}
    s = m["metrics"]["summary"]["macro_f1"]
    assert s["n"] == 5 and s["ci_low"] <= s["mean"] <= s["ci_high"]
    pb = m["metrics"]["paired_bootstrap_vs_reference"]
    assert pb["reference"] == "ppg_code seed 0" and pb["draws"] == 2000
    assert m["metrics"]["threshold"] == 0.5
    seed_metrics = json.loads((dry_run["scratch"] / "EXP001" / "seed_3" / "test_metrics.json").read_text())
    assert m["metrics"]["per_seed"]["3"] == seed_metrics["test"]
    ref = load_experiment(dry_run["scratch"], EXP_ID["ppg_code"])["metrics"]["paired_bootstrap_vs_reference"]
    assert ref["delta"] == 0


def test_baseline_manifest_has_item_bootstrap(dry_run):
    for arm in ("rule", "tfidf"):
        m = load_experiment(dry_run["scratch"], EXP_ID[arm])["metrics"]
        ib = m["item_bootstrap"]["metrics"]["macro_f1"]
        assert ib["ci_low"] <= ib["estimate"] <= ib["ci_high"]
        assert m["item_bootstrap"]["draws"] == 2000
        assert "delta" in m["paired_bootstrap_vs_reference"]


def test_caption_arms_cover_the_rating_sample(dry_run):
    scratch = dry_run["scratch"]
    sample = json.loads((scratch / RATING_SAMPLE_FILENAME).read_text())
    assert sample["test_set_digest"] == digest_test_set(dry_run["dataset"])
    assert dry_run["provider"].calls == len(CAPTION_ARMS) * sample["n"]
    for arm in CAPTION_ARMS:
        m = load_experiment(scratch, EXP_ID[arm])["metrics"]
        assert m["n_captioned"] == sample["n"] and m["calls"] == sample["n"]
        assert m["stopped_by_budget"] is False
        rows = [json.loads(l) for l in (scratch / EXP_ID[arm] / "captions.jsonl").read_text().splitlines()]
        assert [r["prcs_id"] for r in rows] == sample["ids"]
        assert all("evidence" not in r and "prompt" not in r for r in rows)


def test_condition_G_rows_carry_the_ppg_code_seed0_predictions(dry_run):
    scratch = dry_run["scratch"]
    preds = {json.loads(l)["prcs_id"]: json.loads(l)
             for l in (scratch / "EXP004" / "seed_0" / "predictions.jsonl").read_text().splitlines()}
    for r in map(json.loads, (scratch / "EXP010" / "captions.jsonl").read_text().splitlines()):
        assert r["predicted"] == {"practice": preds[r["prcs_id"]]["practice"],
                                  "purpose": preds[r["prcs_id"]]["purpose"]}


def test_rerun_of_a_caption_arm_retrains_nothing_and_calls_nothing(dry_run):
    provider = CountingMock()
    s = run_matrix(dry_run["dataset"], arms=["cap_code"], dry_run=True, epochs=1, provider=provider,
                   scratch_root=dry_run["scratch"])
    assert s["status"] == {"cap_code": "skipped"}
    assert s["train_calls"] == 0 and provider.calls == 0

    (dry_run["scratch"] / "EXP007" / "manifest.json").unlink()
    s = run_matrix(dry_run["dataset"], arms=["cap_code"], dry_run=True, epochs=1, provider=provider,
                   scratch_root=dry_run["scratch"])
    assert s["status"] == {"cap_code": "ran"}
    assert s["train_calls"] == 0 and provider.calls == 0
    assert load_experiment(dry_run["scratch"], "EXP007")["metrics"]["calls"] == 0


def test_rerun_of_a_classification_arm_reuses_seed_predictions(dry_run):
    (dry_run["scratch"] / "EXP002" / "manifest.json").unlink()
    s = run_matrix(dry_run["dataset"], arms="apg_code".split(), dry_run=True, epochs=1,
                   provider=CountingMock(), scratch_root=dry_run["scratch"])
    assert s["status"] == {"apg_code": "ran"} and s["train_calls"] == 0


def test_condition_G_uses_predictions_that_differ_from_gold(dataset_dir, tmp_path):
    fake_trainer.calls = 0
    run_matrix(dataset_dir, arms=["cap_code_taint_pred"], dry_run=True, provider=CountingMock(),
               trainer=fake_trainer, scratch_root=tmp_path)
    assert fake_trainer.calls == 1                       # only the ppg_code seed-0 reference
    gold = {json.loads(l)["prcs_id"]: json.loads(l)["labels"]
            for l in (dataset_dir / "adppg.jsonl").read_text(encoding="utf-8").splitlines()}
    rows = [json.loads(l) for l in (tmp_path / "EXP010" / "captions.jsonl").read_text().splitlines()]
    assert rows
    for r in rows:
        assert r["predicted"] == {"practice": ["Other"], "purpose": ["Other"]}
        assert r["predicted"]["practice"] != gold[r["prcs_id"]]["practice"]
    assert not (tmp_path / "EXP004" / "manifest.json").exists()   # reference outputs, no manifest


def test_budget_stop_is_recorded(dataset_dir, tmp_path):
    cfg = tmp_path / "llm.yaml"
    cfg.write_text("provider: anthropic\nmax_tokens: 100\nproviders:\n"
                   "  anthropic: {model: m, api_key_env: NONE, price_in_per_mtok: 1.0, "
                   "price_out_per_mtok: 1.0}\n", encoding="utf-8")
    provider = PricedProvider()
    # one call reserves roughly (prompt bytes + 64 + 100) / 1e6 USD; allow about one and a half
    s = run_matrix(dataset_dir, arms=["cap_code"], dry_run=True, budget_usd=0.0015,
                   llm_config=cfg, provider=provider, trainer=fake_trainer,
                   scratch_root=tmp_path / "scratch")
    m = load_experiment(tmp_path / "scratch", "EXP007")["metrics"]
    assert m["stopped_by_budget"] is True and s["budget"]["stopped_by_budget"] is True
    assert m["calls"] == provider.calls == 1
    assert m["n_captioned"] == 1 and m["prompt_tokens"] == 1000 and m["completion_tokens"] == 100
    assert m["spent_usd"] == pytest.approx(0.0011)

    # a rerun with more budget captions only the rest and keeps the arm's running totals
    s = run_matrix(dataset_dir, arms=["cap_code"], dry_run=True, budget_usd=1.0,
                   llm_config=cfg, provider=provider, trainer=fake_trainer,
                   scratch_root=tmp_path / "scratch")
    m = load_experiment(tmp_path / "scratch", "EXP007")["metrics"]
    assert m["stopped_by_budget"] is False and m["n_captioned"] == m["n_sample"]
    assert m["calls"] == provider.calls == m["n_sample"]
    assert m["this_run"]["calls"] == m["n_sample"] - 1
    assert m["spent_usd"] == pytest.approx(0.0011 * m["n_sample"])


def test_real_run_refuses_without_a_matching_lock(dataset_dir, tmp_path):
    root = tmp_path / "experiments"
    with pytest.raises(TestSetLockError, match="no TEST_SET.json"):
        run_matrix(dataset_dir, experiments_root=root, arms=["rule"], trainer=fake_trainer)
    lock_test_set(dataset_dir, root, allow_non_gold=True)
    s = run_matrix(dataset_dir, experiments_root=root, arms=["rule"], trainer=fake_trainer,
                   scratch_root=tmp_path / "scratch")
    assert s["status"] == {"rule": "ran"} and (root / "EXP005" / "manifest.json").exists()

    lock = json.loads((root / "TEST_SET.json").read_text())
    lock["digest"] = "0" * 64
    (root / "TEST_SET.json").write_text(json.dumps(lock))
    with pytest.raises(TestSetLockError, match="does not match"):
        run_matrix(dataset_dir, experiments_root=root, arms=["rule"], trainer=fake_trainer)


def test_lock_requires_human_labels_unless_allowed(dataset_dir, tmp_path):
    with pytest.raises(ValueError, match="not all human-labeled"):
        lock_test_set(dataset_dir, tmp_path)
    lock = lock_test_set(dataset_dir, tmp_path, allow_non_gold=True)
    assert lock["banner"] == BANNER_BOOTSTRAP
    assert check_test_set(dataset_dir, tmp_path) == lock["digest"]


def test_digest_ignores_train_changes_but_not_test_changes(dataset_dir, tmp_path):
    ds = _copy_dataset(dataset_dir, tmp_path / "ds")
    before = digest_test_set(ds)
    splits = json.loads((ds / "splits.json").read_text())
    test_ids, train_id = set(splits["test"]), splits["train"][0]

    def rewrite(pick, change):
        rows = [json.loads(l) for l in (ds / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]
        for r in rows:
            if pick(r["prcs_id"]):
                change(r)
        (ds / "adppg.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    rewrite(lambda i: i == train_id, lambda r: r["labels"].update(purpose=["Other"]))
    assert digest_test_set(ds) == before
    first_test = sorted(test_ids)[0]
    rewrite(lambda i: i == first_test, lambda r: r["labels"].update(label_source="human"))
    assert digest_test_set(ds) != before
