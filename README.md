# Hybrid Orchestrator

**Claude Code as architect + any LLM as developer.**

Project orchestration with phases, stages and activities. Full execution traceability via `.md` files. Zero token overhead — plain text, no APIs, no JSON parsing.

---

## Why?

Most multi-agent setups treat all LLMs the same. This skill treats them differently — each agent has a role based on what it does best:

| Agent | Strength | Use for |
|-------|----------|---------|
| **Gemini** | 1M token context window + Google Search | Large codebase analysis, logs, external research |
| **Codex** | Fast generation | Boilerplate, repetitive patterns, quick refactors |
| **Cursor** | Precise file editing | Modifying existing code without breaking context |
| **Claude** | Deep reasoning | Complex logic, architecture decisions, critical components |

Claude Code stays as the **architect and PM** — it never writes implementation code directly. It plans, delegates, reviews, and decides what comes next.

---

## How it works

```
Claude Code (Orchestrator)
  → reads CLAUDE.md + plan/PLAN.md
  → generates activity .md files with acceptance criteria
  → calls run_subagent.py with the activity
  
run_subagent.py
  → reads frontmatter run-agent: from the activity .md
  → loads the matching briefing from templates/agents/[backend].md
  → invokes the CLI with briefing + activity as prompt
  
Sub-agent (Gemini / Codex / Cursor / Claude)
  → reads the activity
  → writes the code
  → logs execution in the .md file
  → reports: ✅ COMPLETED or ⛔ BLOCKED
  
Claude Code (Reviewer)
  → reads the execution log
  → verifies acceptance criteria
  → continues, retries, or escalates to human
```

Each activity `.md` has full traceability:
- Acceptance criteria with checkboxes
- Execution log per agent run (numbered, never deleted)
- Test results table
- Dependencies and related files
- Retry protocol (max 2 auto-retries, then escalate)

---

## Installation

**Requirements:** Python 3.9+ and at least one supported CLI installed.

```bash
git clone https://github.com/YOUR_USERNAME/hybrid-orchestrator
cd hybrid-orchestrator
bash install.sh
```

The installer places the skill in `~/.claude/skills/hybrid-orchestrator/`, copies templates to `~/plantillas-hybrid/`, and wires the `init-hybrid` helper into your shell (zsh or bash, auto-detected).

**To update:**
```bash
bash install.sh --update
```

### Multi-machine setup

The skill is fully portable — run the same two commands on each machine (macOS/zsh or Linux/bash):

```bash
git clone https://github.com/YOUR_USERNAME/hybrid-orchestrator
cd hybrid-orchestrator && bash install.sh   # detects your shell, wires `init-hybrid`
# update later:  git pull && bash install.sh --update
```

`init-hybrid` is installed as a versioned script (`init-hybrid.sh`) and sourced from your shell rc — restart the shell (or `source` your rc) after install. If `gemini` isn't installed, `init-hybrid` detects the available backends and asks whether to continue with what's there or install more. You only need the backends you plan to use: **`claude` is the guaranteed fallback**, so a server with only Claude Code still works (everything routes to `claude`).

**Supported CLIs:**

| Backend | Install |
|---------|---------|
| Gemini | `npm install -g @google/gemini-cli` |
| Codex | `npm install -g @openai/codex` |
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Cursor | `curl https://cursor.com/install -fsS \| bash` |

You only need to install the backends you plan to use.

---

## Quick Start

**1. Initialize a project:**
```bash
cd ~/your-project
init-hybrid
```

This scans the project with Gemini, copies templates, and generates a `CLAUDE.md` with detected context.

**2. Start Claude Code:**
```bash
claude
```

Tell it: *"use hybrid-orchestrator to plan this project"*

**3. Claude generates activities like:**
```
plan/
└── fase_01/
    └── etapa_01/
        ├── act_F01_E01_001.md   ← run-agent: gemini
        ├── act_F01_E01_002.md   ← run-agent: codex
        └── act_F01_E01_003.md   ← run-agent: claude
```

**4. Claude invokes the sub-agent:**
```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py \
  --agent plan/fase_01/etapa_01/act_F01_E01_001.md \
  --cwd $(pwd)
```

**5. List all activities:**
```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --list
```

---

## Activity structure

Each activity file combines Agent Skills frontmatter with full traceability:

```markdown
---
run-agent: gemini
status: 🔲 pendiente
created: 2026-06-01
phase: F01
stage: E01
---

# 📋 Descripción de la actividad
# ✅ Criterio de aceptación
# 📦 Output esperado
# 🤖 Registro de ejecución del agente
# 🧪 Pruebas realizadas
# 🔗 Dependencias y archivos relacionados
# 📝 Notas técnicas adicionales
```

The `run-agent` frontmatter tells `run_subagent.py` which CLI to use. The rest provides full context and traceability for both the agent and the human reviewing the work.

---

## Project structure

```
your-project/
├── CLAUDE.md              ← orchestrator rules (generated by init-hybrid)
├── plan/
│   ├── PLAN.md            ← phases, stages, status overview
│   └── fase_01/
│       └── etapa_01/
│           └── act_F01_E01_001.md
└── src/                   ← code produced by sub-agents

~/.claude/skills/
└── hybrid-orchestrator/   ← the skill (global, never modified per project)
    ├── SKILL.md
    ├── scripts/
    │   ├── run_subagent.py
    │   └── plan.py
    ├── references/
    │   ├── subagents.md
    │   ├── plan-management.md
    │   ├── intake-protocol.md
    │   └── bootstrap-protocol.md
    └── templates/
        ├── CLAUDE.md
        ├── PLAN.md
        ├── fase.md
        ├── etapa.md
        ├── activity.md
        └── agents/
            ├── gemini.md
            ├── codex.md
            ├── cursor.md
            └── claude.md
```

---

## Retry protocol

| Attempt | Action |
|---------|--------|
| 1st failure | Reformulate prompt with exact error |
| 2nd failure | Add full repo context with `--all-files` |
| 3rd failure | **PAUSE** — report to human with `⛔ ACTIVIDAD BLOQUEADA` format |

---

## Inspired by

- [shinpr/sub-agents-skills](https://github.com/shinpr/sub-agents-skills) — cross-LLM orchestration via Agent Skills format

---

## License

MIT
