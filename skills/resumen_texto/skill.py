"""Skill: resumen_texto.

A diferencia de las demas skills, esta puede apoyarse en el LLM del
agente (context.provider) cuando hay uno real configurado, y cae a un
resumen extractivo local cuando no lo hay (MockProvider).
"""
from __future__ import annotations


def run(message: str, context) -> str:
    texto = _extract_text(message, context)
    if texto is None:
        return "Indica el texto a resumir, por ejemplo: 'resume: <texto>' o 'resume archivo ejemplo_texto.txt'."

    provider = getattr(context, "provider", None)
    if provider is not None and getattr(provider, "name", "mock") != "mock":
        resumen = provider.generate(
            system_prompt="Resume el siguiente texto en maximo 3 lineas, en espanol, sin inventar datos.",
            message=texto,
            history=[],
        )
        return f"Resumen (IA):\n{resumen}"

    return f"Resumen (extractivo):\n{_resumen_extractivo(texto)}"


def _extract_text(message: str, context) -> str | None:
    lowered = message.lower()
    if "archivo" in lowered:
        nombre = message.strip().split()[-1]
        ruta = context.data_dir / nombre
        if ruta.exists():
            return ruta.read_text(encoding="utf-8")
        return None
    if ":" in message:
        return message.split(":", 1)[1].strip()
    return None


def _resumen_extractivo(texto: str, max_oraciones: int = 2) -> str:
    oraciones = [o.strip() for o in texto.replace("\n", " ").split(".") if o.strip()]
    if not oraciones:
        return texto
    return ". ".join(oraciones[:max_oraciones]) + "."
