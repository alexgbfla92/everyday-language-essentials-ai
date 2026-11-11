"""Cenários do Entertainment Lab: o registro da sessão decide se a aula pode começar e terminar."""
import io
import json
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "everylang"))
from scripts.lab import check_closing, check_ready, fields, main  # noqa: E402
from scripts.provision import ASSETS, LANGUAGES  # noqa: E402

READY = {
    "lab_status": "pronto",
    "lab_titulo": "At the Airport — Check-in Conversation",
    "lab_canal": "Canal Fictício",
    "lab_url": "https://youtu.be/dQw4w9WgXcQ",
    "lab_idioma_variante": "inglês americano",
    "lab_duracao_aula_min": "20",
    "lab_duracao_video_min": "8:30",
    "lab_trecho": "inteiro",
    "lab_transcricao": "legendas_indicadas",
    "lab_itens_da_aula": "boarding pass, aisle seat, carry-on",
    "lab_pergunta_1": "What does the passenger ask for?",
    "lab_tarefa": "Peça um assento no corredor usando 'Could I…?'",
    "lab_verificado_em": "2026-11-11 17:05",
}


def session(folder, values):
    """Preenche o modelo de aula do idioma como a skill faria."""
    text = (ASSETS / "languages" / folder / "aulas" / "MODELO.md").read_text(encoding="utf-8")
    for key, value in values.items():
        pattern = re.compile(rf"^{key}:.*$", re.M)
        text = pattern.sub(f"{key}: {value}", text) if pattern.search(text) else text + f"\n{key}: {value}"
    return text


class LabScenarioTests(unittest.TestCase):
    def ready(self, values, folder="english"):
        return check_ready(fields(session(folder, values)))

    def closing(self, values, folder="english"):
        return check_closing(fields(session(folder, values)))

    def test_blank_template_blocks_stage_1_in_every_language(self):
        for folder in LANGUAGES.values():
            result = self.ready({}, folder)
            self.assertFalse(result["pode_iniciar"], folder)
            self.assertEqual(result["status"], "a_preparar")

    def test_scenario_video_available(self):
        result = self.ready(READY)
        self.assertTrue(result["pode_iniciar"], result)
        self.assertEqual(result["minutos_assistidos"], 8.5)
        for folder in LANGUAGES.values():
            self.assertTrue(self.ready(READY, folder)["pode_iniciar"], folder)

    def test_ready_requires_reread_and_valid_material(self):
        for change, expected in (
            ({"lab_verificado_em": ""}, "lab_verificado_em"),
            ({"lab_url": "https://www.oxfordonlineenglish.com/airport-english"}, "YouTube"),
            ({"lab_transcricao": "sim"}, "lab_transcricao"),
            ({"lab_pergunta_1": ""}, "pergunta"),
            ({"lab_tarefa": ""}, "lab_tarefa"),
            ({"lab_duracao_video_min": "25"}, "fora de 6–10"),
            ({"lab_trecho": "02:00-01:00"}, "lab_trecho"),
            ({"lab_trecho": "05:00-12:00"}, "lab_trecho"),
        ):
            result = self.ready({**READY, **change})
            self.assertFalse(result["pode_iniciar"], change)
            self.assertTrue(any(expected in p for p in result["problemas"]), (change, result))

    def test_closest_video_outside_range_needs_reason(self):
        result = self.ready({**READY, "lab_duracao_video_min": "12", "lab_motivo_fora_da_faixa":
                             "único vídeo de check-in no aeroporto em inglês americano para o nível"})
        self.assertTrue(result["pode_iniciar"], result)
        self.assertTrue(result["avisos"])
        segment = self.ready({**READY, "lab_duracao_video_min": "35:00", "lab_trecho": "02:10-10:40"})
        self.assertTrue(segment["pode_iniciar"], segment)

    def test_one_off_short_lesson_scales_the_lab_range(self):
        short = {**READY, "lab_duracao_aula_min": "5", "lab_duracao_video_min": "2:10"}
        self.assertTrue(self.ready(short)["pode_iniciar"])
        too_long = self.ready({**short, "lab_duracao_video_min": "8:30"})
        self.assertFalse(too_long["pode_iniciar"])
        self.assertTrue(any("1.5–2.5" in p for p in too_long["problemas"]), too_long)
        segment = self.ready({**short, "lab_duracao_video_min": "8:30", "lab_trecho": "01:00-03:00"})
        self.assertTrue(segment["pode_iniciar"], segment)

    def test_scenario_search_failure_is_never_silent(self):
        silent = self.ready({"lab_status": "pendente_aceito", "lab_pendencia_motivo": "busca indisponível"})
        self.assertFalse(silent["pode_iniciar"])
        self.assertTrue(any("aceitação" in p for p in silent["problemas"]))
        accepted = self.ready({"lab_status": "pendente_aceito", "lab_pendencia_motivo": "busca indisponível",
                               "lab_pendencia_aceita_pelo_aluno": "sim, 2026-11-11 17:00"})
        self.assertTrue(accepted["pode_iniciar"])

    def test_scenario_voice_start_without_access(self):
        # Em voz sem acesso, nada é gravado: o registro continua a_preparar e a aula não pode começar.
        self.assertFalse(self.ready({})["pode_iniciar"])

    def test_scenario_resume_rechecks_lab(self):
        paused = {"lab_status": "a_preparar"}
        self.assertFalse(self.ready(paused)["pode_iniciar"])
        self.assertTrue(self.ready(READY)["pode_iniciar"])

    def test_scenario_close_request_requires_full_checklist(self):
        only_saved = {**READY, "encerramento_aula_salva_relida": "sim"}
        result = self.closing(only_saved)
        self.assertFalse(result["pode_encerrar"])
        self.assertEqual(len(result["problemas"]), 3)
        offered_no_decision = {**only_saved, "encerramento_proximo_passo": "Aula 2: hotel",
                               "lab_oferecido_na_etapa_7": "sim"}
        self.assertFalse(self.closing(offered_no_decision)["pode_encerrar"])

    def test_scenario_lab_postponed(self):
        postponed = {**READY, "encerramento_aula_salva_relida": "sim", "encerramento_proximo_passo": "Aula 2: hotel",
                     "lab_oferecido_na_etapa_7": "sim", "lab_status": "adiado"}
        self.assertFalse(self.closing(postponed)["pode_encerrar"])
        confirmed = {**postponed, "lab_gravacao_confirmada": "sim"}
        self.assertTrue(self.closing(confirmed)["pode_encerrar"])
        self.assertTrue(self.closing({**confirmed, "lab_status": "recusado"})["pode_encerrar"])
        self.assertFalse(self.closing({**confirmed, "lab_status": "feito"})["pode_encerrar"])
        self.assertTrue(self.closing({**confirmed, "lab_status": "feito", "lab_resultado": "3/3 respostas"})["pode_encerrar"])

    def test_cli_exit_codes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aula.md"
            path.write_text(session("english", READY), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["pronto", str(path)]), 0)
                self.assertEqual(main(["encerramento", str(path)]), 1)
            self.assertIn('"pode_iniciar": true', out.getvalue())


if __name__ == "__main__":
    unittest.main()
