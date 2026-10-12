import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core.agent import AgentContext
from core.skill_registry import discover

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


class SkillsTests(unittest.TestCase):
    def setUp(self):
        self.skills = discover(SKILLS_DIR)
        self.tmp_dir = Path(tempfile.mkdtemp())
        (self.tmp_dir / "ejemplo_texto.txt").write_text(
            "Primera oracion de prueba. Segunda oracion de prueba. Tercera oracion.",
            encoding="utf-8",
        )
        self.context = AgentContext(agent_name="Test", data_dir=self.tmp_dir, provider=None)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_calculadora(self):
        resultado = self.skills["calculadora"].run("calcula 2 + 2", self.context)
        self.assertIn("4", resultado)

    def test_calculadora_rechaza_expresion_no_numerica(self):
        resultado = self.skills["calculadora"].run("calcula por favor", self.context)
        self.assertIn("No pude calcular", resultado)

    def test_gestor_tareas_agrega_y_lista(self):
        agregar = self.skills["gestor_tareas"].run("agrega tarea probar el proyecto", self.context)
        self.assertIn("Tarea agregada", agregar)

        listar = self.skills["gestor_tareas"].run("lista tareas", self.context)
        self.assertIn("probar el proyecto", listar)

        data_file = self.tmp_dir / "tareas.json"
        self.assertTrue(data_file.exists())
        tareas = json.loads(data_file.read_text(encoding="utf-8"))
        self.assertEqual(len(tareas), 1)

    def test_gestor_tareas_completa(self):
        self.skills["gestor_tareas"].run("agrega tarea escribir el readme", self.context)
        resultado = self.skills["gestor_tareas"].run("completa tarea 1", self.context)
        self.assertIn("completada", resultado)

    def test_resumen_texto_extractivo_sin_provider(self):
        resultado = self.skills["resumen_texto"].run("resume archivo ejemplo_texto.txt", self.context)
        self.assertIn("Resumen (extractivo)", resultado)

    def test_buscador_archivos(self):
        resultado = self.skills["buscador_archivos"].run("busca archivo ejemplo", self.context)
        self.assertIn("ejemplo_texto.txt", resultado)

    def test_buscador_archivos_sin_coincidencias(self):
        resultado = self.skills["buscador_archivos"].run("busca archivo no_existe_xyz", self.context)
        self.assertIn("No encontre", resultado)


if __name__ == "__main__":
    unittest.main()
