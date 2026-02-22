# Template: Admin List Page (`CAdminList` + `CAdminFilter`)

Use as a starter for classic admin list pages in module admin files:

- `local/modules/<vendor.module>/admin/<entity>_list.php`

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

$sTableID = 'tbl_vendor_entity';
$oSort = new CAdminSorting($sTableID, 'ID', 'desc');
$lAdmin = new CAdminList($sTableID, $oSort);

$lAdmin->AddHeaders([
	['id' => 'ID', 'content' => 'ID', 'sort' => 'ID', 'default' => true],
	['id' => 'NAME', 'content' => Loc::getMessage('VENDOR_ENTITY_FIELD_NAME'), 'sort' => 'NAME', 'default' => true],
	['id' => 'ACTIVE', 'content' => Loc::getMessage('VENDOR_ENTITY_FIELD_ACTIVE'), 'sort' => 'ACTIVE', 'default' => true],
	['id' => 'TIMESTAMP_X', 'content' => Loc::getMessage('VENDOR_ENTITY_FIELD_UPDATED'), 'sort' => 'TIMESTAMP_X', 'default' => true],
]);

// Filter
$filterFields = ['find_id', 'find_name', 'find_active'];
$lAdmin->InitFilter($filterFields);

$find_id = (int)($find_id ?? 0);
$find_name = trim((string)($find_name ?? ''));
$find_active = trim((string)($find_active ?? ''));

$ormFilter = [];
if ($find_id > 0)
{
	$ormFilter['=ID'] = $find_id;
}
if ($find_name !== '')
{
	$ormFilter['%NAME'] = $find_name;
}
if (in_array($find_active, ['Y', 'N'], true))
{
	$ormFilter['=ACTIVE'] = $find_active;
}

// Inline edit
if ($canWrite && $lAdmin->EditAction() && check_bitrix_sessid())
{
	foreach ($lAdmin->GetEditFields() as $id => $fields)
	{
		$id = (int)$id;
		if ($id <= 0 || !$lAdmin->IsUpdated($id))
		{
			continue;
		}

		// TODO: call repository/service update here.
		// $result = Vendor\Module\Repository\EntityTable::update($id, $fields);
		$result = new \Bitrix\Main\Result();
		if (!$result->isSuccess())
		{
			$lAdmin->AddUpdateError(implode("\n", $result->getErrorMessages()), $id);
		}
	}
}

// Group action
if ($canWrite && ($arID = $lAdmin->GroupAction()) && check_bitrix_sessid())
{
	if ($lAdmin->IsGroupActionToAll())
	{
		$arID = [];
		// TODO: select IDs by current filter.
	}

	$action = $lAdmin->GetAction();
	foreach ($arID as $id)
	{
		$id = (int)$id;
		if ($id <= 0)
		{
			continue;
		}

		switch ($action)
		{
			case 'delete':
				// TODO: delete in repository/service.
				break;
			case 'activate':
				// TODO: set ACTIVE => 'Y'
				break;
			case 'deactivate':
				// TODO: set ACTIVE => 'N'
				break;
		}
	}
}

// Data query
$by = mb_strtoupper((string)$oSort->GetField());
$order = mb_strtoupper((string)$oSort->GetOrder());
if (!in_array($order, ['ASC', 'DESC'], true))
{
	$order = 'DESC';
}

// TODO: replace with ORM query and CAdminResult-compatible result.
// $rsData = new CAdminResult(Vendor\Module\Repository\EntityTable::getList([...]), $sTableID);
$rsData = new CAdminResult(new CDBResult(), $sTableID);
$rsData->NavStart();
$lAdmin->NavText($rsData->GetNavPrint(Loc::getMessage('VENDOR_ENTITY_PAGES')));

while ($arRes = $rsData->NavNext(true, 'f_'))
{
	$row = $lAdmin->AddRow($f_ID, $arRes, 'vendor_module_entity_edit.php?ID='.$f_ID.'&lang='.LANGUAGE_ID);

	$row->AddViewField('ID', '<a href="vendor_module_entity_edit.php?ID='.$f_ID.'&lang='.LANGUAGE_ID.'">'.$f_ID.'</a>');
	$row->AddInputField('NAME', ['size' => 40]);
	$row->AddCheckField('ACTIVE');

	$actions = [
		[
			'ICON' => 'edit',
			'TEXT' => Loc::getMessage('MAIN_ADMIN_MENU_EDIT'),
			'ACTION' => $lAdmin->ActionRedirect('vendor_module_entity_edit.php?ID='.$f_ID.'&lang='.LANGUAGE_ID),
			'DEFAULT' => true,
		],
	];

	if ($canWrite)
	{
		$actions[] = [
			'ICON' => 'delete',
			'TEXT' => Loc::getMessage('MAIN_ADMIN_MENU_DELETE'),
			'ACTION' => "if(confirm('".CUtil::JSEscape(Loc::getMessage('VENDOR_ENTITY_DELETE_CONFIRM'))."')) ".
				$lAdmin->ActionDoGroup($f_ID, 'delete'),
		];
	}

	$row->AddActions($actions);
}

$groupActions = [];
if ($canWrite)
{
	$groupActions = [
		'delete' => true,
		'activate' => Loc::getMessage('MAIN_ADMIN_LIST_ACTIVATE'),
		'deactivate' => Loc::getMessage('MAIN_ADMIN_LIST_DEACTIVATE'),
	];
}
$lAdmin->AddGroupActionTable($groupActions);

$context = [];
if ($canWrite)
{
	$context[] = [
		'TEXT' => Loc::getMessage('VENDOR_ENTITY_ADD'),
		'LINK' => 'vendor_module_entity_edit.php?lang='.LANGUAGE_ID,
		'TITLE' => Loc::getMessage('VENDOR_ENTITY_ADD'),
		'ICON' => 'btn_new',
	];
}
$lAdmin->AddAdminContextMenu($context);

$lAdmin->CheckListMode();

$APPLICATION->SetTitle(Loc::getMessage('VENDOR_ENTITY_LIST_TITLE'));
require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_admin_after.php');

$oFilter = new CAdminFilter(
	$sTableID.'_filter',
	[
		Loc::getMessage('VENDOR_ENTITY_FIELD_ID'),
		Loc::getMessage('VENDOR_ENTITY_FIELD_NAME'),
		Loc::getMessage('VENDOR_ENTITY_FIELD_ACTIVE'),
	]
);
?>
<form name="find_form" method="get" action="<?=htmlspecialcharsbx($APPLICATION->GetCurPage())?>">
	<?php
	$oFilter->Begin();
	?>
	<tr>
		<td>ID</td>
		<td><input type="text" name="find_id" size="20" value="<?=htmlspecialcharsbx($find_id > 0 ? (string)$find_id : '')?>"></td>
	</tr>
	<tr>
		<td><?=Loc::getMessage('VENDOR_ENTITY_FIELD_NAME')?></td>
		<td><input type="text" name="find_name" size="40" value="<?=htmlspecialcharsbx($find_name)?>"></td>
	</tr>
	<tr>
		<td><?=Loc::getMessage('VENDOR_ENTITY_FIELD_ACTIVE')?></td>
		<td>
			<select name="find_active">
				<option value=""><?=Loc::getMessage('MAIN_ALL')?></option>
				<option value="Y"<?=$find_active === 'Y' ? ' selected' : ''?>><?=Loc::getMessage('MAIN_YES')?></option>
				<option value="N"<?=$find_active === 'N' ? ' selected' : ''?>><?=Loc::getMessage('MAIN_NO')?></option>
			</select>
		</td>
	</tr>
	<?php
	$oFilter->Buttons(['table_id' => $sTableID, 'form' => 'find_form']);
	$oFilter->End();
	?>
</form>
<?php

$lAdmin->DisplayList();

require_once($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/epilog_admin.php');
```

## Notes

- Keep data writes in service/repository layer, not in page body.
- Always keep `check_bitrix_sessid()` on edit/group actions.
- Keep list context action as primary create entry point.
