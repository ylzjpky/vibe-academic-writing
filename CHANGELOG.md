# Changelog

All notable changes to this project will be documented here. Versions follow Semantic Versioning.

## [1.2.0] - 2026-07-20

### Added

- Single-task and persistent course workflows.
- Authorized LMS course-material synchronization and metadata-only resynchronization.
- Public and institutional-library source routing.
- User and course preference storage.
- APA, MLA, Chicago, Harvard, and custom citation workflows.
- Word/PDF delivery selection and result-directory generation.
- Compact run state, recovery diagnostics, browser locking, artifact validation, citation auditing, source-policy validation, download verification, and sensitive-data scanning.

### Changed

- English is the fallback interaction and deliverable language; detected user and assignment languages take precedence.
- Course slides are non-citable by default rather than permanently prohibited.
- Resynchronization defaults to metadata-only comparison to reduce unnecessary browsing, downloads, and token use.
