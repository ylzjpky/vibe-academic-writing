#!/usr/bin/env python3
"""Create and update compact, resumable workflow state with sanitized events."""

from __future__ import annotations

import argparse
import re
import uuid
from pathlib import Path
from typing import Any

from _common import SCHEMA_VERSION, append_jsonl, now_utc, read_json, resolve_explicit, sensitive_text_findings, write_json


STAGE_STATUSES = {"pending", "running", "succeeded", "failed", "blocked", "skipped"}
RUN_STATUSES = {"running", "succeeded", "failed", "blocked", "cancelled"}
ERROR_CODES = {
    "AUTH_REQUIRED",
    "SESSION_EXPIRED",
    "PAGE_GATE_FAILED",
    "RATE_LIMITED",
    "PERMISSION_DENIED",
    "CLOUD_SYNC_WORKSPACE",
    "DOWNLOAD_LIMIT_EXCEEDED",
    "DOWNLOAD_MISMATCH",
    "UNSAFE_FILE",
    "SENSITIVE_DATA_DETECTED",
    "SOURCE_UNVERIFIED",
    "PLAN_STALE",
    "VALIDATION_FAILED",
    "RENDER_FAILED",
    "TOOL_UNAVAILABLE",
    "TRANSIENT_NETWORK_ERROR",
    "UNKNOWN_FAILURE",
}


def safe_text(value: str, field: str, limit: int = 500) -> str:
    normalized = " ".join(value.split())[:limit]
    if sensitive_text_findings(normalized):
        raise ValueError(f"{field} contains credential-like or signed-URL data")
    return normalized


def safe_relative(value: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Artifact references must be workspace-relative")
    return path.as_posix()


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start", help="Create a new run_state.json")
    start.add_argument("operation_root")
    start.add_argument("--mode", choices=("single_task", "course_sync", "course_assignment"), required=True)
    start.add_argument("--operation", required=True)
    start.add_argument("--run-id")
    stage = sub.add_parser("stage", help="Update one stage and emit a compact resume state")
    stage.add_argument("operation_root")
    stage.add_argument("--stage", required=True)
    stage.add_argument("--status", choices=sorted(STAGE_STATUSES), required=True)
    stage.add_argument("--input", action="append", default=[])
    stage.add_argument("--output", action="append", default=[])
    stage.add_argument("--error-code", choices=sorted(ERROR_CODES))
    stage.add_argument("--message", default="")
    stage.add_argument("--recovery-hint", default="")
    finish = sub.add_parser("finish", help="Finish or block the overall run")
    finish.add_argument("operation_root")
    finish.add_argument("--status", choices=sorted(RUN_STATUSES - {"running"}), required=True)
    finish.add_argument("--error-code", choices=sorted(ERROR_CODES))
    finish.add_argument("--message", default="")
    finish.add_argument("--recovery-hint", default="")
    return value


def paths(root: Path) -> tuple[Path, Path, Path]:
    return root / "run_state.json", root / "resume_state.json", root / "events.jsonl"


def stage_name(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", normalized):
        raise ValueError("Stage names must use lowercase letters, digits, and underscores")
    return normalized


def event(events_path: Path, state: dict[str, Any], event_type: str, **details: Any) -> None:
    append_jsonl(
        events_path,
        {
            "schema_version": SCHEMA_VERSION,
            "at": now_utc(),
            "run_id": state["run_id"],
            "event": event_type,
            **{key: item for key, item in details.items() if item not in (None, "", [])},
        },
    )


def write_resume(root: Path, state: dict[str, Any]) -> None:
    blockers = []
    artifacts = []
    for name, item in state.get("stages", {}).items():
        if item.get("status") in {"failed", "blocked"}:
            blockers.append(
                {
                    "stage": name,
                    "error_code": item.get("error_code"),
                    "message": item.get("message"),
                    "recovery_hint": item.get("recovery_hint"),
                }
            )
        if item.get("status") == "succeeded":
            artifacts.extend(item.get("outputs") or [])
    resume = {
        "schema_version": SCHEMA_VERSION,
        "run_id": state["run_id"],
        "mode": state["mode"],
        "operation": state["operation"],
        "status": state["status"],
        "current_stage": state.get("current_stage"),
        "last_successful_checkpoint": state.get("last_successful_checkpoint"),
        "updated_at": state["updated_at"],
        "blockers": blockers,
        "key_artifacts": list(dict.fromkeys(artifacts))[-20:],
    }
    write_json(root / "resume_state.json", resume)


def load_state(root: Path) -> dict[str, Any]:
    state_path = root / "run_state.json"
    if not state_path.is_file():
        raise SystemExit("run_state.json does not exist; start the run first")
    return read_json(state_path)


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.operation_root)
    root.mkdir(parents=True, exist_ok=True)
    state_path, _, events_path = paths(root)
    if args.command == "start":
        if state_path.exists():
            previous_state = read_json(state_path)
            if previous_state.get("status") == "running":
                raise SystemExit("A run is already active in this operation root")
            previous_run_id = safe_text(str(previous_state.get("run_id") or "previous-run"), "previous run_id", 80)
            write_json(root / "run_history" / f"{previous_run_id}.json", previous_state)
        created = now_utc()
        run_id = args.run_id or f"run-{uuid.uuid4().hex[:12]}"
        state = {
            "schema_version": SCHEMA_VERSION,
            "run_id": safe_text(run_id, "run_id", 80),
            "mode": args.mode,
            "operation": safe_text(args.operation, "operation", 120),
            "status": "running",
            "current_stage": None,
            "last_successful_checkpoint": None,
            "started_at": created,
            "updated_at": created,
            "finished_at": None,
            "stages": {},
        }
        write_json(state_path, state)
        event(events_path, state, "run_started", mode=args.mode, operation=state["operation"])
        write_resume(root, state)
    elif args.command == "stage":
        state = load_state(root)
        if state.get("status") != "running":
            raise SystemExit(f"Cannot update a run with status {state.get('status')!r}")
        name = stage_name(args.stage)
        previous = dict(state.get("stages", {}).get(name) or {})
        attempts = int(previous.get("attempts") or 0)
        if args.status == "running" and previous.get("status") != "running":
            attempts += 1
        elif args.status in {"succeeded", "failed", "blocked"} and attempts == 0:
            attempts = 1
        record = {
            "status": args.status,
            "attempts": attempts,
            "started_at": previous.get("started_at") or (now_utc() if args.status == "running" else None),
            "ended_at": now_utc() if args.status in {"succeeded", "failed", "blocked", "skipped"} else None,
            "inputs": [safe_relative(item) for item in args.input],
            "outputs": [safe_relative(item) for item in args.output],
            "error_code": args.error_code,
            "message": safe_text(args.message, "message") if args.message else "",
            "recovery_hint": safe_text(args.recovery_hint, "recovery_hint") if args.recovery_hint else "",
        }
        if args.status in {"failed", "blocked"} and not args.error_code:
            raise SystemExit("Failed or blocked stages require --error-code")
        state.setdefault("stages", {})[name] = record
        state["current_stage"] = name
        state["updated_at"] = now_utc()
        if args.status == "succeeded":
            state["last_successful_checkpoint"] = name
        write_json(state_path, state)
        event(events_path, state, "stage_updated", stage=name, status=args.status, error_code=args.error_code)
        write_resume(root, state)
    else:
        state = load_state(root)
        if args.status in {"failed", "blocked"} and not args.error_code:
            raise SystemExit("Failed or blocked runs require --error-code")
        state["status"] = args.status
        state["updated_at"] = now_utc()
        state["finished_at"] = now_utc()
        state["final_error"] = {
            "error_code": args.error_code,
            "message": safe_text(args.message, "message") if args.message else "",
            "recovery_hint": safe_text(args.recovery_hint, "recovery_hint") if args.recovery_hint else "",
        } if args.error_code or args.message or args.recovery_hint else None
        write_json(state_path, state)
        event(events_path, state, "run_finished", status=args.status, error_code=args.error_code)
        write_resume(root, state)
    print(state_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
