# Project Profile (Current Baseline)

Use this file as fixed defaults for this skill instance.

## Scope

- Platform: 1C-Bitrix Site Management, Bitrix24 box, and Bitrix24 cloud.
- Task types: module, component, integration, dorabotka/feature, fix/debug, update/release, QA/testing.
- Project mode: new and existing codebases.

Cloud platform boundary:

- Bitrix24 cloud supports REST-app integration flows in this skill.
- Bitrix24 cloud does not use filesystem module/component development in this skill.

## Runtime Baseline

- Site Management and Bitrix24 box:
  - PHP: 8.0+.
  - MySQL: 8.0+.
- Bitrix24 cloud:
  - runtime stack constraints are managed by platform; focus on REST auth/scopes/events and integration behavior.

## Intake Behavior

- Do not re-ask baseline constraints unless user input conflicts with them.
- Ask clarifying questions only for blockers that materially affect architecture, safety, or delivery.
- When done criteria are missing, use temporary acceptance contract from `SKILL.md` and mark it as assumption.

## Priority Policy

1. Preserve production safety and backward compatibility for existing projects.
2. Keep D7-first implementation approach.
3. Prefer minimal-change delivery for fixes and incidents.
4. Prefer clear modular boundaries for new development.
5. For update tasks, require explicit migration and rollback artifact coverage.
6. For Bitrix24 REST tasks, require explicit auth/scope/event safety decisions.
7. For Bitrix24 cloud requests, avoid module/component filesystem implementation assumptions.
