# Template: REST Domain Artifact Pack (CRM)

Use this template when preparing delivery artifacts for CRM-focused Bitrix24 REST integration.

## Header

- Domain: `CRM`
- Portal:
- Environment: `dev/stage/prod`
- Auth model: `webhook/oauth`
- Owner:
- Date:

## 1) Integration Plan

### Objective

- 

### In Scope

- `crm.item.list`
- `crm.item.get`
- `crm.item.add`
- `crm.item.update`
- `crm.item.delete`
- `crm.item.fields`

### Out of Scope

- 

### Risks

- 

### Rollback Trigger

- 

## 2) Scope and Permission Matrix

| Scope | Required | Why | Evidence |
|---|---|---|---|
| `crm` | Yes/No |  |  |
| `user_basic` | Yes/No |  |  |

## 3) Capability and Method Matrix

| Method/Feature | Required | Runtime Check (`scope/method.get/feature.get`) | Fallback |
|---|---|---|---|
| `crm.item.list` | Yes/No | PASS/FAIL |  |
| `crm.item.get` | Yes/No | PASS/FAIL |  |
| `crm.item.add` | Yes/No | PASS/FAIL |  |
| `crm.item.update` | Yes/No | PASS/FAIL |  |
| `crm.item.delete` | Yes/No | PASS/FAIL |  |
| `crm.item.fields` | Yes/No | PASS/FAIL |  |

## 4) Entity Mapping Contract

| External Entity | `entityTypeId` | Field Map Source | Upsert Key | Notes |
|---|---|---|---|---|
|  |  | `crm.item.fields` |  |  |

Rules:

- `entityTypeId` mapping must be explicit and versioned.
- `useOriginalUfNames` must be fixed for the whole integration (`Y` or `N`).
- Legacy methods are allowed only behind explicit compatibility flag.

## 5) Event Map and Handler Safety

| Event | Mode (`online/offline`) | Handler | `application_token` Check | Idempotency Key | Retry Policy |
|---|---|---|---|---|---|
| `<crm_event_name>` |  |  | PASS/FAIL |  |  |

Notes:

- If CRM events are not reliable/available in target portal, define polling fallback.
- Keep event handlers fast, queue heavy work.

## 6) Retry and Idempotency Contract

| Operation | Idempotency Key | Retryable Errors | Max Retries | Backoff |
|---|---|---|---|---|
| Pull sync |  |  |  |  |
| Create/update |  |  |  |  |
| Delete |  |  |  |  |

## 7) Verification Checklist

| Check | Status (`PASS/FAIL/N-A`) | Evidence | Risk | Fix |
|---|---|---|---|---|
| `crm.item.fields` cache refresh on install/update |  |  |  |  |
| Pagination completeness (`start`, 50/page) |  |  |  |  |
| Required-by-stage fields handled |  |  |  |  |
| Legacy fallback controlled by feature flag |  |  |  |  |
| Robots/automation side effects covered |  |  |  |  |

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
| CRM domain checks |  |  |  |  |

