#!/usr/bin/env python3
"""Scaffold Bitrix module admin skeleton (menu/list/edit/options + proxies)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Tuple


MODULE_ID_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
ENTITY_RE = re.compile(r"^[a-z0-9_]+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a Bitrix admin skeleton for a module: "
            "admin/menu.php, list/edit pages, options.php, lang files, and proxies."
        )
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to project root that contains /local and /bitrix folders.",
    )
    parser.add_argument(
        "--module-id",
        required=True,
        help="Bitrix module ID in form vendor.code (example: vendor.module).",
    )
    parser.add_argument(
        "--entity",
        required=True,
        help="Entity code in snake_case (example: employee).",
    )
    parser.add_argument(
        "--namespace",
        default="Vendor\\Module",
        help="PHP namespace root used in TODO comments. Default: Vendor\\Module",
    )
    parser.add_argument(
        "--lang",
        default="ru",
        help="Language folder for generated lang files. Default: ru",
    )
    parser.add_argument(
        "--skip-project-proxies",
        action="store_true",
        help=(
            "Do not generate direct /bitrix/admin proxies in project root. "
            "Install proxies under local/modules/<module>/install/admin are still generated."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not MODULE_ID_RE.match(args.module_id):
        raise ValueError(
            "Invalid --module-id. Expected vendor.code with lowercase letters, numbers or underscore."
        )
    if not ENTITY_RE.match(args.entity):
        raise ValueError(
            "Invalid --entity. Use snake_case: lowercase letters, numbers, underscore."
        )
    if "\\" not in args.namespace and not args.namespace:
        raise ValueError("Invalid --namespace.")


def pascal_case(value: str) -> str:
    parts = [chunk for chunk in re.split(r"[_\-\.\s]+", value) if chunk]
    return "".join(part[:1].upper() + part[1:] for part in parts)


def fill(template: str, replacements: Dict[str, str]) -> str:
    for key, value in replacements.items():
        template = template.replace(f"__{key}__", value)
    return template


def module_menu_template() -> str:
    return """<?php
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Localization\\Loc;

Loc::loadMessages(__FILE__);

if (!Loader::includeModule('__MODULE_ID__'))
{
\treturn false;
}

global $APPLICATION;
$right = $APPLICATION->GetGroupRight('__MODULE_ID__');
if ($right < 'R')
{
\treturn false;
}

return [
\t'parent_menu' => 'global_menu_services',
\t'section' => '__MODULE_PREFIX__',
\t'sort' => 600,
\t'text' => Loc::getMessage('__MSG_PREFIX___MENU_TEXT'),
\t'title' => Loc::getMessage('__MSG_PREFIX___MENU_TEXT'),
\t'icon' => '__MODULE_PREFIX___menu_icon',
\t'page_icon' => '__MODULE_PREFIX___page_icon',
\t'url' => '__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID,
\t'items_id' => 'menu___MODULE_PREFIX__',
\t'items' => [
\t\t[
\t\t\t'text' => Loc::getMessage('__MSG_PREFIX___MENU_ITEM_LIST'),
\t\t\t'title' => Loc::getMessage('__MSG_PREFIX___MENU_ITEM_LIST'),
\t\t\t'url' => '__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID,
\t\t\t'more_url' => ['__ADMIN_PAGE_PREFIX___edit.php'],
\t\t\t'items_id' => '__ADMIN_PAGE_PREFIX___list',
\t\t],
\t],
];
"""


def module_lang_menu_template() -> str:
    return """<?php
$MESS['__MSG_PREFIX___MENU_TEXT'] = '__ENTITY_PASCAL__';
$MESS['__MSG_PREFIX___MENU_ITEM_LIST'] = '__ENTITY_PASCAL__ list';
"""


def admin_list_template() -> str:
    return """<?php
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Localization\\Loc;

require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php');

Loc::loadMessages(__FILE__);

global $APPLICATION;

$moduleId = '__MODULE_ID__';
if (!Loader::includeModule($moduleId))
{
\t$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}

$right = $APPLICATION->GetGroupRight($moduleId);
if ($right < 'R')
{
\t$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}
$canWrite = ($right >= 'W');

$sTableID = 'tbl___MODULE_PREFIX_____ENTITY_CODE__';
$oSort = new CAdminSorting($sTableID, 'ID', 'DESC');
$lAdmin = new CAdminList($sTableID, $oSort);

$lAdmin->AddHeaders([
\t['id' => 'ID', 'content' => 'ID', 'sort' => 'ID', 'default' => true],
\t['id' => 'NAME', 'content' => Loc::getMessage('__MSG_PREFIX___FIELD_NAME'), 'sort' => 'NAME', 'default' => true],
\t['id' => 'ACTIVE', 'content' => Loc::getMessage('__MSG_PREFIX___FIELD_ACTIVE'), 'sort' => 'ACTIVE', 'default' => true],
\t['id' => 'TIMESTAMP_X', 'content' => Loc::getMessage('__MSG_PREFIX___FIELD_UPDATED'), 'sort' => 'TIMESTAMP_X', 'default' => true],
]);

$filterFields = ['find_id', 'find_name', 'find_active'];
$lAdmin->InitFilter($filterFields);

$find_id = (int)($find_id ?? 0);
$find_name = trim((string)($find_name ?? ''));
$find_active = trim((string)($find_active ?? ''));

if ($canWrite && $lAdmin->EditAction() && check_bitrix_sessid())
{
\tforeach ($lAdmin->GetEditFields() as $id => $fields)
\t{
\t\t$id = (int)$id;
\t\tif ($id <= 0 || !$lAdmin->IsUpdated($id))
\t\t{
\t\t\tcontinue;
\t\t}

\t\t// TODO: call service layer, example:
\t\t// \\__NAMESPACE__\\Hl\\__ENTITY_PASCAL__Service::update($id, $fields);
\t}
}

if ($canWrite && ($arID = $lAdmin->GroupAction()) && check_bitrix_sessid())
{
\t$action = (string)$lAdmin->GetAction();
\tforeach ($arID as $id)
\t{
\t\t$id = (int)$id;
\t\tif ($id <= 0)
\t\t{
\t\t\tcontinue;
\t\t}

\t\tswitch ($action)
\t\t{
\t\t\tcase 'delete':
\t\t\t\t// TODO: delete via service.
\t\t\t\tbreak;
\t\t\tcase 'activate':
\t\t\t\t// TODO: set ACTIVE = Y.
\t\t\t\tbreak;
\t\t\tcase 'deactivate':
\t\t\t\t// TODO: set ACTIVE = N.
\t\t\t\tbreak;
\t\t}
\t}
}

// TODO: replace with real CAdminResult from repository query.
$rsData = new CAdminResult(new CDBResult(), $sTableID);
$rsData->NavStart();
$lAdmin->NavText($rsData->GetNavPrint(Loc::getMessage('__MSG_PREFIX___PAGES')));

while ($arRes = $rsData->NavNext(true, 'f_'))
{
\t$row = $lAdmin->AddRow($f_ID, $arRes, '__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID . '&ID=' . $f_ID);
\t$row->AddViewField('ID', '<a href="__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID . '&ID=' . $f_ID . '">' . $f_ID . '</a>');
\t$row->AddInputField('NAME', ['size' => 40]);
\t$row->AddCheckField('ACTIVE');

\t$actions = [
\t\t[
\t\t\t'ICON' => 'edit',
\t\t\t'TEXT' => Loc::getMessage('MAIN_ADMIN_MENU_EDIT'),
\t\t\t'ACTION' => $lAdmin->ActionRedirect('__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID . '&ID=' . $f_ID),
\t\t\t'DEFAULT' => true,
\t\t],
\t];

\tif ($canWrite)
\t{
\t\t$actions[] = [
\t\t\t'ICON' => 'delete',
\t\t\t'TEXT' => Loc::getMessage('MAIN_ADMIN_MENU_DELETE'),
\t\t\t'ACTION' => "if(confirm('" . CUtil::JSEscape(Loc::getMessage('__MSG_PREFIX___DELETE_CONFIRM')) . "')) " . $lAdmin->ActionDoGroup($f_ID, 'delete'),
\t\t];
\t}

\t$row->AddActions($actions);
}

$groupActions = [];
if ($canWrite)
{
\t$groupActions = [
\t\t'delete' => true,
\t\t'activate' => Loc::getMessage('MAIN_ADMIN_LIST_ACTIVATE'),
\t\t'deactivate' => Loc::getMessage('MAIN_ADMIN_LIST_DEACTIVATE'),
\t];
}
$lAdmin->AddGroupActionTable($groupActions);

$context = [];
if ($canWrite)
{
\t$context[] = [
\t\t'TEXT' => Loc::getMessage('__MSG_PREFIX___ADD'),
\t\t'LINK' => '__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID,
\t\t'TITLE' => Loc::getMessage('__MSG_PREFIX___ADD'),
\t\t'ICON' => 'btn_new',
\t];
}
$lAdmin->AddAdminContextMenu($context);
$lAdmin->CheckListMode();

$APPLICATION->SetTitle(Loc::getMessage('__MSG_PREFIX___LIST_TITLE'));
require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php');

$oFilter = new CAdminFilter(
\t$sTableID . '_filter',
\t[
\t\t'ID',
\t\tLoc::getMessage('__MSG_PREFIX___FIELD_NAME'),
\t\tLoc::getMessage('__MSG_PREFIX___FIELD_ACTIVE'),
\t]
);
?>
<form name="find_form" method="get" action="<?=htmlspecialcharsbx($APPLICATION->GetCurPage())?>">
\t<?php $oFilter->Begin(); ?>
\t<tr>
\t\t<td>ID</td>
\t\t<td><input type="text" name="find_id" size="20" value="<?=htmlspecialcharsbx($find_id > 0 ? (string)$find_id : '')?>"></td>
\t</tr>
\t<tr>
\t\t<td><?=Loc::getMessage('__MSG_PREFIX___FIELD_NAME')?></td>
\t\t<td><input type="text" name="find_name" size="40" value="<?=htmlspecialcharsbx($find_name)?>"></td>
\t</tr>
\t<tr>
\t\t<td><?=Loc::getMessage('__MSG_PREFIX___FIELD_ACTIVE')?></td>
\t\t<td>
\t\t\t<select name="find_active">
\t\t\t\t<option value=""><?=Loc::getMessage('MAIN_ALL')?></option>
\t\t\t\t<option value="Y"<?=$find_active === 'Y' ? ' selected' : ''?>><?=Loc::getMessage('MAIN_YES')?></option>
\t\t\t\t<option value="N"<?=$find_active === 'N' ? ' selected' : ''?>><?=Loc::getMessage('MAIN_NO')?></option>
\t\t\t</select>
\t\t</td>
\t</tr>
\t<?php
\t$oFilter->Buttons(['table_id' => $sTableID, 'form' => 'find_form']);
\t$oFilter->End();
\t?>
</form>
<?php
$lAdmin->DisplayList();

require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/epilog_admin.php');
"""


def admin_list_lang_template() -> str:
    return """<?php
$MESS['__MSG_PREFIX___LIST_TITLE'] = '__ENTITY_PASCAL__ list';
$MESS['__MSG_PREFIX___PAGES'] = 'Records';
$MESS['__MSG_PREFIX___FIELD_NAME'] = 'Name';
$MESS['__MSG_PREFIX___FIELD_ACTIVE'] = 'Active';
$MESS['__MSG_PREFIX___FIELD_UPDATED'] = 'Updated';
$MESS['__MSG_PREFIX___ADD'] = 'Add __ENTITY_PASCAL__';
$MESS['__MSG_PREFIX___DELETE_CONFIRM'] = 'Delete selected record?';
"""


def admin_edit_template() -> str:
    return """<?php
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Localization\\Loc;

require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php');

Loc::loadMessages(__FILE__);

global $APPLICATION;

$moduleId = '__MODULE_ID__';
if (!Loader::includeModule($moduleId))
{
\t$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}

$right = $APPLICATION->GetGroupRight($moduleId);
if ($right < 'R')
{
\t$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}
$canWrite = ($right >= 'W');

$ID = (int)($_REQUEST['ID'] ?? 0);
$action = (string)($_REQUEST['action'] ?? '');
$save = (string)($_POST['save'] ?? '');
$apply = (string)($_POST['apply'] ?? '');
$isUpdate = ($ID > 0);
$errors = [];

$entity = [
\t'ID' => $ID,
\t'NAME' => '',
\t'ACTIVE' => 'Y',
\t'SORT' => 500,
\t'DESCRIPTION' => '',
];

if ($isUpdate)
{
\t// TODO: load entity via service/repository.
\t// $entity = \\__NAMESPACE__\\Hl\\__ENTITY_PASCAL__Service::get($ID);
\tif (!$entity)
\t{
\t\t$errors[] = Loc::getMessage('__MSG_PREFIX___NOT_FOUND');
\t\t$isUpdate = false;
\t\t$ID = 0;
\t}
}

$aTabs = [
\t['DIV' => 'edit1', 'TAB' => Loc::getMessage('__MSG_PREFIX___TAB_MAIN'), 'TITLE' => Loc::getMessage('__MSG_PREFIX___TAB_MAIN_TITLE')],
\t['DIV' => 'edit2', 'TAB' => Loc::getMessage('__MSG_PREFIX___TAB_EXTRA'), 'TITLE' => Loc::getMessage('__MSG_PREFIX___TAB_EXTRA_TITLE')],
];
$tabControl = new CAdminTabControl('tabControl', $aTabs);

if ($isUpdate && $action === 'delete' && $canWrite && check_bitrix_sessid())
{
\t// TODO: delete via service.
\t$result = new \\Bitrix\\Main\\Result();
\tif ($result->isSuccess())
\t{
\t\tLocalRedirect('__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID);
\t}
\t$errors = array_merge($errors, $result->getErrorMessages());
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($save !== '' || $apply !== '') && $canWrite && check_bitrix_sessid())
{
\t$data = [
\t\t'NAME' => trim((string)($_POST['NAME'] ?? '')),
\t\t'ACTIVE' => (($_POST['ACTIVE'] ?? 'N') === 'Y' ? 'Y' : 'N'),
\t\t'SORT' => (int)($_POST['SORT'] ?? 500),
\t\t'DESCRIPTION' => trim((string)($_POST['DESCRIPTION'] ?? '')),
\t];

\tif ($data['NAME'] === '')
\t{
\t\t$errors[] = Loc::getMessage('__MSG_PREFIX___ERR_NAME_REQUIRED');
\t}

\tif (empty($errors))
\t{
\t\tif ($isUpdate)
\t\t{
\t\t\t// TODO: update via service.
\t\t\t$result = new \\Bitrix\\Main\\Result();
\t\t}
\t\telse
\t\t{
\t\t\t// TODO: create via service.
\t\t\t$result = new \\Bitrix\\Main\\Result();
\t\t\t$ID = 1;
\t\t\t$isUpdate = true;
\t\t}

\t\tif ($result->isSuccess())
\t\t{
\t\t\tif ($save !== '')
\t\t\t{
\t\t\t\tLocalRedirect('__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID);
\t\t\t}
\t\t\tLocalRedirect('__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID . '&ID=' . $ID . '&' . $tabControl->ActiveTabParam());
\t\t}

\t\t$errors = array_merge($errors, $result->getErrorMessages());
\t}

\t$entity = array_merge($entity, $data);
}

$menu = [
\t[
\t\t'TEXT' => Loc::getMessage('__MSG_PREFIX___TO_LIST'),
\t\t'TITLE' => Loc::getMessage('__MSG_PREFIX___TO_LIST'),
\t\t'LINK' => '__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID,
\t\t'ICON' => 'btn_list',
\t],
];

if ($isUpdate && $canWrite)
{
\t$menu[] = ['SEPARATOR' => true];
\t$menu[] = [
\t\t'TEXT' => Loc::getMessage('__MSG_PREFIX___ADD'),
\t\t'TITLE' => Loc::getMessage('__MSG_PREFIX___ADD'),
\t\t'LINK' => '__ADMIN_PAGE_PREFIX___edit.php?lang=' . LANGUAGE_ID,
\t\t'ICON' => 'btn_new',
\t];
\t$menu[] = [
\t\t'TEXT' => Loc::getMessage('__MSG_PREFIX___DELETE'),
\t\t'TITLE' => Loc::getMessage('__MSG_PREFIX___DELETE'),
\t\t'LINK' => "javascript:if(confirm('" . CUtil::JSEscape(Loc::getMessage('__MSG_PREFIX___DELETE_CONFIRM')) . "')) window.location='__ADMIN_PAGE_PREFIX___edit.php?lang=" . LANGUAGE_ID . "&ID=" . $ID . "&action=delete&" . bitrix_sessid_get() . "';",
\t\t'ICON' => 'btn_delete',
\t];
}

$APPLICATION->SetTitle(
\t$isUpdate
\t\t? Loc::getMessage('__MSG_PREFIX___EDIT_TITLE', ['#ID#' => (string)$ID])
\t\t: Loc::getMessage('__MSG_PREFIX___ADD_TITLE')
);

require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php');

$context = new CAdminContextMenu($menu);
$context->Show();

if (!empty($errors))
{
\tCAdminMessage::ShowMessage(implode("\\n", $errors));
}
?>
<form method="post" action="<?=htmlspecialcharsbx($APPLICATION->GetCurPage())?>?lang=<?=LANGUAGE_ID?><?=($ID > 0 ? '&ID=' . $ID : '')?>">
\t<?php
\t$tabControl->BeginEpilogContent();
\techo bitrix_sessid_post();
\t?>
\t<input type="hidden" name="ID" value="<?= (int)$ID ?>">
\t<input type="hidden" name="lang" value="<?= LANGUAGE_ID ?>">
\t<?php
\t$tabControl->EndEpilogContent();
\t$tabControl->Begin();
\t$tabControl->BeginNextTab();
\t?>
\t<tr>
\t\t<td width="40%">ID</td>
\t\t<td width="60%"><?=($ID > 0 ? (int)$ID : Loc::getMessage('__MSG_PREFIX___NEW'))?></td>
\t</tr>
\t<tr class="adm-detail-required-field">
\t\t<td><label for="NAME"><?=Loc::getMessage('__MSG_PREFIX___FIELD_NAME')?></label></td>
\t\t<td><input type="text" id="NAME" name="NAME" size="50" value="<?=htmlspecialcharsbx((string)$entity['NAME'])?>"></td>
\t</tr>
\t<tr>
\t\t<td><label for="ACTIVE"><?=Loc::getMessage('__MSG_PREFIX___FIELD_ACTIVE')?></label></td>
\t\t<td>
\t\t\t<input type="hidden" name="ACTIVE" value="N">
\t\t\t<input type="checkbox" id="ACTIVE" name="ACTIVE" value="Y"<?=($entity['ACTIVE'] === 'Y' ? ' checked' : '')?>>
\t\t</td>
\t</tr>
\t<tr>
\t\t<td><label for="SORT"><?=Loc::getMessage('__MSG_PREFIX___FIELD_SORT')?></label></td>
\t\t<td><input type="text" id="SORT" name="SORT" size="10" value="<?= (int)$entity['SORT'] ?>"></td>
\t</tr>
\t<?php
\t$tabControl->BeginNextTab();
\t?>
\t<tr>
\t\t<td class="adm-detail-valign-top"><label for="DESCRIPTION"><?=Loc::getMessage('__MSG_PREFIX___FIELD_DESCRIPTION')?></label></td>
\t\t<td><textarea id="DESCRIPTION" name="DESCRIPTION" rows="8" cols="60"><?=htmlspecialcharsbx((string)$entity['DESCRIPTION'])?></textarea></td>
\t</tr>
\t<?php
\techo BeginNote();
\techo Loc::getMessage('__MSG_PREFIX___NOTE');
\techo EndNote();
\t$tabControl->Buttons(['disabled' => !$canWrite, 'back_url' => '__ADMIN_PAGE_PREFIX___list.php?lang=' . LANGUAGE_ID]);
\t?>
\t<input type="submit" name="save" value="<?=Loc::getMessage('MAIN_SAVE')?>" class="adm-btn-save">
\t<input type="submit" name="apply" value="<?=Loc::getMessage('MAIN_APPLY')?>">
\t<?php $tabControl->End(); ?>
</form>
<?php
require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/epilog_admin.php');
"""


def admin_edit_lang_template() -> str:
    return """<?php
$MESS['__MSG_PREFIX___ADD_TITLE'] = 'Create __ENTITY_PASCAL__';
$MESS['__MSG_PREFIX___EDIT_TITLE'] = 'Edit __ENTITY_PASCAL__ ##ID#';
$MESS['__MSG_PREFIX___TAB_MAIN'] = 'Main';
$MESS['__MSG_PREFIX___TAB_MAIN_TITLE'] = '__ENTITY_PASCAL__ main settings';
$MESS['__MSG_PREFIX___TAB_EXTRA'] = 'Extra';
$MESS['__MSG_PREFIX___TAB_EXTRA_TITLE'] = '__ENTITY_PASCAL__ extra settings';
$MESS['__MSG_PREFIX___TO_LIST'] = 'Back to list';
$MESS['__MSG_PREFIX___ADD'] = 'Add __ENTITY_PASCAL__';
$MESS['__MSG_PREFIX___DELETE'] = 'Delete';
$MESS['__MSG_PREFIX___DELETE_CONFIRM'] = 'Delete this record?';
$MESS['__MSG_PREFIX___FIELD_NAME'] = 'Name';
$MESS['__MSG_PREFIX___FIELD_ACTIVE'] = 'Active';
$MESS['__MSG_PREFIX___FIELD_SORT'] = 'Sort';
$MESS['__MSG_PREFIX___FIELD_DESCRIPTION'] = 'Description';
$MESS['__MSG_PREFIX___ERR_NAME_REQUIRED'] = 'Name is required.';
$MESS['__MSG_PREFIX___NOT_FOUND'] = 'Record not found.';
$MESS['__MSG_PREFIX___NEW'] = 'New';
$MESS['__MSG_PREFIX___NOTE'] = 'Use this tab to configure advanced __ENTITY_PASCAL__ data.';
"""


def options_template() -> str:
    return """<?php
/** @global CUser $USER */
/** @global CMain $APPLICATION */
/** @global string $mid */

use Bitrix\\Main\\Application;
use Bitrix\\Main\\Config\\Option;
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Localization\\Loc;

$moduleId = '__MODULE_ID__';

if (!$USER->IsAdmin())
{
\treturn;
}

if (!Loader::includeModule($moduleId))
{
\treturn;
}

Loc::loadMessages(__FILE__);
Loc::loadMessages(Application::getDocumentRoot() . BX_ROOT . '/modules/main/options.php');

if ($APPLICATION->GetGroupRight($moduleId) < 'S')
{
\t$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}

$tabs = [
\t['DIV' => 'edit1', 'TAB' => Loc::getMessage('MAIN_TAB_SET'), 'TITLE' => Loc::getMessage('MAIN_TAB_TITLE_SET')],
];
$tabControl = new CAdminTabControl('tabControl', $tabs);

$options = [
\t['CODE' => 'enabled', 'NAME' => Loc::getMessage('__OPT_PREFIX___ENABLED'), 'TYPE' => 'checkbox', 'DEFAULT' => 'Y'],
\t['CODE' => 'batch_limit', 'NAME' => Loc::getMessage('__OPT_PREFIX___BATCH_LIMIT'), 'TYPE' => 'int', 'DEFAULT' => '100'],
];

$request = Application::getInstance()->getContext()->getRequest();
$backUrl = (string)$request->get('back_url_settings');

$action = null;
if ($request->isPost())
{
\tif ($request->getPost('RestoreDefaults') !== null)
\t{
\t\t$action = 'reset';
\t}
\telseif ($request->getPost('Update') !== null)
\t{
\t\t$action = 'save';
\t}
\telseif ($request->getPost('Apply') !== null)
\t{
\t\t$action = 'apply';
\t}
}

if ($request->isPost() && $action !== null && check_bitrix_sessid())
{
\tif ($action === 'reset')
\t{
\t\tOption::delete($moduleId);
\t}
\telse
\t{
\t\tforeach ($options as $option)
\t\t{
\t\t\t$code = (string)$option['CODE'];
\t\t\t$value = $request->getPost($code);
\t\t\tswitch ($option['TYPE'])
\t\t\t{
\t\t\t\tcase 'checkbox':
\t\t\t\t\t$value = ($value === 'Y' ? 'Y' : 'N');
\t\t\t\t\tbreak;
\t\t\t\tcase 'int':
\t\t\t\t\t$value = (string)max(1, (int)$value);
\t\t\t\t\tbreak;
\t\t\t\tdefault:
\t\t\t\t\t$value = trim((string)$value);
\t\t\t\t\tbreak;
\t\t\t}
\t\t\tOption::set($moduleId, $code, $value);
\t\t}
\t}

\tif ($action === 'save' && $backUrl !== '')
\t{
\t\tLocalRedirect($backUrl);
\t}
\telse
\t{
\t\tLocalRedirect(
\t\t\t$APPLICATION->GetCurPage()
\t\t\t. '?mid=' . urlencode($mid)
\t\t\t. '&lang=' . urlencode(LANGUAGE_ID)
\t\t\t. ($backUrl !== '' ? '&back_url_settings=' . urlencode($backUrl) : '')
\t\t\t. '&' . $tabControl->ActiveTabParam()
\t\t);
\t}
}

$values = [];
foreach ($options as $option)
{
\t$values[$option['CODE']] = Option::get($moduleId, $option['CODE'], (string)$option['DEFAULT']);
}

$tabControl->Begin();
?>
<form method="post" action="<?=$APPLICATION->GetCurPage()?>?mid=<?=urlencode($mid)?>&lang=<?=LANGUAGE_ID?>">
\t<?=bitrix_sessid_post()?>
\t<?php $tabControl->BeginNextTab(); ?>
\t<?php foreach ($options as $option): ?>
\t\t<?php
\t\t$code = (string)$option['CODE'];
\t\t$type = (string)$option['TYPE'];
\t\t$current = (string)$values[$code];
\t\t?>
\t\t<tr>
\t\t\t<td width="40%"><label for="<?=htmlspecialcharsbx($code)?>"><?=htmlspecialcharsbx((string)$option['NAME'])?></label></td>
\t\t\t<td width="60%">
\t\t\t\t<?php if ($type === 'checkbox'): ?>
\t\t\t\t\t<input type="hidden" name="<?=htmlspecialcharsbx($code)?>" value="N">
\t\t\t\t\t<input type="checkbox" id="<?=htmlspecialcharsbx($code)?>" name="<?=htmlspecialcharsbx($code)?>" value="Y"<?=($current === 'Y' ? ' checked' : '')?>>
\t\t\t\t<?php else: ?>
\t\t\t\t\t<input type="text" id="<?=htmlspecialcharsbx($code)?>" name="<?=htmlspecialcharsbx($code)?>" size="20" value="<?=htmlspecialcharsbx($current)?>">
\t\t\t\t<?php endif; ?>
\t\t\t</td>
\t\t</tr>
\t<?php endforeach; ?>

\t<?php
\t$tabControl->Buttons();
\t?>
\t<input type="submit" name="Update" value="<?=Loc::getMessage('MAIN_SAVE')?>" class="adm-btn-save">
\t<input type="submit" name="Apply" value="<?=Loc::getMessage('MAIN_APPLY')?>">
\t<input type="submit" name="RestoreDefaults" value="<?=Loc::getMessage('MAIN_RESTORE_DEFAULTS')?>" onclick="return confirm('<?=CUtil::JSEscape(Loc::getMessage('MAIN_HINT_RESTORE_DEFAULTS_WARNING'))?>');">
\t<?php if ($backUrl !== ''): ?>
\t\t<input type="hidden" name="back_url_settings" value="<?=htmlspecialcharsbx($backUrl)?>">
\t\t<input type="button" value="<?=Loc::getMessage('MAIN_OPT_CANCEL')?>" onclick="window.location='<?=htmlspecialcharsbx(CUtil::addslashes($backUrl))?>'">
\t<?php endif; ?>
</form>
<?php
$tabControl->End();
"""


def options_lang_template() -> str:
    return """<?php
$MESS['__OPT_PREFIX___ENABLED'] = 'Enable module features';
$MESS['__OPT_PREFIX___BATCH_LIMIT'] = 'Batch limit';
"""


def proxy_template(target_rel_path: str) -> str:
    return f"""<?php
$paths = [
\t$_SERVER['DOCUMENT_ROOT'] . '/local/modules/__MODULE_ID__/admin/{target_rel_path}',
\t$_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/__MODULE_ID__/admin/{target_rel_path}',
];
foreach ($paths as $path)
{{
\tif (file_exists($path))
\t{{
\t\trequire_once $path;
\t\treturn;
\t}}
}}
"""


def build_files(
    project_root: Path,
    module_id: str,
    module_prefix: str,
    entity_code: str,
    entity_pascal: str,
    namespace: str,
    lang: str,
    include_project_proxies: bool,
) -> Dict[Path, str]:
    msg_prefix = f"{module_prefix.upper()}_{entity_code.upper()}"
    opt_prefix = f"{module_prefix.upper()}_OPT"

    replacements = {
        "MODULE_ID": module_id,
        "MODULE_PREFIX": module_prefix,
        "ENTITY_CODE": entity_code,
        "ENTITY_PASCAL": entity_pascal,
        "ADMIN_PAGE_PREFIX": f"{module_prefix}_{entity_code}",
        "MSG_PREFIX": msg_prefix,
        "OPT_PREFIX": opt_prefix,
        "NAMESPACE": namespace,
    }

    module_root = project_root / "local" / "modules" / module_id
    files: Dict[Path, str] = {
        module_root / "admin" / "menu.php": fill(module_menu_template(), replacements),
        module_root / "admin" / f"{entity_code}_list.php": fill(admin_list_template(), replacements),
        module_root / "admin" / f"{entity_code}_edit.php": fill(admin_edit_template(), replacements),
        module_root / "options.php": fill(options_template(), replacements),
        module_root / "lang" / lang / "admin" / "menu.php": fill(module_lang_menu_template(), replacements),
        module_root / "lang" / lang / "admin" / f"{entity_code}_list.php": fill(admin_list_lang_template(), replacements),
        module_root / "lang" / lang / "admin" / f"{entity_code}_edit.php": fill(admin_edit_lang_template(), replacements),
        module_root / "lang" / lang / "options.php": fill(options_lang_template(), replacements),
        module_root
        / "install"
        / "admin"
        / f"{module_prefix}_{entity_code}_list.php": fill(proxy_template(f"{entity_code}_list.php"), replacements),
        module_root
        / "install"
        / "admin"
        / f"{module_prefix}_{entity_code}_edit.php": fill(proxy_template(f"{entity_code}_edit.php"), replacements),
    }

    if include_project_proxies:
        files[project_root / "bitrix" / "admin" / f"{module_prefix}_{entity_code}_list.php"] = fill(
            proxy_template(f"{entity_code}_list.php"), replacements
        )
        files[project_root / "bitrix" / "admin" / f"{module_prefix}_{entity_code}_edit.php"] = fill(
            proxy_template(f"{entity_code}_edit.php"), replacements
        )

    return files


def write_file(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    validate_args(args)

    project_root = Path(args.project_root).resolve()
    module_id = args.module_id
    module_prefix = module_id.replace(".", "_")
    entity_code = args.entity
    entity_pascal = pascal_case(entity_code)
    namespace = args.namespace.strip("\\")

    files = build_files(
        project_root=project_root,
        module_id=module_id,
        module_prefix=module_prefix,
        entity_code=entity_code,
        entity_pascal=entity_pascal,
        namespace=namespace,
        lang=args.lang,
        include_project_proxies=not args.skip_project_proxies,
    )

    created = 0
    skipped = 0
    for path, content in files.items():
        if write_file(path, content, overwrite=args.overwrite):
            created += 1
            print(f"created: {path}")
        else:
            skipped += 1
            print(f"skipped: {path} (exists)")

    print(f"done: created={created}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
