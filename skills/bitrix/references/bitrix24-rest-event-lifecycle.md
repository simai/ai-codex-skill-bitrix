# Bitrix24 REST Event Lifecycle

Use this guide to design and maintain event-driven REST integrations across install/update/uninstall cycles.

## Lifecycle Stages

1. Install (`OnAppInstall`)
2. Update (new app version deployment)
3. Runtime operations (online/offline events)
4. Uninstall (`OnAppUninstall`)
5. Reinstall

## Install Stage Contract

At install:

- verify request authenticity and save `application_token`
- persist portal identity (`member_id`, `domain`, endpoints)
- run capability probe (`scope`, `method.get`, `feature.get`)
- register required event bindings and placements
- record bind results and version tag

## Update Stage Contract

At update:

- re-run capability probe (portal capabilities can change)
- reconcile required bindings against actual (`event.get`)
- re-bind missing handlers
- apply schema/config migrations idempotently
- keep old bindings cleanup bounded and safe

## Runtime Event Contract

### Online events

- verify `application_token` on every incoming event
- reject unknown portals/tokens
- enqueue heavy work, acknowledge fast

### Offline events

- prefer safe flow `event.offline.get(clear=0)`
- process using `process_id`
- acknowledge via `event.offline.clear`
- mark failures via `event.offline.error`

## Uninstall Stage Contract

At uninstall:

- read `CLEAN` flag and execute cleanup policy
- do not depend on REST API calls after uninstall event (rights are revoked)
- keep local cleanup deterministic and idempotent
- keep uninstall logs for audit

## Reinstall Behavior

Treat reinstall as new install with existing residue possibility:

- reinitialize token and capability profile
- recreate required bindings
- repair stale local state if previous uninstall used `CLEAN=0`

## Method Confirm Lifecycle

For methods requiring admin approval:

- handle `METHOD_CONFIRM_WAITING`
- store pending call context by token/method
- consume `OnAppMethodConfirm`
- execute pending call only if confirmed

## Operational Monitoring

Track:

- binding health (expected vs actual)
- event handler auth failures (`application_token` mismatch)
- offline queue lag and error-marked items
- retry storms and rate-limit errors

## Recovery Playbook

If events stop arriving:

1. verify installation finished
2. verify handler endpoint reachability from public internet
3. verify bindings via `event.get`
4. rebind missing handlers
5. validate token/profile consistency

## Deliverables

- lifecycle sequence notes (install/update/runtime/uninstall)
- binding matrix (event, mode, handler, owner)
- recovery checklist
- security checks (`application_token`, portal identity)
