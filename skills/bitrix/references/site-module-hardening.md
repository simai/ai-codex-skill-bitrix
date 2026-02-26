# Site Module Hardening (Site Management / Box)

Apply this checklist for filesystem module/component tasks (`local/modules`, `local/components`, public pages).

Goal:

- prevent installer/runtime regressions that usually appear only after install/uninstall/reinstall;
- keep visual editor compatibility for component parameters;
- keep cleanup behavior deterministic on real servers.

## Mandatory Preflight for Module/Component Tasks

### 1) Installer DB batch compatibility

- Do not assume `Application::getConnection()->runSqlBatch()` exists in every core build.
- Use compatibility wrapper:
  - first try `Application::getConnection()->runSqlBatch(...)`;
  - fallback to global `$DB->RunSQLBatch(...)`.

Acceptance:

- install/uninstall SQL batch runs without fatal on MySQL cores using `MysqliConnection`.

### 2) Visual editor safe component call

- If component parameters must be editable via visual editor, do not pass main params as runtime variable in public page:
  - avoid `IncludeComponent(..., $componentParams, ...)` for editable page files.
- Prefer literal array in page source that Bitrix parser can read.
- If params depend on selected site/folder, generate final public `index.php` during installation with resolved literal params.

Acceptance:

- component settings dialog opens;
- current values are prefilled;
- iblock type and iblock lists are available.

### 3) Public folder ownership and safe cleanup

- Mark installed public folders with module marker file (ownership metadata).
- Remove public folders only if they were installed by module (marker/option ownership check).
- For shared folders (for example `simai.data`), install only when missing and remove only when installed by module.

Acceptance:

- uninstall with `remove_public=Y` removes only module-owned public files;
- existing user/project folders are not deleted.

### 4) Component folder cleanup robustness

- `DeleteDirFiles(...)` alone may leave residue (for example `.DS_Store`, local temp files).
- For copied component directories use explicit `DeleteDirFilesEx(...)` for target path.
- Keep backward cleanup for old package names if module was renamed.

Acceptance:

- after uninstall no stale component folders remain under `/bitrix/components/<vendor>/...`.

### 5) Module path compatibility (`local/modules` and `bitrix/modules`)

- Admin proxy files and runtime includes must support both module locations.
- Avoid hardcoded single-root assumptions.

Acceptance:

- admin pages/settings work when module is installed from either path.

### 6) Multi-site iblock code isolation

- For per-site data, generate iblock type/code using site code convention.
- Resolve all demo/public component bindings to selected site code during installation.

Acceptance:

- installation on different sites does not mix iblock types/codes;
- component parameters point to selected site data.

### 7) Parameter hygiene

- Remove legacy/irrelevant component params from `.parameters.php` when feature was removed.
- Keep parameter groups aligned with current implementation only.

Acceptance:

- no obsolete fields in component settings;
- no empty artifacts from deprecated integrations.

## QA Evidence Snippets

Use these checks in addition to generic QA gate:

```bash
# 1) detect variable params in editable public pages
rg -n "IncludeComponent\\(.+\\$[A-Za-z_][A-Za-z0-9_]*" /path/to/site/map /path/to/site

# 2) verify uninstall hard cleanup for component folders
rg -n "DeleteDirFilesEx\\(\"/bitrix/components/" local/modules/<module_id>/install/index.php

# 3) verify marker-based ownership checks
rg -n "marker|managed|simai_data_installed|public_url|public_folder" local/modules/<module_id>/install/index.php
```

Parser-level check (optional):

```php
$component = PHPParser::FindComponent("vendor:component", $source, $line);
// Expected: is_array($component["DATA"]["PARAMS"]) === true
```

## Release Gate Add-on

Before release of module/public data updates:

1. Clean install on empty site.
2. Reinstall on same site.
3. Uninstall with/without data removal flags.
4. Verify public folder and component directory residue.
5. Open component parameters in visual editor and verify prefilled values.
