# Feature A3 — Protocolo de bootstrap (generación inicial del plan)

**Fecha:** 2026-06-02
**Estado:** Diseño aprobado, pendiente de implementación
**Skill:** hybrid-orchestrator
**Contexto:** Tercera y última pieza de Feature A ("plan vivo"). Se apoya en A1 (`scripts/plan.py`)
y A2 (protocolo de intake: tests de clasificación, gate, bitácora), ambos ya implementados.

---

## Problema

`init-hybrid` prepara el entorno (copia `CLAUDE.md`/`PLAN.md`, escanea con Gemini, corre
`claude /init`) pero **no genera la estructura del plan**: un proyecto arranca con un
`plan/PLAN.md` vacío y sin fases/etapas/actividades. La descomposición inicial del objetivo
queda improvisada y sin gobierno.

## Objetivo

Un **protocolo de bootstrap** documentado: al iniciar un proyecto hybrid cuyo plan aún no
tiene fases, el orquestador descompone el objetivo **top-down** en fases → etapas →
actividades (reusando los tests de A2), lo confirma en un gate, y lo materializa con
`plan.py`. Cubre proyectos **nuevos** (greenfield) y **existentes** (brownfield, marcando ✅
lo ya hecho).

**Naturaleza:** documentación (comportamiento del orquestador) + ajuste menor a `init-hybrid`.
**Sin código nuevo** — reusa `plan.py` de A1. Fuera de alcance (YAGNI): auto-ejecución de las
actividades creadas, generación headless sin gate, re-bootstrap de proyectos ya planeados.

---

## Dónde vive

- `SKILL.md` — nueva sección **"Protocolo de bootstrap"** (descomposición top-down inicial).
  Reusa los tests de clasificación, el gate y la bitácora del Protocolo de intake (A2).
- `~/.zshrc` (`init-hybrid`) — ajuste de mensajería para apuntar al bootstrap; opcionalmente
  dejar `plan/PLAN.md` consistente con `plan.py sync`.
- `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md` — escenarios de validación.

> Nota: como la skill instalada vive en `~/.claude/skills/`, `init-hybrid` no puede leerse
> a sí misma; los cambios de `~/.zshrc` se editan directo (con backup) y no entran al repo.
> El repo documenta el comportamiento esperado de `init-hybrid` en el README/SKILL si aplica.

---

## Disparador

El orquestador, al iniciar sesión en un proyecto hybrid cuyo plan **no tiene fases aún**, ofrece
hacer el bootstrap. Detección: `plan.py status` responde "No hay plan aún" (o `plan/` no tiene
carpetas `fase_*`).

---

## El protocolo (flujo del orquestador)

1. **Leer contexto.** Objetivo del proyecto (de `CLAUDE.md` / del usuario) + el `SCAN_RESULT`
   que `init-hybrid` ya inyectó en `CLAUDE.md` (stack, archivos clave, TIPO nuevo|existente).
2. **Indagación ligera.** Si el objetivo es vago, hacer **1-3 preguntas clave** (alcance/MVP,
   must-haves, restricciones de stack) antes de descomponer. No es un brainstorm completo.
3. **Descomponer top-down.** Objetivo → fases (hitos mayores) → etapas (sub-objetivos) →
   actividades (unidades ejecutables), aplicando los tests de clasificación de A2 de lo grande
   a lo atómico (una actividad = un checklist atómico, un backend, una corrida). Asignar
   `run-agent` sugerido por actividad según la tabla de backends.
   - **Brownfield:** mapear lo que YA existe (según el SCAN_RESULT y/o lectura del repo) a
     actividades marcadas **✅ hecho**, para que el estado derivado refleje el avance real.
4. **Gate — confirmar el árbol completo.** Presentar el árbol propuesto (fases/etapas/
   actividades con backends; en brownfield, qué queda ✅) y esperar OK explícito. Permitir
   "ajustar nivel / ajustar desglose". **No crear nada antes del OK.**
5. **Materializar.** Ejecutar la cadena `plan.py add-phase/add-stage/add-activity` (auto-sync);
   rellenar el contenido autorado (objetivo/criterios) de cada nivel; en brownfield, fijar el
   `status: ✅ hecho` de las actividades ya hechas y correr `plan.py sync`.
6. **Registrar.** Anexar una entrada inicial a la "📥 Bitácora de intake" de `PLAN.md`:
   `| fecha | bootstrap inicial | — | objetivo | N fases / M actividades |`.

### Formato del gate (ejemplo)

```
🌱 BOOTSTRAP — TaskApp
Objetivo: app de tareas con autenticación y recordatorios
Tipo: nuevo (greenfield)
Plan propuesto:
  F01 — Autenticación
    E01 — Login con email
      act_F01_E01_001 — Form de login        [cursor-agent]
      act_F01_E01_002 — Endpoint /login       [gemini]
  F02 — Gestión de tareas
    E01 — CRUD de tareas
      act_F02_E01_001 — Modelo + endpoints     [gemini]
¿Confirmas?  (sí / ajustar)
```

En brownfield, las actividades ya hechas se muestran con `✅` en el árbol propuesto.

---

## Relación con A2

El bootstrap es **A2 aplicado top-down al objetivo completo en t=0**. Comparte: los tests de
clasificación, el principio del gate obligatorio, y la bitácora. Lo nuevo de A3: la
descomposición recursiva de un objetivo grande, el marcado ✅ en brownfield, la indagación
ligera, y el disparador "plan vacío al iniciar". La sección de SKILL.md referencia el
Protocolo de intake en lugar de duplicar los tests.

---

## init-hybrid (cambios mínimos)

- Tras el `claude /init`, el mensaje final debe indicar: *"Inicia `claude` y pídele: 'haz el
  bootstrap del plan'"*.
- Opcional: tras copiar `plan/PLAN.md`, dejarlo consistente ejecutando
  `python3 ~/.claude/skills/hybrid-orchestrator/scripts/plan.py --cwd . sync` (regenera la zona
  auto vacía sin romper nada).
- Conserva el scan de Gemini: su `SCAN_RESULT` es **input** del bootstrap.

---

## Red flags — DETENTE (añadir a la sección de bootstrap)

| Si piensas… | Realidad |
|-------------|----------|
| "Genero el plan y empiezo a ejecutar de una" | Bootstrap solo crea el plan. Ejecutar es otro paso, con su confirmación. |
| "El objetivo es claro, materializo sin gate" | El árbol completo pasa por el gate, igual que en intake. |
| "Es brownfield pero marco todo 🔲" | Mapea lo ya hecho a ✅ para que el estado derivado sea real. |
| "El objetivo es vago, asumo el alcance" | Indaga 1-3 preguntas antes de descomponer; no inventes el alcance. |

---

## Validación (skill-testing con subagentes)

Como A2 (autorizado por el usuario): RED (baseline sin protocolo) → GREEN (con protocolo) →
REFACTOR (cerrar loopholes). Escenarios mínimos:

1. **Greenfield, objetivo claro** — verificar descomposición coherente top-down + gate + bitácora.
2. **Greenfield, objetivo vago** ("hazme una app") — verificar que **indaga** antes de descomponer.
3. **Brownfield** (repo con código existente sin plan) — verificar que marca ✅ lo ya hecho y
   respeta el gate.

**Criterio de éxito:** descompone con método, **nunca materializa sin gate**, indaga cuando el
objetivo es vago, marca ✅ en brownfield, y registra el bootstrap.

---

## Archivos afectados

- `SKILL.md` — sección "Protocolo de bootstrap".
- `~/.zshrc` (`init-hybrid`) — mensajería + sync opcional (fuera del repo; con backup).
- `docs/superpowers/skill-tests/a3-bootstrap-scenarios.md` — escenarios.

Sin código nuevo. La instalación ya copia `SKILL.md` y `templates/`.

---

## Entregable de A3

Al arrancar un proyecto (nuevo o existente), el orquestador genera la estructura inicial del
plan con contenido — descompuesta con método, confirmada en un gate y materializada con
`plan.py` — completando Feature A: un plan que nace poblado (A3), se mantiene sincronizado (A1)
y crece de forma gobernada ante cada nueva función (A2).
