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

_(pendiente)_

## Observaciones con protocolo (GREEN) — se llenan en Task 5

_(pendiente)_
