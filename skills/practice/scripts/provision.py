"""Provisione a pasta pessoal sem acessar a rede.

Google Drive por conector: planeja a próxima rodada de operações.
  python scripts/provision.py ID_PESSOAL inventario.json en-US es-ES [--abas abas.json]
Pasta local: cria o que falta diretamente no disco, sem sobrescrever (100% Markdown).
  python scripts/provision.py --local CAMINHO en-US es-ES

No Drive, os arquivos gravados durante o uso são nativos (Google Doc ou Google Sheet,
sem a extensão .md no nome); os que só são lidos continuam em Markdown.
"""
import argparse
import csv
import io
import json
import re
from pathlib import Path, PurePosixPath


ASSETS = Path(__file__).resolve().parents[1] / "assets"
LANGUAGES = {"en-US": "english", "es-ES": "spanish", "fr-FR": "french"}
FOLDER = "application/vnd.google-apps.folder"
MARKDOWN = "text/markdown"
DOC = "application/vnd.google-apps.document"
SHEET = "application/vnd.google-apps.spreadsheet"
EXPECTED = {"folder": {FOLDER}, "markdown": {MARKDOWN, "text/plain"}, "google-doc": {DOC},
            "google-sheet": {SHEET}}
CREATE_MIME = {"markdown": MARKDOWN, "google-doc": "text/plain", "google-sheet": "text/csv"}
LANG = r"languages/(english|spanish|french)"
DOC_PATTERNS = [r"config/(estado-global|perfil)\.md", LANG + r"/estado/[^/]+\.md",
                LANG + r"/(aulas/aula|diagnosticos/diagnostico)-[^/]+\.md", LANG + r"/planos/[^/]+\.md"]
SHEET_TABS = {LANG + r"/progresso/08-registro-progresso\.md": ["Resumo", "Aulas"]}


def classify(path, is_folder=False):
    """Formato no Drive de um caminho lógico da Central (inclui arquivos criados no uso)."""
    if is_folder:
        return "folder"
    if any(re.fullmatch(pattern, path) for pattern in SHEET_TABS):
        return "google-sheet"
    if any(re.fullmatch(pattern, path) for pattern in DOC_PATTERNS):
        return "google-doc"
    return "markdown"


def drive_name(path, kind):
    name = PurePosixPath(path).name
    return name[:-3] if kind in ("google-doc", "google-sheet") and name.endswith(".md") else name


def tab_names(path):
    for pattern, names in SHEET_TABS.items():
        if re.fullmatch(pattern, path):
            return names
    raise ValueError(f"{path} não é uma planilha.")


def markdown_tables(text):
    tables, current = [], None
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(set(cell) <= set("-: ") and cell for cell in cells):
                continue
            if current is None:
                current = []
                tables.append(current)
            current.append(cells)
        else:
            current = None
    return tables


def sheet_spec(path, source):
    """Abas e CSV inicial gerados das tabelas do modelo .md, na ordem."""
    names = tab_names(path)
    tables = markdown_tables(Path(source).read_text(encoding="utf-8"))
    if len(tables) != len(names):
        raise ValueError(f"O modelo de {path} precisa de {len(names)} tabelas.")
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(tables[0])
    return {"tabs": [{"name": n, "rows": rows} for n, rows in zip(names, tables)], "csv": buffer.getvalue()}


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


def _configure(path, item_id, source, tabs):
    """Compara as abas verificadas da planilha com as esperadas."""
    spec = sheet_spec(path, source)
    expected = [tab["name"] for tab in spec["tabs"]]
    if not tabs:
        raise ValueError(f"Planilha sem abas em {path}.")
    rename = None if tabs[0] == expected[0] or expected[0] in tabs else expected[0]
    present = set(tabs) | ({expected[0]} if rename else set())
    add = [tab for tab in spec["tabs"][1:] if tab["name"] not in present]
    if not rename and not add:
        return None
    return {"action": "configure_sheet", "path": path, "kind": "google-sheet", "args": {
        "spreadsheet_id": item_id, "rename_first_tab": {"from": tabs[0], "to": rename} if rename else None,
        "add_tabs": add}}


def plan(root_id, languages, listings, tabs=None):
    """listings: ID do pai -> listagem COMPLETA dos filhos diretos (id, title, mime_type).
    tabs: ID de planilha -> títulos das abas, na ordem, lidos da planilha."""
    if not root_id or root_id == "root":
        raise ValueError("Indique o ID da pasta pessoal dedicada.")
    tabs = tabs or {}
    ids, kinds = {"": root_id}, {"": "folder"}
    operations, to_list, to_inspect = [], set(), set()
    for path, source in specification(languages).items():
        parent, _, _ = path.rpartition("/")
        if parent not in ids:
            continue
        parent_id = ids[parent]
        if parent_id not in listings:
            to_list.add(parent_id)
            continue
        kind = classify(path, source is None)
        name = drive_name(path, kind)
        matches = [item for item in listings[parent_id] if item["title"] == name]
        if matches:
            if len(matches) != 1 or matches[0]["mime_type"] not in EXPECTED[kind]:
                raise ValueError(f"Conflito em {path}: esperava 1 {kind}. Inspecione o pai {parent_id}.")
            item_id = matches[0]["id"]
            if not item_id or item_id in ids.values():
                raise ValueError(f"ID inválido ou repetido em {path}")
            ids[path], kinds[path] = item_id, kind
            if kind == "google-sheet":
                if item_id not in tabs:
                    to_inspect.add(item_id)
                else:
                    step = _configure(path, item_id, source, tabs[item_id])
                    if step:
                        operations.append(step)
            continue
        if kind == "folder":
            operations.append({"action": "create_folder", "path": path, "kind": kind, "args": {
                "parent_folder_id": parent_id, "name": name, "mime_type": FOLDER}})
            continue
        args = {"parent_folder_id": parent_id, "name": name, "create_mime_type": CREATE_MIME[kind],
                "target_mime_type": next(iter(EXPECTED[kind])) if kind != "markdown" else MARKDOWN}
        if kind == "google-sheet":
            spec = sheet_spec(path, source)
            args["csv"] = spec["csv"]
            args["tabs"] = spec["tabs"]
        else:
            args["content_file"] = str(source)
        operations.append({"action": "create_file", "path": path, "kind": kind, "args": args})
    return {"list_parent_ids": sorted(to_list), "inspect_sheet_ids": sorted(to_inspect),
            "operations": operations, "ids": ids, "kinds": kinds}


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
    parser.add_argument("--abas", type=Path, metavar="ABAS_JSON",
                        help="Drive: JSON com ID da planilha -> títulos das abas, na ordem")
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
        sheets = json.loads(options.abas.read_text(encoding="utf-8-sig")) if options.abas else {}
        result = plan(root_id, languages, json.loads(inventory.read_text(encoding="utf-8-sig")), sheets)
    else:
        result = apply_local(options.local, languages)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
