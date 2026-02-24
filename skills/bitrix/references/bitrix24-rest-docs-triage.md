# Bitrix24 REST Docs Triage

Use this reference when extracting rules from large Bitrix24 REST documentation dumps.

## Source Baseline

Primary dump analyzed:

- `<b24-rest-docs-root>/api-reference`

Current scale:

- ~2789 files in `api-reference`

## Confidence Tiers

### Tier A: Stable (default source for engineering rules)

Use as primary sources for integration contracts:

- `api-reference/common/system/method-get.md`
- `api-reference/common/system/feature-get.md`
- `api-reference/common/system/scope.md`
- `api-reference/common/system/app-info.md`
- `api-reference/common/events/on-app-install.md`
- `api-reference/common/events/on-app-uninstall.md`
- `api-reference/common/events/on-app-method-confirm.md`
- `api-reference/events/event-bind.md`
- `api-reference/events/event-unbind.md`
- `api-reference/events/event-get.md`
- `api-reference/events/offline-events.md`
- `api-reference/events/event-offline-list.md`
- `api-reference/events/event-offline-get.md`
- `api-reference/events/event-offline-clear.md`
- `api-reference/events/event-offline-error.md`
- `api-reference/events/on-offline-event.md`
- `api-reference/events/safe-event-handlers.md`
- `api-reference/scopes/index.md`
- `api-reference/scopes/permissions.md`
- `api-reference/scopes/confirmation.md`
- `api-reference/rest-v3/index.md`
- `api-reference/rest-v3/main/index.md`
- `api-reference/rest-v3/tasks/index.md`
- `api-reference/files/how-to-upload-files.md`

### Tier B: Caution (use only with runtime validation)

Use with extra validation if page contains update-warning markers:

- marker: `Мы еще обновляем эту страницу`
- marker: `TO-DO _не выгружается на prod_`

Examples:

- `api-reference/widgets/placement-unbind.md` (explicitly incomplete)
- `api-reference/data-types.md` (contains TODO sections)

Rule: if Tier B is used, verify behavior via runtime calls (`method.get`, `feature.get`, test portal flow) before codifying in skill guidance.

### Tier C: Legacy/Deprecated (do not use as baseline)

Avoid as primary source for new integration decisions:

- `api-reference/common/system/methods.md` (legacy replacement exists: `method.get`)
- anything under `api-reference/**/outdated/**`
- pages marked with `Развитие метода остановлено`

Rule: legacy pages may be used only for compatibility notes, not for default implementation contracts.

## Extraction Rules

1. Extract platform behavior first, domain methods second.
2. Prioritize contracts that affect reliability and security:
   - token lifecycle
   - scope and confirm flow
   - event lifecycle and trust checks
   - offline queue safety
   - limits/backoff
3. Prefer method-level contracts over narrative/tutorial sections if they conflict.
4. For conflicts between pages, trust Tier A sources plus runtime capability checks.

## Runtime Validation Checklist

Before finalizing integration guidance, verify on portal:

- `scope` for granted scopes
- `method.get` for required method availability
- `feature.get` for `rest_offline_extended` and `rest_auth_connector`
- `event.get` to confirm actual bindings
- response `time.operating` and `time.operating_reset_at` presence

## Recommended Search Filters

Use these filters for future updates in large dumps:

```bash
rg -n --glob '*.md' -i 'method.get|feature.get|scope|event.bind|event.unbind|event.offline|get|clear|error|application_token|METHOD_CONFIRM_WAITING|METHOD_CONFIRM_DENIED|/rest/api/' api-reference
```

```bash
rg -n --glob '*.md' -i 'Мы еще обновляем эту страницу|TO-DO _не выгружается на prod_|Развитие метода остановлено|outdated' api-reference
```

## Integration Output Contract

When converting docs into skill guidance:

- include source tier (`A/B/C`)
- include runtime verification command or method
- include fallback behavior if capability is absent
- include risk note for any Tier B/C dependency
