# Final delivery

Use this workflow only after content review and all blocking validation gates pass.

1. If the assignment already mandates a file format, use it and confirm any ambiguity. Otherwise ask the user to choose Word, PDF, or both.
2. Create `<task-name>_result` inside the current single-task or course-assignment directory only after the choice is known. Sanitize unsafe filesystem characters and preserve the display name in metadata.
3. Keep working Markdown, source records, and review artifacts in their internal directories. Put only user-facing deliverables and a concise validation record in the result folder.
4. Generate `.docx` with the document workflow and PDF with the PDF workflow. When both are requested, render from the same approved content and keep citations, headings, page elements, and references consistent.
5. Render and visually inspect every generated format. Check opening, pagination, headings, tables, figures, footnotes or endnotes, reference list, page numbers, and required template elements.
6. Do not mark delivery complete until the selected files exist, are nonempty, and pass validation. Preserve prior result versions on rerun.

Ask about format earlier only when a supplied template, page-count rule, or layout requirement affects writing and planning.
