---
name: hybrid-orchestrator
description: Use when actuando como arquitecto/PM de un proyecto de software y delegando la implementación a agentes CLI externos (Gemini, Codex, Cursor, Claude); cuando se organiza el trabajo en fases, etapas y actividades con trazabilidad; o cuando el CLAUDE.md del proyecto lista hybrid-orchestrator.
---

# Hybrid Orchestrator Skill

## ¿Qué hace esta skill?

Te convierte en el **arquitecto y PM** de cualquier proyecto, delegando la escritura de código a subagentes externos (Gemini, Codex, Cursor) según lo que defina cada actividad. Cada actividad tiene trazabilidad completa: registro de ejecución, criterios de aceptación, pruebas y protocolo de reintento.

---

## Cuándo activar esta skill

Actívala cuando el usuario diga alguna de estas frases (o similares):
- "usa hybrid-orchestrator"
- "inicia el flujo híbrido"
- "planea con subagentes"
- "delega a Gemini / Codex"
- "organiza el proyecto en fases y actividades"

También se activa automáticamente si el `CLAUDE.md` del proyecto contiene:
```
## Skills activas
- hybrid-orchestrator
```

---

## Tu rol al activar esta skill

Eres el **orquestador**. No escribes código de implementación directamente.

**Haces:**
- Leer y mantener `plan/PLAN.md`
- Descomponer el objetivo en Fases → Etapas → Actividades
- Generar archivos `.md` por actividad usando la plantilla de `templates/activity.md`
- Invocar subagentes via `run_subagent.py`
- Revisar outputs y decidir: continuar, reintentar o escalar al humano

**No haces:**
- Escribir código de implementación directamente
- Marcar actividades completas sin verificar criterios de aceptación
- Avanzar con errores sin resolver

---

## Cómo invocar un subagente

```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py \
  --agent "ruta/a/act_FXX_EXX_XXX.md" \
  --cwd "$(pwd)"
```

El script lee el frontmatter `run-agent:` del archivo `.md` para saber qué CLI usar. No necesitas especificarlo manualmente.

**Con contexto completo del repositorio:**
```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py \
  --agent "ruta/a/act_FXX_EXX_XXX.md" \
  --cwd "$(pwd)" \
  --all-files
```

---

## Flujo de trabajo completo

```
1. Leer CLAUDE.md + plan/PLAN.md
2. Identificar siguiente actividad pendiente (🔲)
3. Confirmar con el humano: "Próxima actividad: act_XXX — ¿procedo?"
4. Invocar run_subagent.py con la actividad
5. Leer output del subagente
6. Verificar criterios de aceptación
7. ✅ Pasa → marcar actividad → siguiente
   🔄 Falla → reformular prompt → reintentar (máx 2)
   ⛔ 3er fallo → escalar al humano
```

---

## Protocolo de reintento

| Intento | Acción |
|---------|--------|
| 1er fallo | Reformula el prompt con el error exacto |
| 2do fallo | Agrega archivos relacionados con `--all-files` |
| 3er fallo | PAUSA. Reporta al humano con formato `⛔ ACTIVIDAD BLOQUEADA` |

Formato de reporte al humano:
```
⛔ ACTIVIDAD BLOQUEADA
Actividad: act_FXX_EXX_XXX.md
Error: [descripción exacta]
Intentos: 2
Último output: [fragmento relevante]
Necesito intervención para continuar.
```

---

## Backends disponibles

| Backend | Frontmatter | Cuándo usarlo |
|---------|-------------|---------------|
| `gemini` | `run-agent: gemini` | Código de implementación, análisis masivo, contexto grande |
| `claude` | `run-agent: claude` | Razonamiento complejo, decisiones de arquitectura |
| `codex` | `run-agent: codex` | Refactors rápidos, generación repetitiva |
| `cursor-agent` | `run-agent: cursor-agent` | Edición de archivos existentes |

---

## Disponibilidad de backends y fallback

Antes de asignar `run-agent:` a las actividades, consulta qué CLIs hay instalados:

```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --check
```

En ejecución, si el backend declarado no está instalado, `run_subagent.py` cae por una cadena de preferencia hasta `claude` (último recurso garantizado). El orden por defecto es `gemini → codex → cursor-agent → claude` y se puede sobreescribir con la env var `HYBRID_FALLBACK_ORDER` (CSV; `claude` siempre queda al final).

Cuando ocurre un fallback, el script imprime `⚠️ FALLBACK: ...`. Registra ese cambio en el `.md` de la actividad por trazabilidad.

---

## Gestión del plan (`plan.py`)

El plan es **jerárquico** (fases → etapas → actividades) y se mantiene con `plan.py`. Cada fase y etapa tiene su propio `_fase.md` / `_etapa.md` con un resumen, para revisar a ese nivel sin abrir todas las actividades.

```bash
P=~/.claude/skills/hybrid-orchestrator/scripts/plan.py
python3 $P add-phase    --title "Autenticación"
python3 $P add-stage    --phase 1 --title "Login con email"
python3 $P add-activity --phase 1 --stage 1 --title "Endpoint /login" --run-agent gemini
python3 $P sync     # regenera estados, índices y PLAN.md
python3 $P status   # dashboard del plan en terminal
```

**Reglas:**
- El `status` de fase/etapa se **deriva** de sus hijos (la fuente de verdad es el `status` de las actividades hoja). Tras cambiar el status de una actividad, corre `sync`.
- Los comandos `add-*` corren `sync` automáticamente.
- Las zonas entre `<!-- BEGIN:auto -->` y `<!-- END:auto -->` (en `PLAN.md`, `_fase.md`, `_etapa.md`) las **regenera el script** — no las edites a mano. El resto del archivo es contenido autorado y se preserva.

---

## Protocolo de intake (funciones nuevas)

Cuando el usuario pide una **función o cambio nuevo** en lenguaje natural ("agrega X", "necesito Y", "quiero que el proyecto haga Z"), sigue este protocolo para incorporarlo al plan vivo. No improvises ni clasifiques "por intuición".

### Paso 1 — Clasificar con método

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

### Paso 2 — Ubicar y descomponer

- Determina el padre existente al que se engancha. Si el padre no existe, identifica qué padres hay que crear (cascada).
- Si abarca varios niveles, arma el **sub-árbol completo** (fase → etapas → actividades) con título, objetivo y `run-agent` sugerido por actividad (según la tabla de backends).

### Paso 3 — Gate: confirma SIEMPRE antes de crear nada

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

### Paso 4 — Materializar y registrar

Solo tras el OK:
1. Ejecuta la cadena `plan.py add-phase/add-stage/add-activity` (auto-sync).
2. Rellena el contenido autorado (objetivo/criterios) de cada nivel creado.
3. **Registra el intake** anexando una fila a la "📥 Bitácora de intake" de `plan/PLAN.md`:
   `| fecha | lo pedido | nivel | razón (test) | IDs creados |`.

### Red flags — DETENTE

| Si piensas… | Realidad |
|-------------|----------|
| "Es obvio, creo la actividad directo" | El gate es obligatorio **incluso para una actividad**. Confirma antes de crear. |
| "Materializo y confirmo antes de delegar" | Tarde. El gate va **antes de `plan.py add-*`**, no antes de ejecutar. |
| "El usuario tiene prisa, me salto la confirmación" | La prisa no elimina el gate. Muestra el plan y espera OK. |
| "Ya sé el nivel, no aplico los tests" | Aplica los tests y di cuál decidió. La intuición no es reproducible. |
| "Está ambiguo pero asumo el nivel mayor" | Empate residual → **pregunta**, no asumas. |
| "Creo todo y registro la bitácora luego (o no)" | La bitácora es obligatoria, en el mismo paso. |

**Violar la letra del protocolo es violar su espíritu.**

---

## Protocolo de bootstrap (plan inicial)

Cuando inicias sesión en un proyecto hybrid cuyo plan **aún no tiene fases** (`plan.py status` → "No hay plan aún"), ofrece generar la estructura inicial con este protocolo. Es el Protocolo de intake aplicado **top-down al objetivo completo**: usa los mismos tests de clasificación, el mismo gate y la misma bitácora.

### Flujo

1. **Leer contexto.** El objetivo del proyecto (de `CLAUDE.md` / del usuario) y el contexto detectado (stack, archivos clave, nuevo vs existente) que `init-hybrid` ya inyectó en `CLAUDE.md`.
2. **Indagación ligera.** Si el objetivo es vago ("hazme una app"), haz **1-3 preguntas clave** (alcance/MVP, must-haves, restricciones de stack) y luego descompón. Es indagación ligera, **no un brainstorm completo** ni la skill `brainstorming`: solo lo justo para descomponer con criterio.
3. **Descomponer top-down.** Objetivo → fases (hitos) → etapas (sub-objetivos) → actividades (atómicas), aplicando los **tests del Protocolo de intake** de lo grande a lo atómico. Asigna `run-agent` por actividad según la tabla de backends.
   - **Brownfield (proyecto existente):** lo que YA está implementado y funcional se incluye como actividades marcadas **✅ hecho**, para que el estado derivado refleje el avance real. No marques todo 🔲 en un proyecto que ya tiene código.
4. **Gate — confirma el árbol completo antes de crear nada:**

   ```
   🌱 BOOTSTRAP — <proyecto>
   Objetivo: <objetivo>
   Tipo: <nuevo | existente>
   Plan propuesto:
     F01 — <fase>
       E01 — <etapa>
         act_F01_E01_001 — <actividad>   [backend]   (✅ si ya está hecho)
   ¿Confirmas?  (sí / ajustar)
   ```

5. **Materializar.** Tras el OK: cadena `plan.py add-*` → rellena el contenido autorado → en brownfield fija `status: ✅ hecho` de lo ya hecho y corre `plan.py sync`.
6. **Registrar.** Anexa a la bitácora: `| fecha | bootstrap inicial | — | <objetivo> | N fases / M actividades |`.

### Red flags — DETENTE

| Si piensas… | Realidad |
|-------------|----------|
| "Genero el plan y empiezo a ejecutar de una" | Bootstrap solo crea el plan. Ejecutar es otro paso, con su confirmación. |
| "El objetivo es claro, materializo sin gate" | El árbol completo pasa por el gate, igual que en intake. |
| "El objetivo es vago, asumo el alcance" | Indaga 1-3 preguntas antes de descomponer; no inventes el alcance. |
| "Es vago → lanzo un brainstorm completo" | Bastan 1-3 preguntas. No escales a la skill `brainstorming` para esto. |
| "Es brownfield pero marco todo 🔲" | Mapea lo ya implementado a ✅ para que el estado derivado sea real. |

---

## Archivos de esta skill

```
hybrid-orchestrator/
├── SKILL.md              ← este archivo
├── scripts/
│   ├── run_subagent.py   ← invocador de subagentes
│   └── plan.py           ← gestión del plan vivo (fases/etapas/actividades, estado)
└── templates/
    ├── CLAUDE.md         ← molde para nuevos proyectos
    ├── PLAN.md           ← vista de estado (encabezado autorado + zona generada)
    ├── fase.md           ← molde de resumen de fase
    ├── etapa.md          ← molde de resumen de etapa
    ├── activity.md       ← plantilla de actividad individual
    └── agents/           ← briefings por backend (los carga run_subagent.py)
        ├── gemini.md
        ├── codex.md
        ├── cursor.md
        └── claude.md
```
