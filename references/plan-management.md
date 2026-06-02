# Gestión del plan (`plan.py`)

Referencia detallada de la mecánica del plan vivo. Cargada bajo demanda desde `SKILL.md`.

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
