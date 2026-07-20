#!/usr/bin/env python3
"""Create a concise diagnostic report from workflow state and validator outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import now_utc, read_json, resolve_explicit, write_text


REPORTS = (
    "artifact_validation.json",
    "sensitive_artifact_scan.json",
    "verification_report.json",
    "sync_state.json",
    "source_policy_validation.json",
    "citation_audit.json",
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("operation_root")
    value.add_argument("--output", help="Output Markdown report; defaults to diagnostic_report.md")
    return value


def compact_report(path: Path, data: dict[str, Any]) -> list[str]:
    lines = [f"### `{path.name}`", ""]
    for key in ("valid", "safe", "status", "error_count", "finding_count", "missing_count", "status_counts"):
        if key in data:
            lines.append(f"- {key}: `{data[key]}`")
    issues = data.get("issues") or data.get("findings") or []
    if isinstance(issues, list):
        for item in issues[:10]:
            if isinstance(item, dict):
                code = item.get("code") or item.get("kind") or item.get("severity") or "issue"
                location = item.get("path") or item.get("stage") or ""
                message = item.get("message") or item.get("reason") or ""
                lines.append(f"- `{code}` {location}: {message}".rstrip())
        if len(issues) > 10:
            lines.append(f"- … {len(issues) - 10} additional findings remain in the machine report.")
    lines.append("")
    return lines


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.operation_root)
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    output = resolve_explicit(args.output) if args.output else root / "diagnostic_report.md"
    lines = ["# Workflow diagnostic report", "", f"Generated: {now_utc()}", ""]
    state_path = root / "run_state.json"
    if not state_path.is_file():
        lines.extend(["## Run state", "", "`run_state.json` is missing. Start or reconstruct the run state before resuming.", ""])
    else:
        state = read_json(state_path)
        lines.extend(
            [
                "## Run state",
                "",
                f"- Run: `{state.get('run_id')}`",
                f"- Status: `{state.get('status')}`",
                f"- Current stage: `{state.get('current_stage')}`",
                f"- Last successful checkpoint: `{state.get('last_successful_checkpoint')}`",
                "",
            ]
        )
        failed = [(name, item) for name, item in (state.get("stages") or {}).items() if item.get("status") in {"failed", "blocked"}]
        if failed:
            lines.extend(["## Blocking stages", ""])
            for name, item in failed:
                lines.append(f"- `{name}` — `{item.get('error_code')}`: {item.get('message') or 'No message recorded.'}")
                if item.get("recovery_hint"):
                    lines.append(f"  Recovery: {item['recovery_hint']}")
            lines.append("")
    discovered = []
    for name in REPORTS:
        candidates = [path for path in root.rglob(name) if path.is_file() and path != output]
        if candidates:
            discovered.append(max(candidates, key=lambda item: item.stat().st_mtime))
    lines.extend(["## Validator evidence", ""])
    if not discovered:
        lines.extend(["No known validator reports were found.", ""])
    else:
        for path in discovered:
            try:
                lines.extend(compact_report(path, read_json(path)))
            except Exception as exc:
                lines.extend([f"### `{path.name}`", "", f"Could not read report: {type(exc).__name__}", ""])
    lines.extend(
        [
            "## Resume rule",
            "",
            "Resolve the recorded blocker, rerun the failed stage only, then rerun every downstream validator affected by changed inputs. Do not repeat successful authenticated downloads unless their local verification is no longer valid.",
            "",
        ]
    )
    write_text(output, "\n".join(lines))
    print(output.as_posix())
    return 1 if not state_path.is_file() else 0


if __name__ == "__main__":
    raise SystemExit(main())
