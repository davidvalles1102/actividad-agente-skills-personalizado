"""Configuracion de un agente: la parte "configuracion" del triangulo
logica / configuracion / comportamiento que pide la actividad.

Un AgentConfig no sabe nada de como se ejecuta una skill ni de como se
genera una respuesta por LLM: solo describe quien es el agente y que
tiene permitido usar. Esto permite crear un agente nuevo (ver agents/*.json)
sin tocar una sola linea de core/ ni de skills/.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentConfig:
    id: str
    name: str
    role: str
    tone: str
    language: str
    system_prompt: str
    enabled_skills: list[str]
    llm_provider: str

    @staticmethod
    def load(path: Path) -> "AgentConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return AgentConfig(
            id=data["id"],
            name=data["name"],
            role=data["rol"],
            tone=data["tono"],
            language=data.get("idioma", "es"),
            system_prompt=data["system_prompt"],
            enabled_skills=data["skills_habilitadas"],
            llm_provider=data.get("llm_provider", "mock"),
        )
