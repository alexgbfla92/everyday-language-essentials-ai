import io
import json
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "talkgo"))

from scripts.central import main, parse_language  # noqa: E402
from scripts.layout import MANIFEST, Layout  # noqa: E402


class CentralTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.registry = self.base / "home" / "centrals.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--registry", str(self.registry), *args])
        result = json.loads(out.getvalue())
        result["_code"] = code
        return result

    def create(self, name, *languages, native="en"):
        result = self.run_cli("create", "--root", str(self.base / name), "--name", name, "--native", native,
                              *languages)
        self.assertEqual(result["status"], "ok", result)
        return self.base / name

    @staticmethod
    def layout(root):
        return Layout.read(root)

    def mission(self, root, tag, mission_id, title):
        layout = self.layout(root)
        text = (layout.render("mission").replace("mission_id:  #", f"mission_id: {mission_id}  #", 1)
                .replace("mission_title:  #", f"mission_title: {title}  #", 1)
                .replace("mission_target_date:  #", "mission_target_date: 20/04/2027  #", 1))
        path = root / layout.missions(tag) / f"{mission_id}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def practice(self, root, tag, number, mission_id, status, situation="Airport", day="20261110"):
        layout = self.layout(root)
        practice_id = f"{layout.prefix('practice')}-{day}-{number:02d}"
        text = f"practice_id: {practice_id}\nmission_id: {mission_id}\nsituation: {situation}\nstatus: {status}\n"
        (root / layout.practices(tag) / f"{practice_id}.md").write_text(text, encoding="utf-8")
        return practice_id

    def test_language_aliases(self):
        for text, tag in [("Inglês", "en-US"), ("english", "en-US"), ("en", "en-US"), ("Español", "es-ES"),
                          ("espanhol", "es-ES"), ("Français", "fr-FR"), ("fr-FR", "fr-FR"), ("Englisch", "en-US"),
                          ("Português brasileiro", "pt-BR"), ("Chinês", "zh-CN"), ("Mandarin", "zh-CN"), ("italiano", "it-IT"),
                          ("Japonês", "ja-JP"), ("Alemão", "de-DE"), ("Deutsch", "de-DE"), ("coreano", "ko-KR"), ("Híndi", "hi-IN"),
                          ("Árabe", "ar"), ("arabic", "ar")]:
            self.assertEqual(parse_language(text), tag)

    def test_create_registers_default_native_language_and_fills_state(self):
        root = self.create("Personal", "Spanish", "English", native="pt-BR")
        layout = self.layout(root)
        self.assertEqual(json.loads((root / MANIFEST).read_text(encoding="utf-8"))["native_language"], "pt-BR")
        self.assertTrue((root / "Idiomas" / "Espanhol" / "Missões").is_dir())
        state = (root / layout.central_state()).read_text(encoding="utf-8")
        for line in ("central_name: Personal", "storage: local-folder", "record_format: markdown",
                     "chosen_languages: [en-US, es-ES]", "default_language: es-ES", "native_language: pt-BR",
                     "status: configured"):
            self.assertIn(line, state)
        info = self.run_cli("info")
        self.assertEqual(info["default"], "Personal")
        central = info["centrals"][0]
        self.assertEqual((central["provider"], central["native_language"]), ("local", "pt-BR"))
        self.assertEqual([i["language"] for i in central["languages"]], ["English", "Spanish"])
        self.assertTrue(next(i for i in central["languages"] if i["tag"] == "es-ES")["default"])

    def test_add_language_keeps_records_and_native_names(self):
        root = self.create("Personal", "en", native="fr")
        layout = self.layout(root)
        profile = root / layout.current_profile("en-US")
        profile.write_text("evidence", encoding="utf-8")
        again = self.run_cli("create", "--root", str(root), "--native", "de", "French")
        self.assertFalse(again["new"])
        self.assertEqual(again["languages"], ["English", "French"])
        self.assertEqual(profile.read_text(encoding="utf-8"), "evidence")
        self.assertTrue((root / "Langues" / "Français").is_dir())

    def test_create_asks_for_languages_and_detects_provider(self):
        self.assertEqual(self.run_cli("create", "--root", str(self.base / "x"))["status"], "ambiguous")
        (self.base / "OneDrive").mkdir()
        result = self.run_cli("create", "--root", str(self.base / "OneDrive" / "Languages"), "en")
        self.assertEqual(result["central"]["provider"], "onedrive")
        self.assertEqual(result["central"]["name"], "Languages")

    def test_name_conflict(self):
        self.create("Personal", "en")
        clash = self.run_cli("create", "--root", str(self.base / "Other"), "--name", "personal", "en")
        self.assertEqual(clash["status"], "error")

    def test_several_centrals_ask_with_default_first_and_marked(self):
        self.create("Personal", "en")
        self.create("Work", "en")
        asked = self.run_cli("reset", "practices", "en")
        self.assertEqual((asked["status"], asked["options"], asked["default"]),
                         ("ambiguous", ["Personal", "Work"], "Personal"))
        self.run_cli("default", "Work")
        asked = self.run_cli("practices", "en")
        self.assertEqual((asked["options"], asked["default"]), (["Work", "Personal"], "Work"))
        self.assertEqual(self.run_cli("practices", "en", "--central", "Personal")["status"], "ok")

    def test_language_and_mission_defaults(self):
        root = self.create("Personal", "Spanish", "English")
        asked = self.run_cli("practices")
        self.assertEqual((asked["status"], asked["options"], asked["default"]),
                         ("ambiguous", ["Spanish", "English"], "Spanish"))
        self.assertEqual(self.run_cli("default", "--language", "en")["default"], "English")
        self.assertEqual(self.run_cli("practices")["options"][0], "English")
        self.mission(root, "en-US", "london-trip", "Get ready for a trip to London")
        self.mission(root, "en-US", "meetings", "Meetings")
        done = self.run_cli("default", "--mission", "Get ready for a trip to London", "--language", "en")
        self.assertEqual((done["level"], done["default"]), ("mission", "london-trip"))
        english = next(i for i in self.run_cli("info")["centrals"][0]["languages"] if i["tag"] == "en-US")
        self.assertEqual((english["default"], english["default_mission"], english["missions"]),
                         (True, "london-trip", 2))
        self.assertEqual(english["mission_list"][0]["target_date"], "20/04/2027")
        self.assertEqual(self.run_cli("default", "--mission", "none", "--language", "en")["status"], "error")

    def test_get_practices_groups_by_mission_and_status_with_native_labels(self):
        root = self.create("Personal", "en", native="pt-BR")
        self.mission(root, "en-US", "viagem-londres", "Viagem a Londres")
        self.mission(root, "en-US", "reunioes", "Reuniões")
        self.run_cli("default", "--mission", "reunioes", "--language", "en")
        self.practice(root, "en-US", 1, "viagem-londres", "completed", day="20261110")
        self.practice(root, "en-US", 1, "viagem-londres", "paused", "Hotel", day="20261111")
        self.practice(root, "en-US", 1, "reunioes", "completed", day="20261112")
        listed = self.run_cli("practices")
        self.assertEqual(listed["total"], 3)
        self.assertEqual([m["id"] for m in listed["missions"]], ["reunioes", "viagem-londres"])
        self.assertTrue(listed["missions"][0]["default"])
        london = listed["missions"][1]
        self.assertEqual([g["status"] for g in london["practices"]], ["paused", "completed"])
        self.assertEqual(london["practices"][0]["status_label"], "Em andamento (pausada)")
        self.assertEqual(london["practices"][0]["items"][0]["date"], "11/11/2026")
        self.assertEqual(london["practices"][0]["items"][0]["id"], "pratica-20261111-01")
        self.assertEqual(self.run_cli("practices", "--status", "paused")["total"], 1)
        self.assertEqual(self.run_cli("practices", "--mission", "reunioes")["total"], 1)

    def test_reset_practices_erases_every_trace_without_backup(self):
        root = self.create("Personal", "en", native="pt-BR")
        layout = self.layout(root)
        first = self.practice(root, "en-US", 1, "viagem-londres", "completed")
        second = self.practice(root, "en-US", 2, "viagem-londres", "paused")
        rows = f"| {first} | 10/11/2026 | Aeroporto | Concluída |\n| {second} | 10/11/2026 | Hotel | Em andamento (pausada) |\n"
        mission = self.mission(root, "en-US", "viagem-londres", "Viagem a Londres")
        text = mission.read_text(encoding="utf-8")
        text = text.replace("| Prática | Data | Situação | Status |\n|---|---|---|---|\n",
                            "| Prática | Data | Situação | Status |\n|---|---|---|---|\n" + rows)
        text = text.replace("|---|---|---|\n\nExemplo", "|---|---|---|\n| 1 | Aeroporto | Check-in |\n\nExemplo")
        mission.write_text(text, encoding="utf-8")
        progress_path = root / layout.progress_log("en-US")
        progress = progress_path.read_text(encoding="utf-8")
        progress = progress.replace("| Práticas regulares concluídas | 0 (testes excluídos) |",
                                    "| Práticas regulares concluídas | 2 |")
        progress = progress.replace("| Duração real observada | Nenhuma observada |", "| Duração real observada | 38 min |")
        progress += f"| {first} | 2026-11-10 | Check-in | F1-F20 | Hotel |\n"
        progress_path.write_text(progress, encoding="utf-8")
        (root / layout.active_session("en-US")).write_text(f"active_session: {second}\n", encoding="utf-8")
        preview = self.run_cli("reset", "practices", "en")
        self.assertEqual(preview["status"], "preview")
        self.assertEqual(len(preview["remove"]), 2)
        self.assertEqual(sorted(preview["adjust"]), sorted([layout.missions("en-US") + "/viagem-londres.md",
                                                            layout.progress_log("en-US")]))
        self.assertIn(layout.active_session("en-US"), preview["restore_template"])
        done = self.run_cli("reset", "practices", "en", "--confirm")
        self.assertEqual(done["status"], "ok")
        self.assertEqual(list((root / layout.practices("en-US")).iterdir()), [])
        mission_now = mission.read_text(encoding="utf-8")
        self.assertNotIn("pratica-2026", mission_now)
        self.assertIn("| 1 | Aeroporto | Check-in |", mission_now)
        progress_now = progress_path.read_text(encoding="utf-8")
        self.assertNotIn(first, progress_now)
        self.assertIn("| Práticas regulares concluídas | 0 (testes excluídos) |", progress_now)
        self.assertIn("| Duração real observada | Nenhuma observada |", progress_now)
        self.assertEqual((root / layout.active_session("en-US")).read_text(encoding="utf-8"),
                         layout.render("active-session", "en-US"))
        self.assertFalse(any("backup" in str(f).lower() for f in self.base.rglob("*")))
        self.assertEqual(self.run_cli("info")["centrals"][0]["languages"][0]["practices"], 0)
        self.assertEqual(self.run_cli("reset", "practices", "en")["message"], "Nothing to reset.")

    def test_reset_diagnostics_and_progress(self):
        root = self.create("Personal", "fr", native="de")
        layout = self.layout(root)
        (root / layout.diagnostics("fr-FR") / "diagnose-20261030-01.md").write_text("diag", encoding="utf-8")
        (root / layout.current_profile("fr-FR")).write_text("B1", encoding="utf-8")
        self.practice(root, "fr-FR", 1, None, "completed")
        done = self.run_cli("reset", "diagnostics", "--confirm")
        self.assertEqual(done["remove"], [layout.diagnostics("fr-FR") + "/diagnose-20261030-01.md"])
        self.assertEqual((root / layout.current_profile("fr-FR")).read_text(encoding="utf-8"),
                         layout.render("current-profile", "fr-FR"))
        self.assertEqual(len(list((root / layout.practices("fr-FR")).iterdir())), 1)
        (root / layout.history("fr-FR") / "cycle-1.md").write_text("summary", encoding="utf-8")
        (root / layout.progress_log("fr-FR")).write_text("changed", encoding="utf-8")
        done = self.run_cli("reset", "progress", "French", "--confirm")
        self.assertIn(layout.history("fr-FR") + "/cycle-1.md", done["remove"])
        self.assertTrue((root / layout.history_readme("fr-FR")).is_file())
        self.assertEqual((root / layout.progress_log("fr-FR")).read_text(encoding="utf-8"),
                         layout.render("progress-log", "fr-FR"))

    def test_reset_errors(self):
        self.create("Personal", "en")
        self.assertEqual(self.run_cli("reset", "practices", "Spanish")["status"], "error")
        self.assertEqual(self.run_cli("reset", "practices", "klingon")["status"], "error")

    def test_remove_mission_with_preview_and_id_confirmation(self):
        root = self.create("Personal", "en")
        layout = self.layout(root)
        self.mission(root, "en-US", "london-trip", "London trip")
        self.mission(root, "en-US", "meetings", "Meetings")
        self.run_cli("default", "--mission", "london-trip", "--language", "en")
        gone = self.practice(root, "en-US", 1, "london-trip", "completed")
        kept = self.practice(root, "en-US", 2, "meetings", "completed")
        progress_path = root / layout.progress_log("en-US")
        progress = progress_path.read_text(encoding="utf-8").replace(
            "| Completed regular practices | 0 (tests excluded) |", "| Completed regular practices | 2 |")
        progress += f"| {gone} | 2026-11-10 | Check-in | F1-F9 | Hotel |\n| {kept} | 2026-11-10 | Daily | F10 | x |\n"
        progress_path.write_text(progress, encoding="utf-8")
        self.assertEqual(self.run_cli("remove-mission")["status"], "ambiguous")
        preview = self.run_cli("remove-mission", "london-trip")
        self.assertEqual(preview["status"], "preview")
        self.assertEqual(preview["remove"], [layout.missions("en-US") + "/london-trip.md",
                                             layout.practices("en-US") + f"/{gone}.md"])
        self.assertEqual(preview["default_mission_after"], "meetings")
        self.assertEqual(self.run_cli("remove-mission", "london-trip", "--confirm", "meetings")["status"], "error")
        done = self.run_cli("remove-mission", "london-trip", "--confirm", "london-trip")
        self.assertEqual(done["status"], "ok")
        self.assertFalse((root / layout.practices("en-US") / f"{gone}.md").exists())
        self.assertTrue((root / layout.practices("en-US") / f"{kept}.md").exists())
        progress_now = progress_path.read_text(encoding="utf-8")
        self.assertNotIn(gone, progress_now)
        self.assertIn("| Completed regular practices | 1 |", progress_now)
        english = self.run_cli("info")["centrals"][0]["languages"][0]
        self.assertEqual(english["default_mission"], "meetings")
        self.assertFalse(any("backup" in str(f).lower() for f in self.base.rglob("*")))

    def test_backup_only_on_request_and_outside_the_central(self):
        root = self.create("Personal", "en")
        self.practice(root, "en-US", 1, None, "completed")
        files = sum(1 for f in root.rglob("*") if f.is_file())
        done = self.run_cli("backup")
        archive = Path(done["backup"])
        self.assertEqual(archive.parent, root.parent)
        self.assertTrue(archive.name.startswith("Personal-backup-") and archive.suffix == ".zip")
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(sum(1 for n in z.namelist() if not n.endswith("/")), files)
        self.assertEqual(self.run_cli("backup", "--destination", str(root / "Settings"))["status"], "error")
        elsewhere = self.base / "copies"
        elsewhere.mkdir()
        self.assertEqual(Path(self.run_cli("backup", "--destination", str(elsewhere))["backup"]).parent, elsewhere)

    def test_remove_requires_choice_and_name_confirmation(self):
        root = self.create("Personal", "en")
        self.create("Work", "es")
        self.assertEqual(self.run_cli("remove")["status"], "ambiguous")
        preview = self.run_cli("remove", "--central", "Personal")
        self.assertEqual(preview["status"], "preview")
        self.assertEqual(self.run_cli("remove", "--central", "Personal", "--confirm", "Work")["status"], "error")
        self.assertTrue(root.exists())
        done = self.run_cli("remove", "--central", "Personal", "--confirm", "personal")
        self.assertTrue(done["folder_removed"])
        self.assertFalse(root.exists())
        self.assertEqual(done["default"], "Work")
        self.assertEqual([p.name for p in self.base.iterdir() if p.suffix == ".zip"], [])

    def test_remove_refuses_non_central_folders(self):
        folder = self.base / "Documents"
        folder.mkdir()
        (folder / "important.txt").write_text("keep", encoding="utf-8")
        self.run_cli("register", "--root", str(folder), "--name", "Fake", "--provider", "local",
                     "--access", "local-folder", "en")
        self.assertEqual(self.run_cli("remove", "--central", "Fake", "--confirm", "Fake")["status"], "error")
        self.assertTrue((folder / "important.txt").exists())

    def test_cloud_central_only_leaves_registry(self):
        self.run_cli("register", "--root", "1AbCdriveFolderId", "--name", "Drive", "--provider", "google-drive",
                     "--access", "drive", "--native", "pt-BR", "es", "fr")
        info = self.run_cli("info", "--central", "Drive")["centrals"][0]
        self.assertEqual((info["languages"], info["record_format"], info["native_language"]),
                         (["Spanish", "French"], "native", "pt-BR"))
        self.assertEqual(self.run_cli("reset", "practices", "es")["status"], "error")
        self.assertIn("connector", self.run_cli("remove", "--central", "Drive")["action"])
        done = self.run_cli("remove", "--central", "Drive", "--confirm", "Drive")
        self.assertFalse(done["folder_removed"])
        self.assertEqual(self.run_cli("info")["centrals"], [])

    def test_info_without_centrals(self):
        info = self.run_cli("info")
        self.assertEqual((info["status"], info["centrals"]), ("ok", []))


if __name__ == "__main__":
    unittest.main()
