"""Confere o registro do Entertainment Lab de uma prática, sem acessar a rede.

  python scripts/lab.py pronto ARQUIVO        # a prática pode começar? (material do Lab pronto ou falta aceita)
  python scripts/lab.py encerramento ARQUIVO  # o encerramento está completo? (prática Concluída e Lab sugerido)

O Lab não tem status próprio: quem tem status é a prática (campo `status:`).

ARQUIVO é o arquivo da sessão (Markdown) ou "-" para ler o texto pela entrada padrão
(por exemplo, o conteúdo de um Google Doc). A saída é JSON; o código de saída é 0 só
quando a conferência passa. Campos e regras em references/ENTERTAINMENT-LAB.md.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube import normalize  # noqa: E402

TRANSCRIPT = {"obtida", "legendas_indicadas", "nao_confirmada"}
SOURCES = {"pagina_youtube", "navegador", "busca"}
PRACTICE_STATUS = {"Em andamento (preparada)", "Em andamento (em execução)", "Em andamento (pausada)", "Concluída"}
REQUIRED = ["lab_titulo", "lab_canal", "lab_url", "lab_idioma_variante", "lab_duracao_pratica_min",
            "lab_duracao_video_min", "lab_trecho", "lab_transcricao", "lab_itens_da_pratica", "lab_tarefa"]
YES = {"sim", "yes", "sí", "si", "oui"}


def fields(text):
    """Lê linhas `campo: valor` (comentários após ' #' são ignorados)."""
    found = {}
    for line in text.splitlines():
        match = re.match(r"^\s*((?:lab|encerramento)_[a-z0-9_]+|status)\s*:\s*(.*)$", line)
        if match:
            raw = match.group(2)
            value = "" if raw.lstrip().startswith("#") else re.split(r"\s+#", raw, maxsplit=1)[0].strip()
            found[match.group(1)] = value
    return found


def minutes(value):
    value = value.replace(",", ".").strip()
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)
    match = re.fullmatch(r"(\d+):(\d{2})(?::(\d{2}))?", value)
    if match:
        a, b, c = match.groups()
        return int(a) * 60 + int(b) + int(c) / 60 if c else int(a) + int(b) / 60
    raise ValueError(value)


def clock(value):
    parts = [int(p) for p in value.split(":")]
    if len(parts) == 2:
        return parts[0] + parts[1] / 60
    if len(parts) == 3:
        return parts[0] * 60 + parts[1] + parts[2] / 60
    raise ValueError(value)


def check_ready(data):
    problems, warnings = [], []
    if data.get("lab_pendencia_motivo") or data.get("lab_pendencia_aceita_pelo_aluno"):
        for key in ("lab_pendencia_motivo", "lab_pendencia_aceita_pelo_aluno"):
            if not data.get(key):
                problems.append(f"{key} vazio: começar sem o vídeo só vale com motivo e aceitação registrada do aluno")
        return {"pode_iniciar": not problems, "material": "pendencia_aceita" if not problems else None,
                "problemas": problems, "avisos": warnings}
    if not data.get("lab_url") and not data.get("lab_verificado_em"):
        return {"pode_iniciar": False, "material": None,
                "problemas": ["material do Lab ainda não preparado: prepare e verifique antes da etapa 1, "
                              "ou avise a falha e peça a aceitação do aluno"], "avisos": []}
    for key in REQUIRED:
        if not data.get(key):
            problems.append(f"{key} vazio")
    questions = [data[k] for k in ("lab_pergunta_1", "lab_pergunta_2", "lab_pergunta_3") if data.get(k)]
    if not questions:
        problems.append("nenhuma pergunta (lab_pergunta_1 a 3)")
    if data.get("lab_url"):
        try:
            data["lab_url"] = normalize(data["lab_url"])
        except ValueError as error:
            problems.append(str(error))
    source = data.get("lab_fonte_verificacao", "")
    if source not in SOURCES:
        problems.append(f"lab_fonte_verificacao deve ser {', '.join(sorted(SOURCES))}")
    elif source == "busca":
        if not data.get("lab_evidencia_busca"):
            problems.append("lab_evidencia_busca vazio: com fonte busca, copie o resultado usado")
        if data.get("lab_trecho", "").lower() not in ("inteiro", "video inteiro", "vídeo inteiro"):
            problems.append("com fonte busca, use o vídeo inteiro (lab_trecho: inteiro): o trecho não pode ser confirmado")
    if data.get("lab_transcricao") and data["lab_transcricao"] not in TRANSCRIPT:
        problems.append(f"lab_transcricao deve ser {', '.join(sorted(TRANSCRIPT))}")
    unconfirmed = {"nao_confirmado", "nao_confirmada", "não confirmado", "não confirmada"}
    by_search = data.get("lab_fonte_verificacao") == "busca"
    for key in ("lab_canal", "lab_duracao_video_min"):
        if data.get(key, "").lower() in unconfirmed:
            if by_search:
                warnings.append(f"{key} não confirmado (fonte busca): avise o aluno na etapa 7")
            else:
                problems.append(f"{key} não confirmado: só é aceito com lab_fonte_verificacao: busca")
    duration_unknown = data.get("lab_duracao_video_min", "").lower() in unconfirmed
    watch = None
    try:
        if duration_unknown:
            raise LookupError
        practice = minutes(data.get("lab_duracao_pratica_min", ""))
        video = minutes(data.get("lab_duracao_video_min", ""))
        segment = data.get("lab_trecho", "")
        if segment.lower() in ("inteiro", "video inteiro", "vídeo inteiro", "whole", "entero", "entier"):
            watch = video
        elif segment:
            start, end = (clock(p) for p in segment.split("-", 1))
            if not start < end <= video + 0.01:
                problems.append("lab_trecho fora do vídeo ou com início depois do fim")
            watch = end - start
        if watch is not None:
            low, high = 0.3 * practice, 0.5 * practice
            if not low - 0.01 <= watch <= high + 0.01:
                if data.get("lab_motivo_fora_da_faixa"):
                    warnings.append(f"duração {watch:.1f} min fora de {low:g}–{high:g} min (motivo registrado)")
                else:
                    problems.append(f"duração {watch:.1f} min fora de {low:g}–{high:g} min sem lab_motivo_fora_da_faixa")
    except LookupError:
        pass
    except ValueError:
        problems.append("durações ou trecho em formato inválido (minutos, mm:ss ou mm:ss-mm:ss)")
    if not data.get("lab_verificado_em"):
        problems.append("lab_verificado_em vazio: o material só está pronto depois de reler o registro salvo")
    return {"pode_iniciar": not problems, "material": "pronto" if not problems else None,
            "problemas": problems, "avisos": warnings,
            "minutos_assistidos": round(watch, 1) if watch is not None else None}


def check_closing(data):
    problems = []
    status = data.get("status", "")
    if status not in PRACTICE_STATUS:
        problems.append(f"status da prática inválido ({status or 'vazio'}): use {', '.join(sorted(PRACTICE_STATUS))}")
    elif status != "Concluída":
        problems.append("prática não marcada como Concluída (status)")
    if data.get("encerramento_pratica_salva_relida", "").lower() not in YES:
        problems.append("prática não salva e relida (encerramento_pratica_salva_relida)")
    if not data.get("encerramento_proximo_passo"):
        problems.append("próximo passo não informado (encerramento_proximo_passo)")
    if data.get("lab_sugerido_apos_encerramento", "").lower() not in YES:
        problems.append("Lab não sugerido depois do encerramento (lab_sugerido_apos_encerramento)")
    return {"pode_encerrar": not problems, "status": status or None, "problemas": problems}


def main(argv):
    if len(argv) != 2 or argv[0] not in ("pronto", "encerramento"):
        print(__doc__)
        return 2
    text = sys.stdin.read() if argv[1] == "-" else Path(argv[1]).read_text(encoding="utf-8")
    data = fields(text)
    result = check_ready(data) if argv[0] == "pronto" else check_closing(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("pode_iniciar", result.get("pode_encerrar")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
