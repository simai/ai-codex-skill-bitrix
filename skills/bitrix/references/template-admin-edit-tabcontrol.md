# Template: Admin Edit Page (`CAdminTabControl`)

Use as a starter for create/edit admin pages:

- `local/modules/<vendor.module>/admin/<entity>_edit.php`

```php
<?php

use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;

require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_before.php');

Loc::loadMessages(__FILE__);

global $APPLICATION;

$moduleId = 'vendor.module';
if (!Loader::includeModule($moduleId))
{
	$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}

$RIGHT = $APPLICATION->GetGroupRight($moduleId);
if ($RIGHT < 'R')
{
	$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}
$canWrite = ($RIGHT >= 'W');

$ID = (int)($_REQUEST['ID'] ?? 0);
$action = (string)($_REQUEST['action'] ?? '');
$save = (string)($_POST['save'] ?? '');
$apply = (string)($_POST['apply'] ?? '');

$isUpdate = ($ID > 0);
$errors = [];

$aTabs = [
	['DIV' => 'edit1', 'TAB' => Loc::getMessage('VENDOR_ENTITY_TAB_MAIN'), 'TITLE' => Loc::getMessage('VENDOR_ENTITY_TAB_MAIN_TITLE')],
	['DIV' => 'edit2', 'TAB' => Loc::getMessage('VENDOR_ENTITY_TAB_EXTRA'), 'TITLE' => Loc::getMessage('VENDOR_ENTITY_TAB_EXTRA_TITLE')],
];
$tabControl = new CAdminTabControl('tabControl', $aTabs);

$entity = [
	'ID' => $ID,
	'NAME' => '',
	'ACTIVE' => 'Y',
	'SORT' => 500,
];

if ($isUpdate)
{
	// TODO: load entity by ID from repository/service.
	// $entity = Vendor\Module\Repository\EntityTable::getById($ID)->fetch() ?: [];
	if (empty($entity))
	{
		$errors[] = Loc::getMessage('VENDOR_ENTITY_NOT_FOUND');
		$isUpdate = false;
		$ID = 0;
	}
}

if ($isUpdate && $action === 'delete' && $canWrite && check_bitrix_sessid())
{
	// TODO: delete in repository/service.
	$result = new \Bitrix\Main\Result();
	if ($result->isSuccess())
	{
		LocalRedirect('vendor_module_entity_list.php?lang='.LANGUAGE_ID);
	}
	$errors = array_merge($errors, $result->getErrorMessages());
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($save !== '' || $apply !== '') && $canWrite && check_bitrix_sessid())
{
	$data = [
		'NAME' => trim((string)($_POST['NAME'] ?? '')),
		'ACTIVE' => (($_POST['ACTIVE'] ?? 'N') === 'Y' ? 'Y' : 'N'),
		'SORT' => (int)($_POST['SORT'] ?? 500),
		'DESCRIPTION' => trim((string)($_POST['DESCRIPTION'] ?? '')),
	];

	if ($data['NAME'] === '')
	{
		$errors[] = Loc::getMessage('VENDOR_ENTITY_ERR_NAME_REQUIRED');
	}

	if (empty($errors))
	{
		if ($isUpdate)
		{
			// TODO: update in repository/service.
			$result = new \Bitrix\Main\Result();
		}
		else
		{
			// TODO: add in repository/service.
			$result = new \Bitrix\Main\Result();
			// $ID = (int)$result->getData()['ID'];
			$ID = 1;
			$isUpdate = true;
		}

		if ($result->isSuccess())
		{
			if ($save !== '')
			{
				LocalRedirect('vendor_module_entity_list.php?lang='.LANGUAGE_ID);
			}

			LocalRedirect(
				'vendor_module_entity_edit.php?lang='.LANGUAGE_ID.'&ID='.$ID.'&'.$tabControl->ActiveTabParam()
			);
		}

		$errors = array_merge($errors, $result->getErrorMessages());
	}

	$entity = array_merge($entity, $data);
}

$menu = [
	[
		'TEXT' => Loc::getMessage('VENDOR_ENTITY_TO_LIST'),
		'TITLE' => Loc::getMessage('VENDOR_ENTITY_TO_LIST'),
		'LINK' => 'vendor_module_entity_list.php?lang='.LANGUAGE_ID,
		'ICON' => 'btn_list',
	],
];
if ($isUpdate && $canWrite)
{
	$menu[] = ['SEPARATOR' => true];
	$menu[] = [
		'TEXT' => Loc::getMessage('VENDOR_ENTITY_ADD'),
		'TITLE' => Loc::getMessage('VENDOR_ENTITY_ADD'),
		'LINK' => 'vendor_module_entity_edit.php?lang='.LANGUAGE_ID,
		'ICON' => 'btn_new',
	];
	$menu[] = [
		'TEXT' => Loc::getMessage('VENDOR_ENTITY_DELETE'),
		'TITLE' => Loc::getMessage('VENDOR_ENTITY_DELETE'),
		'LINK' => "javascript:if(confirm('".CUtil::JSEscape(Loc::getMessage('VENDOR_ENTITY_DELETE_CONFIRM'))."')) ".
			"window.location='vendor_module_entity_edit.php?lang=".LANGUAGE_ID."&ID=".$ID."&action=delete&".bitrix_sessid_get()."';",
		'ICON' => 'btn_delete',
	];
}

if ($isUpdate)
{
	$APPLICATION->SetTitle(Loc::getMessage('VENDOR_ENTITY_EDIT_TITLE', ['#ID#' => (string)$ID]));
}
else
{
	$APPLICATION->SetTitle(Loc::getMessage('VENDOR_ENTITY_ADD_TITLE'));
}

require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_after.php');

$context = new CAdminContextMenu($menu);
$context->Show();

if (!empty($errors))
{
	CAdminMessage::ShowMessage(implode("\n", $errors));
}
?>
<form method="post" action="<?=htmlspecialcharsbx($APPLICATION->GetCurPage())?>?lang=<?=LANGUAGE_ID?><?=($ID > 0 ? '&ID='.$ID : '')?>">
	<?php
	$tabControl->BeginEpilogContent();
	echo bitrix_sessid_post();
	?>
	<input type="hidden" name="ID" value="<?= (int)$ID ?>">
	<input type="hidden" name="lang" value="<?= LANGUAGE_ID ?>">
	<?php
	$tabControl->EndEpilogContent();

	$tabControl->Begin();
	$tabControl->BeginNextTab();
	?>
	<tr>
		<td width="40%"><?=Loc::getMessage('VENDOR_ENTITY_FIELD_ID')?></td>
		<td width="60%"><?=($ID > 0 ? (int)$ID : Loc::getMessage('VENDOR_ENTITY_NEW'))?></td>
	</tr>
	<tr class="adm-detail-required-field">
		<td><label for="NAME"><?=Loc::getMessage('VENDOR_ENTITY_FIELD_NAME')?></label></td>
		<td><input type="text" name="NAME" id="NAME" size="50" value="<?=htmlspecialcharsbx((string)$entity['NAME'])?>"></td>
	</tr>
	<tr>
		<td><label for="ACTIVE"><?=Loc::getMessage('VENDOR_ENTITY_FIELD_ACTIVE')?></label></td>
		<td>
			<input type="hidden" name="ACTIVE" value="N">
			<input type="checkbox" name="ACTIVE" id="ACTIVE" value="Y"<?=($entity['ACTIVE'] === 'Y' ? ' checked' : '')?>>
		</td>
	</tr>
	<tr>
		<td><label for="SORT"><?=Loc::getMessage('VENDOR_ENTITY_FIELD_SORT')?></label></td>
		<td><input type="text" name="SORT" id="SORT" size="10" value="<?= (int)$entity['SORT'] ?>"></td>
	</tr>
	<?php
	$tabControl->BeginNextTab();
	?>
	<tr>
		<td class="adm-detail-valign-top"><label for="DESCRIPTION"><?=Loc::getMessage('VENDOR_ENTITY_FIELD_DESCRIPTION')?></label></td>
		<td><textarea name="DESCRIPTION" id="DESCRIPTION" rows="8" cols="60"><?=htmlspecialcharsbx((string)($entity['DESCRIPTION'] ?? ''))?></textarea></td>
	</tr>
	<?php
	echo BeginNote();
	echo Loc::getMessage('VENDOR_ENTITY_NOTE');
	echo EndNote();

	$tabControl->Buttons([
		'disabled' => !$canWrite,
		'back_url' => 'vendor_module_entity_list.php?lang='.LANGUAGE_ID,
	]);
	?>
	<input type="submit" name="save" value="<?=Loc::getMessage('MAIN_SAVE')?>" class="adm-btn-save">
	<input type="submit" name="apply" value="<?=Loc::getMessage('MAIN_APPLY')?>">
	<?php
	$tabControl->End();
	?>
</form>
<?php
require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/epilog_admin.php');
```

## Notes

- Keep save/apply redirect flow deterministic.
- Keep delete path explicit and protected with session check.
- For UF-heavy entities use `CAdminForm` + `$USER_FIELD_MANAGER` field APIs.
