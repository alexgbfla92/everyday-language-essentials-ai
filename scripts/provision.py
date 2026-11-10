"""Planeje a próxima rodada do conector Drive sem acessar a rede."""
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_id")
    parser.add_argument("inventory", type=Path, help="JSON UTF-8 com listagens completas por ID do pai")
    parser.add_argument("languages", nargs="+", choices=LANGUAGES)
    args = parser.parse_args()
    result = plan(args.root_id, args.languages, json.loads(args.inventory.read_text(encoding="utf-8-sig")))
    print(json.dumps(result, indent=2, ensure_ascii=True))
