# Bitrix24 Box Source Analysis Guide

Use this guide when user provides full Bitrix24 box source and asks to extract reusable engineering patterns.

## 1) High-Value Paths

Inspect in this order:

1. `bitrix/modules/<module>/install/index.php`:
   - install/uninstall flow contract,
   - event/agent registration lifecycle,
   - DB script execution pattern.
2. `bitrix/modules/<module>/install/version.php`:
   - module version source and release metadata.
3. `bitrix/modules/<module>/install/db/{mysql,pgsql}/*.sql`:
   - schema ownership and cleanup model.
4. `bitrix/modules/<module>/install/admin/*.php`, `bitrix/admin/*.php`, `bitrix/modules/<module>/admin/*.php`:
   - proxy style and admin UI entry pattern.
5. `bitrix/modules/rest/*`:
   - OAuth/event/offline-event implementation constraints.

## 2) Extraction Rules

Extract only stable, reusable patterns:

- lifecycle symmetry (`Install*`/`UnInstall*`),
- permission and session checks for admin entrypoints,
- DB-type-aware install scripts,
- safe handler registration/unregistration,
- idempotency and cleanup behavior.

Ignore:

- generated/minified frontend bundles,
- product-specific business content, marketing assets,
- environment-specific secrets and host paths.

## 3) Current Box Snapshot Notes (from latest provided source)

- Approximate module count under `bitrix/modules`: `98`.
- Modules with `install/index.php`: `98`.
- Modules with `install/version.php`: `97` (core `main` uses internal version constants).
- Admin proxy pattern is consistent:
  - `bitrix/admin/<file>.php` usually `require_once` to module admin file.
- REST module uses explicit install/uninstall symmetry for:
  - event handlers,
  - auth providers,
  - agents.
- REST install adds URL rewrite rules and marketplace/public routes; handle route lifecycle explicitly in custom modules.
- `crm` install flow enforces preconditions before side effects:
  - feature availability gate,
  - required module checks (example: `sale` must be installed).
- `sale` and `rest` installers use step-based UI flow (`step1/step2`, `unstep1/unstep2`).
- Core modules combine legacy and D7 event wiring:
  - `RegisterModuleDependences(...)` and
  - `EventManager::registerEventHandler(...)`.
  Uninstall must clear both layers.
- Agent cleanup pattern is consolidated with `CAgent::RemoveModuleAgents('<module>')` instead of removing one by one.
- REST provider patterns in core:
  - large domain APIs can use one dispatcher with method registry (`crm`),
  - focused APIs map methods directly to handlers (`sale` pay-system service).

Treat these as strong defaults for custom module design unless project conventions explicitly differ.

## 4) Integration Into Skill

When new useful pattern is found:

1. Put concise rule in the closest existing reference (`module-contract`, `admin-ui`, `bitrix24-rest-integration`, etc.).
2. If pattern is broad and source-analysis-specific, keep it in this file.
3. If pattern is implementation-heavy and reusable, add/update corresponding `template-*.md` starter.
4. Avoid copying large code fragments; prefer short rule statements.
