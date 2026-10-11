# Changelog

All notable changes to this project will be documented here. Versions follow Semantic Versioning.

## [Unreleased]

### Added

- Browser execution procedures for Codex's built-in browser, authorized CDP, and enabled user-computer control, with capability discovery and session-aware fallback.
- Download-event and native-directory workflows, plus explicit remote-to-local download mapping.
- Regression coverage for same-name files, browser-renamed downloads, partial downloads, external mapping paths, and historical remote timestamps.

### Fixed

- Download verification now preserves remote identity, original name and modification time, rejects ambiguous/reused file matches, and does not mark partial browser files verified.
- Resynchronization uses historical remote modification timestamps when older local inventories lack them and does not substitute a different stable identity by filename.

## [1.3.0] - 2026-07-21

### Added

- Codex plugin manifest for marketplace installation.
- Repository marketplace catalog for address-based installation.
- Full English and Simplified Chinese READMEs with marketplace, manual fallback, workflow, differentiation, safety, and verification guidance.
- Repository tests that keep plugin, marketplace, and Skill identities aligned.

### Changed

- Moved the runtime Skill under the canonical plugin directory.
- Updated CI and contributor commands for the plugin-backed layout.

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
