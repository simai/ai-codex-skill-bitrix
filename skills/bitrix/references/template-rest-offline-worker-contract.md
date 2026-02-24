# Template: REST Offline Worker Contract

Use this template for queue consumers working with `event.offline.*` APIs.

## Preconditions

- `event.bind` registered with `event_type=offline`
- required features checked (`rest_offline_extended`, `rest_auth_connector`)
- worker has persistent storage for checkpoints and retries

## Processing Model

Safe mode:

1. `event.offline.get` with `clear=0`
2. process events batch (`events[]`) with idempotency checks
3. `event.offline.clear` by `process_id` for successful items
4. `event.offline.error` for failed items

## Batch State Model

States:

- `claimed` (received with `process_id`)
- `processed` (business action completed)
- `acked` (cleared from queue)
- `errored` (flagged via `event.offline.error`)

## Idempotency Rules

- dedupe by (`EVENT_NAME`, `MESSAGE_ID`, portal)
- business writes must be idempotent
- retry must not create duplicate side effects

## Concurrency Rules

- parallel `event.offline.get` is allowed
- each worker logs `process_id` ownership
- ack only items owned by current worker/process

## Failure Handling

- transient errors -> bounded retry with backoff+jitter
- permanent validation errors -> mark via `event.offline.error`
- worker crash recovery -> resume by pending `process_id` journal

## Metrics

Track:

- queue lag
- processed/sec
- retries count
- error-marked messages
- ack latency

## Exit Criteria for Release

- no unbounded retries
- idempotency confirmed on repeated replays
- clear/error flows validated on stage
