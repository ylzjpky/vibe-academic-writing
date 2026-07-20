#!/usr/bin/env python3
"""Compare normalized remote and local inventories and emit sync state plus missing report."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import PurePosixPath
from typing import Any

from _common import SCHEMA_VERSION, now_utc, read_records, resolve_explicit, workspace_relative, write_csv, write_json, write_text


STATUSES = {
    "verified_match",
    "unchanged",
    "new",
    "updated",
    "renamed",
    "local_missing",
    "local_corrupt",
    "locked",
    "download_failed",
    "remote_removed",
    "excluded_video",
    "metadata_only",
    "unresolved_identity",
    "content_change_unknown",
    "unsafe_file",
    "review_required",
}
MISSING_STATUSES = {"new", "updated", "local_missing", "local_corrupt", "locked", "download_failed", "unresolved_identity", "content_change_unknown", "unsafe_file", "review_required"}
VALID_ACTIONS = {
    "downloaded_new",
    "downloaded_update",
    "redownloaded_missing",
    "redownloaded_corrupt",
    "skipped_existing",
    "metadata_updated",
    "retained_local",
    "attempted_failed",
    "pending_download",
    "none",
}
CSV_FIELDS = [
    "comparison_status",
    "operation_action",
    "download_attempted",
    "remote_item_id",
    "name",
    "local_name",
    "dashboard_path",
    "module_path",
    "url",
    "reason",
    "material_type",
    "local_path",
    "local_integrity_status",
]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("remote_inventory", help="Normalized remote inventory JSON/CSV")
    value.add_argument("local_inventory", help="Local inventory JSON/CSV")
    value.add_argument("output_directory", help="Directory for sync_state.json and sync_results.csv")
    value.add_argument("--missing-report", help="Optional explicit missing_materials.md path")
    value.add_argument("--previous-remote", help="Optional previous remote inventory for resync provenance")
    value.add_argument("--actions", help="Optional JSON/CSV recording actions taken in this run")
    value.add_argument("--operation", choices=("first_sync", "resync", "deep_resync"), default="resync")
    value.add_argument("--workspace-root", help="Workspace root used to persist relative artifact paths")
    return value


def normalized_name(value: Any) -> str:
    return PurePosixPath(str(value or "").replace("\\", "/")).name.casefold()


def pick_match(remote: dict[str, Any], local: list[dict[str, Any]], used: set[int]) -> int | None:
    remote_id = str(remote.get("remote_item_id") or remote.get("remote_id") or "")
    url = str(remote.get("clean_url") or remote.get("url") or "")
    path = str(remote.get("dashboard_path") or "")
    name = normalized_name(remote.get("name"))
    criteria = (
        lambda item: remote_id and str(item.get("remote_item_id") or item.get("remote_id") or "") == remote_id,
        lambda item: url and str(item.get("clean_url") or item.get("url") or "") == url,
        lambda item: path and name and str(item.get("dashboard_path") or "") == path and normalized_name(item.get("name")) == name,
        lambda item: name and normalized_name(item.get("name")) == name,
    )
    for criterion in criteria:
        candidates = [index for index, item in enumerate(local) if index not in used and criterion(item)]
        if len(candidates) == 1:
            return candidates[0]
    return None


def compare_one(remote: dict[str, Any], local: dict[str, Any] | None) -> tuple[str, str]:
    record_role = str(remote.get("record_role") or "").lower()
    if record_role == "excluded_video" or str(remote.get("exclusion_status") or "").lower() == "excluded_video" or "video" in str(remote.get("material_type") or "").lower():
        return "excluded_video", "Video is outside the synchronization download scope"
    if record_role == "metadata_only":
        unresolved = str(remote.get("unresolved_status") or "").lower()
        if unresolved:
            return "unresolved_identity", f"Metadata-only activity is unresolved: {unresolved}"
        return "metadata_only", "LMS-native activity is retained as metadata only"
    availability = str(remote.get("availability") or "available").lower()
    if availability in {"locked", "hidden", "unavailable", "permission_denied"} or remote.get("download_eligible") is False:
        return "locked", f"Remote availability is {availability}"
    if local is None:
        if remote.get("local_path") or remote.get("previous_local_path"):
            return "local_missing", "Expected local file was not found"
        return "new", "Remote item has no local match"
    integrity = str(local.get("integrity_status") or local.get("status") or "verified").lower()
    if integrity in {"local_missing", "missing"}:
        return "local_missing", str(local.get("integrity_reason") or "Local file is missing")
    if integrity in {"local_corrupt", "corrupt", "invalid"}:
        return "local_corrupt", str(local.get("integrity_reason") or "Local file failed integrity validation")
    if integrity == "unsafe_macro":
        return "unsafe_file", str(local.get("integrity_reason") or "Macro-enabled file requires manual review")
    if integrity == "archive_requires_review":
        return "review_required", str(local.get("integrity_reason") or "Archive requires manual review")
    remote_hash = str(remote.get("sha256") or "").lower()
    local_hash = str(local.get("sha256") or "").lower()
    if remote_hash and local_hash and remote_hash != local_hash:
        return "updated", "Remote and local SHA-256 values differ"
    remote_size = remote.get("size_bytes")
    local_size = local.get("size_bytes")
    if remote_size not in (None, "") and local_size not in (None, "") and int(remote_size) != int(local_size):
        return "updated", "Remote and local sizes differ"
    remote_modified = str(remote.get("modified_at") or "")
    local_modified = str(local.get("remote_modified_at") or "")
    if remote_modified and local_modified and remote_modified != local_modified:
        return "updated", "Remote modification timestamp changed"
    if normalized_name(remote.get("name")) != normalized_name(local.get("name")):
        return "renamed", "Stable identity matched but file name changed"
    if str(remote.get("content_change_signal") or "").lower() in {"unknown", "unavailable", "insufficient"}:
        return "content_change_unknown", "The LMS exposes insufficient metadata to prove that content is unchanged"
    return "unchanged", "Remote item matches verified local file"


def default_action(status: str) -> str:
    if status == "unchanged":
        return "skipped_existing"
    if status == "renamed":
        return "metadata_updated"
    if status == "remote_removed":
        return "retained_local"
    if status == "download_failed":
        return "attempted_failed"
    if status in {"new", "updated", "local_missing", "local_corrupt"}:
        return "pending_download"
    return "none"


def action_key(item: dict[str, Any]) -> str:
    return str(item.get("remote_item_id") or item.get("remote_id") or item.get("name") or "")


def result_row(
    status: str,
    remote: dict[str, Any],
    local: dict[str, Any] | None,
    reason: str,
    action: dict[str, Any] | None = None,
) -> dict[str, Any]:
    operation_action = str((action or {}).get("operation_action") or default_action(status))
    if operation_action not in VALID_ACTIONS:
        raise ValueError(f"Unsupported operation_action: {operation_action}")
    download_attempted = bool((action or {}).get("download_attempted")) or operation_action in {
        "downloaded_new", "downloaded_update", "redownloaded_missing", "redownloaded_corrupt", "attempted_failed"
    }
    comparison_status = "verified_match" if operation_action in {"downloaded_new", "downloaded_update", "redownloaded_missing", "redownloaded_corrupt"} and status == "unchanged" else status
    return {
        "status": comparison_status,
        "comparison_status": comparison_status,
        "operation_action": operation_action,
        "download_attempted": download_attempted,
        "remote_item_id": remote.get("remote_item_id") or remote.get("remote_id") or "",
        "name": remote.get("name") or "",
        "local_name": (local or {}).get("name") or "",
        "dashboard_path": remote.get("dashboard_path") or "",
        "module_path": remote.get("module_path") or "",
        "url": remote.get("clean_url") or remote.get("url") or "",
        "reason": reason,
        "material_type": remote.get("material_type") or "unknown",
        "local_path": (local or {}).get("local_path") or "",
        "local_integrity_status": (local or {}).get("integrity_status") or "",
    }


def write_missing(path, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing = [item for item in results if item["comparison_status"] in MISSING_STATUSES]
    generated = now_utc()
    lines = [
        "# Missing or unresolved course materials",
        "",
        f"Generated: {generated}",
        "",
        f"Total: {len(missing)}",
        "",
    ]
    if not missing:
        lines.append("No missing or unresolved downloadable course materials were detected.")
    else:
        lines.extend(
            [
                "| Name | Dashboard path | Type | Status | Reason | Last checked | Remote location | Suggested action |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in missing:
            values = [
                item["name"] or "(unnamed material)",
                item["dashboard_path"] or "(not recorded)",
                str(item.get("material_type") or "unknown"),
                f"`{item['comparison_status']}`",
                item["reason"],
                generated,
                item["url"] or "(not recorded)",
                "Retry when available, verify access, provide the file manually, or request deep verification.",
            ]
            escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
            lines.append("| " + " | ".join(escaped) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, "\n".join(lines).rstrip() + "\n")
    return missing


def main() -> int:
    args = parser().parse_args()
    remote_path = resolve_explicit(args.remote_inventory)
    local_path = resolve_explicit(args.local_inventory)
    output = resolve_explicit(args.output_directory)
    workspace = resolve_explicit(args.workspace_root) if args.workspace_root else None
    remote = read_records(remote_path)
    local = read_records(local_path)
    previous_remote = read_records(resolve_explicit(args.previous_remote)) if args.previous_remote else []
    action_rows = read_records(resolve_explicit(args.actions)) if args.actions else []
    actions = {action_key(row): row for row in action_rows if action_key(row)}
    used: set[int] = set()
    results: list[dict[str, Any]] = []
    for remote_item in remote:
        match_index = pick_match(remote_item, local, used)
        local_item = local[match_index] if match_index is not None else None
        if match_index is not None:
            used.add(match_index)
        status, reason = compare_one(remote_item, local_item)
        if status not in STATUSES:
            raise AssertionError(status)
        results.append(result_row(status, remote_item, local_item, reason, actions.get(action_key(remote_item))))
    for index, local_item in enumerate(local):
        if index in used:
            continue
        results.append(
            result_row(
                "remote_removed",
                {
                    "remote_item_id": local_item.get("remote_item_id") or "",
                    "name": local_item.get("name") or "",
                    "dashboard_path": local_item.get("dashboard_path") or "",
                    "module_path": local_item.get("module_path") or "",
                    "clean_url": local_item.get("clean_url") or local_item.get("url") or "",
                },
                local_item,
                "Verified local item no longer appears in the remote inventory",
            )
        )
    counts = Counter(item["status"] for item in results)
    action_counts = Counter(item["operation_action"] for item in results)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "sync_state.json"
    state = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "operation": args.operation,
        "remote_inventory": workspace_relative(remote_path, workspace) if workspace else remote_path.name,
        "local_inventory": workspace_relative(local_path, workspace) if workspace else local_path.name,
        "previous_remote_inventory": workspace_relative(resolve_explicit(args.previous_remote), workspace) if args.previous_remote and workspace else (resolve_explicit(args.previous_remote).name if args.previous_remote else None),
        "remote_count": len(remote),
        "previous_remote_count": len(previous_remote),
        "local_count": len(local),
        "downloadable_remote_count": sum(item.get("record_role") in {None, "", "downloadable_file"} and item.get("download_eligible") is not False for item in remote),
        "status_counts": {status: counts.get(status, 0) for status in sorted(STATUSES)},
        "operation_action_counts": {action: action_counts.get(action, 0) for action in sorted(VALID_ACTIONS)},
        "download_attempt_count": sum(bool(item["download_attempted"]) for item in results),
        "results": results,
    }
    write_json(state_path, state)
    write_csv(output / "sync_results.csv", results, CSV_FIELDS)
    missing_path = resolve_explicit(args.missing_report) if args.missing_report else output / "missing_materials.md"
    missing = write_missing(missing_path, results)
    write_json(
        missing_path.with_suffix(".json"),
        {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now_utc(),
            "missing_count": len(missing),
            "materials": missing,
        },
    )
    print(state_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
