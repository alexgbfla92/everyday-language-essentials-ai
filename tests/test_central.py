import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "talkgo"))

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

    def fake_practices(self, root, folder="english"):
        (root / f"languages/{folder}/praticas/pratica-20261101-01.md").write_text("prática fictícia", encoding="utf-8")
        (root / f"languages/{folder}/praticas/pratica-20261102-01.md").write_text("prática fictícia", encoding="utf-8")
        (root / f"languages/{folder}/diagnosticos/diagnostico-20261030-01.md").write_text("diag", encoding="utf-8")
        (root / f"languages/{folder}/estado/sessao-ativa.md").write_text("Ativa: pratica-20261102-01", encoding="utf-8")
        (root / f"languages/{folder}/estado/contexto-recente.md").write_text("contexto real", encoding="utf-8")
        (root / f"languages/{folder}/progresso/08-registro-progresso.md").write_text("2 práticas", encoding="utf-8")

    def test_info_lists_missions_with_target_date_and_status(self):
        root = self.create("Pessoal", "en")
        template = (ASSETS / "modelos" / "missao.md").read_text(encoding="utf-8")
        missions = root / "languages/english/missoes"
        (missions / "viagem-londres.md").write_text(
            template.replace("missao_id:  #", "missao_id: viagem-londres  #", 1)
            .replace("missao_titulo:  #", "missao_titulo: Me preparar para uma viagem a Londres  #", 1)
            .replace("missao_data_alvo:  #", "missao_data_alvo: 20/04/2027  #", 1), encoding="utf-8")
        (missions / "reunioes.md").write_text(template.replace("missao_status: ativa", "missao_status: pausada", 1),
                                              encoding="utf-8")
        english = self.run_cli("info")["centrais"][0]["idiomas"][0]
        self.assertEqual(english["missoes"], 2)
        self.assertEqual(english["lista_missoes"], [
            {"id": "reunioes", "titulo": "reunioes", "data_alvo": None, "status": "pausada"},
            {"id": "viagem-londres", "titulo": "Me preparar para uma viagem a Londres", "data_alvo": "20/04/2027",
             "status": "ativa"}])

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
        self.assertIn("formato_registros: markdown", state)
        self.assertEqual(central["formato_registros"], "markdown")
        self.assertIn("idiomas_escolhidos_pelo_aluno: [en-US, es-ES]", state)

    def test_create_adds_language_without_overwriting(self):
        root = self.create("Pessoal", "Inglês")
        self.fake_practices(root)
        again = self.run_cli("create", "--raiz", str(root), "--nome", "Pessoal", "Francês")
        self.assertFalse(again["nova"])
        self.assertEqual(again["idiomas"], ["Inglês", "Francês"])
        self.assertEqual((root / "languages/english/progresso/08-registro-progresso.md").read_text(), "2 práticas")
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

    def test_reset_practices_preview_confirm_and_backup(self):
        root = self.create("Pessoal", "en", "es")
        self.fake_practices(root)
        asked = self.run_cli("reset", "praticas")
        self.assertEqual(asked["status"], "ambiguo")
        self.assertIn("Todos", asked["opcoes"])
        preview = self.run_cli("reset", "praticas", "Inglês")
        self.assertEqual(preview["status"], "previa")
        self.assertEqual(len(preview["remover"]), 2)
        self.assertIn("languages/english/estado/sessao-ativa.md", preview["restaurar_modelo"])
        self.assertTrue((root / "languages/english/praticas/pratica-20261101-01.md").exists())
        done = self.run_cli("reset", "praticas", "Inglês", "--confirmar")
        self.assertEqual(done["status"], "ok")
        praticas = root / "languages/english/praticas"
        self.assertEqual(sorted(p.name for p in praticas.iterdir()), ["MODELO.md"])
        template = ASSETS / "languages/english/estado/contexto-recente.md"
        self.assertEqual((root / "languages/english/estado/contexto-recente.md").read_bytes(), template.read_bytes())
        self.assertTrue((root / "languages/english/diagnosticos/diagnostico-20261030-01.md").exists())
        self.assertEqual((root / "languages/english/progresso/08-registro-progresso.md").read_text(), "2 práticas")
        backup = root / done["backup"]
        self.assertEqual((backup / "languages/english/praticas/pratica-20261101-01.md").read_text(encoding="utf-8"),
                         "prática fictícia")
        self.assertEqual(self.run_cli("reset", "praticas", "en")["mensagem"], "Nada a zerar.")

    def test_reset_practices_erases_every_trace_of_the_practices(self):
        root = self.create("Pessoal", "en")
        base = root / "languages/english"
        (base / "praticas/pratica-20261101-01.md").write_text("status: Concluída", encoding="utf-8")
        (base / "praticas/pratica-20261102-01.md").write_text("status: Em andamento (pausada)", encoding="utf-8")
        template = (ASSETS / "modelos" / "missao.md").read_text(encoding="utf-8")
        mission = template.replace("| Nº | Situação | O que o aluno precisa conseguir fazer |\n|---|---|---|",
                                   "| Nº | Situação | O que o aluno precisa conseguir fazer |\n|---|---|---|\n"
                                   "| 1 | Aeroporto | Fazer o check-in |\n| 2 | Restaurante | Pedir e pagar |")
        mission = mission.replace("| Prática | Data | Situação | Status |\n|---|---|---|---|",
                                  "| Prática | Data | Situação | Status |\n|---|---|---|---|\n"
                                  "| pratica-20261101-01 | 01/11/2026 | Aeroporto | Concluída, excluída no reset |\n"
                                  "| pratica-20261102-01 | 02/11/2026 | Restaurante | Em andamento (pausada) |")
        (base / "missoes/viagem-londres.md").write_text(mission, encoding="utf-8")
        progress_path = base / "progresso/08-registro-progresso.md"
        progress = progress_path.read_text(encoding="utf-8")
        progress = progress.replace("| Completed regular practices | 0 (tests excluded) |",
                                    "| Completed regular practices | 2 |")
        progress = progress.replace("| Actual observed duration | None observed |", "| Actual observed duration | 38 min |")
        progress += "| pratica-20261101-01 | 2026-11-01 | Check-in | F1-F20 | Hotel |\n"
        progress_path.write_text(progress, encoding="utf-8")
        preview = self.run_cli("reset", "praticas", "en")
        self.assertEqual(sorted(preview["ajustar"]), ["languages/english/missoes/viagem-londres.md",
                                                      "languages/english/progresso/08-registro-progresso.md"])
        done = self.run_cli("reset", "praticas", "en", "--confirmar")
        self.assertEqual(done["status"], "ok")
        mission_now = (base / "missoes/viagem-londres.md").read_text(encoding="utf-8")
        self.assertNotIn("pratica-2026", mission_now)
        self.assertNotIn("excluída", mission_now)
        self.assertIn("| 1 | Aeroporto | Fazer o check-in |", mission_now)
        self.assertIn("| 2 | Restaurante | Pedir e pagar |", mission_now)
        progress_now = progress_path.read_text(encoding="utf-8")
        self.assertNotIn("pratica-20261101-01", progress_now)
        self.assertIn("| Completed regular practices | 0 (tests excluded) |", progress_now)
        self.assertIn("| Actual observed duration | None observed |", progress_now)
        self.assertEqual(self.run_cli("info")["centrais"][0]["idiomas"][0]["praticas"], 0)
        backup = root / done["backup"]
        self.assertIn("excluída no reset",
                      (backup / "languages/english/missoes/viagem-londres.md").read_text(encoding="utf-8"))
        self.assertEqual(self.run_cli("reset", "praticas", "en")["mensagem"], "Nada a zerar.")

    def mission(self, root, folder, mission_id, title):
        template = (ASSETS / "modelos" / "missao.md").read_text(encoding="utf-8")
        text = (template.replace("missao_id:  #", f"missao_id: {mission_id}  #", 1)
                .replace("missao_titulo:  #", f"missao_titulo: {title}  #", 1))
        (root / f"languages/{folder}/missoes/{mission_id}.md").write_text(text, encoding="utf-8")

    def practice(self, root, folder, practice_id, mission_id, status, situation="Aeroporto"):
        text = f"missao_id: {mission_id}\nsituacao: {situation}\nstatus: {status}\n"
        (root / f"languages/{folder}/praticas/{practice_id}.md").write_text(text, encoding="utf-8")

    def test_language_and_mission_defaults(self):
        root = self.create("Pessoal", "Espanhol", "Inglês")
        state = (root / "config/estado-global.md").read_text(encoding="utf-8")
        self.assertIn("idioma_padrao: es-ES", state)
        asked = self.run_cli("practices")
        self.assertEqual((asked["status"], asked["opcoes"], asked["padrao"]), ("ambiguo", ["Espanhol", "Inglês"],
                                                                               "Espanhol"))
        self.assertEqual(self.run_cli("default", "--idioma", "en")["padrao"], "Inglês")
        self.assertEqual(self.run_cli("practices")["opcoes"][0], "Inglês")
        self.mission(root, "english", "viagem-londres", "Viagem a Londres")
        self.mission(root, "english", "reunioes", "Reuniões")
        done = self.run_cli("default", "--missao", "Viagem a Londres", "--idioma", "en")
        self.assertEqual((done["nivel"], done["padrao"]), ("mission", "viagem-londres"))
        info = self.run_cli("info")["centrais"][0]["idiomas"]
        english = next(i for i in info if i["tag"] == "en-US")
        self.assertEqual((english["padrao"], english["missao_padrao"]), (True, "viagem-londres"))
        self.assertEqual(self.run_cli("default", "--missao", "nada", "--idioma", "en")["status"], "erro")

    def test_get_practices_groups_by_mission_and_status(self):
        root = self.create("Pessoal", "en")
        self.mission(root, "english", "viagem-londres", "Viagem a Londres")
        self.mission(root, "english", "reunioes", "Reuniões")
        self.run_cli("default", "--missao", "reunioes", "--idioma", "en")
        self.practice(root, "english", "pratica-20261110-01", "viagem-londres", "Concluída")
        self.practice(root, "english", "pratica-20261111-01", "viagem-londres", "Em andamento (pausada)", "Hotel")
        self.practice(root, "english", "pratica-20261112-01", "reunioes", "Concluída")
        listed = self.run_cli("practices")
        self.assertEqual(listed["total"], 3)
        self.assertEqual([m["id"] for m in listed["missoes"]], ["reunioes", "viagem-londres"])
        self.assertTrue(listed["missoes"][0]["padrao"])
        london = listed["missoes"][1]
        self.assertEqual([g["status"] for g in london["praticas"]], ["Em andamento (pausada)", "Concluída"])
        self.assertEqual(london["praticas"][0]["itens"][0]["data"], "11/11/2026")
        paused = self.run_cli("practices", "--status", "pausada")
        self.assertEqual(paused["total"], 1)
        self.assertEqual(self.run_cli("practices", "--missao", "reunioes")["total"], 1)

    def test_remove_mission_with_preview_backup_and_id_confirmation(self):
        root = self.create("Pessoal", "en")
        base = root / "languages/english"
        self.mission(root, "english", "viagem-londres", "Viagem a Londres")
        self.mission(root, "english", "reunioes", "Reuniões")
        self.run_cli("default", "--missao", "viagem-londres", "--idioma", "en")
        self.practice(root, "english", "pratica-20261110-01", "viagem-londres", "Concluída")
        self.practice(root, "english", "pratica-20261112-01", "reunioes", "Concluída")
        progress_path = base / "progresso/08-registro-progresso.md"
        progress = progress_path.read_text(encoding="utf-8").replace(
            "| Completed regular practices | 0 (tests excluded) |", "| Completed regular practices | 2 |")
        progress += "| pratica-20261110-01 | 2026-11-10 | Check-in | F1-F9 | Hotel |\n"
        progress += "| pratica-20261112-01 | 2026-11-12 | Daily | F10-F20 | Status |\n"
        progress_path.write_text(progress, encoding="utf-8")
        self.assertEqual(self.run_cli("remove-mission")["status"], "ambiguo")
        preview = self.run_cli("remove-mission", "viagem-londres")
        self.assertEqual(preview["status"], "previa")
        self.assertEqual(preview["remover"], ["languages/english/missoes/viagem-londres.md",
                                              "languages/english/praticas/pratica-20261110-01.md"])
        self.assertEqual(preview["missao_padrao_depois"], "reunioes")
        self.assertTrue((base / "missoes/viagem-londres.md").exists())
        self.assertEqual(self.run_cli("remove-mission", "viagem-londres", "--confirmar", "reunioes")["status"], "erro")
        done = self.run_cli("remove-mission", "viagem-londres", "--confirmar", "viagem-londres")
        self.assertEqual(done["status"], "ok")
        self.assertFalse((base / "missoes/viagem-londres.md").exists())
        self.assertFalse((base / "praticas/pratica-20261110-01.md").exists())
        self.assertTrue((base / "praticas/pratica-20261112-01.md").exists())
        progress_now = progress_path.read_text(encoding="utf-8")
        self.assertNotIn("pratica-20261110-01", progress_now)
        self.assertIn("pratica-20261112-01", progress_now)
        self.assertIn("| Completed regular practices | 1 |", progress_now)
        self.assertTrue((root / done["backup"] / "languages/english/praticas/pratica-20261110-01.md").exists())
        english = self.run_cli("info")["centrais"][0]["idiomas"][0]
        self.assertEqual(english["missao_padrao"], "reunioes")
        self.assertEqual(self.run_cli("practices")["total"], 1)

    def test_reset_diagnostic_keeps_practice_pointer(self):
        root = self.create("Pessoal", "en")
        self.fake_practices(root)
        done = self.run_cli("reset", "diagnostico", "--confirmar")
        self.assertEqual(done["remover"], ["languages/english/diagnosticos/diagnostico-20261030-01.md"])
        self.assertNotIn("languages/english/estado/sessao-ativa.md", done["restaurar_modelo"])
        self.assertTrue((root / "languages/english/diagnosticos/MODELO.md").exists())
        self.assertTrue((root / "languages/english/diagnosticos/09-roteiro-diagnostico-inicial.md").exists())

    def test_reset_progress(self):
        root = self.create("Pessoal", "fr")
        self.fake_practices(root, "french")
        (root / "languages/french/progresso/historico/ciclo-1.md").write_text("resumo", encoding="utf-8")
        done = self.run_cli("reset", "progresso", "Francês", "--confirmar")
        self.assertIn("languages/french/progresso/historico/ciclo-1.md", done["remover"])
        self.assertTrue((root / "languages/french/progresso/historico/README.md").exists())
        self.assertEqual(len(list((root / "languages/french/praticas").glob("pratica-*.md"))), 2)
        template = ASSETS / "languages/french/progresso/08-registro-progresso.md"
        self.assertEqual((root / "languages/french/progresso/08-registro-progresso.md").read_bytes(),
                         template.read_bytes())

    def test_reset_errors(self):
        self.create("Pessoal", "en")
        self.assertEqual(self.run_cli("reset", "praticas", "Espanhol")["status"], "erro")
        self.assertEqual(self.run_cli("reset", "praticas", "klingon")["status"], "erro")

    def test_several_centrals_ask_with_default_first_and_marked(self):
        self.create("Pessoal", "en")
        work = self.create("Trabalho", "en")
        self.fake_practices(work)
        asked = self.run_cli("reset", "praticas", "en")
        self.assertEqual((asked["status"], asked["opcoes"], asked["padrao"]),
                         ("ambiguo", ["Pessoal", "Trabalho"], "Pessoal"))
        self.run_cli("default", "Trabalho")
        asked = self.run_cli("practices", "en")
        self.assertEqual((asked["opcoes"], asked["padrao"]), (["Trabalho", "Pessoal"], "Trabalho"))
        preview = self.run_cli("reset", "praticas", "en", "--central", "Trabalho")
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
        self.assertEqual(info["formato_registros"], "nativo")
        self.assertEqual(self.run_cli("reset", "praticas", "es")["status"], "erro")
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
