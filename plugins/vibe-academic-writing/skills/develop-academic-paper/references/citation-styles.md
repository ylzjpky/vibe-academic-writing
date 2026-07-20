# Citation Styles and Normalized Metadata

Keep source metadata style-neutral until rendering. `source_registry.json` is authoritative; formatted in-text citations, notes, and bibliographies are derived artifacts.

## Supported styles

- APA 7th edition (`apa-7`)
- Chicago author-date (`chicago-author-date`)
- Chicago notes and bibliography (`chicago-notes-bibliography`)
- MLA 9th edition (`mla-9`)
- Harvard (`harvard`), using the user's institution guide when supplied
- Custom institution style (`custom`), requiring a guide, template, or explicit rules

If the task does not specify a style, ask once or use the workspace default and state it in `assignment_config.json`. Never assume that all Harvard variants are interchangeable.

## CSL-compatible intermediate record

Store one normalized object per work. Use CSL JSON names and types where possible:

```json
{
  "id": "src-001",
  "type": "article-journal",
  "title": "Article title",
  "author": [{"family": "Ng", "given": "Alex"}],
  "issued": {"date-parts": [[2025, 3, 1]]},
  "container-title": "Journal Title",
  "volume": "12",
  "issue": "2",
  "page": "101-120",
  "DOI": "10.xxxx/xxxxx",
  "URL": "https://example.org/item",
  "publisher": null,
  "publisher-place": null,
  "edition": null,
  "ISBN": null,
  "language": "en",
  "accessed": {"date-parts": [[2026, 7, 17]]},
  "original_material_type": "journal_article",
  "citation_eligibility": "allowed",
  "verification_status": "verified"
}
```

Use `null` for unknown optional fields; never invent values. Keep locators used for claims in `citation_ledger.csv`, not by altering the work-level page range.

## Style routing

### APA 7

Use author-date in-text citations. Include page or paragraph locator for quotations and where needed for precise claims. Render a `References` list; apply APA rules for capitalization, DOI URLs, author ordering, and repeated authors.

### Chicago author-date

Use parenthetical author-date citations with locators and a reference list. Preserve the distinction between publication year and access date.

### Chicago notes-bibliography

Use numbered notes and a bibliography. Maintain separate first-note and shortened-note forms. A parenthetical author-date string is not an acceptable substitute.

### MLA 9

Use author/page-style parenthetical references when appropriate and a `Works Cited` list. Model containers and nested containers explicitly rather than forcing author-date output.

### Harvard

Load the institution's Harvard guide before formatting. Record the selected variant and guide path or URL in citation configuration. If none is supplied, use a declared generic Harvard template and flag that institutional conformance is unverified.

### Custom

Extract rules from the provided guide into `citation_config.json`, including in-text or note pattern, bibliography order, capitalization, italics, punctuation, locator rules, and edge cases. If critical rules are missing, ask the user rather than guessing.

## Required configuration

```json
{
  "style_id": "apa-7",
  "variant": null,
  "locale": "en-US",
  "institution_guide": null,
  "bibliography_heading": "References",
  "include_doi_as_url": true
}
```

## Citation audit

Before delivery verify:

- every citation/footnote resolves to one allowed registry entry;
- every cited work appears in the bibliography when the selected style requires it, and every bibliography item is used unless the assignment requires a reading list;
- author, date, title, locator, DOI/URL, note numbering, and ordering agree with the source and selected style;
- quotations have exact locators;
- no prohibited or unverified source is cited; every cited slide has a recorded task/course permission, complete verified metadata, and an `allowed` registry status;
- formatting is internally consistent across the whole document.
