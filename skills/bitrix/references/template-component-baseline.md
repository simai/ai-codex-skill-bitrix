# Template: Component Baseline (`local/components/vendor/feature`)

Use as a practical starter for Bitrix components in `Site Management` or `Bitrix24 box`.

## Recommended Structure

```text
local/components/vendor/feature/
  class.php
  .description.php
  .parameters.php
  templates/.default/template.php
  lang/ru/.description.php
  lang/ru/.parameters.php
  lang/ru/class.php
  templates/.default/lang/ru/template.php
```

## `class.php`

```php
<?php

use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;
use Bitrix\Main\SystemException;

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true)
{
	die();
}

Loc::loadMessages(__FILE__);

class VendorFeatureComponent extends CBitrixComponent
{
	private const CACHE_TTL_DEFAULT = 3600;

	public function onPrepareComponentParams($params): array
	{
		$params['CACHE_TIME'] = isset($params['CACHE_TIME']) ? (int)$params['CACHE_TIME'] : self::CACHE_TTL_DEFAULT;
		$params['LIMIT'] = isset($params['LIMIT']) ? max(1, (int)$params['LIMIT']) : 20;
		$params['SORT_BY'] = trim((string)($params['SORT_BY'] ?? 'ID'));
		$params['SORT_ORDER'] = strtoupper(trim((string)($params['SORT_ORDER'] ?? 'DESC')));
		$params['SORT_ORDER'] = in_array($params['SORT_ORDER'], ['ASC', 'DESC'], true) ? $params['SORT_ORDER'] : 'DESC';

		return $params;
	}

	public function executeComponent(): void
	{
		try
		{
			$this->validateEnvironment();
			$cacheTtl = (int)$this->arParams['CACHE_TIME'];
			$cacheKey = [$this->arParams['LIMIT'], $this->arParams['SORT_BY'], $this->arParams['SORT_ORDER']];

			if ($this->startResultCache($cacheTtl, $cacheKey))
			{
				$this->arResult['ITEMS'] = $this->loadItems();
				$this->includeComponentTemplate();
			}
		}
		catch (\Throwable $e)
		{
			$this->abortResultCache();
			ShowError($e->getMessage());
		}
	}

	private function validateEnvironment(): void
	{
		if (!Loader::includeModule('iblock'))
		{
			throw new SystemException(Loc::getMessage('VENDOR_FEATURE_ERR_IBLOCK'));
		}
	}

	private function loadItems(): array
	{
		$result = [];

		$res = \CIBlockElement::GetList(
			[$this->arParams['SORT_BY'] => $this->arParams['SORT_ORDER']],
			['ACTIVE' => 'Y'],
			false,
			['nTopCount' => $this->arParams['LIMIT']],
			['ID', 'NAME', 'DATE_ACTIVE_FROM']
		);

		while ($row = $res->Fetch())
		{
			$result[] = [
				'ID' => (int)$row['ID'],
				'NAME' => (string)$row['NAME'],
				'DATE_ACTIVE_FROM' => (string)$row['DATE_ACTIVE_FROM'],
			];
		}

		return $result;
	}
}
```

## `.description.php`

```php
<?php

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true)
{
	die();
}

$arComponentDescription = [
	'NAME' => GetMessage('VENDOR_FEATURE_COMPONENT_NAME'),
	'DESCRIPTION' => GetMessage('VENDOR_FEATURE_COMPONENT_DESC'),
	'ICON' => '/images/icon.gif',
	'PATH' => [
		'ID' => 'vendor',
		'NAME' => GetMessage('VENDOR_FEATURE_COMPONENT_SECTION'),
	],
];
```

## `.parameters.php`

```php
<?php

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true)
{
	die();
}

$arComponentParameters = [
	'PARAMETERS' => [
		'LIMIT' => [
			'PARENT' => 'BASE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_LIMIT'),
			'TYPE' => 'STRING',
			'DEFAULT' => '20',
		],
		'SORT_BY' => [
			'PARENT' => 'DATA_SOURCE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_SORT_BY'),
			'TYPE' => 'LIST',
			'VALUES' => [
				'ID' => 'ID',
				'NAME' => 'NAME',
				'DATE_ACTIVE_FROM' => 'DATE_ACTIVE_FROM',
			],
			'DEFAULT' => 'ID',
		],
		'SORT_ORDER' => [
			'PARENT' => 'DATA_SOURCE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_SORT_ORDER'),
			'TYPE' => 'LIST',
			'VALUES' => [
				'ASC' => 'ASC',
				'DESC' => 'DESC',
			],
			'DEFAULT' => 'DESC',
		],
		'CACHE_TIME' => ['DEFAULT' => 3600],
	],
];
```

## `templates/.default/template.php`

```php
<?php

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true)
{
	die();
}
?>
<div class="vendor-feature-list">
	<?php if (empty($arResult['ITEMS'])): ?>
		<div class="vendor-feature-list__empty"><?=htmlspecialcharsbx(GetMessage('VENDOR_FEATURE_EMPTY'))?></div>
	<?php else: ?>
		<ul class="vendor-feature-list__items">
			<?php foreach ($arResult['ITEMS'] as $item): ?>
				<li class="vendor-feature-list__item">
					<span class="vendor-feature-list__name"><?=htmlspecialcharsbx($item['NAME'])?></span>
				</li>
			<?php endforeach; ?>
		</ul>
	<?php endif; ?>
</div>
```

## Baseline Rules

- Validate params in `onPrepareComponentParams`.
- Keep all data loading in `class.php`; template only renders.
- Include required modules explicitly via `Loader::includeModule`.
- Use caching with stable cache key based on input params.
- On exception, always call `abortResultCache()`.

If you need pagination, tag cache, or `SetResultCacheKeys`, use:
`references/template-component-advanced-pagination-tagcache.md`
