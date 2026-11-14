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
        self.assertFalse((ROOT / "SKILL.md").exists(), "a skill fica em skills/<nome>/, não na raiz")

    def test_manifests_point_to_the_same_plugin(self):
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["name"], claude["name"])
        self.assertNotIn("skills", claude, "skills/ é descoberto automaticamente")
        interface = portable["extensions"]["com.openai"]["interface"]
        for field in ("displayName", "shortDescription", "category", "defaultPrompt"):
            self.assertIn(field, interface)
        claude_market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        openai_market = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(claude_market["name"], openai_market["name"])
        self.assertEqual([p["name"] for p in claude_market["plugins"]], [portable["name"]])
        entry = openai_market["plugins"][0]
        self.assertEqual(entry["name"], portable["name"])
        self.assertEqual(entry["source"], {"source": "local", "path": "./"})
        for field in ("policy", "category"):
            self.assertIn(field, entry)

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
                                f"{path}: {target} sai da pasta da skill")


if __name__ == "__main__":
    unittest.main()
