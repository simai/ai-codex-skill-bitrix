# Template: REST Domain Artifact Pack (Disk)

Use this template when preparing delivery artifacts for Disk/File-focused Bitrix24 REST integration.

## Header

- Domain: `Disk`
- Portal:
- Environment: `dev/stage/prod`
- Auth model: `webhook/oauth`
- Owner:
- Date:

## 1) Integration Plan

### Objective

- 

### In Scope

- `disk.storage.getlist`
- `disk.storage.getchildren`
- `disk.folder.getchildren`
- `disk.storage.uploadfile` and/or `disk.folder.uploadfile`
- `disk.file.get`
- `disk.file.markdeleted`
- `disk.file.delete` (if hard-delete is in scope)

### Out of Scope

- 

### Risks

- 

### Rollback Trigger

- 

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `disk` | Yes/No |  |  |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `disk.storage.getlist` | Yes/No | PASS/FAIL |  |
| `disk.storage.getchildren` | Yes/No | PASS/FAIL |  |
| `disk.folder.getchildren` | Yes/No | PASS/FAIL |  |
| `disk.folder.uploadfile` | Yes/No | PASS/FAIL |  |
| `disk.storage.uploadfile` | Optional | PASS/FAIL |  |
| `disk.file.get` | Yes/No | PASS/FAIL |  |
| `disk.file.markdeleted` | Yes/No | PASS/FAIL |  |
| `disk.file.delete` | Optional | PASS/FAIL |  |
| `disk.rights.getTasks` | Optional | PASS/FAIL |  |

## 4) Upload, Rights, and Delete Policy

| Concern | Rule | Evidence |
|---|---|---|
| Upload mode | `direct base64` / `upload URL` / both |  |
| Name collisions | `generateUniqueName` policy fixed |  |
| Rights assignment | `TASK_ID` + `ACCESS_CODE` validated |  |
| Delete strategy | `soft` (`markdeleted`) first or `hard` (`delete`) |  |
| Restore path | tested if soft delete is used |  |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline/polling`) | Handler/Schedule | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `<disk_event_or_polling_job>` |  |  | PASS/FAIL |  |  |

Note:

- if no stable event stream is used, define polling/reconciliation cadence.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Upload |  |  |  |  |
| Metadata read/list |  |  |  |  |
| Delete/restore |  |  |  |  |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| Upload succeeds in selected mode(s) |  |  |  |  |
| Duplicate-name handling tested |  |  |  |  |
| Rights behavior validated for target roles |  |  |  |  |
| Soft-delete and restore validated |  |  |  |  |
| Hard-delete restricted and audited |  |  |  |  |
| Base64 payload is not logged |  |  |  |  |

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
| Disk domain checks |  |  |  |  |

