"""The R1/R2/G wall, expressed as code that refuses rather than as a comment.

Inviolable rules 4 and 6 say Gold-300 is eval-only and Verifier-B never enters
the loop. Both are currently enforced by everyone remembering them. This module
exists so that a Phase 3 script which reaches for the wrong partition raises an
exception instead of quietly training on it and producing a number nobody can
tell is contaminated.

The design choice worth stating: `load_training_rows` takes a **role**, not a
partition name. A caller cannot ask for "R2" -- it asks to train Verifier-B and
is given R2. That removes the class of mistake where a copy-pasted config trains
the in-loop verifier on the evaluation half, which is the single failure that
would invalidate RQ5 without leaving a trace in any result file.

Nothing here is clever, and that is deliberate: this file is an appendix
artifact a reviewer may read to check the wall is real.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

#: Verifier-A is the in-loop gate; Verifier-B scores S6 and never enters the
#: loop. The wall between them IS the Goodhart test (inviolable rule 6).
ROLE_PARTITION = {"A": "R1", "B": "R2"}

#: Never a training source, for any role, ever (inviolable rule 4).
FORBIDDEN_AS_TRAINING = {"G"}


class SplitContractError(RuntimeError):
    """Raised when a caller asks for data the split contract forbids it."""


@dataclass(frozen=True)
class LabelledRows:
    """Rows carrying a `cluster_k2` label, with their provenance attached."""

    role: str
    partition: str
    review_ids: tuple[str, ...]
    texts: tuple[str, ...]
    labels: tuple[int, ...]

    def __len__(self) -> int:
        return len(self.review_ids)

    @property
    def class_counts(self) -> dict[int, int]:
        return {c: self.labels.count(c) for c in sorted(set(self.labels))}


def _read_split_map(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_k2_labels(path: str | Path) -> dict[str, int]:
    """review_id -> cluster_k2, from the region-A assignments ONLY.

    `results/s2_cluster_assignments.csv` also exists and is the wrong file: its
    clusters are a corpus detector (93.3% accuracy at identifying which corpus a
    review came from). The region-A K=2 file is the one every Phase 3 label
    comes from, per the 2026-08-05 scope decision.
    """
    labels: dict[str, int] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            labels[row["review_id"]] = int(row["cluster_k2"])
    return labels


def _read_texts(path: str | Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            texts[row["review_id"]] = row["Movie Review"]
    return texts


def load_training_rows(
    role: str,
    *,
    split_map: str | Path,
    k2_assignments: str | Path,
    cleaned_csv: str | Path,
    hold_out_dev: bool = True,
) -> tuple[LabelledRows, LabelledRows | None]:
    """Return (train, dev) for a verifier role. `role` is "A" or "B".

    Only rows that carry a K=2 label are returned -- region B has no such label
    and is therefore absent by construction, not by filtering. `dev` is a subset
    of R1 by the split map's own contract, so it is held out of Verifier-A's
    training set and is `None` for Verifier-B.
    """
    role = role.upper()
    if role not in ROLE_PARTITION:
        raise SplitContractError(
            f"role must be one of {sorted(ROLE_PARTITION)}, got {role!r}. "
            "Partitions are not selectable directly -- ask for a role."
        )
    partition = ROLE_PARTITION[role]
    if partition in FORBIDDEN_AS_TRAINING:  # pragma: no cover - defensive
        raise SplitContractError(f"{partition} may never be training data.")

    smap = _read_split_map(split_map)
    labels = _read_k2_labels(k2_assignments)
    texts = _read_texts(cleaned_csv)

    ids = list(smap[partition])
    dev_ids = set(smap["dev"]) if hold_out_dev else set()
    gold_ids = set(smap["G"])

    # Belt and braces: G must not be reachable through any partition. If this
    # ever fires, the split map itself is broken and nothing downstream is safe.
    leaked = gold_ids & set(ids)
    if leaked:
        raise SplitContractError(
            f"{len(leaked)} Gold-300 ids appear inside {partition}. "
            "The split map is corrupt; stop and do not train."
        )

    def build(selected: list[str]) -> LabelledRows:
        kept = [i for i in selected if i in labels]
        return LabelledRows(
            role=role,
            partition=partition,
            review_ids=tuple(kept),
            texts=tuple(texts[i] for i in kept),
            labels=tuple(labels[i] for i in kept),
        )

    train = build([i for i in ids if i not in dev_ids])
    dev = build([i for i in ids if i in dev_ids]) if (hold_out_dev and role == "A") else None
    return train, dev


def load_gold_ids(split_map: str | Path) -> tuple[str, ...]:
    """The Gold-300 ids, exposed so a script can assert it did NOT touch them.

    Deliberately returns ids only -- no text, no labels. There is no legitimate
    Phase 3 use for G's contents, so this function cannot supply them.
    """
    return tuple(_read_split_map(split_map)["G"])
