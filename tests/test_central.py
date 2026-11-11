import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.central import ASSETS, main, parse_language


class CentralTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.registry = self.base / "home" / "centrais.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--registro", str(self.registry), *args])
        result = json.loads(out.getvalue())
        result["_code"] = code
        return result

    def create(self, name, *languages):
        result = self.run_cli("create", "--raiz", str(self.base / name), "--nome", name, *languages)
        self.assertEqual(result["status"], "ok", result)
        return self.base / name

    def fake_lessons(self, root, folder="english"):
        (root / f"languages/{folder}/aulas/aula-20261101-01.md").write_text("aula fictícia", encoding="utf-8")
        (root / f"languages/{folder}/aulas/aula-20261102-01.md").write_text("aula fictícia", encoding="utf-8")
        (root / f"languages/{folder}/diagnosticos/diagnostico-20261030-01.md").write_text("diag", encoding="utf-8")
        (root / f"languages/{folder}/estado/sessao-ativa.md").write_text("Ativa: aula-20261102-01", encoding="utf-8")
        (root / f"languages/{folder}/estado/contexto-recente.md").write_text("contexto real", encoding="utf-8")
        (root / f"languages/{folder}/progresso/08-registro-progresso.md").write_text("2 aulas", encoding="utf-8")

    def test_language_aliases(self):
        for text, tag in [("Inglês", "en-US"), ("ingles", "en-US"), ("en", "en-US"), ("Español", "es-ES"),
                          ("espanhol", "es-ES"), ("Francês", "fr-FR"), ("fr-FR", "fr-FR")]:
            self.assertEqual(parse_language(text), tag)

    def test_create_registers_first_as_default_and_fills_state(self):
        root = self.create("Pessoal", "Inglês", "Espanhol")
        info = self.run_cli("info")
        self.assertEqual(info["padrao"], "Pessoal")
        central = info["centrais"][0]
        self.assertEqual(central["provedor"], "local")
        self.assertEqual([i["idioma"] for i in central["idiomas"]], ["Inglês", "Espanhol"])
        state = (root / "config/estado-global.md").read_text(encoding="utf-8")
        self.assertIn("nome_central: Pessoal", state)
        self.assertIn("armazenamento: pasta-local", state)
        self.assertIn("idiomas_escolhidos_pelo_aluno: [en-US, es-ES]", state)

    def test_create_adds_language_without_overwriting(self):
        root = self.create("Pessoal", "Inglês")
        self.fake_lessons(root)
        again = self.run_cli("create", "--raiz", str(root), "--nome", "Pessoal", "Francês")
        self.assertFalse(again["nova"])
        self.assertEqual(again["idiomas"], ["Inglês", "Francês"])
        self.assertEqual((root / "languages/english/progresso/08-registro-progresso.md").read_text(), "2 aulas")
        self.assertIn("idiomas_escolhidos_pelo_aluno: [en-US, fr-FR]",
                      (root / "config/estado-global.md").read_text(encoding="utf-8"))

    def test_create_asks_for_languages_and_detects_provider(self):
        self.assertEqual(self.run_cli("create", "--raiz", str(self.base / "x"))["status"], "ambiguo")
        (self.base / "OneDrive").mkdir()
        result = self.run_cli("create", "--raiz", str(self.base / "OneDrive" / "Idiomas"), "en")
        self.assertEqual(result["central"]["provedor"], "onedrive")
        self.assertEqual(result["central"]["nome"], "Idiomas")

    def test_name_and_root_conflicts(self):
        self.create("Pessoal", "en")
        clash = self.run_cli("create", "--raiz", str(self.base / "Outra"), "--nome", "pessoal", "en")
        self.assertEqual(clash["status"], "erro")

    def test_default_with_several_centrals(self):
        self.create("Pessoal", "en")
        self.create("Trabalho", "es")
        self.assertEqual(self.run_cli("info")["padrao"], "Pessoal")
        asked = self.run_cli("default")
        self.assertEqual((asked["status"], asked["_code"]), ("ambiguo", 2))
        self.assertEqual(asked["opcoes"], ["Pessoal", "Trabalho"])
        self.assertEqual(self.run_cli("default", "trabalho")["padrao"], "Trabalho")
        info = self.run_cli("info")
        self.assertEqual([c["padrao"] for c in info["centrais"]], [False, True])

    def test_reset_lessons_preview_confirm_and_backup(self):
        root = self.create("Pessoal", "en", "es")
        self.fake_lessons(root)
        asked = self.run_cli("reset", "aulas")
        self.assertEqual(asked["status"], "ambiguo")
        self.assertIn("Todos", asked["opcoes"])
        preview = self.run_cli("reset", "aulas", "Inglês")
        self.assertEqual(preview["status"], "previa")
        self.assertEqual(len(preview["remover"]), 2)
        self.assertIn("languages/english/estado/sessao-ativa.md", preview["restaurar_modelo"])
        self.assertTrue(preview["avisos"])
        self.assertTrue((root / "languages/english/aulas/aula-20261101-01.md").exists())
        done = self.run_cli("reset", "aulas", "Inglês", "--confirmar")
        self.assertEqual(done["status"], "ok")
        aulas = root / "languages/english/aulas"
        self.assertEqual(sorted(p.name for p in aulas.iterdir()), ["MODELO.md"])
        template = ASSETS / "languages/english/estado/contexto-recente.md"
        self.assertEqual((root / "languages/english/estado/contexto-recente.md").read_bytes(), template.read_bytes())
        self.assertTrue((root / "languages/english/diagnosticos/diagnostico-20261030-01.md").exists())
        self.assertEqual((root / "languages/english/progresso/08-registro-progresso.md").read_text(), "2 aulas")
        backup = root / done["backup"]
        self.assertEqual((backup / "languages/english/aulas/aula-20261101-01.md").read_text(encoding="utf-8"),
                         "aula fictícia")
        self.assertEqual(self.run_cli("reset", "aulas", "en")["mensagem"], "Nada a zerar.")

    def test_reset_diagnostic_keeps_lesson_pointer(self):
        root = self.create("Pessoal", "en")
        self.fake_lessons(root)
        done = self.run_cli("reset", "diagnostico", "--confirmar")
        self.assertEqual(done["remover"], ["languages/english/diagnosticos/diagnostico-20261030-01.md"])
        self.assertNotIn("languages/english/estado/sessao-ativa.md", done["restaurar_modelo"])
        self.assertTrue((root / "languages/english/diagnosticos/MODELO.md").exists())
        self.assertTrue((root / "languages/english/diagnosticos/09-roteiro-diagnostico-inicial.md").exists())

    def test_reset_progress(self):
        root = self.create("Pessoal", "fr")
        self.fake_lessons(root, "french")
        (root / "languages/french/progresso/historico/ciclo-1.md").write_text("resumo", encoding="utf-8")
        done = self.run_cli("reset", "progresso", "Francês", "--confirmar")
        self.assertIn("languages/french/progresso/historico/ciclo-1.md", done["remover"])
        self.assertTrue((root / "languages/french/progresso/historico/README.md").exists())
        self.assertEqual(len(list((root / "languages/french/aulas").glob("aula-*.md"))), 2)
        template = ASSETS / "languages/french/progresso/08-registro-progresso.md"
        self.assertEqual((root / "languages/french/progresso/08-registro-progresso.md").read_bytes(),
                         template.read_bytes())

    def test_reset_errors(self):
        self.create("Pessoal", "en")
        self.assertEqual(self.run_cli("reset", "aulas", "Espanhol")["status"], "erro")
        self.assertEqual(self.run_cli("reset", "aulas", "klingon")["status"], "erro")

    def test_reset_uses_default_but_central_choice_wins(self):
        self.create("Pessoal", "en")
        work = self.create("Trabalho", "en")
        self.fake_lessons(work)
        preview = self.run_cli("reset", "aulas", "en")
        self.assertEqual((preview["central"], preview["padrao"]), ("Pessoal", True))
        preview = self.run_cli("reset", "aulas", "en", "--central", "Trabalho")
        self.assertEqual((preview["central"], len(preview["remover"])), ("Trabalho", 2))

    def test_remove_requires_choice_and_name_confirmation(self):
        root = self.create("Pessoal", "en")
        self.create("Trabalho", "es")
        self.assertEqual(self.run_cli("remove")["status"], "ambiguo")
        preview = self.run_cli("remove", "--central", "Pessoal")
        self.assertEqual(preview["status"], "previa")
        self.assertTrue(root.exists())
        self.assertEqual(self.run_cli("remove", "--central", "Pessoal", "--confirmar", "Trabalho")["status"], "erro")
        self.assertTrue(root.exists())
        done = self.run_cli("remove", "--central", "Pessoal", "--confirmar", "pessoal",
                            "--backup", str(self.base / "copia.zip"))
        self.assertTrue(done["pasta_removida"])
        self.assertFalse(root.exists())
        self.assertTrue(Path(done["backup"]).is_file())
        self.assertEqual(done["padrao"], "Trabalho")
        self.assertEqual([c["nome"] for c in self.run_cli("info")["centrais"]], ["Trabalho"])

    def test_remove_refuses_non_central_folders(self):
        folder = self.base / "Documentos"
        folder.mkdir()
        (folder / "importante.txt").write_text("não apagar", encoding="utf-8")
        self.run_cli("register", "--raiz", str(folder), "--nome", "Falsa", "--provedor", "local",
                     "--acesso", "pasta-local", "en")
        result = self.run_cli("remove", "--central", "Falsa", "--confirmar", "Falsa")
        self.assertEqual(result["status"], "erro")
        self.assertTrue((folder / "importante.txt").exists())

    def test_cloud_central_only_leaves_registry(self):
        self.run_cli("register", "--raiz", "1AbCdriveFolderId", "--nome", "Drive", "--provedor",
                     "google-drive", "--acesso", "drive", "es", "fr")
        info = self.run_cli("info", "--central", "Drive")["centrais"][0]
        self.assertEqual(info["idiomas"], ["Espanhol", "Francês"])
        self.assertEqual(self.run_cli("reset", "aulas", "es")["status"], "erro")
        preview = self.run_cli("remove", "--central", "Drive")
        self.assertIn("conector", preview["acao"])
        done = self.run_cli("remove", "--central", "Drive", "--confirmar", "Drive")
        self.assertFalse(done["pasta_removida"])
        self.assertEqual(self.run_cli("info")["centrais"], [])

    def test_info_without_centrals(self):
        info = self.run_cli("info")
        self.assertEqual((info["status"], info["centrais"]), ("ok", []))


if __name__ == "__main__":
    unittest.main()
