# Admin UI Strict Rules (Blocker-Level)

Use this reference when task requires strict validation or generation of Bitrix admin pages, forms, lists, and dialogs.

## 1) Admin Page Bootstrap

MUST:

- Start with admin prolog (`prolog_admin_before.php` or `prolog_admin.php` when appropriate).
- End with `epilog_admin.php`.
- Perform permission checks before rendering UI.

MUST NOT:

- Include public `header.php` / `footer.php`.
- Use public site templates or wrappers in admin pages.

Blocker:

- Any admin page that runs in public layout context is invalid and must be reworked.

## 2) File Placement and Proxy Pattern

MUST:

- Keep real admin page implementation in module path:
  - `/bitrix/modules/<vendor.module>/admin/<page>.php`
- Keep `/bitrix/admin/<vendor_module>_<page>.php` as thin proxy only:
  - `require($_SERVER["DOCUMENT_ROOT"]."/bitrix/modules/<vendor.module>/admin/<page>.php");`

MUST NOT:

- Duplicate business logic in proxy and implementation files.

## 3) Admin Forms

MUST:

- Build forms with `CAdminTabControl` (at least one tab).
- Keep fields inside tab body and standard table rows (`<tr>`).
- Use canonical two-cell row structure:
  - Left cell: label (`adm-detail-content-cell-l`)
  - Right cell: input (`adm-detail-content-cell-r`)
- Render actions in footer area after `$tabControl->Buttons()`.
- Keep notes in admin-style blocks (`BeginNote()/EndNote()` or `CAdminMessage`).
- Protect state-changing requests with `check_bitrix_sessid()`.

MUST NOT:

- Place action buttons in body rows, notes, or outside tab footer flow.
- Build ad-hoc tabs/forms with arbitrary `<div>` layout as replacement for `CAdminTabControl`.
- Use custom non-standard left/right cell classes for main form rows.

## 4) Admin Lists

MUST:

- Place filter above the table.
- Use standard filter API (`CAdminFilter` or `CAdminList->InitFilter()`).
- Build list table through `CAdminList` (or project-approved `CAdminUiList` equivalent).
- Define headers explicitly in one structure.
- Add rows through `AddRow(...)` with stable unique row IDs.
- Add row actions through `$row->AddActions(...)`.
- Add group actions through `AddGroupActionTable(...)`.
- Put primary create action in table header/context menu (`CAdminContextMenu`).
- Use table footer for navigation and bulk operations (`DisplayList()` flow).

MUST NOT:

- Put filter inside table body.
- Render custom checkboxes/actions bypassing list APIs.
- Put row action links directly inside cells as ad-hoc controls.
- Split one logical list into multiple independent tables without clear UX reason.

## 5) Admin Dialogs

MUST:

- Build modals with standard admin dialog API (`BX.CAdminDialog` or project-approved wrapper).
- Keep dialog structure in API terms: header, body, footer buttons.
- Pass content as HTML string or DOM node/container.
- Bind actions via dialog button config or proper `BX` events.
- Set stacking concerns (for nested dialogs like `BXFileDialog`) via dialog config.
- Keep source DOM container visible before handing it to dialog if using existing nodes.
- Keep small dialogs compact; avoid arbitrary large fixed heights.

MUST NOT:

- Handcraft admin dialog shell HTML classes (`bx-core-window`, `bx-core-adm-dialog-*`) as if it were API output.
- Replace admin modal behavior with public Bootstrap/custom modal frameworks in admin context.
- Inline fake dialog headers/footers in content payload.

Blocker:

- Hand-rolled admin dialog chrome is invalid and must be replaced by standard API usage.

## 6) Quick Review Gates

Before accepting admin UI work, verify:

- Admin page uses prolog/epilog and access checks.
- Proxy file is thin and module file owns behavior.
- Form uses `CAdminTabControl` and canonical row layout.
- List uses standard filter/list/action APIs.
- Dialog uses `BX.CAdminDialog` (or accepted wrapper) without handcrafted shell.
