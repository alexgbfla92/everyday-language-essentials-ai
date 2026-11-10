import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.provision import ASSETS, FOLDER, LANGUAGES, MARKDOWN, apply_local, main, plan


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


class LocalProvisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "EverydayEssentials"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_matches_drive_layout_and_copies_templates(self):
        result = apply_local(self.root, ["es-ES"])
        drive = self.drive_paths(["es-ES"])
        self.assertEqual(set(result["ids"]), drive)
        self.assertFalse(result["existing"])
        for path in result["created"]:
            source = ASSETS.joinpath(*path.split("/"))
            target = self.root.joinpath(*path.split("/"))
            if source.is_file():
                self.assertEqual(target.read_bytes(), source.read_bytes())
            else:
                self.assertTrue(target.is_dir())
        self.assertTrue((self.root / "languages/spanish/planos").is_dir())

    def test_repeat_and_extend_preserve_learner_data(self):
        first = apply_local(self.root, ["es-ES"])
        progress = self.root / "languages/spanish/progresso/08-registro-progresso.md"
        progress.write_text("Evidência fictícia F002", encoding="utf-8")
        again = apply_local(self.root, ["es-ES"])
        self.assertFalse(again["created"])
        self.assertEqual(again["ids"], first["ids"])
        complete = apply_local(self.root, list(LANGUAGES))
        self.assertEqual(set(complete["ids"]), self.drive_paths(list(LANGUAGES)))
        self.assertEqual(progress.read_text(encoding="utf-8"), "Evidência fictícia F002")
        self.assertTrue(set(first["ids"]) <= set(complete["existing"]))

    def test_conflicts(self):
        (self.root / "languages").write_text("não é pasta", encoding="utf-8")
        with self.assertRaises(ValueError):
            apply_local(self.root, ["en-US"])
        (self.root / "languages").unlink()
        perfil = self.root / "config/perfil.md"
        if perfil.exists():
            perfil.unlink()
        perfil.mkdir(parents=True)
        with self.assertRaises(ValueError):
            apply_local(self.root, ["en-US"])

    def test_refuses_symlink_missing_root_and_package(self):
        with self.assertRaises(ValueError):
            apply_local(self.root / "inexistente", ["en-US"])
        link = Path(self.tmp.name) / "atalho"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            apply_local(link, ["en-US"])
        with self.assertRaises(ValueError):
            apply_local(ASSETS, ["en-US"])
        (self.root / "config").symlink_to(Path(self.tmp.name), target_is_directory=True)
        with self.assertRaises(ValueError):
            apply_local(self.root, ["en-US"])

    def test_cli_local(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--local", str(self.root), "fr-FR"])
        result = json.loads(out.getvalue())
        self.assertIn("languages/french/aulas/MODELO.md", result["created"])

    def drive_paths(self, languages):
        inventory, ids = {"personal": []}, None
        for _ in range(12):
            batch = plan("personal", languages, inventory)
            if not batch["operations"]:
                ids = batch["ids"]
                break
            for operation in batch["operations"]:
                args, item_id = operation["args"], f"id-{operation['path']}"
                if operation["action"] == "create_folder":
                    parent, name, mime = args["parent_folder"], args["name"], FOLDER
                    inventory[item_id] = []
                else:
                    parent, name, mime = args["parent_folder_id"], args["file_name"], MARKDOWN
                inventory[parent].append({"id": item_id, "title": name, "mime_type": mime})
        return {path for path in ids if path}
