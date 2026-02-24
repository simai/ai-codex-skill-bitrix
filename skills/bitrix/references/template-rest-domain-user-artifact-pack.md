# Template: REST Domain Artifact Pack (User)

Use this template when preparing delivery artifacts for User/Directory-focused Bitrix24 REST integration.

## Header

- Domain: `User`
- Portal:
- Environment: `dev/stage/prod`
- Auth model: `webhook/oauth`
- Owner:
- Date:

## 1) Integration Plan

### Objective

- 

### In Scope

- `user.get`
- `user.search`
- `user.current`
- `user.fields`
- `user.add` (if admin flow is in scope)
- `user.update` (if admin flow is in scope)

### Out of Scope

- 

### Risks

- 

### Rollback Trigger

- 

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `user_brief` | Yes/No |  |  |
| `user_basic` | Yes/No |  |  |
| `user` | Yes/No |  |  |

Rule:

- choose least-privilege scope and document why higher scope is needed if selected.

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `user.get` | Yes/No | PASS/FAIL |  |
| `user.search` | Yes/No | PASS/FAIL |  |
| `user.current` | Yes/No | PASS/FAIL |  |
| `user.fields` | Yes/No | PASS/FAIL |  |
| `user.add` | Optional | PASS/FAIL |  |
| `user.update` | Optional | PASS/FAIL |  |

## 4) Data Privacy and Access Contract

| Concern | Rule | Evidence |
|---|---|---|
| PII logging | sensitive fields masked/redacted |  |
| `ADMIN_MODE` usage | restricted to admin-only service path |  |
| Invite flow | intranet -> `UF_DEPARTMENT`, extranet -> `EXTRANET` + `SONET_GROUP_ID` |  |
| Search filter contract | `FIND` not mixed with other filters |  |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline/polling`) | Handler/Schedule | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `<user_event_or_polling_job>` |  |  | PASS/FAIL |  |  |

Note:

- if no stable event source is used, define polling schedule and checkpoint key.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Directory pull |  |  |  |  |
| Invite/update |  |  |  |  |
| Access sync |  |  |  |  |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| Scope minimization validated |  |  |  |  |
| Missing fields with narrow scope handled safely |  |  |  |  |
| Admin-only methods protected |  |  |  |  |
| `FIND` search contract respected |  |  |  |  |
| PII masking in logs/reports |  |  |  |  |

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
| User domain checks |  |  |  |  |

