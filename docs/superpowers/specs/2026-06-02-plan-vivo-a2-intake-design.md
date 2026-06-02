# Feature A2 — Protocolo de intake (clasificación + gobierno)

**Fecha:** 2026-06-02
**Estado:** Implementado (2026-06-02)
**Skill:** hybrid-orchestrator
**Contexto:** Segunda pieza de Feature A ("plan vivo"). Se apoya en A1 (`scripts/plan.py`,
ya implementado). A3 (bootstrap en init) queda para después.

---

## Problema

A1 dio la mecánica (`plan.py` crea niveles y deriva estado). Falta el **comportamiento**:
cuando el usuario pide una función nueva durante una sesión, el orquestador debe decidir su
**nivel** (fase/etapa/actividad), confirmarlo (gobierno) y materializarlo con `plan.py`,
manteniendo el plan permanentemente actualizado. Hoy eso queda al criterio improvisado del
agente, sin método ni gate.

## Objetivo

Un **protocolo de intake** documentado que el orquestador siga de forma consistente:
clasificar con un método explícito, confirmar siempre antes de materializar, proponer el
sub-árbol completo cuando aplica, y registrar la decisión para auditoría.

**Naturaleza:** documentación (comportamiento del orquestador). **Sin código nuevo** — usa
`plan.py` de A1. Fuera de alcance (YAGNI): auto-ejecución de las actividades creadas (eso es
`run_subagent.py`), re-clasificación de lo existente, cualquier script nuevo.

---

## Dónde vive

- `SKILL.md` — nueva sección **"Protocolo de intake"** (el procedimiento completo).
- `templates/CLAUDE.md` — resumen del protocolo + apuntador, para sesiones por proyecto.
- `templates/PLAN.md` — nueva sección autorada **"📥 Bitácora de intake"**.

---

## Metodología de clasificación

Criterio = **alcance de lo pedido**. Definiciones operativas:

- **Actividad** — unidad que un subagente ejecuta en una corrida (un endpoint, función,
  módulo). Cabe en una etapa existente.
- **Etapa** — sub-objetivo coherente que agrupa varias actividades; capacidad parcial dentro
  de una fase.
- **Fase** — capacidad/hito mayor; agrupa varias etapas; suele tener dependencias con otras
  fases.

**Tests discriminantes (en orden), tomados de la práctica de WBS:**

1. **Test de descomposición (principal).** Escribir los criterios de aceptación de lo pedido
   y contar sub-unidades naturales:
   - atómico (un solo checklist) → **actividad**
   - sub-unidades = actividades → **etapa**
   - sub-unidades = etapas → **fase**
2. **Test del ejecutor único.** ¿Un backend lo termina en una corrida? → actividad. ¿Varias
   corridas coordinadas? → sube de nivel.
3. **Test del tipo de entregable.** Artefacto concreto = actividad · capacidad parcial
   probable = etapa · subsistema/hito = fase.
4. **Test de dependencias.** Si tiene prerrequisitos sobre otras fases o bloquea su inicio →
   nivel fase.
5. **Heurística de tamaño (estilo 8/80).** Número de sub-unidades: 0 → actividad; un puñado
   de actividades → etapa; múltiples etapas → fase.

**Procedimiento ante ambigüedad:** aplicar tests 1-3; si sigue en frontera, usar 4 (escala a
fase) y el sub-test de ejecutor único (colapsa a actividad). **Si AÚN queda empate →
preguntar el nivel al humano** (no asumir).

---

## El protocolo (flujo del orquestador)

Disparador: el usuario pide una función/cambio nuevo en lenguaje natural ("agrega X",
"necesito Y", "quiero que el proyecto haga Z") durante una sesión hybrid.

1. **Clasificar** con la metodología anterior. Empate residual → preguntar nivel.
2. **Ubicar** — determinar el padre existente al que se engancha; si falta, identificar qué
   padres hay que crear (cascada).
3. **Descomponer** — si abarca varios niveles, armar el **sub-árbol completo** (fase →
   etapas → actividades) con título, objetivo y `run-agent` sugerido por actividad (según la
   tabla de backends de la skill).
4. **Gate — confirmar SIEMPRE.** Mostrar al humano y esperar OK explícito antes de tocar
   archivos.
5. **Materializar** — al aprobar: ejecutar la cadena de `plan.py add-phase/add-stage/
   add-activity` (auto-sync) y rellenar el contenido autorado (objetivos/criterios) de cada
   nivel creado.
6. **Registrar** — anexar una línea a la "📥 Bitácora de intake" de PLAN.md.

### Formato del gate

```
📥 INTAKE — "agrega autenticación con Google"
Clasificación: ETAPA  (test 1: se descompone en 3 actividades; test 2: varias corridas)
Ubicación: dentro de F01 — Autenticación (existente)
Voy a crear:
  E02 — Login con Google
    act_F01_E02_001 — Configurar OAuth client   [gemini]
    act_F01_E02_002 — Endpoint /auth/google     [gemini]
    act_F01_E02_003 — Tests del flujo           [codex]
¿Confirmas?  (sí / ajustar nivel / ajustar desglose)
```

### Formato de la bitácora (sección autorada de PLAN.md)

```markdown
## 📥 Bitácora de intake

| Fecha | Pedido | Nivel | Razón (test) | IDs creados |
|-------|--------|-------|--------------|-------------|
| 2026-06-02 | auth con Google | etapa | test 1: 3 actividades | F01_E02 |
```

---

## Reglas de gobierno (red flags para el orquestador)

El riesgo central es que el agente **se salte el gate** bajo presión. El protocolo incluye
una lista de "red flags — DETENTE":

- "Es obvio, lo creo directo" → No. El gate es obligatorio incluso para una actividad.
- "El usuario tiene prisa, me salto la confirmación" → No. Mostrar y esperar OK.
- "Ya sé el nivel, no aplico los tests" → Aplica los tests; documenta cuál decidió.
- "Materializo y luego registro… o no" → La bitácora es obligatoria, no opcional.

**Principio:** violar la letra del protocolo es violar su espíritu.

---

## Validación (skill-testing con subagentes)

Se valida como recomienda `writing-skills` (TDD-for-skills), con autorización del usuario para
abrir subagentes:

- **RED (baseline):** dar a un subagente fresco un proyecto con un plan existente + una
  petición ambigua, **sin** el protocolo. Documentar verbatim: ¿clasifica?, ¿se salta el
  gate?, ¿inventa estructura?, ¿registra?
- **GREEN:** mismo escenario **con** el protocolo en la skill. Verificar que aplica los tests,
  respeta el gate, propone el árbol y registra.
- **REFACTOR:** capturar nuevas racionalizaciones y cerrar loopholes (ampliar red flags),
  re-testear hasta que cumpla bajo presión (prisa + sunk cost + "es obvio").

Escenarios mínimos: una petición que es **actividad** (cabe en etapa existente), una que es
**etapa** (cascada parcial), una que es **fase** (cascada completa), y una **ambigua**
(verificar que pregunta el nivel).

**Criterio de éxito:** bajo presión combinada, el agente clasifica con los tests, **nunca**
materializa sin gate, y registra el intake.

---

## Archivos afectados

- `SKILL.md` — sección "Protocolo de intake" (metodología + flujo + formatos + red flags).
- `templates/CLAUDE.md` — resumen del protocolo para sesiones por proyecto.
- `templates/PLAN.md` — sección autorada "📥 Bitácora de intake".

Sin código nuevo. La instalación ya copia `SKILL.md` y `templates/` (no requiere cambios en
`install.sh`).

---

## Entregable de A2

El orquestador, ante una petición nueva, clasifica con método explícito, confirma siempre,
propone y materializa el sub-árbol con `plan.py`, y registra la decisión — manteniendo el plan
vivo con gobierno. Deja listo el terreno para A3 (bootstrap en init), que reusa este protocolo
para poblar el plan inicial.
