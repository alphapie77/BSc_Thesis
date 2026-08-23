"""Build the CC BY-SA attribution appendix from the frozen plot corpus."""

from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import quote

from src.common.seed import set_seed


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "plots" / "plots_bn.csv"
OUTPUT = ROOT / "docs" / "appendices" / "appendix_d_plot_attribution.md"


def escaped(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    set_seed()
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 120:
        raise ValueError(f"expected frozen 120 plots, found {len(rows)}")
    required = {"plot_id", "title_bn", "source_url", "revision_id",
                "revision_timestamp", "licence", "split"}
    if any(required - set(row) for row in rows):
        raise ValueError("plot attribution fields are incomplete")
    if any(not all(row[key].strip() for key in required) for row in rows):
        raise ValueError("plot attribution contains blank required values")
    if len({row["plot_id"] for row in rows}) != 120:
        raise ValueError("plot ids are not unique")

    lines = [
        "# Appendix D — Bangla Wikipedia plot attribution",
        "",
        "The 120 frozen plot synopses were extracted verbatim from Bangla",
        "Wikipedia and are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).",
        "Attribution is to the contributors of each linked article revision.",
        "The revision ID and timestamp identify the exact text used; any",
        "distributed derivative of this plot set must retain attribution and a",
        "compatible share-alike licence. Harvest date: 2026-07-31.",
        "",
        "| Plot ID | Split | Article | Exact revision | Revision timestamp |",
        "|---|---|---|---|---|",
    ]
    for row in sorted(rows, key=lambda item: item["plot_id"]):
        url = row["source_url"].strip()
        oldid = f"{url}?oldid={quote(row['revision_id'].strip())}"
        title = escaped(row["title_bn"])
        lines.append(
            f"| {escaped(row['plot_id'])} | {escaped(row['split'])} | "
            f"[{title}]({url}) | [{escaped(row['revision_id'])}]({oldid}) | "
            f"{escaped(row['revision_timestamp'])} |"
        )
    lines.extend([
        "",
        "Source metadata: `data/plots/plots_bn.csv`. This appendix attributes",
        "the plot corpus only; it does not change the standing or licence of the",
        "separate review corpus.",
        "",
    ])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(rows)} attributions")


if __name__ == "__main__":
    main()
