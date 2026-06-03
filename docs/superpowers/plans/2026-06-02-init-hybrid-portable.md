# init-hybrid portable: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Versionar `init-hybrid` como un script portable (zsh/bash), que `install.sh` cablee al shell autodetectado, degradando con gracia cuando falta `gemini` (preguntando al usuario), para que la skill sea instalable en cualquier equipo.

**Architecture:** `init-hybrid` deja de vivir pegado en `~/.zshrc` y pasa a `init-hybrid.sh` (repo → skill dir), sourceado desde el rc vía un bloque gestionado idempotente que añade `install.sh`. El escaneo con Gemini se vuelve opcional con detección por `command -v` y un prompt. Migración one-time del `~/.zshrc` de esta Mac, con backup.

**Tech Stack:** Shell POSIX-ish compatible zsh+bash. Sin código Python nuevo (la suite de 34 tests debe seguir verde).

---

## File Structure

- `init-hybrid.sh` (crear) — la función `init-hybrid` portable + `HYBRID_TEMPLATES`, gemini-optional.
- `install.sh` (modificar) — copiar `init-hybrid.sh` al skill dir + cablear el bloque `source` en el rc autodetectado (idempotente); reemplazar el recordatorio impreso.
- `~/.zshrc` (migración, fuera del repo, con backup) — quitar la función pegada + `HYBRID_TEMPLATES`.
- `README.md` (modificar) — instalación multi-equipo.

---

## Task 1: Crear `init-hybrid.sh` (base portable)

**Files:**
- Create: `init-hybrid.sh`

- [ ] **Step 1: Crear el archivo con la función actual, portabilizada**

Contenido (la función actual de `~/.zshrc`, con `HYBRID_TEMPLATES` usando `$HOME` y sin
sintaxis zsh-only; el escaneo se ajusta en Task 2):

```bash
# init-hybrid.sh — Hybrid Orchestrator
# Se sourcea desde ~/.zshrc o ~/.bashrc (lo cablea install.sh).
# Compatible con zsh y bash.

# Ruta global de plantillas híbridas
HYBRID_TEMPLATES="$HOME/plantillas-hybrid"

init-hybrid() {
    echo "🔍 Iniciando entorno híbrido en: $(pwd)"
    echo ""

    # 1. Verificar plantillas
    if [ ! -d "$HYBRID_TEMPLATES" ]; then
        echo "❌ No se encontró la carpeta de plantillas en $HYBRID_TEMPLATES"
        echo "   Ejecuta install.sh para crearla, o: mkdir -p ~/plantillas-hybrid"
        return 1
    fi
    for archivo in CLAUDE.md PLAN.md; do
        if [ ! -f "$HYBRID_TEMPLATES/$archivo" ]; then
            echo "❌ Falta la plantilla: $HYBRID_TEMPLATES/$archivo"
            return 1
        fi
    done
    echo "✅ Plantillas encontradas en $HYBRID_TEMPLATES"
    echo ""

    # 2. Detectar archivos híbridos existentes
    CLAUDE_EXISTS=false
    PLAN_EXISTS=false
    [ -f "CLAUDE.md" ] && CLAUDE_EXISTS=true
    [ -f "plan/PLAN.md" ] && PLAN_EXISTS=true
    echo "📁 Estado actual del proyecto:"
    echo "   CLAUDE.md  → $( [ "$CLAUDE_EXISTS" = true ] && echo '✅ existe' || echo '🆕 se creará' )"
    echo "   plan/PLAN.md → $( [ "$PLAN_EXISTS" = true ] && echo '✅ existe' || echo '🆕 se creará' )"
    echo ""

    # 3. Copiar plantillas si no existen
    if [ "$PLAN_EXISTS" = false ]; then
        mkdir -p plan
        cp "$HYBRID_TEMPLATES/PLAN.md" ./plan/PLAN.md
        echo "📋 plan/PLAN.md copiado desde plantilla"
        python3 "$HOME/.claude/skills/hybrid-orchestrator/scripts/plan.py" --cwd . sync 2>/dev/null
    fi

    # 4. Escanear el proyecto (Task 2 lo vuelve gemini-optional)
    echo ""
    echo "🤖 Analizando proyecto con Gemini..."
    SCAN_RESULT=$(gemini -p "Analiza el directorio actual y genera un resumen técnico conciso en español con este formato exacto:

TIPO: [nuevo | existente]
STACK: [tecnologías detectadas separadas por coma, o 'No detectado' si está vacío]
ARCHIVOS_CLAVE: [lista de archivos importantes encontrados, o 'Ninguno' si está vacío]
TIENE_SRC: [sí | no]
TIENE_TESTS: [sí | no]
RESUMEN: [2 oraciones describiendo qué es este proyecto y en qué estado está. Si está vacío: 'Proyecto nuevo sin contenido aún.']
RECOMENDACION: [qué debería hacer Claude Code primero al iniciar sesión aquí]

Solo responde con ese bloque. Sin explicaciones adicionales." --all-files 2>/dev/null)

    echo ""
    echo "📊 Resultado del escaneo:"
    echo "──────────────────────────────────────────────"
    echo "$SCAN_RESULT"
    echo "──────────────────────────────────────────────"
    echo ""

    # 5. Generar o actualizar CLAUDE.md
    if [ "$CLAUDE_EXISTS" = false ]; then
        echo "✍️  Generando CLAUDE.md desde plantilla + contexto del proyecto..."
        cp "$HYBRID_TEMPLATES/CLAUDE.md" ./CLAUDE.md
        cat << CONTEXT >> CLAUDE.md

---

## 🌐 Contexto detectado del proyecto

> Generado automáticamente por init-hybrid — $(date '+%Y-%m-%d %H:%M')

\`\`\`
$SCAN_RESULT
\`\`\`

---

## 📋 Instrucción de inicio de sesión

Al iniciar cada sesión en este proyecto:
1. Lee este archivo completo
2. Lee \`plan/PLAN.md\` para orientarte
3. Si el plan está vacío, pide 'haz el bootstrap del plan'
4. Identifica la siguiente actividad pendiente y confirma antes de proceder
CONTEXT
        echo "✅ CLAUDE.md generado"
    else
        cat << CONTEXT >> CLAUDE.md

---

## 🔄 Re-escaneo del proyecto — $(date '+%Y-%m-%d %H:%M')

\`\`\`
$SCAN_RESULT
\`\`\`
CONTEXT
        echo "✅ Contexto del nuevo escaneo agregado al CLAUDE.md existente"
    fi

    # 6. Inicializar Claude Code
    echo ""
    claude /init

    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "🚀 Entorno híbrido listo"
    echo "   Proyecto : $(pwd)"
    echo "   Plantillas: $HYBRID_TEMPLATES"
    echo "   Bootstrap : inicia 'claude' y pídele 'haz el bootstrap del plan'"
    echo "═══════════════════════════════════════════════════"
}
```

- [ ] **Step 2: Verificar sintaxis en ambos shells**

Run: `bash -n init-hybrid.sh && zsh -n init-hybrid.sh && echo OK`
Expected: `OK`

- [ ] **Step 3: Verificar que define la función al sourcear**

Run: `bash -c '. ./init-hybrid.sh; type init-hybrid >/dev/null && echo bash-ok' && zsh -c '. ./init-hybrid.sh; type init-hybrid >/dev/null && echo zsh-ok'`
Expected: `bash-ok` y `zsh-ok`

- [ ] **Step 4: Commit**

```bash
git add init-hybrid.sh
git commit -m "feat(init): init-hybrid.sh versionado y portable (zsh/bash)"
```

---

## Task 2: Hacer el escaneo gemini-optional (con prompt)

**Files:**
- Modify: `init-hybrid.sh` (reemplazar el bloque "4. Escanear")

- [ ] **Step 1: Reemplazar el bloque de escaneo**

Sustituir todo el bloque `# 4. Escanear el proyecto ...` (desde `echo "🤖 Analizando..."`
hasta el cierre `──────` con el `echo ""`) por:

```bash
    # 4. Detectar backends y escanear (solo si hay gemini)
    echo ""
    if command -v gemini >/dev/null 2>&1; then
        echo "🤖 Analizando proyecto con Gemini..."
        SCAN_RESULT=$(gemini -p "Analiza el directorio actual y genera un resumen técnico conciso en español con este formato exacto:

TIPO: [nuevo | existente]
STACK: [tecnologías detectadas separadas por coma, o 'No detectado' si está vacío]
ARCHIVOS_CLAVE: [lista de archivos importantes encontrados, o 'Ninguno' si está vacío]
TIENE_SRC: [sí | no]
TIENE_TESTS: [sí | no]
RESUMEN: [2 oraciones describiendo qué es este proyecto y en qué estado está. Si está vacío: 'Proyecto nuevo sin contenido aún.']
RECOMENDACION: [qué debería hacer Claude Code primero al iniciar sesión aquí]

Solo responde con ese bloque. Sin explicaciones adicionales." --all-files 2>/dev/null)
        echo ""
        echo "📊 Resultado del escaneo:"
        echo "──────────────────────────────────────────────"
        echo "$SCAN_RESULT"
        echo "──────────────────────────────────────────────"
        echo ""
    else
        available=""
        for b in claude codex cursor-agent; do
            command -v "$b" >/dev/null 2>&1 && available="$available $b"
        done
        if [ -z "${available# }" ]; then
            echo "❌ No hay ningún backend instalado (ni claude). Instala al menos Claude Code:"
            echo "   curl -fsSL https://claude.ai/install.sh | bash"
            return 1
        fi
        echo "⚠️  gemini no está instalado. Backends disponibles:$available"
        printf "¿Continuar solo con lo disponible? [s] continuar / [n] ver cómo instalar más: "
        read -r answer
        case "$answer" in
            n|N)
                echo "Instala los backends que quieras y re-corre init-hybrid:"
                echo "   gemini:       npm install -g @google/gemini-cli"
                echo "   codex:        npm install -g @openai/codex"
                echo "   cursor-agent: curl https://cursor.com/install -fsS | bash"
                return 0
                ;;
        esac
        SCAN_RESULT="TIPO: [no escaneado]
RESUMEN: Escaneo automático omitido (no hay gemini). El protocolo de bootstrap leerá el repo en la sesión.
RECOMENDACION: Pide a Claude 'haz el bootstrap del plan'."
        echo "ℹ️  Escaneo omitido; el bootstrap armará el contexto en la sesión."
        echo ""
    fi
```

> Nota: el default (solo Enter) **continúa** (el `case` solo intercepta `n`/`N`). `${available# }`
> quita el espacio inicial para el test de vacío (portable en zsh/bash).

- [ ] **Step 2: Verificar sintaxis en ambos shells**

Run: `bash -n init-hybrid.sh && zsh -n init-hybrid.sh && echo OK`
Expected: `OK`

- [ ] **Step 3: Dry-run del camino SIN gemini (rama 'n')**

Con un PATH que excluye gemini (homebrew) y respondiendo `n` (retorna antes de `claude /init`):

```bash
mkdir -p /tmp/hyb-test && cd /tmp/hyb-test && \
echo n | env PATH=/usr/bin:/bin bash -c '. ~/Proyectos/hybrid-orchestrator/init-hybrid.sh; init-hybrid'
```
Expected: detecta que falta gemini, lista backends disponibles, muestra el prompt, y con `n`
imprime los comandos de instalación y termina sin error (no llega a `claude /init`).

- [ ] **Step 4: Commit**

```bash
git add init-hybrid.sh
git commit -m "feat(init): escaneo gemini-optional con detección de backends y prompt"
```

---

## Task 3: `install.sh` copia y cablea `init-hybrid.sh`

**Files:**
- Modify: `install.sh` (sección 4: reemplazar el recordatorio por instalación real)

- [ ] **Step 1: Reemplazar la sección 4 de `install.sh`**

Sustituir el bloque actual (el `echo "📌 Recuerda…"`) por:

```bash
# ── 4. Instalar init-hybrid y cablearlo al shell ──────────────────
mkdir -p "$SKILL_TARGET"
cp "$SKILL_SOURCE/init-hybrid.sh" "$SKILL_TARGET/init-hybrid.sh"
echo "✅ init-hybrid.sh instalado en $SKILL_TARGET"

shell_name="$(basename "${SHELL:-zsh}")"
case "$shell_name" in
    zsh)  RC="$HOME/.zshrc" ;;
    bash) RC="$HOME/.bashrc" ;;
    *)    RC="$HOME/.zshrc"; echo "⚠️  Shell '$shell_name' no reconocido; usando $RC" ;;
esac

MARKER="# >>> hybrid-orchestrator >>>"
if ! grep -qF "$MARKER" "$RC" 2>/dev/null; then
    {
        echo ""
        echo "$MARKER"
        echo '[ -f "$HOME/.claude/skills/hybrid-orchestrator/init-hybrid.sh" ] && . "$HOME/.claude/skills/hybrid-orchestrator/init-hybrid.sh"'
        echo "# <<< hybrid-orchestrator <<<"
    } >> "$RC"
    echo "✅ init-hybrid cableado en $RC — reinicia el shell o ejecuta: source $RC"
else
    echo "✅ init-hybrid ya estaba cableado en $RC"
fi
```

- [ ] **Step 2: Verificar sintaxis**

Run: `bash -n install.sh && echo OK`
Expected: `OK`

- [ ] **Step 3: Probar instalación + idempotencia**

Run: `bash install.sh --update >/dev/null 2>&1 && ls "$HOME/.claude/skills/hybrid-orchestrator/init-hybrid.sh" && grep -c "# >>> hybrid-orchestrator >>>" "$HOME/.zshrc"`
Expected: el archivo existe y el marcador aparece **una sola vez** (correr de nuevo no duplica).

- [ ] **Step 4: Commit**

```bash
git add install.sh
git commit -m "build(install): instalar init-hybrid.sh y cablear source en el rc (idempotente)"
```

---

## Task 4: Migrar el `~/.zshrc` de esta Mac

**Files:**
- Modify: `~/.zshrc` (fuera del repo, con backup)

- [ ] **Step 1: Backup**

Run: `cp ~/.zshrc ~/.zshrc.bak-$(date +%Y%m%d-%H%M%S) && echo backup-ok`
Expected: `backup-ok`

- [ ] **Step 2: Localizar el bloque pegado a mano**

Run: `grep -n "Ruta global de plantillas híbridas\|^HYBRID_TEMPLATES=\|^init-hybrid() {" ~/.zshrc`
Expected: ubica el comentario, la asignación `HYBRID_TEMPLATES=` y la apertura de la función
(la definición pegada, NO el bloque `source` que añadió install.sh).

- [ ] **Step 3: Eliminar la definición pegada**

Quitar del `~/.zshrc`: el comentario "Ruta global de plantillas híbridas", la línea
`HYBRID_TEMPLATES=~/plantillas-hybrid`, y la función `init-hybrid() { … }` completa (hasta su
`}` de cierre). **No** tocar el bloque gestionado `# >>> hybrid-orchestrator >>>`.

- [ ] **Step 4: Verificar**

Run: `zsh -n ~/.zshrc && grep -c "^init-hybrid() {" ~/.zshrc && zsh -ic 'type init-hybrid >/dev/null 2>&1 && echo definida-por-source'`
Expected: `zsh -n` OK; `0` definiciones pegadas; `definida-por-source` (la función existe vía el `source`).

> Sin commit (fuera del repo). La validación es que `init-hybrid` queda definida una sola vez,
> desde el script versionado.

---

## Task 5: README — instalación multi-equipo

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Añadir sección de instalación multi-equipo**

Tras la sección de instalación actual, añadir:

```markdown
### Multi-machine setup

On each machine (macOS/zsh or Linux/bash):

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/hybrid-orchestrator
cd hybrid-orchestrator && bash install.sh   # detects your shell, wires `init-hybrid`
# update later:  git pull && bash install.sh --update
\`\`\`

`init-hybrid` is installed as a versioned script and sourced from your shell rc. If `gemini`
isn't installed, it detects the available backends and asks whether to continue (everything
falls back to `claude`) or install more. You only need the backends you plan to use — `claude`
is the guaranteed fallback.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: instalación multi-equipo en el README"
```

---

## Task 6: Cierre

**Files:**
- Modify: `docs/superpowers/specs/2026-06-02-init-hybrid-portable-design.md`

- [ ] **Step 1: Suite Python sigue verde**

Run: `python3 -m unittest discover -s tests`
Expected: PASS (no se tocó código Python).

- [ ] **Step 2: Marcar el spec como implementado**

Cambiar `**Estado:** Diseño aprobado, pendiente de implementación` por
`**Estado:** Implementado (2026-06-02)`.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-06-02-init-hybrid-portable-design.md
git commit -m "docs: marcar spec de init-hybrid portable como implementado"
```

---

## Notas

- **Portabilidad:** `printf` + `read -r` (no `read -p`, que es bash-only) para el prompt; `$HOME`
  en vez de `~` en asignaciones; `command -v` para detección. Verificado con `bash -n` y `zsh -n`.
- **Idempotencia:** el bloque del rc se añade solo si el marcador no existe.
- **Fallback:** en una máquina con solo `claude`, init-hybrid pregunta y continúa; la ejecución
  de actividades cae a `claude` por la cadena de Feature B.
- **YAGNI:** sin plugin, sin fish, sin sync de datos (el git del proyecto ya lo cubre).
