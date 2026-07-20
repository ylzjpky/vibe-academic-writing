# Course-list page validation gate

Apply this gate before reading a course catalog, counting courses, creating course directories, or synchronizing materials. Treat failure or uncertainty as blocking.

## User-controlled authentication

1. Ask the user to open the institution dashboard and complete sign-in, MFA, CAPTCHA, consent, and account-selection steps.
2. Do not ask the user to disclose credentials in chat.
3. Do not store credentials, tokens, cookies, or recovery data.
4. Resume only after the user states that authentication is complete and the page is ready.

## Positive checks

Require all applicable checks:

- the hostname belongs to the institution or its recognized LMS provider;
- the session is authenticated and not expired;
- the page title, heading, breadcrumb, or navigation state identifies a dashboard or course-list view;
- multiple course cards or course rows are visible, or the page explicitly states that the scoped list is empty;
- each observed course has a recognizable name and a link or stable LMS identifier when exposed;
- active, current, archived, or other filters are visible or inferable;
- the current filter matches the user-confirmed synchronization scope.

## Exclusion checks

Fail the gate when the page is any of the following:

- a login, MFA, consent, or session-expired page;
- a search-engine result or general institution homepage;
- a single-course home page;
- a module, content, assignment, grade, calendar, notification, inbox, or discussion page;
- an e-library search-results page;
- a browser download page;
- a partial overlay, loading skeleton, error page, or access-denied page;
- a course list filtered to an unconfirmed term, status, campus, or role.

## Gate record

Record a non-secret validation object before catalog extraction:

```json
{
  "status": "passed",
  "checked_at": "ISO-8601 timestamp",
  "host": "lms.example.edu",
  "page_title": "Courses",
  "breadcrumb": ["Dashboard", "Courses"],
  "scope_filter": "current_active",
  "visible_course_count": 4,
  "evidence": ["course_cards_visible", "courses_nav_selected"]
}
```

Do not store session identifiers or full URLs containing personal tokens. Redact sensitive query parameters.

## Confirmation

1. Extract a proposed list only after the gate passes.
2. Present the visible course count and names to the user.
3. Ask the user to confirm the list and scope.
4. If the user reports missing or extra courses, recheck filters and pagination; do not silently correct the catalog.
5. If pagination or lazy loading exists, traverse it completely before declaring the count.

## Failure behavior

On failure, report which condition failed and ask the user to navigate to the correct course-list page. Do not create, rename, merge, archive, or delete course directories until validation and confirmation succeed.
