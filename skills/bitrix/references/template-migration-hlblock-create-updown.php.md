# Template: Migration `up/down` for Highloadblock Create/Delete

Use this as a generic migration template (framework-agnostic `up/down` style).

```php
<?php

use Bitrix\Highloadblock\HighloadBlockLangTable;
use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Loader;

final class CreateEmployeeHlblockMigration
{
	private const HL_NAME = 'EmployeeRegistry';
	private const TABLE_NAME = 'vendor_employee_registry';

	public function up(): void
	{
		if (!Loader::includeModule('highloadblock'))
		{
			throw new \RuntimeException('Module highloadblock is not available.');
		}

		$existing = HighloadBlockTable::getList([
			'filter' => ['=TABLE_NAME' => self::TABLE_NAME],
			'select' => ['ID'],
			'limit' => 1,
		])->fetch();
		if ($existing)
		{
			return;
		}

		$addResult = HighloadBlockTable::add([
			'NAME' => self::HL_NAME,
			'TABLE_NAME' => self::TABLE_NAME,
		]);
		if (!$addResult->isSuccess())
		{
			throw new \RuntimeException(implode('; ', $addResult->getErrorMessages()));
		}

		$hlId = (int)$addResult->getId();

		$langRows = [
			['LID' => 'ru', 'NAME' => 'Сотрудники'],
			['LID' => 'en', 'NAME' => 'Employees'],
		];

		foreach ($langRows as $row)
		{
			HighloadBlockLangTable::add([
				'ID' => $hlId,
				'LID' => $row['LID'],
				'NAME' => $row['NAME'],
			]);
		}
	}

	public function down(): void
	{
		if (!Loader::includeModule('highloadblock'))
		{
			throw new \RuntimeException('Module highloadblock is not available.');
		}

		$hl = HighloadBlockTable::getList([
			'filter' => ['=TABLE_NAME' => self::TABLE_NAME],
			'select' => ['ID'],
			'limit' => 1,
		])->fetch();

		if (!$hl)
		{
			return;
		}

		$deleteResult = HighloadBlockTable::delete((int)$hl['ID']);
		if (!$deleteResult->isSuccess())
		{
			throw new \RuntimeException(implode('; ', $deleteResult->getErrorMessages()));
		}
	}
}
```

## Notes

- Keep `TABLE_NAME` stable; use it as idempotent key.
- If data retention is required, replace delete with "soft rollback" and document it.
