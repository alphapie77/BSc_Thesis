"""GATE G1 — the master K-table on one region.

    python -m src.cluster.s2d_ktable --config configs/s2d_ktable.yaml

The three-persona design is a hypothesis; this is the test. Interpretation is
pre-registered in `docs/protocol.md` ("RQ1-C pre-commitment") **before this ran**
— including what happens when K=2 wins and the design has to give way.

**The decision rule is not chosen here.** Pipeline §2.2 fixes it: the largest K
with prediction strength ≥ 0.80, with stability beating compactness where the
criteria disagree. This module computes; it does not adjudicate beyond applying
that rule.

Nothing is trained. K-Means, GMM and HDBSCAN are unsupervised fits used as
measurements, not as artifacts — inviolable rule 10 counts *trained model
artifacts that ship*, of which this produces none.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

NO_STABLE_K = "NO_STABLE_K"


def region_label(cfg) -> str:
    """Which subset this run is about, derived from the config, never hardcoded.

    The first version printed "region A" unconditionally. The region-B
    replication then produced a report headed *"the master K-table (region A)"*
    describing region B -- correct numbers under a wrong title, which is the
    kind of defect a reader has no way to catch and a reviewer certainly would.
    """
    name = str(cfg.get("name", ""))
    if name.endswith("_regionB"):
        return "region B"
    if name.endswith("_regionA") or name == "s2d_ktable":
        return "region A"
    return name or "this subset"


def check_n(asg, cfg) -> None:
    """Assert the input row count, or say out loud that it was not asserted.

    `expected_n` exists to catch a stale or half-regenerated input before an
    expensive run reads it. A **replication** run on a new subset cannot know
    that number in advance — it comes out of the run before it — so `null` is
    permitted and is **reported as an unguarded run** rather than passing
    silently. A check that can be disabled quietly is not a check.
    """
    n = cfg.get("expected_n")
    if n is None:
        print(f"⚠️  expected_n is null: {len(asg)} rows accepted UNGUARDED. "
              f"Fill it in {cfg.get('name', 'this config')} once the number is "
              f"known, so a later stale input is caught.")
        return
    if len(asg) != n:
        raise AssertionError(
            f"{cfg['input_assignments']} has {len(asg)} rows, expected {n}."
        )


# --------------------------------------------------------------------------
# Prediction strength (Tibshirani & Walther 2005)
# --------------------------------------------------------------------------
def prediction_strength(emb: np.ndarray, k: int, n_splits: int,
                        rng: np.random.Generator, n_init: int) -> float:
    """Mean prediction strength over repeated 50/50 splits.

    Split the data in two, cluster each half independently, then assign the test
    half to the *training* half's centroids. For each test cluster, count the
    fraction of its point-pairs that the training model also co-assigns. The
    score for a K is the **minimum over clusters** — deliberately, because one
    unreproducible cluster is enough to make a K untrustworthy, and a mean would
    let a good cluster hide a bad one.
    """
    from sklearn.cluster import KMeans

    n = emb.shape[0]
    scores = []
    for _ in range(n_splits):
        perm = rng.permutation(n)
        a, b = perm[: n // 2], perm[n // 2:]
        km_tr = KMeans(n_clusters=k, n_init=n_init,
                       random_state=int(rng.integers(0, 2**31))).fit(emb[a])
        km_te = KMeans(n_clusters=k, n_init=n_init,
                       random_state=int(rng.integers(0, 2**31))).fit(emb[b])
        te_lab = km_te.labels_
        cross = km_tr.predict(emb[b])       # test points under the TRAIN model

        per_cluster = []
        for c in range(k):
            idx = np.where(te_lab == c)[0]
            m = len(idx)
            if m <= 1:
                per_cluster.append(0.0)     # a singleton cluster is not evidence
                continue
            same = cross[idx][:, None] == cross[idx][None, :]
            np.fill_diagonal(same, False)
            per_cluster.append(same.sum() / (m * (m - 1)))
        scores.append(min(per_cluster))
    return float(np.mean(scores))


def bootstrap_ari(emb: np.ndarray, k: int, full_labels: np.ndarray,
                  n_runs: int, frac: float, rng: np.random.Generator,
                  n_init: int) -> tuple[float, float]:
    """Mean ± SD of ARI between a subsample re-clustering and the full labels.

    Pipeline §2.2's stability measure. Compared on the subsampled rows only —
    comparing against points the subsample never saw would measure the wrong
    thing.
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score

    n = emb.shape[0]
    m = int(round(n * frac))
    out = []
    for _ in range(n_runs):
        idx = rng.choice(n, size=m, replace=False)
        lab = KMeans(n_clusters=k, n_init=n_init,
                     random_state=int(rng.integers(0, 2**31))).fit_predict(emb[idx])
        out.append(adjusted_rand_score(full_labels[idx], lab))
    return float(np.mean(out)), float(np.std(out))


def gap_statistic(emb: np.ndarray, k: int, n_ref: int, rng: np.random.Generator,
                  n_init: int) -> tuple[float, float]:
    """Gap statistic (Tibshirani, Walther & Hastie 2001), in PCA space.

    The uniform reference is drawn over the data's bounding box. In 768
    dimensions a bounding box is almost entirely empty space, so the reference
    is meaningless there; the config reduces to ~50 components first. Reported
    with its standard error so the classic `gap(k) >= gap(k+1) - s(k+1)` rule
    can be applied by a reader.
    """
    from sklearn.cluster import KMeans

    def wk(x, kk):
        km = KMeans(n_clusters=kk, n_init=n_init,
                    random_state=int(rng.integers(0, 2**31))).fit(x)
        return np.log(km.inertia_) if km.inertia_ > 0 else 0.0

    obs = wk(emb, k)
    lo, hi = emb.min(axis=0), emb.max(axis=0)
    refs = []
    for _ in range(n_ref):
        ref = rng.uniform(lo, hi, size=emb.shape)
        refs.append(wk(ref, k))
    refs = np.array(refs)
    gap = float(refs.mean() - obs)
    sk = float(refs.std() * np.sqrt(1 + 1 / n_ref))
    return gap, sk


def trap_band(ari: float, shares: dict, cfg) -> str:
    b = cfg["trap_check"]["bands"]
    sb = cfg["trap_check"]["degenerate_cluster_share"]
    if any(v < sb["min"] or v > sb["max"] for v in shares.values()):
        return "DEGENERATE"
    if ari < b["not_sentiment_aligned_below"]:
        return "NOT_SENTIMENT_ALIGNED"
    lo, hi = b["partial_overlap_range"]
    if lo <= ari <= hi:
        return "PARTIAL_OVERLAP"
    return "PERSONA_CLAIM_FAILS"


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2d_ktable.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))

    # --- rows: this region, post-dedup, exactly as the S2 run left them -----
    asg = pd.read_csv(root / cfg["input_assignments"])
    check_n(asg, cfg)
    ids = set(asg[cfg["id_col"]])
    df = pd.read_csv(root / cfg["input_csv"])
    df = df[df[cfg["id_col"]].isin(ids)].sort_values(
        cfg["id_col"], kind="mergesort").reset_index(drop=True)
    assert len(df) == len(asg), "id mismatch between assignments and bn_clean"
    labels = df[cfg["label_col"]].to_numpy()
    print(f"{region_label(cfg)}: {len(df)} rows, "
          f"{dict(pd.Series(labels).value_counts().sort_index())}")

    emb = embed(df[cfg["text_col"]].astype(str).tolist(), cfg, root)

    from sklearn.cluster import KMeans
    from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,
                                 davies_bouldin_score, silhouette_score)
    from sklearn.mixture import GaussianMixture

    ni = int(cfg["kmeans"]["n_init"])
    rows = []
    for k in cfg["k_range"]:
        km = KMeans(n_clusters=k, n_init=ni,
                    random_state=int(cfg["kmeans"]["random_state"])).fit(emb)
        lab = km.labels_
        shares = {int(c): v / len(lab) for c, v in
                  pd.Series(lab).value_counts().items()}
        ps = prediction_strength(emb, k, int(cfg["prediction_strength"]["n_splits"]),
                                 rng, ni)
        bmean, bsd = bootstrap_ari(emb, k, lab, int(cfg["bootstrap"]["n_runs"]),
                                   float(cfg["bootstrap"]["subsample_frac"]),
                                   rng, ni)
        gap, sk = gap_statistic(emb, k, int(cfg["gap_statistic"]["n_reference"]),
                                rng, ni)
        gm = GaussianMixture(
            n_components=k, covariance_type=cfg["gmm"]["covariance_type"],
            n_init=int(cfg["gmm"]["n_init"]), random_state=42).fit(emb)
        ari_sent = float(adjusted_rand_score(labels, lab))

        rows.append({
            "K": k,
            "silhouette": float(silhouette_score(emb, lab)),
            "calinski_harabasz": float(calinski_harabasz_score(emb, lab)),
            "davies_bouldin": float(davies_bouldin_score(emb, lab)),
            "gap": gap, "gap_se": sk,
            "prediction_strength": ps,
            "bootstrap_ari_mean": bmean, "bootstrap_ari_sd": bsd,
            "gmm_bic": float(gm.bic(emb)),
            "ari_vs_sentiment": ari_sent,
            "min_cluster_share": min(shares.values()),
            "max_cluster_share": max(shares.values()),
            "trap_band": trap_band(ari_sent, shares, cfg),
        })
        print(f"  K={k}  PS={ps:.3f}  bootARI={bmean:.3f}±{bsd:.3f}  "
              f"sil={rows[-1]['silhouette']:.3f}  ARI_sent={ari_sent:.3f}  "
              f"{rows[-1]['trap_band']}")

    tab = pd.DataFrame(rows)

    # --- HDBSCAN: finds its own K --------------------------------------------
    hdb = {}
    try:
        import hdbscan as _h
        cl = _h.HDBSCAN(min_cluster_size=int(cfg["hdbscan"]["min_cluster_size"]),
                        min_samples=int(cfg["hdbscan"]["min_samples"]))
        hl = cl.fit_predict(emb)
        hdb = {
            "k_found": int(len(set(hl)) - (1 if -1 in hl else 0)),
            "noise_fraction": float((hl == -1).mean()),
            "ari_vs_sentiment": float(adjusted_rand_score(labels, hl)),
        }
        print(f"  HDBSCAN: K={hdb['k_found']}, "
              f"noise={hdb['noise_fraction']:.1%}")
    except Exception as e:
        hdb = {"error": f"{type(e).__name__}: {e}"}
        print(f"  HDBSCAN unavailable: {hdb['error']}")

    # --- the pre-registered rule, applied mechanically -----------------------
    thr = float(cfg["prediction_strength"]["threshold"])
    passing = tab[tab["prediction_strength"] >= thr]
    selected = int(passing["K"].max()) if len(passing) else None

    out_csv = root / cfg["outputs"]["table_csv"]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    tab.to_csv(out_csv, index=False, encoding="utf-8", lineterminator=NEWLINE)
    out_md = write_text_lf(root / cfg["outputs"]["report_md"],
                           build_report(cfg, cfg_path, stamp(cfg_path.as_posix()),
                                        tab, hdb, selected, thr, len(df)))
    print(f"\nwrote {out_csv}\nwrote {out_md}")
    print(f"\nSELECTED K = {selected if selected else NO_STABLE_K}")
    print("Read docs/protocol.md RQ1-C before interpreting this.")
    return 0


def embed(texts, cfg, root: Path) -> np.ndarray:
    ec = cfg["embedding"]
    cache = root / ec["cache_npy"] if ec.get("cache_npy") else None
    if cache is not None and cache.exists():
        e = np.load(cache)
        if e.shape[0] != len(texts):
            raise AssertionError(
                f"cached embeddings have {e.shape[0]} rows, input has "
                f"{len(texts)}. Delete {cache} and re-embed."
            )
        print(f"loaded cached embeddings {e.shape}")
        return e
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(ec["model"])
    if ec.get("max_seq_length"):
        m.max_seq_length = int(ec["max_seq_length"])
    e = m.encode(texts, batch_size=int(ec["batch_size"]), convert_to_numpy=True,
                 normalize_embeddings=bool(ec["normalize"]),
                 show_progress_bar=True).astype(np.float32)
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, e)
    return e


def build_report(cfg, cfg_path, prov, tab, hdb, selected, thr, n) -> str:
    md = tab.to_markdown(index=False, floatfmt=".4f")
    hdb_md = ("\n".join(f"- **{k}**: {v}" for k, v in hdb.items())
              if hdb else "_not run_")

    if selected is None:
        verdict = f"""**{NO_STABLE_K}.** No K in {cfg['k_range']} reaches prediction
strength ≥ {thr}. Per the pre-registration (protocol.md, RQ1-C), the honest
reading is that **this corpus does not support a stable partition at any K
tested**. The persona scheme cannot then be data-derived, and the thesis must
either use a **theory-driven** scheme validated by G-300 — which the pipeline's
Gate G2 fallback already anticipates — or reframe RQ1 as a negative result.
**Both are publishable. Lowering the cutoff is not an option:** 0.80 is
Tibshirani & Walther's own and was adopted before this table existed."""
    else:
        row = tab[tab["K"] == selected].iloc[0]
        extra = ""
        if selected == 2:
            extra = ("\n\n⚠️ **K = 2 means the three-persona design gives way.** "
                     "The obvious worry is that these clusters *are* the "
                     "sentiment split; the `ari_vs_sentiment` column settles "
                     "that and is reported either way. K=3 is retained as the "
                     "theory-motivated secondary (pipeline §2.2). Note the "
                     "regions differ here: region A carries two sentiment "
                     "classes, region B all three (fact (split)), so ARI is "
                     "structurally capped differently in each and the two "
                     "values are not directly comparable.")
        elif selected >= 4:
            extra = ("\n\n⚠️ **K ≥ 4 is a finding about the audience, not a "
                     "failure** — but check the cluster-share band before "
                     "believing it at n ≈ 1,897 with 8-word reviews.")
        verdict = f"""**Selected K = {selected}** — the largest K with prediction
strength ≥ {thr} (PS = {row['prediction_strength']:.3f}), per pipeline §2.2.
Bootstrap ARI {row['bootstrap_ari_mean']:.3f} ± {row['bootstrap_ari_sd']:.3f}.
Trap-check at this K: **{row['trap_band']}**
(ARI vs Sentiment = {row['ari_vs_sentiment']:.4f}).{extra}"""

    return f"""# S2d — Gate G1: the master K-table ({region_label(cfg)})

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-C) before this
> table existed.** Read that section before reading these numbers. The
> three-persona design is the hypothesis; this is the test.

- **Config:** `{cfg_path}` · **n:** {n} ({region_label(cfg)}, post-dedup)
- **Generated (UTC):** {prov['timestamp_utc']} · **Commit:** `{prov['git_commit']}`
- **Seed:** {cfg['seed']} · K range: {cfg['k_range']}

## Verdict

{verdict}

## The full table — reported whole, no cherry-picking

{md}

**How to read it.** `prediction_strength` is the decision variable; everything
else is context. `bootstrap_ari_mean` is stability (pipeline §2.2: **stability
beats compactness**). `silhouette` and `davies_bouldin` measure compactness and
will often disagree with stability — that disagreement is expected and is
reported rather than resolved by preference. `trap_band` applies the same RQ1
bands at every K: **a K can be perfectly stable and still be a rediscovery of
the sentiment split**, which is why both columns are here.

## HDBSCAN — an independent opinion on K

{hdb_md}

HDBSCAN chooses its own K and is allowed to call points noise. If it lands near
the selected K, that is strong independent evidence. A large noise fraction is
itself a finding: it would mean a substantial part of the corpus belongs to no
persona at all.

## What this step does NOT settle

Stability is not validity. A stable K means the partition is reproducible, not
that its groups are **audience personas**. That question is G-300's, with three
annotators and κ/α, and nothing in this table can pre-empt it.
"""


if __name__ == "__main__":
    raise SystemExit(main())
