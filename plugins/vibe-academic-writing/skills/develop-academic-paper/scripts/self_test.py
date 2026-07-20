#!/usr/bin/env python3
"""Run deterministic hardening regression tests for this skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _common import basic_file_integrity, cloud_sync_provider, no_credentials, redact_url, scan_text_file, write_json


SCRIPTS = Path(__file__).resolve().parent


class HardeningTests(unittest.TestCase):
    def test_redact_url(self) -> None:
        value = redact_url("https://student:password@example.edu/auth/abc123/file.pdf?token=secret&view=1#session")
        self.assertEqual(value, "https://example.edu/auth/[redacted]/file.pdf?view=1")

    def test_credential_keys_and_text(self) -> None:
        with self.assertRaises(ValueError):
            no_credentials({"accessToken": "abc12345"})
        with self.assertRaises(ValueError):
            no_credentials({"note": "Authorization: Bearer abcdefghijk"})

    def test_cloud_sync_detection(self) -> None:
        self.assertEqual(cloud_sync_provider(Path("/tmp/OneDrive/course")), "Microsoft OneDrive")

    def test_atomic_json_and_sensitive_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "state.json"
            write_json(target, {"safe": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"safe": True})
            note = root / "note.md"
            note.write_text("password=not-for-storage\n", encoding="utf-8")
            findings = scan_text_file(note)
            self.assertEqual(findings[0]["kind"], "credential_assignment")
            self.assertNotIn("not-for-storage", json.dumps(findings))

    def test_active_content_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            macro = root / "course.docm"
            macro.write_bytes(b"PK\x03\x04")
            archive = root / "course.zip"
            archive.write_bytes(b"PK\x03\x04")
            self.assertEqual(basic_file_integrity(macro)[0], "unsafe_macro")
            self.assertEqual(basic_file_integrity(archive)[0], "archive_requires_review")

    def test_run_state_and_browser_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = [sys.executable, "-B", str(SCRIPTS / "manage_run_state.py")]
            subprocess.run(command + ["start", str(root), "--mode", "single_task", "--operation", "test"], check=True, capture_output=True, text=True)
            subprocess.run(command + ["stage", str(root), "--stage", "intake", "--status", "running"], check=True, capture_output=True, text=True)
            subprocess.run(command + ["stage", str(root), "--stage", "intake", "--status", "succeeded", "--output", "00_brief/intake.json"], check=True, capture_output=True, text=True)
            state = json.loads((root / "run_state.json").read_text(encoding="utf-8"))
            resume = json.loads((root / "resume_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["last_successful_checkpoint"], "intake")
            self.assertEqual(state["stages"]["intake"]["attempts"], 1)
            self.assertEqual(resume["key_artifacts"], ["00_brief/intake.json"])
            lock = [sys.executable, "-B", str(SCRIPTS / "browser_lock.py")]
            subprocess.run(lock + ["acquire", str(root), "--owner", state["run_id"]], check=True, capture_output=True, text=True)
            refused = subprocess.run(lock + ["acquire", str(root), "--owner", "another-run"], capture_output=True, text=True)
            self.assertEqual(refused.returncode, 2)
            subprocess.run(lock + ["renew", str(root), "--owner", state["run_id"]], check=True, capture_output=True, text=True)
            subprocess.run(lock + ["release", str(root), "--owner", state["run_id"]], check=True, capture_output=True, text=True)

    def test_default_language_and_cloud_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            container = Path(temporary)
            workspace = container / "workspace"
            init = [sys.executable, "-B", str(SCRIPTS / "init_workspace.py")]
            subprocess.run(init + [str(workspace), "--mode", "single_task", "--task-name", "Example"], check=True, capture_output=True, text=True)
            config = json.loads((workspace / "workspace_config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["workspace_language"], "en")
            cloud = container / "OneDrive" / "course"
            preflight = [sys.executable, "-B", str(SCRIPTS / "preflight_workspace.py"), str(cloud)]
            blocked = subprocess.run(preflight, capture_output=True, text=True)
            self.assertEqual(blocked.returncode, 2)
            acknowledged = subprocess.run(preflight + ["--acknowledge-cloud-sync"], capture_output=True, text=True)
            self.assertEqual(acknowledged.returncode, 0)

    def test_compact_sync_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote_path = root / "remote_inventory.json"
            local_path = root / "local_inventory.json"
            output = root / "sync"
            write_json(
                remote_path,
                {
                    "schema_version": "1.2",
                    "materials": [
                        {
                            "remote_item_id": "item-1",
                            "name": "reading.pdf",
                            "material_type": "pdf",
                            "dashboard_path": "Course > Week 1",
                            "clean_url": "https://example.edu/reading.pdf",
                            "record_role": "downloadable_file",
                            "download_eligible": True,
                            "size_bytes": 10,
                        }
                    ],
                },
            )
            write_json(
                local_path,
                {
                    "schema_version": "1.2",
                    "materials": [
                        {
                            "remote_item_id": "item-1",
                            "name": "reading.pdf",
                            "local_path": "Week-1/reading.pdf",
                            "size_bytes": 10,
                            "integrity_status": "verified",
                        }
                    ],
                },
            )
            command = [sys.executable, "-B", str(SCRIPTS / "compare_course_sync.py"), str(remote_path), str(local_path), str(output), "--workspace-root", str(root)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            state = json.loads((output / "sync_state.json").read_text(encoding="utf-8"))
            result = state["results"][0]
            self.assertEqual(result["comparison_status"], "unchanged")
            self.assertEqual(result["local_path"], "Week-1/reading.pdf")
            self.assertNotIn("remote", result)
            self.assertNotIn("local", result)

    def test_final_validation_requires_safe_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            container = Path(temporary)
            workspace = container / "workspace"
            init = [sys.executable, "-B", str(SCRIPTS / "init_workspace.py")]
            subprocess.run(init + [str(workspace), "--mode", "single_task", "--task-name", "Final Test"], check=True, capture_output=True, text=True)
            task = workspace / "Final-Test"
            config_path = task / "task_config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["delivery_formats"] = ["word"]
            config["result_directory"] = "Final-Test_result"
            write_json(config_path, config)
            for relative in ("04_content_plan/plan.md", "05_draft/draft.md", "07_final_internal/final.md"):
                path = task / relative
                path.write_text("Safe academic content.\n", encoding="utf-8")
            result = task / "Final-Test_result"
            result.mkdir()
            (result / "final.docx").write_bytes(b"PK\x03\x04test")
            scan = [sys.executable, "-B", str(SCRIPTS / "scan_sensitive_artifacts.py"), str(task)]
            subprocess.run(scan, check=True, capture_output=True, text=True)
            validate = [sys.executable, "-B", str(SCRIPTS / "validate_artifacts.py"), str(task), "--kind", "task", "--stage", "final"]
            subprocess.run(validate, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
