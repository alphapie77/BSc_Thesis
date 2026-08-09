"""The three training backends S3.2's arms need. GPU code lives only here.

Kept in its own module so that everything else in Phase 3 -- the split contract,
the decision rule, the tests, the dry run -- imports and runs with no torch
installed. That separation is why the plumbing can be checked on a laptop.

Each function has the same contract: take the labelled rows, train one arm at
one seed, and return integer predictions for every dev row, in dev order. No
function here writes a file, prints a verdict, or knows what a verdict is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from src.verifier.split_access import LabelledRows


def check_arm_dependencies(arms: list[dict]) -> list[str]:
    """Import every backend an arm needs, and return a list of problems.

    Exists because of what happened on 2026-08-08: the run reached arm 6 of 7
    after roughly four GPU-hours and died on `import setfit`, which is
    incompatible with the transformers 5.x on the host. Every dependency that
    could fail was knowable in the first ten seconds. Fail fast, in preflight,
    on CPU -- not five-sevenths of the way through a session.

    Returns problems rather than raising, so the caller can report all of them
    at once instead of one per re-run.
    """
    problems: list[str] = []
    kinds = {a.get("kind", "finetune") for a in arms}
    try:
        import transformers  # noqa: F401
    except Exception as exc:
        problems.append(f"transformers: {exc}")
    if "setfit" in kinds:
        try:
            import setfit  # noqa: F401
        except Exception as exc:
            problems.append(
                f"setfit: {exc}\n"
                "    setfit's own module chain imports "
                "`transformers.training_args.default_logdir`, which transformers "
                "5.x removed. Pin transformers < 5 for the WHOLE run -- not just "
                "this arm. Mixing environments across arms is invalid: Coakley "
                "et al. (2022) measured >6 pp of accuracy variation from "
                "environment alone, and our whole between-arm spread is ~3 pp."
            )
        try:
            import datasets  # noqa: F401
        except Exception as exc:
            problems.append(f"datasets (needed by setfit): {exc}")
    return problems


def _torch_seed(seed: int):
    """Seed every RNG a transformer touches. Returns the torch module."""
    from src.common.seed import set_seed

    set_seed(seed)
    import torch

    return torch


def finetune_predict(train, dev, arm: dict, seed: int, lr: float, cfg: dict) -> list[int]:
    """Standard sequence-classification fine-tuning: arms 1-5.

    Deliberately plain. No layer freezing, no scheduler tricks, no class
    weighting -- the arms must differ only in their pretrained weights, or the
    ablation stops being an ablation of backbones. The ~40% minority is handled
    by reporting macro-F1, not by reweighting one arm and not another.
    """
    torch = _torch_seed(seed)
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    t = cfg["training"]
    tok = AutoTokenizer.from_pretrained(arm["model"])
    model = AutoModelForSequenceClassification.from_pretrained(arm["model"], num_labels=2)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    def encode(rows) -> TensorDataset:
        enc = tok(
            list(rows.texts),
            truncation=True,
            padding="max_length",
            max_length=t["max_length"],
            return_tensors="pt",
        )
        return TensorDataset(
            enc["input_ids"], enc["attention_mask"], torch.tensor(rows.labels)
        )

    loader = DataLoader(
        encode(train),
        batch_size=t["batch_size"],
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    model.train()
    for _ in range(t["epochs"]):
        for ids, mask, y in loader:
            opt.zero_grad()
            out = model(input_ids=ids.to(device), attention_mask=mask.to(device), labels=y.to(device))
            out.loss.backward()
            opt.step()

    model.eval()
    preds: list[int] = []
    with torch.no_grad():
        for ids, mask, _ in DataLoader(encode(dev), batch_size=t["batch_size"]):
            logits = model(input_ids=ids.to(device), attention_mask=mask.to(device)).logits
            preds.extend(logits.argmax(dim=-1).cpu().tolist())
    return preds


def setfit_predict(train, dev, arm: dict, seed: int, lr: float, cfg: dict) -> list[int]:
    """Arm 6: contrastive Sentence-Transformer fine-tuning + a logistic head.

    Registered in protocol.md with a pre-stated expectation of LOSING, on the
    basis of Beliveau et al. (2024). It uses its own published procedure rather
    than the shared budget above, and that asymmetry is reported rather than
    hidden -- SetFit at a BERT-shaped budget would be a strawman.
    """
    _torch_seed(seed)
    try:
        import setfit
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "arm 'setfit_labse' needs `pip install setfit`. It is a "
            "pre-registered arm, so it may not simply be skipped -- if it "
            "cannot be installed, log a deviation."
        ) from exc
    from datasets import Dataset

    model = setfit.SetFitModel.from_pretrained(arm["model"])
    data = Dataset.from_dict({"text": list(train.texts), "label": list(train.labels)})

    # SetFit 1.0 replaced `SetFitTrainer` with `Trainer` + `TrainingArguments`
    # and later dropped the old alias. Both spellings are attempted so that the
    # arm cannot die six-sevenths of the way through a four-hour GPU run over an
    # API rename -- which is what would have happened here, since setfit is the
    # sixth of seven arms in config order.
    if hasattr(setfit, "TrainingArguments"):
        args = setfit.TrainingArguments(
            batch_size=cfg["training"]["batch_size"],
            num_iterations=20,
            num_epochs=1,
            seed=seed,
        )
        setfit.Trainer(model=model, args=args, train_dataset=data).train()
    else:  # pragma: no cover - older setfit
        setfit.SetFitTrainer(
            model=model,
            train_dataset=data,
            num_iterations=20,
            num_epochs=1,
            batch_size=cfg["training"]["batch_size"],
            seed=seed,
        ).train()
    return [int(p) for p in model.predict(list(dev.texts))]


def nli_transfer_predict(train, dev, arm: dict, seed: int, lr: float, cfg: dict) -> list[int]:
    """Arm 7: BERT-NLI transfer -- fine-tune a model already trained on NLI.

    Laurer et al. (2023) report this is where the gain at 100-2500 training
    texts comes from, and that it helps most on imbalanced data. Mechanically it
    is the same loop as `finetune_predict`; the difference is entirely in which
    checkpoint the weights start from, which is the point.

    ⚠️ The classification head is re-initialised for our 2 labels, so this is
    transfer from an NLI-pretrained encoder, NOT zero-shot NLI inference with
    hypothesis templates. Laurer et al. also evaluate the latter. If the arm
    performs unexpectedly well or badly, that distinction is the first thing to
    check before writing anything about it.
    """
    return finetune_predict(train, dev, arm, seed, lr, cfg)
