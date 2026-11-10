"""Provisione a pasta pessoal sem acessar a rede.

Drive: planeja a próxima rodada de operações para o conector.
  python scripts/provision.py ID_PESSOAL inventario.json en-US es-ES
Pasta local: cria o que falta diretamente no disco, sem sobrescrever.
  python scripts/provision.py --local CAMINHO en-US es-ES
"""
import argparse
import json
from pathlib import Path, PurePosixPath


ASSETS = Path(__file__).resolve().parents[1] / "assets"
LANGUAGES = {"en-US": "english", "es-ES": "spanish", "fr-FR": "french"}
FOLDER = "application/vnd.google-apps.folder"
MARKDOWN = "text/markdown"


def specification(languages):
    roots = [ASSETS / "config"]
    roots.extend(ASSETS / "languages" / LANGUAGES[tag] for tag in languages)
    spec = {}
    for root in roots:
        for source in sorted(root.rglob("*.md")):
            path = PurePosixPath(source.relative_to(ASSETS).as_posix())
            spec[str(path)] = source
            for parent in path.parents:
                if parent.parts:
                    spec[str(parent)] = None
        if root.parent.name == "languages":
            spec[f"languages/{root.name}/planos"] = None
    return dict(sorted(spec.items(), key=lambda pair: (pair[0].count("/"), pair[0])))


def plan(root_id, languages, listings):
    """listings maps verified parent IDs to COMPLETE direct child listings."""
    if not root_id or root_id == "root":
        raise ValueError("Indique o ID da pasta pessoal dedicada.")
    ids = {"": root_id}
    operations = []
    to_list = set()
    for path, source in specification(languages).items():
        parent, _, name = path.rpartition("/")
        if parent not in ids:
            continue
        parent_id = ids[parent]
        if parent_id not in listings:
            to_list.add(parent_id)
            continue
        matches = [item for item in listings[parent_id] if item["title"] == name]
        if matches:
            expected = {MARKDOWN, "text/plain"} if source else {FOLDER}
            if len(matches) != 1 or matches[0]["mime_type"] not in expected:
                raise ValueError(f"Conflito em {path}. Inspecione os objetos no pai {parent_id}.")
            item_id = matches[0]["id"]
            if not item_id or item_id in ids.values():
                raise ValueError(f"ID inválido ou repetido em {path}")
            ids[path] = item_id
        elif source:
            operations.append({"action": "upload_file", "path": path, "args": {
                "parent_folder_id": parent_id, "file_name": name,
                "mime_type": MARKDOWN, "file_uri": str(source)}})
        else:
            operations.append({"action": "create_folder", "path": path, "args": {
                "parent_folder": parent_id, "name": name}})
    return {"list_parent_ids": sorted(to_list), "operations": operations, "ids": ids}


def apply_local(root, languages):
    """Create missing folders and templates under a personal local folder.

    Never overwrites, never follows symlinks and refuses the skill package itself.
    """
    root = Path(root).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Indique uma pasta pessoal existente, que não seja link simbólico.")
    package = ASSETS.parent.resolve()
    resolved = root.resolve()
    if resolved == package or package in resolved.parents:
        raise ValueError("A pasta pessoal não pode ficar dentro da pasta da skill.")
    created, existing = [], []
    for path, source in specification(languages).items():
        target = root.joinpath(*PurePosixPath(path).parts)
        if target.is_symlink():
            raise ValueError(f"Link simbólico em {path}. Inspecione antes de continuar.")
        if source is None:
            if target.is_dir():
                existing.append(path)
            elif target.exists():
                raise ValueError(f"Conflito em {path}: esperava uma pasta.")
            else:
                target.mkdir()
                created.append(path)
            continue
        if target.is_file():
            existing.append(path)
            continue
        if target.exists():
            raise ValueError(f"Conflito em {path}: esperava um arquivo.")
        data = source.read_bytes()
        with open(target, "xb") as handle:
            handle.write(data)
        if target.read_bytes() != data:
            raise ValueError(f"Releitura divergente em {path}.")
        created.append(path)
    ids = {path: path for path in created + existing}
    return {"root": str(resolved), "created": created, "existing": existing,
            "ids": dict(sorted(ids.items()))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local", type=Path, metavar="PASTA",
                        help="cria a estrutura numa pasta local em vez de planejar operações do Drive")
    parser.add_argument("args", nargs="+", metavar="ARG",
                        help="Drive: ID_PESSOAL INVENTARIO IDIOMA...; local: IDIOMA...")
    options = parser.parse_args(argv)
    if options.local is None:
        if len(options.args) < 3:
            parser.error("Drive: informe ID_PESSOAL, inventario.json e ao menos um idioma.")
        root_id, inventory, languages = options.args[0], Path(options.args[1]), options.args[2:]
    else:
        languages = options.args
    unknown = [tag for tag in languages if tag not in LANGUAGES]
    if unknown:
        parser.error(f"Idiomas inválidos: {', '.join(unknown)}. Use: {', '.join(LANGUAGES)}.")
    if options.local is None:
        result = plan(root_id, languages, json.loads(inventory.read_text(encoding="utf-8-sig")))
    else:
        result = apply_local(options.local, languages)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
