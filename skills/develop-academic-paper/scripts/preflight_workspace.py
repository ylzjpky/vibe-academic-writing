#!/usr/bin/env python3
"""Check an academic workspace for cloud-sync and storage-scope risks."""

from __future__ import annotations

import argparse
import os

from _common import SCHEMA_VERSION, cloud_sync_provider, now_utc, read_json, resolve_explicit, write_json


DEFAULT_MAX_FILES = 500
DEFAULT_MAX_FILE_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("workspace", help="Explicit workspace path to inspect")
    value.add_argument("--report", help="Output report; defaults to workspace_preflight.json")
    value.add_argument("--acknowledge-cloud-sync", action="store_true", help="Record the user's explicit decision to use a detected cloud-synced directory")
    value.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    value.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    value.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    return value


def main() -> int:
    args = parser().parse_args()
    workspace = resolve_explicit(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    provider = cloud_sync_provider(workspace)
    findings = []
    if provider:
        findings.append(
            {
                "severity": "warning" if args.acknowledge_cloud_sync else "blocker",
                "code": "CLOUD_SYNC_WORKSPACE",
                "message": f"The workspace appears to be inside {provider}; licensed or private course files may be uploaded automatically.",
                "recovery_hint": "Use a non-synced local directory or obtain user confirmation and rerun with --acknowledge-cloud-sync.",
            }
        )
    if args.max_files < 1 or args.max_file_bytes < 1 or args.max_total_bytes < 1:
        raise SystemExit("Download limits must be positive integers")
    if args.max_file_bytes > args.max_total_bytes:
        raise SystemExit("--max-file-bytes cannot exceed --max-total-bytes")
    if os.name != "nt":
        try:
            mode = workspace.stat().st_mode & 0o777
            if mode & 0o004:
                findings.append(
                    {
                        "severity": "warning",
                        "code": "WORLD_READABLE_WORKSPACE",
                        "message": "The workspace is readable by other local users.",
                        "recovery_hint": "Restrict directory permissions when the device is shared.",
                    }
                )
        except OSError:
            pass
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "workspace": ".",
        "cloud_sync_provider": provider,
        "cloud_sync_acknowledged": bool(provider and args.acknowledge_cloud_sync),
        "download_limits": {
            "max_files": args.max_files,
            "max_file_bytes": args.max_file_bytes,
            "max_total_bytes": args.max_total_bytes,
        },
        "macro_enabled_office_files": "prohibited_without_manual_review",
        "automatic_archive_extraction": "prohibited",
        "status": "blocked" if any(item["severity"] == "blocker" for item in findings) else "passed_with_warnings" if findings else "passed",
        "findings": findings,
    }
    report_path = resolve_explicit(args.report) if args.report else workspace / "workspace_preflight.json"
    write_json(report_path, report)
    config_path = workspace / "workspace_config.json"
    if args.acknowledge_cloud_sync and provider and config_path.exists():
        config = read_json(config_path)
        config["cloud_sync_acknowledgement"] = {
            "provider": provider,
            "acknowledged_at": now_utc(),
            "basis": "explicit_user_confirmation",
        }
        config["updated_at"] = now_utc()
        write_json(config_path, config)
    print(report_path.as_posix())
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
