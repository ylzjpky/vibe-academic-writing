# Task intake and brief adaptation

Use this procedure whenever the user supplies assignment information in chat, uploads files, or places files in the current workspace.

## Intake order

1. Inventory the user's current message and relevant files before presenting a questionnaire.
2. Extract task title or question, deliverable type, target language, length, deadline, citation style, instructions, rubric, required and prohibited sources, existing thesis or materials, and requested workflow stage. Match the user's interaction language; if the deliverable language is absent and material, ask rather than assuming it matches the chat.
3. Record each field with its provenance and one status: `confirmed`, `inferred_needs_confirmation`, `missing_nonblocking`, `missing_blocking`, or `conflict`.
4. Prefer an explicit current user correction over stored state. When an official brief, rubric, template, and user statement conflict, surface the conflict instead of silently choosing.
5. Show a concise interpreted-task summary. Ask only about blocking, conflicting, or materially ambiguous fields.

Do not require the user to retype information already present in a readable file. Preserve original briefs under `00_brief/`; store extraction notes separately.

## Dependency gate

Treat a missing value as blocking when it can change the research object, assigned scope, structure, evidence set, citation behavior, or deliverable identity. Common examples include a topic allocated in class or group discussion, the user's group role, an instructor-assigned country or case, required data not supplied, classroom feedback, an unavailable original draft, or a required source that is not in the LMS.

Stop before retrieval or drafting and ask a direct question that names the missing dependency and why it is required. Do not infer classroom-only information from neighboring students, old tasks, course titles, or the absence of an LMS item.

Run this gate once after initial brief extraction and again after inspecting user-provided or selected course materials. If the second pass reveals that the brief depends on an absent group topic, class discussion, instructor allocation, data set, or original draft, pause immediately even if external retrieval has already begun.

Nonblocking fields may remain `null` or explicitly pending. Never invent an institutional default.

## Folder naming

Derive a short task name from the confirmed title. If more than one sensible identity remains, ask the user to choose. Create a sanitized child directory in the selected workspace. On collision, offer to continue the existing task, create a versioned sibling, or use another name; never overwrite silently.
