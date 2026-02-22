# Template: Highloadblock Repository + Service (CRUD + Unified Errors)

Use this pair when module logic works with HL entities and UF-heavy registries.

## `lib/Hl/EmployeeRepository.php`

```php
<?php

namespace Vendor\Module\Hl;

use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Error;
use Bitrix\Main\Loader;
use Bitrix\Main\Result;

class EmployeeRepository
{
	private int $hlId;
	private string $dataClass;

	public function __construct(int $hlId)
	{
		if (!Loader::includeModule('highloadblock'))
		{
			throw new \RuntimeException('Module highloadblock is not available.');
		}

		$this->hlId = $hlId;
		$this->dataClass = $this->resolveDataClass($hlId);
	}

	public function list(
		array $filter = [],
		array $order = ['ID' => 'DESC'],
		int $limit = 50,
		int $offset = 0,
		array $select = ['*']
	): array
	{
		try
		{
			$dataClass = $this->dataClass;
			$res = $dataClass::getList([
				'filter' => $filter,
				'order' => $order,
				'limit' => $limit,
				'offset' => $offset,
				'select' => $select,
			]);
			return $res->fetchAll();
		}
		catch (\Throwable)
		{
			return [];
		}
	}

	public function getById(int $id): ?array
	{
		if ($id <= 0)
		{
			return null;
		}

		try
		{
			$dataClass = $this->dataClass;
			$row = $dataClass::getById($id)->fetch();
			return is_array($row) ? $row : null;
		}
		catch (\Throwable)
		{
			return null;
		}
	}

	public function add(array $fields): Result
	{
		try
		{
			$dataClass = $this->dataClass;
			$addResult = $dataClass::add($fields);
			if (!$addResult->isSuccess())
			{
				return $this->fail(implode('; ', $addResult->getErrorMessages()), 'HL_ADD_FAILED');
			}

			$result = new Result();
			$result->setData(['ID' => (int)$addResult->getId()]);
			return $result;
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'HL add failed');
		}
	}

	public function update(int $id, array $fields): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid row ID.', 'INVALID_ID');
		}

		try
		{
			$dataClass = $this->dataClass;
			$updateResult = $dataClass::update($id, $fields);
			if (!$updateResult->isSuccess())
			{
				return $this->fail(implode('; ', $updateResult->getErrorMessages()), 'HL_UPDATE_FAILED');
			}

			return new Result();
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'HL update failed');
		}
	}

	public function delete(int $id): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid row ID.', 'INVALID_ID');
		}

		try
		{
			$dataClass = $this->dataClass;
			$deleteResult = $dataClass::delete($id);
			if (!$deleteResult->isSuccess())
			{
				return $this->fail(implode('; ', $deleteResult->getErrorMessages()), 'HL_DELETE_FAILED');
			}

			return new Result();
		}
		catch (\Throwable $e)
		{
			return $this->failThrowable($e, 'HL delete failed');
		}
	}

	private function resolveDataClass(int $hlId): string
	{
		$hl = HighloadBlockTable::getById($hlId)->fetch();
		if (!$hl)
		{
			throw new \RuntimeException('Highloadblock not found: ' . $hlId);
		}

		$entity = HighloadBlockTable::compileEntity($hl);
		return $entity->getDataClass();
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

## `lib/Hl/EmployeeService.php`

```php
<?php

namespace Vendor\Module\Hl;

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

		return $this->repository->add($this->mapPayloadToFields($payload));
	}

	public function update(int $id, array $payload): Result
	{
		if ($id <= 0)
		{
			return $this->fail('Invalid row ID.', 'INVALID_ID');
		}

		$validation = $this->validateUpdate($payload);
		if (!$validation->isSuccess())
		{
			return $validation;
		}

		return $this->repository->update($id, $this->mapPayloadToFields($payload));
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
		$name = trim((string)($payload['UF_NAME'] ?? ''));
		if ($name === '')
		{
			$result->addError(new Error('Field UF_NAME is required.', 'UF_NAME_REQUIRED'));
		}
		return $result;
	}

	private function validateUpdate(array $payload): Result
	{
		$result = new Result();
		if (array_key_exists('UF_NAME', $payload) && trim((string)$payload['UF_NAME']) === '')
		{
			$result->addError(new Error('Field UF_NAME cannot be empty.', 'UF_NAME_EMPTY'));
		}
		return $result;
	}

	private function mapPayloadToFields(array $payload): array
	{
		$fields = [];
		if (array_key_exists('UF_NAME', $payload))
		{
			$fields['UF_NAME'] = trim((string)$payload['UF_NAME']);
		}
		if (array_key_exists('UF_ACTIVE', $payload))
		{
			$fields['UF_ACTIVE'] = ($payload['UF_ACTIVE'] === 'N' ? 'N' : 'Y');
		}
		if (array_key_exists('UF_SORT', $payload))
		{
			$fields['UF_SORT'] = (int)$payload['UF_SORT'];
		}
		if (array_key_exists('UF_NOTE', $payload))
		{
			$fields['UF_NOTE'] = (string)$payload['UF_NOTE'];
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

- Keep rights checks in admin endpoints before service calls.
- Use `Result + Error` across all operations for predictable error handling.
- For UF file fields and copy flow, strip file values explicitly in service logic.
