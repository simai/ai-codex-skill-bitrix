# Changelog

All notable changes to this repository are documented in this file.

## [v1.2.0] - 2026-02-24

### Added

- REST documentation triage and lifecycle references:
  - `skills/bitrix/references/bitrix24-rest-docs-triage.md`
  - `skills/bitrix/references/bitrix24-rest-v3-migration.md`
  - `skills/bitrix/references/bitrix24-rest-event-lifecycle.md`
  - `skills/bitrix/references/bitrix24-rest-domain-quickstart.md`
- Domain-specific REST packs:
  - `skills/bitrix/references/bitrix24-rest-domain-crm.md`
  - `skills/bitrix/references/bitrix24-rest-domain-tasks.md`
  - `skills/bitrix/references/bitrix24-rest-domain-user.md`
  - `skills/bitrix/references/bitrix24-rest-domain-disk.md`
- New REST templates:
  - `skills/bitrix/references/template-rest-capability-bootstrap.md`
  - `skills/bitrix/references/template-rest-offline-worker-contract.md`
  - `skills/bitrix/references/template-rest-method-confirm-handler.md`
  - `skills/bitrix/references/template-rest-domain-crm-artifact-pack.md`
  - `skills/bitrix/references/template-rest-domain-tasks-artifact-pack.md`
  - `skills/bitrix/references/template-rest-domain-user-artifact-pack.md`
  - `skills/bitrix/references/template-rest-domain-disk-artifact-pack.md`
- Filled example artifacts for domain mode:
  - `skills/bitrix/examples/rest-domain-artifacts/README.md`
  - `skills/bitrix/examples/rest-domain-artifacts/crm.md`
  - `skills/bitrix/examples/rest-domain-artifacts/tasks.md`
  - `skills/bitrix/examples/rest-domain-artifacts/user.md`
  - `skills/bitrix/examples/rest-domain-artifacts/disk.md`
- REST artifact CI examples:
  - `.github/workflows/bitrix-rest-artifacts-example.yml`
  - `skills/bitrix/examples/ci/github-actions-bitrix-rest-artifacts.yml`
- Combined REST + QA CI examples:
  - `.github/workflows/bitrix-rest-qa-example.yml`
  - `skills/bitrix/examples/ci/github-actions-bitrix-rest-qa.yml`

### Changed

- `skills/bitrix/scripts/scaffold_artifacts.py` now supports REST presets:
  - `rest_crm`, `rest_tasks`, `rest_user`, `rest_disk`, `rest_all`
- `skills/bitrix/SKILL.md`, `work-modes.md`, `blueprints.md`, `testing-qa.md`, and `qa-gate-checklist.md` were extended with REST domain routing and QA guidance.
- Root `README.md` was updated with REST domain quickstart paths and new artifact scaffold commands.

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
