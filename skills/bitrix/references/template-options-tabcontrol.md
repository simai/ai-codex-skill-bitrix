# Template: Module Options Page (`options.php` + `CAdminTabControl`)

Use for module settings page:

- `local/modules/<vendor.module>/options.php`

```php
<?php
/** @global CUser $USER */
/** @global CMain $APPLICATION */
/** @global string $mid */

use Bitrix\Main\Application;
use Bitrix\Main\Config\Option;
use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;

$moduleId = 'vendor.module';

if (!$USER->IsAdmin())
{
	return;
}

if (!Loader::includeModule($moduleId))
{
	return;
}

Loc::loadMessages(__FILE__);
Loc::loadMessages(Application::getDocumentRoot().BX_ROOT.'/modules/main/options.php');

if ($APPLICATION->GetGroupRight($moduleId) < 'S')
{
	$APPLICATION->AuthForm(Loc::getMessage('ACCESS_DENIED'));
}

$tabs = [
	[
		'DIV' => 'edit1',
		'TAB' => Loc::getMessage('MAIN_TAB_SET'),
		'TITLE' => Loc::getMessage('MAIN_TAB_TITLE_SET'),
	],
	[
		'DIV' => 'edit2',
		'TAB' => Loc::getMessage('VENDOR_OPTIONS_TAB_ADV'),
		'TITLE' => Loc::getMessage('VENDOR_OPTIONS_TAB_ADV_TITLE'),
	],
];
$tabControl = new CAdminTabControl('tabControl', $tabs);

$options = [
	[
		'CODE' => 'enabled',
		'NAME' => Loc::getMessage('VENDOR_OPT_ENABLED'),
		'TYPE' => 'checkbox',
		'DEFAULT' => 'Y',
	],
	[
		'CODE' => 'sync_interval',
		'NAME' => Loc::getMessage('VENDOR_OPT_SYNC_INTERVAL'),
		'TYPE' => 'int',
		'DEFAULT' => '300',
		'MIN' => 60,
	],
	[
		'CODE' => 'endpoint',
		'NAME' => Loc::getMessage('VENDOR_OPT_ENDPOINT'),
		'TYPE' => 'string',
		'DEFAULT' => '',
		'SIZE' => 50,
	],
	[
		'CODE' => 'admin_note',
		'TYPE' => 'note',
		'TEXT' => Loc::getMessage('VENDOR_OPT_NOTE'),
	],
];

$request = Application::getInstance()->getContext()->getRequest();
$backUrl = (string)$request->get('back_url_settings');

$action = null;
if ($request->isPost())
{
	if ($request->getPost('RestoreDefaults') !== null)
	{
		$action = 'reset';
	}
	elseif ($request->getPost('Update') !== null)
	{
		$action = 'save';
	}
	elseif ($request->getPost('Apply') !== null)
	{
		$action = 'apply';
	}
}

if ($request->isPost() && $action !== null && check_bitrix_sessid())
{
	if ($action === 'reset')
	{
		Option::delete($moduleId);
	}
	else
	{
		foreach ($options as $option)
		{
			if (($option['TYPE'] ?? '') === 'note')
			{
				continue;
			}

			$code = $option['CODE'];
			$value = $request->getPost($code);

			switch ($option['TYPE'])
			{
				case 'checkbox':
					$value = ($value === 'Y' ? 'Y' : 'N');
					break;
				case 'int':
					$value = (string)max((int)($option['MIN'] ?? 0), (int)$value);
					break;
				default:
					$value = trim((string)$value);
					break;
			}

			Option::set($moduleId, $code, $value);
		}
	}

	if ($action === 'save' && $backUrl !== '')
	{
		LocalRedirect($backUrl);
	}
	else
	{
		LocalRedirect(
			$APPLICATION->GetCurPage()
			. '?mid=' . urlencode($mid)
			. '&lang=' . urlencode(LANGUAGE_ID)
			. ($backUrl !== '' ? '&back_url_settings=' . urlencode($backUrl) : '')
			. '&' . $tabControl->ActiveTabParam()
		);
	}
}

$values = [];
foreach ($options as $option)
{
	if (($option['TYPE'] ?? '') === 'note')
	{
		continue;
	}

	$values[$option['CODE']] = Option::get(
		$moduleId,
		$option['CODE'],
		(string)($option['DEFAULT'] ?? '')
	);
}

$tabControl->Begin();
?>
<form method="post" action="<?=$APPLICATION->GetCurPage()?>?mid=<?=urlencode($mid)?>&lang=<?=LANGUAGE_ID?>">
	<?php
	echo bitrix_sessid_post();

	$tabControl->BeginNextTab();
	foreach ($options as $option):
		if (($option['TYPE'] ?? '') === 'note'):
			?>
			<tr>
				<td colspan="2"><?php echo BeginNote().$option['TEXT'].EndNote(); ?></td>
			</tr>
			<?php
			continue;
		endif;

		$code = (string)$option['CODE'];
		$type = (string)$option['TYPE'];
		$current = (string)($values[$code] ?? '');
		?>
		<tr>
			<td width="40%"><label for="<?=htmlspecialcharsbx($code)?>"><?=htmlspecialcharsbx((string)$option['NAME'])?></label></td>
			<td width="60%">
				<?php if ($type === 'checkbox'): ?>
					<input type="hidden" name="<?=htmlspecialcharsbx($code)?>" value="N">
					<input type="checkbox" id="<?=htmlspecialcharsbx($code)?>" name="<?=htmlspecialcharsbx($code)?>" value="Y"<?=($current === 'Y' ? ' checked' : '')?>>
				<?php else: ?>
					<input type="text" id="<?=htmlspecialcharsbx($code)?>" name="<?=htmlspecialcharsbx($code)?>" size="<?= (int)($option['SIZE'] ?? 20) ?>" value="<?=htmlspecialcharsbx($current)?>">
				<?php endif; ?>
			</td>
		</tr>
		<?php
	endforeach;

	$tabControl->BeginNextTab();
	?>
	<tr>
		<td width="40%"><?=Loc::getMessage('VENDOR_OPT_ADV_HEADING')?></td>
		<td width="60%">
			<?php
			echo BeginNote();
			echo Loc::getMessage('VENDOR_OPT_ADV_NOTE');
			echo EndNote();
			?>
		</td>
	</tr>
	<?php
	$tabControl->Buttons();
	?>
	<input type="submit" name="Update" value="<?=Loc::getMessage('MAIN_SAVE')?>" class="adm-btn-save">
	<input type="submit" name="Apply" value="<?=Loc::getMessage('MAIN_APPLY')?>">
	<input type="submit" name="RestoreDefaults" value="<?=Loc::getMessage('MAIN_RESTORE_DEFAULTS')?>" onclick="return confirm('<?=CUtil::JSEscape(Loc::getMessage('MAIN_HINT_RESTORE_DEFAULTS_WARNING'))?>');">
	<?php if ($backUrl !== ''): ?>
		<input type="hidden" name="back_url_settings" value="<?=htmlspecialcharsbx($backUrl)?>">
		<input type="button" value="<?=Loc::getMessage('MAIN_OPT_CANCEL')?>" onclick="window.location='<?=htmlspecialcharsbx(CUtil::addslashes($backUrl))?>'">
	<?php endif; ?>
</form>
<?php
$tabControl->End();
```

## Notes

- Keep POST handling in PRG style (`LocalRedirect` after save/reset).
- Treat checkboxes via hidden `N` + checkbox `Y`.
- Keep destructive reset (`RestoreDefaults`) explicit and confirmed.
