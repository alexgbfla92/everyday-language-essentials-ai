"""Gerencie as Centrais de idioma numa pasta local, sem acessar a rede.

Comandos (a skill traduz os comandos do aluno para estes):
  info     [--central NOME]                         Get-Central
  create   --raiz PASTA [--nome N] [--provedor P] IDIOMA...   New-Central
  register --raiz ID --acesso A --provedor P --nome N IDIOMA...  (central criada por conector)
  default  [NOME]                                   Set-Default central
  default  --idioma IDIOMA [--central NOME]          Set-Default language
  default  --missao ID --idioma IDIOMA [--central NOME]  Set-Default mission
  practices [IDIOMA] [--missao ID] [--status TEXTO] [--central NOME]  Get-Practices
  remove-mission [ID] --idioma IDIOMA [--central NOME] [--confirmar ID]  Remove-Mission
  remove   [--central NOME] [--confirmar NOME] [--backup ZIP] [--somente-registro]
                                                    Remove-Central
  reset    {diagnostico,praticas,progresso} [IDIOMA] [--central NOME] [--confirmar]
                                                    Reset-Diagnostics / Reset-Practices / Reset-Progress

Sem --confirmar, remove e reset só mostram a prévia. A saída é sempre JSON com
"status": ok | previa | ambiguo | erro. Em "ambiguo", pergunte ao aluno usando "opcoes", com a
opção "padrao" (quando houver) em primeiro lugar, marcada e já assumida.
O registro das centrais fica em ~/.talkgo/centrais.json (ou $TALKGO_HOME, ou --registro).
"""
import argparse
import json
import os
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from provision import ASSETS, LANGUAGES, apply_local  # noqa: E402

NAMES = {"en-US": "Inglês", "es-ES": "Espanhol", "fr-FR": "Francês"}
ALIASES = {
    "en-US": {"en", "enus", "english", "ingles", "inglesamericano", "americanenglish"},
    "es-ES": {"es", "eses", "spanish", "espanhol", "espanol"},
    "fr-FR": {"fr", "frfr", "french", "frances", "francais"},
}
ALL = {"todos", "todas", "all"}
PROVIDERS = ("local", "google-drive", "onedrive")
ACCESS = ("pasta-local", "drive", "onedrive", "manual")
BACKUPS = "_backups"
RESETS = {
    "diagnostico": {"remove": ("diagnosticos", "diagnostico-"),
                    "restore": ["estado/perfil-atual.md"], "pointer": "diagnostico-"},
    "praticas": {"remove": ("praticas", "pratica-"),
              "restore": ["estado/contexto-recente.md"], "pointer": "pratica-"},
    "progresso": {"remove": ("progresso/historico", ""),
                  "restore": ["progresso/08-registro-progresso.md", "estado/perfil-atual.md",
                              "estado/contexto-recente.md"], "pointer": None},
}


class Outcome(Exception):
    def __init__(self, status, message, **extra):
        super().__init__(message)
        self.payload = {"status": status, "mensagem": message, **extra}


def fail(message, **extra):
    raise Outcome("erro", message, **extra)


def ask(message, options, **extra):
    raise Outcome("ambiguo", message, opcoes=options, **extra)


def _key(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "".join(ch for ch in text.lower() if ch.isalnum())


def parse_language(text):
    key = _key(text)
    for tag, aliases in ALIASES.items():
        if key == _key(tag) or key in aliases:
            return tag
    fail(f"Idioma desconhecido: {text}.", opcoes=[NAMES[t] for t in LANGUAGES])


# ---------- registro ----------

def registry_path(explicit=None):
    if explicit:
        return Path(explicit).expanduser()
    home = os.environ.get("TALKGO_HOME")
    return (Path(home).expanduser() if home else Path.home() / ".talkgo") / "centrais.json"


def load(path):
    if not path.exists():
        return {"versao": 1, "padrao": None, "centrais": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("padrao", None)
    data.setdefault("centrais", [])
    return data


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    temp = path.with_suffix(".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
    if path.read_text(encoding="utf-8") != text:
        fail(f"Releitura divergente do registro {path}.")


def summary(entry, default):
    return {"nome": entry["nome"], "provedor": entry["provedor"], "acesso": entry["acesso"],
            "raiz": entry["raiz"], "padrao": entry["nome"] == default}


def find(data, name):
    key = _key(name)
    for entry in data["centrais"]:
        if _key(entry["nome"]) == key or entry["raiz"] == name:
            return entry
    if Path(name).expanduser().exists():
        resolved = str(Path(name).expanduser().resolve())
        for entry in data["centrais"]:
            if entry["raiz"] == resolved:
                return entry
    fail(f"Central não encontrada: {name}.", opcoes=[e["nome"] for e in data["centrais"]])


def resolve(data, name, allow_default=True):
    if name:
        return find(data, name)
    centrals = data["centrais"]
    if not centrals:
        fail("Nenhuma Central registrada. Use New-Central.")
    if len(centrals) == 1:
        return centrals[0]
    names = [e["nome"] for e in centrals]
    default = data["padrao"] if allow_default and data["padrao"] in names else None
    if default:
        names = [default] + [n for n in names if n != default]
    ask("Há mais de uma Central. Qual delas?", names, padrao=default)


def local_root(entry):
    if entry["acesso"] != "pasta-local":
        fail(f"A Central {entry['nome']} usa {entry['acesso']}; esta operação é feita pelo conector.",
             central=summary(entry, None))
    return Path(entry["raiz"])


# ---------- leitura da central ----------

def languages_in(root):
    return [tag for tag, folder in LANGUAGES.items() if (root / "languages" / folder).is_dir()]


def read_field(root, field):
    state = root / "config" / "estado-global.md"
    if not state.is_file():
        return None
    for line in state.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{field}:"):
            value = line.split(":", 1)[1].split("#", 1)[0].strip()
            return None if value in ("", "null") else value
    return None


def write_fields(root, values):
    """Preenche campos ainda vazios (null) e une a lista de idiomas escolhidos."""
    state = root / "config" / "estado-global.md"
    lines = state.read_text(encoding="utf-8").splitlines()
    changed = False
    for index, line in enumerate(lines):
        field, sep, rest = line.partition(":")
        if not sep or field not in values:
            continue
        current = rest.split("#", 1)[0].strip()
        wanted = values[field]
        if isinstance(wanted, list):
            known = [t.strip() for t in current.strip("[]").split(",") if t.strip()]
            merged = known + [t for t in wanted if t not in known]
            new = f"{field}: [{', '.join(merged)}]"
        elif current in ("", "null"):
            new = f"{field}: {wanted}"
        else:
            continue
        if new != line:
            lines[index] = new
            changed = True
    if changed:
        text = "\n".join(lines) + "\n"
        state.write_text(text, encoding="utf-8")
        if state.read_text(encoding="utf-8") != text:
            fail("Releitura divergente de config/estado-global.md.")


def set_field(root, field, value):
    """Grava um campo do estado global, substituindo o valor atual (cria a linha se faltar)."""
    state = root / "config" / "estado-global.md"
    lines = state.read_text(encoding="utf-8").splitlines()
    new = f"{field}: {value}"
    for index, line in enumerate(lines):
        if line.partition(":")[0] == field:
            comment = line.split("#", 1)[1] if "#" in line else None
            lines[index] = new + (f"  #{comment}" if comment else "")
            break
    else:
        lines.insert(next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines)), new)
    text = "\n".join(lines) + "\n"
    state.write_text(text, encoding="utf-8")
    if state.read_text(encoding="utf-8") != text:
        fail("Releitura divergente de config/estado-global.md.")


def default_missions(root):
    raw = read_field(root, "missoes_padrao") or ""
    found = {}
    for part in raw.strip("{}").split(","):
        key, sep, value = part.partition(":")
        if sep:
            value = value.strip()
            found[key.strip()] = None if value in ("", "null") else value
    return found


def set_default_mission(root, tag, mission):
    current = default_missions(root)
    current = {t: current.get(t) for t in LANGUAGES}
    current[tag] = mission
    set_field(root, "missoes_padrao", "{" + ", ".join(f"{t}: {current[t] or 'null'}" for t in LANGUAGES) + "}")


def resolve_language(root, name, central):
    present = languages_in(root)
    if not present:
        fail("A Central não tem idiomas. Use Add-Language.")
    if name:
        tag = parse_language(name)
        if tag not in present:
            fail(f"A Central {central} não tem {NAMES[tag]}.", opcoes=[NAMES[t] for t in present])
        return tag
    if len(present) == 1:
        return present[0]
    default = read_field(root, "idioma_padrao")
    options = sorted(present, key=lambda t: t != default)
    ask("Qual idioma?", [NAMES[t] for t in options], central=central,
        padrao=NAMES[default] if default in present else None)


def fields_of(path, keys):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, rest = line.partition(":")
        if sep and key.strip() in keys:
            values[key.strip()] = rest.split("#", 1)[0].strip() or None
    return values


def practices_in(base):
    found = []
    folder = base / "praticas"
    for path in sorted(folder.glob("pratica-*.md")) if folder.is_dir() else []:
        values = fields_of(path, ("status", "missao_id", "situacao"))
        stamp = path.stem.split("-")[1] if path.stem.count("-") >= 2 else ""
        date = f"{stamp[6:8]}/{stamp[4:6]}/{stamp[:4]}" if len(stamp) == 8 else None
        found.append({"id": path.stem, "data": date, "missao_id": values.get("missao_id"),
                      "situacao": values.get("situacao"), "status": values.get("status") or "desconhecido",
                      "arquivo": path})
    return found


def count(folder, prefix):
    if not folder.is_dir():
        return 0
    return sum(1 for f in folder.glob(f"{prefix}*.md") if f.is_file() and f.name != "MODELO.md")


def missions_in(folder):
    """Missões do idioma: id, título, data-alvo e status (campos missao_* do modelo)."""
    missions = []
    if not folder.is_dir():
        return missions
    for path in sorted(folder.glob("*.md")):
        if path.name == "MODELO.md":
            continue
        values = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            key, sep, rest = line.partition(":")
            if sep and key in ("missao_id", "missao_titulo", "missao_data_alvo", "missao_status"):
                value = rest.split("#", 1)[0].strip()
                values[key] = value or None
        missions.append({"id": values.get("missao_id") or path.stem,
                         "titulo": values.get("missao_titulo") or path.stem,
                         "data_alvo": values.get("missao_data_alvo"),
                         "status": values.get("missao_status") or "desconhecido"})
    return missions


def describe(entry, default):
    info = summary(entry, default)
    info["formato_registros"] = "nativo" if entry["acesso"] == "drive" else "markdown"
    if entry["acesso"] != "pasta-local":
        info["idiomas"] = [NAMES[t] for t in entry.get("idiomas", [])]
        info["observacao"] = "Detalhes por idioma são lidos pelo conector."
        return info
    root = Path(entry["raiz"])
    if not root.is_dir():
        info["idiomas"] = [NAMES[t] for t in entry.get("idiomas", [])]
        info["raiz_inacessivel"] = True
        return info
    info["status"] = read_field(root, "status")
    info["idiomas"] = []
    for tag in languages_in(root):
        base = root / "languages" / LANGUAGES[tag]
        info["idiomas"].append({
            "idioma": NAMES[tag], "tag": tag,
            "diagnosticos": count(base / "diagnosticos", "diagnostico-"),
            "praticas": count(base / "praticas", "pratica-"),
            "padrao": tag == read_field(root, "idioma_padrao"),
            "missoes": count(base / "missoes", ""),
            "missao_padrao": default_missions(root).get(tag),
            "lista_missoes": missions_in(base / "missoes"),
        })
    backups = root / BACKUPS
    info["backups"] = sum(1 for _ in backups.iterdir()) if backups.is_dir() else 0
    return info


# ---------- comandos ----------

def cmd_info(data, args):
    if args.central:
        return {"status": "ok", "centrais": [describe(find(data, args.central), data["padrao"])],
                "padrao": data["padrao"]}
    if not data["centrais"]:
        return {"status": "ok", "centrais": [], "padrao": None,
                "mensagem": "Nenhuma Central registrada. Use New-Central."}
    return {"status": "ok", "padrao": data["padrao"],
            "centrais": [describe(e, data["padrao"]) for e in data["centrais"]]}


def guess_provider(root):
    text = _key(str(root))
    if "onedrive" in text:
        return "onedrive"
    if any(k in text for k in ("googledrive", "meudrive", "mydrive", "drivefs")):
        return "google-drive"
    return "local"


def _languages(values):
    if not values:
        ask("Quais idiomas a Central deve ter?", [NAMES[t] for t in LANGUAGES])
    tags = []
    for value in values:
        chosen = list(LANGUAGES) if _key(value) in ALL else [parse_language(value)]
        tags += [t for t in chosen if t not in tags]
    return tags


def _upsert(data, entry):
    for other in data["centrais"]:
        same_name = _key(other["nome"]) == _key(entry["nome"])
        same_root = other["raiz"] == entry["raiz"]
        if same_name != same_root:
            fail(f"Conflito com a Central {other['nome']} ({other['raiz']}). Escolha outro nome ou pasta.")
        if same_name:
            other["idiomas"] = sorted(set(other.get("idiomas", [])) | set(entry["idiomas"]))
            return other, False
    data["centrais"].append(entry)
    if len(data["centrais"]) == 1 or not data["padrao"]:
        data["padrao"] = entry["nome"]
    return entry, True


def cmd_create(data, args, path):
    tags = _languages(args.idiomas)
    root = Path(args.raiz).expanduser()
    if not root.exists():
        if not root.parent.is_dir():
            fail(f"A pasta pai {root.parent} não existe.")
        root.mkdir()
    root = root.resolve()
    provider = args.provedor or guess_provider(root)
    name = args.nome or root.name
    result = apply_local(root, tags)
    present = languages_in(root)
    write_fields(root, {"nome_central": name, "provedor": provider, "armazenamento": "pasta-local",
                        "formato_registros": "markdown",
                        "raiz": str(root), "idiomas_escolhidos_pelo_aluno": present,
                        "idioma_padrao": tags[0] if tags else None})
    entry, new = _upsert(data, {"nome": name, "provedor": provider, "acesso": "pasta-local",
                                "raiz": str(root), "idiomas": present,
                                "criada_em": datetime.now().strftime("%Y-%m-%d")})
    entry["idiomas"] = present
    save(path, data)
    return {"status": "ok", "central": summary(entry, data["padrao"]), "nova": new,
            "idiomas": [NAMES[t] for t in present], "criados": len(result["created"]),
            "existentes": len(result["existing"])}


def cmd_register(data, args, path):
    tags = _languages(args.idiomas)
    entry, new = _upsert(data, {"nome": args.nome, "provedor": args.provedor, "acesso": args.acesso,
                                "raiz": args.raiz, "idiomas": tags,
                                "criada_em": datetime.now().strftime("%Y-%m-%d")})
    save(path, data)
    return {"status": "ok", "central": summary(entry, data["padrao"]), "nova": new}


def cmd_default(data, args, path):
    if args.idioma or args.missao:
        entry = resolve(data, args.central)
        root = local_root(entry)
        tag = resolve_language(root, args.idioma, entry["nome"])
        if not args.missao:
            before = read_field(root, "idioma_padrao")
            set_field(root, "idioma_padrao", tag)
            return {"status": "ok", "central": entry["nome"], "nivel": "language",
                    "anterior": NAMES.get(before), "padrao": NAMES[tag]}
        missions = {m["id"]: m for m in missions_in(root / "languages" / LANGUAGES[tag] / "missoes")}
        wanted = next((m for m in missions.values() if _key(m["id"]) == _key(args.missao)
                       or _key(m["titulo"]) == _key(args.missao)), None)
        if not wanted:
            fail(f"Missão {args.missao} não encontrada em {NAMES[tag]}.", opcoes=sorted(missions))
        before = default_missions(root).get(tag)
        set_default_mission(root, tag, wanted["id"])
        return {"status": "ok", "central": entry["nome"], "nivel": "mission", "idioma": NAMES[tag],
                "anterior": before, "padrao": wanted["id"]}
    if args.nome:
        entry = find(data, args.nome)
    elif len(data["centrais"]) == 1:
        entry = data["centrais"][0]
    elif not data["centrais"]:
        fail("Nenhuma Central registrada. Use New-Central.")
    else:
        ask("Qual Central deve ser a padrão?", [e["nome"] for e in data["centrais"]],
            padrao_atual=data["padrao"])
    before = data["padrao"]
    data["padrao"] = entry["nome"]
    save(path, data)
    return {"status": "ok", "nivel": "central", "anterior": before, "padrao": entry["nome"]}


def cmd_practices(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    tag = resolve_language(root, args.idioma, entry["nome"])
    base = root / "languages" / LANGUAGES[tag]
    missions = {m["id"]: m for m in missions_in(base / "missoes")}
    default = default_missions(root).get(tag)
    groups = {}
    for practice in practices_in(base):
        if args.missao and _key(practice["missao_id"] or "") != _key(args.missao):
            continue
        if args.status and _key(args.status) not in _key(practice["status"]):
            continue
        practice = {k: v for k, v in practice.items() if k != "arquivo"}
        groups.setdefault(practice["missao_id"], {}).setdefault(practice["status"], []).append(practice)
    order = sorted(groups, key=lambda m: (m != default, m is None, m or ""))
    result = []
    for mission_id in order:
        info = missions.get(mission_id, {"id": mission_id, "titulo": None, "data_alvo": None, "status": None})
        by_status = groups[mission_id]
        statuses = sorted(by_status, key=lambda s: (s == "Concluída", s))
        result.append({**info, "padrao": mission_id is not None and mission_id == default,
                       "praticas": [{"status": s, "itens": by_status[s]} for s in statuses]})
    return {"status": "ok", "central": entry["nome"], "idioma": NAMES[tag], "missoes": result,
            "total": sum(len(i) for g in groups.values() for i in g.values())}


def cmd_remove_mission(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    tag = resolve_language(root, args.idioma, entry["nome"])
    base = root / "languages" / LANGUAGES[tag]
    missions = {m["id"]: m for m in missions_in(base / "missoes")}
    if not missions:
        fail(f"{NAMES[tag]} não tem missões.")
    if not args.missao:
        ask("Qual missão?", sorted(missions), central=entry["nome"], idioma=NAMES[tag])
    mission = next((m for m in missions.values() if _key(m["id"]) == _key(args.missao)
                    or _key(m["titulo"]) == _key(args.missao)), None)
    if not mission:
        fail(f"Missão {args.missao} não encontrada em {NAMES[tag]}.", opcoes=sorted(missions))
    mission_file = base / "missoes" / f"{mission['id']}.md"
    if not mission_file.is_file():
        mission_file = next(p for p in (base / "missoes").glob("*.md") if missions_in_file(p) == mission["id"])
    practices = [p for p in practices_in(base) if p["missao_id"] == mission["id"]]
    ids = {p["id"] for p in practices}
    remove = [mission_file] + [p["arquivo"] for p in practices]
    adjust, restore = [], []
    progress = base / "progresso" / "08-registro-progresso.md"
    template = ASSETS / "languages" / LANGUAGES[tag] / "progresso" / "08-registro-progresso.md"
    if ids and progress.is_file():
        current = progress.read_text(encoding="utf-8")
        cleaned = progress_without_practices(current, template.read_text(encoding="utf-8"), ids)
        if cleaned != current:
            adjust.append((progress, cleaned))
    pointer = base / "estado" / "sessao-ativa.md"
    if pointer.is_file() and any(i in pointer.read_text(encoding="utf-8") for i in ids):
        restore.append((pointer, ASSETS / "languages" / LANGUAGES[tag] / "estado" / "sessao-ativa.md"))
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    remaining = sorted(set(missions) - {mission["id"]})
    default = default_missions(root).get(tag)
    new_default = default if default != mission["id"] else (remaining[0] if len(remaining) == 1 else None)
    preview = {"central": entry["nome"], "idioma": NAMES[tag], "missao": mission,
               "remover": [rel(p) for p in remove], "ajustar": [rel(c) for c, _ in adjust],
               "restaurar_modelo": [rel(c) for c, _ in restore], "missao_padrao_depois": new_default}
    if _key(args.confirmar or "") != _key(mission["id"]):
        if args.confirmar:
            fail("A confirmação não corresponde ao missao_id.", esperado=mission["id"])
        return {"status": "previa", **preview, "confirmacao": f"--confirmar {mission['id']}"}
    backup = _backup(root, remove + [c for c, _ in adjust + restore], f"remove-mission-{mission['id']}")
    for item in remove:
        item.unlink()
    for current, template_path in restore:
        current.write_bytes(template_path.read_bytes())
    for current, cleaned in adjust:
        current.write_text(cleaned, encoding="utf-8")
        if current.read_text(encoding="utf-8") != cleaned:
            fail(f"Releitura divergente em {rel(current)}.")
    if default != new_default:
        set_default_mission(root, tag, new_default)
    return {"status": "ok", **preview, "backup": rel(backup)}


def missions_in_file(path):
    return fields_of(path, ("missao_id",)).get("missao_id")


def _backup(root, items, label):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = root / BACKUPS / f"{stamp}-{label}"
    suffix = 2
    while backup.exists():
        backup = backup.with_name(f"{stamp}-{label}-{suffix}")
        suffix += 1
    for item in items:
        copy = backup / item.relative_to(root)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, copy)
        if copy.read_bytes() != item.read_bytes():
            fail(f"Backup divergente em {item.relative_to(root).as_posix()}. Nada foi apagado.")
    return backup


def _check_central_root(root):
    if root.is_symlink():
        fail("A raiz é um link simbólico. Remova manualmente após conferir.")
    resolved = root.resolve()
    package = ASSETS.parent.resolve()
    if resolved in (Path.home().resolve(), Path(resolved.anchor)) or resolved == package \
            or package in resolved.parents or resolved in package.parents:
        fail(f"Recusado: {resolved} não pode ser removida.")
    if not (root / "config" / "estado-global.md").is_file() or not (root / "languages").is_dir():
        fail(f"{resolved} não tem a estrutura de uma Central (config/estado-global.md e languages/).")


def cmd_remove(data, args, path):
    entry = resolve(data, args.central, allow_default=False)
    info = describe(entry, data["padrao"])
    local = entry["acesso"] == "pasta-local"
    root = Path(entry["raiz"])
    if local and root.exists() and not args.somente_registro:
        _check_central_root(root)
        info["arquivos"] = sum(1 for f in root.rglob("*") if f.is_file())
    if not args.confirmar:
        steps = ("apagar a pasta e tirar do registro" if local and root.exists()
                 and not args.somente_registro else "tirar do registro (a pasta é removida pelo conector)")
        return {"status": "previa", "acao": steps, "central": info,
                "confirmacao": f"--confirmar {entry['nome']}"}
    if _key(args.confirmar) != _key(entry["nome"]):
        fail("A confirmação não corresponde ao nome da Central.", esperado=entry["nome"])
    result = {"status": "ok", "central": entry["nome"], "pasta_removida": False}
    if local and root.exists() and not args.somente_registro:
        if args.backup:
            target = Path(args.backup).expanduser().resolve()
            if root.resolve() in target.parents:
                fail("O backup precisa ficar fora da Central.")
            base = str(target)[:-4] if str(target).endswith(".zip") else str(target)
            result["backup"] = shutil.make_archive(base, "zip", root.parent, root.name)
        shutil.rmtree(root)
        if root.exists():
            fail(f"Não foi possível remover {root} por completo.")
        result["pasta_removida"] = True
    elif not args.somente_registro and local:
        result["observacao"] = "A pasta já não existia; só o registro foi atualizado."
    data["centrais"] = [e for e in data["centrais"] if e is not entry]
    if data["padrao"] == entry["nome"]:
        data["padrao"] = data["centrais"][0]["nome"] if len(data["centrais"]) == 1 else None
    save(path, data)
    result["padrao"] = data["padrao"]
    if data["padrao"] is None and len(data["centrais"]) > 1:
        result["aviso"] = "Não há Central padrão. Use Set-Default central."
    return result


PRACTICE_TABLE_HEADS = {"session id", "identificador", "identifiant"}
COUNT_ROWS = {"completed regular practices", "prácticas regulares completadas", "pratiques régulières terminées"}
PRACTICE_SUMMARY_ROWS = {"completed regular practices", "actual observed duration", "prácticas regulares completadas",
                         "duración real acumulada", "pratiques régulières terminées", "durée réelle cumulée"}


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_row(line):
    return line.lstrip().startswith("|")


def _is_separator(line):
    return _is_row(line) and all(set(c) <= set("-: ") for c in _cells(line))


def mission_without_practices(text):
    """Tira da tabela Práticas da missão as linhas das sessões apagadas (todas as do idioma)."""
    out, in_practices = [], False
    for line in text.splitlines():
        if not _is_row(line):
            in_practices = False
        elif not in_practices and _cells(line) and _cells(line)[0].lower() in ("prática", "pratica"):
            in_practices = True
        elif in_practices and not _is_separator(line):
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def progress_without_practices(text, template, ids=None):
    """Tira do registro 08 as linhas das práticas (todas, ou só as de `ids`). Sem nenhuma prática
    restante, devolve ao modelo o total de práticas e a duração real; senão, recalcula o total."""
    model = {_cells(l)[0].lower(): l for l in template.splitlines() if _is_row(l) and len(_cells(l)) == 2}
    kept, in_practices, remaining = [], False, 0
    for line in text.splitlines():
        if not _is_row(line):
            in_practices = False
        elif _cells(line)[0].lower() in PRACTICE_TABLE_HEADS:
            in_practices = True
        elif in_practices and not _is_separator(line):
            if ids is None or _cells(line)[0] in ids:
                continue
            remaining += 1
        kept.append(line)
    out = []
    for line in kept:
        label = _cells(line)[0].lower() if _is_row(line) else ""
        if label in PRACTICE_SUMMARY_ROWS and label in model:
            if remaining == 0:
                line = model[label]
            elif label in COUNT_ROWS:
                line = f"| {_cells(line)[0]} | {remaining} |"
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _reset_scope(root, kind, tags):
    spec = RESETS[kind]
    remove, restore, warnings, adjust = [], [], [], []
    for tag in tags:
        folder = LANGUAGES[tag]
        base = root / "languages" / folder
        sub, prefix = spec["remove"]
        target = base / sub
        if target.is_dir():
            for item in sorted(target.rglob("*")):
                if item.is_file() and item.name.startswith(prefix) and item.name not in ("MODELO.md", "README.md") \
                        and (kind == "progresso" or item.parent == target):
                    remove.append(item)
        candidates = list(spec["restore"])
        pointer = base / "estado" / "sessao-ativa.md"
        if spec["pointer"] and pointer.is_file() and spec["pointer"] in pointer.read_text(encoding="utf-8"):
            candidates.append("estado/sessao-ativa.md")
        for relative in candidates:
            current = base / relative
            template = ASSETS / "languages" / folder / relative
            if not current.is_file() or current.read_bytes() != template.read_bytes():
                restore.append((current, template))
        progress = base / "progresso" / "08-registro-progresso.md"
        template = ASSETS / "languages" / folder / "progresso" / "08-registro-progresso.md"
        if kind == "praticas" and remove:
            if progress.is_file():
                current = progress.read_text(encoding="utf-8")
                cleaned = progress_without_practices(current, template.read_text(encoding="utf-8"))
                if cleaned != current:
                    adjust.append((progress, cleaned))
            missions = base / "missoes"
            for mission in sorted(missions.glob("*.md")) if missions.is_dir() else []:
                if mission.name in ("MODELO.md", "README.md"):
                    continue
                current = mission.read_text(encoding="utf-8")
                cleaned = mission_without_practices(current)
                if cleaned != current:
                    adjust.append((mission, cleaned))
        elif kind == "diagnostico" and progress.is_file() and progress.read_bytes() != template.read_bytes():
            warnings.append(f"O progresso de {NAMES[tag]} foi calculado com esses registros. "
                            "Considere também Reset-Progress.")
    return remove, restore, warnings, adjust


def cmd_reset(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    if not root.is_dir():
        fail(f"A pasta da Central não está acessível: {root}.")
    present = languages_in(root)
    if args.idioma:
        tags = present if _key(args.idioma) in ALL else [parse_language(args.idioma)]
        missing = [t for t in tags if t not in present]
        if missing:
            fail(f"A Central {entry['nome']} não tem {NAMES[missing[0]]}.", opcoes=[NAMES[t] for t in present])
    elif len(present) == 1:
        tags = present
    else:
        default = read_field(root, "idioma_padrao")
        options = sorted(present, key=lambda t: t != default)
        ask("Qual idioma?", [NAMES[t] for t in options] + ["Todos"], central=entry["nome"],
            padrao=NAMES[default] if default in present else None)
    remove, restore, warnings, adjust = _reset_scope(root, args.tipo, tags)
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    preview = {"central": entry["nome"], "padrao": entry["nome"] == data["padrao"], "tipo": args.tipo,
               "idiomas": [NAMES[t] for t in tags], "remover": [rel(p) for p in remove],
               "restaurar_modelo": [rel(c) for c, _ in restore], "ajustar": [rel(c) for c, _ in adjust],
               "avisos": warnings}
    if not remove and not restore and not adjust:
        return {"status": "ok", **preview, "mensagem": "Nada a zerar."}
    if not args.confirmar:
        return {"status": "previa", **preview, "confirmacao": "--confirmar"}
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    label = "todos" if len(tags) > 1 else LANGUAGES[tags[0]]
    backup = root / BACKUPS / f"{stamp}-reset-{args.tipo}-{label}"
    suffix = 2
    while backup.exists():
        backup = backup.with_name(f"{stamp}-reset-{args.tipo}-{label}-{suffix}")
        suffix += 1
    for item in remove + [c for c, _ in restore if c.is_file()] + [c for c, _ in adjust]:
        copy = backup / rel(item)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, copy)
        if copy.read_bytes() != item.read_bytes():
            fail(f"Backup divergente em {rel(item)}. Nada foi apagado.")
    for item in remove:
        item.unlink()
    for current, template in restore:
        current.write_bytes(template.read_bytes())
        if current.read_bytes() != template.read_bytes():
            fail(f"Releitura divergente em {rel(current)}.")
    for current, cleaned in adjust:
        current.write_text(cleaned, encoding="utf-8")
        if current.read_text(encoding="utf-8") != cleaned:
            fail(f"Releitura divergente em {rel(current)}.")
    return {"status": "ok", **preview, "backup": rel(backup)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registro", help="arquivo de registro das centrais")
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("info")
    p.add_argument("--central")
    p = sub.add_parser("create")
    p.add_argument("--raiz", required=True)
    p.add_argument("--nome")
    p.add_argument("--provedor", choices=PROVIDERS)
    p.add_argument("idiomas", nargs="*")
    p = sub.add_parser("register")
    p.add_argument("--raiz", required=True)
    p.add_argument("--nome", required=True)
    p.add_argument("--provedor", choices=PROVIDERS, required=True)
    p.add_argument("--acesso", choices=ACCESS, required=True)
    p.add_argument("idiomas", nargs="*")
    p = sub.add_parser("default")
    p.add_argument("nome", nargs="?")
    p.add_argument("--idioma")
    p.add_argument("--missao")
    p.add_argument("--central")
    p = sub.add_parser("practices")
    p.add_argument("idioma", nargs="?")
    p.add_argument("--missao")
    p.add_argument("--status")
    p.add_argument("--central")
    p = sub.add_parser("remove-mission")
    p.add_argument("missao", nargs="?")
    p.add_argument("--idioma")
    p.add_argument("--central")
    p.add_argument("--confirmar")
    p = sub.add_parser("remove")
    p.add_argument("--central")
    p.add_argument("--confirmar")
    p.add_argument("--backup")
    p.add_argument("--somente-registro", action="store_true")
    p = sub.add_parser("reset")
    p.add_argument("tipo", choices=sorted(RESETS))
    p.add_argument("idioma", nargs="?")
    p.add_argument("--central")
    p.add_argument("--confirmar", action="store_true")
    args = parser.parse_args(argv)
    path = registry_path(args.registro)
    try:
        data = load(path)
        if args.comando == "info":
            result = cmd_info(data, args)
        elif args.comando == "create":
            result = cmd_create(data, args, path)
        elif args.comando == "register":
            result = cmd_register(data, args, path)
        elif args.comando == "default":
            result = cmd_default(data, args, path)
        elif args.comando == "remove":
            result = cmd_remove(data, args, path)
        elif args.comando == "practices":
            result = cmd_practices(data, args)
        elif args.comando == "remove-mission":
            result = cmd_remove_mission(data, args)
        else:
            result = cmd_reset(data, args)
    except ValueError as error:
        result = {"status": "erro", "mensagem": str(error)}
    except Outcome as outcome:
        result = outcome.payload
    result["registro"] = str(path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {"ok": 0, "previa": 0, "ambiguo": 2}.get(result["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
