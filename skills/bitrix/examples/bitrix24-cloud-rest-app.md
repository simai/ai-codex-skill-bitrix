# Example: Bitrix24 Cloud REST App

Use for cloud integrations only. Do not generate filesystem module/component paths.

## Input profile

- Platform: Bitrix24 cloud
- Task: integration / REST app
- Auth: webhook or OAuth
- Scope: events, placements, REST methods

## Recommended flow

1. Define auth model (`webhook` vs `oauth`) and scope matrix.
2. Define event map and idempotency/retry policy.
3. Validate install callback and secure token storage.
4. Prepare QA checks for:
   - source/token validation
   - retries and duplicate event handling
   - error logging and observability

## QA command pattern

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/cloud-app-project" \
  --module-id "vendor.cloudapp" \
  --skip-integration
```

`--skip-integration` is acceptable when no local Bitrix kernel is available. Report should explicitly contain `N-A` for integration-dependent areas.

## Expected deliverables

- Integration plan + scope matrix
- Event safety notes
- QA report with A-I sections adapted for cloud runtime constraints
