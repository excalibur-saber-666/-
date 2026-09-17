"""Refresh machine-generated semantic mappings without touching manual prose.

Only rows explicitly marked complete or partial are eligible. Pending rows are
never interpreted, and terms are copied from semantic_index.csv rather than
inferred from filenames or paper text.
"""

from __future__ import annotations

import csv
import os
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_INDEX = ROOT / "metadata" / "semantic_index.csv"
NOTES = ROOT / "paper_notes"
START = "<!-- AUTO-GENERATED START -->"
END = "<!-- AUTO-GENERATED END -->"
TARGETS = {
    "problem_types": ROOT / "strategy" / "PROBLEM_PATTERN_INDEX.md",
    "algorithms": ROOT / "strategy" / "METHOD_INDEX.md",
    "knowledge_points": ROOT / "strategy" / "KNOWLEDGE_INDEX.md",
}
ALLOWED_STATUS = {"complete", "partial"}


def split_terms(value: str) -> list[str]:
    return [term.strip() for term in re.split(r"[;,；，|\n]+", value) if term.strip()]


def relative_link(from_dir: Path, target: Path) -> str:
    relative = Path(os.path.relpath(target, from_dir)).as_posix()
    return quote(relative, safe="/.-_")


def load_rows() -> list[dict[str, str]]:
    with SEMANTIC_INDEX.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        paper_id = row.get("paper_id", "")
        year = row.get("year", "")
        question = row.get("question", "")
        card = NOTES / year / question / f"{paper_id}.md"
        if not card.exists():
            raise FileNotFoundError(f"missing paper note: {card.relative_to(ROOT)}")
        card.read_text(encoding="utf-8")
    return rows


def generated_block(field: str, rows: list[dict[str, str]], target: Path) -> str:
    mapping: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("semantic_status", "") not in ALLOWED_STATUS:
            continue
        for term in split_terms(row.get(field, "")):
            mapping[term].append(row)

    lines = [START, "## 已审核经验卡映射", ""]
    if not mapping:
        lines.append("当前没有由经验卡标记为 complete/partial 且可自动汇总的语义条目。自动脚本不会从 pending 条目推断内容。")
    else:
        lines.append("> 下列映射直接来自 semantic_index.csv 中 complete/partial 条目；使用时仍应回看经验卡与 source_md。")
        lines.append("")
        for term in sorted(mapping):
            lines.extend([f"### {term}", ""])
            for row in sorted(mapping[term], key=lambda item: item["paper_id"]):
                card = NOTES / row["year"] / row["question"] / f"{row['paper_id']}.md"
                source = ROOT / row["source_md"]
                card_link = relative_link(target.parent, card)
                source_link = relative_link(target.parent, source)
                lines.append(
                    f"- {row['paper_id']}（{row['semantic_status']}）："
                    f"[经验卡]({card_link}) · [source_md]({source_link})"
                )
            lines.append("")
    lines.append(END)
    return "\n".join(lines)


def replace_generated_region(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)} must contain exactly one auto-generated region")
    updated = pattern.sub(block, text)
    path.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    rows = load_rows()
    reviewed = sum(row.get("semantic_status", "") in ALLOWED_STATUS for row in rows)
    for field, target in TARGETS.items():
        replace_generated_region(target, generated_block(field, rows, target))
    print(f"semantic_rows={len(rows)} reviewed_rows={reviewed} indexes_updated={len(TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
