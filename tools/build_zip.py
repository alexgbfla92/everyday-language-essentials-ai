"""Gera o pacote .zip da skill para envio pelo navegador (Claude e ChatGPT).

  python tools/build_zip.py            # cria dist/everylang-<versão>.zip a partir do git (HEAD)

O .zip contém só a pasta everylang/ (SKILL.md, references/, assets/, scripts/), como exigem o
Claude (pasta com o nome da skill na raiz do arquivo) e o ChatGPT (uma skill completa por envio).
Antes de gravar, confere: nome da pasta = name do SKILL.md, frontmatter válido, nenhuma entrada fora
de everylang/ e nenhum arquivo oculto, compilado ou de sistema.
"""
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = "everylang"
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


def build():
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
    out = ROOT / "dist" / f"{SKILL}-{version}.zip"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(raw)
    files = sum(1 for n in names if not n.endswith("/"))
    print(f"{out} ({len(raw) // 1024} KB, {files} arquivos)")
    return out


if __name__ == "__main__":
    build()
    sys.exit(0)
