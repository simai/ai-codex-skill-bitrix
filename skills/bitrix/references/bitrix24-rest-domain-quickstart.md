# Bitrix24 REST Domain Quickstart

Use this quickstart for REST integration tasks focused on one business domain (`CRM`, `Tasks`, `User`, `Disk`).

## 0) Start Conditions

Required inputs:

- platform (`Bitrix24 cloud` or `Bitrix24 box`)
- auth model (`webhook` or `oauth`)
- target domain (`crm/tasks/user/disk`)
- project root path for artifacts

Base references:

- `references/bitrix24-rest-integration.md`
- `references/bitrix24-rest-docs-triage.md`
- `references/bitrix24-rest-event-lifecycle.md`

## 1) Capability Bootstrap First

Before coding, build capability profile for portal:

- scopes via `scope`
- methods via `method.get`
- features via `feature.get`

Template:

- `references/template-rest-capability-bootstrap.md`

Blocking rule:

- if required method/scope is missing, stop implementation and produce fallback contract.

## 2) Choose Domain Pack

- CRM: `references/bitrix24-rest-domain-crm.md`
- Tasks: `references/bitrix24-rest-domain-tasks.md`
- User: `references/bitrix24-rest-domain-user.md`
- Disk: `references/bitrix24-rest-domain-disk.md`

Each pack defines:

- source triage (`A/B/C`)
- integration contract
- starter templates
- domain QA checks

## 3) Scaffold Delivery Artifact Template

Generate domain-specific artifact skeleton:

```bash
python3 skills/bitrix/scripts/scaffold_artifacts.py \
  --out "<project_root>/artifacts/rest" \
  --preset rest_<domain>
```

Examples:

```bash
python3 skills/bitrix/scripts/scaffold_artifacts.py --out "artifacts/rest" --preset rest_crm
python3 skills/bitrix/scripts/scaffold_artifacts.py --out "artifacts/rest" --preset rest_tasks
python3 skills/bitrix/scripts/scaffold_artifacts.py --out "artifacts/rest" --preset rest_user
python3 skills/bitrix/scripts/scaffold_artifacts.py --out "artifacts/rest" --preset rest_disk
```

All-at-once option:

```bash
python3 skills/bitrix/scripts/scaffold_artifacts.py \
  --out "<project_root>/artifacts/rest" \
  --preset rest_all
```

## 4) Fill Artifact Sections in Fixed Order

Use generated template and complete in this order:

1. `Integration Plan`
2. `Scope and Permission Matrix`
3. `Capability and Method Matrix`
4. `Event Map and Handler Safety`
5. `Retry and Idempotency Contract`
6. `Verification Checklist`
7. `QA Summary`

Rule:

- do not skip risk and fallback fields, even if status is `N-A`.

## 5) Run QA Gate

Use:

- `references/testing-qa.md`
- `references/qa-gate-checklist.md`

Static-first then dynamic:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "<project_root>" \
  --module-id "<vendor.module-or-app-id>" \
  --report "<project_root>/artifacts/rest/qa-run-report.md"
```

If local Bitrix kernel is unavailable:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "<project_root>" \
  --module-id "<vendor.module-or-app-id>" \
  --skip-integration \
  --report "<project_root>/artifacts/rest/qa-run-report.md"
```

## 6) Final Delivery Set

For each domain task, publish:

- filled domain artifact pack (`rest-domain-<domain>-artifact-pack.md`)
- QA report with `A-I` and domain addendum
- risk-sorted fix backlog
- rollback notes for risky operations

Reference examples:

- `examples/rest-domain-artifacts/README.md`
- `examples/rest-domain-artifacts/crm.md`
- `examples/rest-domain-artifacts/tasks.md`
- `examples/rest-domain-artifacts/user.md`
- `examples/rest-domain-artifacts/disk.md`

