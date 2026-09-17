"""Organize the paper corpus and maintain its Markdown knowledge base.

Run from the repository root on Windows:
  D:\\CodexTools\\MarkItDown\\.venv\\Scripts\\python.exe scripts\\organize_and_update.py --organize --reuse-legacy --cleanup-legacy
  D:\\CodexTools\\MarkItDown\\.venv\\Scripts\\python.exe scripts\\organize_and_update.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import quote, unquote

from markitdown import MarkItDown


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
KNOWLEDGE = ROOT / "knowledge_base"
METADATA = ROOT / "metadata"
REPORTS = ROOT / "reports"
MANIFEST = METADATA / "papers_manifest.csv"
LEGACY = ROOT / "markdown"
EXCLUDED = {".git", ".markitdown-tests", "papers", "knowledge_base", "metadata", "reports", "scripts", "markdown", "tmp"}
QUESTION_TITLES = {
    "2022": {
        "A": "移动场景超分辨定位问题", "B": "方形件组批优化问题",
        "C": "汽车制造公司涂装-总装缓存区调序调度优化问题", "D": "PISA 架构芯片资源排布问题",
        "E": "草原放牧策略研究", "F": "COVID-19 疫情期间生活物资的科学管理问题",
    },
    "2023": {
        "A": "WLAN 网络信道接入机制建模", "B": "DFT 类矩阵的整数分解逼近",
        "C": "大规模创新类竞赛评审方案研究", "D": "区域双碳目标与路径规划研究",
        "E": "出血性脑卒中临床智能诊疗建模", "F": "强对流降水临近预报",
    },
    "2024": {
        "A": "风电场有功功率优化分配", "B": "WLAN 组网中网络吞吐量建模",
        "C": "数据驱动下磁性元件的磁芯损耗建模", "D": "大数据驱动的地理综合问题",
        "E": "高速公路应急车道紧急启用模型", "F": "X 射线脉冲星光子到达时间建模",
    },
    # 2025 themes are taken only from the repeated source-file descriptions.
    "2025": {
        "A": "通用神经网络处理器下的核内调度问题", "B": "MIMO-OFDM 链路速率预测问题",
        "C": "围岩裂隙精准识别与三维模型重构", "D": "低空湍流监测及最优航路规划",
        "E": "高速列车轴承智能故障诊断问题", "F": "江南古典园林的美学特征建模",
    },
}
FIELDS = [
    "id", "year", "question", "title", "source_filename", "source_pdf", "markdown_file",
    "file_size", "sha256", "conversion_status", "conversion_tool", "notes", "original_path",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def info_from_path(path: Path) -> tuple[str, str]:
    match = re.search(r"20(22|23|24|25)", path.as_posix())
    if not match:
        raise ValueError(f"Cannot determine year: {path}")
    year = match.group(0)
    match = re.match(r"([A-F])(?:题)?(?=[0-9\-_]|$)", path.stem)
    if not match:
        raise ValueError(f"Cannot determine question from filename: {path.name}")
    return year, match.group(1)


def scan_unorganized_pdfs() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.pdf")
        if not any(part in EXCLUDED for part in path.relative_to(ROOT).parts)
    )


def load_manifest() -> dict[str, dict[str, str]]:
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["source_pdf"]: row for row in csv.DictReader(handle)}


def stable_ids(pdf_paths: list[Path]) -> dict[Path, str]:
    assigned: dict[Path, str] = {}
    by_year_question: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for path in pdf_paths:
        year, question = info_from_path(path)
        by_year_question[(year, question)].append(path)
    for (year, question), members in by_year_question.items():
        for ordinal, path in enumerate(sorted(members, key=lambda item: item.name), start=1):
            assigned[path] = path.stem if year != "2025" else f"{year}-{question}-{ordinal:03d}"
    return assigned


def clean_legacy_body(text: str) -> str:
    marker = "\n---\n\n"
    if text.startswith("---\n"):
        # Remove this script's YAML front matter before considering its body.
        closing = text.find("\n---\n", 4)
        text = text[closing + len("\n---\n"):] if closing >= 0 else text
    elif marker in text:
        # One-time migration from the earlier temporary Markdown layout.
        text = text.split(marker, 1)[1]
    # Earlier versions of this script could re-wrap their own notice on every
    # incremental run. Strip only that generated prefix, never paper content.
    generated_notice = re.compile(
        r"\A\s*(?:> 原始文件：\[PDF\]\([^\n]*\)\s*\n)?"
        r"> 自动转换：Microsoft MarkItDown 0\.1\.7。公式、图形、流程图、复杂表格和页码须以原始 PDF 为准。\s*\n?",
    )
    while True:
        cleaned = generated_notice.sub("", text, count=1)
        if cleaned == text:
            break
        text = cleaned
    return text.strip()


def markdown_header(record: dict[str, str]) -> str:
    values = {key: json.dumps(record[key], ensure_ascii=False) for key in ("id", "title", "source_pdf", "source_filename", "conversion_status")}
    return (
        "---\n"
        f"id: {values['id']}\n"
        f"year: {record['year']}\n"
        f"question: {record['question']}\n"
        f"title: {values['title']}\n"
        f"source_pdf: {values['source_pdf']}\n"
        f"source_filename: {values['source_filename']}\n"
        f"conversion_status: {values['conversion_status']}\n"
        "---\n\n"
        f"> 原始文件：[PDF]({url(record['source_pdf'])})\n"
        "> 自动转换：Microsoft MarkItDown 0.1.7。公式、图形、流程图、复杂表格和页码须以原始 PDF 为准。\n\n"
    )


def assess(body: str, pdf_size: int) -> tuple[str, str]:
    compact = re.sub(r"\s+", "", body)
    chinese = len(re.findall(r"[\u4e00-\u9fff]", body))
    if not compact:
        return "failed", "Markdown 为空"
    if len(compact) < 600:
        return "warning", "提取文本少于 600 个非空白字符"
    if pdf_size > 200_000 and len(compact) < 1_500:
        return "warning", "PDF 大于 200 KB 但提取文本少于 1,500 个非空白字符"
    if chinese == 0:
        return "warning", "未检测到中文字符，需人工确认"
    return "success", ""


def organize() -> tuple[list[tuple[Path, Path]], list[str]]:
    original = scan_unorganized_pdfs()
    if not original:
        return [], []
    ids = stable_ids(original)
    moves: list[tuple[Path, Path]] = []
    issues: list[str] = []
    seen: set[Path] = set()
    for source in original:
        year, question = info_from_path(source)
        destination = PAPERS / year / question / source.name
        if destination in seen:
            raise RuntimeError(f"Destination collision: {destination}")
        seen.add(destination)
        if destination.exists():
            if sha256(source) != sha256(destination):
                raise RuntimeError(f"Destination exists with different content: {destination}")
            source.unlink()
            issues.append(f"Removed duplicate source after hash match: {rel(source)}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
        moves.append((source, destination))
    for path in sorted({source.parent for source, _ in moves}, key=lambda item: len(item.parts), reverse=True):
        while path != ROOT:
            try:
                path.rmdir()
            except OSError:
                break
            path = path.parent
    return moves, issues


def source_pdfs() -> list[Path]:
    return sorted(PAPERS.rglob("*.pdf"))


def question_id(year: str, question: str, position: int) -> str:
    return f"{year}-{question}-{position:03d}"


def update(args: argparse.Namespace, original_lookup: dict[Path, Path]) -> tuple[list[dict[str, str]], Counter[str]]:
    existing = load_manifest()
    pdfs = source_pdfs()
    if not pdfs:
        raise RuntimeError("No PDFs found under papers/")
    grouped: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for pdf in pdfs:
        parts = pdf.relative_to(PAPERS).parts
        if len(parts) != 3 or not re.fullmatch(r"20\d{2}", parts[0]) or parts[1] not in "ABCDEF":
            raise RuntimeError(f"Unexpected PDF path: {rel(pdf)}")
        grouped[(parts[0], parts[1])].append(pdf)

    converter: MarkItDown | None = None
    records: list[dict[str, str]] = []
    counters: Counter[str] = Counter()
    for (year, question) in sorted(grouped):
        for position, pdf in enumerate(sorted(grouped[(year, question)], key=lambda item: item.name), start=1):
            source_pdf = rel(pdf)
            output = KNOWLEDGE / year / question / pdf.with_suffix(".md").name
            markdown_file = rel(output)
            digest = sha256(pdf)
            old = existing.get(source_pdf, {})
            if year == "2025" and old.get("id"):
                item_id = old["id"]
            elif year == "2025":
                used = [
                    int(row["id"].rsplit("-", 1)[1])
                    for row in existing.values()
                    if row.get("year") == year and row.get("question") == question and re.fullmatch(r"2025-[A-F]-\d{3}", row.get("id", ""))
                ]
                item_id = question_id(year, question, max(used, default=0) + 1)
            else:
                item_id = pdf.stem
            record = {
                "id": item_id, "year": year, "question": question, "title": "",
                "source_filename": pdf.name, "source_pdf": source_pdf, "markdown_file": markdown_file,
                "file_size": str(pdf.stat().st_size), "sha256": digest, "conversion_status": "",
                "conversion_tool": "Microsoft MarkItDown 0.1.7", "notes": "", "original_path": "",
            }
            legacy_source = original_lookup.get(pdf)
            if legacy_source:
                record["original_path"] = legacy_source.as_posix()
            elif old:
                record["original_path"] = old.get("original_path", "")
            source_relative_from_md = Path("..") / ".." / ".." / Path(source_pdf)
            record["source_pdf"] = source_pdf
            header_record = dict(record)
            header_record["source_pdf"] = source_relative_from_md.as_posix()
            body = ""
            action = ""
            legacy_path = LEGACY / legacy_source.with_suffix(".md") if legacy_source else None
            if old and old.get("sha256") == digest and output.exists():
                body = clean_legacy_body(output.read_text(encoding="utf-8"))
                action = "skipped"
            elif args.reuse_legacy and legacy_path and legacy_path.exists():
                body = clean_legacy_body(legacy_path.read_text(encoding="utf-8"))
                action = "migrated"
            else:
                if converter is None:
                    converter = MarkItDown(enable_plugins=False)
                try:
                    body = converter.convert(pdf).markdown.strip()
                    action = "converted"
                except Exception as exc:
                    record["conversion_status"] = "failed"
                    record["notes"] = f"{type(exc).__name__}: {exc}"
                    records.append(record)
                    counters["failed"] += 1
                    continue
            body = "\n".join(line.rstrip() for line in body.splitlines()).strip()
            status, note = assess(body, int(record["file_size"]))
            record["conversion_status"] = status
            record["notes"] = note if action != "migrated" else (note + "; migrated from verified legacy MarkItDown output").strip("; ")
            header_record["conversion_status"] = status
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(markdown_header(header_record) + body + "\n", encoding="utf-8")
            records.append(record)
            counters[status] += 1
            counters[action] += 1
            print(f"{action:9} {status:7} {source_pdf}", flush=True)
    return records, counters


def url(path: str) -> str:
    return quote(path, safe="/.-_")


def write_manifest(records: list[dict[str, str]]) -> None:
    METADATA.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def write_indexes(records: list[dict[str, str]]) -> None:
    by_group: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for record in records:
        by_group[(record["year"], record["question"])].append(record)
    index = ["# 论文知识库索引", "", "按年份和题号浏览。Markdown 适合检索与阅读；公式、图表、复杂表格及精确页码请以 PDF 为准。", ""]
    years = sorted(set(QUESTION_TITLES) | {record["year"] for record in records})
    for year in years:
        index.extend([f"## {year}", ""])
        for question in "ABCDEF":
            index.append(f"### {question} 题：{QUESTION_TITLES.get(year, {}).get(question, '题目待补充')}")
            for record in sorted(by_group[(year, question)], key=lambda item: item["id"]):
                label = record["id"] + (f" — {record['title']}" if record["title"] else "")
                md_link = url(str(Path(year) / question / Path(record["markdown_file"]).name))
                pdf_link = url("../" + record["source_pdf"])
                index.append(f"- {label}（{record['conversion_status']}）：[Markdown]({md_link}) · [PDF]({pdf_link})")
            if not by_group[(year, question)]:
                index.append("- 暂无论文")
            index.append("")
    KNOWLEDGE.mkdir(parents=True, exist_ok=True)
    (KNOWLEDGE / "INDEX.md").write_text("\n".join(index), encoding="utf-8")

    catalog = ["# 历年赛题目录", ""]
    for year in years:
        catalog.extend([f"## {year}", ""])
        for question in "ABCDEF":
            suffix = "（根据 2025 源文件名归纳）" if year == "2025" else ""
            catalog.append(f"- {question}：{QUESTION_TITLES.get(year, {}).get(question, '题目待补充')}{suffix}")
        catalog.append("")
    (KNOWLEDGE / "QUESTION_CATALOG.md").write_text("\n".join(catalog), encoding="utf-8")
    (KNOWLEDGE / "README.md").write_text(
        "# 数学建模论文知识库\n\n入口：[论文索引](INDEX.md) · [历年赛题目录](QUESTION_CATALOG.md)。\n\n"
        "Markdown 由 Microsoft MarkItDown 自动生成，用于检索、摘要和对比；涉及公式、图表、复杂表格或页码时请回看 `papers/` 的原始 PDF。\n",
        encoding="utf-8",
    )

    counts = Counter(record["year"] for record in records)
    root = [
        "# 中国研究生数学建模竞赛优秀论文知识库", "",
        "本仓库保存 2022—2025 年优秀论文的原始 PDF 与可检索 Markdown，服务于数模比赛备赛时的快速检索、方法比较和论文结构参考。", "",
        "## 当前收录", "", "| 年份 | 论文数 |", "|---|---:|",
    ]
    root += [f"| {year} | {counts[year]} |" for year in sorted(counts)]
    root += [f"| 合计 | {len(records)} |", "", "## 目录说明", "", "- `papers/`：原始 PDF，唯一权威版本。", "- `knowledge_base/`：自动生成、可检索的 Markdown；入口为 [INDEX](knowledge_base/INDEX.md) 和 [QUESTION_CATALOG](knowledge_base/QUESTION_CATALOG.md)。", "- `metadata/papers_manifest.csv`：机器可读清单，包含路径、哈希和转换状态。", "- `scripts/organize_and_update.py`：可重复运行的整理、转换与索引更新脚本。", "- `reports/conversion_report.md`：本次转换与验证报告。", "", "## 第二阶段：方法论与写作经验库", "", "- `paper_notes/`：逐篇可追溯的经验卡；语义内容须在阅读原文后填写。", "- [`strategy/`](strategy/README.md)：建模方法论、题型、验证、解释、写作、比赛流程和证据案例。", "- `metadata/semantic_index.csv`：与论文 manifest 一一对应的语义索引。", "- `reports/semantic_summary_report.md`：第二阶段完成度与待确认项。", "- `reports/methodology_summary_review.md`：GPT 总结审阅、修订边界和抽查证据。", "", "## 新增或更新 PDF", "", "1. 将文件置于 `papers/{year}/{question}/`。", "2. 运行下方命令；未变化文件会跳过，新增或哈希变化文件会重新转换。", "", "```powershell", "& 'D:\\CodexTools\\MarkItDown\\.venv\\Scripts\\python.exe' .\\scripts\\organize_and_update.py", "```", "", "Markdown 是文本提取结果。公式、图形、流程图、复杂表格和精确页码请以 PDF 为准。", ""]
    root += ["## 初始化或补齐第二阶段经验卡", "", "```powershell", "& 'D:\\CodexTools\\MarkItDown\\.venv\\Scripts\\python.exe' .\\scripts\\initialize_semantic_stage.py", "```", ""]
    root_readme = ROOT / "README.md"
    if not root_readme.exists():
        root_readme.write_text("\n".join(root), encoding="utf-8")


def validate(records: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        errors.append("manifest contains duplicate IDs")
    for record in records:
        pdf = ROOT / record["source_pdf"]
        markdown = ROOT / record["markdown_file"]
        if not pdf.exists(): errors.append(f"missing PDF: {record['source_pdf']}")
        if record["conversion_status"] != "failed" and not markdown.exists(): errors.append(f"missing Markdown: {record['markdown_file']}")
        if pdf.exists() and sha256(pdf) != record["sha256"]: errors.append(f"SHA256 mismatch: {record['source_pdf']}")
    return errors


def check_links() -> list[str]:
    errors: list[str] = []
    documents = [ROOT / "README.md", KNOWLEDGE / "README.md", KNOWLEDGE / "INDEX.md", KNOWLEDGE / "QUESTION_CATALOG.md"]
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for document in documents:
        if not document.exists():
            errors.append(f"missing linked-document source: {rel(document)}")
            continue
        for target in pattern.findall(document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            local_target = unquote(target.split("#", 1)[0])
            if not (document.parent / local_target).resolve().exists():
                errors.append(f"broken link in {rel(document)}: {target}")
    pdf_pattern = re.compile(r"^> 原始文件：\[PDF\]\(([^)]+)\)", re.MULTILINE)
    for document in KNOWLEDGE.rglob("*.md"):
        if document.name in {"README.md", "INDEX.md", "QUESTION_CATALOG.md"}:
            continue
        match = pdf_pattern.search(document.read_text(encoding="utf-8"))
        if not match:
            errors.append(f"missing generated PDF link: {rel(document)}")
        elif not (document.parent / unquote(match.group(1))).resolve().exists():
            errors.append(f"broken generated PDF link in {rel(document)}: {match.group(1)}")
    return errors


def write_report(records: list[dict[str, str]], counters: Counter[str], moves: list[tuple[Path, Path]], issues: list[str], errors: list[str]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    counts = Counter(record["conversion_status"] for record in records)
    group_counts = Counter((record["year"], record["question"]) for record in records)
    migration_records = sum(bool(record["original_path"]) for record in records)
    warnings = [record for record in records if record["conversion_status"] in {"warning", "failed"}]
    lines = [
        "# PDF 转换与整理报告", "", f"- 生成日期：{date.today().isoformat()}", f"- 原始 PDF 总数：{len(records)}", f"- 成功：{counts['success']}", f"- warning：{counts['warning']}", f"- failed：{counts['failed']}", f"- skipped（本次未重新转换）：{counters['skipped']}", f"- Markdown 总数：{sum(1 for record in records if record['conversion_status'] != 'failed')}", f"- 已从原始路径迁移入标准目录的 PDF：{migration_records}", f"- 本次运行移动 PDF：{len(moves)}", f"- 本次运行复用既有 MarkItDown 输出：{counters['migrated']}", "", "## 年份与题号统计", "", "| 年份 | A | B | C | D | E | F | 合计 |", "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for year in sorted(set(QUESTION_TITLES) | {record["year"] for record in records}):
        values = [group_counts[(year, question)] for question in "ABCDEF"]
        lines.append(f"| {year} | " + " | ".join(map(str, values)) + f" | {sum(values)} |")
    lines.extend(["", "## 异常项", ""])
    if warnings:
        for record in warnings:
            lines.append(f"- `{record['source_pdf']}` — {record['conversion_status']}: {record['notes']}")
    else:
        lines.append("- 无。")
    lines.extend(["", "## 验证", "", "- 已检查 manifest ID 唯一性、PDF/Markdown 路径存在性、所有 PDF SHA256 及 Markdown 相对链接。"])
    if errors:
        lines += ["- 失败："] + [f"  - {error}" for error in errors]
    else:
        lines.append("- 全部通过。")
    if issues:
        lines.extend(["", "## 整理备注", ""] + [f"- {issue}" for issue in issues])
    (REPORTS / "conversion_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--organize", action="store_true", help="Move legacy source PDFs into papers/{year}/{question}/")
    parser.add_argument("--reuse-legacy", action="store_true", help="Reuse prior MarkItDown output under markdown/ during one-time migration")
    parser.add_argument("--cleanup-legacy", action="store_true", help="Remove legacy markdown/ only after successful migration")
    args = parser.parse_args()
    moves, issues = organize() if args.organize else ([], [])
    original_lookup = {destination: source.relative_to(ROOT) for source, destination in moves}
    records, counters = update(args, original_lookup)
    write_manifest(records)
    write_indexes(records)
    errors = validate(records) + check_links()
    write_report(records, counters, moves, issues, errors)
    if args.cleanup_legacy and args.reuse_legacy and not errors and len(records) == 145 and LEGACY.exists():
        shutil.rmtree(LEGACY)
        print("Removed verified legacy markdown/ directory", flush=True)
    print(json.dumps({"records": len(records), "status": Counter(record['conversion_status'] for record in records), "actions": counters, "validation_errors": errors}, ensure_ascii=True, default=dict))
    return 1 if errors or any(record["conversion_status"] == "failed" for record in records) else 0


if __name__ == "__main__":
    sys.exit(main())
