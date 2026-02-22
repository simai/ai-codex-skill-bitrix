# Testing and QA Runbook

Apply for pre-release validation, post-change checks, and QA-focused tasks.

For strict quality gate (A-I sections and static->dynamic order), also apply:

- `references/qa-gate-checklist.md`
- `references/template-qa-audit-prompt.md`
- `references/root-testing-toolkit.md`
- `references/troubleshooting.md`
- `scripts/scaffold_qa_gate.py`
- `scripts/scaffold_root_tests.py`
- `scripts/qa_run.py`
- `examples/seeds/README.md`

## Result Model

For each major area, record:

- Status: `PASS`, `FAIL`, `N-A`, or `NEEDS RUN`
- Evidence: command/log/screenshot/SQL (sanitized)
- Risk: `Low`, `Medium`, or `High`
- Recommendation: short corrective action

Execution order:

1. Static audit first (`rg`, code search, config inspection).
2. Dynamic validation second (admin UI, CLI, integration runtime).
3. Report and fix backlog sorted by risk.

## Minimum Smoke Checks

- Install/update flow works without critical errors.
- Admin pages/settings open and save correctly.
- Primary business happy-path works end to end.
- Permission checks and CSRF checks are intact.
- No critical PHP/runtime errors in logs.

## Regression Minimum

- Critical scenario set passes (happy-path and negative cases).
- Access boundaries remain intact.
- Migration/update side effects are verified.
- Cache behavior remains correct for affected flows.
- Rollback steps are validated for risky updates.

## Security and Reliability Checks

- Input validation and output escaping are in place.
- No silent failures without logging.
- Idempotency is preserved for repeated update/operation runs.
- Concurrency-sensitive operations are evaluated when relevant.

## Evidence Collection

- Sanitized command outputs.
- Screenshots for admin/UI failures.
- SQL checks for data invariants.
- File list for touched areas and related risks.

## QA Deliverables

- QA Report (`references/template-qa-report.md`)
- Risk-ranked finding list
- Re-test plan

## Automation Command

Single run (static shell audit + phpunit static + phpunit integration + one report):

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/bitrix-project" \
  --module-id "vendor.module" \
  --bitrix-root "/absolute/path/to/site"
```

Notes:

- If `BITRIX_ROOT`/`--bitrix-root` is missing, integration is marked `N-A`.
- If `qa-static-audit.sh` is available in project root, it is executed before PHPUnit.
- Report is saved by default to `tests/qa-run-report-YYYYMMDD-HHMMSS.md`.
- Report includes auto `A-I` summary table (`PASS/FAIL/N-A`, evidence, risk, concrete fix).
- Report includes risk-sorted fix backlog (`High`, `Medium`, `Low`) for all `FAIL` areas.

## CI Example

- Root workflow example: `.github/workflows/bitrix-qa-example.yml`
- Reusable project template: `examples/ci/github-actions-bitrix-qa.yml`
- CI must upload markdown QA report as artifact.

## Large Data QA

For UX/performance checks on big lists use seed pack:

- `examples/seeds/mysql_large_list_seed.sql`
- `examples/seeds/seed_iblock_employees.php`
- `examples/seeds/seed_hlblock_employees.php`
