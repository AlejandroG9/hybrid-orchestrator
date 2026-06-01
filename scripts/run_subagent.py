#!/usr/bin/env python3
"""
run_subagent.py — Hybrid Orchestrator Skill
Invoca el subagente correcto según el frontmatter run-agent: del archivo .md
"""

import argparse
import subprocess
import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime


# ── Backends disponibles ─────────────────────────────────────────────────────

BACKENDS = {
    "gemini":       ["gemini", "-p"],
    "claude":       ["claude", "-p"],
    "codex":        ["codex", "-q"],
    "cursor-agent": ["cursor-agent", "-p"],
}

DEFAULT_BACKEND = "gemini"

# ── Cadena de fallback ────────────────────────────────────────────────────────

FALLBACK_ORDER = ["gemini", "codex", "cursor-agent", "claude"]  # claude SIEMPRE al final


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


def is_available(backend: str) -> bool:
    """True si el ejecutable del backend está en PATH."""
    exe = BACKENDS[backend][0]
    return shutil.which(exe) is not None


def available_backends() -> set:
    """Conjunto de backends instalados en el sistema."""
    return {b for b in BACKENDS if is_available(b)}


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


# ── Rutas de plantillas ───────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
AGENTS_DIR = TEMPLATES_DIR / "agents"


# ── Parser de frontmatter ────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Extrae el frontmatter YAML de un archivo .md.
    Retorna (metadata_dict, contenido_sin_frontmatter).
    """
    meta = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip()

    return meta, body


# ── Construcción del prompt ──────────────────────────────────────────────────

def build_prompt(activity_content: str, backend: str) -> str:
    """
    Construye el prompt completo para el subagente:
    briefing de templates/agents/[backend].md + contenido de la actividad.
    Si no existe el briefing del backend, usa un briefing genérico.
    """
    briefing_path = AGENTS_DIR / f"{backend}.md"

    if briefing_path.exists():
        briefing = briefing_path.read_text(encoding="utf-8")
        print(f"📄 Briefing cargado: templates/agents/{backend}.md")
    else:
        briefing = (
            "Eres un agente developer. "
            "Ejecuta la actividad asignada, escribe el código requerido "
            "y registra tu trabajo en la sección de ejecución del .md."
        )
        print(f"⚠️  No se encontró briefing para '{backend}' — usando briefing genérico")

    prompt = f"{briefing}\n\n---\n\nACTIVIDAD A EJECUTAR:\n\n{activity_content}"
    return prompt


# ── Invocador del subagente ──────────────────────────────────────────────────

def run_agent(backend: str, prompt: str, cwd: str, all_files: bool, timeout: int) -> tuple[int, str]:
    """
    Ejecuta el CLI del backend con el prompt dado.
    Retorna (código_de_salida, output).
    """
    if backend not in BACKENDS:
        print(f"❌ Backend '{backend}' no reconocido. Backends disponibles: {list(BACKENDS.keys())}")
        sys.exit(1)

    cmd = BACKENDS[backend] + [prompt]

    # Gemini soporta --all-files para escanear el directorio
    if all_files and backend == "gemini":
        cmd.append("--all-files")

    print(f"🤖 Invocando subagente: {backend}")
    print(f"📁 Directorio: {cwd}")
    print(f"⏱️  Timeout: {timeout}s")
    print("─" * 50)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=False,   # mostrar output en tiempo real
            text=True,
            timeout=timeout,
        )
        return result.returncode, ""

    except subprocess.TimeoutExpired:
        print(f"\n⏱️  Timeout alcanzado ({timeout}s). El subagente no respondió a tiempo.")
        return 1, "timeout"

    except FileNotFoundError:
        print(f"\n❌ CLI '{backend}' no encontrado.")
        print(f"   Instala con:")
        installs = {
            "gemini":       "npm install -g @google/gemini-cli",
            "claude":       "curl -fsSL https://claude.ai/install.sh | bash",
            "codex":        "npm install -g @openai/codex",
            "cursor-agent": "curl https://cursor.com/install -fsS | bash",
        }
        print(f"   {installs.get(backend, 'Ver documentación del backend')}")
        return 1, "not_found"


# ── Listado de agentes ───────────────────────────────────────────────────────

def list_agents(agents_dir: Path):
    """Lista todos los archivos .md en el directorio de agentes."""
    if not agents_dir.exists():
        print(f"❌ No se encontró directorio de agentes: {agents_dir}")
        return

    agents = list(agents_dir.rglob("*.md"))
    if not agents:
        print("No hay actividades definidas aún.")
        return

    print(f"\n📋 Actividades en {agents_dir}:\n")
    for agent_path in sorted(agents):
        content = agent_path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(content)
        backend = meta.get("run-agent", DEFAULT_BACKEND)
        status = meta.get("status", "🔲 pendiente")
        rel_path = agent_path.relative_to(agents_dir.parent)
        print(f"  [{backend:12}] {status}  {rel_path}")

    print()


# ── Doctor de backends ────────────────────────────────────────────────────────

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


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hybrid Orchestrator — invoca subagentes por actividad"
    )
    parser.add_argument("--agent",     help="Ruta al archivo .md de la actividad")
    parser.add_argument("--cwd",       help="Directorio de trabajo (ruta absoluta)")
    parser.add_argument("--cli",       help="Forzar backend: gemini, claude, codex, cursor-agent")
    parser.add_argument("--all-files", action="store_true", help="Pasar contexto completo del repo al subagente")
    parser.add_argument("--timeout",   type=int, default=600, help="Timeout en segundos (default: 600)")
    parser.add_argument("--list",      action="store_true", help="Listar actividades disponibles")
    parser.add_argument("--check",     action="store_true", help="Reporta backends instalados y la cadena de fallback")

    args = parser.parse_args()

    # ── Modo doctor ──────────────────────────────────────────────────────────
    if args.check:
        print_check()
        return

    # Directorio de trabajo
    cwd = args.cwd or os.getcwd()
    cwd = str(Path(cwd).resolve())

    # Directorio de agentes (plan/ por convención)
    agents_dir = Path(cwd) / "plan"

    # ── Modo listado ─────────────────────────────────────────────────────────
    if args.list:
        list_agents(agents_dir)
        return

    # ── Modo ejecución ───────────────────────────────────────────────────────
    if not args.agent:
        print("❌ Debes especificar --agent o usar --list")
        parser.print_help()
        sys.exit(1)

    agent_path = Path(args.agent)
    if not agent_path.is_absolute():
        agent_path = Path(cwd) / args.agent

    if not agent_path.exists():
        print(f"❌ Actividad no encontrada: {agent_path}")
        sys.exit(1)

    # Leer actividad
    content = agent_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    # Determinar backend
    backend = args.cli or meta.get("run-agent", DEFAULT_BACKEND)

    # Construir prompt
    prompt = build_prompt(content, backend)

    # Mostrar resumen antes de ejecutar
    print(f"\n{'═'*50}")
    print(f"🚀 Hybrid Orchestrator — Ejecutando actividad")
    print(f"{'═'*50}")
    print(f"  Actividad : {agent_path.name}")
    print(f"  Backend   : {backend}")
    print(f"  Directorio: {cwd}")
    print(f"  All-files : {'sí' if args.all_files else 'no'}")
    print(f"  Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═'*50}\n")

    # Ejecutar subagente
    exit_code, error_type = run_agent(backend, prompt, cwd, args.all_files, args.timeout)

    # Resultado
    print(f"\n{'─'*50}")
    if exit_code == 0:
        print(f"✅ Subagente completó la actividad: {agent_path.name}")
        print(f"   Verifica los criterios de aceptación antes de continuar.")
    else:
        print(f"⛔ El subagente terminó con errores (código: {exit_code})")
        print(f"   Revisa el output y decide si reintentar o escalar.")
    print(f"{'─'*50}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
