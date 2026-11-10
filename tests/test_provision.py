import unittest
from pathlib import Path

from scripts.provision import FOLDER, LANGUAGES, MARKDOWN, plan


class ProvisionTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {"personal": []}
        self.contents = {}

    def run_install(self, languages):
        for _ in range(12):
            batch = plan("personal", languages, self.inventory)
            self.assertFalse(batch["list_parent_ids"])
            if not batch["operations"]:
                return batch["ids"]
            for operation in batch["operations"]:
                args = operation["args"]
                path = operation["path"]
                item_id = f"id-{path}"
                if operation["action"] == "create_folder":
                    parent, name, mime = args["parent_folder"], args["name"], FOLDER
                    self.inventory[item_id] = []
                else:
                    parent, name, mime = args["parent_folder_id"], args["file_name"], MARKDOWN
                    self.assertNotIn(item_id, self.contents)
                    self.contents[item_id] = Path(args["file_uri"]).read_text(encoding="utf-8")
                self.inventory[parent].append({"id": item_id, "title": name, "mime_type": mime})
        self.fail("Provisionamento não convergiu")

    def test_repeat_and_extend(self):
        first = self.run_install(["es-ES"])
        progress = first["languages/spanish/progresso/08-registro-progresso.md"]
        self.contents[progress] = "Evidência fictícia F002"
        self.assertEqual(first, self.run_install(["es-ES"]))
        complete = self.run_install(list(LANGUAGES))
        self.assertEqual(first.items() & complete.items(), first.items())
        self.assertEqual(self.contents[progress], "Evidência fictícia F002")
        for lang in LANGUAGES.values():
            for suffix in ("diagnosticos/09-roteiro-diagnostico-inicial.md", "aulas/MODELO.md",
                           "progresso/historico", "estado/sessao-ativa.md", "conteudo/essentials.md", "planos"):
                self.assertIn(f"languages/{lang}/{suffix}", complete)

    def test_unlisted_parent_and_lost_response(self):
        self.assertEqual(plan("personal", ["en-US"], {})["operations"], [])
        self.inventory["personal"].append({"id": "old", "title": "languages", "mime_type": FOLDER})
        batch = plan("personal", ["en-US"], self.inventory)
        self.assertEqual(batch["list_parent_ids"], ["old"])
        self.assertEqual([op["path"] for op in batch["operations"]], ["config"])

    def test_collisions(self):
        for entries in ([MARKDOWN], [FOLDER, FOLDER]):
            self.inventory["personal"] = [
                {"id": str(i), "title": "languages", "mime_type": mime} for i, mime in enumerate(entries)]
            with self.assertRaises(ValueError):
                plan("personal", ["en-US"], self.inventory)

    def test_requires_personal_folder(self):
        with self.assertRaises(ValueError):
            plan("root", ["en-US"], {})
