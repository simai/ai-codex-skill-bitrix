# Example: REST Domain Artifact Pack (Disk)

## Header

- Domain: `Disk`
- Portal: `acme.bitrix24.ru`
- Environment: `stage`
- Auth model: `oauth`
- Owner: `document-integration-team`
- Date: `2026-02-24`

## 1) Integration Plan

### Objective

- Upload and maintain contract documents on Bitrix24 Disk with controlled access and lifecycle.

### In Scope

- `disk.storage.getlist`
- `disk.storage.getchildren`
- `disk.folder.getchildren`
- `disk.folder.uploadfile`
- `disk.file.get`
- `disk.file.markdeleted`
- `disk.file.delete` (cleanup only)
- `disk.rights.getTasks`

### Out of Scope

- Document editing workflow and version merge UI.

### Risks

- File name collisions.
- Overly broad access rights.
- Raw base64 logging.

### Rollback Trigger

- Access control mismatch or failed restore during soft-delete test.

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `disk` | Yes | file/folder/storage operations | capability profile |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `disk.storage.getlist` | Yes | PASS | stop workflow |
| `disk.storage.getchildren` | Yes | PASS | stop folder traversal |
| `disk.folder.getchildren` | Yes | PASS | stop folder traversal |
| `disk.folder.uploadfile` | Yes | PASS | fallback to storage root upload |
| `disk.storage.uploadfile` | No | PASS | keep folder upload only |
| `disk.file.get` | Yes | PASS | fail-safe with retry |
| `disk.file.markdeleted` | Yes | PASS | block delete flow |
| `disk.file.delete` | Optional | PASS | keep soft delete only |
| `disk.rights.getTasks` | Yes | PASS | static rights map (temporary) |

## 4) Upload, Rights, and Delete Policy

| Concern | Rule | Evidence |
|---|---|---|
| Upload mode | direct base64 for <=10MB, upload URL above | integration test |
| Name collisions | `generateUniqueName=true` | duplicate-name test |
| Rights assignment | `TASK_ID` from `disk.rights.getTasks` + strict `ACCESS_CODE` | role tests |
| Delete strategy | soft delete first (`markdeleted`) | delete tests |
| Restore path | mandatory restore test in stage | restore logs |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline/polling`) | Handler/Schedule | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| file reconciliation | polling (20m) | `cron:disk-reconcile` | PASS | `portal + fileId + updateTime` | max 4 |
| delete queue | async queue | `worker:disk-delete` | PASS | `portal + fileId + opType` | max 3 |

Note:

- No critical business logic is tied to near-real-time events.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Upload | `portal + path + fileHash` | timeout, lock conflict | 5 | `2s..45s + jitter` |
| Metadata read/list | `portal + objectId + updateTime` | timeout, `503` | 5 | `2s..45s + jitter` |
| Delete/restore | `portal + fileId + opType` | lock conflict, timeout | 3 | `2s..20s + jitter` |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| Upload succeeds in selected mode(s) | PASS | upload integration report | med | n/a |
| Duplicate-name handling tested | PASS | duplicate test logs | med | n/a |
| Rights behavior validated for target roles | PASS | role matrix screenshots | high | n/a |
| Soft-delete and restore validated | PASS | restore scenario logs | high | n/a |
| Hard-delete restricted and audited | PASS | cleanup runbook + logs | high | n/a |
| Base64 payload is not logged | PASS | log scan results | high | n/a |

## 8) QA Summary (A-I + Domain)

| Area | Status | Evidence | Risk | Recommendation |
|---|---|---|---|---|
| A. Install/Uninstall/Update | PASS | lifecycle logs | low | keep smoke |
| B. Code quality | PASS | static audit | low | keep lint |
| C. E2E scenarios | PASS | 6 scenarios | med | add large-file case |
| D. Performance | PASS | upload timing report | med | tune worker parallelism |
| E. UX on large data | N-A | backend integration | n/a | n/a |
| F. Security | PASS | rights + payload masking checks | high | periodic review |
| G. Reliability | PASS | retry/replay tests | high | keep chaos checks |
| H. Diagnostics | PASS | structured logs | med | add upload trace id |
| I. Compatibility | PASS | cloud+box smoke | med | keep matrix up to date |
| Disk domain checks | PASS | domain checklist | high | quarterly audit |

