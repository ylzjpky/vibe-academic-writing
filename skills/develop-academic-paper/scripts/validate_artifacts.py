#!/usr/bin/env python3
"""Validate deterministic workspace, course, or assignment artifact contracts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import SCHEMA_VERSION, no_credentials, now_utc, read_json, resolve_explicit, write_json


TASK_DIRS = ("00_brief", "01_sources", "02_source_registry", "03_evidence", "04_content_plan", "05_draft", "06_review", "07_final_internal")
COURSE_DIRS = ("courses", "_incoming")
COURSE_DETAIL_DIRS = ("01_course_materials", "02_course_library", "03_assignments", "04_course_memory", "05_sync", "90_missing_materials")
ASSIGNMENT_DIRS = ("00_brief", "01_course_context", "02_external_sources", "03_source_registry", "04_evidence", "05_content_plan", "06_draft", "07_review", "08_final_internal")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("root", help="Explicit artifact root to validate")
    value.add_argument("--kind", choices=("auto", "task", "course", "assignment"), default="auto")
    value.add_argument("--stage", choices=("initialized", "planned", "drafted", "final"), default="initialized")
    value.add_argument("--report", help="Optional validation report JSON")
    return value


def nonempty_artifact(directory: Path) -> bool:
    return directory.is_dir() and any(path.is_file() and path.stat().st_size > 0 for path in directory.rglob("*"))


def detect_kind(root: Path) -> str:
    if (root / "assignment_config.json").is_file():
        return "assignment"
    if (root / "task_config.json").is_file():
        return "task"
    config = root / "workspace_config.json"
    if config.is_file():
        mode = str(read_json(config).get("workspace_mode") or "")
        if mode in {"single_task", "task"}:
            return "task"
        if mode == "course":
            return "course"
    raise ValueError("Could not infer artifact kind; pass --kind")


def require_path(path: Path, kind: str, issues: list[dict[str, Any]]) -> None:
    if not path.exists():
        issues.append({"severity": "error", "code": "missing_artifact", "path": path.as_posix(), "message": f"Required {kind} is missing."})


def validate_json(path: Path, issues: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        data = read_json(path)
        no_credentials(data)
        return data
    except Exception as exc:
        issues.append({"severity": "error", "code": "invalid_json", "path": path.as_posix(), "message": str(exc)})
        return {}


def validate_stage(root: Path, kind: str, stage: str, issues: list[dict[str, Any]]) -> None:
    if stage == "initialized" or kind == "course":
        return
    task_final = "07_final_internal" if (root / "07_final_internal").exists() else "07_final"
    assignment_final = "08_final_internal" if (root / "08_final_internal").exists() else "08_final"
    folders = {
        "task": {"planned": "04_content_plan", "drafted": "05_draft", "final": task_final},
        "assignment": {"planned": "05_content_plan", "drafted": "06_draft", "final": assignment_final},
    }
    ordered = ["planned", "drafted", "final"]
    current_index = ordered.index(stage)
    for required_stage in ordered[: current_index + 1]:
        directory = root / folders[kind][required_stage]
        if not nonempty_artifact(directory):
            issues.append(
                {
                    "severity": "error",
                    "code": "stage_artifact_empty",
                    "path": directory.as_posix(),
                    "message": f"Stage {required_stage} requires at least one non-empty file.",
                }
            )
    if stage == "final":
        config_name = "task_config.json" if kind == "task" else "assignment_config.json"
        config = validate_json(root / config_name, issues)
        formats = config.get("delivery_formats") if isinstance(config.get("delivery_formats"), list) else []
        result_path = str(config.get("result_directory") or "")
        if not formats or not result_path:
            severity = "warning" if str(config.get("schema_version") or "") == "1.0" else "error"
            issues.append({"severity": severity, "code": "legacy_delivery_untracked" if severity == "warning" else "delivery_not_configured", "path": (root / config_name).as_posix(), "message": "Final validation requires confirmed delivery_formats and result_directory; schema v1.0 artifacts may use the legacy final directory."})
        else:
            result_root = root / result_path
            require_path(result_root, "directory", issues)
            extensions = {"word": ".docx", "pdf": ".pdf"}
            for output_format in formats:
                suffix = extensions.get(str(output_format))
                if suffix and not any(path.is_file() and path.suffix.lower() == suffix and path.stat().st_size > 0 for path in result_root.glob("*")):
                    issues.append({"severity": "error", "code": "missing_delivery_format", "path": result_root.as_posix(), "message": f"No non-empty {suffix} deliverable was found."})
        sensitive_report_path = root / "sensitive_artifact_scan.json"
        require_path(sensitive_report_path, "file", issues)
        if sensitive_report_path.exists():
            sensitive_report = validate_json(sensitive_report_path, issues)
            if sensitive_report.get("safe") is not True:
                issues.append({"severity": "error", "code": "sensitive_artifact_scan_failed", "path": sensitive_report_path.as_posix(), "message": "Final delivery requires a passing sensitive-artifact scan."})


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.root)
    issues: list[dict[str, Any]] = []
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    try:
        kind = detect_kind(root) if args.kind == "auto" else args.kind
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if kind == "course":
        config_path = root / "workspace_config.json"
        require_path(config_path, "file", issues)
        if config_path.exists():
            config = validate_json(config_path, issues)
            expected_modes = {"single_task", "task"} if kind == "task" else {"course"}
            if config.get("workspace_mode") not in expected_modes:
                issues.append({"severity": "error", "code": "mode_mismatch", "path": config_path.as_posix(), "message": f"workspace_mode must be one of {sorted(expected_modes)!r}."})
    if kind == "task":
        config_path = root / "task_config.json"
        require_path(config_path, "file", issues)
        config = validate_json(config_path, issues) if config_path.exists() else {}
        if config.get("source_scope") not in {None, "user_materials_only", "external_only", "mixed"}:
            issues.append({"severity": "error", "code": "invalid_source_scope", "path": config_path.as_posix(), "message": "Single-task source_scope is invalid."})
        if config.get("external_access") not in {None, "institutional_library", "public_sources", "both", "none"}:
            issues.append({"severity": "error", "code": "invalid_external_access", "path": config_path.as_posix(), "message": "external_access is invalid."})
        slide_policy = config.get("slide_citation_policy") or config.get("ppt_citation_policy")
        if slide_policy not in {"prohibited", "allowed_by_user_confirmation"}:
            issues.append({"severity": "error", "code": "slide_policy_missing", "path": config_path.as_posix(), "message": "slide_citation_policy is invalid."})
        if slide_policy == "allowed_by_user_confirmation" and (not config.get("slide_permission_basis") or config.get("slide_permission_scope") not in {"current_task", "course"}):
            issues.append({"severity": "error", "code": "slide_permission_incomplete", "path": config_path.as_posix(), "message": "Allowed slide citation requires a basis and task/course scope."})
        require_path(root / "task_summary.md", "file", issues)
        for folder in TASK_DIRS:
            if folder == "07_final_internal" and (root / "07_final").is_dir():
                continue
            require_path(root / folder, "directory", issues)
    elif kind == "course":
        for folder in COURSE_DIRS:
            require_path(root / folder, "directory", issues)
        catalog_path = root / "course_catalog.json"
        require_path(catalog_path, "file", issues)
        catalog = validate_json(catalog_path, issues) if catalog_path.exists() else {}
        courses = catalog.get("courses") if isinstance(catalog.get("courses"), list) else []
        if catalog.get("course_count") not in (None, len(courses)):
            issues.append({"severity": "error", "code": "course_count_mismatch", "path": catalog_path.as_posix(), "message": "course_count does not match courses length."})
        for course in courses:
            course_root = root / "courses" / str(course.get("folder_name") or "")
            require_path(course_root / "course_manifest.json", "file", issues)
            for folder in COURSE_DETAIL_DIRS:
                require_path(course_root / folder, "directory", issues)
    else:
        config_path = root / "assignment_config.json"
        require_path(config_path, "file", issues)
        config = validate_json(config_path, issues) if config_path.exists() else {}
        slide_policy = config.get("slide_citation_policy") or config.get("ppt_citation_policy")
        if slide_policy not in {"prohibited", "allowed_by_user_confirmation"}:
            issues.append({"severity": "error", "code": "slide_policy_missing", "path": config_path.as_posix(), "message": "slide_citation_policy is invalid."})
        if slide_policy == "allowed_by_user_confirmation" and (not config.get("slide_permission_basis") or config.get("slide_permission_scope") not in {"current_task", "course"}):
            issues.append({"severity": "error", "code": "slide_permission_incomplete", "path": config_path.as_posix(), "message": "Allowed slide citation requires a basis and task/course scope."})
        if config.get("source_scope") not in {"course_only", "external_only", "mixed"}:
            issues.append({"severity": "error", "code": "invalid_source_scope", "path": config_path.as_posix(), "message": "source_scope is invalid."})
        if config.get("external_access") not in {None, "institutional_library", "public_sources", "both", "none"}:
            issues.append({"severity": "error", "code": "invalid_external_access", "path": config_path.as_posix(), "message": "external_access is invalid."})
        for folder in ASSIGNMENT_DIRS:
            if folder == "08_final_internal" and (root / "08_final").is_dir():
                continue
            require_path(root / folder, "directory", issues)
        require_path(root / "task_summary.md", "file", issues)
    validate_stage(root, kind, args.stage, issues)
    for json_path in root.rglob("*.json"):
        if args.report and json_path == resolve_explicit(args.report):
            continue
        try:
            no_credentials(read_json(json_path))
        except Exception as exc:
            issues.append({"severity": "error", "code": "unsafe_or_invalid_json", "path": json_path.as_posix(), "message": str(exc)})
    for issue in issues:
        raw_path = issue.get("path")
        if not raw_path:
            continue
        try:
            issue["path"] = resolve_explicit(str(raw_path)).relative_to(root).as_posix()
        except ValueError:
            issue["path"] = Path(str(raw_path)).name
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "root": ".",
        "kind": kind,
        "stage": args.stage,
        "valid": not any(issue["severity"] == "error" for issue in issues),
        "error_count": sum(issue["severity"] == "error" for issue in issues),
        "issues": issues,
    }
    report_path = resolve_explicit(args.report) if args.report else root / "artifact_validation.json"
    write_json(report_path, report)
    print(report_path.as_posix())
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
