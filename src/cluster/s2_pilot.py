"""S2 PILOT -- LaBSE near-duplicate removal + the mandatory ARI trap-check.

Reads `data/cleaned/bn_clean.csv`, embeds every surviving review with LaBSE,
removes near-duplicates above a cosine threshold, then runs K-Means (K=3) on the
survivors and reports ARI(cluster_labels, Sentiment).

Writes exactly two files (plus an optional embedding cache):
  * `data/cleaned/near_dup_pairs.csv`      -- every near-duplicate pair found
  * `results/s2_pilot_ari_trapcheck.md`    -- the trap-check report

**THIS SCRIPT DOES NOT FREEZE THE SPLIT.** It writes no split map. The frozen
split (`data/splits/split_map_v1.json`) is created in a later step, deliberately
after the trap-check outcome is on record, so the split cannot be tuned to it.

The trap-check exists because S0 found a median review length of 8 words: the
easiest structure for LaBSE to recover from 8 words is plausibly sentiment
itself, not engagement persona. The bands in `configs/s2_pilot.yaml` are
pre-committed in `docs/protocol.md` (RQ1). The number is reported under every
outcome. Do not re-run with different settings to move it.

Intended host: Kaggle GPU. Run:
    python -m src.cluster.s2_pilot --config configs/s2_pilot.yaml
"""
import os

# Must precede any transformers/sentence-transformers import. Without this,
# transformers probes for a TensorFlow backend and dies on Keras 3
# ("not yet supported in Transformers"). We only ever use the torch backend.
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"

import argparse  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


def load_clean(cfg, repo_root: Path) -> pd.DataFrame:
    path = repo_root / cfg["input_csv"]
    df = pd.read_csv(path, dtype={cfg["id_col"]: str})
    expected = cfg["expected_input_n"]
    if len(df) != expected:
        raise AssertionError(
            f"{cfg['input_csv']} has {len(df)} rows, expected {expected}. "
            "bn_clean.csv must not be regenerated -- review_ids are referenced "
            "by the split map. Investigate before changing this number."
        )
    if df[cfg["id_col"]].duplicated().any():
        raise AssertionError("review_id is not unique in the input")
    # Deterministic order by review_id: 'keep first' must not depend on CSV order.
    return df.sort_values(cfg["id_col"], kind="mergesort").reset_index(drop=True)


def embed(texts: list[str], cfg, repo_root: Path) -> np.ndarray:
    """LaBSE embeddings, L2-normalized so cosine == dot product."""
    ec = cfg["embedding"]
    cache = repo_root / ec["cache_npy"] if ec.get("cache_npy") else None
    if cache is not None and cache.exists():
        emb = np.load(cache)
        if emb.shape[0] != len(texts):
            raise AssertionError(
                f"cached embeddings have {emb.shape[0]} rows, input has "
                f"{len(texts)}. Delete {cache} and re-embed."
            )
        print(f"loaded cached embeddings {emb.shape} from {cache}")
        return emb

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(ec["model"])
    if ec.get("max_seq_length"):
        model.max_seq_length = int(ec["max_seq_length"])
    emb = model.encode(
        texts,
        batch_size=int(ec["batch_size"]),
        convert_to_numpy=True,
        normalize_embeddings=bool(ec["normalize"]),
        show_progress_bar=True,
    ).astype(np.float32)

    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, emb)
        print(f"cached embeddings {emb.shape} to {cache}")
    return emb


#: Histogram resolution for the off-diagonal cosine distribution: 20,000 bins
#: over [-1, 1] => bin width 1e-4. The full upper triangle is ~11.2M values at
#: n=4730; a histogram summarises it in fixed memory so the n x n matrix is
#: never materialised. Percentiles are therefore accurate to the bin width,
#: which is reported alongside them. The max is tracked exactly.
COSINE_BINS = 20000


def all_near_dup_pairs(emb: np.ndarray, min_threshold: float):
    """Every pair (i < j) with cosine >= min_threshold, plus a distribution.

    Row order is already review_id order, so i < j means i has the lower id.
    Computed in row blocks to keep peak memory bounded rather than
    materializing the full n x n matrix. The same pass accumulates a histogram
    of every off-diagonal (strict upper triangle) cosine, so the distribution
    costs no extra matmuls.
    """
    n = emb.shape[0]
    rows = []
    edges = np.linspace(-1.0, 1.0, COSINE_BINS + 1)
    hist = np.zeros(COSINE_BINS, dtype=np.int64)
    max_cos, total = -1.0, 0

    block = 512
    for start in range(0, n, block):
        stop = min(start + block, n)
        sims = emb[start:stop] @ emb.T          # (block, n)
        # Keep only the strict upper triangle for these rows.
        for local, i in enumerate(range(start, stop)):
            s = sims[local][i + 1:]
            if s.size == 0:
                continue
            total += int(s.size)
            hist += np.histogram(s, bins=edges)[0]
            max_cos = max(max_cos, float(s.max()))
            for j in np.nonzero(s >= min_threshold)[0]:
                rows.append((i, i + 1 + int(j), float(s[j])))

    pairs = pd.DataFrame(rows, columns=["i", "j", "cosine"])
    dist = {
        "n_offdiagonal_pairs": total,
        "max": max_cos,
        "bin_width": float(edges[1] - edges[0]),
        "percentiles": {
            q: hist_percentile(hist, edges, q)
            for q in (50, 90, 95, 99, 99.9)
        },
    }
    return pairs, dist


def hist_percentile(hist: np.ndarray, edges: np.ndarray, q: float) -> float:
    """Percentile from a histogram, interpolated within the containing bin.

    Locates the bin holding the q-th ranked value, then interpolates linearly
    across it by how far into that bin's count the target rank falls. Without
    the interpolation the estimate is only as good as the bin's upper edge,
    which in the sparse upper tail can sit several bin widths above the true
    order statistic.
    """
    total = int(hist.sum())
    if total == 0:
        return float("nan")
    cum = np.cumsum(hist)
    target = q / 100.0 * total
    idx = min(int(np.searchsorted(cum, target)), len(hist) - 1)
    below = float(cum[idx - 1]) if idx else 0.0
    in_bin = float(hist[idx])
    frac = (target - below) / in_bin if in_bin > 0 else 0.0
    lo, hi = float(edges[idx]), float(edges[idx + 1])
    return lo + min(max(frac, 0.0), 1.0) * (hi - lo)


def greedy_keep_first(n: int, pairs: pd.DataFrame, threshold: float):
    """Remove j when it is >= threshold to an already-KEPT row i < j.

    Greedy in review_id order, so the lowest-id member of a near-duplicate
    cluster always survives ('keep: first_by_review_id'). Comparing only against
    kept rows means a row removed as a duplicate cannot itself evict a third row
    -- without that, transitive chains would delete more than intended.
    """
    at = pairs[pairs["cosine"] >= threshold]
    # partners_before[j] = [(i, cos), ...] for i < j
    partners = {}
    for i, j, c in at[["i", "j", "cosine"]].itertuples(index=False):
        partners.setdefault(j, []).append((i, c))

    removed = {}   # j -> (anchor_i, cosine)
    for j in range(n):
        for i, c in sorted(partners.get(j, []), key=lambda t: (-t[1], t[0])):
            if i not in removed:            # anchor is still kept
                removed[j] = (i, c)
                break
    kept = np.array([k for k in range(n) if k not in removed], dtype=int)
    return kept, removed


def region_of(ids: np.ndarray, boundary: int) -> np.ndarray:
    """Which half of the source .xlsx each review came from.

    `review_id` is `bn_<raw row>`, so the raw row order of the source file --
    and therefore how the file was assembled -- is recoverable from the id
    alone. See `results/s2c_region_split.md`: the corpus is two corpora joined
    at row 1999, and the register signature tracks this boundary rather than the
    sentiment label.
    """
    rows = np.array([int(str(i).replace("bn_", "")) for i in ids])
    return np.where(rows < boundary, "A_organic", "B_uniform")


def cluster_and_ari(emb: np.ndarray, labels: np.ndarray, cfg,
                    aux_labels: np.ndarray | None = None):
    """Cluster, then score against Sentiment and (optionally) against region.

    `aux_labels` exists because of S2c: if the clusters are recovering which
    FILE a review came from rather than anything about audiences, then
    ARI(cluster, region) will exceed ARI(cluster, Sentiment) -- and that
    comparison is the whole question. Reported side by side so neither number
    can be quoted without the other.
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score

    cc = cfg["clustering"]
    if cc.get("cluster_in_umap_space"):
        raise ValueError(
            "cluster_in_umap_space=true violates inviolable rule 9 "
            "(UMAP is visualization-only); refusing to run."
        )
    km = KMeans(
        n_clusters=int(cc["k"]),
        n_init=int(cc["n_init"]),
        random_state=int(cc["random_state"]),
    )
    from scipy.stats import chi2_contingency

    assign = km.fit_predict(emb)
    n = len(assign)

    sizes = {
        int(k): int(v)
        for k, v in pd.Series(assign).value_counts().sort_index().items()
    }
    shares = {k: v / n for k, v in sizes.items()}

    # A cluster holding almost nothing, or nearly everything, means K-Means
    # found no usable structure -- ARI on such a solution is not interpretable.
    # Thresholds come from the config so they cannot drift from protocol.md.
    share_band = cfg.get("trap_check", {}).get(
        "degenerate_cluster_share", {"min": 0.05, "max": 0.70}
    )
    lo_share, hi_share = float(share_band["min"]), float(share_band["max"])
    degenerate = [k for k, s in shares.items() if s < lo_share or s > hi_share]

    ct = pd.crosstab(pd.Series(assign, name="cluster"),
                     pd.Series(labels, name="sentiment"))
    chi2, p, dof, _ = chi2_contingency(ct.to_numpy())
    # Cramer's V for an r x c table; min(r,c)-1 = 2 for 3 clusters x 3 classes.
    denom = n * (min(ct.shape) - 1)
    cramers_v = float(np.sqrt(chi2 / denom)) if denom > 0 else float("nan")

    aux = {}
    if aux_labels is not None:
        aux_ct = pd.crosstab(pd.Series(assign, name="cluster"),
                             pd.Series(aux_labels, name="region"))
        aux = {
            "ari_region": float(adjusted_rand_score(aux_labels, assign)),
            "region_crosstab_index": [int(x) for x in aux_ct.index],
            "region_crosstab_columns": [str(c) for c in aux_ct.columns],
            "region_crosstab_values": aux_ct.to_numpy().tolist(),
        }

    return {
        "assign": assign.tolist(),
        **aux,
        "ari": float(adjusted_rand_score(labels, assign)),
        "n": n,
        "cluster_sizes": sizes,
        "cluster_shares": {k: round(v, 4) for k, v in shares.items()},
        "degenerate": bool(degenerate),
        "degenerate_clusters": degenerate,
        "crosstab": ct.to_dict(),
        "crosstab_index": [int(x) for x in ct.index],
        "crosstab_columns": [int(x) for x in ct.columns],
        "crosstab_values": ct.to_numpy().tolist(),
        "chi2": float(chi2),
        "chi2_p": float(p),
        "chi2_dof": int(dof),
        "cramers_v": cramers_v,
        "inertia": float(km.inertia_),
    }


# Verdict strings map ONE-TO-ONE onto the band names in docs/protocol.md, so a
# reader can line up this report against the pre-registration without
# interpretation. Do not rename without renaming the protocol band.
NO_CLAIM = "NO_CLAIM"                              # Band 0 -- degenerate
NOT_SENTIMENT_ALIGNED = "NOT_SENTIMENT_ALIGNED"    # Band 1 -- ARI < 0.20
PARTIAL_OVERLAP = "PARTIAL_OVERLAP"                # Band 2 -- 0.20..0.60
PERSONA_CLAIM_FAILS = "PERSONA_CLAIM_FAILS"        # Band 3 -- ARI > 0.60

#: Emitted with Band 2 only. The pre-registration makes the residual test
#: mandatory, so the marker is part of the verdict rather than a footnote.
RESIDUAL_TEST_REQUIRED = "RESIDUAL_TEST_REQUIRED"


def verdict(res: dict, bands: dict) -> dict:
    """Map a clustering result onto its pre-registered band.

    **Degeneracy is the first gate and overrides ARI entirely.** A partition
    where one cluster is near-empty or holds most of the data scores a LOW ARI
    by construction -- by failing to partition, not by being independent of
    sentiment. Reading that as PASS is the precise failure this ordering
    prevents, so Band 0 returns NO_CLAIM and no PASS/CAVEAT/FAIL-style verdict
    is emitted at all. Only a non-degenerate partition reaches the ARI bands.

    Returns {band, verdict, markers, text}.
    """
    if res.get("degenerate"):
        shares = ", ".join(
            f"cluster {k}: {v * 100:.1f}%" for k, v in res["cluster_shares"].items()
        )
        return {
            "band": 0,
            "verdict": NO_CLAIM,
            "markers": [],
            "text": (
                f"**{NO_CLAIM} (Band 0 — DEGENERATE).** Cluster(s) "
                f"{res['degenerate_clusters']} fall outside the permitted share "
                f"band ({shares}). K-Means did not partition the data, so **ARI "
                f"is uninterpretable here and no claim is permitted in either "
                f"direction** — a non-partition scores low ARI by construction "
                f"and must not be read as independence from sentiment. "
                f"Re-examine K, the encoder, and the distance metric; ARI "
                f"reporting is suspended until the partition is non-degenerate "
                f"(protocol.md RQ1, Band 0)."
            ),
        }

    ari = res["ari"]
    lo, hi = bands["partial_overlap_range"]

    if ari < bands["not_sentiment_aligned_below"]:
        return {
            "band": 1,
            "verdict": NOT_SENTIMENT_ALIGNED,
            "markers": [],
            "text": (
                f"**{NOT_SENTIMENT_ALIGNED} (Band 1).** ARI {ari:.4f} < "
                f"{bands['not_sentiment_aligned_below']}: the clusters are not "
                "aligned with the sentiment axis. **This is not evidence that "
                "the personas are valid** — only that they are not a sentiment "
                "rediscovery. G-300 human validation remains the arbiter "
                "(protocol.md RQ1, Band 1)."
            ),
        }

    if lo <= ari <= hi:
        return {
            "band": 2,
            "verdict": PARTIAL_OVERLAP,
            "markers": [RESIDUAL_TEST_REQUIRED],
            "text": (
                f"**{PARTIAL_OVERLAP} (Band 2) — {RESIDUAL_TEST_REQUIRED}.** ARI "
                f"{ari:.4f} falls in [{lo}, {hi}]. The residual test is "
                "**mandatory, not discretionary**: conditioning on `Sentiment`, "
                "does cluster membership still predict length, intensifier rate "
                "and specificity? If yes, the persona claim survives but must be "
                "disclosed as sentiment-correlated wherever it appears. If no, "
                "Band 3 applies (protocol.md RQ1, Band 2)."
            ),
        }

    return {
        "band": 3,
        "verdict": PERSONA_CLAIM_FAILS,
        "markers": [],
        "text": (
            f"**{PERSONA_CLAIM_FAILS} (Band 3).** ARI {ari:.4f} > "
            f"{bands['persona_claim_fails_above']}: the persona claim fails as "
            "stated. Two candidate explanations, which this data cannot "
            "distinguish: (1) genuine persona/sentiment overlap; or (2) a "
            "**venue/community selection effect** — clusters recovering the "
            "source Facebook group or YouTube channel rather than any persona. "
            "Explanation (2) is **untestable in principle here**, because venue "
            "was not retained at collection (provenance fact (c)); it must be "
            "stated as an unresolvable alternative, not dismissed. Reframe as "
            "'sentiment-anchored engagement tiers' or re-operationalize with "
            "engagement features. Reported either way (protocol.md RQ1, Band 3)."
        ),
    }


def crosstab_md(res) -> str:
    """3x3 cluster x Sentiment contingency table with margins."""
    cols = res["crosstab_columns"]
    vals = res["crosstab_values"]
    head = " | ".join(f"Sentiment {c}" for c in cols)
    lines = [f"| Cluster | {head} | Row total |", "|---" * (len(cols) + 2) + "|"]
    for k, row in zip(res["crosstab_index"], vals):
        lines.append(
            f"| {k} | " + " | ".join(str(v) for v in row) + f" | {sum(row)} |"
        )
    totals = [sum(r[c] for r in vals) for c in range(len(cols))]
    lines.append(
        "| **Total** | " + " | ".join(f"**{t}**" for t in totals)
        + f" | **{sum(totals)}** |"
    )
    return "\n".join(lines)


def region_md(primary, baseline) -> str:
    """The S2c question, answered numerically: sentiment or file of origin?

    Reported next to the sentiment ARI rather than in a separate document,
    because quoting either number alone misrepresents the result.
    """
    if "ari_region" not in primary:
        return (
            "### Cluster × region\n\n_Not scored: this run covers a single "
            "region, so there is nothing to separate._"
        )

    a_sent, a_reg = primary["ari"], primary["ari_region"]
    cols = primary["region_crosstab_columns"]
    vals = primary["region_crosstab_values"]
    lines = ["| Cluster | " + " | ".join(cols) + " | Row total |",
             "|---" * (len(cols) + 2) + "|"]
    for k, row in zip(primary["region_crosstab_index"], vals):
        lines.append(f"| {k} | " + " | ".join(str(v) for v in row)
                     + f" | {sum(row)} |")
    ct = "\n".join(lines)

    if a_reg > a_sent:
        verdict = (
            f"**ARI(cluster, region) = {a_reg:.4f} EXCEEDS ARI(cluster, "
            f"Sentiment) = {a_sent:.4f}.** The clustering agrees more with which "
            "half of the source file a review came from than with what the "
            "review says. Any persona reading of these clusters is unsupported "
            "until the corpus is restricted to one region: the structure being "
            "recovered is provenance."
        )
    else:
        verdict = (
            f"**ARI(cluster, region) = {a_reg:.4f} does NOT exceed "
            f"ARI(cluster, Sentiment) = {a_sent:.4f}.** The two-corpus split is "
            "not the dominant axis the encoder recovered. That does not clear "
            "the corpus -- the split is still a confound to disclose -- but it "
            "removes the strongest version of the objection."
        )

    return f"""### Cluster × region — is this sentiment, or file of origin?

`results/s2c_region_split.md` established that the source `.xlsx` is two corpora
joined at raw row 1999, with sharply different register on either side. If the
encoder is separating those two corpora rather than anything about audiences,
this table is where it shows.

{ct}

| Scored against | ARI |
|---|---|
| `Sentiment` | {a_sent:.4f} |
| **`region`** | **{a_reg:.4f}** |
| `Sentiment`, before dedup | {baseline["ari"]:.4f} |
| `region`, before dedup | {baseline.get("ari_region", float("nan")):.4f} |

{verdict}
"""


def degeneracy_md(res) -> str:
    shares = ", ".join(
        f"cluster {k}: {v * 100:.1f}%" for k, v in res["cluster_shares"].items()
    )
    if not res["degenerate"]:
        return (
            f"**Not degenerate.** Cluster shares ({shares}) are all within the "
            "5%–70% band, so the K-Means solution is interpretable and the ARI "
            "below is meaningful."
        )
    return (
        f"**DEGENERATE — cluster(s) {res['degenerate_clusters']} fall outside "
        f"the 5%–70% band** ({shares}). K-Means has not found three usable "
        "groups: at least one cluster is near-empty or absorbs most of the "
        "data. **The ARI below is not interpretable as evidence about personas** "
        "— a degenerate partition can score a low ARI simply by failing to "
        "partition, which must not be read as 'personas are independent of "
        "sentiment'. Resolve the degeneracy before using this trap-check."
    )


def build_report(
    cfg, cfg_path, prov, n_in, sweep, primary, pairs_path, dist, baseline
) -> str:
    pt = cfg["near_duplicate"]["primary_threshold"]
    bands = cfg["trap_check"]["bands"]
    v = verdict(primary, bands)
    flag, text = v["verdict"], v["text"]

    markers_md = f" · **{' + '.join(v['markers'])}**" if v["markers"] else ""
    ari_caveat = (
        " — **uninterpretable: partition is degenerate**" if v["band"] == 0 else ""
    )

    def _cell(res):
        vv = verdict(res, bands)
        marks = f" + {' + '.join(vv['markers'])}" if vv["markers"] else ""
        return f"Band {vv['band']} · {vv['verdict']}{marks}"

    sweep_rows = "\n".join(
        f"| {r['threshold']:.2f}{' **(primary)**' if r['threshold'] == pt else ''} "
        f"| {r['n_pairs']} | {r['n_removed']} | {r['n_surviving']} | "
        f"{r['ari']:.4f} | {r['ari'] - baseline['ari']:+.4f} | "
        f"{r['cramers_v']:.4f} | "
        f"{'**YES**' if r['degenerate'] else 'no'} | "
        f"{_cell(r)} |"
        for r in sweep
    )
    baseline_row = (
        f"| — (no dedup) | — | 0 | {baseline['n_surviving']} | "
        f"{baseline['ari']:.4f} | — | {baseline['cramers_v']:.4f} | "
        f"{'**YES**' if baseline['degenerate'] else 'no'} | "
        f"{_cell(baseline)} |"
    )
    sizes = " / ".join(f"{k}:{v}" for k, v in primary["cluster_sizes"].items())

    return f"""# S2 Pilot — near-duplicate removal and the ARI trap-check

**Pilot, not a frozen result. This step writes no split map.**
`data/splits/split_map_v1.json` is created in a later step, deliberately after
this outcome is on record so the split cannot be tuned to it.

- **Config:** `{cfg_path}`
- **Input:** `{cfg['input_csv']}` ({n_in} rows, `n_after_rule_based_cleaning`)
- **Embeddings:** `{cfg['embedding']['model']}`, L2-normalized, max_seq_length
  {cfg['embedding']['max_seq_length']}
- **Clustering:** K-Means K={cfg['clustering']['k']},
  n_init={cfg['clustering']['n_init']},
  random_state={cfg['clustering']['random_state']}, in LaBSE space (rule 9: UMAP
  is visualization-only and is not used here)
- **Seed:** {cfg['seed']}
- **Generated (UTC):** {prov['timestamp_utc']}
- **Git commit:** `{prov['git_commit']}`

## Trap-check result at the primary threshold ({pt})

| Quantity | Value |
|---|---|
| near-duplicate pairs at ≥ {pt} | {primary['n_pairs']} |
| rows removed as near-duplicates | {primary['n_removed']} |
| **surviving n** | **{primary['n_surviving']}** |
| cluster sizes | {sizes} |
| **ARI(cluster, Sentiment)** | **{primary['ari']:.4f}**{ari_caveat} |
| chi2 (df {primary['chi2_dof']}) | {primary['chi2']:.2f} (p = {primary['chi2_p']:.3g}) |
| Cramér's V | {primary['cramers_v']:.4f} |
| **Pre-registered band** | **Band {v['band']}** (protocol.md RQ1) |
| **Verdict** | **{flag}**{markers_md} |

{text}

{region_md(primary, baseline)}

### Cluster degeneracy check

{degeneracy_md(primary)}

### Cluster × Sentiment crosstab (primary threshold)

{crosstab_md(primary)}

χ² = {primary['chi2']:.2f} on {primary['chi2_dof']} df, p = {primary['chi2_p']:.3g};
**Cramér's V = {primary['cramers_v']:.4f}**.

Read these two together with ARI, not instead of it. χ² only tests whether the
clusters are *associated* with sentiment at all — at n ≈ {primary['n']} it will
reach significance on associations far too weak to matter, so its p-value is
close to useless here. Cramér's V gives the association's strength on a 0–1
scale, and ARI gives agreement corrected for chance. A high V with a low ARI
means the clusters lean on sentiment without reproducing its partition — that
combination is a caveat, not a pass.

## Does near-duplicate removal itself move the trap-check?

Near-duplicates create tight artificial groups that K-Means can latch onto, so
the trap-check is reported both before and after removal. If ARI shifts
materially, the dedup threshold is doing real work on the headline number and
must be reported as such rather than treated as housekeeping.

| Stage | n | ARI | Cramér's V | Degenerate? |
|---|---|---|---|---|
| **Before dedup** (all rows) | {baseline['n_surviving']} | {baseline['ari']:.4f} | {baseline['cramers_v']:.4f} | {'YES ' + str(baseline['degenerate_clusters']) if baseline['degenerate'] else 'no'} |
| **After dedup** (t = {pt}) | {primary['n_surviving']} | {primary['ari']:.4f} | {primary['cramers_v']:.4f} | {'YES ' + str(primary['degenerate_clusters']) if primary['degenerate'] else 'no'} |
| **Δ (after − before)** | {primary['n_surviving'] - baseline['n_surviving']:+d} | {primary['ari'] - baseline['ari']:+.4f} | {primary['cramers_v'] - baseline['cramers_v']:+.4f} | — |

## Off-diagonal cosine distribution

All {dist['n_offdiagonal_pairs']:,} distinct pairs (strict upper triangle),
accumulated as a histogram during the same blocked matmul — the full n × n
matrix is never materialised. Percentiles are estimated from that histogram
(bin width {dist['bin_width']:.0e}, interpolated within the containing bin), so
they carry a resolution limit of roughly one bin width in the dense middle of
the distribution; in the sparse upper tail the limit is instead the gap between
neighbouring pair values, which can exceed a bin width. The **maximum is exact**
— it is tracked directly, not read off the histogram — and the threshold sweep
below uses exact cosines throughout, so no removal decision depends on these
estimates.

| Statistic | Cosine |
|---|---|
| 50th percentile (median) | {dist['percentiles'][50]:.4f} |
| 90th percentile | {dist['percentiles'][90]:.4f} |
| 95th percentile | {dist['percentiles'][95]:.4f} |
| 99th percentile | {dist['percentiles'][99]:.4f} |
| 99.9th percentile | {dist['percentiles'][99.9]:.4f} |
| **maximum** | **{dist['max']:.6f}** |

This is the context the thresholds are chosen against. If the 99.9th percentile
already sits above a swept threshold, that threshold is cutting into the bulk of
the distribution rather than trimming a duplicate tail — it is then removing
merely *similar* short reviews, not duplicates, and the choice needs defending.
With a median of 8 words, high baseline cosine between unrelated reviews is
expected, so this table must be checked before the primary threshold is trusted.

## Sensitivity to the near-duplicate threshold

The threshold is a judgement call, so it is reported as a curve rather than a
single number. If the verdict column is not constant across these rows, the
trap-check conclusion depends on an arbitrary choice and must be reported that
way.

| Threshold | Pairs ≥ t | Rows removed | Surviving n | ARI | ΔARI vs no-dedup | Cramér's V | Degenerate | Verdict |
|---|---|---|---|---|---|---|---|---|
{baseline_row}
{sweep_rows}

## Method notes

- **Pair enumeration** — full pairwise cosine over L2-normalized embeddings
  (cosine = dot product), strict upper triangle only, computed in row blocks to
  bound memory. No approximate neighbour search, so no recall loss.
- **Which row survives** — rows are sorted by `review_id` and a row `j` is
  removed only when it is ≥ threshold to an already-**kept** row `i < j`. The
  lowest `review_id` in a near-duplicate cluster therefore always survives
  (`keep: {cfg['near_duplicate']['keep']}`). Comparing against kept rows only
  stops a removed row from evicting a third row, which would delete more than
  intended in transitive chains.
- **Every pair is logged** — `{pairs_path}` lists all pairs at or above the
  lowest swept threshold, with the cosine, which thresholds each pair is above,
  whether the higher-id row was removed at the primary threshold, and both
  review texts so the removals can be eyeballed.
- **ARI is computed on survivors** at each threshold, against the `Sentiment`
  column of the surviving rows.
- Class balance after S1 is **not** uniform (1513/1599/1618); see
  `docs/dataset_card.md`. ARI is chance-corrected, so this does not bias it.
"""


def main() -> int:
    set_seed()

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2_pilot.yaml")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((repo_root / cfg_path).read_text(encoding="utf-8"))

    df = load_clean(cfg, repo_root)

    # Region is computed BEFORE any optional restriction, so `restrict_to_region`
    # and the region scoring share one definition of the boundary.
    rcfg = cfg.get("region", {}) or {}
    boundary = int(rcfg.get("boundary_row", 1999))
    df["_region"] = region_of(df[cfg["id_col"]].to_numpy(), boundary)

    restrict = rcfg.get("restrict_to")
    if restrict:
        before = len(df)
        df = df[df["_region"] == restrict].reset_index(drop=True)
        print(f"restricted to region {restrict}: {before} -> {len(df)} rows")
        if df.empty:
            raise AssertionError(f"region {restrict!r} selected no rows")
        # The embedding cache is keyed to the FULL corpus by row count, so a
        # restricted run must not read or write it -- otherwise the next full
        # run silently loads embeddings for a subset.
        cfg = {**cfg, "embedding": {**cfg["embedding"], "cache_npy": None}}

    ids = df[cfg["id_col"]].to_numpy()
    texts = df[cfg["text_col"]].astype(str).tolist()
    labels_all = df[cfg["label_col"]].to_numpy()
    regions_all = df["_region"].to_numpy()
    score_region = bool(rcfg.get("score_against_region", True)) and (
        len(set(regions_all)) > 1
    )

    emb = embed(texts, cfg, repo_root)
    if emb.shape[0] != len(df):
        raise AssertionError("embedding count != row count")

    nd = cfg["near_duplicate"]
    thresholds = sorted(float(t) for t in nd["sweep_thresholds"])
    primary_t = float(nd["primary_threshold"])
    if primary_t not in thresholds:
        thresholds = sorted(thresholds + [primary_t])

    pairs, dist = all_near_dup_pairs(emb, min(thresholds))
    print(f"{len(pairs)} pairs at cosine >= {min(thresholds)}")

    # Baseline: the trap-check BEFORE any near-duplicate removal. Reported next
    # to the post-dedup numbers so it is visible whether dedup itself moves ARI
    # -- near-duplicates inflate apparent cluster structure.
    baseline = cluster_and_ari(
        emb, labels_all, cfg, regions_all if score_region else None
    )
    baseline["threshold"] = None
    baseline["n_removed"] = 0
    baseline["n_surviving"] = len(df)
    baseline["n_pairs"] = None
    print(f"baseline (no dedup)  n={len(df)}  ARI={baseline['ari']:.4f}")

    sweep, primary, primary_removed = [], None, None
    for t in thresholds:
        kept, removed = greedy_keep_first(len(df), pairs, t)
        res = cluster_and_ari(
            emb[kept], labels_all[kept], cfg,
            regions_all[kept] if score_region else None,
        )
        res["kept_idx"] = kept.tolist()
        row = {
            "threshold": t,
            "n_pairs": int((pairs["cosine"] >= t).sum()),
            "n_removed": len(removed),
            "n_surviving": len(kept),
            **res,
        }
        sweep.append(row)
        extra = (
            f"  ARI_region={res['ari_region']:.4f}" if "ari_region" in res else ""
        )
        print(
            f"t={t:.2f}  removed={len(removed):<5} surviving={len(kept):<5} "
            f"ARI={res['ari']:.4f}{extra}"
        )
        if t == primary_t:
            primary, primary_removed = row, removed

    # --- cluster_assignments.csv -------------------------------------------
    # Persisted because the first run was not: every follow-up question about
    # the clustering then had to be reconstructed from the printed crosstab, or
    # answered by re-embedding the whole corpus. One column per review is a
    # trivial file and it makes the result interrogable instead of final.
    assign_key = cfg["outputs"].get("cluster_assignments_csv")
    if assign_key:
        kept_idx = np.array(primary["kept_idx"], dtype=int)
        out_assign = repo_root / assign_key
        out_assign.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({
            cfg["id_col"]: ids[kept_idx],
            "cluster": primary["assign"],
            cfg["label_col"]: labels_all[kept_idx],
            "region": regions_all[kept_idx],
            "threshold": primary_t,
        }).to_csv(out_assign, index=False, encoding="utf-8",
                  lineterminator=NEWLINE)
        print(f"wrote {out_assign} ({len(kept_idx)} rows)")

    # --- near_dup_pairs.csv: every pair, fully auditable -------------------
    out_pairs = repo_root / cfg["outputs"]["near_dup_pairs_csv"]
    out_pairs.parent.mkdir(parents=True, exist_ok=True)
    if len(pairs):
        log = pd.DataFrame(
            {
                "id_kept_side": ids[pairs["i"].to_numpy()],
                "id_other_side": ids[pairs["j"].to_numpy()],
                "cosine": pairs["cosine"].round(6),
                "above_thresholds": [
                    ";".join(f"{t:.2f}" for t in thresholds if c >= t)
                    for c in pairs["cosine"]
                ],
                "removed_at_primary": [
                    primary_removed.get(j, (None, None))[0] == i
                    for i, j in zip(pairs["i"], pairs["j"])
                ],
                "text_kept_side": [texts[i] for i in pairs["i"]],
                "text_other_side": [texts[j] for j in pairs["j"]],
            }
        ).sort_values("cosine", ascending=False)
    else:
        log = pd.DataFrame(
            columns=[
                "id_kept_side", "id_other_side", "cosine", "above_thresholds",
                "removed_at_primary", "text_kept_side", "text_other_side",
            ]
        )
    log.to_csv(out_pairs, index=False, encoding="utf-8", lineterminator=NEWLINE)

    out_md = write_text_lf(
        repo_root / cfg["outputs"]["report_md"],
        build_report(
            cfg, cfg_path.as_posix(), stamp(cfg_path.as_posix()), len(df),
            sweep, primary, cfg["outputs"]["near_dup_pairs_csv"],
            dist, baseline,
        ),
    )

    print(f"wrote {out_pairs} ({len(log)} pairs)")
    print(f"wrote {out_md}")
    print("NOTE: no split map was written. The split is NOT frozen by this step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
