# User source preferences

Use human-editable Markdown for durable preferences and copy the effective choices into each task configuration.

## Storage and prompting

- Global preferences: `<workspace>/user_preferences.md`.
- Course preferences: `courses/<course>/04_course_memory/source_preferences.md`.
- Effective task snapshot: store the resolved choices in the task configuration and, when useful, `00_brief/source_preferences_snapshot.md`.

Before the first source search in a single-task workspace, ask for preferences only when no global file exists. Before the first assignment in a course, ask whether to inherit global preferences or create a course file when no course preference file exists. When preferences exist, summarize what will be applied and ask only if the current request conflicts or proposes a change.

The user may describe preferences naturally. Normalize them under: scope; preferred, allowed, and excluded source types; databases; date range; language; geography; peer-review preference; primary/secondary balance; access channel; slide policy; and other requirements. Record `last_updated`, scope, and the user's stated basis. Never store credentials or session data.

## Precedence and changes

Resolve rules in this order:

1. access, safety, and academic-integrity boundaries;
2. assignment, rubric, and instructor requirements;
3. confirmed current-task choices;
4. course preferences;
5. global preferences;
6. skill defaults.

Surface conflicts. A task-only choice does not update durable preferences unless the user asks. Version or annotate material preference changes rather than silently replacing their basis.

Slides default to prohibited citations. If the user says slides may be formal references, ask whether the permission applies to the current task or the course and record the assignment/instructor permission basis. A global desire to cite slides is only a request to consider them; it cannot by itself establish permission or source eligibility.
