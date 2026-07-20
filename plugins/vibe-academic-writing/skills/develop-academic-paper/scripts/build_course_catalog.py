#!/usr/bin/env python3
"""Normalize user-observed course-list records into a course catalog."""

from __future__ import annotations

import argparse

from _common import SCHEMA_VERSION, no_credentials, now_utc, read_records, redact_url, resolve_explicit, slugify, write_json


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("input", help="JSON or CSV exported by the user/browser agent")
    value.add_argument("output", help="Output course_catalog.json")
    value.add_argument("--institution-domain", default="")
    value.add_argument("--page-title", default="")
    value.add_argument("--page-url", default="")
    value.add_argument("--breadcrumb", default="")
    value.add_argument("--page-confirmed", action="store_true", help="Record explicit confirmation that this is the course-list page")
    return value


def main() -> int:
    args = parser().parse_args()
    rows = read_records(resolve_explicit(args.input))
    no_credentials(rows)
    if not args.page_confirmed:
        raise SystemExit("Course-list page is not confirmed; rerun only after verification with --page-confirmed")
    courses = []
    identifiers: set[str] = set()
    folder_names: set[str] = set()
    for index, row in enumerate(rows, start=1):
        name = str(row.get("course_name") or row.get("name") or "").strip()
        if not name:
            raise SystemExit(f"Record {index} has no course name")
        course_id = str(row.get("course_id") or row.get("id") or f"course-{index:03d}").strip()
        if course_id in identifiers:
            raise SystemExit(f"Duplicate course_id: {course_id}")
        identifiers.add(course_id)
        base_folder = slugify(str(row.get("folder_name") or name), fallback=course_id)
        folder_name = base_folder
        if folder_name.casefold() in folder_names:
            folder_name = f"{base_folder}-{slugify(course_id, fallback=f'course-{index:03d}')}"
        folder_names.add(folder_name.casefold())
        courses.append(
            {
                "course_id": course_id,
                "course_name": name,
                "folder_name": folder_name,
                "dashboard_path": str(row.get("dashboard_path") or row.get("path") or ""),
                "url": redact_url(str(row.get("url") or "")),
                "status": str(row.get("status") or "active").lower(),
            }
        )
    output = resolve_explicit(args.output)
    document = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "page_verification": {
            "confirmed": True,
            "institution_domain": args.institution_domain,
            "page_title": args.page_title,
            "page_url": redact_url(args.page_url),
            "breadcrumb": args.breadcrumb,
        },
        "course_count": len(courses),
        "courses": courses,
    }
    write_json(output, document)
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
