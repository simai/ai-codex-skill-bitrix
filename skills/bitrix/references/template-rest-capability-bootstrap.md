# Template: REST Capability Bootstrap

Use this template at app startup/install to detect portal capabilities before running business logic.

## Inputs

- portal `member_id`
- portal `domain`
- auth context (`webhook` or OAuth token)
- required method list
- required scope list
- required feature flags

## Probe Flow

1. Call `scope` and collect granted scopes.
2. For each required method call `method.get` and read `isExisting` + `isAvailable`.
3. For each required feature call `feature.get`.
4. Build capability profile and persist atomically.
5. Return explicit diagnostics for missing prerequisites.

## Output Schema (example)

```json
{
  "member_id": "a223c6b3710f85df22e9377d6c4f7553",
  "domain": "example.bitrix24.ru",
  "scopes": ["crm", "task", "user"],
  "methods": {
    "crm.deal.list": { "isExisting": true, "isAvailable": true },
    "event.offline.get": { "isExisting": true, "isAvailable": false }
  },
  "features": {
    "rest_offline_extended": "Y",
    "rest_auth_connector": "N"
  },
  "checked_at": "2026-02-24T10:30:00Z"
}
```

## Fail-Fast Rules

- missing required scope -> block startup for that module path
- method exists but unavailable -> report permission/role requirement
- feature unavailable -> switch to fallback flow (documented)

## Recheck Triggers

Re-run bootstrap on:

- app reinstall
- app version update
- token refresh (for token-bound permissions)
- explicit admin action (`recheck capabilities`)
