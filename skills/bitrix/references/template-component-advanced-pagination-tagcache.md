# Template: Component Advanced (Pagination + Tag Cache + `SetResultCacheKeys`)

Use when component must support page navigation and cache invalidation by iblock tags.

## Recommended Structure

```text
local/components/vendor/feature.list/
  class.php
  .description.php
  .parameters.php
  templates/.default/template.php
  component_epilog.php (optional)
  lang/ru/class.php
  templates/.default/lang/ru/template.php
```

## `class.php`

```php
<?php

use Bitrix\Main\Application;
use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;
use Bitrix\Main\SystemException;

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true)
{
	die();
}

Loc::loadMessages(__FILE__);

class VendorFeatureListComponent extends CBitrixComponent
{
	private const CACHE_TTL_DEFAULT = 3600;
	private const PAGE_SIZE_DEFAULT = 20;

	public function onPrepareComponentParams($params): array
	{
		$params['CACHE_TIME'] = isset($params['CACHE_TIME']) ? (int)$params['CACHE_TIME'] : self::CACHE_TTL_DEFAULT;
		$params['IBLOCK_ID'] = isset($params['IBLOCK_ID']) ? (int)$params['IBLOCK_ID'] : 0;
		$params['SECTION_ID'] = isset($params['SECTION_ID']) ? (int)$params['SECTION_ID'] : 0;
		$params['PAGE_SIZE'] = isset($params['PAGE_SIZE']) ? max(1, (int)$params['PAGE_SIZE']) : self::PAGE_SIZE_DEFAULT;
		$params['SORT_BY'] = trim((string)($params['SORT_BY'] ?? 'ACTIVE_FROM'));
		$params['SORT_ORDER'] = strtoupper(trim((string)($params['SORT_ORDER'] ?? 'DESC')));
		$params['SORT_ORDER'] = in_array($params['SORT_ORDER'], ['ASC', 'DESC'], true) ? $params['SORT_ORDER'] : 'DESC';

		return $params;
	}

	public function executeComponent(): void
	{
		try
		{
			$this->validateEnvironment();

			$page = max(1, (int)($_REQUEST['PAGEN_1'] ?? 1));
			$cacheKey = [
				$this->arParams['IBLOCK_ID'],
				$this->arParams['SECTION_ID'],
				$this->arParams['PAGE_SIZE'],
				$this->arParams['SORT_BY'],
				$this->arParams['SORT_ORDER'],
				$page,
			];

			if ($this->startResultCache((int)$this->arParams['CACHE_TIME'], $cacheKey))
			{
				$this->registerTagCache();
				$this->arResult = $this->buildResult($page);

				$this->SetResultCacheKeys(['SECTION_NAME', 'NAV_STRING']);
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

		if ($this->arParams['IBLOCK_ID'] <= 0)
		{
			throw new SystemException(Loc::getMessage('VENDOR_FEATURE_ERR_IBLOCK_ID'));
		}
	}

	private function registerTagCache(): void
	{
		$taggedCache = Application::getInstance()->getTaggedCache();
		$taggedCache->startTagCache($this->GetCachePath());
		$taggedCache->registerTag('iblock_id_' . $this->arParams['IBLOCK_ID']);
		$taggedCache->endTagCache();
	}

	private function buildResult(int $page): array
	{
		$result = [
			'SECTION_NAME' => '',
			'ITEMS' => [],
			'NAV_STRING' => '',
		];

		if ($this->arParams['SECTION_ID'] > 0)
		{
			$section = \CIBlockSection::GetByID($this->arParams['SECTION_ID'])->Fetch();
			if ($section)
			{
				$result['SECTION_NAME'] = (string)$section['NAME'];
			}
		}

		$filter = [
			'IBLOCK_ID' => $this->arParams['IBLOCK_ID'],
			'ACTIVE' => 'Y',
			'ACTIVE_DATE' => 'Y',
		];
		if ($this->arParams['SECTION_ID'] > 0)
		{
			$filter['SECTION_ID'] = $this->arParams['SECTION_ID'];
			$filter['INCLUDE_SUBSECTIONS'] = 'Y';
		}

		$res = \CIBlockElement::GetList(
			[$this->arParams['SORT_BY'] => $this->arParams['SORT_ORDER']],
			$filter,
			false,
			[
				'nPageSize' => $this->arParams['PAGE_SIZE'],
				'iNumPage' => $page,
			],
			['ID', 'IBLOCK_ID', 'NAME', 'DETAIL_PAGE_URL', 'PREVIEW_TEXT', 'ACTIVE_FROM']
		);

		while ($item = $res->GetNext())
		{
			$result['ITEMS'][] = [
				'ID' => (int)$item['ID'],
				'NAME' => (string)$item['NAME'],
				'DETAIL_PAGE_URL' => (string)$item['DETAIL_PAGE_URL'],
				'PREVIEW_TEXT' => (string)$item['PREVIEW_TEXT'],
				'ACTIVE_FROM' => (string)$item['ACTIVE_FROM'],
			];
		}

		$navComponentObject = null;
		$result['NAV_STRING'] = $res->GetPageNavStringEx(
			$navComponentObject,
			Loc::getMessage('VENDOR_FEATURE_NAV_TITLE'),
			'modern'
		);

		return $result;
	}
}
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
		'IBLOCK_ID' => [
			'PARENT' => 'BASE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_IBLOCK_ID'),
			'TYPE' => 'STRING',
			'DEFAULT' => '',
		],
		'SECTION_ID' => [
			'PARENT' => 'BASE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_SECTION_ID'),
			'TYPE' => 'STRING',
			'DEFAULT' => '',
		],
		'PAGE_SIZE' => [
			'PARENT' => 'DATA_SOURCE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_PAGE_SIZE'),
			'TYPE' => 'STRING',
			'DEFAULT' => '20',
		],
		'SORT_BY' => [
			'PARENT' => 'DATA_SOURCE',
			'NAME' => GetMessage('VENDOR_FEATURE_PARAM_SORT_BY'),
			'TYPE' => 'LIST',
			'VALUES' => [
				'ACTIVE_FROM' => 'ACTIVE_FROM',
				'NAME' => 'NAME',
				'ID' => 'ID',
			],
			'DEFAULT' => 'ACTIVE_FROM',
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
	<?php if ($arResult['SECTION_NAME'] !== ''): ?>
		<h2 class="vendor-feature-list__title"><?=htmlspecialcharsbx($arResult['SECTION_NAME'])?></h2>
	<?php endif; ?>

	<?php if (empty($arResult['ITEMS'])): ?>
		<div class="vendor-feature-list__empty"><?=htmlspecialcharsbx(GetMessage('VENDOR_FEATURE_EMPTY'))?></div>
	<?php else: ?>
		<ul class="vendor-feature-list__items">
			<?php foreach ($arResult['ITEMS'] as $item): ?>
				<li class="vendor-feature-list__item">
					<a href="<?=htmlspecialcharsbx($item['DETAIL_PAGE_URL'])?>">
						<?=htmlspecialcharsbx($item['NAME'])?>
					</a>
				</li>
			<?php endforeach; ?>
		</ul>
		<div class="vendor-feature-list__nav">
			<?=$arResult['NAV_STRING']?>
		</div>
	<?php endif; ?>
</div>
```

## Why This Pattern

- Pagination is cache-safe: current page is part of cache key.
- Tag cache is bound to `iblock_id_<ID>` and invalidates on iblock content updates.
- `SetResultCacheKeys(['SECTION_NAME', 'NAV_STRING'])` exposes values for `component_epilog.php` if needed.
- Data and presentation remain separated: query logic in class, rendering in template.
