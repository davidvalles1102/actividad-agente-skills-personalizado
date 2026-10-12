import unittest

from core import frontmatter


class FrontmatterTests(unittest.TestCase):
    def test_parses_scalars_and_lists(self):
        texto = (
            "---\n"
            "name: calculadora\n"
            "description: Resuelve expresiones matematicas.\n"
            "triggers:\n"
            "  - calcula\n"
            "  - suma\n"
            "---\n"
            "\n"
            "# Cuerpo\n"
            "Contenido de ejemplo.\n"
        )

        doc = frontmatter.parse(texto)

        self.assertEqual(doc.metadata["name"], "calculadora")
        self.assertEqual(doc.metadata["triggers"], ["calcula", "suma"])
        self.assertIn("Cuerpo", doc.body)

    def test_text_without_frontmatter_returns_empty_metadata(self):
        doc = frontmatter.parse("Solo texto, sin frontmatter.")

        self.assertEqual(doc.metadata, {})
        self.assertEqual(doc.body, "Solo texto, sin frontmatter.")


if __name__ == "__main__":
    unittest.main()
