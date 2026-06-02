# P1+P2 — Reestructura de SKILL.md (secciones canónicas + progressive disclosure)

**Fecha:** 2026-06-02
**Estado:** Implementado (2026-06-02)
**Skill:** hybrid-orchestrator
**Contexto:** Mejoras P1 (recortar/reestructurar) y P2 (progressive disclosure) detectadas al
comparar con la guía `writing-skills` de superpowers. P0 (frontmatter) ya está hecho.

---

## Problema

`SKILL.md` pesa **1806 palabras** (objetivo de superpowers: <500). El grueso son dos
secciones de protocolo: intake (540) y bootstrap (410). El archivo mezcla el "cuándo/cómo"
(que debe ser breve y escaneable) con referencia procedimental pesada, y se carga entero en
cada conversación. No usa progressive disclosure ni la estructura canónica recomendada.

## Objetivo

Reestructurar `SKILL.md` a las secciones canónicas y mover la **referencia pesada** a
`references/*.md` (se cargan bajo demanda), **manteniendo prominente el contenido de
disciplina** (triggers, invariante "gate antes de crear", red flags) para que el orquestador
no se salte los gates validados en A2/A3.

**Enfoque elegido:** híbrido — mecánica fuera, disciplina inline. Sin cambios de comportamiento;
es un refactor de documentación. Riesgo central: que mover los protocolos rompa la disciplina
→ se valida con skill-testing (subagentes).

---

## Diseño

### SKILL.md (objetivo ~600-700 palabras, estructura canónica)

1. **Frontmatter** (sin cambios: `name` + `description` "Use when…").
2. **Overview** — principio núcleo en 1-2 frases: orquestador/PM que delega la implementación a
   subagentes CLI y mantiene un plan vivo.
3. **When to Use** — fusiona "¿Qué hace?" + "Cuándo activar" + "Skills activas": triggers de
   activación + activación automática vía `CLAUDE.md`.
4. **Tu rol** — haces / no haces, condensado.
5. **Quick Reference** — tabla escaneable de comandos clave (`run_subagent.py` invoke + `--check`;
   `plan.py add-*/sync/status`) + lista compacta de backends.
6. **Intake (disciplina inline):** trigger + invariante **"confirma SIEMPRE en el gate antes de
   crear nada"** + tabla de red flags + puntero `**REQUIRED:** references/intake-protocol.md`.
7. **Bootstrap (disciplina inline):** trigger (plan vacío) + invariante + red flags + puntero
   `**REQUIRED:** references/bootstrap-protocol.md`.
8. **Archivos de esta skill** — árbol actualizado con `references/`.

### references/ (detalle pesado, carga bajo demanda)

- `references/subagents.md` — invocar subagentes, `--check`, disponibilidad y cadena de
  fallback, protocolo de reintento, **tabla completa de backends** (con cuándo usar cada uno).
- `references/plan-management.md` — `plan.py` (comandos, jerarquía de niveles, zonas
  `BEGIN:auto`/`END:auto`, estado derivado).
- `references/intake-protocol.md` — protocolo de intake completo: los 5 tests de clasificación,
  ubicar/descomponer, formato del gate `📥 INTAKE`, materializar, formato de la bitácora.
- `references/bootstrap-protocol.md` — protocolo de bootstrap completo: flujo de 6 pasos,
  indagación ligera, descomposición top-down, formato `🌱 BOOTSTRAP`, brownfield ✅.

### Reglas de cross-referencia (writing-skills)

- Usar `**REQUIRED:** references/x.md` (ruta relativa, marcador explícito).
- **No** usar `@references/...` (fuerza la carga inmediata y quema contexto).
- El contenido de disciplina (gate, red flags, "no asumas") queda **inline**; las referencias
  amplían con tests, formatos y pasos.

### Cambios de soporte

- **`install.sh`** — copiar también `references/` al skill dir (hoy copia `SKILL.md`,
  `scripts/`, `templates/`). Sin esto, las referencias no llegan a la skill instalada y los
  punteros apuntan a nada.
- **`README.md`** (opcional) — reflejar `references/` en el árbol de la skill si lo lista.

---

## Validación (skill-testing con subagentes)

El riesgo es que, al mover los protocolos a `references/`, el agente no cargue la referencia y
se salte el gate. Por eso, **después** del refactor:

1. Re-correr escenarios de presión de **intake** (p. ej. el de "es trivial, créalo ya") y de
   **bootstrap** (greenfield con presión + brownfield) con subagentes frescos sobre la skill
   reestructurada e instalada.
2. **Criterio de éxito:** el agente sigue clasificando con los tests, **respeta el gate antes de
   crear**, marca ✅ en brownfield y registra la bitácora — igual que antes del refactor.
3. Si algún escenario falla → mover ese invariante de vuelta inline (ajustar el híbrido) y
   re-validar.

Además: la suite Python (34 tests) debe seguir verde (el refactor no toca código).

---

## Archivos afectados

- `SKILL.md` — reescritura a estructura canónica + punteros.
- `references/subagents.md`, `references/plan-management.md`, `references/intake-protocol.md`,
  `references/bootstrap-protocol.md` — **nuevos** (contenido movido desde SKILL.md, sin perder
  nada).
- `install.sh` — copiar `references/`.
- `docs/superpowers/skill-tests/restructure-scenarios.md` — escenarios de re-validación.

---

## Resultado esperado

`SKILL.md` de ~1806 → ~650 palabras, con la disciplina (gates/red flags/triggers) intacta y
prominente y el detalle accesible bajo demanda — alineado con la guía `writing-skills` y sin
cambiar el comportamiento validado de intake/bootstrap.

### YAGNI (fuera)
P3 (TDD-for-skills del resto de la disciplina), reescritura de los protocolos en sí (solo se
mueven), cualquier cambio de comportamiento.
