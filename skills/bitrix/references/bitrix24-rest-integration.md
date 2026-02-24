# Bitrix24 REST Integration Guide

Apply this guide when implementing Bitrix24 REST integrations, local apps, or marketplace apps.

## Platform Boundary

- Bitrix24 cloud: REST app and integration flows only.
- Bitrix24 box: REST app flows plus optional server-side extension patterns.
- Custom REST methods are a box-specific capability; do not assume they exist in cloud.

## Documentation Confidence Policy

When using external docs dumps, apply source triage first:

- primary source: `references/bitrix24-rest-docs-triage.md`
- avoid implementing core contracts from pages marked as in-progress (`Мы еще обновляем эту страницу`, `TO-DO _не выгружается на prod_`)
- treat legacy pages (`outdated`, `Развитие метода остановлено`) as compatibility-only references

Use domain-specific packs when integration is focused on one business area:

- `references/bitrix24-rest-domain-crm.md`
- `references/bitrix24-rest-domain-tasks.md`
- `references/bitrix24-rest-domain-user.md`
- `references/bitrix24-rest-domain-disk.md`
- `references/bitrix24-rest-domain-quickstart.md`

Use matching artifact templates for delivery:

- `references/template-rest-domain-crm-artifact-pack.md`
- `references/template-rest-domain-tasks-artifact-pack.md`
- `references/template-rest-domain-user-artifact-pack.md`
- `references/template-rest-domain-disk-artifact-pack.md`

## Runtime Capability Discovery

At install/startup, detect capabilities per portal:

- `scope` (granted scopes)
- `method.get` (`isExisting` and `isAvailable`)
- `feature.get` (feature gates such as `rest_offline_extended`, `rest_auth_connector`)

Rules:

- cache capability profile by portal (`member_id`/domain)
- refresh profile after reinstall/update/token refresh
- fail fast with explicit diagnostics when required methods/features are missing
- do not rely on legacy `methods` as primary capability source

## Auth Strategy

- Use incoming webhooks for one-portal local automation with minimal setup.
- Use OAuth 2.0 for local apps with UI/API-only mode and for marketplace apps.
- Never expose webhook secrets in frontend code or repositories.
- For box + cloud compatibility, refresh OAuth tokens via `oauth.bitrix.info` (`server_endpoint`).
- For API-only apps, use install callback endpoint to receive initial OAuth tokens.
- Install callback handlers run on backend calls from Bitrix24. Do not call `BX24.installFinish()` there.

## App Lifecycle and Trust Model

### On install (`OnAppInstall`)

- save `application_token` per portal (`member_id`)
- persist portal identity and OAuth endpoints
- initialize event/widget bindings

### On uninstall (`OnAppUninstall`)

- use `CLEAN` flag for cleanup policy
- after uninstall, app API access is already revoked; do not plan API calls in uninstall handler
- verify `application_token` even on uninstall (critical trust check)

### Method confirmation (`OnAppMethodConfirm`)

- handle admin confirmation result asynchronously
- map token -> method -> confirmed state
- re-run previously blocked call only when confirmation state is positive

## Scopes and Confirmation Lifecycle

- Request least-privilege scopes only.
- Validate granted scopes at startup and before risky flows.
- Handle admin-confirm methods explicitly:
  - `METHOD_CONFIRM_WAITING`
  - `METHOD_CONFIRM_DENIED`
- Confirmation is token-bound. New token requires re-confirmation.
- Keep retry workflow idempotent and bounded by timeout/backoff.

## Install-Time and Update-Time Validation

- Verify required methods, events, and features on each install/update.
- Re-register event bindings during each install/update cycle.
- Verify actual bindings via `event.get` after bind operations.
- Do not assume parity across cloud/box or across portals with different editions/tariffs.

## REST v3 Boundary and Migration Rules

- REST v3 methods are addressed via `/rest/api/...` routes.
- REST v2 and v3 can coexist; use hybrid strategy where v3 coverage is partial.
- Current docs note SDK gap for `/rest/api/` calls. Use direct HTTP requests where needed.
- For v3-only methods, enforce JSON request body and POST for parameterized calls.

## Box REST Provider Implementation (Server-Side Extension)

Apply this section only for `Bitrix24 box` or `Site Management` module development.

- Register methods through `onRestServiceBuildDescription()` and return explicit scope map.
- For small APIs, map each REST method directly to callback (`scope.method` => handler).
- For large APIs, use single dispatcher callback plus method registry to centralize validation/routing.
- For custom REST events, publish `\CRestUtil::EVENTS` metadata and include supported options in description.
- At method entry, run permission checks first and throw typed exceptions (`AccessException`/`RestException`).
- Validate and normalize request params before any DB write.
- If app data is stored in module tables, clean it on app removal via `onRestAppDelete` and `CLEAN=true`.
- For sync-style handlers, add loop guards/idempotency markers to avoid self-trigger loops.

## Token Lifecycle

- Store `access_token` and `refresh_token` securely and atomically.
- Keep token sets keyed by portal (`member_id`/domain) and app context.
- `refresh_token` lifetime is finite (commonly up to 180 days in docs).
- Refresh on auth-expiry/invalid-token path (or periodic keepalive), not on every request.
- Persist new token pair atomically before retrying failed call.
- Handle terminal auth states (`PAYMENT_REQUIRED`, uninstall, disabled app) without infinite retry.

## Request Mechanics

- Prefer JSON bodies for complex payloads.
- URL-encode parameters correctly.
- Use `batch` to reduce call count where safe:
  - max 50 commands per batch
  - no nested `batch`
- Use `halt` for chain safety when partial execution is risky.

## Pagination and Load Control

- For v2 list methods, process `next`/`start` flow.
- For large datasets, use explicit `select` fields and chunked workers.
- For offline queue reads:
  - `event.offline.list` has fixed page size 50
  - use `start = (N - 1) * 50` for page navigation

## Cloud Limits and Performance Signals

- Handle `503 QUERY_LIMIT_EXCEEDED` with backoff and jitter.
- Track response `time.operating` and `time.operating_reset_at`.
- Model rate pressure per portal and source IP.
- Prevent head-of-line blocking with queue-based workers and bounded concurrency.

## Events and Webhooks (Online)

- Verify `application_token` in every event handler.
- Keep handlers fast and offload heavy work to queues/workers.
- Ensure handler URLs are reachable from Bitrix24 servers.
- `event.unbind` requires admin context; design role-aware unbind flows.
- Re-bind on reinstall/update because bindings can reset.

## Offline Events Reliability Contract

- Register offline flow via `event.bind` with `event_type=offline`.
- Use `feature.get` for:
  - `rest_offline_extended`
  - `rest_auth_connector`
- Consume queue via:
  - `event.offline.list` (read-only)
  - `event.offline.get` (claim/consume)
  - `event.offline.clear` (ack)
  - `event.offline.error` (mark failed)

Safe flow:

1. Call `event.offline.get` with `clear=0`.
2. Process returned batch and keep `process_id`.
3. Ack success with `event.offline.clear` by `process_id` (and optional IDs).
4. Mark failures with `event.offline.error`.

Additional rules:

- default `clear=1` can lose events if worker crashes after fetch; prefer `clear=0`.
- `event.offline.get` supports multithreaded parsing with non-overlapping batches.
- Use `auth_connector` consistently on write calls to avoid self-loop events (with feature fallback strategy).
- Optional hybrid trigger: use `onOfflineEvent` with `minTimeout` to avoid aggressive polling.

## Widgets and Placement Notes

- `placement.bind` is admin-level and should be part of install/update flows.
- Widgets are not fully visible to non-admin users until app installation is finished.
- For `placement.unbind`, docs page is marked incomplete in current dump; validate behavior in runtime before codifying strict assumptions.

## File Upload Integration Notes

Bitrix has multiple file payload patterns. Select by target field type:

- direct base64 string in `file`
- `[filename, base64]` tuple
- `fileData` object
- disk-first upload for disk-bound fields

Use one normalized upload abstraction in your integration layer to avoid endpoint-specific mistakes.

## Minimal Integration Deliverables

- Auth model decision (`webhook` vs `oauth`).
- Scope matrix and permission rationale.
- Runtime capability matrix (`scope`/`method.get`/`feature.get`).
- Event registration map and verification strategy.
- Offline queue contract (claim, ack, error, retry), if used.
- Confirmation-flow handling (`METHOD_CONFIRM_*`, `OnAppMethodConfirm`).
- Retry/idempotency/error-handling contract.
- Limits/backoff strategy (`QUERY_LIMIT_EXCEEDED`, operating windows).
- Rollback and diagnostics plan.
