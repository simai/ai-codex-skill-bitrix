#!/usr/bin/env php
<?php
declare(strict_types=1);

use Bitrix\Main\Loader;

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "This script must be run from CLI.\n");
    exit(1);
}

function env_int(string $name, int $default): int
{
    $value = getenv($name);
    if ($value === false || $value === '') {
        return $default;
    }
    return (int)$value;
}

$bitrixRoot = (string)(getenv('BITRIX_ROOT') ?: '');
$iblockId = env_int('IBLOCK_ID', 0);
$sectionId = env_int('IBLOCK_SECTION_ID', 0);
$seedCount = env_int('SEED_COUNT', 50000);
$seedChunk = max(1, env_int('SEED_CHUNK', 1000));
$seedStart = max(1, env_int('SEED_START_FROM', 1));

if ($bitrixRoot === '' || !is_dir($bitrixRoot . '/bitrix')) {
    fwrite(STDERR, "BITRIX_ROOT is invalid or not set.\n");
    exit(2);
}
if ($iblockId <= 0) {
    fwrite(STDERR, "IBLOCK_ID must be > 0.\n");
    exit(3);
}

$_SERVER['DOCUMENT_ROOT'] = rtrim($bitrixRoot, '/');

if (!defined('NO_KEEP_STATISTIC')) { define('NO_KEEP_STATISTIC', true); }
if (!defined('NOT_CHECK_PERMISSIONS')) { define('NOT_CHECK_PERMISSIONS', true); }
if (!defined('BX_NO_ACCELERATOR_RESET')) { define('BX_NO_ACCELERATOR_RESET', true); }

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php';

if (!Loader::includeModule('iblock')) {
    fwrite(STDERR, "Module iblock is not installed.\n");
    exit(4);
}

$element = new CIBlockElement();
$created = 0;
$failed = 0;
$startTs = microtime(true);

for ($i = 0; $i < $seedCount; $i++) {
    $n = $seedStart + $i;

    $fields = [
        'IBLOCK_ID' => $iblockId,
        'IBLOCK_SECTION_ID' => $sectionId > 0 ? $sectionId : false,
        'NAME' => sprintf('Employee %06d', $n),
        'CODE' => sprintf('employee-%06d', $n),
        'XML_ID' => sprintf('EMP-%06d', $n),
        'ACTIVE' => ($n % 10 === 0) ? 'N' : 'Y',
        'SORT' => ($n % 1000) + 10,
        'CREATED_BY' => 1,
        'MODIFIED_BY' => 1,
    ];

    $id = $element->Add($fields, false, false, false);
    if ($id === false) {
        $failed++;
        $error = $element->LAST_ERROR ?: 'unknown error';
        fwrite(STDERR, sprintf("[ERROR] row=%d: %s\n", $n, $error));
    } else {
        $created++;
    }

    if ((($i + 1) % $seedChunk) === 0) {
        $elapsed = microtime(true) - $startTs;
        fwrite(STDOUT, sprintf("[PROGRESS] inserted=%d failed=%d elapsed=%.1fs\n", $created, $failed, $elapsed));
    }
}

$elapsed = microtime(true) - $startTs;
fwrite(STDOUT, sprintf("[DONE] created=%d failed=%d elapsed=%.1fs\n", $created, $failed, $elapsed));
exit($failed > 0 ? 5 : 0);
