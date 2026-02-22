# Update and Release Runbook

Apply for updates derived from diff/commits, version bumps, and release packaging.

## Inputs

- Start and end commit/tag (or changed files list).
- Current and target version.
- Scope of schema or data changes.
- Target environment specifics if they affect behavior.

## Diff-to-Release Workflow

1. Collect changed files list.
2. Classify changes: code, install, db, lang, assets, config.
3. Determine schema/data impact and backward compatibility risk.
4. Build `Migration Notes` (always).
5. Build `Upgrade Notes`.
6. Build `Release Notes` or `Changelog Fragment`.
7. Prepare regression checklist and rollback steps.

## Mandatory Artifact Rule

For update/data-impact tasks, `Migration Notes` must exist even when no migrations are needed.

When no DB/data change exists, use explicit text:

- Schema changes: `No schema changes`
- Data changes: `No data changes`
- Rollback: `Not applicable / No changes`

## Rollback and Verification

- Describe rollback steps for schema/data changes.
- Add post-update verification checks for key flows.
- Keep rollback feasible for production constraints.
- For structured rollback artifact, use `references/template-migration-rollback-notes.md`.

## Release Discipline

- Update module version metadata.
- Keep release notes and changelog aligned with delivered change scope.
- Preserve minimal patch principle; do not include unrelated changes.

## Marketplace Packaging Notes

- Verify release package composition and version consistency.
- Ensure required release artifacts are complete before packaging.
- Apply `references/bitrix24-marketplace-publication.md` for moderator-ready checks.
