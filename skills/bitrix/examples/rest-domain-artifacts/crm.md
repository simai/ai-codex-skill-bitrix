# Example: REST Domain Artifact Pack (CRM)

## Header

- Domain: `CRM`
- Portal: `acme.bitrix24.ru`
- Environment: `stage`
- Auth model: `oauth`
- Owner: `integration-team`
- Date: `2026-02-24`

## 1) Integration Plan

### Objective

- Synchronize external ERP deals to Bitrix24 smart process and standard deals.

### In Scope

- `crm.item.list`
- `crm.item.get`
- `crm.item.add`
- `crm.item.update`
- `crm.item.delete`
- `crm.item.fields`

### Out of Scope

- Legacy `crm.deal.*` path, except explicit fallback for one legacy portal.

### Risks

- Field mismatch when `entityTypeId` schema changes.
- Side effects from robots on update.

### Rollback Trigger

- Error rate > 3% on write operations for 15 minutes.

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `crm` | Yes | Read/write CRM items | `scope` response on install |
| `user_basic` | No | Not required for current mapping | Capability profile v1 |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `crm.item.list` | Yes | PASS | Stop sync if unavailable |
| `crm.item.get` | Yes | PASS | Stop sync if unavailable |
| `crm.item.add` | Yes | PASS | Queue for retry if transient |
| `crm.item.update` | Yes | PASS | Queue for retry if transient |
| `crm.item.delete` | No | PASS | Soft close in external ERP |
| `crm.item.fields` | Yes | PASS | Use cached previous schema |

## 4) Entity Mapping Contract

| External Entity | `entityTypeId` | Field Map Source | Upsert Key | Notes |
|---|---|---|---|---|
| ERP Deal | 2 | `crm.item.fields` | `portal + entityTypeId + originId` | `originatorId=erp` |
| ERP Service Ticket | 1280 | `crm.item.fields` | `portal + entityTypeId + originId` | Smart-process |

Rules:

- `useOriginalUfNames` fixed to `N`.
- Legacy methods allowed only under feature flag `crm_legacy_bridge`.

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline`) | Handler | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `ONCRMDEALUPDATE` | online | `/hooks/crm/deal-update` | PASS | `portal + dealId + updatedTime` | max 5, exp backoff |
| `ONCRMDEALADD` | online | `/hooks/crm/deal-add` | PASS | `portal + dealId` | max 5, exp backoff |

Notes:

- Heavy reconciliation is moved to worker queue.
- Polling fallback runs every 15 minutes for missed events.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Pull sync | `portal + entityTypeId + id + updatedTime` | `QUERY_LIMIT_EXCEEDED`, timeout | 6 | `2s..60s + jitter` |
| Create/update | `portal + entityTypeId + originId + payloadHash` | `503`, network | 6 | `2s..60s + jitter` |
| Delete | `portal + entityTypeId + id + opType` | `503`, network | 3 | `2s..20s + jitter` |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| `crm.item.fields` cache refresh on install/update | PASS | install logs + profile dump | low | n/a |
| Pagination completeness (`start`, 50/page) | PASS | sync trace `count=1240` | med | n/a |
| Required-by-stage fields handled | PASS | write tests in stage | high | n/a |
| Legacy fallback controlled by feature flag | PASS | config snapshot | med | n/a |
| Robots/automation side effects covered | PASS | staging scenario logs | med | n/a |

## 8) QA Summary (A-I + Domain)

| Area | Status | Evidence | Risk | Recommendation |
|---|---|---|---|---|
| A. Install/Uninstall/Update | PASS | install callback logs | low | keep smoke in CI |
| B. Code quality | PASS | static grep report | low | keep lint gate |
| C. E2E scenarios | PASS | 7 scenario report | med | add one failure case |
| D. Performance | PASS | batch timing report | med | watch p95 in prod |
| E. UX on large data | N-A | backend-only integration | n/a | n/a |
| F. Security | PASS | token checks + secret audit | high | periodic review |
| G. Reliability | PASS | retry/idempotency tests | high | keep chaos tests |
| H. Diagnostics | PASS | structured logs sample | med | add trace id in UI |
| I. Compatibility | PASS | cloud+box smoke | med | keep hybrid mode |
| CRM domain checks | PASS | domain checklist | med | keep quarterly review |

