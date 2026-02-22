# Template: Migration `up/down` for HL User Fields (UF)

Use this when adding/changing user fields for an HL entity.

```php
<?php

use Bitrix\Main\Loader;

final class UpdateEmployeeHlUfMigration
{
	private const HL_ENTITY_ID = 'HLBLOCK_12'; // replace with real HL entity id

	public function up(): void
	{
		if (!Loader::includeModule('main'))
		{
			throw new \RuntimeException('Module main is not available.');
		}

		$this->saveUserField([
			'ENTITY_ID' => self::HL_ENTITY_ID,
			'FIELD_NAME' => 'UF_NAME',
			'USER_TYPE_ID' => 'string',
			'XML_ID' => 'UF_NAME',
			'SORT' => 100,
			'MULTIPLE' => 'N',
			'MANDATORY' => 'Y',
			'SHOW_FILTER' => 'I',
			'SHOW_IN_LIST' => 'Y',
			'EDIT_IN_LIST' => 'Y',
			'IS_SEARCHABLE' => 'Y',
			'SETTINGS' => ['SIZE' => 30, 'ROWS' => 1, 'REGEXP' => ''],
			'EDIT_FORM_LABEL' => ['ru' => 'Имя', 'en' => 'Name'],
			'LIST_COLUMN_LABEL' => ['ru' => 'Имя', 'en' => 'Name'],
			'LIST_FILTER_LABEL' => ['ru' => 'Имя', 'en' => 'Name'],
		]);

		$this->saveUserField([
			'ENTITY_ID' => self::HL_ENTITY_ID,
			'FIELD_NAME' => 'UF_ACTIVE',
			'USER_TYPE_ID' => 'boolean',
			'XML_ID' => 'UF_ACTIVE',
			'SORT' => 200,
			'MULTIPLE' => 'N',
			'MANDATORY' => 'N',
			'SHOW_FILTER' => 'I',
			'SHOW_IN_LIST' => 'Y',
			'EDIT_IN_LIST' => 'Y',
			'IS_SEARCHABLE' => 'N',
			'SETTINGS' => ['DEFAULT_VALUE' => 1],
			'EDIT_FORM_LABEL' => ['ru' => 'Активность', 'en' => 'Active'],
			'LIST_COLUMN_LABEL' => ['ru' => 'Активность', 'en' => 'Active'],
			'LIST_FILTER_LABEL' => ['ru' => 'Активность', 'en' => 'Active'],
		]);
	}

	public function down(): void
	{
		if (!Loader::includeModule('main'))
		{
			throw new \RuntimeException('Module main is not available.');
		}

		$this->deleteUserField(self::HL_ENTITY_ID, 'UF_NAME');
		$this->deleteUserField(self::HL_ENTITY_ID, 'UF_ACTIVE');
	}

	private function saveUserField(array $field): void
	{
		$existing = $this->findUserField($field['ENTITY_ID'], $field['FIELD_NAME']);
		$userTypeEntity = new \CUserTypeEntity();

		if ($existing)
		{
			$ok = $userTypeEntity->Update((int)$existing['ID'], $field);
			if (!$ok)
			{
				throw new \RuntimeException('UF update failed: ' . $field['FIELD_NAME']);
			}
			return;
		}

		$id = (int)$userTypeEntity->Add($field);
		if ($id <= 0)
		{
			throw new \RuntimeException('UF add failed: ' . $field['FIELD_NAME']);
		}
	}

	private function deleteUserField(string $entityId, string $fieldName): void
	{
		$existing = $this->findUserField($entityId, $fieldName);
		if (!$existing)
		{
			return;
		}

		$userTypeEntity = new \CUserTypeEntity();
		$ok = $userTypeEntity->Delete((int)$existing['ID']);
		if (!$ok)
		{
			throw new \RuntimeException('UF delete failed: ' . $fieldName);
		}
	}

	private function findUserField(string $entityId, string $fieldName): ?array
	{
		$res = \CUserTypeEntity::GetList(
			['ID' => 'ASC'],
			['ENTITY_ID' => $entityId, 'FIELD_NAME' => $fieldName]
		);
		$row = $res->Fetch();
		return is_array($row) ? $row : null;
	}
}
```

## Notes

- Keep UF changes idempotent (update if exists, add otherwise).
- In rollback (`down`), delete only fields owned by this migration scope.
