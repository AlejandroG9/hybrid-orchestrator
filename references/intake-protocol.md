# Protocolo de intake (funciones nuevas)

Referencia detallada del intake. El trigger, el invariante del gate y las red flags están
inline en `SKILL.md`; aquí está el método completo.

Cuando el usuario pide una **función o cambio nuevo** en lenguaje natural ("agrega X", "necesito Y", "quiero que el proyecto haga Z"), sigue este protocolo para incorporarlo al plan vivo. No improvises ni clasifiques "por intuición".

## Paso 1 — Clasificar con método

Decide el nivel (fase / etapa / actividad) aplicando estos **tests en orden** (criterio = alcance de lo pedido):

1. **Test de descomposición (principal).** Escribe los criterios de aceptación de lo pedido y cuenta sus sub-unidades naturales:
   - atómico (un solo checklist que un subagente cumple en una corrida) → **actividad**
   - se rompe en varias actividades → **etapa**
   - se rompe en varias etapas → **fase**
2. **Test del ejecutor único.** ¿Un backend lo termina en una corrida? → actividad. ¿Varias corridas coordinadas? → sube de nivel.
3. **Test del tipo de entregable.** Artefacto concreto (archivo/función/endpoint) = actividad · capacidad parcial probable = etapa · subsistema/hito = fase.
4. **Test de dependencias.** Si tiene prerrequisitos sobre otras fases o bloquea su inicio → nivel fase.
5. **Tamaño (estilo 8/80).** Nº de sub-unidades: 0 → actividad; un puñado de actividades → etapa; múltiples etapas → fase.

**Di siempre qué test decidió la clasificación.** Si tras los tests sigue empatado entre dos niveles → **pregunta el nivel al humano; no asumas.**

## Paso 2 — Ubicar y descomponer

- Determina el padre existente al que se engancha. Si el padre no existe, identifica qué padres hay que crear (cascada).
- Si abarca varios niveles, arma el **sub-árbol completo** (fase → etapas → actividades) con título, objetivo y `run-agent` sugerido por actividad (según la tabla de backends).

## Paso 3 — Gate: confirma SIEMPRE antes de crear nada

Antes de tocar **un solo archivo**, muestra esto al humano y espera OK explícito:

```
📥 INTAKE — "<lo que pidió el usuario>"
Clasificación: <NIVEL>  (<qué test lo decidió>)
Ubicación: <padre existente, o "nueva fase/etapa">
Voy a crear:
  E0X — <título>
    act_..._001 — <título>   [<backend>]
    act_..._002 — <título>   [<backend>]
¿Confirmas?  (sí / ajustar nivel / ajustar desglose)
```

## Paso 4 — Materializar y registrar

Solo tras el OK:
1. Ejecuta la cadena `plan.py add-phase/add-stage/add-activity` (auto-sync).
2. Rellena el contenido autorado (objetivo/criterios) de cada nivel creado.
3. **Registra el intake** anexando una fila a la "📥 Bitácora de intake" de `plan/PLAN.md`:
   `| fecha | lo pedido | nivel | razón (test) | IDs creados |`.

## Red flags — DETENTE

| Si piensas… | Realidad |
|-------------|----------|
| "Es obvio, creo la actividad directo" | El gate es obligatorio **incluso para una actividad**. Confirma antes de crear. |
| "Materializo y confirmo antes de delegar" | Tarde. El gate va **antes de `plan.py add-*`**, no antes de ejecutar. |
| "El usuario tiene prisa, me salto la confirmación" | La prisa no elimina el gate. Muestra el plan y espera OK. |
| "Ya sé el nivel, no aplico los tests" | Aplica los tests y di cuál decidió. La intuición no es reproducible. |
| "Está ambiguo pero asumo el nivel mayor" | Empate residual → **pregunta**, no asumas. |
| "Creo todo y registro la bitácora luego (o no)" | La bitácora es obligatoria, en el mismo paso. |

**Violar la letra del protocolo es violar su espíritu.**
