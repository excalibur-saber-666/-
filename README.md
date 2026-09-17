# 中国研究生数学建模竞赛优秀论文 V1 知识库

本仓库收录 2022—2025 年 145 篇优秀论文的原始 PDF、可检索 Markdown，以及面向比赛的建模方法论、题型/方法导航、验证和写作指南。目标不是储存历史答案，而是帮助完成“识别问题结构 → 建立 baseline → 选择模型 → 构造证据链 → 验证、解释与写作”。

## 当前资料库

| 年份 | 论文数 |
|---|---:|
| 2022 | 42 |
| 2023 | 58 |
| 2024 | 24 |
| 2025 | 21 |
| 合计 | 145 |

- [历年论文索引](knowledge_base/INDEX.md) · [赛题目录](knowledge_base/QUESTION_CATALOG.md)
- [完整方法论](strategy/MASTER_MODELING_GUIDE.md) · [建模手册](strategy/MODELING_PLAYBOOK.md)
- [题型索引](strategy/PROBLEM_PATTERN_INDEX.md) · [方法索引](strategy/METHOD_INDEX.md) · [知识领域入口](strategy/KNOWLEDGE_INDEX.md)
- [验证指南](strategy/VALIDATION_GUIDE.md) · [可解释性指南](strategy/EXPLAINABILITY_GUIDE.md) · [写作指南](strategy/WRITING_GUIDE.md)
- [已核对案例](strategy/EVIDENCE_CASES.md) · [比赛十阶段工作流](strategy/COMPETITION_WORKFLOW.md)
- [同题横向比较卡](question_notes/README.md) · [V1 最终报告](reports/final_v1_report.md)

## 比赛推荐使用流程

    新题
    ↓
    QUESTION_CATALOG：确认赛题与历史材料
    ↓
    PROBLEM_PATTERN_INDEX：识别任务结构
    ↓
    MODELING_PLAYBOOK：拆题、抽象、建立 baseline
    ↓
    METHOD_INDEX / KNOWLEDGE_INDEX：核对方法前提
    ↓
    VALIDATION_GUIDE / EXPLAINABILITY_GUIDE：设计证据链
    ↓
    WRITING_GUIDE：严谨呈现
    ↓
    EVIDENCE_CASES / question_notes：参考可迁移案例

比赛进行中可直接按 [COMPETITION_WORKFLOW](strategy/COMPETITION_WORKFLOW.md) 的十阶段和检查表执行。

## 目录与证据边界

- papers/：145 份原始 PDF，是公式、图形、复杂表格和精确页码的最终依据。
- knowledge_base/：145 份 MarkItDown 转换正文，用于搜索、通读与初筛。
- paper_notes/：145 张可追溯经验卡；当前均为待逐篇深度审阅。
- question_notes/：同题多篇论文横向比较；当前仅有 4 张基于已核对单篇案例的基础卡。
- strategy/：通用方法论和比赛指南；不等同于 145 篇论文的频率统计。
- metadata/：稳定 manifest 与语义审阅队列。
- reports/：转换、方法论审阅、语义状态与 V1 校验报告。

## 当前完成状态

| 层级 | 状态 |
|---|---|
| 原始资料整理 | 完成：145 PDF |
| 全文转换 | 完成：145 Markdown |
| 方法论 V1 | 完成 |
| strategy 核心指南 | 完成 |
| paper_notes 结构 | 完成：145 张 |
| 逐篇深度语义审阅 | 0 complete / 0 partial / 145 pending |

“V1 架构完成”不表示“145 篇论文已完成深度语义分析”。任何 pending 卡都不能作为已确认的方法、结果或创新点。

## 维护与验证

使用独立 MarkItDown 环境补齐/初始化语义结构：

    & 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\initialize_semantic_stage.py
    & 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\build_semantic_indexes.py
    & 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\validate_semantic_kb.py

新增或更新 PDF 后运行：

    & 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\organize_and_update.py

Markdown 是文本提取结果。出现乱码、公式断裂、表格错位、图像缺失或页码需求时，请回看原始 PDF。
