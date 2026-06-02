# Feature A2 — Protocolo de intake: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Documentar un "protocolo de intake" en la skill para que el orquestador, ante una petición de función nueva, la clasifique con un método explícito, confirme siempre (gate), proponga y materialice el sub-árbol con `plan.py`, y registre la decisión.

**Architecture:** Es una **skill de disciplina** (documentación), no código. Se construye con TDD-for-skills (RED-GREEN-REFACTOR): primero escenarios de prueba + baseline con subagentes frescos, luego se escribe el protocolo que cierra esos fallos, luego se re-verifica bajo presión y se cierran loopholes. Reusa `plan.py` de A1; sin código nuevo.

**Tech Stack:** Markdown (SKILL.md, templates/). Validación con subagentes (autorizado por el usuario). Sin dependencias.

---

## File Structure

- `docs/superpowers/skill-tests/a2-intake-scenarios.md` (crear) — escenarios de prueba reusables + observaciones baseline/post.
- `SKILL.md` (modificar) — nueva sección "Protocolo de intake" (metodología + flujo + formatos + red flags).
- `templates/CLAUDE.md` (modificar) — resumen del protocolo para sesiones por proyecto.
- `templates/PLAN.md` (modificar) — sección autorada "📥 Bitácora de intake".
- `docs/superpowers/specs/2026-06-02-plan-vivo-a2-intake-design.md` (modificar) — marcar implementado.

> Nota: el orden sigue RED→GREEN→REFACTOR. La sección del protocolo (GREEN) se escribe
> **después** de observar el baseline (RED), como exige `writing-skills`.

---

## Task 1: Definir escenarios de prueba

**Files:**
- Create: `docs/superpowers/skill-tests/a2-intake-scenarios.md`

- [ ] **Step 1: Escribir los escenarios**

Crear el archivo con un plan de proyecto de ejemplo y cuatro peticiones (una por nivel + una
ambigua). Contenido:

```markdown
# Escenarios de prueba — A2 Protocolo de intake

## Plan de ejemplo (estado inicial dado al subagente)

Proyecto: TaskApp
- F01 — Autenticación
  - E01 — Login con email
    - act_F01_E01_001 — Form de login [✅ hecho]
    - act_F01_E01_002 — Endpoint /login [🔄 en curso]

## Peticiones de prueba

| # | Petición del usuario | Nivel esperado | Comportamiento esperado |
|---|----------------------|----------------|--------------------------|
| A | "agrega un enlace de 'olvidé mi contraseña' en el login" | actividad | Nueva actividad en F01_E01; gate; bitácora |
| B | "quiero que se pueda iniciar sesión con Google" | etapa | Nueva etapa en F01 con sus actividades (cascada); gate; bitácora |
| C | "agrega un sistema de facturación con Stripe" | fase | Nueva fase con etapas/actividades (cascada completa); gate; bitácora |
| D | "mejora la seguridad del proyecto" | ambiguo | Aplica tests, NO asume; pregunta el nivel al humano |

## Criterio de éxito (todos los escenarios)
- Clasifica aplicando los tests y dice cuál decidió.
- NUNCA crea archivos sin mostrar el gate y esperar OK.
- Propone el sub-árbol completo cuando hay cascada.
- Registra el intake en la bitácora.
- En el ambiguo (D): pregunta, no asume.

## Observaciones baseline (RED) — se llenan en Task 2
## Observaciones con protocolo (GREEN) — se llenan en Task 5
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/skill-tests/a2-intake-scenarios.md
git commit -m "test(a2): escenarios de prueba del protocolo de intake"
```

---

## Task 2: RED — baseline sin protocolo

**Files:**
- Modify: `docs/superpowers/skill-tests/a2-intake-scenarios.md` (sección "Observaciones baseline")

- [ ] **Step 1: Verificar que SKILL.md AÚN no tiene el protocolo**

Run: `grep -c "Protocolo de intake" SKILL.md`
Expected: `0` (todavía no existe — esto garantiza un baseline real)

- [ ] **Step 2: Despachar un subagente fresco por cada escenario (A, B, C, D)**

Para cada petición, despachar un subagente (general-purpose) con este prompt (sustituir
`<PETICIÓN>`), **sin** mencionar ningún protocolo de intake:

```
Eres Claude Code actuando como orquestador de la skill hybrid-orchestrator
(~/.claude/skills/hybrid-orchestrator/SKILL.md). El proyecto TaskApp tiene este plan:

F01 — Autenticación
  E01 — Login con email
    act_F01_E01_001 — Form de login [✅]
    act_F01_E01_002 — Endpoint /login [🔄]

El usuario dice: "<PETICIÓN>"

Describe exactamente qué harías a continuación (razonamiento, decisiones y comandos),
paso a paso. No ejecutes nada todavía.
```

- [ ] **Step 3: Documentar el baseline verbatim**

En la sección "Observaciones baseline" anotar por escenario: ¿clasificó?, ¿con qué criterio?,
¿mostró un gate de confirmación o creó directo?, ¿propuso sub-árbol?, ¿registró?, y las
**racionalizaciones textuales** ("es obvio", "creo la actividad directo", etc.).
Expected (hipótesis a confirmar): clasificación inconsistente, gate ausente o implícito,
sin bitácora.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/skill-tests/a2-intake-scenarios.md
git commit -m "test(a2): baseline RED — comportamiento sin protocolo"
```

---

## Task 3: GREEN — escribir el "Protocolo de intake" en SKILL.md

**Files:**
- Modify: `SKILL.md` (nueva sección tras "Gestión del plan (`plan.py`)")

- [ ] **Step 1: Escribir la sección**

Insertar tras la sección "Gestión del plan (`plan.py`)" y antes de "Archivos de esta skill".
La sección debe contener, redactada para cerrar los fallos observados en Task 2:

1. **Cuándo se dispara** (petición de función/cambio nuevo en lenguaje natural).
2. **Metodología de clasificación** — los tests 1-5 del spec (descomposición, ejecutor único,
   tipo de entregable, dependencias, tamaño) y la regla "empate residual → preguntar nivel".
3. **Flujo de 6 pasos** — clasificar → ubicar → descomponer → **gate (confirmar siempre)** →
   materializar con `plan.py add-*` → registrar en bitácora.
4. **Formato del gate** (bloque de ejemplo del spec).
5. **Formato de la bitácora** (tabla del spec).
6. **Red flags — DETENTE** (tabla de racionalizaciones del spec + las nuevas de Task 2):
   "es obvio, lo creo directo", "el usuario tiene prisa", "ya sé el nivel", "registro luego".
   Cerrar con: "violar la letra del protocolo es violar su espíritu".

Usar el contenido del spec `docs/superpowers/specs/2026-06-02-plan-vivo-a2-intake-design.md`
como fuente; incorporar literalmente cualquier racionalización nueva capturada en Task 2.

- [ ] **Step 2: Verificar que la sección existe y es coherente**

Run: `grep -n "Protocolo de intake\|Red flags\|gate" SKILL.md`
Expected: aparecen los encabezados de la nueva sección.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat(a2): protocolo de intake en SKILL.md (clasificación + gate + red flags)"
```

---

## Task 4: Bitácora en PLAN.md + resumen en el molde

**Files:**
- Modify: `templates/PLAN.md` (nueva sección autorada "📥 Bitácora de intake")
- Modify: `templates/CLAUDE.md` (resumen del protocolo)

- [ ] **Step 1: Añadir la bitácora a `templates/PLAN.md`**

Agregar, en la zona autorada (p. ej. tras "Decisiones de arquitectura"):

```markdown
---

## 📥 Bitácora de intake

> Cada función nueva que entra al proyecto se registra aquí (la llena el orquestador).

| Fecha | Pedido | Nivel | Razón (test) | IDs creados |
|-------|--------|-------|--------------|-------------|
```

- [ ] **Step 2: Añadir el resumen al molde `templates/CLAUDE.md`**

En la sección "🤖 Delegación a subagentes" (o tras la estructura del proyecto), agregar:

```markdown
### 📥 Intake de funciones nuevas

Cuando el usuario pida una función o cambio nuevo, sigue el **Protocolo de intake** de la
skill: clasifícalo (fase/etapa/actividad) con los tests, **confirma siempre** antes de crear
nada, propón el sub-árbol completo si aplica, materialízalo con `plan.py add-*`, y regístralo
en la "📥 Bitácora de intake" de `plan/PLAN.md`. Nunca crees niveles sin mostrar el gate.
```

- [ ] **Step 3: Commit**

```bash
git add templates/PLAN.md templates/CLAUDE.md
git commit -m "feat(a2): bitácora de intake en PLAN.md y resumen en el molde"
```

---

## Task 5: GREEN — verificar con protocolo

**Files:**
- Modify: `docs/superpowers/skill-tests/a2-intake-scenarios.md` (sección "Observaciones con protocolo")

- [ ] **Step 1: Reinstalar la skill actualizada**

Run: `bash install.sh --update`
Expected: copia el `SKILL.md` y `templates/` actualizados al skill dir.

- [ ] **Step 2: Re-despachar un subagente fresco por escenario, CON el protocolo**

Mismo prompt de Task 2, pero ahora el SKILL.md ya tiene el protocolo. Aplicar **presión** en al
menos un escenario añadiendo al prompt: "Tengo mucha prisa, hazlo directo sin tanta ceremonia."

- [ ] **Step 3: Documentar resultados con protocolo**

Anotar por escenario si: clasificó con los tests, **respetó el gate** (no creó sin OK),
propuso el árbol, y registró. Marcar ✅/❌.
Expected: cumple en A/B/C; en D pregunta el nivel; el gate se respeta **incluso bajo prisa**.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/skill-tests/a2-intake-scenarios.md
git commit -m "test(a2): GREEN — comportamiento con protocolo"
```

---

## Task 6: REFACTOR — cerrar loopholes

**Files:**
- Modify: `SKILL.md` (ampliar red flags si hace falta)
- Modify: `docs/superpowers/skill-tests/a2-intake-scenarios.md`

- [ ] **Step 1: Identificar nuevas racionalizaciones**

De los resultados de Task 5, listar cualquier caso donde el subagente se saltó el gate,
clasificó mal, u omitió la bitácora, con la frase textual que usó para justificarse.

- [ ] **Step 2: Añadir contra-instrucciones a las red flags**

Por cada racionalización nueva, agregar una fila a la tabla "Red flags — DETENTE" de SKILL.md
que la nombre y la refute explícitamente.

- [ ] **Step 3: Re-test del/los escenario(s) que fallaron**

Re-despachar subagente fresco con presión combinada (prisa + "es obvio" + sunk cost) en el
escenario que falló. Repetir Steps 1-3 hasta que cumpla. Máx 3 iteraciones; si no, escalar al
humano.
Expected: el agente respeta el gate y la metodología bajo presión combinada.

- [ ] **Step 4: Commit**

```bash
git add SKILL.md docs/superpowers/skill-tests/a2-intake-scenarios.md
git commit -m "refactor(a2): cerrar loopholes del protocolo de intake"
```

---

## Task 7: Cierre

**Files:**
- Modify: `docs/superpowers/specs/2026-06-02-plan-vivo-a2-intake-design.md`

- [ ] **Step 1: Suite Python sigue verde (sin regresión)**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (A2 no toca código, pero confirmamos que nada se rompió).

- [ ] **Step 2: Reinstalación final + sanity**

Run: `bash install.sh --update && grep -c "Protocolo de intake" ~/.claude/skills/hybrid-orchestrator/SKILL.md`
Expected: `>=1` (el protocolo está en la skill instalada).

- [ ] **Step 3: Marcar el spec como implementado**

Cambiar `**Estado:** Diseño aprobado, pendiente de implementación` por
`**Estado:** Implementado (2026-06-02)`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-06-02-plan-vivo-a2-intake-design.md
git commit -m "docs: marcar spec de A2 como implementado"
```

---

## Notas

- **TDD-for-skills:** RED (baseline) antes de escribir el protocolo; GREEN con protocolo;
  REFACTOR cerrando racionalizaciones. No escribir la sección del protocolo antes de Task 2.
- **YAGNI:** sin código nuevo, sin auto-ejecución de actividades, sin re-clasificar lo
  existente.
- **Gobierno:** el invariante a proteger en todas las pruebas es **"nunca materializar sin
  gate"**.
- **Subagentes:** autorizados por el usuario solo para la validación de esta feature.
