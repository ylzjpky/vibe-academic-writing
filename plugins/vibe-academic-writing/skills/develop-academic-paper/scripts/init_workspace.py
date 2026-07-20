#!/usr/bin/env python3
"""Initialize an academic workspace and, for single-task mode, a named task child."""

from __future__ import annotations

import argparse

from _common import SCHEMA_VERSION, cloud_sync_provider, now_utc, print_result, read_json, resolve_explicit, slugify, write_json, write_text


TASK_FOLDERS = (
    "00_brief",
    "01_sources",
    "02_source_registry",
    "03_evidence",
    "04_content_plan",
    "05_draft",
    "06_review",
    "07_final_internal",
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("workspace", help="Explicit workspace container to create or initialize")
    value.add_argument("--mode", choices=("single_task", "task", "course"), required=True, help="Use 'single_task' for one assignment; 'task' is accepted as a legacy alias")
    value.add_argument("--name", default="Academic Writing Workspace")
    value.add_argument("--task-name", help="Required display name for a new single task")
    value.add_argument("--task-id", help="Optional stable task identifier")
    value.add_argument("--language", default="English", help="Default academic artifact language")
    value.add_argument("--workspace-language", default="en", help="Interaction/report language; pass the detected user language when known")
    value.add_argument("--citation-style", default="apa-7")
    value.add_argument("--allow-cloud-synced-workspace", action="store_true", help="Proceed only after the user explicitly accepts detected cloud-sync storage")
    value.add_argument("--force", action="store_true", help="Replace only workspace_config.json")
    return value


def main() -> int:
    args = parser().parse_args()
    mode = "single_task" if args.mode == "task" else args.mode
    if mode == "single_task" and not args.task_name:
        raise SystemExit("--task-name is required for single_task mode")
    workspace = resolve_explicit(args.workspace)
    provider = cloud_sync_provider(workspace)
    existing_config_path = workspace / "workspace_config.json"
    existing_acknowledgement = read_json(existing_config_path).get("cloud_sync_acknowledgement") if existing_config_path.is_file() else {}
    if provider and not args.allow_cloud_synced_workspace and (existing_acknowledgement or {}).get("provider") != provider:
        raise SystemExit(f"Workspace appears to be inside {provider}; use a non-synced directory or obtain explicit user confirmation and rerun with --allow-cloud-synced-workspace")
    workspace.mkdir(parents=True, exist_ok=True)
    config_path = workspace / "workspace_config.json"
    if config_path.exists():
        existing = read_json(config_path)
        existing_mode = str(existing.get("workspace_mode") or "")
        normalized_existing = "single_task" if existing_mode == "task" else existing_mode
        if normalized_existing and normalized_existing != mode:
            raise SystemExit("Refusing to change an existing workspace between single_task and course modes")
        if args.force:
            existing.update(
                {
                    "schema_version": SCHEMA_VERSION,
                    "workspace_name": args.name,
                    "workspace_language": args.workspace_language,
                    "artifact_language": args.language,
                    "default_citation_style": args.citation_style,
                    "cloud_sync_acknowledgement": {"provider": provider, "acknowledged_at": now_utc(), "basis": "explicit_user_confirmation"} if provider else None,
                    "updated_at": now_utc(),
                }
            )
            write_json(config_path, existing)
    else:
        created = now_utc()
        config = {
            "schema_version": SCHEMA_VERSION,
            "workspace_mode": mode,
            "workspace_name": args.name,
            "workspace_language": args.workspace_language,
            "artifact_language": args.language,
            "default_citation_style": args.citation_style,
            "task_root_layout": "named_subdirectory" if mode == "single_task" else None,
            "created_at": created,
            "updated_at": created,
            "credential_storage": "prohibited",
            "cloud_sync_acknowledgement": {"provider": provider, "acknowledged_at": created, "basis": "explicit_user_confirmation"} if provider else None,
            "security_defaults": {
                "max_files_per_sync": 500,
                "max_file_bytes": 536870912,
                "max_total_bytes": 2147483648,
                "macro_enabled_office_files": "prohibited_without_manual_review",
                "automatic_archive_extraction": "prohibited",
                "retention_policy": "user_managed_no_automatic_deletion",
                "default_share_scope": "result_directory_only",
                "licensed_material_external_sharing": "prohibited_without_authorization",
            },
        }
        write_json(config_path, config)
    if mode == "single_task":
        task_id = slugify(args.task_id or args.task_name, fallback="task")
        task_root = workspace / slugify(args.task_name, fallback=task_id)
        if (task_root / "task_config.json").exists():
            raise SystemExit(f"Task already exists: {task_root}")
        for folder in TASK_FOLDERS:
            (task_root / folder).mkdir(parents=True, exist_ok=True)
        for folder in ("incoming", "verified", "rejected"):
            (task_root / "01_sources" / folder).mkdir(exist_ok=True)
        created = now_utc()
        write_json(
            task_root / "task_config.json",
            {
                "schema_version": SCHEMA_VERSION,
                "task_id": task_id,
                "task_name": args.task_name,
                "artifact_language": args.language,
                "citation_style": args.citation_style,
                "source_scope": None,
                "external_access": "none",
                "slide_citation_policy": "prohibited",
                "slide_permission_scope": None,
                "slide_permission_basis": None,
                "delivery_formats": [],
                "plan_approved": False,
                "workflow_status": "initialized",
                "created_at": created,
                "updated_at": created,
            },
        )
        summary = task_root / "task_summary.md"
        if not summary.exists():
            write_text(summary, "# Task summary\n\nStatus: initialized\n")
        print_result(task_root / "task_config.json")
    else:
        for folder in ("courses", "_incoming"):
            (workspace / folder).mkdir(exist_ok=True)
        catalog = workspace / "course_catalog.json"
        if not catalog.exists():
            write_json(catalog, {"schema_version": SCHEMA_VERSION, "generated_at": now_utc(), "course_count": 0, "courses": []})
        print_result(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
