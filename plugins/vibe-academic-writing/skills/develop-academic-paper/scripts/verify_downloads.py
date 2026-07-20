#!/usr/bin/env python3
"""Verify newly downloaded local files and reconcile them with an optional remote inventory."""

from __future__ import annotations

import argparse
from collections import Counter

from _common import SCHEMA_VERSION, inventory_file, material_policy, now_utc, read_records, resolve_explicit, workspace_relative, write_json, write_text


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("download_directory", help="Explicit local download directory")
    value.add_argument("output_directory", help="Directory for verification outputs")
    value.add_argument("--expected", help="Optional normalized remote inventory JSON/CSV")
    value.add_argument("--workspace-root", help="Workspace root used to persist relative paths")
    value.add_argument("--max-files", type=int, default=500)
    value.add_argument("--max-file-bytes", type=int, default=512 * 1024 * 1024)
    value.add_argument("--max-total-bytes", type=int, default=2 * 1024 * 1024 * 1024)
    return value


def write_missing(path, rows) -> None:
    generated = now_utc()
    lines = ["# Missing or invalid downloads", "", f"Generated: {generated}", ""]
    unresolved = [row for row in rows if row["status"] not in {"verified", "metadata_only", "excluded_video"}]
    if not unresolved:
        lines.append("All expected downloadable materials were verified.")
    else:
        lines.extend(
            [
                "| Name | Dashboard path | Type | Status | Reason | Last checked | Remote location | Suggested action |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in unresolved:
            values = [
                row.get("name") or "(unnamed material)",
                row.get("dashboard_path") or "(not recorded)",
                row.get("material_type") or "unknown",
                f"`{row['status']}`",
                row.get("reason") or "(not recorded)",
                generated,
                row.get("url") or "(not recorded)",
                "Retry when available, verify access, or provide the file manually.",
            ]
            escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
            lines.append("| " + " | ".join(escaped) + " |")
    write_text(path, "\n".join(lines).rstrip() + "\n")


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.download_directory)
    output = resolve_explicit(args.output_directory)
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    output.mkdir(parents=True, exist_ok=True)
    workspace = resolve_explicit(args.workspace_root) if args.workspace_root else root
    generated_names = {"local_inventory.json", "verification_report.json", "missing_materials.md", "missing_materials.json"}
    candidate_paths = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if output != root and output in path.parents:
            continue
        if path.parent == output and path.name in generated_names:
            continue
        candidate_paths.append(path)
    total_bytes = sum(path.stat().st_size for path in candidate_paths)
    limit_issues = []
    if len(candidate_paths) > args.max_files:
        limit_issues.append({"code": "DOWNLOAD_LIMIT_EXCEEDED", "message": f"File count {len(candidate_paths)} exceeds limit {args.max_files}."})
    oversized = [path.relative_to(root).as_posix() for path in candidate_paths if path.stat().st_size > args.max_file_bytes]
    if oversized:
        limit_issues.append({"code": "DOWNLOAD_LIMIT_EXCEEDED", "message": f"{len(oversized)} file(s) exceed the per-file size limit.", "paths": oversized})
    if total_bytes > args.max_total_bytes:
        limit_issues.append({"code": "DOWNLOAD_LIMIT_EXCEEDED", "message": f"Total size {total_bytes} exceeds limit {args.max_total_bytes}."})
    if limit_issues:
        blocked_report = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now_utc(),
            "download_directory": workspace_relative(root, workspace),
            "status": "blocked",
            "file_count": len(candidate_paths),
            "total_bytes": total_bytes,
            "issues": limit_issues,
            "results": [],
        }
        report_path = output / "verification_report.json"
        write_json(report_path, blocked_report)
        print(report_path.as_posix())
        return 2
    local = [inventory_file(path, root) for path in candidate_paths]
    local_document = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "root": workspace_relative(root, workspace),
        "item_count": len(local),
        "materials": local,
    }
    write_json(output / "local_inventory.json", local_document)
    rows = []
    if args.expected:
        expected = read_records(resolve_explicit(args.expected))
        local_by_name = {str(item["name"]).casefold(): item for item in local}
        for remote in expected:
            name = str(remote.get("name") or "")
            material_type = str(remote.get("material_type") or remote.get("type") or "unknown")
            remote_url = str(remote.get("clean_url") or remote.get("url") or "")
            availability = str(remote.get("availability") or "available").lower()
            eligible = remote.get("download_eligible") is not False
            record_role = str(remote.get("record_role") or "downloadable_file")
            if record_role == "excluded_video":
                rows.append({"name": name, "status": "excluded_video", "dashboard_path": remote.get("dashboard_path") or "", "local_path": "", "material_type": material_type, "url": remote_url, "reason": "Video is excluded from download scope"})
                continue
            if record_role == "metadata_only":
                rows.append({"name": name, "status": "metadata_only", "dashboard_path": remote.get("dashboard_path") or "", "local_path": "", "material_type": material_type, "url": remote_url, "reason": "LMS-native activity retained as metadata only"})
                continue
            if availability in {"locked", "hidden", "unavailable", "permission_denied"} or not eligible:
                rows.append(
                    {
                        "name": name,
                        "status": "locked",
                        "dashboard_path": remote.get("dashboard_path") or "",
                        "local_path": "",
                        "material_type": material_type,
                        "url": remote_url,
                        "reason": f"Remote availability is {availability}",
                    }
                )
                continue
            item = local_by_name.get(name.casefold())
            if item is None:
                rows.append(
                    {
                        "name": name,
                        "status": "local_missing",
                        "dashboard_path": remote.get("dashboard_path") or "",
                        "local_path": "",
                        "material_type": material_type,
                        "url": remote_url,
                        "reason": "Expected download was not found",
                    }
                )
            else:
                status = item["integrity_status"]
                policy = material_policy(
                    root / name,
                    str(remote.get("original_material_type") or remote.get("material_type") or remote.get("type") or ""),
                )
                if status == "verified" and remote.get("size_bytes") not in (None, "") and int(remote["size_bytes"]) != int(item["size_bytes"]):
                    status = "local_corrupt"
                    reason = "Downloaded size differs from remote inventory"
                elif status == "verified" and remote.get("sha256") and str(remote["sha256"]).lower() != item["sha256"]:
                    status = "local_corrupt"
                    reason = "Downloaded SHA-256 differs from remote inventory"
                else:
                    reason = item["integrity_reason"]
                rows.append(
                    {
                        "name": name,
                        "status": status,
                        "dashboard_path": remote.get("dashboard_path") or "",
                        "local_path": item["local_path"],
                        "url": remote_url,
                        "reason": reason,
                        "sha256": item["sha256"],
                        "source_role": policy["source_role"],
                        "citation_eligibility": policy["citation_eligibility"],
                        "material_type": policy["material_type"],
                    }
                )
    else:
        rows = [
            {
                "name": item["name"],
                "status": item["integrity_status"],
                "dashboard_path": "",
                "local_path": item["local_path"],
                "reason": item["integrity_reason"],
                "sha256": item["sha256"],
                "source_role": item["source_role"],
                "citation_eligibility": item["citation_eligibility"],
            }
            for item in local
        ]
    counts = Counter(row["status"] for row in rows)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "download_directory": workspace_relative(root, workspace),
        "status_counts": dict(sorted(counts.items())),
        "results": rows,
    }
    report_path = output / "verification_report.json"
    write_json(report_path, report)
    missing_rows = [row for row in rows if row["status"] not in {"verified", "metadata_only", "excluded_video"}]
    write_missing(output / "missing_materials.md", rows)
    write_json(
        output / "missing_materials.json",
        {"schema_version": SCHEMA_VERSION, "generated_at": now_utc(), "missing_count": len(missing_rows), "materials": missing_rows},
    )
    print(report_path.as_posix())
    return 1 if missing_rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
