# Obsidian 同步

学习数据（JSON）是机器可读的中间态，Obsidian（Markdown）是人类可读的终态。检测到 `obsidian-vault` skill 可用时执行以下同步；不可用时全部跳过。

## 同步时机

| 事件 | 命令 | 条件 |
|------|------|------|
| 建档 / 进度更新 | `learning-profile` | 每次 |
| 完成认知循环 | `learning-session` → 然后 `learning-profile` | 每次评估完成 |
| 掌握度达标 | `learning-insight` | mastery ≥ 0.8 时追加 |
| 首次生成路径 | `learning-mindmap` | 一次 |
| 用户说"继续" | `learning-context` 读取上次进度 | 循环开始前 |

## 命令

```bash
# 同步学习档案
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-profile \
  --profile-json '{"topic":"机器学习","level":"有基础","goal":"求职","overall_progress":0.5}'

# 同步认知循环
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-session \
  --topic "机器学习" \
  --record-json '{"task":{"name":"监督学习"},"assessment":{"mastery_level":0.5}}'

# 同步学习洞察（mastery ≥ 0.8 时触发）
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-insight \
  --concept "监督学习" --topic "机器学习" --content "核心要义"

# 同步思维导图
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-mindmap \
  --topic "机器学习" --mermaid "mindmap\n  root((ML))\n    监督学习"

# 读取学习上下文（启动时）
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-context --topic "机器学习"
```

## Obsidian 目录结构

```
00_Learning/
├── README.md                          ← 学习总览（自动生成）
├── _profiles/{topic}.md               ← 学习档案
├── _sessions/{date}-{task}-认知循环.md ← 认知循环记录
├── _insights/{concept}.md             ← 学习洞察（原子笔记）
└── _maps/{topic}-认知地图.md          ← 思维导图
```
