#!/usr/bin/env python3
"""Does the committed Verifier-A behave the same HERE as where it was measured?

WHY THIS EXISTS
---------------
Verifier-A was fitted on Kaggle: Linux, Python 3.12.13 (`results/s3c_verifier_a.json`).
The Phase 4 loop runs on Sabbir's Windows machine, Python 3.13.3, and
`requirements.lock.txt` of 2026-08-11 records **transformers 5.14.1** there --
while S3.2 was deliberately re-run under **transformers < 5** because 5.x broke
an arm, and its numbers are attributed to transformers 4.57.6.

Two things therefore differ between where the Critic's judge was MEASURED and
where it will JUDGE: the operating system and Python minor, and the encoder
stack around LaBSE. Coakley et al. (2022) measured **> 6 pp** of accuracy
variation from environment alone; Verifier-A's reproduction gate is **0.6 pp**
(half a dev item). Those two numbers are an order of magnitude apart, which is
exactly the situation `protocol.md` §S3.3 was worried about when it declined to
run the verifiers on a third host.

So this is run once, before the Critic is trusted, and its answer goes in the
appendix either way. **A null result here is a real result**: "the artifact
reproduces across hosts" is a claim this thesis would otherwise be making
silently.

WHAT IT DOES NOT DO
-------------------
**It never refits and never writes to `artifacts/` or `results/s3c_*`.** Those
are the committed Kaggle-produced files. Re-running `train_verifier_a.py` here
would overwrite them with locally-fitted ones and destroy the very comparison
this script performs -- and it would look like success, because the numbers
would match themselves.

Read-only, by construction: it loads the committed artifact and the committed
per-item predictions, recomputes predictions in THIS environment, and diffs.
Reported in ITEMS, because one dev item = 0.0122 macro-F1 and decimals invite
over-reading at n = 82.

Run:  python src/agents/preflight.py --config configs/s3c_verifier_a.yaml
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.seed import set_seed  # noqa: E402
from src.verifier.split_access import load_training_rows  # noqa: E402

#: The value S3.2b measured and S3.3 reproduced on Kaggle. Not a target to hit
#: -- a reference to diff against. ref: results/s3c_verifier_a.md
KAGGLE_REFERENCE_MACRO_F1 = 0.9866

#: One dev item, in macro-F1, at n = 82. Every gap below is reported as a
#: multiple of this. ref: protocol.md §S3.3, "read every gap in items".
ONE_DEV_ITEM = 0.0122


def macro_f1(y_true: list[int], y_pred: list[int]) -> float:
    from sklearn.metrics import f1_score

    return float(f1_score(y_true, y_pred, average="macro"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    inp, out = cfg["inputs"], cfg["outputs"]

    _, dev = load_training_rows(
        "A",
        split_map=inp["split_map"],
        k2_assignments=inp["k2_assignments"],
        cleaned_csv=inp["cleaned_csv"],
        hold_out_dev=True,
    )

    committed: dict[str, dict] = {}
    with open(out["dev_predictions_csv"], encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            committed[row["review_id"]] = row

    import warnings

    import joblib
    import sklearn
    from sentence_transformers import SentenceTransformer

    # Capture rather than let scroll past. sklearn's InconsistentVersionWarning
    # is the single most informative line this script can print: it is the
    # pickling library itself saying the artifact was written by a different
    # version, with "may lead to ... invalid results" in its own words. A
    # warning that flies past above a progress bar is not a disclosure.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        art = joblib.load(out["artifact"])
    version_warnings = [
        str(w.message) for w in caught if "Version" in type(w.message).__name__
    ]

    if not isinstance(art, dict) or "head" not in art:
        raise SystemExit(
            f"artifact {out['artifact']} is not the expected dict "
            f"(keys: {sorted(art) if isinstance(art, dict) else type(art)}). "
            "train_verifier_a.py dumps {'role','encoder','head',...}."
        )

    clf = art["head"]

    # Use the ARTIFACT's own recorded encoder and normalisation, not the
    # config's. The question is whether this checkpoint reproduces itself, and
    # a config edited since the fit would silently change what is being tested.
    encoder = SentenceTransformer(art["encoder"])
    vecs = encoder.encode(
        list(dev.texts),
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=bool(art.get("normalize_embeddings", True)),
    )
    here = [int(p) for p in clf.predict(vecs)]

    # 🔑 The load-bearing comparison, and NOT the hard predictions above.
    #
    # The Critic never calls .predict(). It calls predict_proba, mixes the
    # result with the symbolic score, and compares the mixture to tau -- and
    # tau is swept at QUANTILES of the observed score distribution (decision
    # 17). So the object that has to be host-invariant is the SCORE, not the
    # argmax. Two runs can agree on all 82 labels while their probabilities
    # differ enough to reshuffle the quantiles every threshold is placed at.
    #
    # Comparing only labels was this script's first version, and it would have
    # returned HOST_INVARIANT while leaving the question that matters unasked.
    p_here = [float(p) for p in clf.predict_proba(vecs)[:, 1]]
    p_committed = [float(committed[i]["p_cluster1"]) for i in dev.review_ids]
    deltas = [abs(a - b) for a, b in zip(p_here, p_committed)]
    max_delta = max(deltas)
    # The committed CSV stores 6 decimals, so agreement can never be measured
    # finer than 5e-7. A delta at or below that is "identical as far as the
    # recorded file can say", which is a weaker claim than "identical" and is
    # reported as the weaker one.
    CSV_RESOLUTION = 5e-7

    # 🔑 Magnitude is the wrong instrument, and naming a magnitude threshold
    # would be a hand-written constant with no criterion.
    #
    # tau is placed at QUANTILES of the score distribution -- i.e. at ORDER
    # STATISTICS. A drift that preserves the ordering moves no quantile to a
    # different item, however large it is; a drift that swaps two adjacent
    # scores moves a threshold between items, however small it is. So the
    # decisive quantities are (a) whether the ranking changed, and (b) whether
    # the drift is smaller than the closest gap between two observed scores.
    #
    # This is the same instrument decision 17 already used on temperature
    # scaling ("0 rank inversions, 1 new tie, 2 items saturated"), reused rather
    # than reinvented -- and it was the right instrument there for the same
    # reason it is right here.
    order_here = sorted(range(len(p_here)), key=lambda i: p_here[i])
    order_committed = sorted(range(len(p_committed)), key=lambda i: p_committed[i])
    rank_inversions = sum(1 for a, b in zip(order_here, order_committed) if a != b)

    srt = sorted(p_committed)
    gaps = [b - a for a, b in zip(srt, srt[1:]) if b > a]
    min_adjacent_gap = min(gaps) if gaps else 0.0

    # Free wall check while we are here: the artifact records the ids it was
    # fitted on, so the "dev was held out" claim can be verified against the
    # checkpoint itself rather than against the script that wrote it.
    trained_ids = set(art.get("trained_on", {}).get("ids", []))
    overlap = trained_ids & set(dev.review_ids)
    if overlap:
        raise SystemExit(
            f"REFUSED: {len(overlap)} dev ids appear in Verifier-A's recorded "
            "training ids. The 0.9866 is then measured on training data and "
            "nothing downstream is interpretable. Stop."
        )

    y_true = list(dev.labels)
    f1_here = macro_f1(y_true, here)
    f1_committed = macro_f1(
        y_true, [int(committed[i]["y_pred"]) for i in dev.review_ids]
    )

    flips = [
        rid
        for rid, p in zip(dev.review_ids, here)
        if int(committed[rid]["y_pred"]) != p
    ]

    print(f"\nartifact                    : {out['artifact']}")
    print(f"encoder (from artifact)     : {art['encoder']}")
    print(f"dev ids in training set     : {len(overlap)}  (must be 0)")
    print(f"sklearn here                : {sklearn.__version__}")
    if version_warnings:
        print("PICKLE VERSION MISMATCH     : " + version_warnings[0].split("\n")[0])
        print("  ^ sklearn's own words. This is the environment risk, stated by")
        print("    the library rather than inferred by us.")
    else:
        print("pickle version mismatch     : none reported")
    print(f"\ndev rows compared           : {len(dev)}")
    print(f"macro-F1 recorded on Kaggle : {f1_committed:.4f}")
    print(f"macro-F1 recomputed here    : {f1_here:.4f}")
    print(f"reference (S3.2b / S3.3)    : {KAGGLE_REFERENCE_MACRO_F1}")
    gap_items = abs(f1_here - f1_committed) / ONE_DEV_ITEM
    print(f"gap                         : {gap_items:.2f} dev items")
    print(f"per-item prediction flips   : {len(flips)}"
          + (f"  {flips}" if flips else ""))
    print(f"max |Δ p_cluster1|          : {max_delta:.3e}"
          f"   (CSV resolution {CSV_RESOLUTION:.0e})")
    print(f"rank inversions             : {rank_inversions}")
    print(f"smallest gap between scores : {min_adjacent_gap:.3e}")
    print("  ^ THESE are the numbers that decide it, not the magnitude above.\n"
          "    τ is placed at quantiles = order statistics. Drift that keeps\n"
          "    the ordering moves no threshold between items however large it\n"
          "    is; drift that swaps two neighbours moves one however small.")

    if flips:
        print(
            f"\nVERDICT: HOST_DEPENDENT — {len(flips)} label(s) changed with no\n"
            "change to the model or the data, only to the environment. Stop and\n"
            "record it before building the Critic."
        )
        return 1
    elif rank_inversions == 0 and max_delta < min_adjacent_gap:
        print(
            "\nVERDICT: QUANTILES_STABLE — all 82 labels agree, the score\n"
            f"ORDERING is identical (0 inversions), and the drift ({max_delta:.3e})\n"
            f"is smaller than the closest gap between two observed scores\n"
            f"({min_adjacent_gap:.3e}). Every quantile therefore falls between the\n"
            "same two items on both hosts, so τ selects the same operating\n"
            "points. The Critic may use this artifact locally.\n"
            "\n⚠️  What is NOT established, and must not be written as though it\n"
            "    were: that the estimator is unaffected. The sklearn/encoder\n"
            "    stack and the host can change together, and this run cannot\n"
            "    separate them, because the committed file records\n"
            "    probabilities, not embeddings. The drift is at the 1e-6 scale\n"
            "    typical of float/BLAS differences rather than of a changed\n"
            "    estimator, but that is an inference from magnitude, not a\n"
            "    measurement, and it is labelled as one."
        )
        return 0
    else:
        print(
            f"\nVERDICT: QUANTILES_AT_RISK — labels agree, but the ordering does\n"
            f"not survive: {rank_inversions} rank inversion(s), drift {max_delta:.3e}\n"
            f"against a smallest score gap of {min_adjacent_gap:.3e}.\n"
            "🔴 τ is placed at order statistics, so a threshold can now fall\n"
            "between a different pair of items on this host than on Kaggle.\n"
            "Do not build the Critic on this artifact until it is resolved."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
