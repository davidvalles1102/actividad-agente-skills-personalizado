"""Descubrimiento dinamico de skills: la parte "comportamiento" del triangulo
logica / configuracion / comportamiento.

Cada skill vive en su propia carpeta dentro de skills/ con dos archivos:
  - SKILL.md: metadata (nombre, descripcion, triggers) + documentacion.
  - skill.py: una funcion run(message, context) -> str.

discover() no importa las skills como paquetes de Python: las carga por
ruta de archivo con importlib, para que agregar una skill nueva sea
"crear una carpeta", nunca "editar un modulo central que las liste a mano".
"""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import frontmatter


@dataclass
class Skill:
    name: str
    description: str
    triggers: list[str]
    run: Callable[[str, "object"], str]
    doc_path: Path


def discover(skills_dir: Path) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        doc_path = skill_dir / "SKILL.md"
        code_path = skill_dir / "skill.py"
        if not doc_path.exists() or not code_path.exists():
            continue

        parsed = frontmatter.parse(doc_path.read_text(encoding="utf-8"))
        metadata = parsed.metadata

        name = metadata.get("name", skill_dir.name)
        triggers = metadata.get("triggers", [])
        if isinstance(triggers, str):
            triggers = [triggers]

        module = _load_module(name, code_path)
        if not hasattr(module, "run"):
            raise AttributeError(f"La skill '{name}' no define run(message, context) en skill.py.")

        skills[name] = Skill(
            name=name,
            description=metadata.get("description", ""),
            triggers=triggers,
            run=module.run,
            doc_path=doc_path,
        )

    return skills


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(f"skills.{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar la skill desde {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
