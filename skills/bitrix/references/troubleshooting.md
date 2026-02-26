# Troubleshooting

Use this runbook for common failures in module development and QA pipeline.

## 1) `BITRIX_ROOT is not set`

Symptoms:

- `PHPUnit Integration Suite` is `N-A` in `qa_run.py` report.
- Integration tests are skipped.

Fix:

```bash
BITRIX_ROOT="/absolute/path/to/site" \
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module"
```

Checks:

- `BITRIX_ROOT/bitrix/modules/main/include/prolog_before.php` exists.
- path is absolute and accessible.

## 2) `phpunit executable not found`

Symptoms:

- Static/integration suites become `N-A`.

Fix:

```bash
cd /path/to/project
composer install
```

Alternative:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --phpunit-bin "/custom/path/phpunit"
```

## 3) `Required module is not installed: <module>`

Symptoms:

- Integration checks fail/skip at bootstrap with message about missing required module.

Fix options:

1. Install the missing module in target Bitrix environment.
2. If module is optional for current release scope, remove it from `BITRIX_REQUIRED_MODULES` and document this constraint in QA report.
3. Keep base integration test dependent only on target module (`BITRIX_MODULE_ID`) and avoid hardcoded dependencies.

## 4) `Module is not installed: vendor.module`

Symptoms:

- Integration suite is skipped/fails before scenarios.

Fix:

- Install module in target environment before integration run.
- Verify module ID in command/env (`BITRIX_MODULE_ID`).

## 5) CSRF/rights failures in admin pages

Symptoms:

- Save/apply/delete actions fail.
- Admin actions are available to unauthorized roles.

Fix checklist:

- Add `check_bitrix_sessid()` for state-changing actions.
- Validate rights before rendering/processing actions.
- Ensure admin pages use proper prolog/epilog wrappers.

## 6) Slow admin lists on large data

Symptoms:

- list/filter/pagination lag with 10k+ rows.

Fix checklist:

- Add DB indexes for frequent filter/sort columns.
- Move heavy operations to batch/chunk mode.
- Enable safe cache strategy with explicit invalidation.
- Use seed datasets from `skills/bitrix/examples/seeds/` to reproduce.

## 7) Root test toolkit not generated

Symptoms:

- no `tests/`, no `phpunit.xml.dist`, no static suite.

Fix:

```bash
python3 skills/bitrix/scripts/scaffold_root_tests.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module"
```

Then rerun:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module"
```
