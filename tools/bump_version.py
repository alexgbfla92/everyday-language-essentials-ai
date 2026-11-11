"""Atualiza a versão em todos os lugares a partir do VERSION da raiz.

  python tools/bump_version.py patch|minor|major   # sobe a versão e propaga
  python tools/bump_version.py 1.2.3              # define a versão e propaga
  python tools/bump_version.py --check            # só confere se tudo está igual ao VERSION

Cada PR deve subir a versão (a verificação do GitHub recusa PR sem mudança no VERSION).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = ROOT / "VERSION"
MANIFESTS = [ROOT / "plugin.json", ROOT / ".claude-plugin" / "plugin.json"]
SKILL = ROOT / "skills" / "everylang" / "SKILL.md"
SKILL_LINE = re.compile(r"^(Versão instalada: )(\S+)$", re.M)
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def current():
    return VERSION.read_text(encoding="utf-8").strip()


def found():
    versions = {str(VERSION.relative_to(ROOT)): current()}
    for path in MANIFESTS:
        versions[str(path.relative_to(ROOT))] = json.loads(path.read_text(encoding="utf-8"))["version"]
    match = SKILL_LINE.search(SKILL.read_text(encoding="utf-8"))
    versions[str(SKILL.relative_to(ROOT))] = match.group(2) if match else None
    return versions


def bump(version, part):
    major, minor, patch = map(int, version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def write(version):
    VERSION.write_text(version + "\n", encoding="utf-8")
    for path in MANIFESTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    text = SKILL.read_text(encoding="utf-8")
    if not SKILL_LINE.search(text):
        raise SystemExit("SKILL.md sem a linha 'Versão instalada: X.Y.Z'.")
    SKILL.write_text(SKILL_LINE.sub(rf"\g<1>{version}", text), encoding="utf-8")


def main(argv):
    if len(argv) != 1:
        raise SystemExit(__doc__)
    if argv[0] == "--check":
        versions = found()
        wrong = {k: v for k, v in versions.items() if v != current()}
        if wrong or not SEMVER.match(current()):
            print("Versões divergentes do VERSION:", json.dumps(versions, indent=2))
            return 1
        print(f"Versão {current()} consistente em {len(versions)} arquivos.")
        return 0
    version = argv[0] if SEMVER.match(argv[0]) else bump(current(), argv[0]) \
        if argv[0] in ("major", "minor", "patch") else None
    if not version:
        raise SystemExit(__doc__)
    write(version)
    print(version)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
