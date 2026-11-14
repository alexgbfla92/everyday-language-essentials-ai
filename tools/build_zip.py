"""Gera o pacote .zip da skill para envio pelo navegador (Claude e ChatGPT).

  python tools/build_zip.py            # skill: dist/talkgo-practice-<versão>.zip (Claude e ChatGPT > Habilidades)
  python tools/build_zip.py --plugin   # plugin: dist/talkgo-plugin-<versão>.zip (ChatGPT > Plugins > Adicionar)

O .zip contém só a pasta practice/ (SKILL.md, references/, assets/, scripts/), como exigem o
Claude (pasta com o nome da skill na raiz do arquivo) e o ChatGPT (uma skill completa por envio).
Antes de gravar, confere: nome da pasta = name do SKILL.md, frontmatter válido, nenhuma entrada fora
de practice/ e nenhum arquivo oculto, compilado ou de sistema.
"""
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = "practice"
FORBIDDEN = re.compile(r"(^|/)(\.[^/]+|__pycache__|Thumbs\.db)(/|$)|\.(pyc|pyo|exe|dll|so)$")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit("SKILL.md sem frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def plugin_zip(skill_zip, version):
    """Remonta o pacote no formato de plugin: .codex-plugin/plugin.json + skills/practice/."""
    meta = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    manifest = {k: meta[k] for k in ("name", "version", "description", "author", "homepage", "repository",
                                     "keywords")}
    manifest["skills"] = "./skills/"
    manifest["interface"] = meta["extensions"]["com.openai"]["interface"]
    if manifest["version"] != version:
        raise SystemExit("plugin.json com versão diferente do VERSION")
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(skill_zip)) as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        dst.writestr(".codex-plugin/plugin.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for info in src.infolist():
            if not info.is_dir():
                dst.writestr("skills/" + info.filename, src.read(info))
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
        problems.append(f"frontmatter deve ter só name e description: {sorted(meta)}")
    if meta.get("name") != SKILL:
        problems.append(f"name ({meta.get('name')}) diferente da pasta ({SKILL})")
    if not 0 < len(meta.get("description", "")) <= 1024 or re.search(r"[<>]", meta.get("description", "")):
        problems.append("description vazia, com mais de 1024 caracteres ou com < >")
    if f"Versão instalada: {version}" not in skill_md:
        problems.append("linha 'Versão instalada' do SKILL.md diferente do VERSION")
    if problems:
        raise SystemExit("Pacote recusado:\n- " + "\n- ".join(problems))
    name = f"talkgo-{SKILL}-{version}.zip"
    if plugin:
        raw, name = plugin_zip(raw, version), f"talkgo-plugin-{version}.zip"
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = archive.namelist()
    out = ROOT / "dist" / name
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(raw)
    files = sum(1 for n in names if not n.endswith("/"))
    print(f"{out} ({len(raw) // 1024} KB, {files} arquivos)")
    return out


if __name__ == "__main__":
    build(plugin="--plugin" in sys.argv[1:])
    sys.exit(0)
