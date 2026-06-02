# Subagentes: invocación, flujo, disponibilidad y reintento

Referencia detallada para ejecutar actividades con subagentes. Cargada bajo demanda desde
`SKILL.md`.

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

## Backends disponibles

| Backend | Frontmatter | Cuándo usarlo |
|---------|-------------|---------------|
| `gemini` | `run-agent: gemini` | Código de implementación, análisis masivo, contexto grande |
| `claude` | `run-agent: claude` | Razonamiento complejo, decisiones de arquitectura |
| `codex` | `run-agent: codex` | Refactors rápidos, generación repetitiva |
| `cursor-agent` | `run-agent: cursor-agent` | Edición de archivos existentes |

## Disponibilidad de backends y fallback

Antes de asignar `run-agent:` a las actividades, consulta qué CLIs hay instalados:

```bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --check
```

En ejecución, si el backend declarado no está instalado, `run_subagent.py` cae por una cadena de preferencia hasta `claude` (último recurso garantizado). El orden por defecto es `gemini → codex → cursor-agent → claude` y se puede sobreescribir con la env var `HYBRID_FALLBACK_ORDER` (CSV; `claude` siempre queda al final).

Cuando ocurre un fallback, el script imprime `⚠️ FALLBACK: ...`. Registra ese cambio en el `.md` de la actividad por trazabilidad.

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
