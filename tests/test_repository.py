from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "vibe-academic-writing"
SKILL = PLUGIN / "skills" / "develop-academic-paper"


class RepositoryTests(unittest.TestCase):
    def test_required_project_files_exist(self) -> None:
        for relative in (
            "README.md",
            "README.zh-CN.md",
            "LICENSE",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            ".agents/plugins/marketplace.json",
            "plugins/vibe-academic-writing/.codex-plugin/plugin.json",
            "plugins/vibe-academic-writing/skills/develop-academic-paper/SKILL.md",
            "plugins/vibe-academic-writing/skills/develop-academic-paper/LICENSE.txt",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readme_language_switches(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("[简体中文](README.zh-CN.md)", english)
        self.assertIn("[English](README.md)", chinese)

    def test_skill_frontmatter_is_minimal_and_valid(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        self.assertIsNotNone(match)
        keys = []
        for line in match.group(1).splitlines():
            if line and not line.startswith((" ", "\t")) and ":" in line:
                keys.append(line.split(":", 1)[0])
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: develop-academic-paper", match.group(1))

    def test_plugin_and_marketplace_identity_match(self) -> None:
        plugin = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(plugin["name"], "vibe-academic-writing")
        self.assertEqual(plugin["version"], "1.3.0")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertTrue((PLUGIN / plugin["skills"]).is_dir())
        for key in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "defaultPrompt",
        ):
            self.assertIn(key, plugin["interface"])
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], plugin["name"])
        self.assertEqual(entry["source"]["path"], "./plugins/vibe-academic-writing")
        self.assertTrue((ROOT / entry["source"]["path"]).is_dir())
        self.assertFalse((ROOT / "skills" / "develop-academic-paper").exists())

    def test_json_assets_parse(self) -> None:
        paths = list(SKILL.rglob("*.json"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_no_runtime_caches_or_private_workspace_files(self) -> None:
        forbidden_names = {
            "__pycache__",
            "run_state.json",
            "resume_state.json",
            "events.jsonl",
            "workspace_config.json",
            "course_catalog.json",
            "remote_inventory.json",
            "local_inventory.json",
            "sync_state.json",
        }
        violations = [
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.name in forbidden_names
        ]
        self.assertEqual(violations, [])

    def test_no_binary_course_materials(self) -> None:
        blocked_extensions = {
            ".doc", ".docx", ".pdf", ".ppt", ".pptm", ".pptx", ".xls", ".xlsx"
        }
        violations = [
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in blocked_extensions
        ]
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
