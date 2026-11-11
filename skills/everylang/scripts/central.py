"""Gerencie as Centrais de idioma numa pasta local, sem acessar a rede.

Comandos (a skill traduz os comandos do aluno para estes):
  info     [--central NOME]                         Info-CentralIdioma
  create   --raiz PASTA [--nome N] [--provedor P] IDIOMA...   Create-CentralIdioma
  register --raiz ID --acesso A --provedor P --nome N IDIOMA...  (central criada por conector)
  default  [NOME]                                   Default-CentralIdioma
  remove   [--central NOME] [--confirmar NOME] [--backup ZIP] [--somente-registro]
                                                    Remove-CentralIdioma
  reset    {diagnostico,aulas,progresso} [IDIOMA] [--central NOME] [--confirmar]
                                                    Reset-Diagnostic / Reset-Lessons / Reset-Progress

Sem --confirmar, remove e reset só mostram a prévia. A saída é sempre JSON com
"status": ok | previa | ambiguo | erro. Em "ambiguo", pergunte ao aluno usando "opcoes".
O registro das centrais fica em ~/.everylang/centrais.json (ou $EVERYLANG_HOME, ou --registro).
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
    "aulas": {"remove": ("aulas", "aula-"),
              "restore": ["estado/contexto-recente.md"], "pointer": "aula-"},
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
    home = os.environ.get("EVERYLANG_HOME")
    return (Path(home).expanduser() if home else Path.home() / ".everylang") / "centrais.json"


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
        fail("Nenhuma Central registrada. Use Create-CentralIdioma.")
    if len(centrals) == 1:
        return centrals[0]
    if allow_default and data["padrao"]:
        return find(data, data["padrao"])
    ask("Há mais de uma Central. Qual delas?", [e["nome"] for e in centrals])


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


def count(folder, prefix):
    if not folder.is_dir():
        return 0
    return sum(1 for f in folder.glob(f"{prefix}*.md") if f.is_file() and f.name != "MODELO.md")


def plans_in(folder):
    """Planos de missão do idioma: id, nome e status (campos plano_* do modelo)."""
    plans = []
    if not folder.is_dir():
        return plans
    for path in sorted(folder.glob("*.md")):
        if path.name == "MODELO.md":
            continue
        values = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            key, sep, rest = line.partition(":")
            if sep and key in ("plano_id", "plano_nome", "plano_status"):
                value = rest.split("#", 1)[0].strip()
                values[key] = value or None
        plans.append({"id": values.get("plano_id") or path.stem, "nome": values.get("plano_nome") or path.stem,
                      "status": values.get("plano_status") or "desconhecido"})
    return plans


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
            "aulas": count(base / "aulas", "aula-"),
            "planos": count(base / "planos", ""),
            "lista_planos": plans_in(base / "planos"),
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
                "mensagem": "Nenhuma Central registrada. Use Create-CentralIdioma."}
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
                        "raiz": str(root), "idiomas_escolhidos_pelo_aluno": present})
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
    if args.nome:
        entry = find(data, args.nome)
    elif len(data["centrais"]) == 1:
        entry = data["centrais"][0]
    elif not data["centrais"]:
        fail("Nenhuma Central registrada. Use Create-CentralIdioma.")
    else:
        ask("Qual Central deve ser a padrão?", [e["nome"] for e in data["centrais"]],
            padrao_atual=data["padrao"])
    data["padrao"] = entry["nome"]
    save(path, data)
    return {"status": "ok", "padrao": entry["nome"]}


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
        result["aviso"] = "Não há Central padrão. Use Default-CentralIdioma."
    return result


def _reset_plan(root, kind, tags):
    spec = RESETS[kind]
    remove, restore, warnings = [], [], []
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
        if kind != "progresso" and progress.is_file() and progress.read_bytes() != template.read_bytes():
            warnings.append(f"O progresso de {NAMES[tag]} foi calculado com esses registros. "
                            "Considere também Reset-Progress.")
    return remove, restore, warnings


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
        ask("Qual idioma?", [NAMES[t] for t in present] + ["Todos"], central=entry["nome"])
    remove, restore, warnings = _reset_plan(root, args.tipo, tags)
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    preview = {"central": entry["nome"], "padrao": entry["nome"] == data["padrao"], "tipo": args.tipo,
               "idiomas": [NAMES[t] for t in tags], "remover": [rel(p) for p in remove],
               "restaurar_modelo": [rel(c) for c, _ in restore], "avisos": warnings}
    if not remove and not restore:
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
    for item in remove + [c for c, _ in restore if c.is_file()]:
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
