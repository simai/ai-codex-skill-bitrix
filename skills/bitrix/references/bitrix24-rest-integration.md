# Bitrix24 REST Integration Guide

Apply this guide when implementing Bitrix24 REST integrations, local apps, or marketplace apps.

## Platform Boundary

- Bitrix24 cloud: REST app and integration flows only.
- Bitrix24 box: REST app flows plus optional server-side extension patterns.
- Custom REST methods are a box-specific capability; do not assume they exist in cloud.

## Runtime Capability Discovery

- At install/startup, detect capabilities per portal using:
  - `scope` (granted scopes),
  - `method.get` (method availability),
  - `feature.get` (feature gates such as offline events).
- Cache capability profile by portal/member id, but refresh after app reinstall/version update.
- Fail fast with explicit diagnostics when required methods or features are unavailable.

## Auth Strategy

- Use incoming webhooks for one-portal local automation with minimal setup.
- Use OAuth 2.0 for local apps with UI/API-only mode and for marketplace apps.
- Never expose webhook secrets in frontend code or public repositories.
- For box + cloud compatibility, refresh OAuth tokens via `oauth.bitrix.info`.
- For API-only apps, use install callback endpoint to receive initial OAuth tokens.
- Install callback handlers run on backend calls from Bitrix24; do not call `BX24.installFinish()` there.

## Install-Time Validation

- At install/setup, check availability of required REST methods, events, and features.
- Do not assume identical method support across cloud and box or across box instances.
- Re-register event bindings during each install/update cycle.

## Scopes and Permissions

- Request least-privilege scopes only.
- Validate the current app scope set and handle `insufficient_scope` explicitly.
- For methods that require admin confirmation, handle confirmation lifecycle and retries.

## Box REST Provider Implementation (Server-Side Extension)

Apply this section only for `Bitrix24 box` or `Site Management` module development.

- Register methods through `onRestServiceBuildDescription()` and return explicit scope map.
- For small APIs, map each REST method directly to callback (`scope.method` => handler).
- For large APIs, use single dispatcher callback plus method registry (core CRM pattern) to centralize validation/routing.
- For custom REST events, publish `\CRestUtil::EVENTS` metadata and include supported options in description.
- At method entry, run permission checks first and throw typed exceptions (`AccessException`/`RestException`) on deny/invalid input.
- Validate and normalize request params before any DB write (`array_change_key_case`, strict type checks, required fields).
- If app data is stored in module tables, clean it on app removal via `onRestAppDelete` and `CLEAN=true`.
- For sync-style handlers, add loop guards/idempotency markers so integration does not retrigger itself.

## Token Lifecycle

- Store `access_token` and `refresh_token` securely and atomically.
- Keep token sets keyed by portal (`member_id`/domain) and app context.
- `refresh_token` lifetime is finite (documented as up to 180 days); refresh with server-side flow.
- Refresh on auth-expiry/invalid-token path (or infrequent keepalive), not before every request.
- Persist newly issued token pair atomically before retrying failed REST call.
- Handle non-retryable auth states (`PAYMENT_REQUIRED`, uninstall, disabled app) as terminal.

## Request Mechanics

- Prefer JSON request bodies for complex payloads.
- URL-encode parameters correctly; for `batch`, apply required double encoding rules.
- Use `batch` to reduce hit count where safe:
  - maximum 50 commands per batch
  - no nested `batch` calls
- Use `halt` in batch chains when partial execution is risky.

## Pagination and Load Control

- For list methods, process `next` and `start` pagination flow.
- Use explicit field selection (`select`) to minimize payload.
- For huge datasets, design chunked processing and backpressure-safe workers.

## Cloud Limits and Performance Signals

- Cloud request intensity is rate-limited with leaky-bucket behavior; handle `503 QUERY_LIMIT_EXCEEDED`.
- Documented baseline limits:
  - non-enterprise: refill `2 req/s`, bucket `50`,
  - enterprise: refill `5 req/s`, bucket `250`.
- Rate accounting is per portal and source IP; multiple apps behind one IP share pressure.
- Monitor REST response `time.operating` and `time.operating_reset_at`.
- In cloud, per-method operating budget can be blocked when cumulative operating time is exhausted.

## Events and Webhooks (Online)

- Verify `application_token` in event handlers.
- Keep event handlers fast; offload heavy processing to queues/workers.
- Ensure handler URL is reachable from Bitrix24 servers (no private-only endpoints).
- `event.unbind` requires admin context; design unbind flows accordingly.
- On reinstall/update, bindings can be reset: always re-bind from installer/update flow.
- Keep `event.get` verification in health/debug routines.

## Offline Events (Sync-Oriented)

- Register offline flow with `event.bind` + `event_type=offline` (+ `auth_connector` when used).
- Offline queues are consumed via:
  - `event.offline.list` (read-only queue view),
  - `event.offline.get` (claim/consume batches),
  - `event.offline.clear` (confirm processed items),
  - `event.offline.error` (mark failed items).
- `event.offline.get` default behavior clears claimed data (`clear=1`); use `clear=0` for safe processing.
- With `clear=0`, keep `process_id`, process payload, then clear by `process_id` (optionally partial IDs).
- `event.offline.list` uses fixed page size (50) and `start`-based paging.
- Multithreaded `event.offline.get` is supported; claimed batches are separated across workers.
- Use `auth_connector` consistently in write calls to avoid self-trigger sync loops (plan fallback for tiers where unavailable).
- Box source constraints to enforce in integration code:
  - `event.offline.*` endpoints are admin-only in app auth context.
  - `event.bind` with `event_type=offline` also requires admin rights.
  - `clear=0` flow can be feature-gated (`rest_offline_extended`) on some portals.
  - `event.offline.clear` validates `message_id` format strictly (32-char IDs); keep payload validation explicit.

## Box Network and Deployment Notes

- Document required outbound access to OAuth/auth-related endpoints.
- Document required inbound access for event/webhook handlers.
- Include firewall/IP update policy if infrastructure relies on allowlists.
- For iframe-based UI apps, ensure frame headers allow embedding in Bitrix24:
  - avoid conflicting `X-Frame-Options` across proxy/app layers.

## Minimal Integration Deliverables

- Auth model decision (`webhook` vs `oauth`).
- Scope matrix and permission rationale.
- Runtime capability matrix (`scope`/`method.get`/`feature.get` checks).
- Event registration map and handler verification strategy.
- Offline-event processing contract (if used): claim, ack, error, retry.
- Retry/idempotency/error-handling contract.
- Limits/backoff strategy (`QUERY_LIMIT_EXCEEDED`, operating windows).
- Rollback and operational diagnostics plan.
