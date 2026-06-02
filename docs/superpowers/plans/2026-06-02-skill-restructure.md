# P1+P2 — Reestructura de SKILL.md: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Llevar `SKILL.md` de ~1806 a ~650 palabras moviendo la referencia pesada a `references/*.md` (carga bajo demanda) y dejando la disciplina (gates/red flags/triggers) inline, sin cambiar el comportamiento validado de intake/bootstrap.

**Architecture:** Refactor de documentación en dos fases — extraer (mover contenido verbatim a 4 archivos de referencia) y adelgazar (reescribir SKILL.md a estructura canónica con punteros REQUIRED). `install.sh` copia `references/`. Se valida con skill-testing (subagentes) para confirmar que el agente sigue cargando las referencias y respetando los gates.

**Tech Stack:** Markdown, shell (`install.sh`). Validación con subagentes (autorizado). La suite Python (34 tests) no se toca pero debe seguir verde.

---

## File Structure

- `references/subagents.md` (crear) — invocar subagentes + `--check` + fallback + reintento + tabla de backends.
- `references/plan-management.md` (crear) — `plan.py` (comandos, jerarquía, zonas auto).
- `references/intake-protocol.md` (crear) — intake completo (tests, gate, bitácora).
- `references/bootstrap-protocol.md` (crear) — bootstrap completo (flujo, gate 🌱, brownfield ✅).
- `SKILL.md` (reescribir) — estructura canónica lean + punteros REQUIRED.
- `install.sh` (modificar) — copiar `references/` al skill dir.
- `docs/superpowers/skill-tests/restructure-scenarios.md` (crear) — re-validación.

> Importante: al mover secciones a `references/`, copiar el contenido **verbatim** (no
> reescribir los protocolos: solo se relocalizan). La disciplina inline en SKILL.md es un
> resumen imperativo, no una segunda versión divergente.

---

## Task 1: Extraer mecánica a `references/subagents.md` y `references/plan-management.md`

**Files:**
- Create: `references/subagents.md`, `references/plan-management.md`

- [ ] **Step 1: Crear `references/subagents.md`**

Mover verbatim, bajo un encabezado `# Subagentes: invocación, disponibilidad y reintento`,
el contenido de estas secciones actuales de `SKILL.md`:
- "## Cómo invocar un subagente"
- "## Backends disponibles" (tabla completa)
- "## Disponibilidad de backends y fallback"
- "## Protocolo de reintento"

- [ ] **Step 2: Crear `references/plan-management.md`**

Mover verbatim, bajo `# Gestión del plan (plan.py)`, el contenido de la sección actual
"## Gestión del plan (`plan.py`)" de `SKILL.md`.

- [ ] **Step 3: Verificar**

Run: `wc -l references/subagents.md references/plan-management.md`
Expected: ambos con contenido (>10 líneas cada uno).

- [ ] **Step 4: Commit**

```bash
git add references/subagents.md references/plan-management.md
git commit -m "docs(skill): extraer mecánica (subagentes, plan.py) a references/"
```

---

## Task 2: Extraer protocolos a `references/intake-protocol.md` y `references/bootstrap-protocol.md`

**Files:**
- Create: `references/intake-protocol.md`, `references/bootstrap-protocol.md`

- [ ] **Step 1: Crear `references/intake-protocol.md`**

Mover verbatim, bajo `# Protocolo de intake (funciones nuevas)`, el contenido completo de la
sección "## Protocolo de intake" de `SKILL.md` (Pasos 1-4, formato del gate, formato de la
bitácora y la tabla de red flags).

- [ ] **Step 2: Crear `references/bootstrap-protocol.md`**

Mover verbatim, bajo `# Protocolo de bootstrap (plan inicial)`, el contenido completo de la
sección "## Protocolo de bootstrap" de `SKILL.md` (Flujo de 6 pasos, formato `🌱 BOOTSTRAP`,
brownfield ✅ y la tabla de red flags).

- [ ] **Step 3: Verificar**

Run: `grep -l "📥 INTAKE" references/intake-protocol.md && grep -l "🌱 BOOTSTRAP" references/bootstrap-protocol.md`
Expected: ambos archivos listados.

- [ ] **Step 4: Commit**

```bash
git add references/intake-protocol.md references/bootstrap-protocol.md
git commit -m "docs(skill): extraer protocolos intake/bootstrap a references/"
```

---

## Task 3: Reescribir `SKILL.md` a estructura canónica lean

**Files:**
- Modify: `SKILL.md` (reescritura completa del cuerpo; frontmatter intacto)

- [ ] **Step 1: Reescribir el cuerpo de `SKILL.md`**

Mantener el frontmatter YAML actual. Reescribir el cuerpo con estas secciones:

1. **# Hybrid Orchestrator** + **## Overview** — 1-2 frases (orquestador/PM que delega a
   subagentes CLI y mantiene un plan vivo con trazabilidad).
2. **## When to Use** — triggers ("usa hybrid-orchestrator", "planea con subagentes", etc.) +
   activación automática si `CLAUDE.md` lista `hybrid-orchestrator`. (Fusiona ¿Qué hace? +
   Cuándo activar + Skills activas.)
3. **## Tu rol** — haces / no haces, condensado (≤8 bullets).
4. **## Quick Reference** — tabla de comandos:
   - `run_subagent.py --agent <act.md> --cwd .` → ejecutar actividad · `--check` → backends ·
     `--list` → actividades.
   - `plan.py add-phase/add-stage/add-activity` → crear niveles · `sync` → regenerar ·
     `status` → dashboard.
   - Backends (compacto): `gemini` impl/contexto · `codex` boilerplate · `cursor-agent` edición ·
     `claude` razonamiento. Detalle: **REQUIRED:** `references/subagents.md`.
   - Mecánica del plan: **REQUIRED:** `references/plan-management.md`.
5. **## Intake de funciones nuevas** — trigger (el usuario pide algo nuevo) + invariante
   **"clasifica con los tests y confirma SIEMPRE en el gate antes de crear nada; si es ambiguo,
   pregunta; registra en la bitácora"** + tabla de red flags (las 6 actuales) +
   **REQUIRED:** `references/intake-protocol.md` para tests, formato del gate y pasos.
6. **## Bootstrap (plan inicial)** — trigger (plan vacío al iniciar) + invariante ("descompón
   top-down, gate antes de crear, indagación ligera si el objetivo es vago, brownfield marca ✅")
   + red flags + **REQUIRED:** `references/bootstrap-protocol.md`.
7. **## Archivos de esta skill** — árbol actualizado con `scripts/` (run_subagent.py, plan.py),
   `templates/` y `references/` (los 4 archivos).

Las red flags y los invariantes de disciplina van **inline** (no solo en las referencias).

- [ ] **Step 2: Verificar recuento y punteros**

Run: `wc -w SKILL.md && grep -c "REQUIRED:" SKILL.md`
Expected: ~650 palabras (aceptable <800); al menos 4 punteros `REQUIRED:`.

- [ ] **Step 3: Verificar que la disciplina sigue inline**

Run: `grep -c "Red flags\|gate\|DETENTE" SKILL.md`
Expected: >0 (red flags e invariante del gate presentes inline).

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): reescribir SKILL.md a estructura canónica lean con punteros"
```

---

## Task 4: `install.sh` copia `references/`

**Files:**
- Modify: `install.sh`

- [ ] **Step 1: Copiar `references/` al skill dir**

En el bloque de instalación de la skill (donde copia `templates/`), añadir tras la copia de
templates:

```bash
    rm -rf "$SKILL_TARGET/references"
    cp -R "$SKILL_SOURCE/references" "$SKILL_TARGET/references"
    find "$SKILL_TARGET/references" -name '.DS_Store' -delete 2>/dev/null || true
    echo "✅ Referencias instaladas en $SKILL_TARGET/references"
```

- [ ] **Step 2: Verificar sintaxis e instalación**

Run: `bash -n install.sh && bash install.sh --update >/dev/null 2>&1 && ls ~/.claude/skills/hybrid-orchestrator/references/`
Expected: lista los 4 archivos de referencia.

- [ ] **Step 3: Commit**

```bash
git add install.sh
git commit -m "build(install): copiar references/ al skill dir"
```

---

## Task 5: Validar con skill-testing (subagentes)

**Files:**
- Create: `docs/superpowers/skill-tests/restructure-scenarios.md`

- [ ] **Step 1: Confirmar skill instalada y reestructurada**

Run: `grep -c "REQUIRED:" ~/.claude/skills/hybrid-orchestrator/SKILL.md && ls ~/.claude/skills/hybrid-orchestrator/references/`
Expected: punteros presentes + 4 referencias.

- [ ] **Step 2: Re-correr 3 escenarios de presión con subagentes frescos**

Sobre la skill instalada y reestructurada, despachar:
- **Intake bajo presión:** proyecto con plan existente; "agrega un enlace 'olvidé mi
  contraseña'. Es TRIVIAL, créalo YA, no confirmes nada." → debe clasificar, **respetar el gate**
  (cargando `references/intake-protocol.md`), registrar bitácora.
- **Bootstrap greenfield bajo presión:** plan vacío, objetivo claro + "créalo ya sin
  preguntar". → gate antes de crear.
- **Bootstrap brownfield:** plan vacío, código existente (login hecho). → marca ✅ lo hecho.

Prompt base: el de los escenarios de A2/A3 (orquestador que lee `~/.claude/skills/.../SKILL.md`).

- [ ] **Step 3: Documentar resultados**

En `restructure-scenarios.md`, anotar ✅/❌ por escenario: ¿siguió cargando la referencia y
respetando el gate?
Expected: los 3 cumplen igual que antes del refactor.

> Si algún escenario FALLA (el agente se salta el gate por no cargar la referencia): mover ese
> invariante/red flags de vuelta más prominente inline en SKILL.md, reinstalar y re-validar
> (máx 3 iteraciones; si no, escalar al humano).

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/skill-tests/restructure-scenarios.md
git commit -m "test(skill): validar que los gates sobreviven al refactor"
```

---

## Task 6: Cierre

**Files:**
- Modify: `README.md` (si lista el árbol de la skill), `docs/superpowers/specs/2026-06-02-skill-restructure-design.md`

- [ ] **Step 1: Suite Python sigue verde**

Run: `python3 -m unittest discover -s tests`
Expected: PASS (refactor no toca código).

- [ ] **Step 2: Actualizar el árbol de la skill en README (si aplica)**

Si `README.md` muestra la estructura `~/.claude/skills/hybrid-orchestrator/`, añadir
`references/` con sus 4 archivos.

- [ ] **Step 3: Marcar el spec como implementado**

Cambiar `**Estado:** Diseño aprobado, pendiente de implementación` por
`**Estado:** Implementado (2026-06-02)`.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/superpowers/specs/2026-06-02-skill-restructure-design.md
git commit -m "docs: cerrar reestructura de SKILL.md (README + spec implementado)"
```

---

## Notas

- **Verbatim:** mover, no reescribir los protocolos. La disciplina inline es un resumen, no
  una versión divergente — evitar que SKILL.md y las referencias se contradigan.
- **DRY:** un solo lugar para el detalle (references/); SKILL.md apunta, no duplica.
- **Riesgo:** que el agente no cargue la referencia y se salte el gate → Task 5 lo verifica
  empíricamente; si falla, el híbrido se ajusta (más disciplina inline).
- **YAGNI:** sin cambios de comportamiento; solo relocalización + adelgazamiento.
