"""Extract BibTeX entries cited by one or more Markdown chapters."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.common.seed import set_seed


ENTRY_START = re.compile(r"^@[A-Za-z]+\{([^,]+),", re.MULTILINE)
CITATION = re.compile(r"@([A-Za-z0-9_:-]+)")


def parse_entries(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for match in ENTRY_START.finditer(text):
        depth = 0
        end = None
        for index in range(match.start(), len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
        if end is None:
            raise ValueError(f"Unclosed BibTeX entry: {match.group(1)}")
        entries[match.group(1)] = text[match.start() : end].strip()
    return entries


def main() -> None:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=Path, action="append", required=True)
    parser.add_argument("--source-bib", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cited: list[str] = []
    for chapter_path in args.chapter:
        chapter = chapter_path.read_text(encoding="utf-8")
        for key in CITATION.findall(chapter):
            if key not in cited:
                cited.append(key)
    entries = parse_entries(args.source_bib.read_text(encoding="utf-8"))
    missing = [key for key in cited if key not in entries]
    if missing:
        raise KeyError(f"Missing BibTeX entries: {', '.join(missing)}")

    header = (
        "% References cited by completed chapters.\n"
        "% Generated without changing keys or metadata from "
        "docs/references_ieee.bib.\n\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        header + "\n\n".join(entries[key] for key in cited) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(cited)} cited entries to {args.output}")


if __name__ == "__main__":
    main()
