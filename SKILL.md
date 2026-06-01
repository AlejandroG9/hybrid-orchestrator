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

## Archivos de esta skill

```
hybrid-orchestrator/
├── SKILL.md              ← este archivo
├── scripts/
│   └── run_subagent.py   ← invocador de subagentes
└── templates/
    ├── CLAUDE.md         ← molde para nuevos proyectos
    ├── PLAN.md           ← documento maestro del proyecto
    ├── activity.md       ← plantilla de actividad individual
    └── agents/           ← briefings por backend (los carga run_subagent.py)
        ├── gemini.md
        ├── codex.md
        ├── cursor.md
        └── claude.md
```
