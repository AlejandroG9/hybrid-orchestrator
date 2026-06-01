# Feature B — Backend Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `run_subagent.py` detecte qué CLIs están instalados y, si el backend declarado falta, caiga en cadena hasta `claude` (último recurso garantizado), más un comando `--check` para consciencia previa del orquestador.

**Architecture:** Se extrae la lógica de selección de backend a funciones **puras y testeables** (`resolve_backend`, `effective_fallback_order`) separadas de la detección de sistema (`is_available`) y de la integración en `main()`. La pureza permite TDD sin mocks pesados: `resolve_backend(declared, available, order)` recibe el conjunto de disponibles como dato.

**Tech Stack:** Python 3.9 (stdlib only). Tests con `unittest` + `unittest.mock` (sin dependencias externas — el repo no tiene ninguna y se conserva así). Spec de referencia: `docs/superpowers/specs/2026-06-01-backend-fallback-design.md`.

---

## File Structure

- `scripts/run_subagent.py` (modificar) — agrega `import shutil`; constante `FALLBACK_ORDER`; funciones `is_available`, `available_backends`, `effective_fallback_order`, `resolve_backend`, `print_check`; integración en `main()` (flag `--check`, resolución + aviso de fallback, descarte de `--all-files` con aviso).
- `tests/test_run_subagent.py` (crear) — unitarios de la lógica de resolución, override de env y doctor.
- `SKILL.md` (modificar) — sección "Disponibilidad de backends y fallback".
- `templates/CLAUDE.md` (modificar) — instrucción al orquestador de correr `--check` antes de asignar `run-agent:`.

Convención de pruebas: `python3 -m unittest discover -s tests -v` desde la raíz del repo. Para que `tests/` pueda importar el módulo, los tests insertan `scripts/` en `sys.path` (no hay paquete instalable).

---

## Task 1: Función pura `resolve_backend` (núcleo de la cadena)

**Files:**
- Create: `tests/test_run_subagent.py`
- Modify: `scripts/run_subagent.py` (agregar `FALLBACK_ORDER` y `resolve_backend` cerca del bloque `BACKENDS`, ~línea 25)

- [ ] **Step 1: Escribir el test que falla**

```python
# tests/test_run_subagent.py
import sys
import unittest
from pathlib import Path

# Permitir importar el script (no es un paquete instalable)
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_subagent as r  # noqa: E402


class TestResolveBackend(unittest.TestCase):
    def setUp(self):
        # Orden por defecto, claude al final
        self.order = ["gemini", "codex", "cursor-agent", "claude"]

    def test_declared_available_returns_itself(self):
        chosen, fell_back, _ = r.resolve_backend(
            "gemini", available={"gemini", "claude"}, order=self.order
        )
        self.assertEqual(chosen, "gemini")
        self.assertFalse(fell_back)

    def test_declared_missing_falls_to_next_installed(self):
        chosen, fell_back, motivo = r.resolve_backend(
            "gemini", available={"codex", "claude"}, order=self.order
        )
        self.assertEqual(chosen, "codex")
        self.assertTrue(fell_back)
        self.assertIn("gemini", motivo)
        self.assertIn("codex", motivo)

    def test_falls_through_to_claude_when_only_claude(self):
        chosen, fell_back, _ = r.resolve_backend(
            "gemini", available={"claude"}, order=self.order
        )
        self.assertEqual(chosen, "claude")
        self.assertTrue(fell_back)

    def test_raises_when_nothing_available(self):
        with self.assertRaises(RuntimeError):
            r.resolve_backend("gemini", available=set(), order=self.order)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL con `AttributeError: module 'run_subagent' has no attribute 'resolve_backend'`

- [ ] **Step 3: Implementación mínima**

En `scripts/run_subagent.py`, después del bloque `BACKENDS` / `DEFAULT_BACKEND` (~línea 25), agregar:

```python
# ── Cadena de fallback ────────────────────────────────────────────────────────

FALLBACK_ORDER = ["gemini", "codex", "cursor-agent", "claude"]  # claude SIEMPRE al final


def resolve_backend(declared: str, available: set, order: list) -> tuple:
    """
    Elige el backend a usar dado el declarado y los disponibles.

    Args:
        declared:  backend pedido por la actividad (debe estar en BACKENDS).
        available: conjunto de backends instalados en el sistema.
        order:     cadena de preferencia efectiva (claude al final).

    Returns:
        (backend_elegido, hubo_fallback, motivo)

    Raises:
        RuntimeError: si ningún backend de la cadena está disponible.
    """
    if declared in available:
        return declared, False, ""

    for candidate in order:
        if candidate == declared:
            continue
        if candidate in available:
            motivo = (
                f"'{declared}' no disponible → usando '{candidate}' "
                f"(siguiente instalado en la cadena)"
            )
            return candidate, True, motivo

    raise RuntimeError(
        f"Ningún backend disponible para ejecutar '{declared}'. "
        f"Instala al menos uno (recomendado: claude)."
    )
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (4 tests de `TestResolveBackend`)

- [ ] **Step 5: Commit**

```bash
git add tests/test_run_subagent.py scripts/run_subagent.py
git commit -m "feat(run_subagent): resolve_backend con cadena de fallback"
```

---

## Task 2: `effective_fallback_order` (override de env, claude pinneado)

**Files:**
- Modify: `scripts/run_subagent.py` (agregar `effective_fallback_order` bajo `FALLBACK_ORDER`; requiere `import os` — ya está importado)
- Modify: `tests/test_run_subagent.py` (nueva clase de tests)

- [ ] **Step 1: Escribir el test que falla**

```python
from unittest import mock  # agregar al tope del archivo de tests si no está


class TestEffectiveFallbackOrder(unittest.TestCase):
    def test_default_when_no_env(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["gemini", "codex", "cursor-agent", "claude"])

    def test_env_override_respected_claude_last(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "codex,gemini,claude"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["codex", "gemini", "claude"])
        self.assertEqual(order[-1], "claude")

    def test_env_override_without_claude_appends_it(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "codex,gemini"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order[-1], "claude")
        self.assertIn("codex", order)

    def test_env_override_ignores_unknown_names(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "foo,codex,bar"}, clear=True):
            order = r.effective_fallback_order()
        self.assertNotIn("foo", order)
        self.assertNotIn("bar", order)
        self.assertIn("codex", order)
        self.assertEqual(order[-1], "claude")

    def test_env_override_all_invalid_falls_to_default(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "foo,bar"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["gemini", "codex", "cursor-agent", "claude"])
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL con `AttributeError: module 'run_subagent' has no attribute 'effective_fallback_order'`

- [ ] **Step 3: Implementación mínima**

Bajo `FALLBACK_ORDER` en `scripts/run_subagent.py`:

```python
def effective_fallback_order() -> list:
    """
    Cadena de fallback efectiva. Lee HYBRID_FALLBACK_ORDER (CSV) si está;
    ignora nombres desconocidos y garantiza 'claude' al final.
    """
    raw = os.environ.get("HYBRID_FALLBACK_ORDER", "").strip()
    if raw:
        order = [x.strip() for x in raw.split(",") if x.strip() in BACKENDS]
        if not order:
            print("⚠️  HYBRID_FALLBACK_ORDER inválido — usando orden por defecto")
            order = list(FALLBACK_ORDER)
    else:
        order = list(FALLBACK_ORDER)

    # Forzar claude como último recurso
    order = [b for b in order if b != "claude"]
    order.append("claude")
    return order
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (todos los tests de `TestEffectiveFallbackOrder` + los de Task 1)

- [ ] **Step 5: Commit**

```bash
git add scripts/run_subagent.py tests/test_run_subagent.py
git commit -m "feat(run_subagent): effective_fallback_order con override por env"
```

---

## Task 3: Detección de sistema `is_available` / `available_backends`

**Files:**
- Modify: `scripts/run_subagent.py` (agregar `import shutil` al tope; funciones bajo el bloque de cadena)
- Modify: `tests/test_run_subagent.py`

- [ ] **Step 1: Escribir el test que falla**

```python
class TestAvailability(unittest.TestCase):
    def test_is_available_true_when_which_finds_it(self):
        with mock.patch("run_subagent.shutil.which", return_value="/usr/bin/gemini"):
            self.assertTrue(r.is_available("gemini"))

    def test_is_available_false_when_which_returns_none(self):
        with mock.patch("run_subagent.shutil.which", return_value=None):
            self.assertFalse(r.is_available("gemini"))

    def test_available_backends_collects_only_installed(self):
        def fake_which(exe):
            return "/path" if exe in ("gemini", "claude") else None
        with mock.patch("run_subagent.shutil.which", side_effect=fake_which):
            avail = r.available_backends()
        self.assertEqual(avail, {"gemini", "claude"})
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL con `AttributeError` (`is_available` / `shutil`)

- [ ] **Step 3: Implementación mínima**

Agregar `import shutil` junto a los otros imports (~línea 10). Luego:

```python
def is_available(backend: str) -> bool:
    """True si el ejecutable del backend está en PATH."""
    exe = BACKENDS[backend][0]
    return shutil.which(exe) is not None


def available_backends() -> set:
    """Conjunto de backends instalados en el sistema."""
    return {b for b in BACKENDS if is_available(b)}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/run_subagent.py tests/test_run_subagent.py
git commit -m "feat(run_subagent): detección de backends instalados"
```

---

## Task 4: Comando `--check` (doctor)

**Files:**
- Modify: `scripts/run_subagent.py` (función `print_check`; flag `--check` en argparse; short-circuit en `main()`)
- Modify: `tests/test_run_subagent.py`

- [ ] **Step 1: Escribir el test que falla**

```python
import io
from contextlib import redirect_stdout


class TestCheck(unittest.TestCase):
    def test_print_check_lists_installed_and_missing(self):
        def fake_which(exe):
            return "/usr/bin/" + exe if exe in ("gemini", "claude") else None
        buf = io.StringIO()
        with mock.patch("run_subagent.shutil.which", side_effect=fake_which):
            with mock.patch.dict("os.environ", {}, clear=True):
                with redirect_stdout(buf):
                    r.print_check()
        out = buf.getvalue()
        self.assertIn("gemini", out)
        self.assertIn("✅", out)
        self.assertIn("❌", out)
        self.assertIn("Cadena efectiva", out)
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL con `AttributeError: ... 'print_check'`

- [ ] **Step 3: Implementación mínima**

Agregar la función (cerca de `list_agents`):

```python
def print_check() -> None:
    """Reporta qué backends están instalados y la cadena de fallback efectiva."""
    print("Backends:")
    for backend in BACKENDS:
        exe = BACKENDS[backend][0]
        path = shutil.which(exe)
        if path:
            print(f"  {backend:13} ✅ {path}")
        else:
            print(f"  {backend:13} ❌ no instalado")

    order = effective_fallback_order()
    avail = available_backends()
    cadena = " → ".join(b for b in order if b in avail) or "(ninguno instalado)"
    print(f"\nCadena efectiva: {cadena}")
```

En `main()`, agregar el flag junto a los otros `add_argument` (~línea 167):

```python
    parser.add_argument("--check", action="store_true", help="Reporta backends instalados y la cadena de fallback")
```

Y el short-circuit al inicio de la lógica de `main()`, **antes** de calcular `cwd`/`agents_dir` (justo tras `args = parser.parse_args()`):

```python
    if args.check:
        print_check()
        return
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

Verificación manual:
Run: `python3 scripts/run_subagent.py --check`
Expected: lista de backends con ✅/❌ según tu máquina y la línea "Cadena efectiva: ...".

- [ ] **Step 5: Commit**

```bash
git add scripts/run_subagent.py tests/test_run_subagent.py
git commit -m "feat(run_subagent): comando --check (doctor de backends)"
```

---

## Task 5: Integrar resolución + fallback en `main()`

**Files:**
- Modify: `scripts/run_subagent.py` (`main()`, bloque "Determinar backend" ~líneas 200-205, y `run_agent` para el aviso de `--all-files`)

- [ ] **Step 1: Reemplazar la selección de backend en `main()`**

Localizar (actual ~líneas 201-205):

```python
    # Determinar backend
    backend = args.cli or meta.get("run-agent", DEFAULT_BACKEND)

    # Construir prompt
    prompt = build_prompt(content, backend)
```

Reemplazar por:

```python
    # Determinar backend declarado y resolver disponibilidad / fallback
    declared = args.cli or meta.get("run-agent", DEFAULT_BACKEND)

    if declared not in BACKENDS:
        print(f"❌ Backend '{declared}' no reconocido. Disponibles: {list(BACKENDS.keys())}")
        sys.exit(1)

    try:
        backend, fell_back, motivo = resolve_backend(
            declared, available_backends(), effective_fallback_order()
        )
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if fell_back:
        print(f"⚠️  FALLBACK: {motivo}")
        if declared == "gemini" and args.all_files:
            print("   (--all-files se descarta: solo aplica a gemini)")

    # Construir prompt con el briefing del backend EFECTIVO
    prompt = build_prompt(content, backend)
```

> Nota: `build_prompt` ya carga `agents/{backend}.md`, así que al pasar el backend
> efectivo se usa automáticamente el briefing correcto. El resumen impreso y
> `run_agent(...)` siguientes ya usan la variable `backend`, ahora la efectiva.

- [ ] **Step 2: Correr la suite y verificar que sigue verde**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (sin regresiones; esta tarea es de cableado)

- [ ] **Step 3: Verificación manual del cableado**

Con un backend declarado inexistente forzado por env a no tener intermedios, comprobar
el aviso de fallback usando `--check` y la lectura del código. (No se invoca un CLI real
para no ejecutar un agente.)

Run: `python3 scripts/run_subagent.py --check`
Expected: refleja correctamente el estado de tu máquina.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_subagent.py
git commit -m "feat(run_subagent): aplicar fallback en main con briefing efectivo"
```

---

## Task 6: Documentación (SKILL.md + molde)

**Files:**
- Modify: `SKILL.md` (nueva sección tras "Backends disponibles", ~línea 108)
- Modify: `templates/CLAUDE.md` (nota en la sección "Delegación a subagentes")

- [ ] **Step 1: Agregar sección a `SKILL.md`**

Tras la tabla "Backends disponibles", insertar:

```markdown
---

## Disponibilidad de backends y fallback

Antes de asignar `run-agent:` a las actividades, consulta qué CLIs hay instalados:

\`\`\`bash
python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --check
\`\`\`

En ejecución, si el backend declarado no está instalado, `run_subagent.py` cae por una
cadena de preferencia hasta `claude` (último recurso garantizado). El orden por defecto
es `gemini → codex → cursor-agent → claude` y se puede sobreescribir con la env var
`HYBRID_FALLBACK_ORDER` (CSV; `claude` siempre queda al final).

Cuando ocurre un fallback, el script imprime `⚠️ FALLBACK: ...`. Registra ese cambio en
el `.md` de la actividad por trazabilidad.
```

- [ ] **Step 2: Agregar nota al molde `templates/CLAUDE.md`**

En la sección "🤖 Delegación a subagentes", tras el párrafo introductorio, agregar:

```markdown
> **Antes de asignar `run-agent:`** corre `run_subagent.py --check` para ver qué
> backends están instalados y asignar de forma realista. Si un backend declarado no
> está disponible al ejecutar, el sistema cae en cadena hasta `claude`; registra ese
> fallback en el `.md` de la actividad.
```

- [ ] **Step 3: Commit**

```bash
git add SKILL.md templates/CLAUDE.md
git commit -m "docs: documentar --check y fallback de backends"
```

---

## Task 7: Cierre — suite completa + estado del spec

**Files:**
- Modify: `docs/superpowers/specs/2026-06-01-backend-fallback-design.md` (estado → implementado)

- [ ] **Step 1: Correr toda la suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS, sin fallos ni errores.

- [ ] **Step 2: Reinstalar la skill y verificar `--check` end-to-end**

Run: `bash install.sh --update && python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --check`
Expected: el doctor corre desde la skill instalada y refleja tu máquina.

- [ ] **Step 3: Marcar el spec como implementado**

Cambiar la línea `**Estado:** Diseño aprobado, pendiente de implementación` por
`**Estado:** Implementado (2026-06-01)`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-06-01-backend-fallback-design.md
git commit -m "docs: marcar spec de fallback como implementado"
```

---

## Notas

- **DRY/YAGNI:** `resolve_backend` es pura y recibe `available`/`order` como datos →
  testeable sin mocks. La detección de sistema (`is_available`) se aísla y se mockea solo
  donde toca PATH.
- **Sin dependencias nuevas:** se usa `unittest` + `unittest.mock` de la stdlib (el spec
  mencionaba pytest; se cambia para mantener el repo sin dependencias externas).
- **Invariante clave:** `claude` siempre es el último de la cadena efectiva.
