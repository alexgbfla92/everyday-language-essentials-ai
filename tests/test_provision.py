import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "talkgo"))

from scripts.layout import ASSETS, MANIFEST, Layout, available_locales, build_manifest, locale_code  # noqa: E402
from scripts.provision import (DOC, FOLDER, JSON, LANGUAGES, MARKDOWN, SHEET, apply_local,  # noqa: E402
                               main, next_operations, sheet_spec)

CREATED = {"text/plain": DOC, "text/csv": SHEET, MARKDOWN: MARKDOWN, JSON: JSON}


class LayoutTests(unittest.TestCase):
    def test_native_language_picks_the_locale(self):
        for native, code in (("pt-BR", "pt-BR"), ("pt", "pt-BR"), ("es-MX", "es"), ("fr-CA", "fr"),
                             ("de-AT", "de"), ("en-GB", "en"), ("ja", "en"), ("", "en")):
            self.assertEqual(locale_code(native), code, native)

    def test_folder_and_file_names_follow_the_native_language(self):
        en, pt = Layout.for_native("en"), Layout.for_native("pt-BR")
        self.assertEqual(en.missions("en-US"), "Languages/English/Missions")
        self.assertEqual(pt.missions("en-US"), "Idiomas/Inglês/Missões")
        self.assertEqual(pt.practices("es-ES"), "Idiomas/Espanhol/Práticas")
        self.assertEqual(Layout.for_native("de").progress_log("fr-FR"),
                         "Sprachen/Französisch/Fortschritt/fortschrittsprotokoll.md")
        self.assertEqual(pt.prefix("practice"), "pratica")
        self.assertEqual(pt.status_label("paused"), "Em andamento (pausada)")
        self.assertEqual(Layout.for_native("ja").native, "ja")
        self.assertEqual(Layout.for_native("ja").missions("en-US"), "Languages/English/Missions")

    def test_every_locale_renders_every_template_without_tokens(self):
        for native in available_locales():
            layout = Layout.for_native(native)
            for template in ("central-state", "learner-profile", "active-session", "recent-context",
                             "current-profile", "history-readme", "progress-log", "diagnostic", "practice", "mission"):
                text = layout.render(template, "en-US")
                self.assertNotIn("[[", text, (native, template))
                self.assertNotIn("{{", text, (native, template))
            self.assertIn(f"native_language: {native}", layout.render("central-state"))

    def test_records_keep_english_machine_keys_in_every_locale(self):
        for native in available_locales():
            layout = Layout.for_native(native)
            practice = layout.render("practice", "en-US")
            for key in ("practice_id:", "mission_id:", "situation:", "status: prepared", "closing_next_step:",
                        "lab_url:", "lab_suggested_after_closing:"):
                self.assertIn(key, practice, (native, key))
            mission = layout.render("mission")
            for key in ("mission_id:", "mission_title:", "mission_description:", "mission_target_date:",
                        "mission_status: active"):
                self.assertIn(key, mission, (native, key))
            state = layout.render("central-state")
            for key in ("default_language:", "default_missions:", "phrase_counter:", "dialogue_counter:"):
                self.assertIn(key, state, (native, key))


class ProvisionTests(unittest.TestCase):
    """Simulates the connector: create_file turns text/plain into a Doc and text/csv into a Sheet ("Untitled")."""

    native = "pt-BR"

    def setUp(self):
        self.inventory = {"personal": []}
        self.contents = {}
        self.tabs = {}
        self.inspect = True
        self.layout = Layout.for_native(self.native)

    def run_install(self, languages):
        for _ in range(20):
            batch = next_operations("personal", languages, self.inventory, self.tabs if self.inspect else None,
                                    self.native)
            self.assertFalse(batch["list_parent_ids"])
            if not batch["operations"] and not batch["inspect_sheet_ids"]:
                return batch
            for operation in batch["operations"]:
                self.apply(operation)
            if not self.inspect:
                return batch
        self.fail("Provisioning did not converge")

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
                self.contents[item_id] = args["content"]
        self.inventory[args["parent_folder_id"]].append({"id": item_id, "title": args["name"], "mime_type": mime})

    def test_formats_names_and_mimes(self):
        batch = self.run_install(["en-US"])
        kinds, ids, layout = batch["kinds"], batch["ids"], self.layout
        self.assertEqual(kinds[MANIFEST], "manifest")
        self.assertEqual(json.loads(self.contents[ids[MANIFEST]])["native_language"], "pt-BR")
        self.assertEqual(kinds[layout.central_state()], "google-doc")
        self.assertEqual(kinds[layout.learner_profile()], "google-doc")
        self.assertEqual(kinds[layout.history_readme("en-US")], "markdown")
        for path in (layout.active_session("en-US"), layout.recent_context("en-US"), layout.current_profile("en-US")):
            self.assertEqual(kinds[path], "google-doc")
        sheet = ids[layout.progress_log("en-US")]
        self.assertEqual(kinds[layout.progress_log("en-US")], "google-sheet")
        self.assertEqual(self.tabs[sheet], ["Resumo", "Práticas"])
        self.assertTrue(self.contents[sheet].startswith("Campo,Valor\nIdioma,Inglês americano (en-US)\n"))
        titles = {item["title"] for items in self.inventory.values() for item in items}
        for title in ("Configuração", "Idiomas", "Inglês", "Missões", "Práticas", "Diagnósticos",
                      "estado-central", "registro-progresso", "LEIAME.md", MANIFEST):
            self.assertIn(title, titles)
        self.assertFalse({"Settings", "Missions", "missoes", "praticas"} & titles)

    def test_session_and_mission_classification(self):
        layout = self.layout
        self.assertEqual(layout.classify(f"{layout.practices('es-ES')}/pratica-20261110-01.md"), "google-doc")
        self.assertEqual(layout.classify(f"{layout.diagnostics('fr-FR')}/diagnostico-20261110-01.md"), "google-doc")
        self.assertEqual(layout.classify(f"{layout.missions('en-US')}/viagem-londres.md"), "google-doc")
        self.assertEqual(layout.classify(layout.history_readme("en-US")), "markdown")

    def test_sheet_tabs_follow_the_native_language(self):
        for native in available_locales():
            layout = Layout.for_native(native)
            spec = sheet_spec(layout, layout.render("progress-log", "es-ES"))
            names = [tab["name"] for tab in spec["tabs"]]
            self.assertEqual(names, [layout.m["tabs"]["summary"], layout.m["tabs"]["practices"]])
            self.assertEqual(len(spec["tabs"][0]["rows"]), 15)
            self.assertEqual(len(spec["tabs"][1]["rows"][0]), 5)

    def test_interrupted_sheet_is_configured_not_recreated(self):
        self.inspect = False
        for _ in range(20):
            batch = self.run_install(["es-ES"])
            if not any(op["action"] != "configure_sheet" for op in batch["operations"]):
                break
        self.inspect = True
        sheet = f"id-{self.layout.progress_log('es-ES')}"
        self.assertEqual(self.tabs[sheet], ["Untitled"])
        batch = next_operations("personal", ["es-ES"], self.inventory, native=self.native)
        self.assertEqual(batch["inspect_sheet_ids"], [sheet])
        self.assertFalse(batch["operations"])
        steps = next_operations("personal", ["es-ES"], self.inventory, self.tabs, self.native)["operations"]
        self.assertEqual([s["action"] for s in steps], ["configure_sheet"])
        self.assertEqual(steps[0]["args"]["rename_first_tab"], {"from": "Untitled", "to": "Resumo"})
        self.assertEqual(steps[0]["args"]["add_tabs"][0]["rows"][0][0], "ID da sessão")
        self.tabs[sheet] = ["Resumo", "Práticas"]
        self.assertFalse(next_operations("personal", ["es-ES"], self.inventory, self.tabs, self.native)["operations"])

    def test_existing_manifest_names_win(self):
        self.run_install(["en-US"])
        manifest = build_manifest("pt-BR")
        batch = next_operations("personal", ["en-US"], self.inventory, self.tabs, "en", manifest)
        self.assertFalse(batch["operations"])

    def test_repeat_and_extend(self):
        first = self.run_install(["es-ES"])["ids"]
        state = first[self.layout.current_profile("es-ES")]
        self.contents[state] = "Fictional evidence F002"
        self.assertEqual(first, self.run_install(["es-ES"])["ids"])
        complete = self.run_install(list(LANGUAGES))["ids"]
        self.assertEqual(first.items() & complete.items(), first.items())
        self.assertEqual(self.contents[state], "Fictional evidence F002")
        for tag in LANGUAGES:
            for path in (self.layout.missions(tag), self.layout.practices(tag), self.layout.diagnostics(tag),
                         self.layout.history(tag), self.layout.active_session(tag)):
                self.assertIn(path, complete)

    def test_wrong_type_is_a_conflict(self):
        self.run_install(["en-US"])
        config = next(i for i in self.inventory["personal"] if i["title"] == "Configuração")["id"]
        for item in self.inventory[config]:
            if item["title"] == "estado-central":
                item["mime_type"] = MARKDOWN
        with self.assertRaises(ValueError):
            next_operations("personal", ["en-US"], self.inventory, self.tabs, self.native)

    def test_unlisted_parent_and_lost_response(self):
        self.assertEqual(next_operations("personal", ["en-US"], {}, native=self.native)["operations"], [])
        self.inventory["personal"].append({"id": "old", "title": "Idiomas", "mime_type": FOLDER})
        batch = next_operations("personal", ["en-US"], self.inventory, native=self.native)
        self.assertEqual(batch["list_parent_ids"], ["old"])
        self.assertEqual([op["path"] for op in batch["operations"]], ["Configuração", MANIFEST])

    def test_collisions(self):
        for entries in ([MARKDOWN], [FOLDER, FOLDER]):
            self.inventory["personal"] = [
                {"id": str(i), "title": "Idiomas", "mime_type": mime} for i, mime in enumerate(entries)]
            with self.assertRaises(ValueError):
                next_operations("personal", ["en-US"], self.inventory, native=self.native)

    def test_requires_personal_folder(self):
        with self.assertRaises(ValueError):
            next_operations("root", ["en-US"], {})

    def test_cli_with_tabs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.run_install(["en-US"])
        inventory, tabs = Path(tmp.name) / "inv.json", Path(tmp.name) / "tabs.json"
        inventory.write_text(json.dumps(self.inventory), encoding="utf-8")
        tabs.write_text(json.dumps(self.tabs), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            main(["personal", str(inventory), "en-US", "--native", "pt-BR", "--tabs", str(tabs)])
        result = json.loads(out.getvalue())
        self.assertEqual((result["operations"], result["inspect_sheet_ids"]), ([], []))


class LocalProvisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "TalkGo"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_matches_drive_layout_in_each_native_language(self):
        for native in available_locales():
            root = Path(self.tmp.name) / f"c-{native}"
            root.mkdir()
            result = apply_local(root, ["es-ES"], native)
            layout = Layout.for_native(native)
            self.assertEqual(set(result["ids"]), set(layout.specification(["es-ES"])))
            self.assertEqual(json.loads((root / MANIFEST).read_text(encoding="utf-8"))["native_language"], native)
            self.assertTrue((root / layout.missions("es-ES")).is_dir())
            self.assertEqual((root / layout.recent_context("es-ES")).read_text(encoding="utf-8"),
                             layout.render("recent-context", "es-ES"))

    def test_repeat_and_extend_preserve_learner_data_and_names(self):
        apply_local(self.root, ["es-ES"], "fr")
        layout = Layout.for_native("fr")
        profile = self.root / layout.current_profile("es-ES")
        profile.write_text("evidence F001", encoding="utf-8")
        again = apply_local(self.root, ["es-ES", "en-US"], "de")
        self.assertEqual(again["native_language"], "fr")
        self.assertEqual(profile.read_text(encoding="utf-8"), "evidence F001")
        self.assertTrue((self.root / layout.practices("en-US")).is_dir())
        self.assertFalse((self.root / Layout.for_native("de").languages()).exists())

    def test_conflicts(self):
        layout = Layout.for_native("en")
        (self.root / layout.config()).write_text("not a folder", encoding="utf-8")
        with self.assertRaises(ValueError):
            apply_local(self.root, ["en-US"])

    def test_refuses_symlink_missing_root_and_package(self):
        link = Path(self.tmp.name) / "link"
        link.symlink_to(self.root, target_is_directory=True)
        for bad in (link, Path(self.tmp.name) / "missing", ASSETS):
            with self.assertRaises(ValueError):
                apply_local(bad, ["en-US"])

    def test_cli_local(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--local", str(self.root), "en-US", "--native", "es"])
        result = json.loads(out.getvalue())
        self.assertEqual(result["native_language"], "es")
        self.assertIn("Idiomas/Inglés/Misiones", result["created"])


class TemplateAndModuleTests(unittest.TestCase):
    def test_session_templates_have_global_phrase_and_dialogue_tables(self):
        for native in available_locales():
            layout = Layout.for_native(native)
            for template in ("practice", "diagnostic"):
                text = layout.render(template, "fr-FR")
                self.assertIn("| ID |", text)
                self.assertIn("phrase_range:", text)

    def test_practice_template_tracks_stages_and_lab(self):
        for native in available_locales():
            text = Layout.for_native(native).render("practice", "en-US")
            self.assertIn("current_stage:  # 1–7", text, native)
            self.assertIn("## Entertainment Lab", text, native)
            self.assertIn("https://www.youtube.com/watch?v=", text, native)
            self.assertIn("| 7 ", text, native)
            self.assertIn("| 0 ", text, native)

    def test_feedback_module_hands_over_to_closing_and_lab(self):
        modules = ASSETS / "modules"
        feedback = (modules / "05-performance-evaluator.md").read_text(encoding="utf-8")
        self.assertIn("Stage 6/7 · Closing", feedback)
        for name in ("01-meeting-simulator.md", "02-travel-survival.md", "03-technical-communication.md",
                     "04-listening-trainer.md"):
            self.assertIn("Entertainment Lab", (modules / name).read_text(encoding="utf-8"), name)

    def test_targets_have_notes_essentials_and_roadmap(self):
        for folder in ("english", "spanish", "french"):
            for name in ("notes.md", "essentials.md", "diagnostic-roadmap.md"):
                self.assertTrue((ASSETS / "targets" / folder / name).is_file(), (folder, name))


if __name__ == "__main__":
    unittest.main()
