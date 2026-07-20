#!/usr/bin/env python3
"""Audit a citation ledger and optional draft against the source registry."""

from __future__ import annotations

import argparse
import re

from _common import SCHEMA_VERSION, is_slide_material, now_utc, read_records, resolve_explicit, slide_policy_config, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("registry", help="Source registry JSON/CSV")
    value.add_argument("ledger", help="Citation ledger JSON/CSV containing source_id")
    value.add_argument("--draft", help="Optional Markdown/text draft")
    value.add_argument("--report", help="Optional audit report JSON")
    value.add_argument("--policy-config", help="Task or assignment config containing any confirmed slide permission")
    return value


def main() -> int:
    args = parser().parse_args()
    registry_path = resolve_explicit(args.registry)
    ledger_path = resolve_explicit(args.ledger)
    sources = read_records(registry_path)
    ledger = read_records(ledger_path)
    policy_path = resolve_explicit(args.policy_config) if args.policy_config else None
    try:
        slide_policy, slide_basis, _ = slide_policy_config(policy_path)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    source_map = {str(item.get("source_id") or item.get("id") or ""): item for item in sources}
    issues = []
    cited_ids: set[str] = set()
    for index, citation in enumerate(ledger, start=1):
        source_id = str(citation.get("source_id") or citation.get("id") or "").strip()
        if not source_id:
            issues.append({"severity": "error", "code": "ledger_missing_source_id", "location": index, "message": "Citation ledger row has no source_id."})
            continue
        cited_ids.add(source_id)
        source = source_map.get(source_id)
        if source is None:
            issues.append({"severity": "error", "code": "unknown_source", "source_id": source_id, "location": index, "message": "Citation references a source absent from the registry."})
            continue
        source_name = str(source.get("local_path") or source.get("name") or source.get("title") or source_id)
        source_type = str(source.get("original_material_type") or source.get("material_type") or source.get("type") or "")
        is_slide = is_slide_material(registry_path.parent / source_name, source_type)[0]
        eligibility = str(source.get("citation_eligibility") or "requires_verification").lower()
        if is_slide:
            slide_allowed = (
                slide_policy == "allowed_by_user_confirmation"
                and bool(slide_basis)
                and str(source.get("slide_permission_status") or "").lower() == "confirmed"
                and str(source.get("verification_status") or "").lower() == "verified"
                and eligibility == "allowed"
            )
            eligibility = "allowed" if slide_allowed else "prohibited"
        if eligibility != "allowed":
            issues.append(
                {
                    "severity": "error",
                    "code": "source_not_citable",
                    "source_id": source_id,
                    "location": index,
                    "message": f"Citation eligibility is {eligibility!r}, not 'allowed'.",
                }
            )
    if args.draft:
        draft_path = resolve_explicit(args.draft)
        draft = draft_path.read_text(encoding="utf-8")
        for source_id, source in source_map.items():
            if not source_id:
                continue
            if re.search(rf"(?<![\w-])@?{re.escape(source_id)}(?![\w-])", draft) and source_id not in cited_ids:
                severity = "error" if str(source.get("citation_eligibility") or "").lower() == "prohibited" else "warning"
                issues.append(
                    {
                        "severity": severity,
                        "code": "draft_citation_missing_from_ledger",
                        "source_id": source_id,
                        "message": "Draft mentions this source identifier but the citation ledger does not.",
                    }
                )
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "registry_source_count": len(sources),
        "ledger_entry_count": len(ledger),
        "error_count": sum(issue["severity"] == "error" for issue in issues),
        "warning_count": sum(issue["severity"] == "warning" for issue in issues),
        "issues": issues,
    }
    report_path = resolve_explicit(args.report) if args.report else ledger_path.with_name("citation_audit.json")
    write_json(report_path, report)
    print(report_path.as_posix())
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
