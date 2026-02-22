# Admin UI Standards

Apply when implementing or changing admin pages, forms, lists, and dialogs.

For detailed creation patterns and ready implementation sequences, also use:

- `references/admin-ui-patterns-cookbook.md`
- `references/iblock-hlblock-patterns.md` (when data is in iblock or highloadblock)
- `references/template-admin-list-cadminlist.md`
- `references/template-admin-edit-tabcontrol.md`
- `references/template-options-tabcontrol.md`

For stricter acceptance gates (blocker rules and micro-structure), also apply `references/admin-ui-strict-rules.md`.

## 1) Entry Point and Access

- Include admin prolog in page start and admin epilog in page end.
- Check permissions before rendering any admin UI.
- Do not use public site `header.php` or `footer.php` for admin pages.

## 2) Placement and Proxies

- Keep admin page implementation inside module folders.
- Keep `/bitrix/admin/*.php` as proxy files only.
- Avoid duplicated logic in both proxy and implementation files.

## 3) Forms

- Use `CAdminTabControl` for settings/edit forms.
- Keep tab content in standard table row layout (`<tr><td>...`).
- Render footer actions through tab control buttons area.
- Avoid ad-hoc form layouts built only with arbitrary `<div>` blocks.

## 4) Lists

- Use standard admin list APIs (`CAdminList` or `CAdminUiList` based on project style).
- Use standard filter APIs instead of hand-rolled filter parsing.
- Keep row actions and bulk actions in standard list action APIs.

## 5) Dialogs

- Use standard admin modal dialog APIs (`BX.CAdminDialog` or accepted project wrapper).
- Avoid custom modal HTML frameworks in admin context unless project already standardizes on them.

## 6) Localization and Safety

- Localize admin text through lang files and `Loc::getMessage(...)`.
- Keep CSRF and session checks for state-changing actions.
- Ensure all outputs are escaped where needed.

## Review Checklist

- Prolog/epilog and permission checks are present.
- Proxy files are thin and only route to module admin files.
- Forms use `CAdminTabControl` with standard layout.
- Lists use standard Bitrix list APIs and filters.
- Dialogs use standard admin dialog APIs.
- Localization and CSRF/session checks are preserved.
- No blocker anti-patterns from `admin-ui-strict-rules.md` are present.
