# IBlock and Highloadblock Patterns

Use this reference when a task touches:

- iblock data structures and admin pages
- highloadblock entities/rows/rights
- employee-like registries with filters and tab forms
- module settings and admin UX tied to iblock/HL data

This file is designed for both new modules and safe refactoring in existing projects.

## 1) Selection Heuristic: IBlock vs HL Block

Use `IBlock` when:

- content tree/sections are required
- public components and standard content workflows are required
- rich property model and catalog-like semantics are needed

Use `Highloadblock` when:

- flat/high-volume registries are required
- entity is mostly tabular and admin-list driven
- UF-driven schema is enough and faster to evolve for service data

Hybrid approach:

- keep publishable content in iblock
- keep operational registries/mappings/state in HL block

## 2) Module Structure for Data + Admin

```text
local/modules/<vendor.module>/
  lib/
    Iblock/
      <Entity>Repository.php
      <Entity>Service.php
    Hl/
      <Entity>Repository.php
      <Entity>Service.php
  admin/
    <entity>_list.php
    <entity>_edit.php
  install/
    db/mysql/install.sql
    db/mysql/uninstall.sql
```

Principles:

- Keep admin controllers thin (request, permissions, output).
- Keep data operations in `lib/*Repository` or `lib/*Service`.
- Keep install/uninstall and migrations idempotent.

## 3) Highloadblock Data Pattern

### 3.1 Runtime entity bootstrap

```php
$hlblock = \Bitrix\Highloadblock\HighloadBlockTable::getById($entityId)->fetch();
$entity = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
$dataClass = $entity->getDataClass();
```

Use this once per request; pass `$dataClass` into services/repositories.

### 3.2 Rights

For non-admin users, resolve operations:

- `hl_element_read`
- `hl_element_write`
- `hl_element_delete`

Pattern:

```php
$ops = \Bitrix\Highloadblock\HighloadBlockRightsTable::getOperationsName($entityId);
$canEdit = in_array('hl_element_write', $ops, true);
$canDelete = in_array('hl_element_delete', $ops, true);
```

Do not allow destructive actions without rights + `check_bitrix_sessid()`.

### 3.3 Localization and rights persistence

HL metadata often needs:

- `HighloadBlockLangTable` for localized entity names
- `HighloadBlockRightsTable` for per-code access

Safe save strategy:

1. Update/add HL entity.
2. Replace lang rows deterministically.
3. Upsert rights.
4. Delete stale rights not present in submitted payload.

### 3.4 UF fields in HL list/edit pages

Must-use APIs:

- list headers: `AdminListAddHeaders(...)`
- list filters: `AdminListAddFilterFields(...)`, `AdminListAddFilter(...)`
- row rendering: `AddUserFields(...)`
- edit form input extraction: `EditFormAddFields(...)`
- tab rendering: `ShowUserFieldsWithReadyData(...)`

This is the core pattern that keeps custom HL fields stable across list/edit pages.

### 3.5 Copy semantics for file UF

In "copy" flow, clear file UF values before save to avoid linking source file payload unexpectedly.

## 4) IBlock Data Pattern

### 4.1 Service boundary

Separate concerns:

- read model (list/search/filter)
- write model (create/update/deactivate/delete)
- side effects (agents/events/cache invalidation)

Do not mix all of this directly in admin page files.

### 4.2 Options and automation coupling

Iblock option pages frequently control runtime behavior (example: activity-date check agents).

When option changes affect background jobs:

1. Diff old/new selected entities.
2. Remove obsolete agents.
3. Add new agents.
4. Persist option values.
5. Redirect after save.

### 4.3 Properties and complex form fields

For section/element edit pages, use custom tab fields:

- `BeginCustomField(...)`
- `EndCustomField(...)`

Use this for:

- property widgets
- media selectors
- SEO templates
- section-property mapping tables

### 4.4 Import/export long tasks

Prefer staged execution (`DoNext(...)`) and show status via:

- `CAdminMessage::ShowMessage(['TYPE' => 'PROGRESS', ...])`
- progressive step details and optional bar values

This is the standard admin-safe UX for long iblock operations.

## 5) Employee/Registry Admin Pattern

For employee-like lists with filters and mass actions:

- prefer `CAdminUiList` + rich filter schema
- keep explicit header definition
- keep row actions explicit
- keep bulk actions in `AddGroupActionTable`
- keep "create" in context menu only

Apply this whether data lives in `b_user`, iblock elements, or HL rows.

## 6) Caching and Consistency Pattern

General:

- define cache keys by filter + sort + page + language + rights context
- separate short-lived list cache from long-lived dictionary cache
- invalidate on writes deterministically

For component-facing iblock data:

- use tagged cache and include iblock tag when appropriate

For HL data:

- invalidate repository cache on add/update/delete and group operations
- avoid stale results after bulk actions

## 7) Transactions, Errors, and Rollback

For batch/admin actions:

1. Validate input and rights first.
2. Start transaction for multi-step write operations.
3. On failure: rollback and collect meaningful error details.
4. Return admin message and preserve submitted values for retry.

Do not partially apply writes without explicit compensation path.

## 8) Migration and Install/Update Safety

When iblock/HL schema is changed:

- document migration in update artifacts
- implement idempotent migration steps
- include downgrade/rollback notes (even if rollback is "forward fix only")
- keep uninstall behavior explicit (`savedata=Y` vs full cleanup)

Never hide destructive data changes behind implicit "save options" actions.

## 9) Anti-Patterns

- Query logic duplicated across admin pages instead of repository/service.
- Direct raw SQL in page controllers for regular CRUD.
- Rights checks only in UI layer, not in write handlers.
- No diff logic when options control agents/scheduled processes.
- Ignoring UF APIs and handcrafting UF handling.
- Missing session validation for list group actions.

## 10) Quick Delivery Checklist

1. Chosen model (`iblock` or `HL`) matches data shape and UX.
2. Data access is isolated in service/repository classes.
3. Admin list and edit pages use standard Bitrix admin APIs.
4. Rights are checked for view/edit/delete paths.
5. Session checks exist for all state-changing actions.
6. Cache invalidation rules are explicit.
7. Migration/install/uninstall behavior is documented and idempotent.
8. User-facing errors/messages are clear and localized.

## Source Anchors Used

- `/bitrix/modules/highloadblock/admin/highloadblock_rows_list.php`
- `/bitrix/modules/highloadblock/admin/highloadblock_row_edit.php`
- `/bitrix/modules/highloadblock/admin/highloadblock_entity_edit.php`
- `/bitrix/modules/iblock/options.php`
- `/bitrix/modules/iblock/admin/iblock_section_edit.php`
- `/bitrix/modules/iblock/admin/iblock_element_edit.php`
- `/bitrix/modules/iblock/admin/iblock_xml_import.php`
- `/bitrix/modules/iblock/admin/iblock_xml_export.php`
- `/bitrix/modules/main/admin/user_admin.php`

## Ready Templates

- `references/template-iblock-repository-service.md`
- `references/template-hlblock-repository-service.md`
- `references/template-migration-hlblock-create-updown.php.md`
- `references/template-migration-hlblock-uf-updown.php.md`
- `references/template-migration-iblock-property-updown.php.md`
- `references/template-migration-agents-updown.php.md`
- `references/template-migration-rollback-notes.md`
- `scripts/scaffold_data_layer.py`
