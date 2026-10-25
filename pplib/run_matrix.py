"""
Purpose: Run the canonical experiment matrix (pplib/experiment_matrix.py) and save one manifest
         per arm under its fixed experiment id. Resumable: finished arms are skipped, and per-seed
         predictions and per-item caption rows are reused when present.
Input:   --dataset (adppg.jsonl + splits.json), configs/convgnn.yaml, configs/llm.yaml.
Output:  <root>/EXPnnn/manifest.json (+ index.jsonl), per-seed predictions.jsonl and
         test_metrics.json, baseline predictions.jsonl, caption captions.jsonl, RATING_SAMPLE.json.

    classification  5 seeds through step2_convgnn.train.train; metrics come from its return value
                    (fixed 0.5 threshold); mean and 95% t-interval over seeds
    baseline        rule / tfidf fit on train, one deterministic run; 95% item-bootstrap interval
    both            paired item bootstrap (2,000 draws) of macro-F1 against ppg_code seed 0
    captions        the 60-item rating sample drawn from the locked test ids; spend goes through
                    step3_caption.budget.Budget (--budget-usd); condition G captions with the
                    labels ppg_code seed 0 predicted

A real run refuses to start unless <root>/TEST_SET.json matches the current test split
(pplib.testset). --dry-run writes to data/scratch_experiments/ instead and skips that check, so the
matrix can be exercised on weak labels; its manifests keep their banners. --force recomputes the
named arms from scratch (caption arms call the provider again).

Run: python -m pplib.run_matrix --dry-run --dataset data/corpus_run/dataset
     python -m pplib.run_matrix --dataset data/corpus_run/dataset --budget-usd 3 --provider anthropic
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from pplib.experiment import (ExperimentRun, MANIFEST_FILENAME, current_code_version,
                              digest_configs, digest_dataset, save_experiment)
from pplib.experiment_matrix import (BOOTSTRAP_DRAWS, FINAL_ARMS, RATING_SAMPLE_SIZE, REFERENCE_ARM,
                                     REFERENCE_SEED, SEEDS, THRESHOLD, arm_spec)
from pplib.io_utils import REPO_ROOT, dump_json, ensure_dir, get_logger, load_dotenv, load_json, load_yaml
from pplib.matrix_stats import (SUMMARY_KEYS, bootstrap_interval, label_matrix, label_support,
                                paired_bootstrap, score, t_interval)
from pplib.schema import BANNER_BOOTSTRAP, is_gold
from pplib.testset import TestSetLockError, check_test_set, digest_test_set

log = get_logger("run_matrix")

DEFAULT_ROOT = REPO_ROOT / "experiments"
SCRATCH_ROOT = REPO_ROOT / "data" / "scratch_experiments"
RATING_SAMPLE_FILENAME = "RATING_SAMPLE.json"
RATING_SAMPLE_SEED = 2026
CONVGNN_CONFIG = REPO_ROOT / "configs" / "convgnn.yaml"
LLM_CONFIG = REPO_ROOT / "configs" / "llm.yaml"
DIGESTED_CONFIGS = [REPO_ROOT / "configs" / n for n in
                    ("convgnn.yaml", "llm.yaml", "weak_labels.yaml", "sdk_catalog.yaml")]
CAPTION_FIELDS = ("prcs_id", "condition", "condition_label", "caption", "provider", "model",
                  "prompt_tokens", "completion_tokens", "latency_seconds", "error")


def _read_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _write_jsonl(rows: Iterable[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _shown_path(p: str | Path) -> str:
    """Repo-relative path for manifests (never an absolute user path)."""
    p = Path(p).resolve()
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.name


class _Context:
    """Everything shared by the arms of one run."""

    def __init__(self, dataset_dir, root: Path, force: bool, dry_run: bool, config: str,
                 epochs: Optional[int], test_set_digest: str):
        self.dataset_dir = str(dataset_dir)
        self.root = root
        self.force = force
        self.dry_run = dry_run
        self.config = str(config)
        self.epochs = epochs
        self.test_set_digest = test_set_digest
        self.records = {r["prcs_id"]: r for r in _read_jsonl(Path(dataset_dir) / "adppg.jsonl")}
        self.splits = load_json(Path(dataset_dir) / "splits.json")
        self.test_ids = sorted(self.splits.get("test", []))
        if not self.test_ids:
            raise ValueError("the dataset has an empty test split; the matrix needs one")
        gold_labels = {i: self.records[i]["labels"] for i in self.test_ids}
        self.gold = label_matrix(self.test_ids, gold_labels)
        self.test_all_gold = all(is_gold(l.get("label_source", "weak")) for l in gold_labels.values())
        self.banner = "" if self.test_all_gold else BANNER_BOOTSTRAP
        self.code_version = current_code_version(REPO_ROOT)
        self.config_digest = digest_configs(DIGESTED_CONFIGS)
        self.dataset_digest = digest_dataset(dataset_dir)
        self.train_calls = 0
        self.reference: Optional[Dict[str, Dict]] = None

    def exp_dir(self, arm: str) -> Path:
        return self.root / arm_spec(arm).exp_id

    def matrix(self, preds: Dict[str, Dict]) -> Dict:
        missing = set(self.test_ids) - set(preds)
        if missing:
            raise ValueError(f"predictions miss {len(missing)} test items, e.g. {sorted(missing)[:3]}")
        return label_matrix(self.test_ids, preds)

    def run(self, arm: str, metrics: Dict, artifacts: List[str], model_version: str,
            seeds: List[int], notes: str) -> ExperimentRun:
        spec = arm_spec(arm)
        mode = "dry run on non-locked labels" if self.dry_run else "locked test split"
        return ExperimentRun(
            exp_id=spec.exp_id, name=f"final_matrix::{arm}", code_version=self.code_version,
            config_digest=self.config_digest, dataset_digest=self.dataset_digest,
            seed=seeds[0] if seeds else REFERENCE_SEED, seeds=seeds, metrics=metrics,
            artifacts=artifacts, model_version=model_version, banner=self.banner,
            test_set_digest=self.test_set_digest,
            notes=f"arm={arm}, task={spec.task}, {mode}, dataset={_shown_path(self.dataset_dir)}. {notes}")


# --- classification -------------------------------------------------------------------------

def _seed_outputs(ctx: _Context, arm: str, seed: int) -> Optional[Dict]:
    """Reusable per-seed outputs, or None when they are missing or from another test split."""
    d = ctx.exp_dir(arm) / f"seed_{seed}"
    if ctx.force or not (d / "predictions.jsonl").exists() or not (d / "test_metrics.json").exists():
        return None
    m = load_json(d / "test_metrics.json")
    if m.get("test_set_digest") != ctx.test_set_digest:
        return None
    return {**m, "predictions": _read_jsonl(d / "predictions.jsonl")}


def _train_seed(ctx: _Context, arm: str, seed: int, trainer: Callable) -> Dict:
    """Train one seed (or reuse its outputs) and return train()'s metrics plus predictions."""
    found = _seed_outputs(ctx, arm, seed)
    if found is not None:
        return found
    flags = arm_spec(arm).flags
    d = ensure_dir(ctx.exp_dir(arm) / f"seed_{seed}")
    log.info("Training %s seed %d", arm, seed)
    ctx.train_calls += 1
    res = trainer(ctx.config, ctx.dataset_dir, str(d), ctx.epochs, seed=seed, **flags)
    out = {"seed": seed, "test": res["test"], "is_weak": res["is_weak"],
           "best_val_macro_f1": res["best_val_macro_f1"], "threshold": res.get("threshold", THRESHOLD),
           "test_set_digest": ctx.test_set_digest}
    _write_jsonl(res["predictions"], d / "predictions.jsonl")
    dump_json(out, d / "test_metrics.json")
    return {**out, "predictions": res["predictions"]}


def _by_id(rows: List[Dict]) -> Dict[str, Dict]:
    return {r["prcs_id"]: r for r in rows}


def _reference(ctx: _Context, trainer: Callable) -> Dict[str, Dict]:
    """ppg_code seed-0 predictions by prcs_id (trained once if missing)."""
    if ctx.reference is None:
        ctx.reference = _by_id(_train_seed(ctx, REFERENCE_ARM, REFERENCE_SEED, trainer)["predictions"])
    return ctx.reference


def run_classification(ctx: _Context, arm: str, trainer: Callable) -> ExperimentRun:
    per_seed = {s: _train_seed(ctx, arm, s, trainer) for s in SEEDS}
    if arm == REFERENCE_ARM:
        ctx.reference = _by_id(per_seed[REFERENCE_SEED]["predictions"])
    summary = {k: t_interval([per_seed[s]["test"][k] for s in SEEDS]) for k in SUMMARY_KEYS}
    seed0 = ctx.matrix(_by_id(per_seed[REFERENCE_SEED]["predictions"]))
    metrics = {
        "threshold": THRESHOLD, "n_test": len(ctx.test_ids), "label_support": label_support(ctx.gold),
        "summary": summary,
        "per_seed": {str(s): per_seed[s]["test"] for s in SEEDS},
        "paired_bootstrap_vs_reference": {
            "reference": f"{REFERENCE_ARM} seed {REFERENCE_SEED}", "arm_seed": REFERENCE_SEED,
            **paired_bootstrap(ctx.gold, seed0, ctx.matrix(_reference(ctx, trainer)), BOOTSTRAP_DRAWS)},
    }
    artifacts = [f"seed_{s}/{n}" for s in SEEDS
                 for n in ("predictions.jsonl", "test_metrics.json", "metrics.csv", "train_log.csv")]
    flags = arm_spec(arm).flags
    model = f"rgcn privacy_features={flags['privacy_features']} token_features={flags['token_features']}"
    return ctx.run(arm, metrics, artifacts, model, list(SEEDS), "Mean and 95% t-interval over seeds.")


# --- baselines --------------------------------------------------------------------------------

def run_baseline(ctx: _Context, arm: str, trainer: Callable) -> ExperimentRun:
    from step3_caption.baselines import RuleBaseline, TfIdfBaseline

    model = {"rule": RuleBaseline, "tfidf": TfIdfBaseline}[arm]()
    model.fit([ctx.records[i] for i in ctx.splits.get("train", []) if i in ctx.records])
    preds = [p.to_dict() for p in model.predict([ctx.records[i] for i in ctx.test_ids])]
    _write_jsonl(preds, ctx.exp_dir(arm) / "predictions.jsonl")
    pred = ctx.matrix(_by_id(preds))
    metrics = {
        "threshold": None, "n_test": len(ctx.test_ids), "label_support": label_support(ctx.gold),
        "test": score(ctx.gold, pred),
        "item_bootstrap": bootstrap_interval(ctx.gold, pred, BOOTSTRAP_DRAWS),
        "paired_bootstrap_vs_reference": {
            "reference": f"{REFERENCE_ARM} seed {REFERENCE_SEED}",
            **paired_bootstrap(ctx.gold, pred, ctx.matrix(_reference(ctx, trainer)), BOOTSTRAP_DRAWS)},
    }
    note = ("Deterministic; fit on the train split. The rule baseline is the weak labeler, so on weak "
            "test labels it scores itself.")
    return ctx.run(arm, metrics, ["predictions.jsonl"], arm, [], note)


# --- captions ---------------------------------------------------------------------------------

def rating_sample(ctx: _Context) -> Dict:
    """Load RATING_SAMPLE.json, or draw it once from the test ids with a fixed seed."""
    path = ctx.root / RATING_SAMPLE_FILENAME
    if path.exists():
        sample = load_json(path)
        if sample.get("test_set_digest") != ctx.test_set_digest:
            raise ValueError(f"{path} was drawn from a different test split; delete it to redraw")
        return sample
    n = min(RATING_SAMPLE_SIZE, len(ctx.test_ids))
    ids = sorted(random.Random(RATING_SAMPLE_SEED).sample(ctx.test_ids, n))
    sample = {"ids": ids, "n": n, "seed": RATING_SAMPLE_SEED, "test_set_digest": ctx.test_set_digest}
    dump_json(sample, path)
    return sample


def _caption_rows(path: Path) -> Dict[str, Dict]:
    """Last row per prcs_id (a retried item overrides its earlier failed row)."""
    return {r["prcs_id"]: r for r in _read_jsonl(path)}


def _captions_complete(ctx: _Context, arm: str) -> bool:
    path = ctx.root / RATING_SAMPLE_FILENAME
    if not path.exists():
        return False
    rows = _caption_rows(ctx.exp_dir(arm) / "captions.jsonl")
    return all(i in rows and not rows[i].get("error") for i in load_json(path)["ids"])


def _prior_metrics(ctx: _Context, arm: str) -> Dict:
    """Totals from this arm's previous manifest on the same test split (spend accumulates)."""
    path = ctx.exp_dir(arm) / MANIFEST_FILENAME
    if not path.exists():
        return {}
    m = load_json(path)
    return m.get("metrics", {}) if m.get("test_set_digest") == ctx.test_set_digest else {}


def run_captions(ctx: _Context, arm: str, trainer: Callable, llm: Dict) -> ExperimentRun:
    from step3_caption.experiments import BUDGET_REFUSED, run_condition

    spec = arm_spec(arm)
    sample = rating_sample(ctx)
    path = ensure_dir(ctx.exp_dir(arm)) / "captions.jsonl"
    rows = {} if ctx.force else _caption_rows(path)
    if ctx.force and path.exists():
        path.unlink()
    predicted = _reference(ctx, trainer) if spec.condition == "G" else {}
    provider, budget = llm["provider"](), llm["budget"]
    before = budget.summary()
    stopped = False
    for pid in sample["ids"]:
        if pid in rows and not rows[pid].get("error"):
            continue
        r = run_condition(ctx.records[pid], spec.condition, provider, budget=budget,
                          predicted=predicted.get(pid) if spec.condition == "G" else None)
        if r.error == BUDGET_REFUSED:
            stopped = True
            log.warning("%s: budget reached; %s and later items not captioned", arm, pid)
            break
        row = {k: getattr(r, k) for k in CAPTION_FIELDS}
        if spec.condition == "G":
            row["predicted"] = {"practice": r.evidence["practice"], "purpose": r.evidence["purpose"]}
        rows[pid] = row
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    order = {pid: i for i, pid in enumerate(sample["ids"])}
    _write_jsonl(sorted(rows.values(), key=lambda r: order.get(r["prcs_id"], len(order))), path)

    after = budget.summary()
    this_run = {k: after[k] - before[k] for k in ("calls", "prompt_tokens", "completion_tokens")}
    this_run["spent_usd"] = round(after["spent_usd"] - before["spent_usd"], 6)
    prior = {} if ctx.force else _prior_metrics(ctx, arm)
    done = [pid for pid in sample["ids"] if pid in rows and not rows[pid].get("error")]
    metrics = {
        "n_sample": sample["n"], "n_captioned": len(done),
        "n_errors": sum(1 for pid in sample["ids"] if pid in rows and rows[pid].get("error")),
        **{k: round(prior.get(k, 0) + v, 6) if k == "spent_usd" else prior.get(k, 0) + v
           for k, v in this_run.items()},
        "this_run": {**this_run, "budget_usd": budget.limit_usd},
        "stopped_by_budget": stopped,
        "rating_sample": {"seed": sample["seed"], "n": sample["n"]},
    }
    first = next(iter(rows.values()), {})
    model = f"{first.get('provider', llm['name'])}:{first.get('model', '')}".rstrip(":")
    note = f"Condition {spec.condition}; quality ratings are added in Phase 4."
    if spec.condition == "G":
        note += f" Labels predicted by {REFERENCE_ARM} seed {REFERENCE_SEED}, never the stored labels."
    return ctx.run(arm, metrics, ["captions.jsonl", f"../{RATING_SAMPLE_FILENAME}"], model, [], note)


# --- driver -----------------------------------------------------------------------------------

def _arm_complete(ctx: _Context, arm: str) -> bool:
    d = ctx.exp_dir(arm)
    if not (d / MANIFEST_FILENAME).exists():
        return False
    if load_json(d / MANIFEST_FILENAME).get("test_set_digest") != ctx.test_set_digest:
        return False
    task = arm_spec(arm).task
    if task == "classification":
        return all(_seed_outputs(ctx, arm, s) is not None for s in SEEDS)
    if task == "baseline":
        return (d / "predictions.jsonl").exists()
    return _captions_complete(ctx, arm)


def _llm_factory(llm_config: str | Path, provider_name: Optional[str], provider,
                 budget_usd: float) -> Dict:
    from step3_caption.budget import Budget
    from step3_caption.llm_interface import get_provider

    cfg = load_yaml(llm_config)
    if provider_name:
        cfg = {**cfg, "provider": provider_name}
    cache: Dict = {}

    def make():
        if "p" not in cache:
            if provider is not None:
                cache["p"] = provider
            else:
                if cfg.get("provider", "mock") != "mock":
                    load_dotenv(REPO_ROOT / ".env")
                cache["p"] = get_provider(cfg)
        return cache["p"]

    return {"provider": make, "budget": Budget.from_config(cfg, budget_usd),
            "name": cfg.get("provider", "mock")}


def run_matrix(dataset_dir: str | Path, experiments_root: str | Path = DEFAULT_ROOT,
               arms: Optional[List[str]] = None, dry_run: bool = False, force: bool = False,
               budget_usd: float = 0.0, config: str | Path = CONVGNN_CONFIG,
               llm_config: str | Path = LLM_CONFIG, provider_name: Optional[str] = None,
               provider=None, epochs: Optional[int] = None, trainer: Optional[Callable] = None,
               scratch_root: str | Path = SCRATCH_ROOT) -> Dict:
    """Run the named arms (default all) and return {arm: 'ran' | 'skipped'} plus run totals."""
    arms = list(arms or FINAL_ARMS)
    unknown = [a for a in arms if a not in FINAL_ARMS]
    if unknown:
        raise ValueError(f"unknown arms {unknown}; expected some of {FINAL_ARMS}")
    root = Path(scratch_root if dry_run else experiments_root)
    digest = digest_test_set(dataset_dir) if dry_run else check_test_set(dataset_dir, root)
    if trainer is None:
        from step2_convgnn.train import train as trainer
    ctx = _Context(dataset_dir, ensure_dir(root), force, dry_run, config, epochs, digest)
    llm = _llm_factory(llm_config, provider_name, provider, budget_usd)

    ordered = sorted(arms, key=lambda a: (a != REFERENCE_ARM, FINAL_ARMS.index(a)))
    status: Dict[str, str] = {}
    for arm in ordered:
        if not force and _arm_complete(ctx, arm):
            log.info("%s (%s): outputs present, skipped", arm, arm_spec(arm).exp_id)
            status[arm] = "skipped"
            continue
        task = arm_spec(arm).task
        if task == "classification":
            run = run_classification(ctx, arm, trainer)
        elif task == "baseline":
            run = run_baseline(ctx, arm, trainer)
        else:
            run = run_captions(ctx, arm, trainer, llm)
        save_experiment(run, root)
        status[arm] = "ran"
    return {"root": str(root), "status": {a: status[a] for a in arms}, "banner": ctx.banner,
            "train_calls": ctx.train_calls, "budget": llm["budget"].summary()}


def _parse_arms(values: Optional[List[str]]) -> Optional[List[str]]:
    if not values:
        return None
    return [a.strip() for v in values for a in v.split(",") if a.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the canonical experiment matrix (EXP001-EXP010).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--arms", nargs="+", default=None,
                    help=f"arms to run, space or comma separated (default all): {', '.join(FINAL_ARMS)}")
    ap.add_argument("--experiments-root", default=str(DEFAULT_ROOT))
    ap.add_argument("--dry-run", action="store_true",
                    help=f"write to {_shown_path(SCRATCH_ROOT)}/ and skip the TEST_SET.json check")
    ap.add_argument("--force", action="store_true", help="recompute the named arms from scratch")
    ap.add_argument("--budget-usd", type=float, default=0.0,
                    help="spending cap for caption calls in this run (the offline mock is free)")
    ap.add_argument("--config", default=str(CONVGNN_CONFIG))
    ap.add_argument("--llm-config", default=str(LLM_CONFIG))
    ap.add_argument("--provider", default=None, help="override the llm config provider")
    ap.add_argument("--epochs", type=int, default=None, help="override train.epochs")
    args = ap.parse_args()
    try:
        s = run_matrix(args.dataset, args.experiments_root, _parse_arms(args.arms), args.dry_run,
                       args.force, args.budget_usd, args.config, args.llm_config, args.provider,
                       epochs=args.epochs)
    except TestSetLockError as e:
        raise SystemExit(f"refusing a real run: {e}")
    print("\n=== Experiment matrix ===")
    if s["banner"]:
        print(f"  *** {s['banner']} ***")
    for arm, st in s["status"].items():
        print(f"  {arm_spec(arm).exp_id} {arm:20} {st}")
    b = s["budget"]
    stopped = " (stopped by budget)" if b["stopped_by_budget"] else ""
    print(f"  root={_shown_path(s['root'])}  trainings={s['train_calls']}  caption calls={b['calls']}  "
          f"spent=${b['spent_usd']}{stopped}")


if __name__ == "__main__":
    main()
