# 中国研究生数学建模竞赛优秀论文知识库

本仓库保存 2022—2025 年优秀论文的原始 PDF 与可检索 Markdown，服务于数模比赛备赛时的快速检索、方法比较和论文结构参考。

## 当前收录

| 年份 | 论文数 |
|---|---:|
| 2022 | 42 |
| 2023 | 58 |
| 2024 | 24 |
| 2025 | 21 |
| 合计 | 145 |

## 目录说明

- `papers/`：原始 PDF，唯一权威版本。
- `knowledge_base/`：自动生成、可检索的 Markdown；入口为 [INDEX](knowledge_base/INDEX.md) 和 [QUESTION_CATALOG](knowledge_base/QUESTION_CATALOG.md)。
- `metadata/papers_manifest.csv`：机器可读清单，包含路径、哈希和转换状态。
- `scripts/organize_and_update.py`：可重复运行的整理、转换与索引更新脚本。
- `reports/conversion_report.md`：本次转换与验证报告。

## 第二阶段：方法论与写作经验库

- `paper_notes/`：逐篇可追溯的经验卡；当前全部等待基于原文的语义审阅。
- `strategy/`：题型、方法、知识点、验证、写作和证据案例的索引框架。
- `metadata/semantic_index.csv`：与论文 manifest 一一对应的语义审阅队列。
- `reports/semantic_summary_report.md`：第二阶段完成度与待确认项。

初始化或补齐缺失经验卡：

```powershell
& 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\initialize_semantic_stage.py
```

## 新增或更新 PDF

1. 将文件置于 `papers/{year}/{question}/`。
2. 运行下方命令；未变化文件会跳过，新增或哈希变化文件会重新转换。

```powershell
& 'D:\CodexTools\MarkItDown\.venv\Scripts\python.exe' .\scripts\organize_and_update.py
```

Markdown 是文本提取结果。公式、图形、流程图、复杂表格和精确页码请以 PDF 为准。
