"""Skill: buscador_archivos.

Busca por nombre dentro de context.data_dir (en vez de recorrer todo el
directorio de trabajo, como hacia legacy/agente_monolitico.py con
os.walk(".")).
"""
from __future__ import annotations


def run(message: str, context) -> str:
    patron = _extract_pattern(message)
    if not patron:
        return "Indica que nombre de archivo buscar, por ejemplo: 'busca archivo tareas'."

    coincidencias = sorted(
        str(p.relative_to(context.data_dir))
        for p in context.data_dir.rglob("*")
        if p.is_file() and patron.lower() in p.name.lower()
    )
    if not coincidencias:
        return f"No encontre archivos que coincidan con '{patron}' en {context.data_dir}."

    return "Archivos encontrados:\n" + "\n".join(f"- {c}" for c in coincidencias)


def _extract_pattern(message: str) -> str:
    lowered = message.lower()
    for prefix in ("busca archivo", "encuentra archivo", "buscar archivo"):
        if prefix in lowered:
            return message[lowered.index(prefix) + len(prefix):].strip()
    return ""
