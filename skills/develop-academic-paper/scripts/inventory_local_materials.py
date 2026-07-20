#!/usr/bin/env python3
"""Inventory and hash files under one explicit local course-material directory."""

from __future__ import annotations

import argparse

from _common import SCHEMA_VERSION, inventory_file, now_utc, resolve_explicit, workspace_relative, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("directory", help="Explicit directory to scan recursively")
    value.add_argument("output", help="Output local_inventory.json")
    value.add_argument("--workspace-root", help="Workspace root used to persist a relative materials-root path")
    value.add_argument("--include-hidden", action="store_true")
    value.add_argument("--max-files", type=int, default=500)
    value.add_argument("--max-file-bytes", type=int, default=512 * 1024 * 1024)
    value.add_argument("--max-total-bytes", type=int, default=2 * 1024 * 1024 * 1024)
    return value


def main() -> int:
    args = parser().parse_args()
    root = resolve_explicit(args.directory)
    output = resolve_explicit(args.output)
    workspace = resolve_explicit(args.workspace_root) if args.workspace_root else root
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    candidates = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        relative = path.relative_to(root)
        if not args.include_hidden and any(part.startswith(".") for part in relative.parts):
            continue
        candidates.append(path)
    total_bytes = sum(path.stat().st_size for path in candidates)
    if len(candidates) > args.max_files:
        raise SystemExit(f"DOWNLOAD_LIMIT_EXCEEDED: file count {len(candidates)} exceeds {args.max_files}")
    if any(path.stat().st_size > args.max_file_bytes for path in candidates):
        raise SystemExit("DOWNLOAD_LIMIT_EXCEEDED: at least one file exceeds --max-file-bytes")
    if total_bytes > args.max_total_bytes:
        raise SystemExit(f"DOWNLOAD_LIMIT_EXCEEDED: total size {total_bytes} exceeds {args.max_total_bytes}")
    materials = [inventory_file(path, root) for path in candidates]
    document = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "root": workspace_relative(root, workspace),
        "item_count": len(materials),
        "total_bytes": total_bytes,
        "materials": materials,
    }
    write_json(output, document)
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
