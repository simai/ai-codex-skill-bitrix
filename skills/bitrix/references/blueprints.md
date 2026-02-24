# Bitrix Blueprints

Use these blueprints as starting points. Adapt to repository conventions first.

## 1. Module Blueprint

Typical layout:

```text
local/modules/vendor.module/
  install/
    admin/
    index.php
    version.php
  lib/
    Service/
    Repository/
    Http/
  admin/
  lang/
  include.php
  options.php
```

Execution pattern:

1. Define module ID, namespace, and compatibility constraints.
2. Prepare install/uninstall and update flow with idempotent operations.
3. Keep admin entry logic in module admin files and publish thin proxies in `/bitrix/admin`.
4. Isolate domain logic in `lib/`.
5. Expose minimal integration points (events/services/CLI hooks).
6. Add migration/update notes for production rollout.

## 2. Component Blueprint

Typical layout:

```text
local/components/vendor/feature/
  class.php
  .description.php
  .parameters.php
  templates/.default/template.php
  templates/.default/style.css
  lang/
```

Execution pattern:

1. Define strict input parameters and output contract.
2. Keep logic in `class.php`, keep template mostly presentation-only.
3. Add cache strategy and invalidation points.
4. Validate compatibility with current template/composite behavior.

## 3. Integration Blueprint

Typical layout:

```text
local/lib/Integration/Partner/
  Client.php
  Mapper.php
  RetryPolicy.php
local/php_interface/init.php
```

Execution pattern:

1. Define API/data contract and error model.
2. Build transport client with timeout/retry controls.
3. Add idempotency guarantees for write operations.
4. Add structured logging and operator-readable error messages.
5. Define safe replay or compensation strategy.
6. Keep secrets in settings/environment, never hardcoded.

## 4. Existing Project Change Blueprint

Execution pattern:

1. Capture baseline behavior and failing scenario.
2. Identify minimal change surface in existing paths.
3. Preserve old contract unless acceptance criteria require breaking changes.
4. Add migration or compatibility layer when data model changes.
5. Validate with focused regression checks.

## 5. Update-by-Diff Blueprint

Execution pattern:

1. Build file list from commit/tag range.
2. Classify changes (code, install, db, lang, assets, config).
3. Determine schema/data impact and rollback complexity.
4. Prepare Migration Notes (always), Upgrade Notes, and changelog/release artifact.
5. Run smoke + regression minimum checks.

## 6. Admin Module Blueprint (Menu/List/Edit/Options)

Typical layout:

```text
local/modules/vendor.module/
  admin/
    menu.php
    vendor_entity_list.php
    vendor_entity_edit.php
  options.php
  lib/
    Repository/
    Service/
bitrix/admin/
  vendor_module_vendor_entity_list.php   # proxy only
  vendor_module_vendor_entity_edit.php   # proxy only
```

Execution pattern:

1. Register admin menu in `admin/menu.php` with rights-aware visibility.
2. Build list page with `CAdminList`/`CAdminUiList`, standard filter APIs, row and group actions.
3. Build edit/settings pages with `CAdminTabControl`/`CAdminForm`.
4. Keep `save/apply/delete` requests protected by `check_bitrix_sessid()`.
5. Use `CAdminMessage`/`BeginNote` for status and hints.
6. Keep long tasks in staged mode with PROGRESS messages.

## D7-First Guidance

- Prefer D7-compatible services and APIs.
- Minimize procedural code in `init.php`.
- Keep custom logic in namespaced classes under `local/`.
- Use explicit boundaries between domain, integration, and presentation layers.
- Keep localization in `lang/*` with `Loc::getMessage(...)`.

## Ready Templates

- Module installer baseline: `references/template-module-install-index.php.md`
- Box REST provider baseline: `references/template-rest-service-provider.php.md`
- Component baseline: `references/template-component-baseline.md`
- Component advanced (pagination + tag cache): `references/template-component-advanced-pagination-tagcache.md`
- Admin list starter (`CAdminList`): `references/template-admin-list-cadminlist.md`
- Admin edit starter (`CAdminTabControl`): `references/template-admin-edit-tabcontrol.md`
- Module options starter (`options.php`): `references/template-options-tabcontrol.md`
- IBlock repository/service starter: `references/template-iblock-repository-service.md`
- HL repository/service starter: `references/template-hlblock-repository-service.md`
- HL create migration starter: `references/template-migration-hlblock-create-updown.php.md`
- HL UF migration starter: `references/template-migration-hlblock-uf-updown.php.md`
- IBlock property migration starter: `references/template-migration-iblock-property-updown.php.md`
- Agents migration starter: `references/template-migration-agents-updown.php.md`
- Rollback notes starter: `references/template-migration-rollback-notes.md`
- REST capability bootstrap starter: `references/template-rest-capability-bootstrap.md`
- REST offline worker contract starter: `references/template-rest-offline-worker-contract.md`
- REST method-confirm handler starter: `references/template-rest-method-confirm-handler.md`
- Data-layer scaffolder script: `scripts/scaffold_data_layer.py`
- QA gate scaffolder script: `scripts/scaffold_qa_gate.py`
- Root test toolkit scaffolder script: `scripts/scaffold_root_tests.py`
- Unified QA runner script: `scripts/qa_run.py`
- Troubleshooting runbook: `references/troubleshooting.md`
- REST docs source triage: `references/bitrix24-rest-docs-triage.md`
- REST v3 migration guide: `references/bitrix24-rest-v3-migration.md`
- REST event lifecycle guide: `references/bitrix24-rest-event-lifecycle.md`
- REST domain quickstart: `references/bitrix24-rest-domain-quickstart.md`
- REST domain pack (CRM): `references/bitrix24-rest-domain-crm.md`
- REST domain pack (Tasks): `references/bitrix24-rest-domain-tasks.md`
- REST domain pack (User): `references/bitrix24-rest-domain-user.md`
- REST domain pack (Disk): `references/bitrix24-rest-domain-disk.md`
- REST artifact template (CRM): `references/template-rest-domain-crm-artifact-pack.md`
- REST artifact template (Tasks): `references/template-rest-domain-tasks-artifact-pack.md`
- REST artifact template (User): `references/template-rest-domain-user-artifact-pack.md`
- REST artifact template (Disk): `references/template-rest-domain-disk-artifact-pack.md`
- Scenario examples: `examples/new-module-site-management.md`, `examples/existing-project-fix.md`, `examples/bitrix24-cloud-rest-app.md`
- REST domain artifact examples: `examples/rest-domain-artifacts/README.md`
- Large-data seed pack: `examples/seeds/README.md`
- CI QA template: `examples/ci/github-actions-bitrix-qa.yml`
- CI REST artifacts template: `examples/ci/github-actions-bitrix-rest-artifacts.yml`
- CI REST + QA template: `examples/ci/github-actions-bitrix-rest-qa.yml`
- Detailed admin implementation patterns: `references/admin-ui-patterns-cookbook.md`
- IBlock/HL data and admin patterns: `references/iblock-hlblock-patterns.md`
