# Changelog

All notable changes to this repository are documented in this file.

## [v1.1.0] - 2026-02-22

### Added

- Bitrix skill structure in `skills/bitrix/` with references, templates, and helper scripts.
- Root-level test toolkit scaffolder `skills/bitrix/scripts/scaffold_root_tests.py`.
- QA gate scaffolder `skills/bitrix/scripts/scaffold_qa_gate.py`.
- Unified QA runner `skills/bitrix/scripts/qa_run.py`.
- New QA artifacts in reports:
  - auto A-I summary table (`PASS/FAIL/N-A`, evidence, risk, concrete fix)
  - risk-sorted fix backlog (`High`, `Medium`, `Low`).
- CI workflow example with QA report artifact publishing:
  - `.github/workflows/bitrix-qa-example.yml`
  - `skills/bitrix/examples/ci/github-actions-bitrix-qa.yml`.
- Scenario examples:
  - `skills/bitrix/examples/new-module-site-management.md`
  - `skills/bitrix/examples/existing-project-fix.md`
  - `skills/bitrix/examples/bitrix24-cloud-rest-app.md`.
- Large dataset seed pack for UX/perf checks:
  - `skills/bitrix/examples/seeds/mysql_large_list_seed.sql`
  - `skills/bitrix/examples/seeds/mysql_large_list_cleanup.sql`
  - `skills/bitrix/examples/seeds/seed_iblock_employees.php`
  - `skills/bitrix/examples/seeds/seed_hlblock_employees.php`
  - `skills/bitrix/examples/seeds/README.md`.
- Troubleshooting runbook:
  - `skills/bitrix/references/troubleshooting.md`.

### Changed

- Root `README.md` now documents install, scaffold commands, unified QA run, CI examples, and seed usage.
- `skills/bitrix/SKILL.md` and QA-related references updated to include v1.1 workflows and examples.
