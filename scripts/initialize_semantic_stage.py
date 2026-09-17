"""Create the non-semantic scaffolding for stage 2 of the paper knowledge base.

This script intentionally does not infer methods from filenames or bulk-generate
semantic claims. It preserves completed human/ChatGPT review cards and creates
only missing cards, indexes, and a machine-readable pending-review queue.
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "metadata" / "papers_manifest.csv"
NOTES = ROOT / "paper_notes"
STRATEGY = ROOT / "strategy"
SEMANTIC_INDEX = ROOT / "metadata" / "semantic_index.csv"
REPORT = ROOT / "reports" / "semantic_summary_report.md"
SEMANTIC_FIELDS = [
    "year", "question", "paper_id", "title", "problem_types", "overall_pipeline",
    "q1_task", "q1_methods", "q2_task", "q2_methods", "q3_task", "q3_methods",
    "q4_task", "q4_methods", "algorithms", "knowledge_points", "validation_methods",
    "writing_features", "reusable_ideas", "applicable_patterns", "source_md", "source_pdf",
    "review_status", "review_notes",
]
PATTERNS = [
    "预测", "分类", "回归", "聚类", "综合评价", "优化决策", "调度", "路径规划",
    "多目标优化", "机理建模", "故障诊断", "信号处理", "图像识别", "时间序列",
    "空间分析", "多源数据融合", "参数估计", "异常检测", "鲁棒优化", "敏感性分析", "不确定性分析",
]
KNOWLEDGE = [
    "概率统计", "回归分析", "假设检验", "时间序列", "图论", "运筹学", "最优化", "微分方程",
    "动力学", "控制理论", "信号处理", "机器学习", "深度学习", "迁移学习", "空间统计", "GIS",
    "多源融合", "不确定性分析", "鲁棒优化", "多目标优化", "评价体系",
]


def relative_link(from_dir: Path, target: str) -> str:
    return quote(Path(os.path.relpath(ROOT / target, from_dir)).as_posix(), safe="/.-_")


def load_manifest() -> list[dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_existing_index() -> dict[str, dict[str, str]]:
    if not SEMANTIC_INDEX.exists():
        return {}
    with SEMANTIC_INDEX.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["paper_id"]: row for row in csv.DictReader(handle)}


def write_utf8(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def note_template(row: dict[str, str]) -> str:
    note_dir = NOTES / row["year"] / row["question"]
    md_link = relative_link(note_dir, row["markdown_file"])
    pdf_link = relative_link(note_dir, row["source_pdf"])
    return f'''# 论文经验卡：{row["id"]}

> 语义整理状态：`pending_chatgpt_review`
> 本卡仅建立可追溯的审阅结构。方法、题型、结果与优劣在有阅读依据前不得填写。

## 基本信息

- 年份：{row["year"]}
- 题号：{row["question"]}
- 论文 ID：{row["id"]}
- 原始 Markdown：[打开]({md_link})
- 原始 PDF：[打开]({pdf_link})

## 题型

unknown

## 整体建模逻辑

unknown

## 问题一

### 任务本质

unknown

### 使用方法

unknown

### 为什么这样建模

unknown

### 输入

unknown

### 输出

unknown

### 验证方式

unknown

### 可迁移经验

unknown

## 问题二

待依据原始论文填写。

## 问题三

待依据原始论文填写。

## 问题四

如论文存在第四问，待依据原始论文填写。

## 核心方法

unknown

## 关键知识点

unknown

## 模型验证方式

unknown

## 值得学习的建模思想

unknown

## 值得学习的写作手法

unknown

## 可迁移题型

unknown

## 注意事项

unknown
'''


def paper_notes_index(rows: list[dict[str, str]]) -> str:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["year"], row["question"])].append(row)
    lines = ["# 论文经验卡", "", "本目录的每张卡都可追溯到原始 Markdown 与 PDF。`pending_chatgpt_review` 表示尚未填写任何未经审阅的语义结论。", ""]
    for (year, question) in sorted(groups):
        lines.extend([f"## {year} {question} 题", ""])
        for row in sorted(groups[(year, question)], key=lambda item: item["id"]):
            target = f"{year}/{question}/{row['id']}.md"
            lines.append(f"- `{row['id']}`：[经验卡]({quote(target, safe='/.-_')})")
        lines.append("")
    return "\n".join(lines)


def scaffold_documents() -> dict[str, str]:
    pattern_sections = []
    for pattern in PATTERNS:
        pattern_sections.extend([
            f"## {pattern}", "", "- 典型任务：待从已审阅经验卡归纳。",
            "- 建模前检查：输入、输出、约束、数据质量与评价目标。",
            "- 候选方法与选择依据：待附有论文证据后填写。",
            "- 验证方法、常见错误与优秀论文案例：待填写。", "",
        ])
    knowledge_sections = []
    for item in KNOWLEDGE:
        knowledge_sections.extend([f"## {item}", "", "- 相关论文与可复用知识点：待从已审阅经验卡建立链接。", ""])
    return {
        "MODELING_PLAYBOOK.md": """# 建模方法论手册

> 证据状态：通用审阅框架；尚未把任何未审阅论文结论列为证据。

## 读题

先识别任务动词、输入、输出、约束、数据形态，以及时间、空间、网络或机理结构。

## 拆题

复杂任务 → 子任务 → 可计算量 → 局部模型 → 整体方案。每一步应说明其输出如何进入下一步。

## 量化抽象概念

抽象概念 → 可观测变量 → 指标体系 → 映射/权重 → 综合量。指标定义和权重来源必须可追溯。

## 选择与组合模型

按任务结构选择；简单模型先作基线；复杂模型需说明新增解决的困难及额外验证。常见流程为预处理 → 特征提取 → 建模 → 求解 → 验证 → 改进。

## 验证

计算出结果不等于模型成立。分别检查准确性、稳定性、鲁棒性、泛化性与实际可解释性。
""",
        "PROBLEM_PATTERN_INDEX.md": "# 题型索引\n\n> 证据状态：以下为检索骨架。案例、方法与结论只在经验卡经审阅后补入。\n\n" + "\n".join(pattern_sections),
        "METHOD_INDEX.md": """# 方法索引

> 证据状态：未依据文件名或自动文本猜测算法。本页只在方法被原始论文明确支持后添加条目。

每个方法条目应说明：解决的问题、适用数据、局限、何时不宜使用、输入/输出、对比模型、验证方式，以及可追溯的论文链接。
""",
        "KNOWLEDGE_INDEX.md": "# 知识点索引\n\n> 证据状态：待由审阅后的经验卡建立论文关联。\n\n" + "\n".join(knowledge_sections),
        "VALIDATION_GUIDE.md": """# 模型验证指南

> 证据状态：这是按模型类型组织的核对框架；具体案例待附审阅证据。

## 回归

可检查 MAE、MSE、RMSE、MAPE、R² 与残差；须说明划分方式与对照基线。

## 分类与聚类

分类可检查混淆矩阵、Precision、Recall、F1、ROC-AUC；聚类可检查轮廓系数、DBI、CH，并审查业务可解释性。

## 优化与评价

优化需检查可行性、基准对比、收敛、多次随机运行与目标权衡；综合评价需检查权重敏感性、排名一致性和交叉方法对照。

## 机理、机器学习与鲁棒性

机理模型需与观测、极限情况或物理约束对照；机器学习需说明划分、交叉验证、基线、消融与泛化；鲁棒性可采用参数扰动、噪声注入、Monte Carlo 与不同场景测试。
""",
        "WRITING_GUIDE.md": """# 数模论文写作指南

> 证据状态：通用写作核对框架；优秀论文的具体语言案例待经审阅后补入。

## 摘要

背景 → 总体方案 → 各问方法与关键定量结果 → 关键词。避免只写“效果好”，应给出指标或比较条件。

## 分析、建模与结果

用数学语言重构任务，说明困难与拆解逻辑；变量定义 → 公式 → 参数来源 → 求解设置；结果 → 对比 → 解释 → 现实含义。

## 严谨表达

结论应由证据、指标和实验/推导支撑。例如应写明“在相同数据划分和评价指标下”的比较条件，而非笼统断言模型最优。
""",
        "EVIDENCE_CASES.md": """# 可追溯案例库

> 当前没有论文语义案例。本页只收录已填经验卡中的可追溯案例，禁止从题名或文件名推断。

## 抽象概念量化

待添加经审阅案例。

## 机理与数据驱动结合

待添加经审阅案例。

## 特征工程、多模型比较与验证

待添加经审阅案例。
""",
    }


def write_semantic_index(rows: list[dict[str, str]], existing: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        prior = existing.get(row["id"], {})
        item = {field: prior.get(field, "") for field in SEMANTIC_FIELDS}
        item.update({
            "year": row["year"], "question": row["question"], "paper_id": row["id"], "title": row["title"],
            "source_md": row["markdown_file"], "source_pdf": row["source_pdf"],
        })
        if not item["review_status"]:
            item["review_status"] = "pending_chatgpt_review"
        output.append(item)
    with SEMANTIC_INDEX.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEMANTIC_FIELDS)
        writer.writeheader()
        writer.writerows(output)
    return output


def validate(rows: list[dict[str, str]], semantic_rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    manifest_ids = {row["id"] for row in rows}
    semantic_ids = {row["paper_id"] for row in semantic_rows}
    if manifest_ids != semantic_ids:
        errors.append("semantic_index IDs do not exactly match papers_manifest IDs")
    for row in rows:
        card = NOTES / row["year"] / row["question"] / f"{row['id']}.md"
        if not card.exists():
            errors.append(f"missing card: {card.relative_to(ROOT).as_posix()}")
        if not (ROOT / row["markdown_file"]).exists():
            errors.append(f"missing source Markdown: {row['markdown_file']}")
        if not (ROOT / row["source_pdf"]).exists():
            errors.append(f"missing source PDF: {row['source_pdf']}")
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    documents = [ROOT / "README.md", NOTES / "README.md"]
    documents.extend(NOTES.rglob("*.md"))
    documents.extend(STRATEGY.glob("*.md"))
    for document in documents:
        if not document.exists():
            errors.append(f"missing linked-document source: {document.relative_to(ROOT).as_posix()}")
            continue
        for target in link_pattern.findall(document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (document.parent / unquote(target.split("#", 1)[0])).resolve().exists():
                errors.append(f"broken link in {document.relative_to(ROOT).as_posix()}: {target}")
    return errors


def write_report(rows: list[dict[str, str]], semantic_rows: list[dict[str, str]], errors: list[str]) -> None:
    status = Counter(row["review_status"] for row in semantic_rows)
    groups = Counter((row["year"], row["question"]) for row in semantic_rows)
    lines = [
        "# 第二阶段语义整理报告", "",
        f"- 论文总数：{len(rows)}", f"- 已完成语义审阅：{status.get('reviewed', 0)}",
        f"- 待 ChatGPT 审阅：{status.get('pending_chatgpt_review', 0)}", "- 已识别题型/算法/验证方式：0（本轮未进行语义猜测）",
        "- 索引状态：经验卡、语义索引、方法/题型/知识点/验证/写作/证据模板已生成。", "",
        "## 年份与题号待审阅数", "", "| 年份 | A | B | C | D | E | F | 合计 |", "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for year in sorted({row["year"] for row in semantic_rows}):
        values = [groups[(year, question)] for question in "ABCDEF"]
        lines.append(f"| {year} | " + " | ".join(map(str, values)) + f" | {sum(values)} |")
    lines.extend(["", "## 未确认项目", "", "- 所有方法、题型、验证方式、写作特征与可迁移结论均待基于原始论文由 ChatGPT 审阅后填入。", "", "## 结构校验", ""])
    lines += [f"- {error}" for error in errors] if errors else ["- 通过：145 张经验卡、语义索引 ID、原始 Markdown 与 PDF 路径均匹配。"]
    write_utf8(REPORT, "\n".join(lines) + "\n")


def main() -> int:
    rows = load_manifest()
    if len(rows) != 145:
        raise RuntimeError(f"Expected 145 manifest records, found {len(rows)}")
    existing = read_existing_index()
    created = 0
    for row in rows:
        card = NOTES / row["year"] / row["question"] / f"{row['id']}.md"
        if not card.exists():
            write_utf8(card, note_template(row))
            created += 1
    write_utf8(NOTES / "README.md", paper_notes_index(rows))
    for filename, content in scaffold_documents().items():
        path = STRATEGY / filename
        if not path.exists():
            write_utf8(path, content)
    semantic_rows = write_semantic_index(rows, existing)
    errors = validate(rows, semantic_rows)
    write_report(rows, semantic_rows, errors)
    print(f"cards_created={created} cards_total={len(rows)} pending={Counter(row['review_status'] for row in semantic_rows)['pending_chatgpt_review']} validation_errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
