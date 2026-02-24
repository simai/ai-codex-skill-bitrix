# Example: REST Domain Artifact Pack (Tasks)

## Header

- Domain: `Tasks`
- Portal: `acme.bitrix24.ru`
- Environment: `stage`
- Auth model: `oauth`
- Owner: `tasks-sync-team`
- Date: `2026-02-24`

## 1) Integration Plan

### Objective

- Synchronize external PM tasks with Bitrix24 tasks and linked CRM entities.

### In Scope

- `tasks.task.list`
- `tasks.task.get`
- `tasks.task.add`
- `tasks.task.update`
- `tasks.task.delete`
- `tasks.task.getFields`
- `tasks.task.history.list`
- `tasks.task.getaccess`

### Out of Scope

- Deprecated `task.item.*` methods.

### Risks

- Missing required custom fields on create/update.
- Incorrect `UF_CRM_TASK` / `UF_TASK_WEBDAV_FILES` payload format.

### Rollback Trigger

- Create/update failures > 2% on 30-minute window.

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `task` | Yes | Task read/write operations | `scope` + method probe |
| `user_basic` | Yes | User mapping for assignees | capability profile |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `tasks.task.list` | Yes | PASS | stop incremental sync |
| `tasks.task.get` | Yes | PASS | stop per-task read |
| `tasks.task.add` | Yes | PASS | queue for retry |
| `tasks.task.update` | Yes | PASS | queue for retry |
| `tasks.task.delete` | Yes | PASS | disable delete flow |
| `tasks.task.getFields` | Yes | PASS | use previous cached schema |
| `tasks.task.history.list` | No | PASS | fallback to changedDate polling |
| `tasks.task.getaccess` | Yes | PASS | block destructive actions |

## 4) Field and Action Contract

| Concern | Rule | Evidence |
|---|---|---|
| Create required fields | `TITLE`, `RESPONSIBLE_ID`, required UF | schema check in worker |
| Update contract | at least one changed field | request validator |
| CRM binding | `UF_CRM_TASK` values `D_`, `L_`, `C_`, `CO_` | mapping tests |
| File attachments | `UF_TASK_WEBDAV_FILES` values `n<disk_id>` | integration tests |
| Runtime schema | from `tasks.task.getFields` | cached profile dump |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline`) | Handler | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `ONTASKADD` | online | `/hooks/tasks/add` | PASS | `portal + taskId` | max 5 |
| `ONTASKUPDATE` | online | `/hooks/tasks/update` | PASS | `portal + taskId + changedDate` | max 5 |

Notes:

- Reconciliation poll runs every 10 minutes for missed webhook events.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| List/history pull | `portal + taskId + changedDate` | timeout, `503` | 6 | `2s..60s + jitter` |
| Create/update | `portal + externalTaskId + payloadHash` | timeout, `503` | 6 | `2s..60s + jitter` |
| Delete | `portal + taskId + opType` | timeout, `503` | 3 | `2s..20s + jitter` |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| No usage of deprecated Tasks methods | PASS | static grep report | high | n/a |
| Explicit `select` in list/get | PASS | API trace | med | n/a |
| Access check before destructive actions | PASS | call log `tasks.task.getaccess` | high | n/a |
| UF fields validated before write | PASS | worker validation logs | high | n/a |
| Pagination completeness (`start`, 50/page) | PASS | page trace dump | med | n/a |

## 8) QA Summary (A-I + Domain)

| Area | Status | Evidence | Risk | Recommendation |
|---|---|---|---|---|
| A. Install/Uninstall/Update | PASS | app lifecycle logs | low | keep smoke |
| B. Code quality | PASS | static audit | low | keep lint |
| C. E2E scenarios | PASS | 8 scenarios | med | add SLA case |
| D. Performance | PASS | load run report | med | tune batch size |
| E. UX on large data | N-A | backend integration | n/a | n/a |
| F. Security | PASS | token + rights checks | high | periodic security test |
| G. Reliability | PASS | idempotency replay test | high | keep replay test |
| H. Diagnostics | PASS | structured log sample | med | add alert mapping |
| I. Compatibility | PASS | cloud+box checks | med | keep compatibility matrix |
| Tasks domain checks | PASS | domain checklist | high | keep quarterly audit |

