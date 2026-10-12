"""Proveedores de LLM para el flujo conversacional del agente.

Se define una interfaz comun (LLMProvider) para poder intercambiar el
"cerebro" conversacional sin tocar core.agent ni las skills. Esto separa
el comportamiento del agente (que hace, a traves de Agent y las skills)
de la implementacion concreta del modelo de lenguaje usado.

MockProvider permite ejecutar y probar todo el flujo del agente sin
necesidad de una API key, lo cual es intencional: el proyecto debe poder
instalarse y calificarse sin credenciales de terceros.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name = "base"

    @abstractmethod
    def generate(self, system_prompt: str, message: str, history: list[tuple[str, str]]) -> str:
        """Genera una respuesta conversacional para `message` dado un prompt de sistema."""


class MockProvider(LLMProvider):
    """Proveedor determinista, sin dependencias externas ni llamadas de red."""

    name = "mock"

    def generate(self, system_prompt: str, message: str, history: list[tuple[str, str]]) -> str:
        persona = system_prompt.strip().splitlines()[0] if system_prompt.strip() else "Agente"
        return (
            f"({persona}) Entiendo tu mensaje: \"{message}\". "
            "Por ahora no tengo una skill especifica para esto, "
            "pero lo registre en el historial de la conversacion."
        )


class AnthropicProvider(LLMProvider):
    """Proveedor real usando la API de Anthropic (requiere ANTHROPIC_API_KEY)."""

    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-5-5") -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no esta configurada.")
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Instala el paquete 'anthropic' (pip install anthropic).") from exc

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate(self, system_prompt: str, message: str, history: list[tuple[str, str]]) -> str:
        messages = []
        for user_msg, agent_msg in history[-5:]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": agent_msg})
        messages.append({"role": "user", "content": message})

        response = self._client.messages.create(
            model=self._model,
            max_tokens=400,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    """Proveedor real usando la API de OpenAI (requiere OPENAI_API_KEY)."""

    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no esta configurada.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Instala el paquete 'openai' (pip install openai).") from exc

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(self, system_prompt: str, message: str, history: list[tuple[str, str]]) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        for user_msg, agent_msg in history[-5:]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": agent_msg})
        messages.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(model=self._model, messages=messages)
        return response.choices[0].message.content


_PROVIDERS = {
    "mock": MockProvider,
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
}


def get_provider(name: str) -> LLMProvider:
    """Crea el proveedor solicitado y degrada a MockProvider si no esta disponible.

    La degradacion se avisa por stdout (no se oculta el fallo) pero nunca
    revienta el programa: asi el agente se puede ejecutar y revisar sin
    necesidad de API keys, documentando igual el flujo con un LLM real.
    """
    provider_cls = _PROVIDERS.get(name, MockProvider)
    try:
        return provider_cls()
    except Exception as exc:
        if provider_cls is not MockProvider:
            print(f"[aviso] No se pudo inicializar el proveedor '{name}' ({exc}). Usando MockProvider.")
        return MockProvider()
