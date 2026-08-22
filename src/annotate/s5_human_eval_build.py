#!/usr/bin/env python3
"""Build the blinded S5 Bangla human-evaluation interface.

The generator archive is input-only. Sampling is deterministic and balanced:
five items from each of the 10 condition x 2 target-level cells (100 total).
All three annotators receive the same items in independently shuffled orders,
which makes per-item agreement identifiable. Condition, target, replicate,
model scores and internal case keys exist only in the researcher key.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS  # noqa: E402


class HumanEvalBuildError(RuntimeError):
    pass


def read_cases(path: Path) -> list[dict]:
    rows, keys = [], set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = row.get("key")
        if not key or key in keys:
            raise HumanEvalBuildError(f"missing/duplicate key at line {line_no}")
        keys.add(key)
        rows.append(row)
    return rows


def emitted_text(row: dict) -> str:
    emitted = row.get("result", {}).get("emitted", {})
    text = emitted.get("text")
    if text is None and isinstance(emitted.get("generation"), dict):
        text = emitted["generation"].get("text")
    if not isinstance(text, str) or not text.strip():
        raise HumanEvalBuildError(f"empty emitted text: {row.get('key')}")
    return text.strip()


def _rank(seed: int, cell: str, key: str) -> str:
    return hashlib.sha256(f"{seed}|{cell}|{key}".encode("utf-8")).hexdigest()


def select_items(rows: list[dict], *, seed: int, per_cell: int) -> list[dict]:
    expected = 90 * 2 * len(CONDITIONS) * len(REPLICATE_SEEDS)
    if len(rows) != expected:
        raise HumanEvalBuildError(f"need frozen 5,400-case archive, got {len(rows)}")
    if {r.get("condition") for r in rows} != set(CONDITIONS):
        raise HumanEvalBuildError("condition registry mismatch")
    if {int(r.get("replicate_seed")) for r in rows} != set(REPLICATE_SEEDS):
        raise HumanEvalBuildError("replicate registry mismatch")

    # Round-robin allocation prevents early cells consuming all diverse plots.
    # Within each cell, seed quotas rotate 2/2/1 across the three registered
    # replicates. Candidate priority is: unused emitted text, least-used plot,
    # then the frozen hash rank. Thus condition coverage never comes at the cost
    # of silently showing one annotator the same output many times.
    cells = [(condition, level) for condition in CONDITIONS for level in (0, 1)]
    pools = {(condition, level): [r for r in rows if r["condition"] == condition
                                  and int(r["target_level"]) == level]
             for condition, level in cells}
    quotas = {}
    for ci, cell in enumerate(cells):
        base, extra = divmod(per_cell, len(REPLICATE_SEEDS))
        q = {s: base for s in REPLICATE_SEEDS}
        for j in range(extra):
            q[REPLICATE_SEEDS[(ci + j) % len(REPLICATE_SEEDS)]] += 1
        quotas[cell] = q
    chosen, used_keys, used_texts, plot_uses = [], set(), set(), defaultdict(int)
    for _ in range(per_cell):
        for cell in cells:
            available = [r for r in pools[cell] if r["key"] not in used_keys
                         and quotas[cell][int(r["replicate_seed"])] > 0]
            if not available:
                raise HumanEvalBuildError(f"cannot satisfy seed-balanced allocation for {cell}")
            available.sort(key=lambda r: (
                emitted_text(r) in used_texts,
                plot_uses[r["plot_id"]],
                _rank(seed, f"{cell[0]}|L{cell[1]}", r["key"]),
            ))
            pick = available[0]
            chosen.append(pick); used_keys.add(pick["key"])
            used_texts.add(emitted_text(pick)); plot_uses[pick["plot_id"]] += 1
            quotas[cell][int(pick["replicate_seed"])] -= 1
    if len({r["key"] for r in chosen}) != len(chosen):
        raise HumanEvalBuildError("sample contains duplicate case keys")
    return chosen


def interface_html(items: list[dict], *, annotator: str, provenance: dict) -> str:
    payload = []
    for item in items:
        payload.append({"item_id": item["item_id"], "plot": item["plot"],
                        "review": item["review"]})
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = f"S5 Bangla human evaluation — annotator {annotator}"
    return f"""<!doctype html>
<html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:850px;margin:2rem auto;padding:0 1rem;line-height:1.5}}article{{border:1px solid #ccc;border-radius:10px;padding:1rem;margin:1rem 0}}.plot{{background:#f5f5f5;padding:.75rem}}label{{display:block;margin:.45rem 0}}button{{padding:.6rem 1rem}}.muted{{color:#555}}</style></head>
<body><h1>{html.escape(title)}</h1>
<p>প্রতিটি প্লট ও সম্ভাব্য দর্শক-মন্তব্য পড়ুন। মন্তব্যটি কোন engagement-specificity level-এর সঙ্গে বেশি মেলে তা বাছুন।</p>
<ul><li><b>Level 0:</b> সাধারণ/ফর্মুলামাফিক প্রতিক্রিয়া; চলচ্চিত্রের নির্দিষ্ট দিক নিয়ে কম সম্পৃক্ততা।</li><li><b>Level 1:</b> চলচ্চিত্রের নির্দিষ্ট দিক, ঘটনা বা নির্মাণ-উপাদান নিয়ে স্পষ্ট সম্পৃক্ততা।</li></ul>
<p class="muted">দৈর্ঘ্য, প্রশংসা/সমালোচনা বা আবেগ—কোনোটিই নিজে level নির্ধারণ করে না। একা কাজ করুন। পরিচয় অনুমান করার চেষ্টা করবেন না। প্রতিটি item-এ সবচেয়ে কাছের level-টি অবশ্যই বাছুন।</p>
<div id="items"></div><button id="download">উত্তর CSV ডাউনলোড করুন</button>
<script>const annotator={json.dumps(annotator)},items={data};const root=document.getElementById('items');
for(const x of items){{const a=document.createElement('article');a.innerHTML=`<h2>${{x.item_id}}</h2><div class="plot"><b>প্লট:</b> ${{x.plot}}</div><p><b>মন্তব্য:</b> ${{x.review}}</p><label><input required type="radio" name="${{x.item_id}}" value="0"> Level 0</label><label><input type="radio" name="${{x.item_id}}" value="1"> Level 1</label>`;root.appendChild(a)}}
document.getElementById('download').onclick=()=>{{const rows=['annotator,item_id,response'];for(const x of items){{const q=document.querySelector(`input[name="${{x.item_id}}"]:checked`);if(!q){{alert(`সব item-এর উত্তর দিন। অসম্পূর্ণ: ${{x.item_id}}`);return}}rows.push(`${{annotator}},${{x.item_id}},${{q.value}}`)}}const b=new Blob([rows.join('\\n')+'\\n'],{{type:'text/csv;charset=utf-8'}});const u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=`s5_human_eval_${{annotator}}.csv`;a.click();URL.revokeObjectURL(u)}};</script>
<!-- generated {html.escape(provenance['timestamp_utc'])}; commit {html.escape(str(provenance['git_commit']))} -->
</body></html>"""


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_human_eval_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rows = read_cases(root / cfg["inputs"]["cases_jsonl"])
    manifest = json.loads((root / cfg["inputs"]["score_manifest_json"]).read_text(encoding="utf-8"))
    observed_hash = hashlib.sha256((root / cfg["inputs"]["cases_jsonl"]).read_bytes()).hexdigest()
    registered_hash = manifest.get("result", {}).get("source_cases_sha256")
    if observed_hash != registered_hash:
        raise HumanEvalBuildError("cases archive SHA-256 does not match sealed score manifest")
    per_cell = int(cfg["sampling"]["per_condition_level"])
    selected = select_items(rows, seed=int(cfg["seed"]), per_cell=per_cell)
    if len(selected) != int(cfg["sampling"]["n_items"]):
        raise HumanEvalBuildError("n_items disagrees with balanced cell allocation")

    # Plot text is repeated identically across conditions in the frozen archive.
    plot_by_id = {}
    for row in rows:
        plot = row.get("plot_text") or row.get("plot")
        if isinstance(plot, str) and plot.strip():
            plot_by_id.setdefault(row["plot_id"], plot.strip())
    if len(plot_by_id) != 90:
        # The archived cases intentionally avoid duplicating plot text; use the
        # frozen eval-plot registry in that case.
        plots = pd.read_csv(root / "data/plots/plots_bn.csv")
        text_col = next(c for c in ("plot", "plot_text", "synopsis") if c in plots.columns)
        plot_by_id = dict(zip(plots["plot_id"], plots[text_col]))

    out = root / cfg["outputs"]["directory"]
    out.mkdir(parents=True, exist_ok=True)
    prov = stamp(cfg_path.as_posix(), {"stage": "human_eval_interface"})
    key_rows = []
    for index, row in enumerate(selected, 1):
        item_id = f"H{index:03d}"
        key_rows.append({"item_id": item_id, "case_key": row["key"],
                         "plot_id": row["plot_id"], "condition": row["condition"],
                         "replicate_seed": row["replicate_seed"],
                         "target_level": row["target_level"]})
        row["item_id"], row["plot"], row["review"] = (
            item_id, str(plot_by_id[row["plot_id"]]), emitted_text(row))

    pd.DataFrame(key_rows).to_csv(root / cfg["outputs"]["key_csv"], index=False,
                                  encoding="utf-8", lineterminator=NEWLINE)
    for annotator in cfg["sampling"]["annotators"]:
        rng = np.random.default_rng(int.from_bytes(hashlib.sha256(
            f"{cfg['seed']}|{annotator}".encode()).digest()[:8], "big"))
        ordered = [selected[i] for i in rng.permutation(len(selected))]
        write_text_lf(out / f"annotator_{annotator}.html",
                      interface_html(ordered, annotator=str(annotator), provenance=prov))
    write_text_lf(out / "README.md", "# S5 Bangla human evaluation\n\nSend annotators only their named HTML file. Never send `researcher_key.csv`.\n")
    print(f"wrote {len(selected)} blinded items for {len(cfg['sampling']['annotators'])} annotators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
