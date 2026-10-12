import unittest
from pathlib import Path

from core.skill_registry import discover

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


class SkillRegistryTests(unittest.TestCase):
    def test_discovers_all_skills_with_metadata(self):
        skills = discover(SKILLS_DIR)

        esperadas = {"calculadora", "gestor_tareas", "resumen_texto", "buscador_archivos"}
        self.assertEqual(esperadas, set(skills.keys()))

        for skill in skills.values():
            self.assertTrue(skill.description)
            self.assertTrue(callable(skill.run))

    def test_skill_has_triggers(self):
        skills = discover(SKILLS_DIR)

        self.assertIn("calcula", skills["calculadora"].triggers)


if __name__ == "__main__":
    unittest.main()
