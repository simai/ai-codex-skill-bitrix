# Template: Module `install/index.php`

Use as a starting point for custom module installer classes.

```php
<?php

use Bitrix\Main\Application;
use Bitrix\Main\Localization\Loc;

Loc::loadMessages(__FILE__);

if (class_exists('vendor_module'))
{
	return;
}

class vendor_module extends CModule
{
	public $MODULE_ID = 'vendor.module';
	public $MODULE_VERSION;
	public $MODULE_VERSION_DATE;
	public $MODULE_NAME;
	public $MODULE_DESCRIPTION;
	public $errors = false;

	public function __construct()
	{
		$arModuleVersion = [];
		include __DIR__ . '/version.php';

		$this->MODULE_VERSION = $arModuleVersion['VERSION'] ?? '1.0.0';
		$this->MODULE_VERSION_DATE = $arModuleVersion['VERSION_DATE'] ?? date('Y-m-d H:i:s');
		$this->MODULE_NAME = Loc::getMessage('VENDOR_MODULE_INSTALL_NAME');
		$this->MODULE_DESCRIPTION = Loc::getMessage('VENDOR_MODULE_INSTALL_DESCRIPTION');
	}

	public function InstallDB($params = [])
	{
		global $APPLICATION;
		$connection = Application::getConnection();

		$this->errors = $this->runSqlBatch(
			$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/db/' . $connection->getType() . '/install.sql'
		);
		if (!empty($this->errors))
		{
			$APPLICATION->ThrowException(implode('<br>', $this->errors));
			return false;
		}

		RegisterModule($this->MODULE_ID);
		$this->installEventHandlers();
		$this->installAgents();
		return true;
	}

	public function UnInstallDB($params = [])
	{
		global $APPLICATION;
		$connection = Application::getConnection();

		$this->uninstallEventHandlers();
		$this->uninstallAgents();

		if (($params['savedata'] ?? 'Y') !== 'Y')
		{
			$this->errors = $this->runSqlBatch(
				$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/db/' . $connection->getType() . '/uninstall.sql'
			);
			if (!empty($this->errors))
			{
				$APPLICATION->ThrowException(implode('<br>', $this->errors));
				return false;
			}
		}

		UnRegisterModule($this->MODULE_ID);
		return true;
	}

	public function InstallFiles($params = [])
	{
		CopyDirFiles(
			$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/admin',
			$_SERVER['DOCUMENT_ROOT'] . '/bitrix/admin',
			true,
			true
		);
		return true;
	}

	public function UnInstallFiles()
	{
		DeleteDirFiles(
			$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/admin',
			$_SERVER['DOCUMENT_ROOT'] . '/bitrix/admin'
		);
		return true;
	}

	private function installEventHandlers(): void
	{
		RegisterModuleDependences('main', 'OnBeforeProlog', $this->MODULE_ID, '\\Vendor\\Module\\EventHandler', 'onBeforeProlog');
	}

	private function uninstallEventHandlers(): void
	{
		UnRegisterModuleDependences('main', 'OnBeforeProlog', $this->MODULE_ID, '\\Vendor\\Module\\EventHandler', 'onBeforeProlog');
	}

	private function installAgents(): void
	{
		CAgent::AddAgent('\\Vendor\\Module\\Agent\\SyncAgent::run();', $this->MODULE_ID, 'N', 3600);
	}

	private function uninstallAgents(): void
	{
		CAgent::RemoveModuleAgents($this->MODULE_ID);
	}

	private function runSqlBatch(string $filePath): array
	{
		global $DB;

		$connection = Application::getConnection();
		if (method_exists($connection, 'runSqlBatch'))
		{
			$result = $connection->runSqlBatch($filePath);
			return is_array($result) ? $result : [];
		}

		if (is_object($DB) && method_exists($DB, 'RunSQLBatch'))
		{
			$result = $DB->RunSQLBatch($filePath);
			return is_array($result) ? $result : [];
		}

		return ['SQL batch runner is not available for this Bitrix core build.'];
	}

	public function DoInstall()
	{
		global $APPLICATION, $USER, $step;
		$step = (int)$step;

		if (!$USER->IsAdmin())
		{
			return;
		}

		if (!check_bitrix_sessid())
		{
			$step = 1;
		}

		if ($step < 2)
		{
			$APPLICATION->IncludeAdminFile(
				Loc::getMessage('VENDOR_MODULE_INSTALL_TITLE'),
				$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/step1.php'
			);
		}
		elseif ($step === 2)
		{
			$this->InstallDB();
			$this->InstallFiles();
			$GLOBALS['errors'] = $this->errors;

			$APPLICATION->IncludeAdminFile(
				Loc::getMessage('VENDOR_MODULE_INSTALL_TITLE'),
				$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/step2.php'
			);
		}
	}

	public function DoUninstall()
	{
		global $APPLICATION, $USER, $step;
		$step = (int)$step;

		if (!$USER->IsAdmin())
		{
			return;
		}

		if ($step < 2)
		{
			$APPLICATION->IncludeAdminFile(
				Loc::getMessage('VENDOR_MODULE_UNINSTALL_TITLE'),
				$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/unstep1.php'
			);
		}
		elseif ($step === 2)
		{
			$this->UnInstallDB(['savedata' => $_REQUEST['savedata'] ?? 'Y']);
			$this->UnInstallFiles();
			$GLOBALS['errors'] = $this->errors;

			$APPLICATION->IncludeAdminFile(
				Loc::getMessage('VENDOR_MODULE_UNINSTALL_TITLE'),
				$_SERVER['DOCUMENT_ROOT'] . '/local/modules/vendor.module/install/unstep2.php'
			);
		}
	}
}
```

Notes:

- Keep `Install*` and `UnInstall*` symmetric.
- Keep permission and session checks in `DoInstall`/`DoUninstall`.
- If module must keep data by default, use `savedata=Y` gate as shown.
- If component directories are copied to `/bitrix/components`, add explicit `DeleteDirFilesEx('/bitrix/components/<vendor>/<component>')` in uninstall.
