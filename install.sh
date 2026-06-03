#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# install.sh — Hybrid Orchestrator Skill
# Instala la skill en ~/.claude/skills/ y las plantillas en ~/plantillas-hybrid/
#
# Uso:
#   bash install.sh           → instalación completa
#   bash install.sh --update  → actualiza archivos existentes
# ═══════════════════════════════════════════════════════════════════

set -e

SKILL_NAME="hybrid-orchestrator"
SKILL_SOURCE="$(cd "$(dirname "$0")" && pwd)"
SKILL_TARGET="$HOME/.claude/skills/$SKILL_NAME"
TEMPLATES_TARGET="$HOME/plantillas-hybrid"
UPDATE_MODE=false

# ── Flags ─────────────────────────────────────────────────────────
for arg in "$@"; do
    case $arg in
        --update) UPDATE_MODE=true ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Hybrid Orchestrator Skill — Instalador"
echo "═══════════════════════════════════════════════════"
echo "  Fuente   : $SKILL_SOURCE"
echo "  Skill    : $SKILL_TARGET"
echo "  Plantillas: $TEMPLATES_TARGET"
echo "  Modo     : $( [ "$UPDATE_MODE" = true ] && echo 'actualización' || echo 'instalación nueva' )"
echo "═══════════════════════════════════════════════════"
echo ""

# ── 1. Verificar Python 3 ─────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 no encontrado. Instálalo antes de continuar."
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# ── 2. Instalar skill en ~/.claude/skills/ ────────────────────────
if [ -d "$SKILL_TARGET" ] && [ "$UPDATE_MODE" = false ]; then
    echo ""
    echo "⚠️  La skill ya existe en $SKILL_TARGET"
    echo "   Usa --update para sobreescribir, o elimínala manualmente."
    echo "   Continuando con la instalación de plantillas..."
else
    mkdir -p "$SKILL_TARGET/scripts"
    cp "$SKILL_SOURCE/SKILL.md"                "$SKILL_TARGET/SKILL.md"
    cp "$SKILL_SOURCE/scripts/run_subagent.py" "$SKILL_TARGET/scripts/run_subagent.py"
    cp "$SKILL_SOURCE/scripts/plan.py"         "$SKILL_TARGET/scripts/plan.py"
    chmod +x "$SKILL_TARGET/scripts/run_subagent.py" "$SKILL_TARGET/scripts/plan.py"

    # Copiar plantillas dentro de la skill — run_subagent.py carga los briefings
    # de cada backend desde $SKILL_TARGET/templates/agents/[backend].md
    rm -rf "$SKILL_TARGET/templates"
    cp -R "$SKILL_SOURCE/templates" "$SKILL_TARGET/templates"
    find "$SKILL_TARGET/templates" -name '.DS_Store' -delete 2>/dev/null || true

    # Copiar referencias (progressive disclosure) — SKILL.md las apunta con REQUIRED
    rm -rf "$SKILL_TARGET/references"
    cp -R "$SKILL_SOURCE/references" "$SKILL_TARGET/references"
    find "$SKILL_TARGET/references" -name '.DS_Store' -delete 2>/dev/null || true

    echo "✅ Skill instalada en $SKILL_TARGET (incluye templates/agents/ y references/)"
fi

# ── 3. Instalar plantillas en ~/plantillas-hybrid/ ────────────────
mkdir -p "$TEMPLATES_TARGET"

for archivo in CLAUDE.md PLAN.md activity.md; do
    src="$SKILL_SOURCE/templates/$archivo"
    dst="$TEMPLATES_TARGET/$archivo"

    if [ ! -f "$src" ]; then
        echo "⚠️  Plantilla no encontrada: $src — omitida"
        continue
    fi

    if [ -f "$dst" ] && [ "$UPDATE_MODE" = false ]; then
        echo "   ⏭️  $archivo ya existe en plantillas — omitido (usa --update para sobreescribir)"
    else
        cp "$src" "$dst"
        echo "✅ Plantilla copiada: $archivo → $TEMPLATES_TARGET/"
    fi
done

# ── 4. Instalar init-hybrid y cablearlo al shell ──────────────────
echo ""
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

# ── 5. Resumen final ──────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "🚀 Instalación completada"
echo ""
echo "  Para usar la skill en cualquier proyecto:"
echo "  → claude: 'usa hybrid-orchestrator para planear este proyecto'"
echo ""
echo "  Para invocar un subagente manualmente:"
echo "  → python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py \\"
echo "      --agent plan/fase_01/etapa_01/act_F01_E01_001.md \\"
echo "      --cwd \$(pwd)"
echo ""
echo "  Para listar actividades del proyecto actual:"
echo "  → python3 ~/.claude/skills/hybrid-orchestrator/scripts/run_subagent.py --list"
echo "═══════════════════════════════════════════════════"
echo ""
