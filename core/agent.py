"""Orquestacion del agente: la parte "logica" del triangulo
logica / configuracion / comportamiento.

Agent no sabe que skills concretas existen ni como esta redactada la
personalidad de un agente en particular: recibe un AgentConfig (config.py)
y un diccionario de Skill (skill_registry.py) ya descubiertas, y solo
decide, mensaje a mensaje, si una skill puede responder o si hay que
recurrir al LLM configurado.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import AgentConfig
from .llm_provider import LLMProvider, get_provider
from .skill_registry import Skill


@dataclass
class AgentContext:
    """Lo que una skill puede necesitar del agente que la invoca."""

    agent_name: str
    data_dir: Path
    provider: Optional[LLMProvider] = None


@dataclass
class AgentResponse:
    text: str
    source: str


class Agent:
    def __init__(self, config: AgentConfig, skills: dict[str, Skill], data_dir: Path):
        self.config = config
        self.skills = {name: skill for name, skill in skills.items() if name in config.enabled_skills}

        provider_name = os.environ.get("LLM_PROVIDER", config.llm_provider)
        self.provider = get_provider(provider_name)
        self.context = AgentContext(agent_name=config.name, data_dir=data_dir, provider=self.provider)
        self.history: list[tuple[str, str]] = []

    def handle_message(self, message: str) -> AgentResponse:
        skill = self._match_skill(message)
        if skill is not None:
            text = skill.run(message, self.context)
            response = AgentResponse(text=text, source=f"skill:{skill.name}")
        else:
            text = self.provider.generate(self.config.system_prompt, message, self.history)
            response = AgentResponse(text=text, source=f"llm:{self.provider.name}")

        self.history.append((message, response.text))
        self.history = self.history[-10:]
        return response

    def _match_skill(self, message: str) -> Optional[Skill]:
        lowered = message.lower()
        for name in self.config.enabled_skills:
            skill = self.skills.get(name)
            if skill is None:
                continue
            if any(trigger.lower() in lowered for trigger in skill.triggers):
                return skill
        return None
