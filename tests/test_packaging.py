import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "talkgo"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    block = text.split("---")[1]
    return dict(line.split(":", 1) for line in block.strip().splitlines() if ":" in line)


class PackagingTests(unittest.TestCase):
    def test_versions_match_root_version(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "bump_version.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_skill_folder_matches_name(self):
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            meta = frontmatter(skill)
            self.assertEqual(meta["name"].strip(), skill.parent.name)
            self.assertRegex(meta["name"].strip(), r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertLessEqual(len(meta["description"].strip()), 1024)
        self.assertFalse((ROOT / "SKILL.md").exists(), "the skill lives in skills/<name>/, not at the root")

    def test_manifests_point_to_the_same_plugin(self):
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["name"], claude["name"])
        self.assertNotIn("skills", claude, "skills/ is discovered automatically")
        interface = portable["extensions"]["com.openai"]["interface"]
        for field in ("displayName", "shortDescription", "category", "defaultPrompt"):
            self.assertIn(field, interface)
        self.assertFalse((ROOT / ".claude-plugin" / "marketplace.json").exists(), "install only through the .zip")
        self.assertFalse((ROOT / ".agents").exists(), "install only through the .zip")

    def test_release_workflow_publishes_the_plugin_zip(self):
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        for needle in ('tags: ["v*"]', "workflow_dispatch", "contents: write", "build_zip.py --plugin",
                       "dist/talkgo-plugin.zip", "gh release create"):
            self.assertIn(needle, workflow)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("releases/latest/download/talkgo-plugin.zip", readme)

    def test_no_compiled_hidden_or_system_files_tracked_in_skill(self):
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "skills"], capture_output=True,
                                 text=True).stdout.split()
        bad = [f for f in tracked if re.search(r"(^|/)(\.[^/]+|__pycache__)(/|$)|\.(pyc|pyo)$", f)]
        self.assertEqual(bad, [])

    def test_plugin_zip_layout(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import io
        import zipfile
        import build_zip
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        with zipfile.ZipFile(io.BytesIO(build_zip.plugin_zip(version))) as z:
            names = z.namelist()
            manifest = json.loads(z.read(".codex-plugin/plugin.json"))
        self.assertIn("skills/talkgo/SKILL.md", names)
        self.assertIn(".claude-plugin/plugin.json", names)
        self.assertEqual((manifest["name"], manifest["skills"]), ("talkgo", "./skills/"))
        manifests = {".codex-plugin/plugin.json", ".claude-plugin/plugin.json"}
        self.assertTrue(all(n in manifests or n.startswith("skills/") for n in names))

    def test_links_inside_skill_stay_inside_skill(self):
        link = re.compile(r"\]\(([^)\s#]+)")
        for path in SKILL_DIR.rglob("*.md"):
            for target in link.findall(path.read_text(encoding="utf-8")):
                if target.startswith("http"):
                    continue
                resolved = (path.parent / target).resolve()
                self.assertTrue(resolved.exists(), f"{path}: {target}")
                self.assertTrue(resolved == SKILL_DIR or SKILL_DIR in resolved.parents,
                                f"{path}: {target} leaves the skill folder")


    def test_locale_templates_are_rendered_and_complete(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "render_locales.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        locales = sorted(p.name for p in (SKILL_DIR / "assets" / "locales").iterdir())
        self.assertEqual(locales, ["de", "en", "es", "fr", "pt-BR"])
        keys = None
        for code in locales:
            data = json.loads((SKILL_DIR / "assets" / "locales" / code / "locale.json").read_text(encoding="utf-8"))
            shape = {k: sorted(v) if isinstance(v, dict) else None for k, v in data.items()}
            keys = keys or shape
            self.assertEqual(shape, keys, code)
            self.assertEqual(len(set(data["paths"].values())), len(data["paths"]), code)

    def test_every_target_language_is_complete(self):
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from layout import TARGETS
        from central import NAMES, parse_language
        catalog = (SKILL_DIR / "assets" / "reference" / "languages.md").read_text(encoding="utf-8")
        rows = dict(re.findall(r"^\| ([a-z]{2}(?:-[A-Z]{2})?) \|.*\[targets/([a-z]+)\]", catalog, re.M))
        self.assertEqual(list(rows), list(TARGETS))
        for tag in TARGETS:
            folder = SKILL_DIR / "assets" / "targets" / rows[tag]
            for name in ("notes.md", "essentials.md", "diagnostic-roadmap.md"):
                self.assertTrue((folder / name).is_file(), f"{tag}: {name}")
            self.assertIn(f"({tag})", (folder / "notes.md").read_text(encoding="utf-8"))
            self.assertEqual(parse_language(NAMES[tag]), tag)
            self.assertEqual(parse_language(tag), tag)
        for code in ("en", "pt-BR", "es", "fr", "de"):
            data = json.loads((SKILL_DIR / "assets" / "locales" / code / "locale.json").read_text(encoding="utf-8"))
            self.assertEqual(list(data["targets"]), list(TARGETS), code)
            folders = [data["targets"][t]["folder"] for t in TARGETS]
            self.assertEqual(len(set(folders)), len(folders), code)

    def test_translated_readmes_keep_the_same_sections(self):
        def sections(path):
            return len(re.findall(r"^## ", path.read_text(encoding="utf-8"), re.M))
        expected = sections(ROOT / "README.md")
        for code in ("pt-BR", "es", "fr", "de", "zh-CN"):
            path = ROOT / f"README-{code}.md"
            self.assertTrue(path.exists(), path.name)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(sections(path), expected, path.name)
            self.assertIn("releases/latest/download/talkgo-plugin.zip", text, path.name)
            self.assertIn("(README.md)", text, path.name)

    def test_english_only_outside_translations(self):
        allowed = re.compile(r"^(README-[A-Za-z-]+\.md|tests/.*|skills/talkgo/assets/(locales|targets)/.*)$")
        portuguese = re.compile(r"\b(não|você|também|então|aluno|prática|missão|idioma|configuração|salvar)\b", re.I)
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
        found = []
        for name in tracked:
            if allowed.match(name) or not name.endswith((".md", ".py", ".json", ".yml")):
                continue
            for number, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
                if portuguese.search(line) and "ALIASES" not in line and "portuguese = re.compile" not in line:
                    found.append(f"{name}:{number}: {line.strip()[:80]}")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
