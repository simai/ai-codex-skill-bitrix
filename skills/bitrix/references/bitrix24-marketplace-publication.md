# Bitrix24 Marketplace Publication Guide

Apply this guide when preparing first publication or updates for Bitrix24 Marketplace apps.

## 1) When to Apply

- New marketplace app submission.
- Updated app version submission.
- Card/content edits that require re-moderation.
- Region expansion for an existing app.

## 2) Technical Pre-Moderation Gates

- Validate install on a clean portal where app was never installed.
- Validate uninstall and repeated reinstall on the same portal.
- Do not use only the development portal as final verification evidence.
- Validate critical flows for both admin and regular-user permissions where behavior differs.
- For API-only apps:
  - installation callback must receive/store OAuth tokens securely,
  - callback is backend flow; do not use `BX24.installFinish()` there.
- Ensure all callback/handler URLs are publicly reachable from Bitrix24 side.
  - URL availability checks should return valid success/redirect status (`200/301/302`).
- Ensure REST event bindings are restored by install/update logic.
- Verify uninstall cleanup for app-side stored portal data:
  - tokens,
  - cached object mappings,
  - integration credentials and temporary sync state.

## 3) Card and Scope Quality Gates

- Use clear app name, accurate description, and production-ready icon/screenshots.
- Describe setup steps concretely; do not rely on generic docs links only.
- Explicitly disclose:
  - required Bitrix24 tariff/features,
  - functional limits,
  - required external systems/services,
  - additional paid options (if any).
- Request only required scopes; avoid "future" scopes.
- Declare only real widget placements used by app behavior.
- Provide support channels and support schedule (SLA/response windows).
- Keep privacy policy and license links valid and app-specific.

## 4) External Service Integration Requirements

If app depends on external paid/free services:

- Provide link to integrated service site.
- Provide link to service pricing/tariff terms when relevant.
- Provide test credentials or test environment access for moderator checks.
- Ensure moderator can connect integration to their own test Bitrix24 portal.

## 5) Region and Localization Gates

- Fill mandatory language content for target region.
- For western publication paths, provide English-facing materials and localized app UI.
- Keep support/help links language-consistent with target region card language.

## 6) Moderation Workflow Discipline

- Submit explicitly to moderation; draft status alone is not moderation.
- Any rejected submission must be fixed and re-submitted (queue position may restart).
- Description/card/version edits become visible only after moderation approval.
- Keep a moderator-ready changelog of what changed since previous submission.

## 7) Operational Ownership

- App developer owns support for app behavior and integration scenarios.
- For suspected Bitrix24 REST issues, collect reproducible HTTP logs and call details.
- Escalate API issues to Bitrix support with concrete request evidence.

## 8) Delivery Artifacts (Marketplace Mode)

- Packaging checklist.
- Regression checklist/results.
- Release notes and changelog fragment.
- Moderator notes:
  - test credentials (private),
  - tested scenarios list,
  - known limitations and required prerequisites.
