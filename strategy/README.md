# 方法论与写作经验库

本目录把通用方法论、题型/方法导航与经原文核对的论文案例分开。除 [EVIDENCE_CASES](EVIDENCE_CASES.md) 和已明确标注来源的题级卡外，内容主要是比赛工作框架，不代表 145 篇论文的统计结论。

## 按问题选择入口

| 现在的问题 | 打开 |
|---|---|
| 需要完整方法论 | [MASTER_MODELING_GUIDE](MASTER_MODELING_GUIDE.md) |
| 比赛现场快速判断题型和路线 | [PROBLEM_METHOD_QUICK_REFERENCE](PROBLEM_METHOD_QUICK_REFERENCE.md) |
| 查看 2022—2025 每年每题的阅读证据 | [ANNUAL_QUESTION_EVIDENCE_MATRIX](ANNUAL_QUESTION_EVIDENCE_MATRIX.md) |
| 不知道怎么建模 | [MODELING_PLAYBOOK](MODELING_PLAYBOOK.md) |
| 知道题型，不知道路线 | [PROBLEM_PATTERN_INDEX](PROBLEM_PATTERN_INDEX.md) |
| 知道方法，想查适用性 | [METHOD_INDEX](METHOD_INDEX.md) |
| 想查某领域知识 | [KNOWLEDGE_INDEX](KNOWLEDGE_INDEX.md) |
| 不知道怎么证明可信 | [VALIDATION_GUIDE](VALIDATION_GUIDE.md) |
| 不知道怎么解释模型 | [EXPLAINABILITY_GUIDE](EXPLAINABILITY_GUIDE.md) |
| 不知道论文怎么写 | [WRITING_GUIDE](WRITING_GUIDE.md) |
| 想找已核对的历年案例 | [EVIDENCE_CASES](EVIDENCE_CASES.md) |
| 比赛正在进行 | [COMPETITION_WORKFLOW](COMPETITION_WORKFLOW.md) |

同一赛题多篇论文的横向比较入口见 [question_notes](../question_notes/README.md)。

## 证据等级

1. 原始 PDF：公式、图表、复杂表格与精确页码的最终依据。
2. 全文 Markdown：便于搜索和通读，但转换可能损失版式或公式。
3. 可追溯案例/已审核卡：经过正文抽查，仍需在迁移时核对边界。
4. 通用指南：用于组织思考和写作，不是具体论文事实。
5. pending 经验卡与自动映射：只是审阅队列，不包含确认后的语义结论。

## 自动生成边界

scripts/build_semantic_indexes.py 只更新各索引中的 AUTO-GENERATED 区域，并且只读取 metadata/semantic_index.csv 与经验卡状态；不会覆盖人工方法论正文，也不会把 pending 条目推断成案例。
