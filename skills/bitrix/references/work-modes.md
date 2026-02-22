# Work Modes Router

Pick exactly one primary mode before implementation. Use secondary references only when needed.

## 1) New Module

Use when creating a module from scratch.

Required outputs:

- Plan
- Patch list
- Module structure outline
- Release Notes or Changelog Fragment

Use with:

- `references/module-contract.md`
- `references/blueprints.md`

## 2) Project Change (Feature/Fix)

Use for minimal scope changes in existing module/project code.

Required outputs:

- Plan
- Patch list
- Regression checklist
- Release Notes or Changelog Fragment for release-scoped changes

Use with:

- `references/blueprints.md`
- `references/testing-qa.md`

## 3) Update by Diff/Commits

Use when update scope is defined by commit range, tag range, or file diff.

Required outputs:

- Plan
- Patch list or classified diff summary
- Migration Notes (always, including explicit "No changes" sections)
- Upgrade Notes
- Changelog Fragment or Release Notes
- Regression checklist

Use with:

- `references/update-and-release.md`
- `references/template-migration-notes.md`
- `references/template-upgrade-notes.md`

## 4) Marketplace Packaging

Use when preparing a release package for Bitrix Marketplace.

Required outputs:

- Packaging checklist
- Release Notes
- Changelog Fragment
- Regression checklist
- Moderator precheck notes (scopes, placements, install/uninstall/reinstall evidence)

Use with:

- `references/update-and-release.md`
- `references/bitrix24-marketplace-publication.md`
- `references/release-checklist.md`

## 5) Testing / QA

Use when primary deliverable is verification and risk assessment.

Required outputs:

- QA Report
- Risk-ranked findings
- Re-test plan

Use with:

- `references/testing-qa.md`
- `references/qa-gate-checklist.md`
- `references/template-qa-report.md`
- `references/template-qa-audit-prompt.md`
- `references/root-testing-toolkit.md`
- `references/troubleshooting.md`
- `scripts/scaffold_qa_gate.py`
- `scripts/scaffold_root_tests.py`
- `scripts/qa_run.py`
- `examples/seeds/README.md`
- `examples/ci/github-actions-bitrix-qa.yml`

## 6) Documentation Update

Use when docs/runbooks/ADR/troubleshooting must be updated after code changes.

Required outputs:

- Documentation change list
- Updated verification steps
- Rollback/constraints notes for risky operations

Use with:

- `references/update-and-release.md`

## 7) Bitrix24 REST App Integration (Cloud and Box)

Use for webhook/OAuth-based integrations, app installation flows, and event-driven synchronization.

Platform notes:

- In Bitrix24 cloud, this is the primary development mode.
- In Bitrix24 box, use this mode for REST app/integration parts alongside module code when needed.

Required outputs:

- Integration plan
- Auth model decision (`webhook` or `oauth`)
- Scope and permission matrix
- Event map and handler safety notes
- Retry/idempotency and failure-handling contract
- Verification checklist

Use with:

- `references/bitrix24-rest-integration.md`
- `references/testing-qa.md`
