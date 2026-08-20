"""Verifier-B batch scoring for S4/S6 evaluation; deliberately outside agents."""
from __future__ import annotations

import json
from pathlib import Path

from src.verifier.calibration import apply_temperature


REGISTERED_HF_CONFIG = (
    Path(__file__).resolve().parents[2] / "configs" / "s3d_verifier_b_hf_config.json"
)


def target_probabilities(
    texts: list[str],
    target_levels: list[int],
    *,
    artifact_path: str | Path = "artifacts/verifier_b.joblib",
    weights_path: str | Path | None = None,
    batch_size: int = 32,
    device: str | None = None,
) -> list[float]:
    """Return calibrated P_B(y=target_level) for each text."""
    if len(texts) != len(target_levels):
        raise ValueError("texts and target_levels must have equal length")
    if any(level not in (0, 1) for level in target_levels):
        raise ValueError("target levels must be 0 or 1")
    import joblib
    import torch
    from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

    meta = joblib.load(artifact_path)
    if meta.get("role") != "B":
        raise ValueError(f"evaluation artifact must have role B, got {meta.get('role')!r}")
    if meta.get("backbone") != "csebuetnlp/banglabert":
        raise ValueError(
            f"Verifier-B backbone mismatch: expected csebuetnlp/banglabert, "
            f"got {meta.get('backbone')!r}"
        )
    weights = Path(weights_path or meta["weights_dir"])
    if not (weights / "model.safetensors").is_file():
        raise FileNotFoundError(f"Verifier-B weights missing: {weights / 'model.safetensors'}")

    # The Kaggle dataset wrapper may carry its own unrelated `config.json` at
    # the mount root. Architecture metadata is part of the trained artifact,
    # not transport metadata, so load the exact save_pretrained config captured
    # from the seed-42 Verifier-B run. `from_pretrained` still validates every
    # tensor against this config and fails on missing/unexpected shapes.
    config_data = json.loads(REGISTERED_HF_CONFIG.read_text(encoding="utf-8"))
    model_type = config_data.pop("model_type")
    model_config = AutoConfig.for_model(model_type, **config_data)
    tok = AutoTokenizer.from_pretrained(weights)
    model = AutoModelForSequenceClassification.from_pretrained(
        weights, config=model_config
    )
    selected_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model.to(selected_device).eval()

    p1: list[float] = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            enc = tok(
                texts[start:start + batch_size],
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt",
            )
            logits = model(**{k: v.to(selected_device) for k, v in enc.items()}).logits
            p1.extend(torch.softmax(logits, dim=-1)[:, 1].cpu().tolist())
    calibrated = apply_temperature(p1, float(meta["temperature"]))
    return [p if level == 1 else 1.0 - p
            for p, level in zip(calibrated, target_levels)]
