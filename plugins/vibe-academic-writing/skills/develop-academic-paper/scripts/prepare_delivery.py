#!/usr/bin/env python3
"""Create a task result directory after the user confirms Word, PDF, or both."""

from __future__ import annotations

import argparse

from _common import SCHEMA_VERSION, no_credentials, now_utc, read_json, resolve_explicit, slugify, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("task_directory", help="Single-task or course-assignment directory")
    value.add_argument("--format", choices=("word", "pdf", "both"), required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.task_directory)
    candidates = [root / "task_config.json", root / "assignment_config.json"]
    config_path = next((path for path in candidates if path.is_file()), None)
    if config_path is None:
        raise SystemExit("Task directory must contain task_config.json or assignment_config.json")
    config = read_json(config_path)
    no_credentials(config)
    name = str(config.get("task_name") or config.get("assignment_name") or config.get("title") or "task")
    formats = ["word", "pdf"] if args.format == "both" else [args.format]
    configured = str(config.get("result_directory") or "")
    if configured:
        result_root = root / configured
    else:
        base_name = f"{slugify(name, fallback='task')}_result"
        result_root = root / base_name
        if result_root.exists() and any(result_root.iterdir()):
            index = 2
            while (root / f"{base_name}_v{index}").exists():
                index += 1
            result_root = root / f"{base_name}_v{index}"
    result_root.mkdir(parents=True, exist_ok=True)
    config.update(
        {
            "schema_version": SCHEMA_VERSION,
            "delivery_formats": formats,
            "result_directory": result_root.relative_to(root).as_posix(),
            "updated_at": now_utc(),
        }
    )
    write_json(config_path, config)
    write_json(
        result_root / "delivery_manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_at": now_utc(),
            "task_name": name,
            "requested_formats": formats,
            "expected_extensions": [".docx" if item == "word" else ".pdf" for item in formats],
            "status": "awaiting_render_and_validation",
        },
    )
    print(result_root.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
