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
