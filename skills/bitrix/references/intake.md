# Bitrix Intake Template

Use this template to collect only data that materially affects architecture or implementation.

## Minimum Required

- Business goal: what must be achieved and why.
- Work type: module, component, integration, feature, fix, optimization, update, packaging, QA.
- Platform: 1C-Bitrix Site Management, Bitrix24 box, or Bitrix24 cloud.
- Repository context: new project or existing codebase; main target paths.
- Runtime constraints: PHP version, DB, cache model, queue/background jobs.
- Acceptance criteria: clear done condition and validation scenario.

Use preset defaults when user does not specify runtime:

- For Site Management and Bitrix24 box:
  - PHP 8.0+.
  - MySQL 8.0+.
- For Bitrix24 cloud:
  - apply REST integration defaults; do not request filesystem module/component paths.

## Strongly Recommended

- Bitrix core version and known project standards.
- Existing module/component names and namespaces.
- Required backward compatibility window.
- Security and compliance constraints.
- Performance target (response time, load, resource limits).
- Deployment strategy (manual, CI/CD, staged rollout).

## Task-Specific Questions

### New Module

- Module ID format and vendor namespace.
- Required install/uninstall behavior.
- Admin settings/options and permission model.
- Expected public API (services/events/hooks).

### Existing Module Change

- Current behavior and problem statement.
- Compatibility constraints for existing consumers.
- Data migration/update requirements.
- Rollback strategy for production.

### Update by Diff/Commits

- Commit/tag range or changed file list.
- Source and target module version.
- Expected schema/data changes.
- Required release artifacts.

### Component Work

- Component scope and template boundaries.
- Data source and caching strategy.
- SEO/composite constraints if relevant.
- Required parameters and expected output contract.

### Integration Work

- Counterparty systems and data contracts.
- Authentication method and secrets handling.
- Integration model: incoming webhook, local app (OAuth), or marketplace app.
- Target scope set and permission boundaries.
- Event model: online events, offline events, or polling strategy.
- Idempotency keys and retry policy.
- Observability: logs, alerts, failure paths.

### Bitrix24 Cloud REST App Work

- App type: local integration or marketplace app.
- Install model: install master UI, install callback, or API-only flow.
- Required scopes and user-role constraints.
- Token lifecycle strategy (refresh and secure storage).
- Event safety model (`application_token` validation, queueing, retries).

### QA/Testing

- Critical scenarios to test.
- Required evidence format (logs/screenshots/SQL checks).
- Risk tolerance and release gate level.

## Fast Intake Mode

If user provides partial requirements:

1. Extract known facts.
2. Mark unknown blockers.
3. Ask only blocker questions.
4. Start with safe assumptions and label them explicitly.

If acceptance criteria are missing, initialize temporary done criteria:

1. Primary business scenario passes.
2. No regression in touched behavior.
3. Setup/migration steps are documented.
4. Rollback path is documented.
