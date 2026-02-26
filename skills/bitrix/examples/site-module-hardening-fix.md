# Example: Site Module Hardening Fix (Install/Uninstall + Public Page)

Use when module has public page, demo data, and copied components in Site Management/Bitrix24 box.

## Input profile

- Platform: Site Management or Bitrix24 box
- Task: fix/regression hardening
- Project state: existing module with `install/index.php` and public install files

## Recommended flow

1. Apply `references/site-module-hardening.md` preflight.
2. Fix installer SQL batch compatibility (`runSqlBatch` wrapper with `$DB->RunSQLBatch` fallback).
3. Make public component page parser-friendly for visual editor:
   - generate resolved literal params in installed page;
   - avoid runtime variable-only params in editable page source.
4. Add marker-based ownership checks for public/shared folders.
5. Add explicit `DeleteDirFilesEx` for copied component folders on uninstall.
6. Validate fresh install -> uninstall -> reinstall on clean and non-clean targets.

## Verification samples

```bash
# Visual editor parser readiness
php -r 'require "bitrix/modules/main/classes/general/php_parser.php"; /* parse component params */'

# Residue check after uninstall
find /path/to/site/bitrix/components/<vendor> -maxdepth 1 -type d

# Marker-based cleanup checks
rg -n "marker|managed|DeleteDirFilesEx|public_url|simai_data_installed" local/modules/<module_id>/install/index.php
```

## Expected deliverables

- Focused patch list for installer/public page/component cleanup.
- Regression checklist for install/uninstall/reinstall.
- QA report with evidence for parser compatibility and filesystem cleanup.
