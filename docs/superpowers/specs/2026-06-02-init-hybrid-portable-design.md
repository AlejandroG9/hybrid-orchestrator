# init-hybrid portable (multi-máquina)

**Fecha:** 2026-06-02
**Estado:** Implementado (2026-06-02)
**Skill:** hybrid-orchestrator

---

## Problema

`init-hybrid` no está versionado: vive pegado a mano en `~/.zshrc` de una sola máquina, y
`install.sh` solo imprime un recordatorio de configurarlo manualmente. Para usar la skill en
otra máquina (servidor Fedora, otros equipos) hay que copiar la función a mano, y además:
- depende de **`gemini`** para el escaneo inicial (un servidor con solo `claude` falla);
- vive solo en **zsh** (`~/.zshrc`), no en bash.

La lógica central (skill, `plan.py`, `run_subagent.py`) **ya es portable** — el problema es
solo el bootstrapper de entorno.

## Objetivo

Que `init-hybrid` sea instalable y actualizable en cualquier equipo (macOS/zsh, Fedora/bash)
con un único `install.sh`, degradando con gracia cuando faltan backends.

Fuera de alcance (YAGNI): plugin de Claude Code, soporte fish, sincronización de datos (eso ya
lo da el git del propio proyecto).

---

## Diseño

### 1. `init-hybrid` como script versionado

- **Nuevo `init-hybrid.sh`** en la raíz del repo: contiene la función `init-hybrid` +
  `HYBRID_TEMPLATES`, en **sintaxis compatible zsh/bash** (sin construcciones zsh-only).
- `install.sh` lo copia a `~/.claude/skills/hybrid-orchestrator/init-hybrid.sh`.
- Se actualiza con `git pull && bash install.sh --update`. Una sola fuente de verdad versionada.

### 2. `install.sh` cablea el `source` en el shell (autodetectado)

- Detecta el shell por `$SHELL`: zsh → `~/.zshrc`, bash → `~/.bashrc` (default `~/.zshrc` si
  no se reconoce, con aviso).
- Inserta un **bloque gestionado idempotente** entre marcadores:

  ```bash
  # >>> hybrid-orchestrator >>>
  [ -f "$HOME/.claude/skills/hybrid-orchestrator/init-hybrid.sh" ] && \
    . "$HOME/.claude/skills/hybrid-orchestrator/init-hybrid.sh"
  # <<< hybrid-orchestrator <<<
  ```

- Si el bloque ya existe (busca el marcador), no duplica. Reemplaza el `echo "📌 Recuerda…"`
  actual por la instalación real + un aviso de "reinicia el shell o `source` el rc".

### 3. Detección de backends + prompt (gemini-optional)

En el paso de escaneo, `init-hybrid` detecta con `command -v` (shell nativo, sin depender de
python para la decisión):

- **`gemini` presente** → escanea como hoy y pre-puebla `CLAUDE.md` con el `SCAN_RESULT`.
- **`gemini` ausente, pero hay otro backend** (`codex`/`cursor-agent`/`claude`) → muestra los
  disponibles y **pregunta** (con `read`):

  ```
  ⚠️ gemini no está instalado. Backends disponibles: claude, codex.
  ¿Continuar solo con lo disponible? [s] continuar / [n] ver cómo instalar más:
  ```

  - **s** → salta el escaneo (el Protocolo de bootstrap A3 arma el contexto leyendo el repo en
    la sesión) y continúa con la preparación de archivos.
  - **n** → imprime los comandos de instalación de los backends y `return` (para instalar y
    re-correr `init-hybrid`).
- **Ningún backend (ni `claude`)** → error: "Instala al menos Claude Code" y `return 1`.

El resto del flujo de `init-hybrid` (copiar `CLAUDE.md`/`PLAN.md`, `plan.py sync`, `claude
/init`, mensaje final con el puntero al bootstrap) se conserva.

### 4. Migración en la MacBook (one-time, con backup)

La máquina actual tiene `init-hybrid` **pegado a mano** en `~/.zshrc` (con las ediciones de
A3). La migración:
1. Backup de `~/.zshrc`.
2. Mover el contenido de esa función al `init-hybrid.sh` versionado (es la base del script).
3. Eliminar del `~/.zshrc` la definición pegada + el `HYBRID_TEMPLATES` suelto.
4. Dejar el bloque `source` (lo agrega `install.sh`).

En Fedora y otros equipos nunca existió, así que ahí `install.sh` solo agrega el bloque limpio.

---

## Validación

`init-hybrid.sh` es una función de shell (difícil de unit-testear); se valida así:

1. **Sintaxis en ambos shells:** `bash -n init-hybrid.sh` y `zsh -n init-hybrid.sh` → sin errores.
2. **Dry-run con gemini presente** (esta Mac): en una carpeta temporal, sourcear el script y
   correr `init-hybrid` (sin llegar a `claude /init`, o mockeándolo); verificar que crea
   `CLAUDE.md` + `plan/PLAN.md` y corre el scan.
3. **Dry-run sin gemini:** enmascarar `gemini` del PATH en una subshell y verificar que aparece
   el prompt y que con "s" salta el scan y continúa.
4. **Idempotencia de install.sh:** correr `install.sh --update` dos veces y verificar que el
   bloque gestionado del rc aparece **una sola vez**; `zsh -n ~/.zshrc` válido.
5. La suite Python (34 tests) sigue verde (no se toca código Python).

---

## Archivos afectados

- **Nuevo** `init-hybrid.sh` — la función portable (zsh/bash) con gemini-optional + prompt.
- `install.sh` — copiar `init-hybrid.sh` al skill dir + cablear el bloque `source` en el rc
  autodetectado (idempotente); reemplazar el recordatorio impreso.
- `~/.zshrc` (migración, con backup, fuera del repo).
- `README.md` — sección breve de instalación multi-equipo (clone + install.sh; el caso "solo
  claude").

---

## Resultado esperado

En cualquier equipo: `git clone … && bash install.sh` deja `init-hybrid` funcionando en el
shell correcto, degradando con gracia si faltan backends (preguntando al usuario), y
actualizable con `git pull && install.sh --update`. La skill queda verdaderamente portable.
