import unittest
from pathlib import Path

from core.agent import Agent
from core.config import AgentConfig
from core.llm_provider import LLMProvider
from core.skill_registry import discover

ROOT_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT_DIR / "skills"
DATA_DIR = ROOT_DIR / "data"


class FakeProvider(LLMProvider):
    name = "fake"

    def generate(self, system_prompt, message, history):
        return "respuesta-llm"


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.config = AgentConfig(
            id="test_agent",
            name="Test",
            role="Agente de prueba",
            tone="neutral",
            language="es",
            system_prompt="Eres un agente de prueba.",
            enabled_skills=["calculadora"],
            llm_provider="mock",
        )
        self.skills = discover(SKILLS_DIR)
        self.agent = Agent(config=self.config, skills=self.skills, data_dir=DATA_DIR)

    def test_routes_to_skill_when_trigger_matches(self):
        respuesta = self.agent.handle_message("calcula 3 + 3")

        self.assertEqual(respuesta.source, "skill:calculadora")
        self.assertIn("6", respuesta.text)

    def test_falls_back_to_llm_when_no_skill_matches(self):
        self.agent.provider = FakeProvider()

        respuesta = self.agent.handle_message("hola, como estas?")

        self.assertEqual(respuesta.source, "llm:fake")
        self.assertEqual(respuesta.text, "respuesta-llm")

    def test_disabled_skill_is_not_used(self):
        # gestor_tareas existe en el registro global pero no esta habilitada
        # para este agente de prueba (enabled_skills=["calculadora"]).
        self.assertNotIn("gestor_tareas", self.agent.skills)

    def test_history_is_recorded_and_trimmed(self):
        for i in range(12):
            self.agent.handle_message(f"calcula {i} + 1")

        self.assertEqual(len(self.agent.history), 10)


if __name__ == "__main__":
    unittest.main()
