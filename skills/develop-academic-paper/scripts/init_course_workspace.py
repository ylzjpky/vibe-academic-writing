#!/usr/bin/env python3
"""Create course folders from a local course catalog without storing credentials."""

from __future__ import annotations

import argparse

from _common import SCHEMA_VERSION, cloud_sync_provider, no_credentials, now_utc, read_json, read_records, resolve_explicit, slugify, write_json, write_text


COURSE_FOLDERS = (
    "01_course_materials",
    "02_course_library",
    "03_assignments",
    "04_course_memory",
    "05_sync",
    "90_missing_materials",
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("workspace", help="Existing course workspace")
    value.add_argument("--catalog", required=True, help="Course catalog JSON or CSV")
    return value


def main() -> int:
    args = parser().parse_args()
    workspace = resolve_explicit(args.workspace)
    workspace_config = workspace / "workspace_config.json"
    if not workspace_config.is_file() or read_json(workspace_config).get("workspace_mode") != "course":
        raise SystemExit("Target must be an initialized course workspace with workspace_mode='course'")
    workspace_data = read_json(workspace_config)
    provider = cloud_sync_provider(workspace)
    acknowledgement = workspace_data.get("cloud_sync_acknowledgement") or {}
    if provider and acknowledgement.get("provider") != provider:
        raise SystemExit(f"Workspace appears to be inside {provider}; run preflight_workspace.py and obtain explicit user acknowledgement before creating course folders")
    catalog_path = resolve_explicit(args.catalog)
    catalog_document = read_json(catalog_path) if catalog_path.suffix.lower() == ".json" else {}
    records = read_records(catalog_path)
    no_credentials(records)
    courses = []
    seen: set[str] = set()
    seen_folders: set[str] = set()
    for index, row in enumerate(records, start=1):
        name = str(row.get("course_name") or row.get("name") or "").strip()
        if not name:
            raise SystemExit(f"Course record {index} has no course_name/name")
        course_id = str(row.get("course_id") or row.get("id") or f"course-{index:03d}").strip()
        if course_id in seen:
            raise SystemExit(f"Duplicate course_id: {course_id}")
        seen.add(course_id)
        folder_name = slugify(str(row.get("folder_name") or name), fallback=course_id)
        if folder_name.casefold() in seen_folders:
            folder_name = f"{folder_name}-{slugify(course_id, fallback=f'course-{index:03d}')}"
        seen_folders.add(folder_name.casefold())
        course_root = workspace / "courses" / folder_name
        for folder in COURSE_FOLDERS:
            (course_root / folder).mkdir(parents=True, exist_ok=True)
        memory_root = course_root / "04_course_memory"
        memory_file = memory_root / "course_memory.md"
        task_index = memory_root / "task_index.csv"
        if not memory_file.exists():
            write_text(memory_file, "# Course memory\n\n")
        if not task_index.exists():
            write_text(task_index, "assignment_id,title,status,source_scope,updated_at,assignment_path\n")
        course = {
            "course_id": course_id,
            "course_name": name,
            "folder_name": folder_name,
            "dashboard_path": str(row.get("dashboard_path") or ""),
            "status": str(row.get("status") or "active"),
        }
        courses.append(course)
        manifest_path = course_root / "course_manifest.json"
        existing = read_json(manifest_path) if manifest_path.exists() else {}
        manifest = {
            **existing,
            "schema_version": SCHEMA_VERSION,
            **course,
            "created_at": existing.get("created_at") or now_utc(),
            "updated_at": now_utc(),
            "last_sync_at": existing.get("last_sync_at"),
            "credential_storage": "prohibited",
        }
        write_json(manifest_path, manifest)
    output = workspace / "course_catalog.json"
    document = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "course_count": len(courses),
        "courses": courses,
    }
    if isinstance(catalog_document, dict) and catalog_document.get("page_verification"):
        document["page_verification"] = catalog_document["page_verification"]
    write_json(output, document)
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
