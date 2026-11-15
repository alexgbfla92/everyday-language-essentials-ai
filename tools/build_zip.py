"""Build the .zip packages uploaded through the browser (Claude and ChatGPT).

  python tools/build_zip.py            # skill: dist/talkgo-skill-<version>.zip
  python tools/build_zip.py --plugin   # plugin: dist/talkgo-plugin-<version>.zip (Plugins > Add, Claude and ChatGPT)

The skill .zip holds only the talkgo/ folder (SKILL.md, references/, assets/, scripts/). The plugin .zip
holds .claude-plugin/plugin.json, .codex-plugin/plugin.json and skills/. Before writing, it checks:
folder name = name in SKILL.md, valid frontmatter, no entry outside the expected folders and no hidden,
compiled or system file.
"""
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = "talkgo"
FORBIDDEN = re.compile(r"(^|/)(\.[^/]+|__pycache__|Thumbs\.db)(/|$)|\.(pyc|pyo|exe|dll|so)$")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit("SKILL.md without frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def plugin_zip(version):
    """Build the plugin for Claude and ChatGPT: .claude-plugin/, .codex-plugin/ and every skill in skills/."""
    skills_zip = subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip", "--prefix=skills/",
                                 "HEAD:skills"], check=True, capture_output=True).stdout
    meta = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    manifest = {k: meta[k] for k in ("name", "version", "description", "author", "homepage", "repository",
                                     "keywords")}
    manifest["skills"] = "./skills/"
    manifest["interface"] = meta["extensions"]["com.openai"]["interface"]
    if manifest["version"] != version:
        raise SystemExit("plugin.json version differs from VERSION")
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(skills_zip)) as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        dst.writestr(".codex-plugin/plugin.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        dst.writestr(".claude-plugin/plugin.json", (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        for info in src.infolist():
            if not info.is_dir():
                dst.writestr(info.filename, src.read(info))
    return out.getvalue()


def build(plugin=False):
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    raw = subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip", f"--prefix={SKILL}/",
                          f"HEAD:skills/{SKILL}"], check=True, capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        skill_md = archive.read(f"{SKILL}/SKILL.md").decode("utf-8")
    problems = [n for n in names if not n.startswith(f"{SKILL}/")]
    problems += [n for n in names if FORBIDDEN.search(n[len(SKILL) + 1:])]
    meta = frontmatter(skill_md)
    if set(meta) != {"name", "description"}:
        problems.append(f"frontmatter must have only name and description: {sorted(meta)}")
    if meta.get("name") != SKILL:
        problems.append(f"name ({meta.get('name')}) differs from the folder ({SKILL})")
    if not 0 < len(meta.get("description", "")) <= 1024 or re.search(r"[<>]", meta.get("description", "")):
        problems.append("description empty, longer than 1024 characters or with < >")
    if f"Installed version: {version}" not in skill_md:
        problems.append("'Installed version' line of SKILL.md differs from VERSION")
    if problems:
        raise SystemExit("Package refused:\n- " + "\n- ".join(problems))
    name = f"talkgo-skill-{version}.zip"
    if plugin:
        raw, name = plugin_zip(version), f"talkgo-plugin-{version}.zip"
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = archive.namelist()
            for skill_md in (n for n in names if re.fullmatch(r"skills/[^/]+/SKILL\.md", n)):
                folder = skill_md.split("/")[1]
                meta = frontmatter(archive.read(skill_md).decode("utf-8"))
                if meta.get("name") != folder or set(meta) != {"name", "description"}:
                    raise SystemExit(f"Package refused: invalid frontmatter in {skill_md}")
            bad = [n for n in names if FORBIDDEN.search(n.split("/", 2)[-1]) and not n.endswith("plugin.json")]
            if bad:
                raise SystemExit("Package refused: hidden or compiled files: " + ", ".join(bad))
    out = ROOT / "dist" / name
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(raw)
    files = sum(1 for n in names if not n.endswith("/"))
    print(f"{out} ({len(raw) // 1024} KB, {files} files)")
    return out


if __name__ == "__main__":
    build(plugin="--plugin" in sys.argv[1:])
    sys.exit(0)
