"""Provision a learner's personal folder as a TalkGo Central, without network access.

Google Drive by connector: computes the next round of operations.
  python scripts/provision.py PERSONAL_ID inventory.json en-US es-ES [--native pt-BR] [--tabs tabs.json]
Local folder: creates what is missing directly on disk, never overwriting (100% Markdown).
  python scripts/provision.py --local PATH en-US es-ES [--native pt-BR]

Folder and file names come from the learner's native language (see scripts/layout.py). An existing
Central keeps the names in its talkgo.json. On Drive, records written during use are native files
(Google Doc or Google Sheet, without the .md extension); read-only files stay in Markdown.
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import ASSETS, MANIFEST, TARGETS, Layout, build_manifest

LANGUAGES = {tag: tag for tag in TARGETS}
FOLDER = "application/vnd.google-apps.folder"
MARKDOWN = "text/markdown"
JSON = "application/json"
DOC = "application/vnd.google-apps.document"
SHEET = "application/vnd.google-apps.spreadsheet"
EXPECTED = {"folder": {FOLDER}, "markdown": {MARKDOWN, "text/plain"}, "manifest": {JSON, "text/plain"},
            "google-doc": {DOC}, "google-sheet": {SHEET}}
CREATE_MIME = {"markdown": MARKDOWN, "manifest": JSON, "google-doc": "text/plain", "google-sheet": "text/csv"}


def drive_name(path, kind):
    name = PurePosixPath(path).name
    return name[:-3] if kind in ("google-doc", "google-sheet") and name.endswith(".md") else name


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


def sheet_spec(layout, text):
    """Tabs and initial CSV built from the two tables of the progress-log template, in order."""
    names = [layout.m["tabs"]["summary"], layout.m["tabs"]["practices"]]
    tables = markdown_tables(text)
    if len(tables) != len(names):
        raise ValueError(f"The progress-log template needs {len(names)} tables.")
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(tables[0])
    return {"tabs": [{"name": n, "rows": rows} for n, rows in zip(names, tables)], "csv": buffer.getvalue()}


def content(layout, path, spec_entry):
    kind, template, tag = spec_entry
    if kind == "manifest":
        return json.dumps(layout.m, ensure_ascii=False, indent=2) + "\n"
    return layout.render(template, tag)


def _configure(layout, path, item_id, text, tabs):
    """Compare the verified tabs of a spreadsheet with the expected ones."""
    spec = sheet_spec(layout, text)
    expected = [tab["name"] for tab in spec["tabs"]]
    if not tabs:
        raise ValueError(f"Spreadsheet without tabs at {path}.")
    rename = None if tabs[0] == expected[0] or expected[0] in tabs else expected[0]
    present = set(tabs) | ({expected[0]} if rename else set())
    add = [tab for tab in spec["tabs"][1:] if tab["name"] not in present]
    if not rename and not add:
        return None
    return {"action": "configure_sheet", "path": path, "kind": "google-sheet", "args": {
        "spreadsheet_id": item_id, "rename_first_tab": {"from": tabs[0], "to": rename} if rename else None,
        "add_tabs": add}}


def next_operations(root_id, languages, listings, tabs=None, native="en", manifest=None):
    """listings: parent ID -> COMPLETE listing of its direct children (id, title, mime_type).
    tabs: spreadsheet ID -> tab titles, in order, read from the spreadsheet.
    manifest: content of an existing talkgo.json (its names win over `native`)."""
    if not root_id or root_id == "root":
        raise ValueError("Give the ID of the dedicated personal folder.")
    layout = Layout(manifest) if manifest else Layout.for_native(native)
    tabs = tabs or {}
    ids, kinds = {"": root_id}, {"": "folder"}
    operations, to_list, to_inspect = [], set(), set()
    for path, entry in layout.specification(languages).items():
        parent, _, _ = path.rpartition("/")
        if parent not in ids:
            continue
        parent_id = ids[parent]
        if parent_id not in listings:
            to_list.add(parent_id)
            continue
        kind = entry[0]
        name = drive_name(path, kind)
        matches = [item for item in listings[parent_id] if item["title"] == name]
        if matches:
            if len(matches) != 1 or matches[0]["mime_type"] not in EXPECTED[kind]:
                raise ValueError(f"Conflict at {path}: expected 1 {kind}. Inspect parent {parent_id}.")
            item_id = matches[0]["id"]
            if not item_id or item_id in ids.values():
                raise ValueError(f"Invalid or repeated ID at {path}")
            ids[path], kinds[path] = item_id, kind
            if kind == "google-sheet":
                if item_id not in tabs:
                    to_inspect.add(item_id)
                else:
                    step = _configure(layout, path, item_id, content(layout, path, entry), tabs[item_id])
                    if step:
                        operations.append(step)
            continue
        if kind == "folder":
            operations.append({"action": "create_folder", "path": path, "kind": kind, "args": {
                "parent_folder_id": parent_id, "name": name, "mime_type": FOLDER}})
            continue
        args = {"parent_folder_id": parent_id, "name": name, "create_mime_type": CREATE_MIME[kind],
                "target_mime_type": next(iter(EXPECTED[kind])) if kind in ("google-doc", "google-sheet")
                else CREATE_MIME[kind]}
        text = content(layout, path, entry)
        if kind == "google-sheet":
            spec = sheet_spec(layout, text)
            args["csv"] = spec["csv"]
            args["tabs"] = spec["tabs"]
        else:
            args["content"] = text
        operations.append({"action": "create_file", "path": path, "kind": kind, "args": args})
    return {"list_parent_ids": sorted(to_list), "inspect_sheet_ids": sorted(to_inspect),
            "operations": operations, "ids": ids, "kinds": kinds, "native_language": layout.native}


def apply_local(root, languages, native="en"):
    """Create missing folders and records under a personal local folder.

    Never overwrites, never follows symlinks and refuses the skill package itself. An existing
    Central keeps the native language and names of its talkgo.json.
    """
    root = Path(root).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Give an existing personal folder that is not a symbolic link.")
    package = ASSETS.parent.resolve()
    resolved = root.resolve()
    if resolved == package or package in resolved.parents:
        raise ValueError("The personal folder cannot be inside the skill folder.")
    layout = Layout.read(root) if (root / MANIFEST).is_file() else Layout(build_manifest(native))
    created, existing = [], []
    for path, entry in layout.specification(languages).items():
        target = root.joinpath(*PurePosixPath(path).parts)
        if target.is_symlink():
            raise ValueError(f"Symbolic link at {path}. Inspect it before going on.")
        if entry[0] == "folder":
            if target.is_dir():
                existing.append(path)
            elif target.exists():
                raise ValueError(f"Conflict at {path}: expected a folder.")
            else:
                target.mkdir()
                created.append(path)
            continue
        if target.is_file():
            existing.append(path)
            continue
        if target.exists():
            raise ValueError(f"Conflict at {path}: expected a file.")
        data = content(layout, path, entry).encode("utf-8")
        with open(target, "xb") as handle:
            handle.write(data)
        if target.read_bytes() != data:
            raise ValueError(f"Reread mismatch at {path}.")
        created.append(path)
    ids = {path: path for path in created + existing}
    return {"root": str(resolved), "native_language": layout.native, "created": created, "existing": existing,
            "ids": dict(sorted(ids.items()))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local", type=Path, metavar="PATH",
                        help="create the structure in a local folder instead of computing Drive operations")
    parser.add_argument("--native", default="en", help="learner's native language (e.g. pt-BR); default en")
    parser.add_argument("--tabs", type=Path, metavar="TABS_JSON",
                        help="Drive: JSON with spreadsheet ID -> tab titles, in order")
    parser.add_argument("--manifest", type=Path, metavar="TALKGO_JSON",
                        help="Drive: talkgo.json already in the Central (its names win)")
    parser.add_argument("args", nargs="+", metavar="ARG",
                        help="Drive: PERSONAL_ID INVENTORY LANGUAGE...; local: LANGUAGE...")
    options = parser.parse_args(argv)
    if options.local is None:
        if len(options.args) < 3:
            parser.error("Drive: give PERSONAL_ID, inventory.json and at least one language.")
        root_id, inventory, languages = options.args[0], Path(options.args[1]), options.args[2:]
    else:
        languages = options.args
    unknown = [tag for tag in languages if tag not in LANGUAGES]
    if unknown:
        parser.error(f"Invalid languages: {', '.join(unknown)}. Use: {', '.join(LANGUAGES)}.")
    if options.local is None:
        sheets = json.loads(options.tabs.read_text(encoding="utf-8-sig")) if options.tabs else {}
        manifest = json.loads(options.manifest.read_text(encoding="utf-8")) if options.manifest else None
        result = next_operations(root_id, languages, json.loads(inventory.read_text(encoding="utf-8-sig")), sheets,
                                 options.native, manifest)
    else:
        result = apply_local(options.local, languages, options.native)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
