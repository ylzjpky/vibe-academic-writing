# Vibe Academic Writing

Vibe Academic Writing is an open-source Agent Skill for source-grounded academic workflows. Its runtime skill is named `develop-academic-paper` and supports assignment intake, public or institutional research, authorized course-material synchronization, content planning, citation checks, drafting, review, and Word/PDF delivery.

## What it does

- Adapts pasted instructions and uploaded assignment briefs into structured task requirements.
- Supports one-off assignments and persistent course workspaces.
- Searches public sources or works with an institution's e-library when the user is authorized.
- Synchronizes non-video course files from an authorized LMS and verifies local inventory.
- Supports APA, MLA, Chicago, Harvard, and assignment-specific citation rules.
- Keeps course slides context-only and non-citable by default unless an explicit, higher-priority rule permits their use.
- Records compact state, checkpoints, diagnostics, and evidence audits for recovery and review.
- Exports reviewed deliverables to Word, PDF, or both.

## Safety model

The user must enter passwords, MFA codes, passkeys, consent, and CAPTCHA responses directly in the institution's website. The skill must never request, store, or transmit those secrets. It does not bypass access controls, paywalls, download restrictions, rate limits, robots controls, or institutional policy.

Use this project only with resources you are authorized to access. Review your institution's academic-integrity, copyright, privacy, and acceptable-use rules before using generated work or synchronized materials. See [Privacy and security](docs/privacy-and-security.md).

## Install

The installable skill is located at [`skills/develop-academic-paper`](skills/develop-academic-paper).

For Codex, copy that directory into your personal skills directory so the final path contains `SKILL.md` directly:

```text
<personal-skills-directory>/develop-academic-paper/SKILL.md
```

Installation paths and discovery behavior vary by client. Do not copy the repository-level documentation, tests, or `.github` directory into the runtime skill directory.

## Quick start

Example single-task request:

```text
Use develop-academic-paper for this assignment. I have attached the brief. Extract the requirements, ask only for blocking information, and help me complete the research and writing workflow.
```

Example course-mode request:

```text
Use develop-academic-paper in course mode. Help me select one course and synchronize its currently available non-video materials. I will complete login and MFA in the website myself.
```

The skill matches the user's current interaction language. If no language can be detected or recovered from the workspace, it defaults to English. Deliverables follow the assignment language.

## Repository layout

```text
skills/develop-academic-paper/  Runtime Agent Skill
docs/                           Architecture, security, support, troubleshooting
examples/                       Synthetic usage examples only
tests/                          Repository-level validation
.github/                        CI and contribution templates
```

## Validation

Run the runtime regression suite and repository checks:

```bash
python -B skills/develop-academic-paper/scripts/self_test.py
python -B -m unittest discover -s tests -v
```

No third-party Python runtime packages are required.

## Platform support

Codex is the currently tested target. The core layout follows the Agent Skills format, but compatibility with other clients is not claimed until that client has been tested. See [Platform support](docs/platform-support.md).

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change. Never open a public issue containing credentials, session data, student information, private course content, or signed URLs. Report security issues according to [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).

This project is not affiliated with or endorsed by any university, learning-management-system vendor, citation-style organization, or database provider.
