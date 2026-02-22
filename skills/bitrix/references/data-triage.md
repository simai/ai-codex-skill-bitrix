# Data Triage Rules

Use these rules to decide what incoming user data to keep, defer, or ignore.

## Required Data

Treat as required when data changes code structure, API contracts, or safety:

- Business-critical behavior and acceptance criteria.
- Platform and environment constraints.
- Storage schema, migration, and compatibility requirements.
- Security rules, permission boundaries, and data sensitivity.
- Integration contracts, retry/idempotency behavior.
- For update tasks: commit/tag range (or equivalent diff input) and version transition.
- For Bitrix24 REST tasks: auth model (webhook/oauth), scope set, and event strategy.

Runtime and platform baseline for this skill:

- Default platform set: 1C-Bitrix Site Management, Bitrix24 box, and Bitrix24 cloud.
- Default runtime set for Site Management and Bitrix24 box: PHP 8.0+ and MySQL 8.0+.
- Bitrix24 cloud boundary: REST-app integration only; no filesystem module/component assumptions.
- Do not ask for these again unless user input conflicts.

## Optional Data

Use when available, but do not block implementation unless user marks them mandatory:

- Preferred naming style.
- Non-critical folder naming variations.
- UI copy details that do not alter backend contracts.
- Nice-to-have performance improvements.
- Detailed definition of done (temporary done contract is acceptable until clarified).
- Release artifact formatting preferences.

## Ignore or Defer

Ignore or defer data that does not affect deliverable quality:

- Abstract preferences without acceptance criteria.
- Contradictory requests without priority.
- Hypothetical edge cases unrelated to stated scope.

## Conflict Resolution

When user inputs conflict:

1. Prioritize explicit acceptance criteria.
2. Prioritize security and data integrity over convenience.
3. Prioritize backward compatibility for existing production systems.
4. Escalate with one concise clarification question if still ambiguous.

## Assumption Policy

- Make assumptions only when blocked by missing non-critical details.
- Log assumptions explicitly in delivery notes.
- Keep assumptions reversible and low-risk.
- Prefer baseline defaults from `references/project-profile.md` before asking extra questions.
