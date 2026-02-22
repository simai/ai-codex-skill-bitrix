#!/usr/bin/env php
<?php
declare(strict_types=1);

use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Loader;
use Bitrix\Main\UserFieldTable;

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
$hlblockId = env_int('HLBLOCK_ID', 0);
$seedCount = env_int('SEED_COUNT', 50000);
$seedChunk = max(1, env_int('SEED_CHUNK', 1000));
$seedStart = max(1, env_int('SEED_START_FROM', 1));

$titleField = (string)(getenv('HL_TITLE_FIELD') ?: 'UF_NAME');
$codeField = (string)(getenv('HL_CODE_FIELD') ?: 'UF_XML_ID');
$activeField = (string)(getenv('HL_ACTIVE_FIELD') ?: 'UF_ACTIVE');
$sortField = (string)(getenv('HL_SORT_FIELD') ?: 'UF_SORT');

if ($bitrixRoot === '' || !is_dir($bitrixRoot . '/bitrix')) {
    fwrite(STDERR, "BITRIX_ROOT is invalid or not set.\n");
    exit(2);
}
if ($hlblockId <= 0) {
    fwrite(STDERR, "HLBLOCK_ID must be > 0.\n");
    exit(3);
}

$_SERVER['DOCUMENT_ROOT'] = rtrim($bitrixRoot, '/');

if (!defined('NO_KEEP_STATISTIC')) { define('NO_KEEP_STATISTIC', true); }
if (!defined('NOT_CHECK_PERMISSIONS')) { define('NOT_CHECK_PERMISSIONS', true); }
if (!defined('BX_NO_ACCELERATOR_RESET')) { define('BX_NO_ACCELERATOR_RESET', true); }

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php';

if (!Loader::includeModule('highloadblock')) {
    fwrite(STDERR, "Module highloadblock is not installed.\n");
    exit(4);
}

$hl = HighloadBlockTable::getById($hlblockId)->fetch();
if (!$hl) {
    fwrite(STDERR, "HL block not found: " . $hlblockId . "\n");
    exit(5);
}

$entity = HighloadBlockTable::compileEntity($hl);
$dataClass = $entity->getDataClass();
$entityId = 'HLBLOCK_' . $hlblockId;

$userFields = UserFieldTable::getList([
    'filter' => ['=ENTITY_ID' => $entityId],
    'select' => ['FIELD_NAME', 'USER_TYPE_ID', 'MANDATORY'],
])->fetchAll();

$fieldMap = [];
foreach ($userFields as $row) {
    $fieldMap[(string)$row['FIELD_NAME']] = [
        'USER_TYPE_ID' => (string)$row['USER_TYPE_ID'],
        'MANDATORY' => (string)$row['MANDATORY'],
    ];
}

$exists = static fn(string $name): bool => isset($fieldMap[$name]);

if (!$exists($titleField)) {
    foreach (['UF_NAME', 'UF_TITLE', 'UF_LABEL'] as $fallbackField) {
        if ($exists($fallbackField)) {
            $titleField = $fallbackField;
            break;
        }
    }
}

if (!$exists($titleField)) {
    fwrite(STDERR, "No suitable title field found. Set HL_TITLE_FIELD to existing UF_* field.\n");
    exit(6);
}

$created = 0;
$failed = 0;
$startTs = microtime(true);

for ($i = 0; $i < $seedCount; $i++) {
    $n = $seedStart + $i;

    $row = [
        $titleField => sprintf('Employee %06d', $n),
    ];

    if ($exists($codeField)) {
        $row[$codeField] = sprintf('EMP-%06d', $n);
    }
    if ($exists($activeField)) {
        $row[$activeField] = ($n % 10 === 0) ? 0 : 1;
    }
    if ($exists($sortField)) {
        $row[$sortField] = ($n % 1000) + 10;
    }

    $result = $dataClass::add($row);
    if (!$result->isSuccess()) {
        $failed++;
        fwrite(
            STDERR,
            sprintf("[ERROR] row=%d: %s\n", $n, implode('; ', $result->getErrorMessages()))
        );
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
exit($failed > 0 ? 7 : 0);
