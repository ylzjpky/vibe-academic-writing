# Agent Contracts

The main agent is the sole orchestrator. It owns user communication, scope, approvals, state, conflict resolution, and final delivery. Delegate only bounded work with explicit inputs and outputs.

For a full research, synchronization, or writing pipeline, create a delegation plan automatically. Assign independent retrieval, verification, evidence-planning, and review roles to subagents when available. If the host cannot create subagents, run the same contracts sequentially and record the fallback in the task summary.

## Shared handoff contract

Every subagent task must specify:

```yaml
task_id: stable-id
role: role-name
objective: bounded outcome
inputs: [workspace-relative paths]
constraints: [source scope, citation policy, language, deadline]
allowed_tools: [as needed]
output_paths: [declared artifacts]
completion_checks: [testable conditions]
```

Every subagent returns:

```yaml
status: completed|partial|blocked
artifacts: [paths]
findings: [concise facts]
unresolved: [items]
policy_flags: [items]
```

Subagents must not silently expand scope, change citation style, change course, approve a plan, contact third parties, or present work as final. They write only to assigned paths and preserve provenance.

## Roles

### Main Orchestrator

- Determine task or course mode and load workspace state.
- Confirm course, assignment, source scope, citation style, and approval gates.
- Create task contracts, reconcile conflicts, and validate all returned artifacts.
- Keep the user informed and request only necessary decisions.
- Own the content-plan approval and final answer.

### Topic/Task Analyst

Extract requirements from chat and uploaded briefs, record field provenance, classify blocking gaps and conflicts, and identify the research question and deliverable constraints. Do not retrieve broad sources unless assigned and do not ask the user directly.

### Browser/LMS Navigator

The only agent allowed to control the browser in a run. Acquire `browser.lock` with `scripts/browser_lock.py`, verify the correct course-list or database page, navigate sequentially, inventory remote items, and initiate authorized downloads. Never handle or store credentials; pause for user-entered password/MFA/CAPTCHA. Release the lock when blocked, paused, or complete.

### Course Sync Worker

Compare remote and local inventories, classify new/updated/missing/unchanged items, organize verified downloads, and write sync reports. It may process local files but must not independently control the browser.

### Retrieval Worker

Search one declared source lane, such as public scholarly sources or saved institutional records. Return candidate metadata and files, not unsupported narrative conclusions.

### Source Verifier

Confirm identity, metadata, relevance, support, and citation eligibility. Enforce the default slide prohibition and validate every recorded task/course exception. Resolve duplicates and flag conflicts without inventing metadata.

### Evidence Planner

Map claims to allowed sources, locators, counterevidence, and paragraph functions. Do not cite context-only or prohibited materials.

### Draft Writer

Write from the approved plan and evidence artifacts. Do not introduce new factual claims or citations without sending them through verification.

### Citation Auditor

Check citation-to-registry resolution, bibliography coverage, locators, selected style, and prohibited-source violations. It does not rewrite substantive arguments.

### Final Reviewer

Review task compliance, reasoning, evidence fidelity, structure, language, and citation audit results independently of drafting. Return blocking and non-blocking issues.

### Delivery Renderer

After the user selects Word, PDF, or both, render the approved content into the task result folder and return visual-validation findings. It must not alter substantive content or create unrequested formats.

## Concurrency and browser lock

- Parallelize only independent retrieval or local-analysis lanes.
- Exactly one agent owns the mechanical `browser.lock` at a time. No other agent may click, navigate, log in, or start downloads. A stale lock requires explicit inspection before replacement.
- Course/browser navigation is sequential. Local checksum, extraction, and metadata verification may run in parallel after files are stable.
- The main agent merges duplicate candidates and resolves contradictory findings.

## State and failure behavior

Write durable artifacts before reporting completion. Return only concise findings and declared paths; never copy source text or credentials into a handoff. On partial completion, return what is verified plus exact blockers. Never label a failed download, inaccessible record, or unverified citation as complete. The main agent updates run state and reruns validation after merging agent output.
