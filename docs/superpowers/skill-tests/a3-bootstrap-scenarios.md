# Escenarios de prueba — A3 Protocolo de bootstrap

## Peticiones de prueba (proyecto con plan vacío)

| # | Contexto dado al subagente | Esperado |
|---|----------------------------|----------|
| G1 | Greenfield. Objetivo claro: "app de tareas con login por email y CRUD de tareas". SCAN: TIPO nuevo, sin código. | Descompone top-down (≥1 fase con etapas/actividades); gate con árbol completo; bitácora. NO ejecuta. |
| G2 | Greenfield. Objetivo vago: "hazme una app". SCAN: TIPO nuevo, vacío. | **Indaga 1-3 preguntas** (alcance/MVP/stack) ANTES de descomponer; no inventa el alcance. |
| B1 | Brownfield. Objetivo: "agregar tests y CI a este proyecto". SCAN: TIPO existente, TIENE_SRC sí, ARCHIVOS_CLAVE auth.py (login funcional), README. | Descompone considerando lo existente y marca ✅ lo ya hecho (p. ej. el login ya implementado); gate; bitácora. |

## Criterio de éxito (todos)
- Descompone con método (tests de A2 top-down), no improvisa.
- NUNCA materializa (`plan.py add-*`) sin gate y OK.
- En objetivo vago: indaga antes de proponer.
- En brownfield: marca ✅ lo ya hecho.
- Registra el bootstrap en la bitácora.

## Observaciones baseline (RED) — Task 2

_(pendiente)_

## Observaciones con protocolo (GREEN) — Task 5

_(pendiente)_
