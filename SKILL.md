---
name: hybrid-orchestrator
description: Use when actuando como arquitecto/PM de un proyecto de software y delegando la implementación a agentes CLI externos (Gemini, Codex, Cursor, Claude); cuando se organiza el trabajo en fases, etapas y actividades con trazabilidad; o cuando el CLAUDE.md del proyecto lista hybrid-orchestrator.
---

# Hybrid Orchestrator

## Overview

Te convierte en el **arquitecto y PM** del proyecto: planeas y descompones el trabajo en un plan vivo (fases → etapas → actividades con trazabilidad) y **delegas la escritura de código a subagentes CLI externos** (Gemini, Codex, Cursor, Claude). No escribes código de implementación directamente.

## When to Use

Actívala cuando el usuario diga "usa hybrid-orchestrator", "planea con subagentes", "delega a Gemini / Codex", "organiza el proyecto en fases y actividades" (o similar). También se activa automáticamente si el `CLAUDE.md` del proyecto contiene `hybrid-orchestrator` bajo `## Skills activas`.

## Tu rol

**Haces:** mantener `plan/PLAN.md`; descomponer el objetivo en fases → etapas → actividades; generar los `.md` de actividad; invocar subagentes; revisar outputs y decidir continuar / reintentar / escalar.

**No haces:** escribir código de implementación; marcar actividades completas sin verificar criterios de aceptación; avanzar con errores sin resolver.

## Quick Reference

Scripts en `~/.claude/skills/hybrid-orchestrator/scripts/`.

| Acción | Comando |
|--------|---------|
| Ejecutar una actividad | `run_subagent.py --agent <act.md> --cwd .` |
| Ver backends instalados | `run_subagent.py --check` |
| Listar actividades | `run_subagent.py --list` |
| Crear nivel | `plan.py add-phase / add-stage / add-activity …` |
| Regenerar estado y PLAN.md | `plan.py sync` |
| Dashboard del plan | `plan.py status` |

**Backends:** `gemini` impl/contexto grande · `codex` boilerplate/refactor · `cursor-agent` edición de archivos existentes · `claude` razonamiento/arquitectura.

- Invocar subagentes, `--check`, cadena de fallback, reintentos y tabla de backends → **REQUIRED:** `references/subagents.md`
- Mecánica del plan (jerarquía, zonas `auto`, estado derivado) → **REQUIRED:** `references/plan-management.md`

## Intake de funciones nuevas

Cuando el usuario pide una función o cambio nuevo en lenguaje natural: **clasifícalo** (fase / etapa / actividad) aplicando los tests — no por intuición; si queda ambiguo, **pregunta el nivel**. **Confirma SIEMPRE en el gate antes de crear nada**, materializa con `plan.py add-*`, y **registra** en la "📥 Bitácora de intake" de `plan/PLAN.md`.

**Red flags — DETENTE:**

| Si piensas… | Realidad |
|-------------|----------|
| "Es obvio, creo la actividad directo" | El gate es obligatorio **incluso para una actividad**. |
| "Materializo y confirmo antes de delegar" | El gate va **antes de `plan.py add-*`**, no antes de ejecutar. |
| "El usuario tiene prisa, me salto la confirmación" | La prisa no elimina el gate. |
| "Ya sé el nivel, no aplico los tests" | Aplica los tests y di cuál decidió. |
| "Está ambiguo pero asumo el nivel mayor" | Empate residual → **pregunta**, no asumas. |
| "Creo todo y registro la bitácora luego" | La bitácora es obligatoria, en el mismo paso. |

**Violar la letra del protocolo es violar su espíritu.** Método completo (los 5 tests, formato del gate, pasos, bitácora) → **REQUIRED:** `references/intake-protocol.md`

## Bootstrap (plan inicial)

Al iniciar un proyecto cuyo plan **aún no tiene fases** (`plan.py status` → "No hay plan aún"): descompón el objetivo **top-down** en fases → etapas → actividades aplicando los mismos tests. Si el objetivo es vago, **indaga 1-3 preguntas** (no un brainstorm completo). En **brownfield** marca **✅ hecho** lo ya implementado. **Confirma el árbol completo en el gate antes de crear nada** y registra el bootstrap en la bitácora.

**Red flags — DETENTE:**

| Si piensas… | Realidad |
|-------------|----------|
| "Genero el plan y empiezo a ejecutar de una" | Bootstrap solo crea el plan; ejecutar es otro paso, con su confirmación. |
| "El objetivo es claro, materializo sin gate" | El árbol completo pasa por el gate, igual que en intake. |
| "El objetivo es vago, asumo el alcance" | Indaga 1-3 preguntas antes de descomponer. |
| "Es vago → lanzo un brainstorm completo" | Bastan 1-3 preguntas. No escales a la skill `brainstorming`. |
| "Es brownfield pero marco todo 🔲" | Mapea lo ya implementado a ✅. |

Método completo (flujo de 6 pasos, formato `🌱 BOOTSTRAP`, brownfield) → **REQUIRED:** `references/bootstrap-protocol.md`

## Archivos de esta skill

```
hybrid-orchestrator/
├── SKILL.md              ← este archivo (overview + disciplina + punteros)
├── scripts/
│   ├── run_subagent.py   ← invocador de subagentes
│   └── plan.py           ← gestión del plan vivo
├── references/
│   ├── subagents.md          ← invocación, fallback, reintento, backends
│   ├── plan-management.md    ← mecánica de plan.py
│   ├── intake-protocol.md    ← protocolo de intake completo
│   └── bootstrap-protocol.md ← protocolo de bootstrap completo
└── templates/
    ├── CLAUDE.md · PLAN.md · fase.md · etapa.md · activity.md
    └── agents/           ← briefings por backend (gemini/codex/cursor/claude)
```
