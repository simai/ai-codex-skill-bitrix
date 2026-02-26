# QA Gate Checklist (A-I)

Use this checklist for quality control of Bitrix modules and updates.

Execution order is mandatory:

1. Static audit first (`rg`/search/logical inspection).
2. Dynamic tests second (admin UI, CLI, integration runtime).
3. Unified report with risk-ranked fixes.

For every section A-I output:

- Status: `PASS` / `FAIL` / `N-A`
- Evidence: command, screenshot, log, SQL
- Risk: `low` / `med` / `high`
- Concrete fix: what/where/how

## A) Install / Uninstall / Update

- Fresh install completes without critical errors.
- Reinstall and uninstall scenarios are deterministic.
- Update path works from previous target versions.
- `savedata=Y/N` behavior is explicit and correct.
- Component settings dialog opens and keeps current values (no endless loading, no empty params for configured page).
- Public folders/shared data cleanup is ownership-based (marker/option) and does not remove foreign files.
- Copied component directories are fully removed on uninstall (no stale residue).
- Multi-site site-code conventions for iblock type/code are preserved after install/reinstall.

Evidence examples:

- install/uninstall logs
- DB state before/after
- module registration state (`b_module`)
- component parser check (`PHPParser::FindComponent(...)->DATA["PARAMS"]` is array)
- filesystem residue check (`/bitrix/components/<vendor>/<component>` absent after uninstall)

## B) Code Quality (Localization, Magic Numbers, Debug)

- UI strings are localized (`Loc::getMessage`, `lang/*`).
- No hardcoded debug output (`var_dump`, `print_r`, `die`, `dd`).
- Critical constants/config are not hidden as unexplained magic numbers.
- No dead/test code in production path.

Static commands:

```bash
rg -n "var_dump|print_r\\(|die\\(|dd\\(" local/modules/<module_id>
rg -n "Loc::getMessage|GetMessage\\(" local/modules/<module_id>
rg -n "[^A-Z_]\\b(300|500|86400)\\b" local/modules/<module_id>
```

## C) End-to-End Scenarios (Top 5-10)

- Define 5-10 most critical business scenarios.
- Cover happy path + key negative path for each.
- Validate full chain: UI -> service -> storage -> side effects.

Required output:

- scenario list with expected result and actual result
- failed scenario repro steps

## D) Performance and Scaling

- Large dataset list/filter behavior checked.
- Slow query risk reviewed.
- Batch/chunk processing boundaries checked.
- Caching and invalidation are consistent.

Evidence examples:

- SQL/profile output
- timings on realistic data volume
- cache hit/miss behavior

## E) UX on Large Data

- Admin lists remain usable with large rows count.
- Filters, sorting, pagination stay responsive.
- Mass actions are predictable and safe.
- No blocking UI operations without progress indication.

## F) Security (Rights, CSRF, Path Traversal)

- Rights checks protect read/write/delete actions.
- `check_bitrix_sessid()` on state-changing actions.
- File/path input does not allow traversal.
- Secrets are not exposed in code/log/UI.

Static commands:

```bash
rg -n "check_bitrix_sessid|bitrix_sessid_post|bitrix_sessid_get" local/modules/<module_id>
rg -n "AuthForm|GetGroupRight|isAdmin|HighloadBlockRightsTable" local/modules/<module_id>
rg -n "\\.\\./|DOCUMENT_ROOT.*\\$_(GET|POST|REQUEST)" local/modules/<module_id>
```

## G) Reliability (Locks, Resume, Concurrency)

- Parallel execution risk is assessed for write paths.
- Long tasks have resume/retry strategy where needed.
- Duplicate runs are idempotent where required.
- No unsafe race in group actions/batch handlers.

## H) Diagnostics / Logging

- Errors are logged with enough context.
- Operational logs are actionable and not noisy.
- Failure states are observable (not silent).

Evidence examples:

- app log excerpt
- monitored error sample
- correlation context fields

## I) Compatibility

- PHP/MySQL baseline compatibility checked (`PHP 8+`, `MySQL 8+`).
- Backward compatibility for existing data/flows verified.
- Bitrix edition/platform constraints respected (Site/Box/Cloud REST).

## REST App Addendum (Cloud/Box REST mode)

Apply this addendum when task includes webhook/OAuth/events integrations.

- Capability bootstrap validated (`scope`, `method.get`, `feature.get`) with evidence.
- Event handlers validate `application_token`.
- Confirm-flow covered (`METHOD_CONFIRM_WAITING`, `METHOD_CONFIRM_DENIED`, `OnAppMethodConfirm`).
- Offline mode (if used) follows safe flow:
  - `event.offline.get` with `clear=0`
  - `process_id` tracked
  - `event.offline.clear` / `event.offline.error` used explicitly
- Install/update/reinstall rebind routine is verified (`event.get` before/after).
- REST v3 usage is explicit (`/rest/api/`), with fallback or hybrid routing documented.

## REST Domain Addendum (CRM/Tasks/User/Disk)

Apply for domain-heavy REST integrations.

- CRM:
  - `crm.item.*` usage is primary for new code.
  - `entityTypeId` mapping and `crm.item.fields` cache are validated.
  - legacy `crm.*` branches are either absent or feature-flagged.
- Tasks:
  - `tasks.task.*` is used instead of deprecated methods.
  - required custom fields are detected before create/update.
  - `UF_CRM_TASK` and `UF_TASK_WEBDAV_FILES` value formats are validated.
- User:
  - scope level is least-privilege and justified.
  - `user.add` / `user.update` paths are admin-protected.
  - `user.search` filter contract (`FIND` exclusivity) is respected.
- Disk:
  - upload flow (`fileContent` or upload URL) is explicit and tested.
  - soft-delete/hard-delete policy is explicit and verified.
  - rights assignment (`TASK_ID`, `ACCESS_CODE`) is validated by role-based checks.

## Final Deliverables

1. Unified QA report (A-I sections).
2. Risk-ranked fix list (high -> med -> low).
3. Re-test checklist for failed items.
