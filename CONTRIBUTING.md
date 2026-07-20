# Contributing

Thank you for contributing to Vibe Academic Writing.

## Before opening a pull request

- Keep the runtime skill concise and use progressive disclosure through `references/`.
- Preserve the standard `SKILL.md` frontmatter fields: `name` and `description` only.
- Add deterministic behavior to `scripts/` when repeated free-form execution would be fragile.
- Use synthetic data in tests and examples.
- Do not submit credentials, cookies, tokens, signed URLs, private course materials, real student work, personal information, or institution-specific confidential data.
- Do not add instructions that bypass access controls or academic-integrity rules.

## Test changes

Run:

```bash
python -B skills/develop-academic-paper/scripts/self_test.py
python -B -m unittest discover -s tests -v
```

Update tests when changing artifact schemas, safety rules, synchronization behavior, or citation policy. A behavior change should also be recorded in `CHANGELOG.md`.

## Pull requests

Keep pull requests focused. Explain the user problem, behavioral change, safety impact, and validation performed. Platform compatibility claims require a reproducible test on that platform.

By contributing, you agree that your contribution is licensed under the MIT License.
