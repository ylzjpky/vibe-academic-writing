# Browser access and downloads

Load before public research, institutional retrieval, LMS enumeration, downloads, or browser recovery. Apply `safety-and-recovery.md`. Use the host's installed browser/computer-use skill and returned API documentation; the examples below apply only when those interfaces are exposed. A missing or policy-disabled interface is unavailable, not permission to build a replacement controller.

## Select an actual capability

1. Honor the user's selected browser, tab, or computer. Otherwise prefer an existing authorized session for the target site; use the Codex built-in browser for a new session, then an available CDP-connected browser or computer-use surface. Inspect only task-relevant tabs/windows.
2. Discover the available interfaces and read their documentation before calling them. Verify navigation, page observation, and local download access separately. A search tool, preview tab, or page screenshot alone cannot synchronize files.
3. Use one browser owner across all backends sharing a session. Acquire `browser_lock.py` in a shared workspace lock directory, not a different assignment directory for each controller. Keep that lock during backend switches; release it when pausing or finishing. Reacquire before resuming.
4. Bind the observed target tab/window and verify the site, course or publication, and login state. Built-in and external browsers have separate profiles; switching does not transfer authentication. The user completes login in the selected surface.
5. Save `browser_session.json` at the operation root with `backend: builtin|cdp|computer`, `status: ready|blocked|unavailable`, `download_method: event|directory_snapshot|manual`, a clean target origin, and a short non-secret fallback reason. Keep tab/window handles and CDP endpoints in runtime memory only. Mark `ready` only after observing the intended page; rediscover capabilities on resume. Record the `browser_access` stage through `manage_run_state.py`; use `TOOL_UNAVAILABLE` for a missing interface and the existing authentication/permission codes for site blockers.

CDP is a transport/capability; it can also be exposed by an in-app tab. Record the method actually used rather than pretending these are three separate authenticated sessions.

## Codex built-in browser

For the `cua_repl` surface, the first call in a fresh runtime is exactly one documented entry call chosen by the host's selection rules. An explicit tab mention goes directly to `cua.getTab({ mention: completeMentionUrl })`. When an inventory is needed, use:

```js
await cua.getState();
```

Inspect the returned state/documentation before the next call. Reuse an existing runtime binding or a known tab with `cua.getTab(observedTabId, { browser: observedBrowserId })`. Otherwise create a task tab:

```js
let tab = await cua.createBrowserTab("iab", confirmedUrl, { visible: false });
```

Use the returned accessibility/DOM state to choose controls. Prefer semantic locators for repetitive LMS lists. Reobserve after navigation, clicks, scrolls, frame changes, or user intervention. Derive selectors from the current page, including frames and newly opened tabs; avoid guessed selectors and blind click retries. Keep the tab available with the documented handoff mechanism when pausing for login or continuing in another turn; do not close user-owned tabs.

Accessibility roles can differ from Playwright's DOM roles: a `<summary>` may appear as an accessibility button but as generic text in `domSnapshot()`. If a role locator reports no matches, inspect the current DOM and use the same control's observed text or DOM attributes. Confirm the resulting expanded section before continuing; a locator mismatch alone does not justify switching backends.

When the returned API exposes `tab.playwright.waitForEvent` and `download.path`, arm the waiter before the observed download click:

```js
let [download] = await Promise.all([
  tab.playwright.waitForEvent("download", { timeoutMs: 30000 }),
  tab.playwright.getByRole("link", { name: observedDownloadLabel, exact: true }).click()
]);
let downloadedPath = await download.path({ timeoutMs: 30000 });
```

A null path, timeout, failed click, or permission prompt leaves the outcome unresolved. Inspect the current page and download state before another action. If a file arrives late, reconcile it instead of clicking again. Use `downloadMedia` only for a file link and only when the selected runtime documents it. For a PDF viewer use its visible download/export control, not a screenshot as a substitute for the source. Move only the returned, locally accessible file into the confirmed workspace; preserve existing versions.

## CDP browser control

Prefer an existing host-advertised CDP browser or a supported tab capability. Select its observed browser/tab ID through the browser tools; do not guess ports or attach to unrelated profiles. Read the capability documentation before commands:

```js
let capabilities = await tab.capabilities.list();
// Continue only when the returned list contains "cdp".
let cdp = await tab.capabilities.get("cdp");
nodeRepl.write(await cdp.documentation());
```

Navigate the selected tab to the intended HTTP(S) page and satisfy the host's origin/CDP approval before sending a permitted command. For example, `await cdp.send("Page.getFrameTree", {}, { timeoutMs: 10000 })` can diagnose which frame contains course content. Keep ordinary navigation, reading and downloads on the higher-level interface where it works. Use documented event cursors when observing CDP events; do not treat discarded events or console messages as download proof.

When the host explicitly permits direct CDP attachment and already provides Playwright, connect only to the user's confirmed local debugging endpoint. Do not use this path to bypass denied host access. In a supported JavaScript runtime:

```js
let address = new URL(confirmedCdpEndpoint);
if (!["http:", "ws:"].includes(address.protocol) ||
    !["localhost", "127.0.0.1", "[::1]"].includes(address.hostname) ||
    address.username || address.password || address.search || address.hash) {
  throw new Error("Use an explicitly confirmed local CDP endpoint without secrets");
}
let { chromium } = await import("playwright");
let connectedBrowser = await chromium.connectOverCDP(address.href, { timeout: 10000 });
let pages = connectedBrowser.contexts().flatMap(context => context.pages());
let page = pages.find(candidate => candidate.url() === confirmedTabUrl);
if (!page) throw new Error("The confirmed target tab is not present");
```

Reuse the selected context; creating an empty context loses the user's session. Check the installed Playwright API before using options; when available, `noDefaults: true` avoids changing an existing profile's settings. Use Playwright's documented `page.waitForEvent("download", { timeout: 30000 })` before the click and `download.saveAs(uniqueIncomingPath)` to copy the file into the workspace. Its option names differ from the Codex wrapper's `timeoutMs`. Verify the saved file. Do not call `browser.close()` on the user's browser, export cookies, read credential storage, clone a profile, or start a debugging port automatically. A denied or unsupported attachment becomes a recorded capability failure.

## Control the user's computer

Use only an enabled host computer-use tool, with the installed skill's initialization, window selection and confirmation rules. For example, the Windows Computer Use plugin exposes `@oai/sky` through `node_repl`:

```js
if (!globalThis.sky) {
  const { sky } = await import("@oai/sky");
  globalThis.sky = sky;
}
```

In a subsequent call, `await sky.list_apps()` returns the actual apps/windows. Select exactly one task-relevant returned window, then follow that skill's observe → act → reobserve loop. On a host exposing native `cua` apps instead, use its returned app/window inventory and documented bindings. Never fabricate window IDs or reuse stale screenshot coordinates.

This route handles an existing logged-in browser, native Save As dialogs, and UI controls unavailable through DOM/CDP. Keep actions on the authorized browser and its download dialogs. Let the user complete authentication and any security/permission changes. Do not automate terminal applications, password managers, security settings, or the Codex application's UI. If native control is disabled, record `TOOL_UNAVAILABLE`; do not simulate it with shell input injection or another controller.

Before each download, snapshot only the confirmed download directory. After the UI action, identify the newly created intended file, wait for partial-download markers to disappear and size to stabilize within a bounded wait, then verify it. Same-name files, concurrent user downloads, and unknown outcomes require an explicit association or manual handoff, never moving every new file.

## Shared retrieval and synchronization

- Public research: derive focused search questions from the brief; inspect promising scholarly records, deduplicate by DOI/stable identity, retrieve original content, and record bibliographic provenance. Search results and abstracts remain discovery leads when the required claim needs full text.
- E-library: reuse the authorized site session, verify the publication record, and obtain full text through its visible authorized controls. Record inaccessible records separately; follow `institutional-library.md`.
- Courses: apply `course-page-validation.md`, then inspect modules, pagination, collapsed sections, frames, popups and lazy-loaded content. Inventory every observed activity once with a stable ID and breadcrumb. Stop enumeration when all in-scope sections/pages are accounted for, not merely when counts match.
- Use the same remote/local inventory and download mapping regardless of backend. Synchronization never establishes citation eligibility.

For each completed download, save a compact row in `download_map.json`:

```json
{"materials": [{"remote_item_id": "item-1", "name": "reading.pdf", "local_path": "Week-1/reading (1).pdf"}]}
```

Paths are relative to the directory passed to the verifier. Include dashboard/module paths and a clean URL when no stable ID exists. Record the actual saved name, including browser collision suffixes; preserve this association after organizing files. Run:

```text
python -B scripts/verify_downloads.py <incoming> <reports> --expected <remote_inventory> --download-map <download_map> --workspace-root <workspace>
```

Preserve the resulting local identity fields and remote modification timestamp for later comparisons. An unresolved same-name file, partial download, or mismatched size/hash remains unavailable to drafting.

## Switch or recover

Switch only for a missing capability, unsupported control/dialog, or confirmed runtime disconnect. Record the reason, inspect pending downloads, bind the new surface, and revalidate site, course, login and download directory before continuing from the checkpoint. A stale tab needs a fresh tab binding, not automatic re-selection of the entire browser.

Authentication, CAPTCHA, `401`, `403`, `429`, access denial, user interruption and policy-disabled control require user handoff or the site's prescribed recovery. Switching backends must not retry those blocked operations. Unknown click/download outcomes require observation and reconciliation before retry. If all allowed routes fail, preserve the inventory and precise manual-download location in the missing report, rather than declaring the whole course synchronized or silently omitting the item.

## Interface references

API names are examples from the available host interfaces, not a guarantee of availability on every Codex surface. Recheck returned tool documentation on each host. Official background: [Browser](https://learn.chatgpt.com/docs/browser), [Playwright CDP attachment](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp).
