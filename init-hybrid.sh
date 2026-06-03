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
