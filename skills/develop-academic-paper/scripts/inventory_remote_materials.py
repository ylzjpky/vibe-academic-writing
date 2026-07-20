#!/usr/bin/env python3
"""Normalize local JSON/CSV observations of remote course materials; never accesses the network."""

from __future__ import annotations

import argparse
from typing import Any

from _common import SCHEMA_VERSION, no_credentials, now_utc, read_records, redact_url, resolve_explicit, write_json


def truthy(value: Any, default: bool = False) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "eligible", "available"}


def integer(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid size value: {value!r}") from exc


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("input", help="Local JSON/CSV generated from the authenticated browser session")
    value.add_argument("output", help="Output remote_inventory.json")
    value.add_argument("--course-id", default="")
    value.add_argument("--course-name", default="")
    value.add_argument("--observed-page", default="", help="Human-readable Dashboard path where inventory was observed")
    return value


def main() -> int:
    args = parser().parse_args()
    rows = read_records(resolve_explicit(args.input))
    no_credentials(rows)
    materials = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        name = str(row.get("name") or row.get("filename") or row.get("title") or "").strip()
        if not name:
            raise SystemExit(f"Remote material record {index} has no name/title")
        remote_id = str(row.get("remote_item_id") or row.get("remote_id") or row.get("id") or "").strip()
        dashboard_path = str(row.get("dashboard_path") or row.get("path") or args.observed_page).strip()
        url = redact_url(str(row.get("clean_url") or row.get("url") or row.get("download_url") or "").strip())
        dedupe_key = remote_id or url or f"{dashboard_path}|{name}"
        if dedupe_key in seen:
            raise SystemExit(f"Duplicate remote material at record {index}: {name}")
        seen.add(dedupe_key)
        availability = str(row.get("availability") or row.get("status") or "available").strip().lower()
        eligible_default = availability not in {"locked", "hidden", "unavailable", "permission_denied"}
        material_type = str(row.get("material_type") or row.get("type") or "unknown").strip().lower()
        is_video = any(marker in material_type for marker in ("video", "movie", "recording"))
        explicit_role = str(row.get("record_role") or "").strip().lower()
        if explicit_role and explicit_role not in {"downloadable_file", "metadata_only", "excluded_video"}:
            raise SystemExit(f"Invalid record_role at record {index}: {explicit_role}")
        explicit_eligible = truthy(row.get("download_eligible"), eligible_default)
        native_markers = ("moodle_native", "announcement", "forum", "survey", "quiz", "page", "discussion")
        if explicit_role:
            record_role = explicit_role
        elif is_video:
            record_role = "excluded_video"
        elif any(marker in material_type for marker in native_markers) or (row.get("download_eligible") not in (None, "") and not explicit_eligible and availability == "available"):
            record_role = "metadata_only"
        else:
            record_role = "downloadable_file"
        download_eligible = record_role == "downloadable_file" and explicit_eligible
        materials.append(
            {
                "remote_item_id": remote_id,
                "name": name,
                "material_type": material_type,
                "dashboard_path": dashboard_path,
                "clean_url": url,
                "module_path": str(row.get("module_path") or row.get("module") or "").strip(),
                "availability": availability,
                "record_role": record_role,
                "download_eligible": download_eligible,
                "exclusion_status": "excluded_video" if record_role == "excluded_video" else "",
                "unresolved_status": str(row.get("unresolved_status") or row.get("issue_status") or "").strip().lower(),
                "modified_at": str(row.get("modified_at") or row.get("last_modified") or "").strip(),
                "size_bytes": integer(row.get("size_bytes") or row.get("size")),
                "sha256": str(row.get("sha256") or "").strip().lower(),
                "content_change_signal": str(row.get("content_change_signal") or "").strip().lower(),
            }
        )
    output = resolve_explicit(args.output)
    write_json(
        output,
        {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now_utc(),
            "source": "authenticated_browser_observation_normalized_locally",
            "course_id": args.course_id,
            "course_name": args.course_name,
            "observed_page": args.observed_page,
            "item_count": len(materials),
            "materials": materials,
        },
    )
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
