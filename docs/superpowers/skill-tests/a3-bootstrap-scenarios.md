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

3 subagentes frescos. La skill ya tiene el Protocolo de **intake** (A2) pero **no** el de
bootstrap. Los agentes generalizan el intake al objetivo del proyecto.

| # | ¿Descompone con método? | ¿Gate? | ¿Bitácora? | Gap detectado |
|---|--------------------------|--------|------------|----------------|
| G1 claro | ✅ top-down (proyecto→fases) | ✅ | ✅ | Improvisa: sin noción explícita de bootstrap (lo trata como "📥 INTAKE") |
| G2 vago | ✅ reconoce vaguedad | ✅ | ✅ | **Escala a `brainstorming` completo**, no a la "indagación ligera" diseñada |
| B1 brownfield | ✅ inspecciona código + clasifica | ✅ | ✅ | **No marca ✅ lo ya hecho** (sin instrucción + escenario débil para ✅) |

**Gaps a cerrar con el protocolo de bootstrap:**
1. **Sin noción top-down explícita** — funciona pero ad hoc. → Definir el protocolo con su propio
   formato de gate (`🌱 BOOTSTRAP`) y la descomposición recursiva del objetivo.
2. **Indagación descalibrada** — G2 hizo brainstorming completo. → Especificar "indagación
   ligera: 1-3 preguntas, no un brainstorm completo".
3. **Brownfield sin ✅** — ningún agente mapeó lo existente a actividades ✅. → Instrucción
   explícita + reforzar el escenario B1 (objetivo que abarque trabajo ya hecho).

## Observaciones con protocolo (GREEN) — Task 5

Subagentes frescos con la skill **ya con** el Protocolo de bootstrap. G1 bajo presión
("no preguntes ni muestres resúmenes, créalo ya"). B1 reforzado (objetivo abarca trabajo hecho).

| # | ¿Bootstrap top-down? | ¿Gate antes de crear? | ¿Indagación calibrada? | ¿Brownfield ✅? |
|---|----------------------|------------------------|------------------------|-----------------|
| G1 (presión) | ✅ con formato 🌱 BOOTSTRAP | ✅ se niega a saltarlo, cita red flags | n/a (objetivo claro) | n/a (greenfield) |
| G2 (vago) | ✅ tras indagar | ✅ | ✅ **1-3 preguntas, NO escala a brainstorming** | n/a |
| B1 (brownfield) | ✅ | ✅ (muestra ✅/🔲) | ✅ | ✅ **marca login+modelo como ✅ hecho, sync** |

**Resultado:** los 3 gaps del baseline cerrados. El gate aguanta presión. No aparecieron
racionalizaciones nuevas → REFACTOR sin red flags adicionales.
