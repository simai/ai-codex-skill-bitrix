# Template: REST Domain Artifact Pack (Tasks)

Use this template when preparing delivery artifacts for Tasks-focused Bitrix24 REST integration.

## Header

- Domain: `Tasks`
- Portal:
- Environment: `dev/stage/prod`
- Auth model: `webhook/oauth`
- Owner:
- Date:

## 1) Integration Plan

### Objective

- 

### In Scope

- `tasks.task.list`
- `tasks.task.get`
- `tasks.task.add`
- `tasks.task.update`
- `tasks.task.delete`
- `tasks.task.getFields`
- `tasks.task.history.list`

### Out of Scope

- `tasks/deprecated/*` methods for new flows

### Risks

- 

### Rollback Trigger

- 

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `task` | Yes/No |  |  |
| `user_basic` | Yes/No |  |  |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `tasks.task.list` | Yes/No | PASS/FAIL |  |
| `tasks.task.get` | Yes/No | PASS/FAIL |  |
| `tasks.task.add` | Yes/No | PASS/FAIL |  |
| `tasks.task.update` | Yes/No | PASS/FAIL |  |
| `tasks.task.delete` | Yes/No | PASS/FAIL |  |
| `tasks.task.getFields` | Yes/No | PASS/FAIL |  |
| `tasks.task.history.list` | Yes/No | PASS/FAIL |  |
| `tasks.task.getaccess` | Optional | PASS/FAIL |  |

## 4) Field and Action Contract

| Concern | Rule | Evidence |
|---|---|---|
| Create required fields | `TITLE`, `RESPONSIBLE_ID`, portal-required UF |  |
| Update contract | at least one changed field |  |
| CRM binding | `UF_CRM_TASK` format (`L_`, `D_`, `C_`, `CO_`) |  |
| File attachments | `UF_TASK_WEBDAV_FILES` values with `n<disk_file_id>` |  |
| Runtime schema | from `tasks.task.getFields` |  |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline`) | Handler | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `<tasks_event_name>` |  |  | PASS/FAIL |  |  |

Notes:

- If event coverage is insufficient, define periodic incremental sync.
- Use history endpoint for audit and reconciliation where applicable.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Pull list/history |  |  |  |  |
| Create/update |  |  |  |  |
| Delete |  |  |  |  |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| No usage of deprecated Tasks methods |  |  |  |  |
| Explicit `select` in list/get |  |  |  |  |
| Access check before destructive actions |  |  |  |  |
| UF fields validated before write |  |  |  |  |
| Pagination completeness (`start`, 50/page) |  |  |  |  |

## 8) QA Summary (A-I + Domain)

| Area | Status | Evidence | Risk | Recommendation |
|---|---|---|---|---|
| A. Install/Uninstall/Update |  |  |  |  |
| B. Code quality |  |  |  |  |
| C. E2E scenarios |  |  |  |  |
| D. Performance |  |  |  |  |
| E. UX on large data |  |  |  |  |
| F. Security |  |  |  |  |
| G. Reliability |  |  |  |  |
| H. Diagnostics |  |  |  |  |
| I. Compatibility |  |  |  |  |
| Tasks domain checks |  |  |  |  |

