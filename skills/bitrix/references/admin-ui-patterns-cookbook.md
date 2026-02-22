# Bitrix Admin UI Patterns Cookbook

Use this file when building or refactoring Bitrix admin pages for modules/components/integrations.

This cookbook complements:

- `references/admin-ui.md` (baseline standards)
- `references/admin-ui-strict-rules.md` (blocker-level MUST/MUST NOT)

## 1) Admin File Topology (Safe-by-Default)

For module-owned admin UI:

```text
local/modules/<vendor.module>/
  admin/
    menu.php
    <entity>_list.php
    <entity>_edit.php
  options.php
  lang/<lang>/admin/<entity>_list.php
  lang/<lang>/admin/<entity>_edit.php

bitrix/admin/
  <vendor_module>_<entity>_list.php   # thin proxy
  <vendor_module>_<entity>_edit.php   # thin proxy
```

Rules:

- Keep business logic in module admin files only.
- Keep `/bitrix/admin/*.php` files as `require_once` proxies.
- Always include admin prolog/epilog in module page implementation.

## 2) Bootstrap and Access Patterns

### Full page mode

Use for normal admin rendering:

```php
require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_before.php');
// ...permission checks and request handling...
require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_after.php');
// ...render...
require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/epilog_admin.php');
```

### List/AJAX mode

Use for side-panel/list mode:

```php
if ($isListMode)
{
    require($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_js.php');
}
else
{
    require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_after.php');
}
```

Permission guard patterns:

- Module/global rights check before rendering.
- Entity rights check (example: HL operations like write/delete).
- Abort early with `AuthForm(GetMessage('ACCESS_DENIED'))` when forbidden.

## 3) Admin Menu Pattern (`admin/menu.php`)

Menu payload is an array with:

- `parent_menu`, `section`, `sort`
- `text`, `title`, `url`
- `icon`, `page_icon`
- `items_id`, `items`, `more_url`

Pattern:

1. Include module and return `false` if unavailable.
2. Build leaf items.
3. Filter by rights (remove forbidden items, do not show empty branches).
4. Return menu tree; return `false` if empty.

Minimal skeleton:

```php
if (!\Bitrix\Main\Loader::includeModule('vendor.module'))
{
    return false;
}

$items = [
    [
        'text' => Loc::getMessage('VENDOR_MENU_LIST'),
        'url' => 'vendor_entity_list.php?lang='.LANGUAGE_ID,
        'module_id' => 'vendor.module',
        'items_id' => 'vendor_entity_list',
        'more_url' => ['vendor_entity_edit.php'],
    ],
];

if (empty($items))
{
    return false;
}

return [
    'parent_menu' => 'global_menu_services',
    'section' => 'vendor',
    'sort' => 600,
    'text' => Loc::getMessage('VENDOR_MENU_ROOT'),
    'title' => Loc::getMessage('VENDOR_MENU_ROOT'),
    'icon' => 'vendor_menu_icon',
    'page_icon' => 'vendor_page_icon',
    'url' => 'vendor_entity_list.php?lang='.LANGUAGE_ID,
    'items_id' => 'menu_vendor',
    'items' => $items,
];
```

## 4) Module Settings Page Pattern (`options.php`)

Use `CAdminTabControl` and strict POST pipeline:

1. Build tabs.
2. Detect action (`save` / `apply` / `reset`).
3. Validate `check_bitrix_sessid()`.
4. Save options.
5. Always redirect (PRG pattern).

Skeleton:

```php
$aTabs = [
    ['DIV' => 'edit1', 'TAB' => Loc::getMessage('MAIN_TAB_SET'), 'TITLE' => Loc::getMessage('MAIN_TAB_TITLE_SET')],
];
$tabControl = new CAdminTabControl('tabControl', $aTabs);

if ($request->isPost() && $currentAction !== null && check_bitrix_sessid())
{
    // save/reset
    LocalRedirect($APPLICATION->GetCurPage().'?...&'.$tabControl->ActiveTabParam());
}

$tabControl->Begin();
?>
<form method="post" action="<?= $APPLICATION->GetCurPage()?>?...">
    <?php
    $tabControl->BeginNextTab();
    ?>
    <tr>
        <td width="40%"><label for="my_opt">My option</label></td>
        <td width="60%">
            <input type="hidden" name="my_opt" value="N">
            <input type="checkbox" id="my_opt" name="my_opt" value="Y">
        </td>
    </tr>
    <?php
    $tabControl->Buttons();
    echo bitrix_sessid_post();
    ?>
</form>
<?php
$tabControl->End();
```

Why this pattern:

- Prevents double-submit.
- Preserves active tab.
- Matches core moderation expectations.

## 5) List + Filter Pattern (`CAdminList` + `CAdminFilter`)

Best for classic admin table flows and HL row-style pages.

Creation order:

1. `$sTableID`, `CAdminSorting`, `CAdminList`.
2. `AddHeaders(...)`.
3. Build filter fields and `InitFilter(...)` or `CAdminFilter`.
4. Process inline edits (`EditAction`) and mass actions (`GroupAction`) with session check.
5. Query data and build `CAdminResult`.
6. Build rows (`AddRow`, `AddViewField`, `AddInputField`, `AddActions`).
7. `AddGroupActionTable(...)`.
8. `AddAdminContextMenu(...)` for primary create actions.
9. `CheckListMode()`.
10. Render filter and `DisplayList()`.

Skeleton:

```php
$sTableID = 'tbl_vendor_entity';
$oSort = new CAdminSorting($sTableID, 'ID', 'desc');
$lAdmin = new CAdminList($sTableID, $oSort);

$lAdmin->AddHeaders([
    ['id' => 'ID', 'content' => 'ID', 'sort' => 'ID', 'default' => true],
    ['id' => 'NAME', 'content' => Loc::getMessage('VENDOR_F_NAME'), 'sort' => 'NAME', 'default' => true],
]);

$filterFields = ['find_id', 'find_name'];
$lAdmin->InitFilter($filterFields);
$find_id = (int)($find_id ?? 0);
$find_name = trim((string)($find_name ?? ''));

if ($lAdmin->EditAction() && check_bitrix_sessid())
{
    foreach ($lAdmin->GetEditFields() as $id => $fields)
    {
        if (!$lAdmin->IsUpdated($id))
        {
            continue;
        }
        // update($id, $fields)
    }
}

if (($ids = $lAdmin->GroupAction()) && check_bitrix_sessid())
{
    $action = $lAdmin->GetAction();
    foreach ($ids as $id)
    {
        // delete/activate/deactivate...
    }
}
```

### User fields in lists

If entity uses UF:

- add UF headers via `$USER_FIELD_MANAGER->AdminListAddHeaders(...)`
- add UF filter fields via `AdminListAddFilterFields(...)`
- render UF values via `$USER_FIELD_MANAGER->AddUserFields(...)`

This is critical for HL blocks and custom entities with UF fields.

## 6) Employee-Style List Pattern (`CAdminUiList`)

For rich filters, pagination, and modern admin list UX (as in employee lists).

Core sequence:

1. `CAdminUiSorting` + `CAdminUiList`.
2. Define filter schema (`id`, `type`, `items`, `default`, `filterable`).
3. `$lAdmin->AddFilter($filterFields, $arFilter)`.
4. Build ORM query with UI pagination.
5. Add rows/actions.
6. `AddGroupActionTable`, `AddAdminContextMenu`, `CheckListMode`.
7. `DisplayFilter($filterFields)` + `DisplayList()`.

When to choose:

- Many filter fields.
- Need UI filter presets.
- Need stable behavior for employee-like registries.

## 7) Edit Form Pattern (`CAdminTabControl` / `CAdminForm`)

Use for entity create/edit pages with tabs.

Pipeline:

1. Define tabs.
2. Resolve create/update mode.
3. Process `save/apply/delete` with `check_bitrix_sessid()`.
4. Use `LocalRedirect` with `$tabControl->ActiveTabParam()`.
5. Render context menu.
6. Show errors/messages.
7. Render tabs and footer buttons.

Hidden/metadata block pattern:

```php
$tabControl->BeginEpilogContent();
echo bitrix_sessid_post();
?>
<input type="hidden" name="ID" value="<?= (int)$ID ?>">
<input type="hidden" name="lang" value="<?= LANGUAGE_ID ?>">
<?php
$tabControl->EndEpilogContent();
```

### Custom complex fields in tabs

Use `BeginCustomField/EndCustomField` for:

- composite controls (selector + hidden input)
- file/image controls with helper UI
- large embedded widgets

Do not replace tab layout with arbitrary `<div>` forms.

## 8) Context Menu Pattern

### Edit pages

Use `CAdminContextMenu`:

```php
$aMenu = [
    ['TEXT' => Loc::getMessage('VENDOR_BACK'), 'LINK' => 'vendor_entity_list.php?lang='.LANGUAGE_ID, 'ICON' => 'btn_list'],
];
$context = new CAdminContextMenu($aMenu);
$context->Show();
```

### List pages

Use `$lAdmin->AddAdminContextMenu($aContext)` and keep primary create action there.

## 9) Notification/Note/Progress Patterns

### Success / info / error

- `CAdminMessage::ShowNote($message)`
- `CAdminMessage::ShowMessage($messageOrArray)`
- `ShowError(...)` for legacy cases

Error with details:

```php
CAdminMessage::ShowMessage([
    'MESSAGE' => Loc::getMessage('VENDOR_SAVE_ERROR'),
    'DETAILS' => implode("\n", $errors),
    'TYPE' => 'ERROR',
    'HTML' => false,
]);
```

### Inline note blocks

Use:

```php
echo BeginNote();
echo Loc::getMessage('VENDOR_NOTE_TEXT');
echo EndNote();
```

### Long operations and progress bars

Use `TYPE => 'PROGRESS'` in `CAdminMessage::ShowMessage(...)`:

```php
CAdminMessage::ShowMessage([
    'TYPE' => 'PROGRESS',
    'DETAILS' => '<p>Step 1 done</p><p><b>Step 2</b><br>#PROGRESS_BAR#</p>',
    'HTML' => true,
    'PROGRESS_TOTAL' => $total,
    'PROGRESS_VALUE' => $current,
]);
```

This is the core-safe pattern for import/export style jobs.

## 10) Dialog Pattern (`BX.CAdminDialog`)

Use API-based admin dialogs, not handcrafted dialog HTML.

Example:

```javascript
(new BX.CAdminDialog({
  content_url: '/bitrix/admin/vendor_dialog.php?lang=' + BX.message('LANGUAGE_ID'),
  width: 700,
  height: 400,
  buttons: [BX.CAdminDialog.btnSave, BX.CAdminDialog.btnCancel]
})).Show();
```

## 11) Highloadblock-Specific Admin Pattern

For HL rows:

1. Get HL metadata by `ENTITY_ID`.
2. Rights check with `HighloadBlockRightsTable::getOperationsName(...)`.
3. `compileEntity(...)` and get DataClass.
4. Build list/form using UF manager:
   - `AdminListAddHeaders`
   - `AdminListAddFilterFields`
   - `AddUserFields`
   - `EditFormAddFields`
   - `ShowUserFieldsWithReadyData`
5. Keep copy mode safe for file UF fields (clear file values before save).

## 12) IBlock-Specific Admin Pattern

For iblock-heavy edit pages:

- Use multiple tabs for base fields, SEO, properties, rights.
- Use `BeginCustomField/EndCustomField` for complex controls.
- For option pages, use `CAdminTabControl` and deterministic POST save/redirect.
- For long import/export flows, use PROGRESS messages with incremental steps.

## 13) Anti-Patterns (Do Not Ship)

- Admin page in public layout (`header.php`/`footer.php`).
- Business logic in `/bitrix/admin` proxy file.
- Custom table/filter rendering bypassing admin list APIs.
- Action buttons in arbitrary page body instead of tab/list footer APIs.
- Handcrafted modal shell instead of `BX.CAdminDialog`.
- State-changing operations without `check_bitrix_sessid()`.

## 14) Practical Checklist Before Merge

1. Prolog/epilog and rights checks exist.
2. Proxy file is thin, implementation is in module admin path.
3. List uses `CAdminList` or `CAdminUiList` with standard filter APIs.
4. Edit/settings page uses `CAdminTabControl`/`CAdminForm`.
5. Context actions are in `CAdminContextMenu` / `AddAdminContextMenu`.
6. Messages/notes/progress use standard admin message APIs.
7. `save/apply/delete/group` actions validate `check_bitrix_sessid()`.
8. `Loc::getMessage(...)` and `lang/` files are used consistently.

## Source Anchors Used

- `/bitrix/modules/highloadblock/admin/menu.php`
- `/bitrix/modules/highloadblock/admin/highloadblock_rows_list.php`
- `/bitrix/modules/highloadblock/admin/highloadblock_row_edit.php`
- `/bitrix/modules/highloadblock/admin/highloadblock_entity_edit.php`
- `/bitrix/modules/iblock/options.php`
- `/bitrix/modules/iblock/admin/iblock_type_edit.php`
- `/bitrix/modules/iblock/admin/iblock_section_edit.php`
- `/bitrix/modules/iblock/admin/iblock_xml_import.php`
- `/bitrix/modules/iblock/admin/iblock_xml_export.php`
- `/bitrix/modules/main/admin/user_admin.php`
- `/bitrix/modules/main/admin/menu.php`
- `/bitrix/modules/main/options.php`
- `/bitrix/modules/rest/options.php`

## Ready Templates

- `references/template-admin-list-cadminlist.md`
- `references/template-admin-edit-tabcontrol.md`
- `references/template-options-tabcontrol.md`
