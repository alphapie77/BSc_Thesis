#!/usr/bin/env python3
"""Kaggle runtime gate for S5; validates infrastructure before 12B load."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.secrets import require  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.gemini_judge import SCHEMA, validate_payload  # noqa: E402
from src.eval.s5_prompts import role_control_messages  # noqa: E402


class KagglePreflightError(RuntimeError):
    pass


def validate_model_path(path: str | Path, *, min_weight_bytes: int = 1_000_000_000) -> dict:
    root = Path(path)
    config_path = root / "config.json"
    tokenizer_path = root / "tokenizer_config.json"
    if not config_path.is_file() or not tokenizer_path.is_file():
        raise KagglePreflightError(
            f"model input lacks config/tokenizer_config: {root}"
        )
    config = json.loads(config_path.read_text(encoding="utf-8"))
    model_type = str(config.get("model_type", "")).lower()
    architectures = [str(x).lower() for x in config.get("architectures", [])]
    if "gemma3" not in model_type.replace("_", "") and not any(
        "gemma3" in x.replace("_", "") for x in architectures
    ):
        raise KagglePreflightError(
            f"expected Gemma-3 config, got model_type={model_type!r}, "
            f"architectures={architectures!r}"
        )
    weights = [
        *root.glob("*.safetensors"), *root.glob("*.bin"),
        *root.glob("**/*.safetensors"), *root.glob("**/*.bin"),
    ]
    unique = {p.resolve(): p for p in weights if p.is_file()}
    total = sum(p.stat().st_size for p in unique.values())
    if total < min_weight_bytes:
        raise KagglePreflightError(
            f"model weights total only {total:,} bytes under {root}"
        )
    return {
        "model_type": config.get("model_type"),
        "architectures": config.get("architectures", []),
        "weight_files": len(unique),
        "weight_bytes": total,
    }


def validate_role_templates(tokenizer) -> dict:
    rendered = {}
    for label, role in (("intrinsic", "assistant"), ("external", "user")):
        messages = role_control_messages(
            base_prompt="BASE", draft="DRAFT", critique="CRITIQUE_BYTES", role=role
        )
        try:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception as exc:
            raise KagglePreflightError(
                f"Gemma tokenizer rejects the {label} role-control sequence: {exc}"
            ) from exc
        if text.count("CRITIQUE_BYTES") != 1:
            raise KagglePreflightError(
                f"{label} chat template lost or duplicated the critique bytes"
            )
        rendered[label] = len(text)
    return rendered


def validate_gemini_api(*, api_key: str, model: str, session=None) -> dict:
    if session is None:
        import requests
        session = requests
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body = {
        "contents": [{"role": "user", "parts": [{"text": (
            "Return a schema-valid evaluation object. Use verdict PASS, "
            "target_fit_score 100, and empty feedback."
        )}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
        },
    }
    response = session.post(url, json=body, timeout=60)
    if response.status_code != 200:
        # Never echo the URL: it contains the API key.
        raise KagglePreflightError(
            f"Gemini structured-output preflight HTTP {response.status_code}: "
            f"{response.text[:200]}"
        )
    raw = response.json()
    try:
        payload = json.loads(raw["candidates"][0]["content"]["parts"][0]["text"])
        verdict, score, feedback = validate_payload(payload)
    except Exception as exc:
        raise KagglePreflightError(
            f"Gemini did not honor the registered JSON schema: {exc}"
        ) from exc
    return {
        "verdict": verdict, "target_fit_score": score,
        "feedback_chars": len(feedback),
        "model_version": raw.get("modelVersion"),
    }


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_main_bn.yaml")
    ap.add_argument("--model-path", required=True)
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    import bitsandbytes
    import sklearn
    import torch
    import transformers
    from transformers import AutoTokenizer

    expected = cfg["runtime"]
    if sklearn.__version__ != str(expected["scikit_learn"]):
        raise KagglePreflightError(
            f"scikit-learn {sklearn.__version__} != {expected['scikit_learn']}"
        )
    if transformers.__version__ != str(expected["transformers"]):
        raise KagglePreflightError(
            f"transformers {transformers.__version__} != {expected['transformers']}"
        )
    if not torch.cuda.is_available():
        raise KagglePreflightError("CUDA is unavailable; enable a Kaggle GPU")
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    if free_bytes < 12_000_000_000:
        raise KagglePreflightError(
            f"only {free_bytes / 1e9:.1f} GB GPU memory free before model load; "
            "restart the Kaggle session"
        )

    model = validate_model_path(args.model_path)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    roles = validate_role_templates(tokenizer)
    gemini = validate_gemini_api(
        api_key=require("GOOGLE_API_KEY"), model=cfg["gemini_judge"]["model"]
    )
    print(json.dumps({
        "status": "KAGGLE_RUNTIME_READY_NO_MODEL_LOADED",
        "sklearn": sklearn.__version__,
        "transformers": transformers.__version__,
        "bitsandbytes": getattr(bitsandbytes, "__version__", "unknown"),
        "gpu": torch.cuda.get_device_name(0),
        "gpu_free_gb": round(free_bytes / 1e9, 2),
        "gpu_total_gb": round(total_bytes / 1e9, 2),
        "model": model,
        "role_template_chars": roles,
        "gemini": gemini,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
