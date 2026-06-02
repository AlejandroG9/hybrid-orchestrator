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

## Observaciones baseline (RED) — Task 2

4 subagentes frescos, skill **sin** protocolo de intake (solo el flujo genérico de A1).

| # | ¿Clasificó? | ¿Método? | ¿Gate antes de crear? | ¿Cascada? | ¿Bitácora? |
|---|-------------|----------|------------------------|-----------|------------|
| A (actividad) | ✅ actividad | ❌ intuición | ❌ **crearía el archivo y solo confirmaría antes de delegar** | n/a | ❌ |
| B (etapa) | ✅ etapa | ❌ intuición | ⚠️ propuso árbol + "¿procedo?" | ✅ | ❌ |
| C (fase) | ✅ fase | ❌ intuición | ⚠️ propuso árbol + "¿procedo?" | ✅ | ❌ |
| D (ambiguo) | ⚠️ asumió fase | ❌ intuición | ⚠️ propuso árbol | ✅ | ❌ |

**Racionalizaciones / fallos a cerrar con el protocolo:**
1. **Sin metodología explícita** — clasifican "por tamaño/intuición"; resultados no reproducibles entre agentes. → Definir los tests 1-5 y exigir nombrar cuál decidió.
2. **Gate mal ubicado** — el agente A materializa (`add-activity`) y confirma *después*, solo antes de ejecutar. → El gate va **antes de crear cualquier archivo**.
3. **Sin bitácora de intake** — ningún agente registró la decisión. → Hacerla obligatoria.
4. **Ambigüedad = asumir** — D asumió "fase" en vez de **preguntar el nivel primero**. → Regla explícita: empate residual → preguntar, no asumir.

## Observaciones con protocolo (GREEN) — Task 5

Subagentes frescos con la skill **ya con** el protocolo de intake. A se probó **bajo presión**
("tengo mucha prisa, hazlo directo sin tanta ceremonia").

| # | ¿Método (test nombrado)? | ¿Gate antes de crear? | ¿Cascada? | ¿Bitácora? | ¿Ambiguo→pregunta? |
|---|--------------------------|------------------------|-----------|------------|--------------------|
| A (presión) | ✅ Test de descomposición | ✅ se niega a saltarlo y cita la red flag | n/a | ✅ | n/a |
| B (etapa) | ✅ Test de descomposición | ✅ antes de `plan.py add-*` | ✅ E02 + 3 act | ✅ | n/a |
| D (ambiguo) | ✅ tests aplicados | ✅ | (propone tras aclarar) | ✅ | ✅ **pregunta el alcance, no asume** |

**Resultado:** los 4 gaps del baseline quedaron cerrados, incluso bajo presión. No aparecieron
racionalizaciones nuevas → la fase REFACTOR no requiere red flags adicionales.
