#!/usr/bin/env python3
"""Scan durable text artifacts for likely credentials or signed URLs."""

from __future__ import annotations

import argparse
from _common import SCHEMA_VERSION, now_utc, resolve_explicit, scan_text_file, write_json


TEXT_EXTENSIONS = {".json", ".jsonl", ".md", ".txt", ".csv", ".tsv", ".log", ".yaml", ".yml", ".bib"}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("root", help="Explicit task, assignment, course, or workspace root")
    value.add_argument("--report", help="Output report; defaults to sensitive_artifact_scan.json")
    value.add_argument("--max-text-bytes", type=int, default=20 * 1024 * 1024, help="Reject individual text artifacts larger than this limit")
    return value


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.root)
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    report_path = resolve_explicit(args.report) if args.report else root / "sensitive_artifact_scan.json"
    findings = []
    scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == report_path or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        scanned += 1
        relative = path.relative_to(root).as_posix()
        if path.stat().st_size > args.max_text_bytes:
            findings.append({"path": relative, "line": None, "kind": "oversized_text_artifact"})
            continue
        try:
            for item in scan_text_file(path):
                findings.append({"path": relative, **item})
        except OSError:
            findings.append({"path": relative, "line": None, "kind": "unreadable_text_artifact"})
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "root": ".",
        "scanned_file_count": scanned,
        "finding_count": len(findings),
        "safe": not findings,
        "findings": findings,
    }
    write_json(report_path, report)
    print(report_path.as_posix())
    return 0 if report["safe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
