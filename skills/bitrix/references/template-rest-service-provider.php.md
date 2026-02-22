# Template: REST Service Provider (`onRestServiceBuildDescription`)

Use for box/server-side module REST methods.

```php
<?php

namespace Vendor\Module\Rest;

use Bitrix\Main\Loader;
use Bitrix\Rest\AccessException;
use Bitrix\Rest\RestException;

if (!Loader::includeModule('rest'))
{
	return;
}

class Service extends \IRestService
{
	public const SCOPE = 'vendor_module';

	public static function onRestServiceBuildDescription(): array
	{
		return [
			static::SCOPE => [
				'vendor.module.list' => [static::class, 'listAction'],
				'vendor.module.add' => [static::class, 'addAction'],
				\CRestUtil::EVENTS => [
					'OnVendorModuleChanged' => [
						'vendor.module',
						'OnVendorModuleChanged',
						[static::class, 'prepareEventPayload'],
						[
							'category' => \Bitrix\Rest\Sqs::CATEGORY_DEFAULT,
							'allowOptions' => ['mode' => 'string'],
						],
					],
				],
			],
		];
	}

	public static function listAction(array $params, $nav, \CRestServer $server): array
	{
		static::assertReadAccess();

		$limit = isset($params['limit']) ? (int)$params['limit'] : 50;
		if ($limit <= 0)
		{
			throw new RestException('Parameter limit must be positive integer', RestException::ERROR_ARGUMENT);
		}

		// Read and return list data from module storage.
		return [
			'items' => [],
			'total' => 0,
		];
	}

	public static function addAction(array $params, $nav, \CRestServer $server): array
	{
		static::assertWriteAccess();

		$name = trim((string)($params['name'] ?? ''));
		if ($name === '')
		{
			throw new RestException('Parameter name is required', RestException::ERROR_ARGUMENT);
		}

		// Save data and return identifier.
		return ['id' => 1];
	}

	public static function prepareEventPayload(array $eventParams, array $handlerFields): array
	{
		// Build deterministic payload for REST event delivery.
		return [
			'FIELDS' => [
				'ID' => (int)($eventParams['ID'] ?? 0),
			],
		];
	}

	public static function onRestAppDelete(array $fields): void
	{
		// Remove app-bound records only when full cleanup is requested.
		if (empty($fields['APP_ID']) || empty($fields['CLEAN']) || $fields['CLEAN'] !== true)
		{
			return;
		}

		// Delete app-linked module records here.
	}

	private static function assertReadAccess(): void
	{
		if (!\CRestUtil::isAdmin())
		{
			throw new AccessException('Access denied.');
		}
	}

	private static function assertWriteAccess(): void
	{
		if (!\CRestUtil::isAdmin())
		{
			throw new AccessException('Access denied.');
		}
	}
}
```

Notes:

- Keep permission checks at method entry.
- Validate all incoming params and throw typed exceptions.
- Keep app cleanup path (`onRestAppDelete`) deterministic and idempotent.
- For cloud apps, do not use this server-side pattern; use external app backend only.
