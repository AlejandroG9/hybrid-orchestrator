#!/usr/bin/env python3
"""
plan.py — Hybrid Orchestrator Skill
Mecánica del plan vivo: crea fases/etapas/actividades y regenera estado e índices.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# scripts/ está en sys.path al ejecutar el script o al importarlo en tests.
from run_subagent import parse_frontmatter


# ── Estados ───────────────────────────────────────────────────────────────────

STATUS = {
    "pendiente": "🔲 pendiente",
    "en curso":  "🔄 en curso",
    "hecho":     "✅ hecho",
    "bloqueado": "⛔ bloqueado",
}


def _category(status: str) -> str:
    """Clasifica un string de status por su emoji."""
    s = status or ""
    if "⛔" in s:
        return "bloqueado"
    if "✅" in s:
        return "hecho"
    if "🔄" in s:
        return "en curso"
    return "pendiente"  # incluye 🔲 y desconocidos


def rollup_status(children: list) -> str:
    """Deriva el estado de un nivel a partir de los status de sus hijos."""
    if not children:
        return STATUS["pendiente"]

    cats = [_category(c) for c in children]
    if any(c == "bloqueado" for c in cats):
        return STATUS["bloqueado"]
    if all(c == "hecho" for c in cats):
        return STATUS["hecho"]
    if any(c == "en curso" for c in cats):
        return STATUS["en curso"]
    if any(c == "hecho" for c in cats) and any(c == "pendiente" for c in cats):
        return STATUS["en curso"]
    return STATUS["pendiente"]


def next_number(existing: list) -> int:
    """Siguiente número en un nivel (append tras el máximo; huecos no se rellenan)."""
    return (max(existing) + 1) if existing else 1


def set_frontmatter_field(text: str, key: str, value: str) -> str:
    """Actualiza (o inserta) un campo en el frontmatter YAML del texto."""
    if not text.startswith("---"):
        return f"---\n{key}: {value}\n---\n\n{text}"

    parts = text.split("---", 2)
    # parts[0] == "" ; parts[1] == frontmatter ; parts[2] == cuerpo
    fm_lines = parts[1].strip("\n").split("\n")
    key_re = re.compile(rf"^{re.escape(key)}\s*:")

    replaced = False
    for i, line in enumerate(fm_lines):
        if key_re.match(line):
            fm_lines[i] = f"{key}: {value}"
            replaced = True
            break
    if not replaced:
        fm_lines.append(f"{key}: {value}")

    new_fm = "\n".join(fm_lines)
    return f"---\n{new_fm}\n---{parts[2]}"


BEGIN_AUTO = "<!-- BEGIN:auto — generado por plan.py, no editar -->"
END_AUTO = "<!-- END:auto -->"


def replace_auto_block(text: str, inner: str) -> str:
    """Reemplaza el contenido entre marcadores BEGIN/END:auto; si faltan, lo agrega."""
    block = f"{BEGIN_AUTO}\n{inner}\n{END_AUTO}"
    pattern = re.compile(
        re.escape(BEGIN_AUTO) + r".*?" + re.escape(END_AUTO),
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(lambda _: block, text)
    sep = "" if text.endswith("\n") else "\n"
    return f"{text}{sep}\n{block}\n"


# ── Render de vistas ──────────────────────────────────────────────────────────

def _count_done(items: list) -> tuple:
    done = sum(1 for it in items if _category(it["status"]) == "hecho")
    return done, len(items)


def render_level_block(node: dict, kind: str) -> str:
    """Bloque generado para un _etapa.md (kind='stage') o _fase.md (kind='phase')."""
    if kind == "stage":
        acts = node["activities"]
        done, total = _count_done(acts)
        lines = [
            f"**Estado:** {node['status']} ({done}/{total} ✅)",
            "",
            "| Actividad | Backend | Estado |",
            "| --- | --- | --- |",
        ]
        for a in acts:
            lines.append(f"| act_{a['id']} | {a['backend']} | {a['status']} |")
        return "\n".join(lines)

    # kind == "phase"
    stages = node["stages"]
    done, total = _count_done(stages)
    lines = [
        f"**Estado:** {node['status']} ({done}/{total} etapas ✅)",
        "",
        "| Etapa | Estado |",
        "| --- | --- |",
    ]
    for s in stages:
        lines.append(f"| E{s['num']:02d} — {s['title']} | {s['status']} |")
    return "\n".join(lines)


def render_plan(tree: dict) -> str:
    """Cuerpo generado de PLAN.md: tabla de fases."""
    phases = tree["phases"]
    done, total = _count_done(phases)
    lines = [
        f"**Estado global:** {done}/{total} fases ✅",
        "",
        "| Fase | Estado |",
        "| --- | --- |",
    ]
    for ph in phases:
        lines.append(f"| F{ph['num']:02d} — {ph['title']} | {ph['status']} |")
    return "\n".join(lines)


# ── Capa de E/S ───────────────────────────────────────────────────────────────

def _num_from_dir(name: str, prefix: str) -> int:
    """Extrae el número de 'fase_03' / 'etapa_02' -> 3 / 2."""
    m = re.match(rf"{prefix}_(\d+)$", name)
    return int(m.group(1)) if m else 0


def _read_meta(path: Path) -> tuple:
    if not path.exists():
        return {}, ""
    content = path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def scan_plan(plan_dir: Path) -> dict:
    """Construye el árbol del plan leyendo frontmatter, con estados derivados bottom-up."""
    tree = {"title": "", "phases": []}
    if not plan_dir.exists():
        return tree

    for fase_dir in sorted(plan_dir.glob("fase_*")):
        if not fase_dir.is_dir():
            continue
        fnum = _num_from_dir(fase_dir.name, "fase")
        fmeta, _ = _read_meta(fase_dir / "_fase.md")
        phase = {
            "id": fmeta.get("id", f"F{fnum:02d}"),
            "num": fnum,
            "title": fmeta.get("title", fase_dir.name),
            "stages": [],
            "status": STATUS["pendiente"],
        }

        for etapa_dir in sorted(fase_dir.glob("etapa_*")):
            if not etapa_dir.is_dir():
                continue
            enum = _num_from_dir(etapa_dir.name, "etapa")
            emeta, _ = _read_meta(etapa_dir / "_etapa.md")
            stage = {
                "id": emeta.get("id", f"F{fnum:02d}_E{enum:02d}"),
                "num": enum,
                "title": emeta.get("title", etapa_dir.name),
                "activities": [],
                "status": STATUS["pendiente"],
            }

            for act in sorted(etapa_dir.glob("act_*.md")):
                ameta, _ = _read_meta(act)
                stage["activities"].append({
                    "id": act.stem.replace("act_", ""),
                    "backend": ameta.get("run-agent", "gemini"),
                    "status": ameta.get("status", STATUS["pendiente"]),
                })

            stage["status"] = rollup_status([a["status"] for a in stage["activities"]])
            phase["stages"].append(stage)

        phase["status"] = rollup_status([s["status"] for s in phase["stages"]])
        tree["phases"].append(phase)

    return tree


def _write_level(path: Path, status: str, block: str):
    """Actualiza status en frontmatter y reemplaza el bloque auto del archivo de nivel."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "status", status)
    text = replace_auto_block(text, block)
    path.write_text(text, encoding="utf-8")


def sync(plan_dir: Path) -> dict:
    """Regenera estados, bloques de nivel y PLAN.md desde la fuente de verdad."""
    tree = scan_plan(plan_dir)

    for phase in tree["phases"]:
        fase_md = plan_dir / f"fase_{phase['num']:02d}" / "_fase.md"
        for stage in phase["stages"]:
            etapa_md = (plan_dir / f"fase_{phase['num']:02d}"
                        / f"etapa_{stage['num']:02d}" / "_etapa.md")
            _write_level(etapa_md, stage["status"], render_level_block(stage, "stage"))
        _write_level(fase_md, phase["status"], render_level_block(phase, "phase"))

    plan_md = plan_dir / "PLAN.md"
    if plan_md.exists():
        text = plan_md.read_text(encoding="utf-8")
    else:
        text = "# Plan del proyecto\n\n> Vista generada por plan.py. No edites las zonas auto.\n"
    text = replace_auto_block(text, render_plan(tree))
    plan_md.parent.mkdir(parents=True, exist_ok=True)
    plan_md.write_text(text, encoding="utf-8")

    return tree
