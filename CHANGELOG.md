# Changelog

This file and the Git tags version the repository as a container: the front matter schema, the decision families, the validator, the templates, and the tooling. Decisions carry their own versions in front matter and never move the repository version. A new or revised decision is recorded in its own file and in the Git history.

- **Minor bump (0.X.0):** a change contributors feel: a new or changed front matter key, a new decision family, a new validator rule, a template change.
- **Patch bump (0.X.Y):** fixes to the above.

To cite a decision, use its ID and version, for example "WAX-0006 v1.0". To pin the whole record at a moment, use a commit permalink or a dated snapshot tag. A consolidated single-document rendering can be generated from any commit; the repository, not the rendering, is authoritative.

## v0.1.0 (2026-08-30)

- Initial public release: 52 decisions, each in its own file with front matter, a stable ID (SHARED, WAX, HIVE, MOD-PURCHASE, MOD-UNSECURED), and its own version.
- INDEX.md, PRINCIPLES.md, OPEN-QUESTIONS.md, START-HERE.md, CONTRIBUTING.md, GOVERNANCE.md, AGENTS.md, the contributor onboarding skill, issue and pull request templates, continuous integration validation, and licensing.
