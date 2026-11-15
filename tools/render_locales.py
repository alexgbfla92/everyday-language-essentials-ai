"""Render the Central record templates for every supported native language.

  python tools/render_locales.py          # writes skills/talkgo/assets/locales/<code>/templates/*.md
  python tools/render_locales.py --check  # fails if a rendered template is missing or out of date

Master templates live in skills/talkgo/assets/templates/ and use [[token]] for text that is
translated per native language (strings in assets/locales/<code>/locale.json, key "text").
{{placeholder}} values (target language name, tag, native language) are filled when a record
is created in a Central.
"""
import json
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "skills" / "talkgo" / "assets"
TOKEN = re.compile(r"\[\[([a-z0-9_]+)\]\]")


def render(text, strings):
    missing = sorted({t for t in TOKEN.findall(text) if t not in strings})
    if missing:
        raise SystemExit(f"Missing translations: {', '.join(missing)}")
    return TOKEN.sub(lambda m: strings[m.group(1)], text)


def rendered():
    out = {}
    for locale_file in sorted((ASSETS / "locales").glob("*/locale.json")):
        strings = json.loads(locale_file.read_text(encoding="utf-8"))["text"]
        for template in sorted((ASSETS / "templates").glob("*.md")):
            target = locale_file.parent / "templates" / template.name
            out[target] = render(template.read_text(encoding="utf-8"), strings)
    return out


def main(argv):
    files = rendered()
    if "--check" in argv:
        stale = [str(p.relative_to(ASSETS)) for p, text in files.items()
                 if not p.is_file() or p.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit("Out of date (run python tools/render_locales.py): " + ", ".join(stale))
        print(f"{len(files)} templates up to date")
        return 0
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"{len(files)} templates written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
