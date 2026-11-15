"""Manage TalkGo Centrals in a local folder, without network access.

Commands (the skill maps the learner's commands to these):
  info     [--central NAME]                                         Get-Central / Get-Missions
  create   --root PATH [--name N] [--provider P] [--native CODE] LANGUAGE...   New-Central / Add-Language
  register --root ID --access A --provider P --name N [--native CODE] LANGUAGE...  (Central created by connector)
  default  [NAME]                                                   Set-Default central
  default  --language LANGUAGE [--central NAME]                     Set-Default language
  default  --mission ID --language LANGUAGE [--central NAME]        Set-Default mission
  practices [LANGUAGE] [--mission ID] [--status CODE] [--central NAME]          Get-Practices
  remove   [--central NAME] [--confirm NAME] [--registry-only]      Remove-Central
  remove-mission [ID] --language LANGUAGE [--central NAME] [--confirm ID]       Remove-Mission
  backup   [--central NAME] [--destination PATH]                    Backup-Central (only when the learner asks)
  reset    {diagnostics,practices,progress} [LANGUAGE] [--central NAME] [--confirm]
                                                                    Reset-Diagnostics / -Practices / -Progress

Without --confirm, remove, remove-mission and reset only return a preview. No command makes an automatic
backup or writes copies inside a Central; backups only with `backup`, outside the Central.
Output is always JSON with "status": ok | preview | ambiguous | error. On "ambiguous", ask the learner using
"options", with "default" (when present) first, marked and preselected.
Folder and file names come from each Central's talkgo.json (see layout.py).
The registry lives in ~/.talkgo/centrals.json (or $TALKGO_HOME, or --registry).
"""
import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import ASSETS, MANIFEST, TARGETS, Layout  # noqa: E402
from provision import apply_local  # noqa: E402

NAMES = {"en-US": "English", "es-ES": "Spanish", "fr-FR": "French"}
ALIASES = {
    "en-US": {"en", "enus", "english", "ingles", "inglesamericano", "americanenglish", "anglais", "englisch"},
    "es-ES": {"es", "eses", "spanish", "espanhol", "espanol", "espagnol", "spanisch"},
    "fr-FR": {"fr", "frfr", "french", "frances", "francais", "franzosisch"},
}
ALL = {"all", "todos", "todas", "tous", "alle"}
PROVIDERS = ("local", "google-drive", "onedrive")
ACCESS = ("local-folder", "drive", "onedrive", "manual")
RESET_KINDS = ("diagnostics", "practices", "progress")


class Outcome(Exception):
    def __init__(self, status, message, **extra):
        super().__init__(message)
        self.payload = {"status": status, "message": message, **extra}


def fail(message, **extra):
    raise Outcome("error", message, **extra)


def ask(message, options, **extra):
    raise Outcome("ambiguous", message, options=options, **extra)


def _key(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return "".join(ch for ch in text.lower() if ch.isalnum())


def parse_language(text):
    key = _key(text)
    for tag, aliases in ALIASES.items():
        if key == _key(tag) or key in aliases:
            return tag
    fail(f"Unknown language: {text}.", options=[NAMES[t] for t in TARGETS])


# ---------- registry ----------

def registry_path(explicit=None):
    if explicit:
        return Path(explicit).expanduser()
    home = os.environ.get("TALKGO_HOME")
    return (Path(home).expanduser() if home else Path.home() / ".talkgo") / "centrals.json"


def load(path):
    if not path.exists():
        return {"version": 1, "default": None, "centrals": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("default", None)
    data.setdefault("centrals", [])
    return data


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    temp = path.with_suffix(".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
    if path.read_text(encoding="utf-8") != text:
        fail(f"Reread mismatch in registry {path}.")


def summary(entry, default):
    return {"name": entry["name"], "provider": entry["provider"], "access": entry["access"],
            "root": entry["root"], "native_language": entry.get("native_language", "en"),
            "default": entry["name"] == default}


def find(data, name):
    key = _key(name)
    for entry in data["centrals"]:
        if _key(entry["name"]) == key or entry["root"] == name:
            return entry
    if Path(name).expanduser().exists():
        resolved = str(Path(name).expanduser().resolve())
        for entry in data["centrals"]:
            if entry["root"] == resolved:
                return entry
    fail(f"Central not found: {name}.", options=[e["name"] for e in data["centrals"]])


def resolve(data, name, allow_default=True):
    if name:
        return find(data, name)
    centrals = data["centrals"]
    if not centrals:
        fail("No Central registered. Use New-Central (or Start).")
    if len(centrals) == 1:
        return centrals[0]
    names = [e["name"] for e in centrals]
    default = data["default"] if allow_default and data["default"] in names else None
    if default:
        names = [default] + [n for n in names if n != default]
    ask("There is more than one Central. Which one?", names, default=default)


def local_root(entry):
    if entry["access"] != "local-folder":
        fail(f"The Central {entry['name']} is on {entry['provider']}: use the connector, as the adapter says.",
             access=entry["access"])
    return Path(entry["root"])


# ---------- reading a Central ----------

def layout_of(root):
    try:
        return Layout.read(root)
    except ValueError as error:
        fail(str(error))


def languages_in(root, layout):
    return [tag for tag in TARGETS if (root / layout.language(tag)).is_dir()]


def _field_lines(path):
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []


def read_field(root, layout, field):
    for line in _field_lines(root / layout.central_state()):
        if line.startswith(f"{field}:"):
            value = line.split(":", 1)[1].split("#", 1)[0].strip()
            return None if value in ("", "null") else value
    return None


def write_fields(root, layout, values):
    """Fill fields that are still empty (null) and merge the list of chosen languages."""
    state = root / layout.central_state()
    lines = _field_lines(state)
    changed = False
    for index, line in enumerate(lines):
        field, sep, rest = line.partition(":")
        if not sep or field not in values or values[field] is None:
            continue
        current = rest.split("#", 1)[0].strip()
        comment = "  #" + rest.split("#", 1)[1] if "#" in rest else ""
        wanted = values[field]
        if isinstance(wanted, list):
            known = [t.strip() for t in current.strip("[]").split(",") if t.strip()]
            merged = known + [t for t in wanted if t not in known]
            new = f"{field}: [{', '.join(merged)}]{comment}"
        elif current in ("", "null"):
            new = f"{field}: {wanted}{comment}"
        else:
            continue
        if new != line:
            lines[index] = new
            changed = True
    if changed:
        _write(state, "\n".join(lines) + "\n")


def set_field(root, layout, field, value):
    """Write a field of the central state, replacing its value (adds the line if missing)."""
    state = root / layout.central_state()
    lines = _field_lines(state)
    for index, line in enumerate(lines):
        if line.partition(":")[0] == field:
            comment = "  #" + line.split("#", 1)[1] if "#" in line else ""
            lines[index] = f"{field}: {value}{comment}"
            break
    else:
        lines.insert(next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines)), f"{field}: {value}")
    _write(state, "\n".join(lines) + "\n")


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    if path.read_text(encoding="utf-8") != text:
        fail(f"Reread mismatch in {path.name}.")


def default_missions(root, layout):
    raw = read_field(root, layout, "default_missions") or ""
    found = {}
    for part in raw.strip("{}").split(","):
        key, sep, value = part.partition(":")
        if sep:
            value = value.strip()
            found[key.strip()] = None if value in ("", "null") else value
    return found


def set_default_mission(root, layout, tag, mission):
    current = default_missions(root, layout)
    current = {t: current.get(t) for t in TARGETS}
    current[tag] = mission
    set_field(root, layout, "default_missions",
              "{" + ", ".join(f"{t}: {current[t] or 'null'}" for t in TARGETS) + "}")


def resolve_language(root, layout, name, central):
    present = languages_in(root, layout)
    if not present:
        fail("The Central has no languages. Use Add-Language.")
    if name:
        tag = parse_language(name)
        if tag not in present:
            fail(f"The Central {central} does not have {NAMES[tag]}.", options=[NAMES[t] for t in present])
        return tag
    if len(present) == 1:
        return present[0]
    default = read_field(root, layout, "default_language")
    options = sorted(present, key=lambda t: t != default)
    ask("Which language?", [NAMES[t] for t in options], central=central,
        default=NAMES[default] if default in present else None)


def fields_of(path, keys):
    values = {}
    for line in _field_lines(path):
        key, sep, rest = line.partition(":")
        if sep and key.strip() in keys:
            values[key.strip()] = rest.split("#", 1)[0].strip() or None
    return values


def session_pattern(layout, kind):
    return re.compile(rf"^{re.escape(layout.prefix(kind))}-\d{{8}}-\d{{2}}$")


def sessions(folder, layout, kind):
    pattern = session_pattern(layout, kind)
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.glob("*.md") if pattern.match(p.stem))


def practices_in(root, layout, tag):
    found = []
    for path in sessions(root / layout.practices(tag), layout, "practice"):
        values = fields_of(path, ("status", "mission_id", "situation", "current_stage"))
        stamp = path.stem.split("-")[-2]
        status = values.get("status") or "unknown"
        found.append({"id": path.stem, "date": f"{stamp[6:8]}/{stamp[4:6]}/{stamp[:4]}",
                      "mission_id": values.get("mission_id"), "situation": values.get("situation"),
                      "stage": values.get("current_stage"), "status": status,
                      "status_label": layout.status_label(status), "file": path})
    return found


def missions_in(folder):
    """Missions of a language: id, title, target date and status (mission_* fields)."""
    missions = []
    if not folder.is_dir():
        return missions
    for path in sorted(folder.glob("*.md")):
        values = fields_of(path, ("mission_id", "mission_title", "mission_target_date", "mission_status"))
        missions.append({"id": values.get("mission_id") or path.stem,
                         "title": values.get("mission_title") or path.stem,
                         "target_date": values.get("mission_target_date"),
                         "status": values.get("mission_status") or "unknown", "file": path})
    return missions


def _public(items):
    return [{k: v for k, v in item.items() if k != "file"} for item in items]


def describe(entry, default):
    info = summary(entry, default)
    info["record_format"] = "native" if entry["access"] == "drive" else "markdown"
    if entry["access"] != "local-folder":
        info["languages"] = [NAMES[t] for t in entry.get("languages", [])]
        info["note"] = "Details per language are read through the connector."
        return info
    root = Path(entry["root"])
    if not root.is_dir() or not (root / MANIFEST).is_file():
        info["languages"] = [NAMES[t] for t in entry.get("languages", [])]
        info["root_unreachable"] = True
        return info
    layout = Layout.read(root)
    info["native_language"] = layout.native
    info["status"] = read_field(root, layout, "status")
    info["languages"] = []
    for tag in languages_in(root, layout):
        missions = missions_in(root / layout.missions(tag))
        info["languages"].append({
            "language": NAMES[tag], "tag": tag, "folder": layout.language(tag),
            "default": tag == read_field(root, layout, "default_language"),
            "diagnostics": len(sessions(root / layout.diagnostics(tag), layout, "diagnostic")),
            "practices": len(sessions(root / layout.practices(tag), layout, "practice")),
            "missions": len(missions),
            "default_mission": default_missions(root, layout).get(tag),
            "mission_list": [{**m, "status_label": layout.mission_status_label(m["status"])}
                             for m in _public(missions)],
        })
    return info


# ---------- commands ----------

def cmd_info(data, args):
    if args.central:
        centrals = [find(data, args.central)]
    else:
        centrals = data["centrals"]
    return {"status": "ok", "default": data["default"], "centrals": [describe(e, data["default"]) for e in centrals]}


def guess_provider(root):
    text = str(root).lower()
    if "onedrive" in text:
        return "onedrive"
    if "google drive" in text or "googledrive" in text or "my drive" in text:
        return "google-drive"
    return "local"


def _languages(values):
    tags = []
    for value in values:
        for tag in (TARGETS if _key(value) in ALL else [parse_language(value)]):
            if tag not in tags:
                tags.append(tag)
    return tags


def _upsert(data, entry):
    for index, current in enumerate(data["centrals"]):
        if current["root"] == entry["root"]:
            merged = {**current, **{k: v for k, v in entry.items() if k not in ("name", "created_at")}}
            data["centrals"][index] = merged
            return merged, False
        if _key(current["name"]) == _key(entry["name"]):
            fail(f"There is already a Central named {current['name']} in another folder.")
    data["centrals"].append(entry)
    if not data["default"]:
        data["default"] = entry["name"]
    return entry, True


def cmd_create(data, args, path):
    tags = _languages(args.languages)
    root = Path(args.root).expanduser()
    if not tags and not (root / MANIFEST).is_file():
        ask("Which languages will the learner practice?", [NAMES[t] for t in TARGETS])
    if not root.exists():
        if not root.parent.is_dir():
            fail(f"The parent folder {root.parent} does not exist.")
        root.mkdir()
    root = root.resolve()
    provider = args.provider or guess_provider(root)
    name = args.name or root.name
    try:
        result = apply_local(root, tags, args.native or "en")
    except ValueError as error:
        fail(str(error))
    layout = Layout.read(root)
    present = languages_in(root, layout)
    set_field(root, layout, "status", "configured")
    write_fields(root, layout, {"central_name": name, "provider": provider,
                                "storage": "local-folder", "record_format": "markdown", "root": str(root),
                                "chosen_languages": present, "default_language": tags[0] if tags else None})
    entry, new = _upsert(data, {"name": name, "provider": provider, "access": "local-folder",
                                "root": str(root), "languages": present, "native_language": layout.native,
                                "created_at": datetime.now().strftime("%Y-%m-%d")})
    entry["languages"] = present
    save(path, data)
    return {"status": "ok", "central": summary(entry, data["default"]), "new": new,
            "languages": [NAMES[t] for t in present], "created": len(result["created"]),
            "existing": len(result["existing"])}


def cmd_register(data, args, path):
    tags = _languages(args.languages)
    entry, new = _upsert(data, {"name": args.name, "provider": args.provider, "access": args.access,
                                "root": args.root, "languages": tags, "native_language": args.native or "en",
                                "created_at": datetime.now().strftime("%Y-%m-%d")})
    save(path, data)
    return {"status": "ok", "central": summary(entry, data["default"]), "new": new}


def _find_mission(missions, wanted):
    return next((m for m in missions if _key(m["id"]) == _key(wanted) or _key(m["title"]) == _key(wanted)), None)


def cmd_default(data, args, path):
    if args.language or args.mission:
        entry = resolve(data, args.central)
        root = local_root(entry)
        layout = layout_of(root)
        tag = resolve_language(root, layout, args.language, entry["name"])
        if not args.mission:
            before = read_field(root, layout, "default_language")
            set_field(root, layout, "default_language", tag)
            return {"status": "ok", "central": entry["name"], "level": "language",
                    "previous": NAMES.get(before), "default": NAMES[tag]}
        missions = missions_in(root / layout.missions(tag))
        wanted = _find_mission(missions, args.mission)
        if not wanted:
            fail(f"Mission {args.mission} not found in {NAMES[tag]}.", options=sorted(m["id"] for m in missions))
        before = default_missions(root, layout).get(tag)
        set_default_mission(root, layout, tag, wanted["id"])
        return {"status": "ok", "central": entry["name"], "level": "mission", "language": NAMES[tag],
                "previous": before, "default": wanted["id"]}
    if args.name:
        entry = find(data, args.name)
    elif len(data["centrals"]) == 1:
        entry = data["centrals"][0]
    elif not data["centrals"]:
        fail("No Central registered. Use New-Central (or Start).")
    else:
        ask("Which Central should be the default?", [e["name"] for e in data["centrals"]],
            current_default=data["default"])
    before = data["default"]
    data["default"] = entry["name"]
    save(path, data)
    return {"status": "ok", "level": "central", "previous": before, "default": entry["name"]}


def cmd_practices(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    layout = layout_of(root)
    tag = resolve_language(root, layout, args.language, entry["name"])
    missions = {m["id"]: m for m in _public(missions_in(root / layout.missions(tag)))}
    default = default_missions(root, layout).get(tag)
    groups = {}
    for practice in practices_in(root, layout, tag):
        if args.mission and _key(practice["mission_id"] or "") != _key(args.mission):
            continue
        if args.status and _key(args.status) not in (_key(practice["status"]), _key(practice["status_label"])):
            continue
        practice = {k: v for k, v in practice.items() if k != "file"}
        groups.setdefault(practice["mission_id"], {}).setdefault(practice["status"], []).append(practice)
    order = sorted(groups, key=lambda m: (m != default, m is None, m or ""))
    result = []
    for mission_id in order:
        info = missions.get(mission_id, {"id": mission_id, "title": None, "target_date": None, "status": None})
        by_status = groups[mission_id]
        statuses = sorted(by_status, key=lambda s: (s == "completed", s))
        result.append({**info, "default": mission_id is not None and mission_id == default,
                       "practices": [{"status": s, "status_label": layout.status_label(s), "items": by_status[s]}
                                     for s in statuses]})
    return {"status": "ok", "central": entry["name"], "language": NAMES[tag], "native_language": layout.native,
            "missions": result, "total": sum(len(i) for g in groups.values() for i in g.values())}


def _check_central_root(root):
    if root.is_symlink():
        fail("The root is a symbolic link. Remove it by hand after checking.")
    resolved = root.resolve()
    package = ASSETS.parent.resolve()
    if resolved in (Path.home().resolve(), Path(resolved.anchor)) or resolved == package \
            or package in resolved.parents or resolved in package.parents:
        fail(f"Refused: {resolved} cannot be used.")
    if not (root / MANIFEST).is_file():
        fail(f"{resolved} does not have the structure of a Central ({MANIFEST}).")


def cmd_remove(data, args, path):
    entry = resolve(data, args.central, allow_default=False)
    info = describe(entry, data["default"])
    local = entry["access"] == "local-folder"
    root = Path(entry["root"])
    if local and root.exists() and not args.registry_only:
        _check_central_root(root)
        info["files"] = sum(1 for f in root.rglob("*") if f.is_file())
    if not args.confirm:
        steps = ("delete the folder and remove it from the registry" if local and root.exists()
                 and not args.registry_only else "remove from the registry (the connector deletes the folder)")
        return {"status": "preview", "action": steps, "central": info, "confirmation": f"--confirm {entry['name']}"}
    if _key(args.confirm) != _key(entry["name"]):
        fail("The confirmation does not match the Central name.", expected=entry["name"])
    result = {"status": "ok", "central": entry["name"], "folder_removed": False}
    if local and root.exists() and not args.registry_only:
        shutil.rmtree(root)
        if root.exists():
            fail(f"Could not remove {root} completely.")
        result["folder_removed"] = True
    elif not args.registry_only and local:
        result["note"] = "The folder no longer existed; only the registry was updated."
    data["centrals"] = [e for e in data["centrals"] if e is not entry]
    if data["default"] == entry["name"]:
        data["default"] = data["centrals"][0]["name"] if len(data["centrals"]) == 1 else None
    save(path, data)
    result["default"] = data["default"]
    if data["default"] is None and len(data["centrals"]) > 1:
        result["warning"] = "There is no default Central. Use Set-Default central."
    return result


def cmd_backup(data, args):
    """Copy the whole Central to a .zip outside it. Runs only when the learner asks explicitly."""
    entry = resolve(data, args.central)
    root = local_root(entry)
    if not root.is_dir():
        fail(f"The Central folder is not reachable: {root}.")
    _check_central_root(root)
    target = Path(args.destination).expanduser().resolve() if args.destination else root.resolve().parent
    if target == root.resolve() or root.resolve() in target.parents:
        fail("The backup must be outside the Central.")
    if not target.is_dir():
        fail(f"The destination folder does not exist: {target}.")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = Path(shutil.make_archive(str(target / f"{root.name}-backup-{stamp}"), "zip", root.parent, root.name))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        copied = sum(1 for n in z.namelist() if not n.endswith("/"))
    expected = sum(1 for f in root.rglob("*") if f.is_file())
    if bad or copied != expected:
        fail(f"Incomplete backup at {archive}: {copied} of {expected} files.")
    return {"status": "ok", "central": entry["name"], "backup": str(archive), "files": copied}


# ---------- removing records ----------

def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_row(line):
    return line.lstrip().startswith("|")


def without_session_rows(text, pattern, ids=None):
    """Remove table rows whose first cell is a session ID (all of them, or only `ids`)."""
    out = [line for line in text.splitlines()
           if not (_is_row(line) and pattern.match(_cells(line)[0])
                   and (ids is None or _cells(line)[0] in ids))]
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def progress_without_practices(text, template, layout, ids=None):
    """Remove practice rows from the progress log. With no practice left, the completed-practices and
    observed-duration rows go back to the template; otherwise the completed count is recomputed."""
    pattern = session_pattern(layout, "practice")
    cleaned = without_session_rows(text, pattern, ids)
    remaining = sum(1 for line in cleaned.splitlines() if _is_row(line) and pattern.match(_cells(line)[0]))
    labels = layout.m["labels"]
    model = {_cells(l)[0]: l for l in template.splitlines() if _is_row(l) and len(_cells(l)) == 2}
    out = []
    for line in cleaned.splitlines():
        label = _cells(line)[0] if _is_row(line) else ""
        if label in (labels["completed_practices"], labels["observed_duration"]) and label in model:
            if remaining == 0:
                line = model[label]
            elif label == labels["completed_practices"]:
                line = f"| {label} | {remaining} |"
        out.append(line)
    return "\n".join(out) + ("\n" if cleaned.endswith("\n") else "")


def _reset_scope(root, layout, kind, tags):
    remove, restore, warnings, adjust = [], [], [], []
    for tag in tags:
        if kind == "diagnostics":
            remove += sessions(root / layout.diagnostics(tag), layout, "diagnostic")
            candidates = [(layout.current_profile(tag), "current-profile")]
            pointer_prefix = layout.prefix("diagnostic") + "-"
        elif kind == "practices":
            remove += sessions(root / layout.practices(tag), layout, "practice")
            candidates = [(layout.recent_context(tag), "recent-context")]
            pointer_prefix = layout.prefix("practice") + "-"
        else:
            history = root / layout.history(tag)
            readme = root / layout.history_readme(tag)
            remove += sorted(p for p in history.rglob("*") if p.is_file() and p != readme) if history.is_dir() else []
            candidates = [(layout.progress_log(tag), "progress-log"), (layout.current_profile(tag), "current-profile"),
                          (layout.recent_context(tag), "recent-context")]
            pointer_prefix = None
        pointer = root / layout.active_session(tag)
        if pointer_prefix and pointer.is_file() and pointer_prefix in pointer.read_text(encoding="utf-8"):
            candidates.append((layout.active_session(tag), "active-session"))
        for relative, template in candidates:
            current = root / relative
            text = layout.render(template, tag)
            if not current.is_file() or current.read_text(encoding="utf-8") != text:
                restore.append((current, text))
        progress = root / layout.progress_log(tag)
        if kind == "practices" and remove:
            if progress.is_file():
                current = progress.read_text(encoding="utf-8")
                cleaned = progress_without_practices(current, layout.render("progress-log", tag), layout)
                if cleaned != current:
                    adjust.append((progress, cleaned))
            pattern = session_pattern(layout, "practice")
            for mission in missions_in(root / layout.missions(tag)):
                current = mission["file"].read_text(encoding="utf-8")
                cleaned = without_session_rows(current, pattern)
                if cleaned != current:
                    adjust.append((mission["file"], cleaned))
        elif kind == "diagnostics" and progress.is_file() \
                and progress.read_text(encoding="utf-8") != layout.render("progress-log", tag):
            warnings.append(f"The {NAMES[tag]} progress was computed with these records. Consider Reset-Progress too.")
    return remove, restore, warnings, adjust


def _apply(root, remove, restore, adjust):
    for item in remove:
        item.unlink()
    for current, text in restore + adjust:
        _write(current, text)


def cmd_reset(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    if not root.is_dir():
        fail(f"The Central folder is not reachable: {root}.")
    layout = layout_of(root)
    present = languages_in(root, layout)
    if args.language:
        tags = present if _key(args.language) in ALL else [parse_language(args.language)]
        missing = [t for t in tags if t not in present]
        if missing:
            fail(f"The Central {entry['name']} does not have {NAMES[missing[0]]}.", options=[NAMES[t] for t in present])
    elif len(present) == 1:
        tags = present
    else:
        default = read_field(root, layout, "default_language")
        options = sorted(present, key=lambda t: t != default)
        ask("Which language?", [NAMES[t] for t in options] + ["All"], central=entry["name"],
            default=NAMES[default] if default in present else None)
    remove, restore, warnings, adjust = _reset_scope(root, layout, args.kind, tags)
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    preview = {"central": entry["name"], "default": entry["name"] == data["default"], "kind": args.kind,
               "languages": [NAMES[t] for t in tags], "remove": [rel(p) for p in remove],
               "restore_template": [rel(c) for c, _ in restore], "adjust": [rel(c) for c, _ in adjust],
               "warnings": warnings}
    if not remove and not restore and not adjust:
        return {"status": "ok", **preview, "message": "Nothing to reset."}
    if not args.confirm:
        return {"status": "preview", **preview, "confirmation": "--confirm"}
    _apply(root, remove, restore, adjust)
    return {"status": "ok", **preview}


def cmd_remove_mission(data, args):
    entry = resolve(data, args.central)
    root = local_root(entry)
    layout = layout_of(root)
    tag = resolve_language(root, layout, args.language, entry["name"])
    missions = missions_in(root / layout.missions(tag))
    if not missions:
        fail(f"{NAMES[tag]} has no missions.")
    if not args.mission:
        ask("Which mission?", sorted(m["id"] for m in missions), central=entry["name"], language=NAMES[tag])
    mission = _find_mission(missions, args.mission)
    if not mission:
        fail(f"Mission {args.mission} not found in {NAMES[tag]}.", options=sorted(m["id"] for m in missions))
    practices = [p for p in practices_in(root, layout, tag) if p["mission_id"] == mission["id"]]
    ids = {p["id"] for p in practices}
    remove = [mission["file"]] + [p["file"] for p in practices]
    adjust, restore = [], []
    progress = root / layout.progress_log(tag)
    if ids and progress.is_file():
        current = progress.read_text(encoding="utf-8")
        cleaned = progress_without_practices(current, layout.render("progress-log", tag), layout, ids)
        if cleaned != current:
            adjust.append((progress, cleaned))
    pointer = root / layout.active_session(tag)
    if pointer.is_file() and any(i in pointer.read_text(encoding="utf-8") for i in ids):
        restore.append((pointer, layout.render("active-session", tag)))
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    remaining = sorted({m["id"] for m in missions} - {mission["id"]})
    default = default_missions(root, layout).get(tag)
    new_default = default if default != mission["id"] else (remaining[0] if len(remaining) == 1 else None)
    preview = {"central": entry["name"], "language": NAMES[tag], "mission": _public([mission])[0],
               "remove": [rel(p) for p in remove], "adjust": [rel(c) for c, _ in adjust],
               "restore_template": [rel(c) for c, _ in restore], "default_mission_after": new_default}
    if _key(args.confirm or "") != _key(mission["id"]):
        if args.confirm:
            fail("The confirmation does not match the mission_id.", expected=mission["id"])
        return {"status": "preview", **preview, "confirmation": f"--confirm {mission['id']}"}
    _apply(root, remove, restore, adjust)
    if default != new_default:
        set_default_mission(root, layout, tag, new_default)
    return {"status": "ok", **preview}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registry", help="file of the Central registry")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("info")
    p.add_argument("--central")
    p = sub.add_parser("create")
    p.add_argument("--root", required=True)
    p.add_argument("--name")
    p.add_argument("--provider", choices=PROVIDERS)
    p.add_argument("--native")
    p.add_argument("languages", nargs="*")
    p = sub.add_parser("register")
    p.add_argument("--root", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--provider", choices=PROVIDERS, required=True)
    p.add_argument("--access", choices=ACCESS, required=True)
    p.add_argument("--native")
    p.add_argument("languages", nargs="*")
    p = sub.add_parser("default")
    p.add_argument("name", nargs="?")
    p.add_argument("--language")
    p.add_argument("--mission")
    p.add_argument("--central")
    p = sub.add_parser("practices")
    p.add_argument("language", nargs="?")
    p.add_argument("--mission")
    p.add_argument("--status")
    p.add_argument("--central")
    p = sub.add_parser("remove")
    p.add_argument("--central")
    p.add_argument("--confirm")
    p.add_argument("--registry-only", action="store_true")
    p = sub.add_parser("remove-mission")
    p.add_argument("mission", nargs="?")
    p.add_argument("--language")
    p.add_argument("--central")
    p.add_argument("--confirm")
    p = sub.add_parser("backup")
    p.add_argument("--central")
    p.add_argument("--destination")
    p = sub.add_parser("reset")
    p.add_argument("kind", choices=RESET_KINDS)
    p.add_argument("language", nargs="?")
    p.add_argument("--central")
    p.add_argument("--confirm", action="store_true")
    args = parser.parse_args(argv)
    path = registry_path(args.registry)
    handlers = {"info": lambda: cmd_info(data, args), "create": lambda: cmd_create(data, args, path),
                "register": lambda: cmd_register(data, args, path), "default": lambda: cmd_default(data, args, path),
                "practices": lambda: cmd_practices(data, args), "remove": lambda: cmd_remove(data, args, path),
                "remove-mission": lambda: cmd_remove_mission(data, args), "backup": lambda: cmd_backup(data, args),
                "reset": lambda: cmd_reset(data, args)}
    try:
        data = load(path)
        result = handlers[args.command]()
    except ValueError as error:
        result = {"status": "error", "message": str(error)}
    except Outcome as outcome:
        result = outcome.payload
    result["registry"] = str(path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {"ok": 0, "preview": 0, "ambiguous": 2}.get(result["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
