#!/usr/bin/env python3
"""Coordinate exclusive browser ownership across agents using a local lock file."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _common import SCHEMA_VERSION, resolve_explicit, sensitive_text_findings, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    for command in ("acquire", "renew", "release", "status"):
        item = sub.add_parser(command)
        item.add_argument("operation_root")
        if command != "status":
            item.add_argument("--owner", required=True, help="Non-secret run or agent identifier")
        if command in {"acquire", "renew"}:
            item.add_argument("--ttl-seconds", type=int, default=1800)
        if command == "acquire":
            item.add_argument("--replace-stale", action="store_true")
    return value


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def safe_owner(value: str) -> str:
    normalized = " ".join(value.split())[:120]
    if not normalized or sensitive_text_findings(normalized):
        raise ValueError("Owner must be a non-secret identifier")
    return normalized


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.operation_root)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / "browser.lock"
    if args.command == "status":
        if not lock.exists():
            print("unlocked")
            return 1
        data = json.loads(lock.read_text(encoding="utf-8"))
        expired = parse_time(data["expires_at"]) <= datetime.now(timezone.utc)
        print(json.dumps({**data, "expired": expired}, ensure_ascii=False))
        return 2 if expired else 0
    owner = safe_owner(args.owner)
    if args.command == "release":
        if not lock.exists():
            print("unlocked")
            return 0
        data = json.loads(lock.read_text(encoding="utf-8"))
        if data.get("owner") != owner:
            raise SystemExit("Refusing to release a browser lock owned by another run")
        lock.unlink()
        print("released")
        return 0
    if args.command == "renew":
        if not lock.exists():
            raise SystemExit("Cannot renew a missing browser lock")
        existing = json.loads(lock.read_text(encoding="utf-8"))
        if existing.get("owner") != owner:
            raise SystemExit("Refusing to renew a browser lock owned by another run")
        if args.ttl_seconds < 60 or args.ttl_seconds > 7200:
            raise SystemExit("--ttl-seconds must be between 60 and 7200")
        current = datetime.now(timezone.utc).replace(microsecond=0)
        existing["expires_at"] = (current + timedelta(seconds=args.ttl_seconds)).isoformat().replace("+00:00", "Z")
        existing["renewed_at"] = current.isoformat().replace("+00:00", "Z")
        write_json(lock, existing)
        print(lock.as_posix())
        return 0
    if args.ttl_seconds < 60 or args.ttl_seconds > 7200:
        raise SystemExit("--ttl-seconds must be between 60 and 7200")
    if lock.exists():
        existing = json.loads(lock.read_text(encoding="utf-8"))
        expired = parse_time(existing["expires_at"]) <= datetime.now(timezone.utc)
        if not expired or not args.replace_stale:
            print(json.dumps({**existing, "expired": expired}, ensure_ascii=False))
            return 2
        lock.unlink()
    created = datetime.now(timezone.utc).replace(microsecond=0)
    data = {
        "schema_version": SCHEMA_VERSION,
        "owner": owner,
        "acquired_at": created.isoformat().replace("+00:00", "Z"),
        "expires_at": (created + timedelta(seconds=args.ttl_seconds)).isoformat().replace("+00:00", "Z"),
    }
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    print(lock.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
