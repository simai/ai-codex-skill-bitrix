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

## 8) Bitrix24 box in Docker: module works on host, but classes are not found in container

Symptoms:

- Public pages show errors like `Class "Vendor\\Module\\..." not found`.
- `Loader::includeModule('vendor.module')` behaves inconsistently.
- Host path has module files, but container path `/opt/www/local/modules/vendor.module` is missing or stale.

Typical root cause:

- Module was linked via host symlink inside `www/local/modules`, but target is not visible from container mount namespace.
- Nested bind mount did not apply because target path existed as symlink during container start.

Fix checklist:

1. Prefer explicit `docker-compose` bind mounts for module path:
   - `<repo>/local/modules/vendor.module:/opt/www/local/modules/vendor.module`
   - apply for at least `php`, and also `nginx`/`cron` when needed.
2. Ensure target path is not a symlink before recreation (`rm -rf www/local/modules/vendor.module`).
3. Recreate containers (`docker compose up -d --force-recreate php nginx cron`).
4. Verify mount inside container:
   - check `/proc/self/mountinfo` contains `/opt/www/local/modules/vendor.module`,
   - verify `/opt/www/local/modules/vendor.module/include.php` exists.

## 9) Open Lines test dialog does not appear or widget page says chat cannot be loaded

Symptoms:

- Public widget page like `/online/<code>` opens, but browser shows chat load failure.
- Module dialog picker returns empty list despite existing line configuration.
- Direct DB inserts into `b_imopenlines_session` do not produce usable test dialogs.

Typical root causes:

- Mixed-content or wrong widget endpoint scheme (`http` under `https` page).
- No real livechat session was created yet.
- Attempt to fake OL session only at DB level without IM chat/runtime side effects.

Fix checklist:

1. Check browser console/network for mixed-content and blocked widget requests.
2. Fix portal/widget URL configuration so public widget loads over the same scheme as the page.
3. Create a real test dialog through public widget by sending a message, not by DB insert.
4. If CLI generation is needed, use supported `imopenlines` runtime APIs to register visitor/dialog and restart session; do not seed only session tables manually.

Verification:

- `b_imopenlines_session` gets real rows,
- related IM chat exists,
- module picker sees `livechat` sessions,
- task-card action can bind/open the dialog.
