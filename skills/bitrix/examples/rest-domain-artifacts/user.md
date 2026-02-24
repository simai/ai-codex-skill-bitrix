# Example: REST Domain Artifact Pack (User)

## Header

- Domain: `User`
- Portal: `acme.bitrix24.ru`
- Environment: `stage`
- Auth model: `oauth`
- Owner: `identity-sync-team`
- Date: `2026-02-24`

## 1) Integration Plan

### Objective

- Keep local employee directory synchronized with Bitrix24 user profiles.

### In Scope

- `user.get`
- `user.search`
- `user.current`
- `user.fields`
- `user.add` (admin path)
- `user.update` (admin path)

### Out of Scope

- HR workflow automation beyond profile update.

### Risks

- Over-scoped permissions (`user` instead of `user_basic`).
- PII leakage in logs.

### Rollback Trigger

- Privacy-control test fails or PII appears in logs.

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `user_brief` | No | insufficient for sync | scope review |
| `user_basic` | Yes | read users + contact basics | capability profile |
| `user` | Yes | invite/update users in admin flow | admin-only workflow doc |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `user.get` | Yes | PASS | stop full sync |
| `user.search` | Yes | PASS | fallback to filtered `user.get` |
| `user.current` | Yes | PASS | use service token metadata |
| `user.fields` | Yes | PASS | use cached field map |
| `user.add` | Optional | PASS | manual invite runbook |
| `user.update` | Optional | PASS | manual update runbook |

## 4) Data Privacy and Access Contract

| Concern | Rule | Evidence |
|---|---|---|
| PII logging | `EMAIL`, phones masked | log policy test |
| `ADMIN_MODE` usage | only admin service account path | auth middleware test |
| Invite flow | intranet -> `UF_DEPARTMENT`; extranet -> `EXTRANET` + `SONET_GROUP_ID` | integration tests |
| Search filter contract | no `FIND` mixed with other filters | request validator test |

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline/polling`) | Handler/Schedule | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| directory sync job | polling (15m) | `cron:user-sync` | PASS | `portal + userId + timestampX` | max 4 |
| invite callback | online | `/hooks/user/invite` | PASS | `portal + email` | max 3 |

Note:

- User sync uses polling to avoid inconsistent event coverage across portals.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| User pull | `portal + userId + timestampX` | timeout, `503` | 5 | `2s..30s + jitter` |
| Invite/update | `portal + email + payloadHash` | timeout, `503` | 3 | `2s..20s + jitter` |
| Deactivate/activate | `portal + userId + state` | timeout | 3 | `2s..20s + jitter` |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| Scope minimization validated | PASS | access matrix | high | n/a |
| Missing fields with narrow scope handled safely | PASS | integration test | med | n/a |
| Admin-only methods protected | PASS | auth policy tests | high | n/a |
| `FIND` search contract respected | PASS | request validator logs | med | n/a |
| PII masking in logs/reports | PASS | sampled logs | high | n/a |

## 8) QA Summary (A-I + Domain)

| Area | Status | Evidence | Risk | Recommendation |
|---|---|---|---|---|
| A. Install/Uninstall/Update | PASS | lifecycle logs | low | keep smoke |
| B. Code quality | PASS | static grep | low | keep lint |
| C. E2E scenarios | PASS | 6 scenarios | med | add offboarding scenario |
| D. Performance | PASS | sync timing report | med | keep chunk size review |
| E. UX on large data | N-A | backend-only sync | n/a | n/a |
| F. Security | PASS | scope + masking checks | high | quarterly review |
| G. Reliability | PASS | replay tests | high | keep replay CI job |
| H. Diagnostics | PASS | structured logs | med | add identity correlation id |
| I. Compatibility | PASS | cloud+box smoke | med | keep portal matrix |
| User domain checks | PASS | domain checklist | high | keep privacy audit |

