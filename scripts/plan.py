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
