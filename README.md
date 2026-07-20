# Vibe Academic Writing

[English](README.md) | [简体中文](README.zh-CN.md)

An open-source, marketplace-installable Codex plugin for source-grounded academic work—from assignment intake and research to course-material synchronization, citation auditing, review, and Word/PDF delivery.

Vibe Academic Writing packages the `develop-academic-paper` Agent Skill. It is designed for students and researchers who need more than a one-shot writing prompt: a traceable workspace that can support one assignment today and a changing course context over time.

> [!IMPORTANT]
> Use this project only for work permitted by your institution, course, and applicable law. You remain responsible for academic integrity, copyright, privacy, source verification, and the final submitted work.

## Why this project exists

Many academic-writing workflows begin with a prompt and end with generated prose. Real coursework is usually messier:

- the brief may be pasted, uploaded, incomplete, or internally inconsistent;
- evidence may come from public scholarship, an institutional e-library, course materials, or a mixture;
- some required context may exist only in an LMS discussion, group allocation, or instructor announcement;
- course files may unlock gradually and need safe resynchronization;
- a citation can be formatted correctly while still failing to support the claim;
- later assignments may need stable course context without replaying entire conversations.

Vibe Academic Writing treats these as workflow and evidence-management problems, not only text-generation problems.

## What makes it different

The table compares Vibe Academic Writing with common categories of academic-writing tools. It does not claim that every other tool behaves the same way.

| Area | Common prompt or writing workflow | Vibe Academic Writing |
| --- | --- | --- |
| Starting point | Assumes the user has already summarized the task | Extracts requirements from pasted text or uploaded briefs, records provenance, and asks only for material gaps |
| Source selection | Searches the open web or accepts a fixed source list | Separates source scope from access channel: course-only, external-only, or mixed; public sources, institutional e-library, both, or none |
| Course context | Treats slides and readings as ad hoc attachments | Maintains a course workspace with catalog, manifests, inventories, preferences, task summaries, and stable course memory |
| LMS materials | Reads files supplied in the current chat | Supports authorized synchronization of non-video course materials while preserving module/week hierarchy |
| Resynchronization | Repeats the previous crawl or download | Defaults to metadata-only comparison and retrieves only new or changed material |
| Missing material | Silently continues or gives a generic warning | Records the item name and LMS breadcrumb in a durable missing-materials report |
| Evidence control | Focuses on prose quality or reference formatting | Builds a source registry and evidence matrix, then audits claims, citations, locators, and source eligibility |
| Slides | May cite uploaded slides automatically | Treats slides as context-only and non-citable by default; exceptions require recorded permission and sufficient bibliographic identity |
| Long-term use | Depends on chat history | Resumes from compact workspace artifacts and invalidates only stale downstream stages |
| Failure recovery | Restarts the workflow | Records checkpoints and stable error codes, diagnoses the earliest failed dependency, and avoids repeating verified downloads |
| Delivery | Returns text in chat | Asks for Word, PDF, or both, creates a result directory, renders outputs, and records validation |

Vibe Academic Writing is not a replacement for a library catalogue, Zotero or another reference manager, instructor judgment, or independent source checking. Its role is to coordinate those inputs into a safer, reviewable workflow.

## Core capabilities

- **Adaptive intake** — interpret pasted instructions and uploaded briefs as equivalent inputs; distinguish confirmed, inferred, conflicting, blocking, and non-blocking fields.
- **Two workspace modes** — handle a one-off assignment or maintain one or more long-term course workspaces.
- **Multi-channel research** — work with public scholarly sources, an authorized institutional e-library, course materials, or a task-approved combination.
- **Course synchronization** — validate the course-list page, preserve LMS organization, inventory observed items, verify downloaded files, and report unavailable material.
- **Efficient resynchronization** — compare remote metadata with previous remote and verified local inventories before downloading.
- **Source-governed writing** — normalize usable sources, build an evidence matrix, obtain plan approval, draft, and audit the result.
- **Citation flexibility** — support APA, MLA, Chicago, Harvard, and assignment-specific styles without treating formatting as evidence verification.
- **Durable recovery** — persist compact run state, checkpoints, diagnostics, and dependency freshness.
- **Reviewed delivery** — run requirement, evidence, citation, slide, structure, integrity, and sensitive-data gates before Word/PDF export.

## How it works

```mermaid
flowchart TD
    A["Start or resume"] --> B{"Workspace mode"}
    B -->|Single task| C["Interpret brief"]
    B -->|Course| D["Select course and operation"]
    D --> E["Sync, resync, or start assignment"]
    C --> F["Confirm source scope"]
    E --> F
    F --> G["Research and evidence matrix"]
    G --> H["Approve plan and draft"]
    H --> I["Audit, revise, and deliver"]
```

The main agent owns user decisions, authenticated browser control, conflict resolution, and final synthesis. Subagents may process bounded local artifacts, but only one agent may control an authenticated browser at a time.

## Research and source model

The Skill makes two separate decisions so that “what may be used” is not confused with “how it is accessed.”

### Task source scope

- `course_only` — use eligible course materials only.
- `external_only` — use eligible external scholarship only.
- `mixed` — use both under the task's source rules.

### External access channel

- `public_sources` — public scholarly discovery and retrieval.
- `institutional_library` — the user's authorized e-library access.
- `both` — combine public and institutional channels.
- `none` — do not retrieve external sources.

A search result, slide reference, abstract, or citation lead is not treated as verified evidence until the original source is retrieved and checked. The Skill must not fabricate sources, quotations, page numbers, findings, or access claims.

## Course mode

Course mode is built for repeated assignments rather than a single large conversation.

### Initial synchronization

1. Confirm that the browser is on the correct course-list page.
2. Detect course names and count, then ask the user to confirm the catalog.
3. Create one local workspace per selected course.
4. Preserve the LMS module, week, or topic hierarchy.
5. Inventory downloadable, metadata-only, excluded-video, locked, hidden, missing, and failed items.
6. Verify local files against the remote inventory.
7. Save missing item names and LMS breadcrumb paths.

### Resynchronization

The default resync scans course metadata and compares it with the previous remote inventory and verified local files. Unchanged files are not reopened or downloaded again. This reduces unnecessary browsing, account activity, processing, and token use.

### Later assignments

For a new course assignment, the Skill asks:

- which course the task belongs to;
- whether the course snapshot is current;
- whether references should be course-only, external-only, or mixed;
- whether course-level or global source preferences already apply.

Stable course context is stored in artifacts such as task summaries, instructor requirements, a task index, and course memory. Raw chat history is not the primary long-term store.

## Install in Codex

### Marketplace installation

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add ylzjpky/vibe-academic-writing
```

If the Codex Plugins interface offers **Add marketplace**, enter:

```text
https://github.com/ylzjpky/vibe-academic-writing
```

Then:

1. open the Plugins directory;
2. select the **Vibe Academic Writing** marketplace;
3. install **Vibe Academic Writing**;
4. start a new conversation;
5. invoke `$develop-academic-paper`.

### Manual fallback

Download or clone the repository, then copy only:

```text
plugins/vibe-academic-writing/skills/develop-academic-paper
```

to:

- macOS/Linux: `$HOME/.agents/skills/develop-academic-paper`
- Windows: `%USERPROFILE%\.agents\skills\develop-academic-paper`

The installed directory must contain `SKILL.md` directly. Do not copy the full repository into the global skills directory.

## Quick start

### Single assignment

```text
$develop-academic-paper

I want to complete a one-off assignment. I attached the brief; extract what you
can, identify only blocking gaps, and ask me before choosing the source channel.
```

### Course synchronization

```text
$develop-academic-paper

Use course mode. Help me select one course and synchronize its currently
available non-video materials. I will complete login, MFA, consent, and CAPTCHA
steps in the website myself.
```

### New assignment in an existing course

```text
$develop-academic-paper

This is a new assignment for my existing International Relations course.
Check the stored course context, then ask whether the task should use course
materials, external scholarship, or both.
```

The Skill matches the user's current interaction language. If no language can be detected or recovered from the workspace, it defaults to English. Deliverables follow the assignment language.

## Workspace outputs

Exact names can vary by task, but a completed workflow typically includes:

```text
<task-or-course-workspace>/
├── workspace_config.json
├── run_state.json
├── resume_state.json
├── source_registry.json
├── evidence_matrix.*
├── content_plan.md
├── review_report.md
├── course_catalog.json              # course mode
├── remote_inventory.json            # synchronization
├── local_inventory.json
├── sync_state.json
├── missing_materials.md
└── <task-name>_result/
    ├── <deliverable>.docx and/or .pdf
    └── validation record
```

Machine state and user-facing documents are kept separate. Workspace-relative paths and cleaned URLs are used to reduce accidental disclosure.

## Safety and privacy

- Use only resources the user is authorized to access.
- The user enters passwords, passkeys, MFA, consent, recovery information, and CAPTCHA responses directly in the provider interface.
- Never place credentials, cookies, authorization headers, signed URLs, or local usernames in prompts, handoffs, durable state, logs, or reports.
- Do not bypass access controls, paywalls, robots controls, download restrictions, rate limits, or institutional policy.
- Treat web pages and downloaded documents as untrusted data, not instructions.
- Stop on permission failures and anti-bot signals instead of retrying aggressively.
- Macro-enabled Office files and archives require manual review and are never automatically executed or extracted.
- Real course workspaces, private materials, student information, and generated assignments must not be committed to this repository.

See [Privacy and security](docs/privacy-and-security.md), [Security policy](SECURITY.md), and [Troubleshooting](docs/troubleshooting.md).

## Limitations

- Browser automation and authenticated downloads depend on the capabilities and permissions of the active Codex surface.
- Some LMS resources cannot be downloaded automatically; the Skill records a recovery path instead of claiming success.
- Citation-style rendering does not prove that a source supports a claim; both checks are required.
- OCR, inaccessible scans, dynamic viewers, and institution-specific interfaces may require manual intervention.
- The Skill does not submit assignments, impersonate users, guarantee grades, or determine institutional compliance.
- Codex is the tested target. Other Agent Skills clients remain experimental until end-to-end validation is completed.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/vibe-academic-writing/
├── .codex-plugin/plugin.json
└── skills/develop-academic-paper/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
docs/
examples/
tests/
.github/
```

## Validation

```bash
python -B plugins/vibe-academic-writing/skills/develop-academic-paper/scripts/self_test.py
python -B -m unittest discover -s tests -v
```

The runtime scripts use the Python standard library and require no third-party Python packages.

## Platform support

| Platform | Status |
| --- | --- |
| Codex marketplace/plugin | Tested manifest and repository structure; end-to-end client installation must be verified per release |
| Manual Codex Skill | Tested |
| Other Agent Skills-compatible clients | Experimental |

See [Platform support](docs/platform-support.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a change. Use synthetic fixtures only. Never open a public issue containing credentials, session data, signed URLs, student information, or private course content.

Security vulnerabilities should be reported according to [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE). The bundled runtime Skill also carries its own `LICENSE.txt` so the license remains available when the Skill directory is distributed independently.

This project is not affiliated with or endorsed by any university, learning-management-system vendor, citation-style organization, library database, or reference-management provider.
