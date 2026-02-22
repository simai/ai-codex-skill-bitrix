# Template: IBlock Repository + Service (CRUD + Unified Errors)

Use this pair when module logic must work with iblock data through service boundaries.

## `lib/Iblock/EmployeeRepository.php`

```php
<?php

namespace Vendor\Module\Iblock;

use Bitrix\Main\Error;
use Bitrix\Main\Loader;
use Bitrix\Main\Result;

class EmployeeRepository
{
	private int $iblockId;

	public function __construct(int $iblockId)
	{
		if (!Loader::includeModule('iblock'))
		{
			throw new \RuntimeException('Module iblock is not available.');
		}

		$this->iblockId = $iblockId;
	}

	public function list(
		array $filter = [],
		array $order = ['ID' => 'DESC'],
		int $limit = 50,
		int $offset = 0,
		array $select = ['ID', 'IBLOCK_ID', 'NAME', 'ACTIVE', 'TIMESTAMP_X']
	): array
	{
		$filter['=IBLOCK_ID'] = $this->iblockId;
		$nav = ['nTopCount' => $limit];
		if ($offset > 0)
		{
			$nav = ['nPageSize' => $limit, 'iNumPage' => (int)floor($offset / max($limit, 1)) + 1];
		}

		$result = [];
		$res = \CIBlockElement::GetList($order, $filter, false, $nav, $select);
		while ($row = $res->Fetch())
		{
			$result[] = $row;
		}

		return $result;
	}

	public function getById(int $id, array $select = ['ID', 'IBLOCK_ID', 'NAME', 'ACTIVE', 'TIMESTAMP_X']): ?array
	{
		if ($id <= 0)
		{
			return null;
		}

		$res = \CIBlockElement::GetList([], ['=ID' => $id, '=IBLOCK_ID' => $this->iblockId], false, ['nTopCount' => 1], $select);
		$row = $res->Fetch();

		return is_array($row) ? $row : null;
	}

	public function add(array $fields): Result
	{
		try
		{
			$fields['IBLOCK_ID'] = $this->iblockId;
			$el = new \CIBlockElement();
			$id = (int)$el->Add($fields);
			if ($id <= 0)
			{
				return $this->fail($el->LAST_ERROR ?: 'Unable to add iblock element.', 'IBLOCK_ADD_FAILED');
			}

			$result = new Result();
			$result->setData(['ID' => $id]);
			return $result;
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'Iblock add failed');
		}
	}

	public function update(int $id, array $fields): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid element ID.', 'INVALID_ID');
		}

		try
		{
			$el = new \CIBlockElement();
			$ok = $el->Update($id, $fields);
			if (!$ok)
			{
				return $this->fail($el->LAST_ERROR ?: 'Unable to update iblock element.', 'IBLOCK_UPDATE_FAILED');
			}

			return new Result();
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'Iblock update failed');
		}
	}

	public function delete(int $id): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid element ID.', 'INVALID_ID');
		}

		try
		{
			$ok = \CIBlockElement::Delete($id);
			if (!$ok)
			{
				return $this->fail('Unable to delete iblock element.', 'IBLOCK_DELETE_FAILED');
			}

			return new Result();
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'Iblock delete failed');
		}
	}

	private function fail(string $message, string $code): Result
	{
		$result = new Result();
		$result->addError(new Error($message, $code));
		return $result;
	}

	private function failThrowable(\Throwable $e, string $context): Result
	{
		return $this->fail($context . ': ' . $e->getMessage(), 'EXCEPTION');
	}
}
```

## `lib/Iblock/EmployeeService.php`

```php
<?php

namespace Vendor\Module\Iblock;

use Bitrix\Main\Error;
use Bitrix\Main\Result;

class EmployeeService
{
	public function __construct(
		private readonly EmployeeRepository $repository
	)
	{
	}

	public function create(array $payload): Result
	{
		$validation = $this->validateCreate($payload);
		if (!$validation->isSuccess())
		{
			return $validation;
		}

		$fields = $this->mapPayloadToFields($payload);
		return $this->repository->add($fields);
	}

	public function update(int $id, array $payload): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid element ID.', 'INVALID_ID');
		}

		$validation = $this->validateUpdate($payload);
		if (!$validation->isSuccess())
		{
			return $validation;
		}

		$fields = $this->mapPayloadToFields($payload);
		return $this->repository->update($id, $fields);
	}

	public function delete(int $id): Result
	{
		return $this->repository->delete($id);
	}

	public function get(int $id): ?array
	{
		return $this->repository->getById($id);
	}

	public function list(array $filter = [], array $order = ['ID' => 'DESC'], int $limit = 50, int $offset = 0): array
	{
		return $this->repository->list($filter, $order, $limit, $offset);
	}

	private function validateCreate(array $payload): Result
	{
		$result = new Result();
		$name = trim((string)($payload['NAME'] ?? ''));
		if ($name === '')
		{
			$result->addError(new Error('Field NAME is required.', 'NAME_REQUIRED'));
		}
		return $result;
	}

	private function validateUpdate(array $payload): Result
	{
		$result = new Result();
		if (array_key_exists('NAME', $payload) && trim((string)$payload['NAME']) === '')
		{
			$result->addError(new Error('Field NAME cannot be empty.', 'NAME_EMPTY'));
		}
		return $result;
	}

	private function mapPayloadToFields(array $payload): array
	{
		$fields = [];

		if (array_key_exists('NAME', $payload))
		{
			$fields['NAME'] = trim((string)$payload['NAME']);
		}
		if (array_key_exists('ACTIVE', $payload))
		{
			$fields['ACTIVE'] = ($payload['ACTIVE'] === 'N' ? 'N' : 'Y');
		}
		if (array_key_exists('SORT', $payload))
		{
			$fields['SORT'] = (int)$payload['SORT'];
		}
		if (array_key_exists('PREVIEW_TEXT', $payload))
		{
			$fields['PREVIEW_TEXT'] = (string)$payload['PREVIEW_TEXT'];
		}
		if (array_key_exists('PROPERTY_VALUES', $payload) && is_array($payload['PROPERTY_VALUES']))
		{
			$fields['PROPERTY_VALUES'] = $payload['PROPERTY_VALUES'];
		}

		return $fields;
	}

	private function fail(string $message, string $code): Result
	{
		$result = new Result();
		$result->addError(new Error($message, $code));
		return $result;
	}
}
```

## Notes

- Keep all admin pages working through service methods, not direct `CIBlockElement` writes.
- Add rights checks before service calls in admin controllers.
- Keep one error model (`Result + Error`) across repository and service layers.
