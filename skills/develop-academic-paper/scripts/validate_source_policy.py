#!/usr/bin/env python3
"""Normalize and validate a source registry with default-prohibited slide citations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import SCHEMA_VERSION, is_slide_material, no_credentials, now_utc, read_records, redact_url, resolve_explicit, slide_policy_config, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("registry", help="Source registry JSON/CSV")
    value.add_argument("--normalized-output", help="Optional normalized JSON output")
    value.add_argument("--report", help="Optional policy audit JSON output")
    value.add_argument("--policy-config", help="Task or assignment config containing any confirmed slide permission")
    return value


def is_slide(source: dict[str, Any], base: Path) -> bool:
    type_hint = str(source.get("original_material_type") or source.get("material_type") or source.get("type") or "")
    name = str(source.get("local_path") or source.get("name") or source.get("title") or "source")
    return is_slide_material(base / name, type_hint)[0]


def missing_slide_metadata(source: dict[str, Any]) -> list[str]:
    checks = {
        "title": source.get("title") or source.get("name"),
        "author": source.get("author") or source.get("authors") or source.get("instructor"),
        "issued": source.get("issued") or source.get("date") or source.get("year"),
        "course_or_container": source.get("course_name") or source.get("course") or source.get("container-title") or source.get("container_title"),
    }
    return [field for field, value in checks.items() if value in (None, "", [])]


def main() -> int:
    args = parser().parse_args()
    registry_path = resolve_explicit(args.registry)
    sources = read_records(registry_path)
    no_credentials(sources)
    config_path = resolve_explicit(args.policy_config) if args.policy_config else None
    try:
        slide_policy, slide_basis, slide_scope = slide_policy_config(config_path)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    normalized = []
    issues = []
    for index, source in enumerate(sources, start=1):
        item = dict(source)
        source_id = str(item.get("source_id") or item.get("id") or f"source-{index:03d}")
        item["id"] = source_id
        for url_field in ("URL", "url", "clean_url", "stable_url", "record_url"):
            if item.get(url_field):
                item[url_field] = redact_url(str(item[url_field]))
        if is_slide(item, registry_path.parent):
            declared_role = str(item.get("source_role") or "")
            declared_eligibility = str(item.get("citation_eligibility") or "").lower()
            if slide_policy == "allowed_by_user_confirmation":
                missing = missing_slide_metadata(item)
                verified = str(item.get("verification_status") or "").lower() == "verified"
                item.update(
                    {
                        "source_role": "evidence",
                        "citation_eligibility": "requires_verification",
                        "slide_permission_status": "confirmed",
                        "slide_permission_scope": slide_scope,
                        "slide_permission_basis": slide_basis,
                        "policy_reason": "Task/course slide citation permission is recorded; bibliographic identity must be verified.",
                    }
                )
                if declared_eligibility == "allowed":
                    if missing or not verified:
                        issues.append(
                            {
                                "source_id": source_id,
                                "severity": "error",
                                "code": "slide_permission_incomplete",
                                "message": "An allowed slide requires verified status and complete title, author, date, and course/container metadata.",
                                "missing_fields": missing,
                            }
                        )
                    else:
                        item["citation_eligibility"] = "allowed"
                if str(item.get("citation_status") or "").lower() in {"cited", "used", "included"} and item["citation_eligibility"] != "allowed":
                    issues.append(
                        {
                            "source_id": source_id,
                            "severity": "error",
                            "code": "unverified_slide_cited",
                            "message": "A permitted slide is marked as cited before its bibliographic identity is verified.",
                        }
                    )
            elif declared_role not in {"", "context_only"} or declared_eligibility not in {"", "prohibited"}:
                issues.append(
                    {
                        "source_id": source_id,
                        "severity": "error",
                        "code": "slide_policy_conflict",
                        "message": "Slides are citation-prohibited by default; no valid task/course permission was supplied.",
                    }
                )
            if slide_policy == "prohibited":
                item.update(
                    {
                        "source_role": "context_only",
                        "citation_eligibility": "prohibited",
                        "slide_permission_status": "not_confirmed",
                        "policy_reason": "Course slide decks are non-citable by default.",
                    }
                )
            if slide_policy == "prohibited" and str(item.get("citation_status") or "").lower() in {"cited", "used", "included"}:
                issues.append(
                    {
                        "source_id": source_id,
                        "severity": "error",
                        "code": "prohibited_slide_cited",
                        "message": "A slide deck is marked as cited.",
                    }
                )
        else:
            item.setdefault("source_role", "unclassified")
            item.setdefault("citation_eligibility", "requires_verification")
        normalized.append(item)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "source_count": len(normalized),
        "error_count": sum(issue["severity"] == "error" for issue in issues),
        "issues": issues,
    }
    if args.normalized_output:
        write_json(resolve_explicit(args.normalized_output), {"schema_version": SCHEMA_VERSION, "sources": normalized})
    report_path = resolve_explicit(args.report) if args.report else registry_path.with_name("source_policy_report.json")
    write_json(report_path, report)
    print(report_path.as_posix())
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
