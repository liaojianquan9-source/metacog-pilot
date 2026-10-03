# Learning Coach · A Metacognitive Monitoring System 🧠

**English** | [中文](README.zh-CN.md)

> There are enough learning methods out there — this Skill adds none.
> It is your **sparring partner**: it moves the metacognitive monitoring loop — *what to learn, have I learned it, what to do when stuck* — out of your head and into an **external brain**.

## Why it exists

The richer the learning ecosystem gets, the scarcer monitoring becomes:

- Working memory can't hold an unfamiliar domain — a few task switches and you forget what you were even looking up
- Right after studying you feel you've learned it — that's the fluency illusion, not mastery
- Facing a hard task, grinding vs. quitting happens by inertia — afterwards you can't say which path you chose

Nelson & Narens (1990) answered this long ago: learning is a system that needs monitoring. But metacognition itself consumes working memory — so this Skill **externalizes** the monitor: the flowchart watches you, you just learn.

## How it works

**Knowledge map = external context**

Start from concepts you already know, and spread a map along four relation types: parent / child / sibling / related. Where you are and where you're stuck both live on the map. Concepts that don't attach yet get a placeholder — don't force them. How deep to go on each concept is decided by its relevance to your goal.

**Monitoring loop = the external brain**

![Metacognitive monitoring flowchart](assets/metacognitive-monitoring-flow.png)

```
Select task → Assess mastery → Judge difficulty → Set strategy → Retrospective check → Record
```

- **Select task**: the most important, not the easiest — most easy tasks are far from the goal
- **Assess mastery**: three layers — surface (recall) / semantic (explain) / intuitive (apply)
- **Judge difficulty**: by material availability; if it's hard and you're not confident, switch tasks — key features of the task (names, terms, formulas) are often the breakthrough
- **Set strategy**: allocate a time budget and pick processing depth — shallow (premises & conclusions only) or deep (semantic + intuitive)
- **Retrospective check**: when stuck, inspect key features to trigger new tasks; when confident but failing, check time allocation first

**Mastery ≠ archived**

The first time a task hits mastery ≥ 0.8 it is only marked "pending re-test"; it is archived as done only after passing a re-test in a later session. This follows the delayed-JOL effect (Nelson & Dunlosky, 1991): self-assessment right after study reads short-term fluency and is systematically inflated — delayed re-testing measures real mastery.

**Socratic questioning**

Auto-enabled for zero-foundation learners. Six dimensions in rotation — clarify → assumption → evidence → perspective → consequence → reflection — at most 3 rounds per goal, and you can say "explain directly" anytime to exit. The coach is a scaffold, not a search engine: building maps and questioning are the default, dumping answers is the exception.

## Features

- ✅ Metacognitive monitoring loop (six-step external-brain flow)
- ✅ Knowledge maps (four relation types, Mermaid mind maps)
- ✅ Three-layer mastery assessment + delayed re-test calibration
- ✅ Four legitimate moves when stuck: grind / switch / seek help / shelve
- ✅ Socratic questioning (auto-enabled for beginners)
- ✅ Resume-from-breakpoint, multi-goal management, cognitive-cycle logging
- ✅ Optional Obsidian vault sync

## Usage

### CLI mode

```bash
# Run inside the project directory (pure Python stdlib, no dependencies)
python scripts/coach.py start "Machine Learning"          # start a new topic
python scripts/coach.py start "Machine Learning" --level 零基础   # beginner: Socratic mode on
python scripts/coach.py status                            # view progress
python scripts/coach.py list                              # list all learning goals
python scripts/coach.py mindmap                           # generate mind map
python scripts/coach.py export                            # export data
python scripts/coach.py socratic "supervised learning"    # Socratic assessment
python scripts/coach.py answer "your answer"
python scripts/coach.py explain                           # exit questioning, get direct explanation
```

### Interactive mode

```bash
python scripts/coach.py

教练> start 机器学习
教练> continue
教练> status
教练> report
教练> mindmap
```

## Use as an AI Skill

Learning Coach is a standard Skill (SKILL.md + scripts + data) — drop it into any AI assistant that supports skills.

### Trigger words

| Trigger | Branch |
|---------|--------|
| `学习X` (learn X) | Onboarding → monitoring loop |
| `继续` (continue) | Re-test pending tasks → resume |
| `评估X` (assess X) | Three-layer mastery assessment |
| `查看进度` / `学习目标列表` | Report profile status |
| `切换目标X` | Switch learning goal |
| `学习报告` | Report + mind map |
| `socratic X` / `直接解释` | Socratic questioning |

See `references/dialogue-examples.md` for typical conversations (Chinese).

## Repository layout

```
learning-coach/
├── README.md           # This file (English)
├── README.zh-CN.md     # 中文说明
├── SKILL.md            # Agent execution manual
├── references/
│   ├── dialogue-examples.md  # Dialogue format reference
│   └── obsidian-sync.md      # Obsidian sync commands
├── assets/
│   └── metacognitive-monitoring-flow.png  # Monitoring flowchart
├── scripts/
│   └── coach.py        # Main program (single source of truth for data & algorithms)
├── data/
│   ├── profiles.json   # Learning profiles (auto-generated)
│   └── records.json    # Cognitive-cycle logs (auto-generated)
└── mindmaps/
    └── *.md            # Generated mind maps (auto-generated)
```

Data structures and algorithms live in `scripts/coach.py`; docs do not restate them.

## References

1. Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *The Psychology of Learning and Motivation*.
2. Nelson, T. O., & Dunlosky, J. (1991). When people's judgments of learning (JOLs) are extremely accurate at predicting subsequent recall: The "delayed-JOL effect." *Psychological Science*, 2, 267–270.
3. Ausubel, D. P. (1968). *Educational Psychology: A Cognitive View*. Holt, Rinehart & Winston.
4. 老奇好好奇. 一名年更UP主的三年：我们是如何快速学习陌生领域的？[Video]. Bilibili.

## Changelog

### v1.00 (2026-10-03)
- ♻️ Repositioned: a metacognitive monitoring system — sparring partner + external brain
- ♻️ SKILL.md rewritten on writing-for-agents principles: step-first structure, completion criteria, progressive disclosure
- 🧠 Monitoring loop calibrated against the source video transcript: difficulty judgment, task switching via key features, shallow/deep processing, adjustable mastery expectation, retrospective monitoring, four legitimate stuck-moves
- 🎯 Monitoring calibration: mastery ≥ 0.8 becomes "pending re-test"; archived only after a delayed re-test (delayed-JOL effect)
- 🗺️ Knowledge-map onboarding rules: four relation types, placeholders, depth by goal relevance
- Dialogue examples moved to `references/dialogue-examples.md`, Obsidian sync to `references/obsidian-sync.md`

## License

MIT License — free to use, modify, and distribute.

---

**Enough methods. What's missing is a system that watches for you.** 🚀
