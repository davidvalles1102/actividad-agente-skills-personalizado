"""Parser minimalista de front matter (subconjunto de YAML) para SKILL.md.

No se usa PyYAML a proposito: el proyecto se mantiene 100% sobre la
libreria estandar de Python (ver README, seccion "Decisiones de diseno"),
y el subconjunto que necesitamos (strings y listas simples) es pequeno.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedDocument:
    metadata: dict = field(default_factory=dict)
    body: str = ""


def parse(text: str) -> ParsedDocument:
    """Separa el bloque `---\\n...\\n---` inicial (metadata) del resto (body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ParsedDocument(metadata={}, body=text)

    metadata: dict = {}
    current_list_key: str | None = None
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("- ") and current_list_key is not None:
            metadata[current_list_key].append(stripped[2:].strip())
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                metadata[key] = []
                current_list_key = key
            else:
                metadata[key] = value
                current_list_key = None
        i += 1

    body = "\n".join(lines[i + 1 :]) if i < len(lines) else ""
    return ParsedDocument(metadata=metadata, body=body.strip())
