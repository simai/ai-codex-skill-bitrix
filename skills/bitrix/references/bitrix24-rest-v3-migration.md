# Bitrix24 REST v3 Migration Guide

Use this guide when deciding whether to move REST integrations from v2 endpoints to v3 endpoints.

## Core Constraint

REST v3 is called through `/rest/api/...` routes and currently has partial functional coverage.

Practical implication:

- many projects must run in hybrid mode (`v2 + v3`) for a period.

## Decision Matrix

Choose per use case, not globally.

Use v3 when:

- target method exists in v3 and is stable in your portal edition
- unified response format reduces parser complexity
- relation loading in one call reduces request count

Keep v2 when:

- method is not available in v3
- SDK/runtime stack does not support your required v3 call path
- migration risk is higher than expected operational gain

Use hybrid when:

- read/search paths can move to v3 first
- write/edge flows still depend on v2

## Pre-Migration Checks

Per portal, verify:

1. method availability via `method.get`
2. scope availability via `scope`
3. response shape compatibility for current parser
4. load behavior with production-like pagination/filter payloads

## Migration Strategy (Phased)

1. Inventory current v2 methods and classify by business criticality.
2. Map each method to target state: `v3`, `v2`, or `hybrid`.
3. Build transport abstraction so endpoint version is a routing concern, not business-logic concern.
4. Add response normalization layer for mixed result shapes.
5. Roll out by slices (low-risk read paths first, then write paths).
6. Keep rollback switch per method/group.

## Compatibility Risks

- route mismatch (`/rest/...` vs `/rest/api/...`)
- payload format assumptions in old SDK wrappers
- field naming/shape differences in DTO-like responses
- filtering semantics differences in complex queries

## Reliability Rules

- keep idempotency keys/guards unchanged during migration
- preserve retry policy, but tag retries with endpoint version for diagnostics
- monitor `time.operating` and `time.operating_reset_at` on both paths

## Rollback Contract

For each migrated method group maintain:

- feature flag key
- fallback target (`v2`)
- max rollback time
- owner/on-call contact

## Verification Checklist

- same business result from v2 and v3 for control dataset
- no regression in permission/scopes behavior
- no increase in error rate or p95 latency beyond allowed threshold
- rollback path tested before release

## Deliverables

- migration map (`method -> v2/v3/hybrid`)
- phased rollout plan
- rollback instructions
- post-migration monitoring plan
