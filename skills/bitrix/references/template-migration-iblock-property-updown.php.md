# Template: Migration `up/down` for IBlock Property

Use this when creating/updating an iblock property safely.

```php
<?php

use Bitrix\Main\Loader;

final class UpdateEmployeeIblockPropertyMigration
{
	private const IBLOCK_ID = 10; // replace
	private const PROPERTY_CODE = 'EMPLOYEE_ID';

	public function up(): void
	{
		if (!Loader::includeModule('iblock'))
		{
			throw new \RuntimeException('Module iblock is not available.');
		}

		$property = $this->findProperty(self::IBLOCK_ID, self::PROPERTY_CODE);
		$fields = [
			'IBLOCK_ID' => self::IBLOCK_ID,
			'NAME' => 'Employee ID',
			'ACTIVE' => 'Y',
			'SORT' => 500,
			'CODE' => self::PROPERTY_CODE,
			'PROPERTY_TYPE' => 'N',
			'MULTIPLE' => 'N',
			'IS_REQUIRED' => 'N',
			'FILTRABLE' => 'Y',
			'SEARCHABLE' => 'Y',
		];

		$ibp = new \CIBlockProperty();
		if ($property)
		{
			$ok = $ibp->Update((int)$property['ID'], $fields);
			if (!$ok)
			{
				throw new \RuntimeException($ibp->LAST_ERROR ?: 'IBlock property update failed.');
			}
			return;
		}

		$newId = (int)$ibp->Add($fields);
		if ($newId <= 0)
		{
			throw new \RuntimeException($ibp->LAST_ERROR ?: 'IBlock property add failed.');
		}
	}

	public function down(): void
	{
		if (!Loader::includeModule('iblock'))
		{
			throw new \RuntimeException('Module iblock is not available.');
		}

		$property = $this->findProperty(self::IBLOCK_ID, self::PROPERTY_CODE);
		if (!$property)
		{
			return;
		}

		$ok = \CIBlockProperty::Delete((int)$property['ID']);
		if (!$ok)
		{
			throw new \RuntimeException('IBlock property delete failed.');
		}
	}

	private function findProperty(int $iblockId, string $code): ?array
	{
		$res = \CIBlockProperty::GetList(
			['ID' => 'ASC'],
			['IBLOCK_ID' => $iblockId, 'CODE' => $code]
		);
		$row = $res->Fetch();
		return is_array($row) ? $row : null;
	}
}
```

## Notes

- `CODE` must be stable and unique in iblock.
- For non-destructive rollback, switch `down()` to disable property (`ACTIVE = N`) instead of delete.
