# Feature B — Adaptación a herramientas + fallback en cadena

**Fecha:** 2026-06-01
**Estado:** Implementado (2026-06-01)
**Skill:** hybrid-orchestrator

---

## Problema

Hoy `run_subagent.py` elige el backend desde `--cli`, el frontmatter `run-agent:` de
la actividad, o `DEFAULT_BACKEND` (`gemini`). Si el CLI elegido **no está instalado**,
la ejecución falla con código 1 e imprime instrucciones de instalación — la actividad
queda bloqueada aunque haya otros backends disponibles en el sistema.

No existe:
- Detección previa de qué CLIs están instalados.
- Ningún mecanismo de fallback.
- Forma de que el orquestador (Claude) sepa qué backends puede asignar de forma realista.

## Objetivo

Que la skill se adapte a las herramientas disponibles en la máquina:
1. **Fallback en cadena** en tiempo de ejecución, con `claude` como último recurso garantizado.
2. **Consciencia previa** del orquestador vía un comando `--check`.

Fuera de alcance (YAGNI): perfiles por capacidad, selección por costo/velocidad,
paralelismo entre backends.

---

## Diseño

### 1. Detección de disponibilidad

```python
def is_available(backend: str) -> bool:
    """True si el ejecutable del backend está en PATH."""
    exe = BACKENDS[backend][0]   # p. ej. "gemini", "claude"
    return shutil.which(exe) is not None
```

Sin red ni latencia: solo `shutil.which()`.

### 2. Cadena de fallback global

```python
FALLBACK_ORDER = ["gemini", "codex", "cursor-agent", "claude"]  # claude SIEMPRE al final
```

- Override por env var `HYBRID_FALLBACK_ORDER` (lista separada por comas).
- Reglas de validación del override:
  - Se ignoran nombres que no estén en `BACKENDS`.
  - Si el override no incluye `claude`, se le **agrega al final** automáticamente.
  - Invariante: `claude` es siempre el último elemento efectivo de la cadena.
  - Si el override queda vacío tras validar, se usa el `FALLBACK_ORDER` por defecto (con aviso).

### 3. Resolución de backend

```python
def resolve_backend(declared: str) -> tuple[str, bool, str]:
    """
    Retorna (backend_elegido, hubo_fallback, motivo).
    - Si `declared` está instalado -> (declared, False, "").
    - Si no, recorre la cadena efectiva saltando `declared` y toma el
      primero instalado -> (otro, True, motivo).
    - Si ninguno de la cadena está instalado -> lanza RuntimeError
      (el caller la traduce a salida 1 con instrucciones de instalación).
    """
```

Notas:
- `declared` siempre debe ser un backend conocido (`in BACKENDS`); si no, error previo
  (comportamiento actual conservado).
- Como `claude` está fijo al final de la cadena efectiva, es el catch garantizado
  siempre que esté instalado.

### 4. Briefing del backend efectivo

`build_prompt(content, chosen)` recibe el backend **elegido** (no el declarado). Si
`gemini → claude`, el prompt carga `templates/agents/claude.md`. Cada agente recibe
el briefing acorde a su rol real.

`--all-files` (solo aplica a `gemini`) ya se descarta para no-gemini por el guard
existente; cuando ese descarte ocurre **por causa de un fallback** desde gemini, se
imprime un aviso explícito.

### 5. Aviso y trazabilidad

Cuando hay fallback, se imprime una línea que el orquestador lee en el output:

```
⚠️ FALLBACK: 'gemini' no disponible → usando 'claude' (siguiente instalado en la cadena)
```

Las briefings/molde instruyen al orquestador a **registrar el fallback** en el `.md`
de la actividad (sección de registro de ejecución), por gobierno y trazabilidad.

### 6. Comando `--check` (doctor)

Nuevo flag que corta antes de ejecutar (igual que `--list`):

```
$ run_subagent.py --check
Backends:
  gemini        ✅ /opt/homebrew/bin/gemini
  codex         ❌ no instalado
  cursor-agent  ❌ no instalado
  claude        ✅ /usr/local/bin/claude
Cadena efectiva: gemini → claude
```

Muestra cada backend (instalado + path, o faltante) y la cadena efectiva tras aplicar
override de env. Sale con código 0.

---

## Flujo de datos

```
main()
 ├─ if --check:  imprimir doctor; return
 ├─ if --list:   (sin cambios)
 ├─ declared = --cli ó frontmatter ó DEFAULT_BACKEND
 ├─ chosen, fell_back, motivo = resolve_backend(declared)
 ├─ if fell_back: imprimir aviso ⚠️ FALLBACK
 ├─ prompt = build_prompt(content, chosen)
 └─ run_agent(chosen, prompt, cwd, all_files, timeout)
```

`--check` no requiere `--agent` ni `--cwd`.

---

## Manejo de errores

| Caso | Comportamiento |
|------|----------------|
| `declared` no es un backend conocido | Error previo, salida 1 (actual). |
| Ningún backend de la cadena instalado | `RuntimeError` → salida 1 con instrucciones para instalar al menos uno (preferente: claude). |
| Override de env con nombres inválidos | Se ignoran; si todos inválidos → default con aviso. |
| Override sin `claude` | Se agrega `claude` al final. |
| `declared == claude` y claude ausente | No hay nada después → error duro. |

---

## Pruebas (TDD)

`run_subagent.py` hoy no tiene tests. Se agrega `tests/test_run_subagent.py` (pytest).
La lógica de resolución debe ser pura/importable (sin efectos secundarios) para testear.

Casos unitarios de `resolve_backend` (mockeando `is_available` / `shutil.which`):
1. Declarado instalado → se devuelve el declarado, sin fallback.
2. Declarado ausente, siguiente de la cadena instalado → ese, con fallback.
3. Declarado ausente y todos los intermedios ausentes → `claude`.
4. Override de env respetado y `claude` forzado al final.
5. Override sin `claude` → `claude` agregado al final.
6. Nada instalado → `RuntimeError`.

Smoke test de `--check`: imprime un backend instalado y uno ausente correctamente
(con `shutil.which` mockeado) y sale 0.

---

## Archivos afectados

- `scripts/run_subagent.py` — `is_available()`, `resolve_backend()`, parser de
  `HYBRID_FALLBACK_ORDER`, comando `--check`, integración en `main()`.
- `SKILL.md` — sección "Disponibilidad de backends y fallback" + instrucción de
  correr `--check` antes de asignar `run-agent:`.
- `templates/CLAUDE.md` (molde) — misma instrucción para el orquestador por proyecto.
- `tests/test_run_subagent.py` — **nuevo**, unitarios de la lógica de resolución.

---

## Configuración (resumen)

| Clave | Default | Notas |
|-------|---------|-------|
| `FALLBACK_ORDER` (constante) | `["gemini", "codex", "cursor-agent", "claude"]` | claude pinneado al final |
| `HYBRID_FALLBACK_ORDER` (env) | — | Override CSV; claude se fuerza al final si falta |
