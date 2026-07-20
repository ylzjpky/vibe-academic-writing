#!/usr/bin/env python3
"""Initialize a course assignment with a machine-readable source policy."""

from __future__ import annotations

import argparse
import csv

from _common import SCHEMA_VERSION, now_utc, resolve_explicit, slugify, write_json, write_text


ASSIGNMENT_FOLDERS = (
    "00_brief",
    "01_course_context",
    "02_external_sources",
    "03_source_registry",
    "04_evidence",
    "05_content_plan",
    "06_draft",
    "07_review",
    "08_final_internal",
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("course_directory", help="Explicit local course directory")
    value.add_argument("--name", required=True, help="Assignment name")
    value.add_argument("--assignment-id", help="Stable assignment identifier")
    value.add_argument("--source-scope", choices=("course_only", "external_only", "mixed"), required=True)
    value.add_argument("--external-access", choices=("institutional_library", "public_sources", "both", "none"), default="none")
    value.add_argument("--slide-policy", choices=("prohibited", "allowed_by_user_confirmation"), default="prohibited")
    value.add_argument("--slide-permission-scope", choices=("current_task", "course"))
    value.add_argument("--slide-permission-basis", default="")
    value.add_argument("--citation-style", default="APA-7")
    value.add_argument("--language", default="English")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.slide_policy == "allowed_by_user_confirmation" and (
        not args.slide_permission_basis.strip() or not args.slide_permission_scope
    ):
        raise SystemExit("Allowed slide citation requires --slide-permission-scope and --slide-permission-basis")
    if args.source_scope == "course_only" and args.external_access != "none":
        raise SystemExit("course_only assignments must use --external-access none")
    course = resolve_explicit(args.course_directory)
    if not (course / "course_manifest.json").is_file():
        raise SystemExit("Target must be an initialized course directory containing course_manifest.json")
    memory_root = course / "04_course_memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    memory_file = memory_root / "course_memory.md"
    task_index = memory_root / "task_index.csv"
    if not memory_file.exists():
        write_text(memory_file, "# Course memory\n\n")
    if not task_index.exists():
        write_text(task_index, "assignment_id,title,status,source_scope,updated_at,assignment_path\n")
    assignment_id = slugify(args.assignment_id or args.name, fallback="assignment")
    root = course / "03_assignments" / assignment_id
    if (root / "assignment_config.json").exists():
        raise SystemExit(f"Assignment already exists: {root}")
    for folder in ASSIGNMENT_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    config = {
        "schema_version": SCHEMA_VERSION,
        "assignment_id": assignment_id,
        "assignment_name": args.name,
        "course_id": "",
        "course_name": course.name,
        "source_scope": args.source_scope,
        "external_access": args.external_access,
        "citation_style": args.citation_style,
        "language": args.language,
        "course_sync_checked": False,
        "slide_citation_policy": args.slide_policy,
        "slide_permission_scope": args.slide_permission_scope,
        "slide_permission_basis": args.slide_permission_basis.strip() or None,
        "delivery_formats": [],
        "plan_approved": False,
        "created_at": now_utc(),
        "updated_at": now_utc(),
    }
    manifest = course / "course_manifest.json"
    if manifest.exists():
        from _common import read_json

        course_data = read_json(manifest)
        config["course_id"] = course_data.get("course_id", "")
        config["course_name"] = course_data.get("course_name", course.name)
    write_json(root / "assignment_config.json", config)
    write_text(root / "task_summary.md", "# Task summary\n\nStatus: initialized\n")
    with task_index.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([assignment_id, args.name, "initialized", args.source_scope, config["updated_at"], root.relative_to(course).as_posix()])
    print(root.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
