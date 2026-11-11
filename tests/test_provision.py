import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "everylang"))

from scripts.provision import (ASSETS, DOC, FOLDER, LANGUAGES, MARKDOWN, SHEET, apply_local, classify,
                               main, plan, sheet_spec)

CREATED = {"text/plain": DOC, "text/csv": SHEET, MARKDOWN: MARKDOWN}


class ProvisionTests(unittest.TestCase):
    """Simula o conector: create_file converte text/plain em Doc e text/csv em Sheet (aba "Untitled")."""

    def setUp(self):
        self.inventory = {"personal": []}
        self.contents = {}
        self.tabs = {}
        self.inspect = True

    def run_install(self, languages):
        for _ in range(16):
            batch = plan("personal", languages, self.inventory, self.tabs if self.inspect else None)
            self.assertFalse(batch["list_parent_ids"])
            if not batch["operations"] and not batch["inspect_sheet_ids"]:
                return batch
            for operation in batch["operations"]:
                self.apply(operation)
            if not self.inspect:
                return batch
        self.fail("Provisionamento não convergiu")

    def apply(self, operation):
        args, path = operation["args"], operation["path"]
        if operation["action"] == "configure_sheet":
            tabs = self.tabs[args["spreadsheet_id"]]
            if args["rename_first_tab"]:
                tabs[0] = args["rename_first_tab"]["to"]
            tabs.extend(tab["name"] for tab in args["add_tabs"])
            return
        item_id = f"id-{path}"
        if operation["action"] == "create_folder":
            mime = FOLDER
            self.inventory[item_id] = []
        else:
            mime = CREATED[args["create_mime_type"]]
            self.assertEqual(mime, args["target_mime_type"])
            self.assertNotIn(item_id, self.contents)
            if mime == SHEET:
                self.contents[item_id] = args["csv"]
                self.tabs[item_id] = ["Untitled"]
            else:
                self.contents[item_id] = Path(args["content_file"]).read_text(encoding="utf-8")
        self.inventory[args["parent_folder_id"]].append({"id": item_id, "title": args["name"], "mime_type": mime})

    def test_formats_names_and_mimes(self):
        batch = self.run_install(["en-US"])
        kinds, ids = batch["kinds"], batch["ids"]
        self.assertEqual(kinds["config/estado-global.md"], "google-doc")
        self.assertEqual(kinds["config/perfil.md"], "google-doc")
        self.assertEqual(kinds["config/defaults.md"], "markdown")
        self.assertEqual(kinds["languages/english/config.md"], "markdown")
        self.assertEqual(kinds["languages/english/aulas/MODELO.md"], "markdown")
        self.assertEqual(kinds["languages/english/progresso/historico/README.md"], "markdown")
        for name in ("sessao-ativa", "contexto-recente", "perfil-atual"):
            self.assertEqual(kinds[f"languages/english/estado/{name}.md"], "google-doc")
        sheet = ids["languages/english/progresso/08-registro-progresso.md"]
        self.assertEqual(kinds["languages/english/progresso/08-registro-progresso.md"], "google-sheet")
        self.assertEqual(self.tabs[sheet], ["Resumo", "Aulas"])
        self.assertTrue(self.contents[sheet].startswith("Field,Value\nLanguage,American English (en-US)\n"))
        titles = {item["title"] for items in self.inventory.values() for item in items}
        self.assertIn("estado-global", titles)
        self.assertIn("08-registro-progresso", titles)
        self.assertIn("defaults.md", titles)
        self.assertNotIn("estado-global.md", titles)
        doc = ids["languages/english/estado/sessao-ativa.md"]
        self.assertEqual(self.contents[doc], (ASSETS / "languages/english/estado/sessao-ativa.md").read_text())

    def test_session_and_history_classification(self):
        self.assertEqual(classify("languages/spanish/aulas/aula-20261111-01.md"), "google-doc")
        self.assertEqual(classify("languages/french/diagnosticos/diagnostico-20261111-02.md"), "google-doc")
        self.assertEqual(classify("languages/english/planos/missao-reunioes.md"), "google-doc")
        self.assertEqual(classify("languages/english/progresso/historico/ciclo-2026-11.md"), "markdown")
        self.assertEqual(classify("languages/english/diagnosticos/09-roteiro-diagnostico-inicial.md"), "markdown")

    def test_sheet_tabs_cover_all_languages(self):
        batch = self.run_install(list(LANGUAGES))
        for folder, header in (("english", ["Session ID", "Date", "Goal", "Evidence", "Next task"]),
                               ("spanish", ["Identificador", "Fecha", "Objetivo", "Evidencias", "Próxima tarea"]),
                               ("french", ["Identifiant", "Date", "Objectif", "Preuves", "Suite"])):
            path = f"languages/{folder}/progresso/08-registro-progresso.md"
            self.assertEqual(self.tabs[batch["ids"][path]], ["Resumo", "Aulas"])
            spec = sheet_spec(path, ASSETS / path)
            self.assertEqual(spec["tabs"][1]["rows"], [header])
            self.assertEqual(len(spec["tabs"][0]["rows"]), 16)

    def test_interrupted_sheet_is_configured_not_recreated(self):
        self.inspect = False
        for _ in range(16):
            batch = self.run_install(["es-ES"])
            if not any(op["action"] != "configure_sheet" for op in batch["operations"]):
                break
        self.inspect = True
        sheet = "id-languages/spanish/progresso/08-registro-progresso.md"
        self.assertEqual(self.tabs[sheet], ["Untitled"])
        batch = plan("personal", ["es-ES"], self.inventory)
        self.assertEqual(batch["inspect_sheet_ids"], [sheet])
        self.assertFalse(batch["operations"])
        steps = plan("personal", ["es-ES"], self.inventory, self.tabs)["operations"]
        self.assertEqual([s["action"] for s in steps], ["configure_sheet"])
        self.assertEqual(steps[0]["args"]["rename_first_tab"], {"from": "Untitled", "to": "Resumo"})
        self.assertEqual(steps[0]["args"]["add_tabs"][0]["rows"][0][0], "Identificador")
        self.tabs[sheet] = ["Resumo"]
        steps = plan("personal", ["es-ES"], self.inventory, self.tabs)["operations"]
        self.assertIsNone(steps[0]["args"]["rename_first_tab"])
        self.tabs[sheet] = ["Resumo", "Aulas"]
        self.assertFalse(plan("personal", ["es-ES"], self.inventory, self.tabs)["operations"])

    def test_repeat_and_extend(self):
        first = self.run_install(["es-ES"])["ids"]
        state = first["languages/spanish/estado/perfil-atual.md"]
        self.contents[state] = "Evidência fictícia F002"
        self.assertEqual(first, self.run_install(["es-ES"])["ids"])
        complete = self.run_install(list(LANGUAGES))["ids"]
        self.assertEqual(first.items() & complete.items(), first.items())
        self.assertEqual(self.contents[state], "Evidência fictícia F002")
        for lang in LANGUAGES.values():
            for suffix in ("diagnosticos/09-roteiro-diagnostico-inicial.md", "aulas/MODELO.md",
                           "progresso/historico", "estado/sessao-ativa.md", "conteudo/essentials.md", "planos"):
                self.assertIn(f"languages/{lang}/{suffix}", complete)

    def test_wrong_type_is_a_conflict(self):
        self.run_install(["en-US"])
        config = next(i for i in self.inventory["personal"] if i["title"] == "config")["id"]
        for item in self.inventory[config]:
            if item["title"] == "estado-global":
                item["mime_type"] = MARKDOWN
        with self.assertRaises(ValueError):
            plan("personal", ["en-US"], self.inventory, self.tabs)
        for item in self.inventory[config]:
            if item["title"] == "estado-global":
                item["mime_type"] = DOC
        self.inventory[config].append({"id": "x", "title": "estado-global.md", "mime_type": MARKDOWN})
        self.assertFalse(plan("personal", ["en-US"], self.inventory, self.tabs)["operations"])

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

    def test_cli_with_tabs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.run_install(["en-US"])
        inventory, tabs = Path(tmp.name) / "inv.json", Path(tmp.name) / "abas.json"
        inventory.write_text(json.dumps(self.inventory), encoding="utf-8")
        tabs.write_text(json.dumps(self.tabs), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            main(["personal", str(inventory), "en-US", "--abas", str(tabs)])
        result = json.loads(out.getvalue())
        self.assertEqual((result["operations"], result["inspect_sheet_ids"]), ([], []))


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
        installer = ProvisionTests("run_install")
        installer.setUp()
        return {path for path in installer.run_install(languages)["ids"] if path}


class TemplateTests(unittest.TestCase):
    def test_session_templates_have_global_phrase_and_dialogue_tables(self):
        for folder in LANGUAGES.values():
            for kind in ("aulas", "diagnosticos"):
                text = (ASSETS / "languages" / folder / kind / "MODELO.md").read_text(encoding="utf-8")
                self.assertIn("F? – F? | D? – D?", text, (folder, kind))
                self.assertIn("| ID |", text)
                self.assertEqual(text.count("|---|---|---|---|---|---|"), 1 if kind == "diagnosticos" else 2)
                self.assertNotIn("F001", text)

    def test_global_counters_in_state(self):
        text = (ASSETS / "config" / "estado-global.md").read_text(encoding="utf-8")
        for field in ("contador_frases", "contador_dialogos", "ids_em_voz"):
            self.assertIn(f"{field}:", text)

    def test_templates_track_the_current_stage(self):
        for folder in LANGUAGES.values():
            lesson = (ASSETS / "languages" / folder / "aulas" / "MODELO.md").read_text(encoding="utf-8")
            diagnostic = (ASSETS / "languages" / folder / "diagnosticos" / "MODELO.md").read_text(encoding="utf-8")
            self.assertIn("(1–7)", lesson, folder)
            self.assertIn("## Entertainment Lab", lesson, folder)
            self.assertIn("https://www.youtube.com/watch?v=", lesson, folder)
            self.assertIn("30–50", lesson, folder)
            self.assertIn("(1–5)", diagnostic, folder)

