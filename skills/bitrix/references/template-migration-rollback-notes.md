# Template: Migration Rollback Notes

Use this artifact for every migration bundle (even if rollback is forward-fix only).

## Scope

- Release version:
- Migration files:
- Affected entities: (`iblock`, `highloadblock`, `UF`, `agents`, options)

## Pre-Rollback Safety Check

1. Confirm maintenance window and responsible engineer.
2. Confirm DB backup snapshot timestamp.
3. Confirm current migration state (`applied` list).
4. Confirm dependent jobs/agents are paused if needed.

## Rollback Strategy

- Type: `full down` / `partial revert` / `forward fix only`
- Data strategy: `restore backup` / `non-destructive disable` / `hard delete`
- Target state definition:

## Step-by-Step

1. Disable user traffic to affected admin flow (if required).
2. Run rollback command/script:
: command
3. Rebuild caches/indexes if needed:
: command
4. Re-enable agents/jobs:
: command
5. Re-enable traffic.

## Verification After Rollback

- Admin pages load without fatal errors.
- Target entities/fields state is consistent.
- Integration events and agents are healthy.
- Smoke tests passed (list/edit/save/delete where applicable).

## Known Data Risks

- Data loss risk:
- Incompatible writes during rollback window:
- Manual reconciliation required:

## Forward-Fix Plan (if no strict down path)

- Hotfix branch:
- ETA:
- Temporary guardrails:

## Sign-Off

- Executed by:
- Verified by:
- Timestamp:
