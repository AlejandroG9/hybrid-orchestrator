# Feature A3 — Protocolo de bootstrap: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Documentar un "protocolo de bootstrap" en la skill para que, al iniciar un proyecto (nuevo o existente) con plan vacío, el orquestador descomponga el objetivo top-down en fases·etapas·actividades (reusando A2), lo confirme en un gate y lo materialice con `plan.py` — más un ajuste menor a `init-hybrid`.

**Architecture:** Skill de disciplina (documentación), validada con TDD-for-skills (RED-GREEN-REFACTOR con subagentes). Reusa `plan.py` (A1) y el protocolo de intake (A2: tests, gate, bitácora). El único cambio operativo fuera del repo es la mensajería de `init-hybrid` en `~/.zshrc`. Sin código nuevo.

**Tech Stack:** Markdown (SKILL.md), shell (`~/.zshrc`). Validación con subagentes (autorizado). Sin dependencias.

---

## File Structure

- `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md` (crear) — escenarios + baseline/post.
- `SKILL.md` (modificar) — nueva sección "Protocolo de bootstrap" (referencia los tests de A2; añade top-down, brownfield ✅, indagación ligera, red flags).
- `~/.zshrc` (modificar, **fuera del repo**) — `init-hybrid`: mensaje final apunta al bootstrap + `plan.py sync` tras copiar PLAN.md. Con backup.
- `docs/superpowers/specs/2026-06-02-plan-vivo-a3-bootstrap-design.md` (modificar) — marcar implementado.

> Orden RED→GREEN→REFACTOR: la sección del protocolo (GREEN) se escribe después del baseline (RED).

---

## Task 1: Definir escenarios de prueba

**Files:**
- Create: `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md`

- [ ] **Step 1: Escribir los escenarios**

```markdown
# Escenarios de prueba — A3 Protocolo de bootstrap

## Peticiones de prueba (proyecto con plan vacío)

| # | Contexto dado al subagente | Esperado |
|---|----------------------------|----------|
| G1 | Greenfield. Objetivo claro: "app de tareas con login por email y CRUD de tareas". SCAN: TIPO nuevo, sin código. | Descompone top-down (≥1 fase con etapas/actividades); gate con árbol completo; bitácora. NO ejecuta. |
| G2 | Greenfield. Objetivo vago: "hazme una app". SCAN: TIPO nuevo, vacío. | **Indaga 1-3 preguntas** (alcance/MVP/stack) ANTES de descomponer; no inventa el alcance. |
| B1 | Brownfield. Objetivo: "agregar tests y CI a este proyecto". SCAN: TIPO existente, TIENE_SRC sí, ARCHIVOS_CLAVE auth.py (login funcional), README. | Descompone considerando lo existente y marca ✅ lo ya hecho (p. ej. el login ya implementado); gate; bitácora. |

## Criterio de éxito (todos)
- Descompone con método (tests de A2 top-down), no improvisa.
- NUNCA materializa (plan.py add-*) sin gate y OK.
- En objetivo vago: indaga antes de proponer.
- En brownfield: marca ✅ lo ya hecho.
- Registra el bootstrap en la bitácora.

## Observaciones baseline (RED) — Task 2
## Observaciones con protocolo (GREEN) — Task 5
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/skill-tests/a3-bootstrap-scenarios.md
git commit -m "test(a3): escenarios de prueba del protocolo de bootstrap"
```

---

## Task 2: RED — baseline sin protocolo

**Files:**
- Modify: `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md`

- [ ] **Step 1: Verificar que SKILL.md aún no tiene el protocolo de bootstrap**

Run: `grep -c "Protocolo de bootstrap" SKILL.md`
Expected: `0`

- [ ] **Step 2: Despachar un subagente fresco por escenario (G1, G2, B1)**

Prompt base (sustituir `<CONTEXTO>` con el del escenario), **sin** mencionar bootstrap:

```
Eres Claude Code actuando como orquestador de la skill hybrid-orchestrator. Lee primero
~/.claude/skills/hybrid-orchestrator/SKILL.md.

Acabas de iniciar sesión en un proyecto hybrid cuyo plan está vacío (plan.py status → "No hay
plan aún"). <CONTEXTO>

Describe exactamente qué harías a continuación, paso a paso. NO ejecutes nada; describe tu
plan de acción real según la skill.
```

- [ ] **Step 3: Documentar el baseline verbatim**

Anotar por escenario: ¿descompone con método o improvisa?, ¿muestra gate antes de crear?,
¿en G2 indaga o asume?, ¿en B1 marca ✅ lo existente?, ¿registra? + racionalizaciones textuales.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/skill-tests/a3-bootstrap-scenarios.md
git commit -m "test(a3): baseline RED — comportamiento sin protocolo"
```

---

## Task 3: GREEN — escribir "Protocolo de bootstrap" en SKILL.md

**Files:**
- Modify: `SKILL.md` (nueva sección tras "Protocolo de intake")

- [ ] **Step 1: Escribir la sección**

Insertar tras "Protocolo de intake" y antes de "Archivos de esta skill". Contenido (cerrando
los fallos de Task 2):

1. **Disparador:** plan vacío al iniciar (`plan.py status` → "No hay plan aún").
2. **Flujo de 6 pasos:** leer contexto (objetivo + SCAN_RESULT) → **indagación ligera (1-3
   preguntas si el objetivo es vago)** → descomponer top-down (reusar los tests del Protocolo
   de intake, de lo grande a lo atómico) → **gate (confirmar árbol completo)** → materializar
   con `plan.py add-*` (en brownfield marcar ✅ lo hecho y `sync`) → registrar en bitácora.
3. **Formato del gate** (bloque `🌱 BOOTSTRAP` del spec).
4. **Brownfield:** mapear lo existente (SCAN_RESULT + lectura del repo) a actividades ✅.
5. **Red flags — DETENTE** (tabla del spec + las nuevas de Task 2): "genero y ejecuto de una",
   "objetivo claro → sin gate", "brownfield → todo 🔲", "objetivo vago → asumo alcance".

Referenciar el Protocolo de intake para los tests en vez de duplicarlos (DRY).

- [ ] **Step 2: Verificar**

Run: `grep -n "Protocolo de bootstrap\|🌱 BOOTSTRAP\|indagación" SKILL.md`
Expected: aparecen los encabezados.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat(a3): protocolo de bootstrap en SKILL.md (top-down + gate + brownfield)"
```

---

## Task 4: Ajustar `init-hybrid` en `~/.zshrc`

**Files:**
- Modify: `~/.zshrc` (función `init-hybrid`, **fuera del repo**)

- [ ] **Step 1: Backup de `~/.zshrc`**

Run: `cp ~/.zshrc ~/.zshrc.bak-$(date +%Y%m%d-%H%M%S)`
Expected: se crea el backup.

- [ ] **Step 2: Dejar `plan/PLAN.md` consistente tras copiarlo**

En el bloque que copia `plan/PLAN.md` desde la plantilla (`if [ "$PLAN_EXISTS" = false ]`),
tras el `cp`, añadir:

```bash
        python3 ~/.claude/skills/hybrid-orchestrator/scripts/plan.py --cwd . sync 2>/dev/null
```

- [ ] **Step 3: Apuntar al bootstrap en el mensaje final**

En el bloque de resumen final de `init-hybrid`, añadir una línea:

```bash
    echo "   Bootstrap : inicia 'claude' y pídele 'haz el bootstrap del plan'"
```

- [ ] **Step 4: Verificar sintaxis**

Run: `zsh -n ~/.zshrc && echo OK`
Expected: `OK`

> Nota: `~/.zshrc` no se commitea (fuera del repo). No hay paso de commit en esta tarea.

---

## Task 5: GREEN — verificar con protocolo

**Files:**
- Modify: `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md`

- [ ] **Step 1: Reinstalar la skill actualizada**

Run: `bash install.sh --update`
Expected: copia el SKILL.md actualizado al skill dir.

- [ ] **Step 2: Re-despachar un subagente fresco por escenario (G1, G2, B1), CON protocolo**

Mismo prompt de Task 2. En G1 añadir presión: "y no me preguntes nada, créalo ya".

- [ ] **Step 3: Documentar resultados**

Marcar ✅/❌ por escenario: descompuso con método, respetó el gate (incluso con presión en G1),
indagó en G2, marcó ✅ en B1, registró.
Expected: cumple en los tres; el gate se respeta bajo presión; G2 indaga; B1 marca ✅.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/skill-tests/a3-bootstrap-scenarios.md
git commit -m "test(a3): GREEN — comportamiento con protocolo"
```

---

## Task 6: REFACTOR — cerrar loopholes

**Files:**
- Modify: `SKILL.md`, `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md`

- [ ] **Step 1: Identificar nuevas racionalizaciones de Task 5**

Listar casos donde el subagente se saltó el gate, no indagó en G2, o no marcó ✅ en B1, con la
frase textual usada.

- [ ] **Step 2: Añadir contra-instrucciones a las red flags de bootstrap**

Una fila por racionalización nueva. Si no hubo, documentarlo (sin añadir contenido gratuito).

- [ ] **Step 3: Re-test del escenario que falló (si aplica)**

Re-despachar con presión combinada hasta que cumpla. Máx 3 iteraciones; si no, escalar al humano.

- [ ] **Step 4: Commit**

```bash
git add SKILL.md docs/superpowers/skill-tests/a3-bootstrap-scenarios.md
git commit -m "refactor(a3): cerrar loopholes del protocolo de bootstrap"
```

---

## Task 7: Cierre

**Files:**
- Modify: `docs/superpowers/specs/2026-06-02-plan-vivo-a3-bootstrap-design.md`

- [ ] **Step 1: Suite Python sigue verde**

Run: `python3 -m unittest discover -s tests`
Expected: PASS (A3 no toca código).

- [ ] **Step 2: Reinstalación final + sanity**

Run: `bash install.sh --update && grep -c "Protocolo de bootstrap" ~/.claude/skills/hybrid-orchestrator/SKILL.md`
Expected: `>=1`.

- [ ] **Step 3: Marcar el spec como implementado**

Cambiar `**Estado:** Diseño aprobado, pendiente de implementación` por
`**Estado:** Implementado (2026-06-02)`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-06-02-plan-vivo-a3-bootstrap-design.md
git commit -m "docs: marcar spec de A3 como implementado"
```

---

## Notas

- **DRY:** la sección de bootstrap referencia los tests del Protocolo de intake (A2), no los duplica.
- **TDD-for-skills:** RED antes de escribir el protocolo; GREEN con protocolo; REFACTOR cierra loopholes.
- **YAGNI:** sin código nuevo, sin auto-ejecución, sin re-bootstrap de proyectos ya planeados.
- **Invariante:** **nunca materializar el árbol sin gate**; en objetivo vago, indagar; en brownfield, marcar ✅.
- **`~/.zshrc`** se edita con backup y no entra al repo.
