#!/usr/bin/env python3
"""Shared, standard-library helpers for develop-academic-paper scripts."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SCHEMA_VERSION = "1.2"
SLIDE_EXTENSIONS = {".ppt", ".pptx", ".pps", ".ppsx", ".odp"}
MACRO_EXTENSIONS = {".docm", ".dotm", ".xlsm", ".xltm", ".xlam", ".pptm", ".ppsm", ".potm"}
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar", ".tar", ".tgz", ".gz", ".bz2", ".xz"}
CLOUD_SYNC_MARKERS = {
    "onedrive": "Microsoft OneDrive",
    "dropbox": "Dropbox",
    "icloud drive": "Apple iCloud Drive",
    "icloud": "Apple iCloud",
    "mobile documents": "Apple iCloud",
    "clouddocs": "Apple iCloud",
    "google drive": "Google Drive",
    "googledrive": "Google Drive",
    "my drive": "Google Drive",
    "box sync": "Box Sync",
    "box-box": "Box Sync",
}
SLIDE_WORDS = re.compile(
    r"(?:^|[\W_])(slides?|slide[ -]?deck|lecture[ -]?slides?|presentation|powerpoint)(?:$|[\W_])",
    re.IGNORECASE,
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    """Atomically replace a JSON artifact in its destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_text(path: Path, value: str) -> None:
    """Atomically replace a UTF-8 text artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, data: Any) -> None:
    """Append one compact event record and flush it to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, payload.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    value = read_json(path)
    if isinstance(value, list):
        return [dict(item) for item in value]
    if isinstance(value, dict):
        for key in ("materials", "items", "sources", "courses", "records", "results"):
            if isinstance(value.get(key), list):
                return [dict(item) for item in value[key]]
    raise ValueError(f"No record list found in {path}")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    """Atomically replace a CSV artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: scalar(row.get(field, "")) for field in fields})
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def scalar(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return value


def slugify(value: str, fallback: str = "item") -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "-", normalized)
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip(" .-")
    return normalized[:100] or fallback


def resolve_explicit(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_looks_like_slides(path: Path) -> bool:
    searchable = " ".join((path.stem, *path.parent.parts[-2:]))
    if SLIDE_WORDS.search(searchable):
        return True
    try:
        with path.open("rb") as handle:
            sample = handle.read(1024 * 1024).lower()
    except OSError:
        return False
    markers = (b"microsoft powerpoint", b"powerpoint", b"slide deck")
    return any(marker in sample for marker in markers)


def is_slide_material(path: Path, material_type_hint: str = "") -> tuple[bool, str]:
    extension = path.suffix.lower()
    hint = material_type_hint.strip().lower().replace("-", "_")
    hinted_slides = any(word in hint for word in ("slide", "powerpoint", "presentation", "ppt"))
    is_slide = extension in SLIDE_EXTENSIONS or hinted_slides
    if extension == ".pdf" and (hinted_slides or pdf_looks_like_slides(path)):
        is_slide = True
        material_type = "lecture_slides_pdf"
    elif extension in SLIDE_EXTENSIONS:
        material_type = "lecture_slides"
    else:
        material_type = hint or {
            ".pdf": "pdf",
            ".doc": "document",
            ".docx": "document",
            ".txt": "text",
            ".md": "text",
            ".html": "web_export",
            ".htm": "web_export",
        }.get(extension, "other")
    return is_slide, material_type


def material_policy(
    path: Path,
    material_type_hint: str = "",
    slide_citation_policy: str = "prohibited",
    slide_permission_basis: str = "",
) -> dict[str, str]:
    is_slide, material_type = is_slide_material(path, material_type_hint)
    if is_slide and slide_citation_policy == "allowed_by_user_confirmation" and slide_permission_basis.strip():
        return {
            "material_type": material_type,
            "source_role": "evidence",
            "citation_eligibility": "requires_verification",
            "policy_reason": "Slide citation was user-confirmed for this task or course; source metadata still requires verification.",
        }
    if is_slide:
        return {
            "material_type": material_type,
            "source_role": "context_only",
            "citation_eligibility": "prohibited",
            "policy_reason": "Course slide decks are non-citable by default unless a task/course permission is recorded and verified.",
        }
    return {
        "material_type": material_type,
        "source_role": "unclassified",
        "citation_eligibility": "requires_verification",
        "policy_reason": "Citation eligibility requires source verification.",
    }


def redact_url(value: str) -> str:
    """Remove userinfo, fragments, secret queries, and obvious secret path segments."""
    if not value:
        return ""
    try:
        parts = urlsplit(value)
    except ValueError:
        return ""
    sensitive = re.compile(r"(?:token|signature|sig|auth|authorization|session|ticket|credential|code|secret|key|cookie)", re.IGNORECASE)
    safe_query = [(key, item) for key, item in parse_qsl(parts.query, keep_blank_values=True) if not sensitive.search(key)]
    hostname = parts.hostname or ""
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    safe_netloc = hostname
    try:
        if parts.port:
            safe_netloc = f"{safe_netloc}:{parts.port}"
    except ValueError:
        return ""
    path = parts.path
    path = re.sub(
        r"(?i)(/(?:token|auth|authorization|session|ticket|credential|secret|key)/)[^/]+",
        r"\1[redacted]",
        path,
    )
    path = re.sub(r"(?i)/eyJ[A-Za-z0-9_-]{20,}(?:\.[A-Za-z0-9_-]+){1,2}(?=/|$)", "/[redacted]", path)
    return urlunsplit((parts.scheme, safe_netloc, path, urlencode(safe_query, doseq=True), ""))


def basic_file_integrity(path: Path) -> tuple[str, str]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        return "local_missing", str(exc)
    if size == 0:
        return "local_corrupt", "File is empty"
    extension = path.suffix.lower()
    if extension in MACRO_EXTENSIONS:
        return "unsafe_macro", "Macro-enabled Office files require explicit user review and must not be executed"
    if extension in ARCHIVE_EXTENSIONS:
        return "archive_requires_review", "Archives must not be extracted automatically; review size and contents first"
    try:
        with path.open("rb") as handle:
            signature = handle.read(8)
    except OSError as exc:
        return "local_corrupt", str(exc)
    if extension == ".pdf" and not signature.startswith(b"%PDF-"):
        return "local_corrupt", "PDF signature is missing"
    if extension in {".pptx", ".docx", ".xlsx"} and not signature.startswith(b"PK"):
        return "local_corrupt", "OOXML ZIP signature is missing"
    return "verified", ""


def inventory_file(path: Path, root: Path) -> dict[str, Any]:
    status, reason = basic_file_integrity(path)
    policy = material_policy(path)
    result: dict[str, Any] = {
        "name": path.name,
        "local_path": path.relative_to(root).as_posix(),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if status == "verified" else "",
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if path.exists() else None,
        "integrity_status": status,
        "integrity_reason": reason,
    }
    result.update(policy)
    return result


def workspace_relative(path: Path, workspace_root: Path) -> str:
    """Return a portable workspace-relative path and reject external references."""
    ensure_under(path, workspace_root)
    return path.resolve().relative_to(workspace_root.resolve()).as_posix()


def slide_policy_config(path: Path | None) -> tuple[str, str, str | None]:
    if path is None:
        return "prohibited", "", None
    data = read_json(path)
    policy = str(data.get("slide_citation_policy") or data.get("ppt_citation_policy") or "prohibited")
    basis = str(data.get("slide_permission_basis") or "").strip()
    scope = data.get("slide_permission_scope")
    if policy == "allowed_by_user_confirmation" and (not basis or scope not in {"current_task", "course"}):
        raise ValueError("Allowed slide citation requires slide_permission_basis and scope current_task|course")
    if policy not in {"prohibited", "allowed_by_user_confirmation"}:
        raise ValueError(f"Unsupported slide_citation_policy: {policy}")
    return policy, basis, str(scope) if scope else None


def ensure_under(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Path {path} is outside workspace {root}") from exc


def no_credentials(data: Any) -> None:
    forbidden = re.compile(
        r"^(?:password|passwd|pwd|passcode|secret|client_secret|token|access_?token|refresh_?token|api_?key|credential|authorization|bearer|cookie|session_?id|sessioncookie)$",
        re.IGNORECASE,
    )
    findings: list[str] = []

    def visit(value: Any, trail: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if forbidden.match(str(key)) and nested not in (None, "", False):
                    findings.append(f"{trail}.{key}")
                visit(nested, f"{trail}.{key}")
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                visit(nested, f"{trail}[{index}]")
        elif isinstance(value, str):
            findings.extend(f"{trail}:{kind}" for kind in sensitive_text_findings(value))

    visit(data, "root")
    if findings:
        raise ValueError("Credential-like values are not allowed: " + ", ".join(findings))


SENSITIVE_TEXT_PATTERNS = (
    ("authorization_header", re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}")),
    ("credential_assignment", re.compile(r"(?i)\b(?:password|passwd|pwd|passcode|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token|session[_-]?id|cookie)\b\s*[:=]\s*['\"]?[^\s,'\";]{4,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}(?:\.[A-Za-z0-9_-]{10,})?\b")),
    ("url_userinfo", re.compile(r"(?i)https?://[^\s/@:]+:[^\s/@]+@")),
    ("signed_url", re.compile(r"(?i)[?&](?:token|signature|sig|auth|authorization|session|ticket|credential|secret|key|code)=[^\s&#]+")),
)


def sensitive_text_findings(value: str) -> list[str]:
    """Return finding labels without returning the sensitive values themselves."""
    return [label for label, pattern in SENSITIVE_TEXT_PATTERNS if pattern.search(value)]


def scan_text_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            for kind in sensitive_text_findings(line):
                findings.append({"line": line_number, "kind": kind})
    return findings


def cloud_sync_provider(path: Path) -> str | None:
    """Return a likely desktop cloud-sync provider based on path components."""
    for part in path.resolve().parts:
        normalized = part.strip().casefold()
        for marker, provider in CLOUD_SYNC_MARKERS.items():
            if marker in normalized:
                return provider
    return None


def print_result(path: Path) -> None:
    print(path.as_posix())
