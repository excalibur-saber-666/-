"""Validate the V1 paper and semantic knowledge-base structure."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "metadata" / "papers_manifest.csv"
SEMANTIC = ROOT / "metadata" / "semantic_index.csv"
ALLOWED_STATUS = {"complete", "partial", "pending_chatgpt_review"}
ALLOWED_SOURCE = {"chatgpt_review", "structured_from_master_guide", "template_only"}
CORE_FIELDS = {
    "problem_types", "algorithms", "knowledge_points", "validation_methods",
    "writing_features", "reusable_ideas",
}
REQUIRED_STRATEGY = {
    "README.md", "MASTER_MODELING_GUIDE.md", "PROBLEM_METHOD_QUICK_REFERENCE.md",
    "ANNUAL_QUESTION_EVIDENCE_MATRIX.md", "MODELING_PLAYBOOK.md",
    "PROBLEM_PATTERN_INDEX.md", "METHOD_INDEX.md", "KNOWLEDGE_INDEX.md",
    "VALIDATION_GUIDE.md", "EXPLAINABILITY_GUIDE.md", "WRITING_GUIDE.md",
    "EVIDENCE_CASES.md", "COMPETITION_WORKFLOW.md",
}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def duplicate_values(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if value and count > 1)


def check_links(document: Path, errors: list[str]) -> None:
    text = document.read_text(encoding="utf-8")
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        local = unquote(target.split("#", 1)[0])
        if not local:
            continue
        if not (document.parent / local).resolve().exists():
            errors.append(f"broken link in {document.relative_to(ROOT).as_posix()}: {target}")


def main() -> int:
    errors: list[str] = []
    manifest = read_csv(MANIFEST)
    semantic = read_csv(SEMANTIC)

    manifest_ids = [row.get("id", "").strip() for row in manifest]
    semantic_ids = [row.get("paper_id", "").strip() for row in semantic]
    if any(not paper_id for paper_id in manifest_ids):
        errors.append("manifest contains empty id")
    if any(not paper_id for paper_id in semantic_ids):
        errors.append("semantic_index contains empty paper_id")
    for duplicate in duplicate_values(manifest_ids):
        errors.append(f"duplicate manifest id: {duplicate}")
    for duplicate in duplicate_values(semantic_ids):
        errors.append(f"duplicate semantic paper_id: {duplicate}")

    manifest_by_id = {row["id"]: row for row in manifest if row.get("id")}
    semantic_by_id = {row["paper_id"]: row for row in semantic if row.get("paper_id")}
    unknown = sorted(set(semantic_by_id) - set(manifest_by_id))
    missing = sorted(set(manifest_by_id) - set(semantic_by_id))
    if unknown:
        errors.append(f"semantic IDs missing from manifest: {', '.join(unknown)}")
    if missing:
        errors.append(f"manifest IDs missing from semantic index: {', '.join(missing)}")

    required_columns = {
        "paper_id", "year", "question", "source_md", "source_pdf",
        "semantic_status", "semantic_source", "last_reviewed",
    }
    actual_columns = set(semantic[0]) if semantic else set()
    missing_columns = sorted(required_columns - actual_columns)
    if missing_columns:
        errors.append(f"semantic_index missing columns: {', '.join(missing_columns)}")

    for row in semantic:
        paper_id = row.get("paper_id", "").strip() or "<empty>"
        status = row.get("semantic_status", "")
        source = row.get("semantic_source", "")
        if status not in ALLOWED_STATUS:
            errors.append(f"invalid semantic_status for {paper_id}: {status!r}")
        if source not in ALLOWED_SOURCE:
            errors.append(f"invalid semantic_source for {paper_id}: {source!r}")
        if status == "complete" and not any(row.get(field, "").strip() for field in CORE_FIELDS):
            errors.append(f"complete semantic row has no core semantics: {paper_id}")
        for field in ("source_md", "source_pdf"):
            value = row.get(field, "").strip()
            if not value:
                errors.append(f"{paper_id} has empty {field}")
            elif not (ROOT / value).exists():
                errors.append(f"{paper_id} missing {field}: {value}")
        year = row.get("year", "")
        question = row.get("question", "")
        card = ROOT / "paper_notes" / year / question / f"{row.get('paper_id', '')}.md"
        if not card.exists():
            errors.append(f"missing paper note: {card.relative_to(ROOT).as_posix()}")

    pdf_files = list((ROOT / "papers").rglob("*.pdf"))
    paper_markdown = {
        row.get("markdown_file", "") for row in manifest if row.get("markdown_file", "")
    }
    existing_paper_markdown = {path for path in paper_markdown if (ROOT / path).exists()}
    note_files = [
        path for path in (ROOT / "paper_notes").rglob("*.md")
        if path.name != "README.md"
    ]
    if len(manifest) != 145:
        errors.append(f"expected 145 manifest rows, found {len(manifest)}")
    if len(pdf_files) != 145:
        errors.append(f"expected 145 PDFs, found {len(pdf_files)}")
    if len(paper_markdown) != 145 or len(existing_paper_markdown) != 145:
        errors.append(
            f"expected 145 paper Markdown paths/files, found "
            f"{len(paper_markdown)}/{len(existing_paper_markdown)}"
        )
    if len(note_files) != 145:
        errors.append(f"expected 145 paper notes, found {len(note_files)}")

    year_counts = Counter(row.get("year", "") for row in manifest)
    expected_years = {"2022": 42, "2023": 58, "2024": 24, "2025": 21}
    if dict(year_counts) != expected_years:
        errors.append(f"unexpected year distribution: {dict(year_counts)}")

    strategy_files = {path.name for path in (ROOT / "strategy").glob("*.md")}
    for filename in sorted(REQUIRED_STRATEGY - strategy_files):
        errors.append(f"missing strategy file: strategy/{filename}")
    if not (ROOT / "question_notes" / "README.md").exists():
        errors.append("missing question_notes/README.md")

    link_documents = [ROOT / "paper_notes" / "README.md"]
    link_documents.extend((ROOT / "paper_notes").rglob("*.md"))
    link_documents.extend((ROOT / "strategy").glob("*.md"))
    link_documents.extend((ROOT / "question_notes").rglob("*.md"))
    for document in sorted(set(link_documents)):
        check_links(document, errors)

    markdown_files = [
        path for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
    ]
    for document in markdown_files:
        try:
            document.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append(f"not valid UTF-8: {document.relative_to(ROOT).as_posix()} ({exc})")

    status_counts = Counter(row.get("semantic_status", "") for row in semantic)
    print(
        " ".join([
            f"manifest={len(manifest)}", f"pdf={len(pdf_files)}",
            f"paper_markdown={len(existing_paper_markdown)}",
            f"paper_notes={len(note_files)}",
            f"complete={status_counts['complete']}",
            f"partial={status_counts['partial']}",
            f"pending={status_counts['pending_chatgpt_review']}",
            f"markdown_utf8={len(markdown_files)}",
            f"errors={len(errors)}",
        ])
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: V1 structure, IDs, paths, links, statuses, counts, and UTF-8 checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
