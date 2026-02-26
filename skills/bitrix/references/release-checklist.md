# Release Checklist

Run this checklist before final delivery.

## Correctness

- Functional scenario from acceptance criteria passes.
- Affected edge cases are verified.
- No unintended behavior changes in nearby flows.
- Scope is minimal and limited to requested change set.

## Data and Migrations

- Install/update or migration steps are explicit.
- Data changes are reversible or rollback-safe.
- Compatibility strategy is documented for existing records.
- For update tasks, Migration Notes exist even when there are no schema/data changes.

## Site Module/Component Hardening (Site Management / Box)

- Visual editor compatibility is validated for editable component pages (params prefilled).
- Public folders and shared data directories use ownership markers before uninstall deletion.
- Component folders copied to `/bitrix/components` are force-cleaned on uninstall (`DeleteDirFilesEx` path check).
- Per-site iblock type/code bindings are validated on fresh install and reinstall.

## Security

- Input validation and output escaping are in place where applicable.
- Access/permission checks are explicit for admin and API operations.
- Secrets are not hardcoded; storage approach is defined.
- Session/CSRF checks exist for state-changing actions.

## Bitrix24 REST Integration (when applicable)

- Auth model is justified (`webhook` or `oauth`) and secrets are protected.
- Scope set is least-privilege and required methods are confirmed available.
- Runtime capability checks are implemented (`scope`, `method.get`, `feature.get` where relevant).
- Event handler authenticity checks are implemented (`application_token` validation where relevant).
- Batch/pagination usage respects platform constraints.
- Token refresh behavior is safe and not over-polling auth endpoints.
- Rate-limit strategy exists for `QUERY_LIMIT_EXCEEDED` and operating-window pressure.
- Offline-event flow (if used) has explicit `get/list/clear/error` contract with `process_id`.

## Performance and Stability

- Cache behavior is defined and invalidation points are clear.
- Integration calls have timeout and retry boundaries.
- Failure handling is deterministic and observable.

## Operability

- Logs are actionable and identify operation context.
- Deployment steps are explicit.
- Rollback path is documented.
- Version metadata is updated when release/update scope requires it.
- For iframe UI apps, frame headers are compatible with Bitrix24 embedding.

## Marketplace Publication (when applicable)

- App card quality is complete (name, description, screenshots/icon, support channels/SLA).
- Legal/compliance links are valid (license/privacy) and match app identity.
- External integration prerequisites and pricing dependencies are disclosed.
- Test credentials/sandbox access for moderators are prepared (private channel only).
- Install, uninstall, and reinstall were validated on clean test portals.
- Admin and regular-user flows were validated when permission model differs.

## Testing

- Smoke checks are completed.
- Regression minimum checks are completed for touched flows.

## Delivery Output

- Plan and changed file list with rationale.
- Setup/migration instructions.
- Verification steps and expected results.
- Mode-specific artifacts (Migration/Upgrade/Release/Changelog/QA when applicable).
- Known risks and follow-up items.
