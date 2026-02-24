---
name: bitrix
description: Build, refactor, test, and release solutions for 1C-Bitrix Site Management, Bitrix24 box, and Bitrix24 cloud. Use for module/component/integration development, project fixes, update planning by diff or commits, migrations and rollback design, marketplace packaging, admin UI implementation, QA/regression checklists, and Bitrix release artifacts. For Bitrix24 cloud, use this skill in REST-app integration mode only (webhook/OAuth/scopes/events), not filesystem module/component development.
---

# Bitrix

Use this skill to turn incomplete or detailed requests into safe, production-ready Bitrix implementation and release outputs.

## Platform Scope Matrix

- `1C-Bitrix Site Management`: full development scope (`module`, `component`, `integration`, `update`, `QA`, `release`).
- `Bitrix24 box`: full development scope (`module`, `integration`, `REST apps`, `update`, `QA`, `release`).
- `Bitrix24 cloud`: REST-app integration scope only (`webhook`, `oauth`, `scopes`, `events`, `marketplace app flows`, `QA/release artifacts`).

For `Bitrix24 cloud`, do not propose filesystem module/component implementation paths like `local/modules` or `local/components`.

## Workflow

1. Identify work mode via `references/work-modes.md`.
2. Validate input completeness via `references/intake.md`.
3. Filter incoming data with `references/data-triage.md`.
4. Apply module and architecture contract from `references/module-contract.md`.
5. Apply implementation blueprint from `references/blueprints.md`.
   - when user provides full Bitrix24 box source, apply extraction workflow from `references/bitrix24-box-source-analysis.md`.
6. Apply mode-specific standards:
   - admin UI (baseline): `references/admin-ui.md`
   - admin UI strict/blocker rules and skeletons: `references/admin-ui-strict-rules.md`
   - admin UI implementation cookbook (menus/options/lists/tabs/notes/progress/dialogs): `references/admin-ui-patterns-cookbook.md`
   - iblock/highloadblock architecture and admin data patterns: `references/iblock-hlblock-patterns.md`
   - Bitrix24 REST integrations: `references/bitrix24-rest-integration.md`
   - Bitrix24 REST source triage policy: `references/bitrix24-rest-docs-triage.md`
   - Bitrix24 REST v3 migration boundaries: `references/bitrix24-rest-v3-migration.md`
   - Bitrix24 REST event lifecycle contract: `references/bitrix24-rest-event-lifecycle.md`
   - Bitrix24 REST domain pack (CRM): `references/bitrix24-rest-domain-crm.md`
   - Bitrix24 REST domain pack (Tasks): `references/bitrix24-rest-domain-tasks.md`
   - Bitrix24 REST domain pack (User): `references/bitrix24-rest-domain-user.md`
   - Bitrix24 REST domain pack (Disk): `references/bitrix24-rest-domain-disk.md`
   - Bitrix24 REST domain quickstart: `references/bitrix24-rest-domain-quickstart.md`
   - Bitrix24 REST domain artifact templates: `references/template-rest-domain-*-artifact-pack.md`
   - Bitrix24 marketplace publication/moderation: `references/bitrix24-marketplace-publication.md`
   - updates/releases: `references/update-and-release.md`
   - testing/QA: `references/testing-qa.md`
   - troubleshooting: `references/troubleshooting.md`
7. Run `references/release-checklist.md` before finalizing.

## Input Handling

Collect minimum context before code changes:

- Bitrix platform: `1C-Bitrix Site Management`, `Bitrix24 box`, or `Bitrix24 cloud`.
- Codebase mode: `new` or `existing`.
- Target artifact: `module`, `component`, `integration`, `feature`, `bug fix`, or `optimization`.
- Runtime constraints: PHP version, DB engine/version, deployment model, and CI/CD rules.
- Non-functional constraints: security, performance, caching, backward compatibility.
- Acceptance criteria: definition of done, test scenario, and delivery format.
- Update scope (if relevant): commit range/tag range or changed file list.

If critical data is missing, ask only the shortest set of questions required to unblock implementation.

## Default Baseline

Use these defaults unless user explicitly overrides:

- Runtime (`Site Management` and `Bitrix24 box`): `PHP 8+`.
- Database (`Site Management` and `Bitrix24 box`): `MySQL 8+`.
- Project state: `new` or `existing` (both valid; do not assume one).
- Task classes: `module`, `component`, `integration`, `dorabotka/feature`, `fix`.
- Cloud class subset: `integration` and `REST app` flows only.

If definition of done is missing, derive a temporary done contract:

1. Primary scenario works end to end.
2. No regressions in touched flow.
3. Migration/deploy steps are explicit.
4. Risks and rollback are documented.

## Non-Negotiables

- Keep custom code in `local/` unless repository standards define another path.
- Prefer D7 APIs, namespaced classes, and explicit service boundaries.
- Avoid direct core modifications in `/bitrix` unless the project already depends on patching and user approval is explicit.
- In `Bitrix24 cloud` mode, avoid filesystem code paths and use REST-app patterns only.
- Load modules explicitly before usage (`Loader::includeModule(...)`).
- Guard admin entry points with admin prolog/epilog and permission checks before output.
- Keep localization in `lang/` and message access through `Loc::getMessage(...)`.
- Handle schema/content changes as versioned updates via install/update scripts or project migration tooling.
- Keep business logic out of templates; move logic into services or module classes.
- For integrations, define idempotency, retries, and failure handling before coding.
- For Bitrix24 REST event handlers, validate source and secret context (`application_token` checks for app events).
- Keep webhook and OAuth secrets out of repository and frontend runtime payloads.
- For risky refactors, preserve backward compatibility through adapters, feature flags, or phased rollout.

## Practical Patterns: `bitrix:lists` in Bitrix24 Air

- For Bitrix24 Air header actions, prefer `\Bitrix\UI\Toolbar\Facade\Toolbar::addButton(...)` over ad-hoc markup in view targets.
- If you use `inside_pagetitle`, ensure page body class includes `pagetitle-toolbar-field-view`; without it controls can disappear.
- In custom `bitrix:lists` templates, `list_element_edit.php` often orchestrates both view-mode and edit-mode routing; verify this file first.
- In edit flow, pass `LIST_URL` as the real list route from `URL_TEMPLATES["list"]` with `#list_id#` / `#section_id#` replacements; do not reuse current page with `?element_just_view=y`.
- For edit visibility, combine list permission and element right checks:
  - `CListPermissions::CheckAccess(...) >= CListPermissions::CAN_WRITE`
  - `CIBlockElementRights::UserHasRightTo(..., "element_edit")`
- When actions are duplicated, check both `page__toolbar` and `page__actions`; remove fallback rendering from `below_pagetitle` if toolbar already renders buttons.
- After live template fixes, clear `bitrix/cache`, `bitrix/managed_cache`, `bitrix/stack_cache`, and `bitrix/html_pages`.
- If `patch` tooling was used, remove `*.orig` artifacts before commit.

## Artifact Contract

Use mode-specific outputs from `references/work-modes.md` and templates from `references/template-*.md`.

Required baseline for substantial tasks:

1. Plan.
2. Patch list (or changed file plan).
3. Checklist (mode-specific).
4. Verification and regression steps.
5. Risks and rollback notes.

Additional required artifacts:

- Update or data-impact task: `Migration Notes` is mandatory (use explicit "No changes" when applicable).
- Update/release task: `Upgrade Notes` plus `Release Notes` or `Changelog Fragment`.
- Testing task: `QA Report`.
- Marketplace packaging task: `Moderator Precheck Notes`.
- Documentation task: updated docs map (what docs changed and why).

You may scaffold artifact files with:

- `scripts/scaffold_artifacts.py --out <dir> --preset update|release|marketplace|qa|rest_crm|rest_tasks|rest_user|rest_disk|rest_all|full [--overwrite]`
- `scripts/scaffold_module_admin.py --project-root <repo> --module-id <vendor.module> --entity <entity_code> [--namespace Vendor\\Module] [--overwrite]`
- `scripts/scaffold_data_layer.py --project-root <repo> --module-id <vendor.module> --entity <entity_code> --storage iblock|hlblock|both [--namespace Vendor\\Module] [--iblock-id 10] [--hl-id 12] [--overwrite]`
- `scripts/scaffold_qa_gate.py --out <dir> --module-id <vendor.module> [--module-path local/modules/<vendor.module>] [--version 1.2.3] [--environment stage] [--overwrite]`
- `scripts/scaffold_root_tests.py --project-root <repo> --module-id <vendor.module> [--force-bitrix] [--overwrite]`
- `scripts/qa_run.py --project-root <repo> --module-id <vendor.module> [--bitrix-root /abs/path] [--report tests/qa-run-report.md] [--skip-integration]`

## References

- `references/project-profile.md`: fixed baseline constraints for this skill instance.
- `references/work-modes.md`: mode routing and required outputs.
- `references/intake.md`: required context and targeted question set.
- `references/data-triage.md`: rules for deciding what data is required, optional, or ignorable.
- `references/module-contract.md`: module structure, install/uninstall, proxy, versioning, data safety rules.
- `references/blueprints.md`: baseline folder structures and execution patterns.
- `references/bitrix24-box-source-analysis.md`: workflow for extracting reusable rules from full Bitrix24 box source.
- `references/admin-ui.md`: standards for admin forms, lists, dialogs, and proxy files.
- `references/admin-ui-strict-rules.md`: blocker-level admin UI contract with strict MUST/MUST NOT rules.
- `references/admin-ui-patterns-cookbook.md`: detailed build patterns for menu, options page, list/filter tables, tab forms, context menus, notes, notifications, progress bars, and dialogs.
- `references/iblock-hlblock-patterns.md`: practical architecture and implementation patterns for iblock/highloadblock data and admin UX.
- `references/bitrix24-rest-integration.md`: auth/scopes/events/performance rules for Bitrix24 REST.
- `references/bitrix24-rest-docs-triage.md`: source-quality triage for large Bitrix24 REST docs dumps (stable/caution/deprecated).
- `references/bitrix24-rest-v3-migration.md`: v2/v3/hybrid routing and phased migration contract for REST integrations.
- `references/bitrix24-rest-event-lifecycle.md`: install/update/runtime/uninstall lifecycle for event-driven REST apps.
- `references/bitrix24-rest-domain-crm.md`: domain-specific triage/contract/templates/QA for CRM REST integrations.
- `references/bitrix24-rest-domain-tasks.md`: domain-specific triage/contract/templates/QA for Tasks REST integrations.
- `references/bitrix24-rest-domain-user.md`: domain-specific triage/contract/templates/QA for User REST integrations.
- `references/bitrix24-rest-domain-disk.md`: domain-specific triage/contract/templates/QA for Disk REST integrations.
- `references/bitrix24-rest-domain-quickstart.md`: end-to-end flow for domain-mode REST tasks (bootstrap -> domain pack -> artifacts -> QA -> delivery).
- `references/bitrix24-marketplace-publication.md`: engineering and moderation checklist for Bitrix24 marketplace submissions.
- `references/external-knowledge.md`: policy for extracting reusable rules from external knowledge dumps.
- `references/update-and-release.md`: diff-to-release workflow, migration discipline, rollback, versioning.
- `references/testing-qa.md`: smoke/regression and evidence model.
- `references/qa-gate-checklist.md`: strict QA checklist A-I with mandatory static-first and dynamic-second execution.
- `references/root-testing-toolkit.md`: root-level static and integration test toolkit contract (outside module folders).
- `references/troubleshooting.md`: common failure diagnostics for QA/runtime/setup issues.
- `references/release-checklist.md`: release-safe verification checklist.
- `references/template-migration-notes.md`: migration artifact template.
- `references/template-upgrade-notes.md`: upgrade artifact template.
- `references/template-release-notes.md`: release artifact template.
- `references/template-changelog-fragment.md`: changelog fragment template.
- `references/template-regression-checklist.md`: regression checklist template.
- `references/template-qa-report.md`: QA report template.
- `references/template-qa-audit-prompt.md`: reusable QA audit prompt (A-I) for static + dynamic verification flow.
- `references/template-moderator-precheck.md`: marketplace moderation precheck template.
- `references/template-module-install-index.php.md`: starter installer class template for module lifecycle.
- `references/template-rest-service-provider.php.md`: server-side REST method/event provider template for box modules.
- `references/template-rest-capability-bootstrap.md`: startup capability probe template (`scope`, `method.get`, `feature.get`).
- `references/template-rest-offline-worker-contract.md`: safe offline queue worker contract (`event.offline.get/clear/error`).
- `references/template-rest-method-confirm-handler.md`: admin confirmation handling template (`METHOD_CONFIRM_*`, `OnAppMethodConfirm`).
- `references/template-rest-domain-crm-artifact-pack.md`: ready artifact skeleton (`integration plan`, `scope matrix`, `event map`, `QA`) for CRM domain integrations.
- `references/template-rest-domain-tasks-artifact-pack.md`: ready artifact skeleton (`integration plan`, `scope matrix`, `event map`, `QA`) for Tasks domain integrations.
- `references/template-rest-domain-user-artifact-pack.md`: ready artifact skeleton (`integration plan`, `scope matrix`, `event map`, `QA`) for User domain integrations.
- `references/template-rest-domain-disk-artifact-pack.md`: ready artifact skeleton (`integration plan`, `scope matrix`, `event map`, `QA`) for Disk domain integrations.
- `references/template-component-baseline.md`: starter component template (`class.php`, params, cache, template).
- `references/template-component-advanced-pagination-tagcache.md`: advanced component template with pagination, tag cache, and cache key export.
- `references/template-admin-list-cadminlist.md`: starter admin list template with filter, row actions, and group actions.
- `references/template-admin-edit-tabcontrol.md`: starter admin edit template with `CAdminTabControl`, context menu, save/apply/delete flow.
- `references/template-options-tabcontrol.md`: starter module `options.php` template with tabbed settings and PRG save flow.
- `references/template-iblock-repository-service.md`: repository/service pair template for iblock CRUD with unified `Result + Error` handling.
- `references/template-hlblock-repository-service.md`: repository/service pair template for highloadblock CRUD with unified `Result + Error` handling.
- `references/template-migration-hlblock-create-updown.php.md`: migration template for highloadblock create/delete (`up/down`).
- `references/template-migration-hlblock-uf-updown.php.md`: migration template for HL user fields (`up/down`).
- `references/template-migration-iblock-property-updown.php.md`: migration template for iblock property add/update/delete.
- `references/template-migration-agents-updown.php.md`: migration template for agent add/remove flows.
- `references/template-migration-rollback-notes.md`: rollback checklist template for migration bundles.
- `scripts/scaffold_artifacts.py`: optional artifact scaffolding utility.
- `scripts/scaffold_module_admin.py`: optional module admin skeleton scaffolder (menu/list/edit/options/lang/proxies).
- `scripts/scaffold_data_layer.py`: optional data-layer scaffolder for `lib/Iblock/*` and `lib/Hl/*` repository/service classes.
- `scripts/scaffold_qa_gate.py`: optional QA gate package scaffolder (A-I report, static audit script, dynamic checklist, risk backlog).
- `scripts/scaffold_root_tests.py`: optional root-level test toolkit scaffolder (`tests/`, `phpunit`, `composer`, `.gitignore`, README testing section).
- `scripts/qa_run.py`: optional unified QA runner (static shell audit + phpunit static + phpunit integration) with one markdown report output, including auto `A-I` summary and risk-sorted fix backlog.
- `scripts/search_reference_dump.py`: optional search utility for large external docs dumps.
- `examples/new-module-site-management.md`: scenario recipe for greenfield module implementation.
- `examples/existing-project-fix.md`: scenario recipe for focused fixes in existing codebase.
- `examples/bitrix24-cloud-rest-app.md`: scenario recipe for Bitrix24 cloud REST app tasks.
- `examples/rest-domain-artifacts/README.md`: ready examples for filled domain artifact packs (`CRM/Tasks/User/Disk`).
- `examples/seeds/README.md`: dataset seeding guide for UX/performance checks.
- `examples/ci/github-actions-bitrix-qa.yml`: CI template for running `qa_run.py` and publishing report artifact.
- `examples/ci/github-actions-bitrix-rest-artifacts.yml`: CI template for generating REST domain artifact packs and publishing them as workflow artifacts.
- `examples/ci/github-actions-bitrix-rest-qa.yml`: CI template for one-pass pipeline (`REST artifacts + QA report`) with both artifact outputs.
