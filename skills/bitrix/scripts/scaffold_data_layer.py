#!/usr/bin/env python3
"""Scaffold Bitrix data layer classes (IBlock/HL repository + service)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable


MODULE_ID_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
ENTITY_RE = re.compile(r"^[a-z0-9_]+$")
STORAGE_CHOICES = ("iblock", "hlblock", "both")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate data-layer classes for Bitrix module: "
            "IBlock and/or HL repository/service pairs."
        )
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to project root containing /local/modules.",
    )
    parser.add_argument(
        "--module-id",
        required=True,
        help="Bitrix module ID in form vendor.code (example: vendor.module).",
    )
    parser.add_argument(
        "--entity",
        required=True,
        help="Entity code in snake_case (example: employee).",
    )
    parser.add_argument(
        "--namespace",
        default="Vendor\\Module",
        help="Namespace root for generated classes. Default: Vendor\\Module",
    )
    parser.add_argument(
        "--storage",
        choices=STORAGE_CHOICES,
        default="both",
        help="Which layer to scaffold: iblock, hlblock or both. Default: both.",
    )
    parser.add_argument(
        "--iblock-id",
        type=int,
        default=1,
        help="Default IBlock ID constructor example value. Default: 1",
    )
    parser.add_argument(
        "--hl-id",
        type=int,
        default=1,
        help="Default HL ID constructor example value. Default: 1",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not MODULE_ID_RE.match(args.module_id):
        raise ValueError(
            "Invalid --module-id. Expected vendor.code with lowercase letters, numbers or underscore."
        )
    if not ENTITY_RE.match(args.entity):
        raise ValueError(
            "Invalid --entity. Use snake_case: lowercase letters, numbers, underscore."
        )
    if not args.namespace.strip("\\"):
        raise ValueError("Invalid --namespace.")
    if args.iblock_id <= 0:
        raise ValueError("--iblock-id must be > 0.")
    if args.hl_id <= 0:
        raise ValueError("--hl-id must be > 0.")


def pascal_case(value: str) -> str:
    parts = [chunk for chunk in re.split(r"[_\-\.\s]+", value) if chunk]
    return "".join(part[:1].upper() + part[1:] for part in parts)


def fill(template: str, replacements: Dict[str, str]) -> str:
    for key, value in replacements.items():
        template = template.replace(f"__{key}__", value)
    return template


def iblock_repository_template() -> str:
    return """<?php

namespace __NAMESPACE__\\Iblock;

use Bitrix\\Main\\Error;
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Result;

class __ENTITY_PASCAL__Repository
{
\tprivate int $iblockId;

\tpublic function __construct(int $iblockId = __IBLOCK_ID__)
\t{
\t\tif (!Loader::includeModule('iblock'))
\t\t{
\t\t\tthrow new \\RuntimeException('Module iblock is not available.');
\t\t}

\t\t$this->iblockId = $iblockId;
\t}

\tpublic function list(
\t\tarray $filter = [],
\t\tarray $order = ['ID' => 'DESC'],
\t\tint $limit = 50,
\t\tint $offset = 0,
\t\tarray $select = ['ID', 'IBLOCK_ID', 'NAME', 'ACTIVE', 'TIMESTAMP_X']
\t): array
\t{
\t\t$filter['=IBLOCK_ID'] = $this->iblockId;
\t\t$nav = ['nTopCount' => $limit];
\t\tif ($offset > 0)
\t\t{
\t\t\t$nav = ['nPageSize' => $limit, 'iNumPage' => (int)floor($offset / max($limit, 1)) + 1];
\t\t}

\t\t$result = [];
\t\t$res = \\CIBlockElement::GetList($order, $filter, false, $nav, $select);
\t\twhile ($row = $res->Fetch())
\t\t{
\t\t\t$result[] = $row;
\t\t}

\t\treturn $result;
\t}

\tpublic function getById(int $id, array $select = ['ID', 'IBLOCK_ID', 'NAME', 'ACTIVE', 'TIMESTAMP_X']): ?array
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn null;
\t\t}

\t\t$res = \\CIBlockElement::GetList([], ['=ID' => $id, '=IBLOCK_ID' => $this->iblockId], false, ['nTopCount' => 1], $select);
\t\t$row = $res->Fetch();
\t\treturn is_array($row) ? $row : null;
\t}

\tpublic function add(array $fields): Result
\t{
\t\ttry
\t\t{
\t\t\t$fields['IBLOCK_ID'] = $this->iblockId;
\t\t\t$el = new \\CIBlockElement();
\t\t\t$id = (int)$el->Add($fields);
\t\t\tif ($id <= 0)
\t\t\t{
\t\t\t\treturn $this->fail($el->LAST_ERROR ?: 'Unable to add iblock element.', 'IBLOCK_ADD_FAILED');
\t\t\t}

\t\t\t$result = new Result();
\t\t\t$result->setData(['ID' => $id]);
\t\t\treturn $result;
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'Iblock add failed');
\t\t}
\t}

\tpublic function update(int $id, array $fields): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid element ID.', 'INVALID_ID');
\t\t}

\t\ttry
\t\t{
\t\t\t$el = new \\CIBlockElement();
\t\t\t$ok = $el->Update($id, $fields);
\t\t\tif (!$ok)
\t\t\t{
\t\t\t\treturn $this->fail($el->LAST_ERROR ?: 'Unable to update iblock element.', 'IBLOCK_UPDATE_FAILED');
\t\t\t}

\t\t\treturn new Result();
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'Iblock update failed');
\t\t}
\t}

\tpublic function delete(int $id): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid element ID.', 'INVALID_ID');
\t\t}

\t\ttry
\t\t{
\t\t\t$ok = \\CIBlockElement::Delete($id);
\t\t\tif (!$ok)
\t\t\t{
\t\t\t\treturn $this->fail('Unable to delete iblock element.', 'IBLOCK_DELETE_FAILED');
\t\t\t}

\t\t\treturn new Result();
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'Iblock delete failed');
\t\t}
\t}

\tprivate function fail(string $message, string $code): Result
\t{
\t\t$result = new Result();
\t\t$result->addError(new Error($message, $code));
\t\treturn $result;
\t}

\tprivate function failThrowable(\\Throwable $e, string $context): Result
\t{
\t\treturn $this->fail($context . ': ' . $e->getMessage(), 'EXCEPTION');
\t}
}
"""


def iblock_service_template() -> str:
    return """<?php

namespace __NAMESPACE__\\Iblock;

use Bitrix\\Main\\Error;
use Bitrix\\Main\\Result;

class __ENTITY_PASCAL__Service
{
\tpublic function __construct(
\t\tprivate readonly __ENTITY_PASCAL__Repository $repository
\t)
\t{
\t}

\tpublic function create(array $payload): Result
\t{
\t\t$validation = $this->validateCreate($payload);
\t\tif (!$validation->isSuccess())
\t\t{
\t\t\treturn $validation;
\t\t}

\t\treturn $this->repository->add($this->mapPayloadToFields($payload));
\t}

\tpublic function update(int $id, array $payload): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid element ID.', 'INVALID_ID');
\t\t}

\t\t$validation = $this->validateUpdate($payload);
\t\tif (!$validation->isSuccess())
\t\t{
\t\t\treturn $validation;
\t\t}

\t\treturn $this->repository->update($id, $this->mapPayloadToFields($payload));
\t}

\tpublic function delete(int $id): Result
\t{
\t\treturn $this->repository->delete($id);
\t}

\tpublic function get(int $id): ?array
\t{
\t\treturn $this->repository->getById($id);
\t}

\tpublic function list(array $filter = [], array $order = ['ID' => 'DESC'], int $limit = 50, int $offset = 0): array
\t{
\t\treturn $this->repository->list($filter, $order, $limit, $offset);
\t}

\tprivate function validateCreate(array $payload): Result
\t{
\t\t$result = new Result();
\t\t$name = trim((string)($payload['NAME'] ?? ''));
\t\tif ($name === '')
\t\t{
\t\t\t$result->addError(new Error('Field NAME is required.', 'NAME_REQUIRED'));
\t\t}
\t\treturn $result;
\t}

\tprivate function validateUpdate(array $payload): Result
\t{
\t\t$result = new Result();
\t\tif (array_key_exists('NAME', $payload) && trim((string)$payload['NAME']) === '')
\t\t{
\t\t\t$result->addError(new Error('Field NAME cannot be empty.', 'NAME_EMPTY'));
\t\t}
\t\treturn $result;
\t}

\tprivate function mapPayloadToFields(array $payload): array
\t{
\t\t$fields = [];
\t\tif (array_key_exists('NAME', $payload))
\t\t{
\t\t\t$fields['NAME'] = trim((string)$payload['NAME']);
\t\t}
\t\tif (array_key_exists('ACTIVE', $payload))
\t\t{
\t\t\t$fields['ACTIVE'] = ($payload['ACTIVE'] === 'N' ? 'N' : 'Y');
\t\t}
\t\tif (array_key_exists('SORT', $payload))
\t\t{
\t\t\t$fields['SORT'] = (int)$payload['SORT'];
\t\t}
\t\tif (array_key_exists('PREVIEW_TEXT', $payload))
\t\t{
\t\t\t$fields['PREVIEW_TEXT'] = (string)$payload['PREVIEW_TEXT'];
\t\t}
\t\tif (array_key_exists('PROPERTY_VALUES', $payload) && is_array($payload['PROPERTY_VALUES']))
\t\t{
\t\t\t$fields['PROPERTY_VALUES'] = $payload['PROPERTY_VALUES'];
\t\t}
\t\treturn $fields;
\t}

\tprivate function fail(string $message, string $code): Result
\t{
\t\t$result = new Result();
\t\t$result->addError(new Error($message, $code));
\t\treturn $result;
\t}
}
"""


def hl_repository_template() -> str:
    return """<?php

namespace __NAMESPACE__\\Hl;

use Bitrix\\Highloadblock\\HighloadBlockTable;
use Bitrix\\Main\\Error;
use Bitrix\\Main\\Loader;
use Bitrix\\Main\\Result;

class __ENTITY_PASCAL__Repository
{
\tprivate int $hlId;
\tprivate string $dataClass;

\tpublic function __construct(int $hlId = __HL_ID__)
\t{
\t\tif (!Loader::includeModule('highloadblock'))
\t\t{
\t\t\tthrow new \\RuntimeException('Module highloadblock is not available.');
\t\t}

\t\t$this->hlId = $hlId;
\t\t$this->dataClass = $this->resolveDataClass($hlId);
\t}

\tpublic function list(
\t\tarray $filter = [],
\t\tarray $order = ['ID' => 'DESC'],
\t\tint $limit = 50,
\t\tint $offset = 0,
\t\tarray $select = ['*']
\t): array
\t{
\t\ttry
\t\t{
\t\t\t$dataClass = $this->dataClass;
\t\t\t$res = $dataClass::getList([
\t\t\t\t'filter' => $filter,
\t\t\t\t'order' => $order,
\t\t\t\t'limit' => $limit,
\t\t\t\t'offset' => $offset,
\t\t\t\t'select' => $select,
\t\t\t]);
\t\t\treturn $res->fetchAll();
\t\t}
\t\tcatch (\\Throwable)
\t\t{
\t\t\treturn [];
\t\t}
\t}

\tpublic function getById(int $id): ?array
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn null;
\t\t}

\t\ttry
\t\t{
\t\t\t$dataClass = $this->dataClass;
\t\t\t$row = $dataClass::getById($id)->fetch();
\t\t\treturn is_array($row) ? $row : null;
\t\t}
\t\tcatch (\\Throwable)
\t\t{
\t\t\treturn null;
\t\t}
\t}

\tpublic function add(array $fields): Result
\t{
\t\ttry
\t\t{
\t\t\t$dataClass = $this->dataClass;
\t\t\t$addResult = $dataClass::add($fields);
\t\t\tif (!$addResult->isSuccess())
\t\t\t{
\t\t\t\treturn $this->fail(implode('; ', $addResult->getErrorMessages()), 'HL_ADD_FAILED');
\t\t\t}

\t\t\t$result = new Result();
\t\t\t$result->setData(['ID' => (int)$addResult->getId()]);
\t\t\treturn $result;
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'HL add failed');
\t\t}
\t}

\tpublic function update(int $id, array $fields): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid row ID.', 'INVALID_ID');
\t\t}

\t\ttry
\t\t{
\t\t\t$dataClass = $this->dataClass;
\t\t\t$updateResult = $dataClass::update($id, $fields);
\t\t\tif (!$updateResult->isSuccess())
\t\t\t{
\t\t\t\treturn $this->fail(implode('; ', $updateResult->getErrorMessages()), 'HL_UPDATE_FAILED');
\t\t\t}

\t\t\treturn new Result();
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'HL update failed');
\t\t}
\t}

\tpublic function delete(int $id): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid row ID.', 'INVALID_ID');
\t\t}

\t\ttry
\t\t{
\t\t\t$dataClass = $this->dataClass;
\t\t\t$deleteResult = $dataClass::delete($id);
\t\t\tif (!$deleteResult->isSuccess())
\t\t\t{
\t\t\t\treturn $this->fail(implode('; ', $deleteResult->getErrorMessages()), 'HL_DELETE_FAILED');
\t\t\t}

\t\t\treturn new Result();
\t\t}
\t\tcatch (\\Throwable $e)
\t\t{
\t\t\treturn $this->failThrowable($e, 'HL delete failed');
\t\t}
\t}

\tprivate function resolveDataClass(int $hlId): string
\t{
\t\t$hl = HighloadBlockTable::getById($hlId)->fetch();
\t\tif (!$hl)
\t\t{
\t\t\tthrow new \\RuntimeException('Highloadblock not found: ' . $hlId);
\t\t}

\t\t$entity = HighloadBlockTable::compileEntity($hl);
\t\treturn $entity->getDataClass();
\t}

\tprivate function fail(string $message, string $code): Result
\t{
\t\t$result = new Result();
\t\t$result->addError(new Error($message, $code));
\t\treturn $result;
\t}

\tprivate function failThrowable(\\Throwable $e, string $context): Result
\t{
\t\treturn $this->fail($context . ': ' . $e->getMessage(), 'EXCEPTION');
\t}
}
"""


def hl_service_template() -> str:
    return """<?php

namespace __NAMESPACE__\\Hl;

use Bitrix\\Main\\Error;
use Bitrix\\Main\\Result;

class __ENTITY_PASCAL__Service
{
\tpublic function __construct(
\t\tprivate readonly __ENTITY_PASCAL__Repository $repository
\t)
\t{
\t}

\tpublic function create(array $payload): Result
\t{
\t\t$validation = $this->validateCreate($payload);
\t\tif (!$validation->isSuccess())
\t\t{
\t\t\treturn $validation;
\t\t}

\t\treturn $this->repository->add($this->mapPayloadToFields($payload));
\t}

\tpublic function update(int $id, array $payload): Result
\t{
\t\tif ($id <= 0)
\t\t{
\t\t\treturn $this->fail('Invalid row ID.', 'INVALID_ID');
\t\t}

\t\t$validation = $this->validateUpdate($payload);
\t\tif (!$validation->isSuccess())
\t\t{
\t\t\treturn $validation;
\t\t}

\t\treturn $this->repository->update($id, $this->mapPayloadToFields($payload));
\t}

\tpublic function delete(int $id): Result
\t{
\t\treturn $this->repository->delete($id);
\t}

\tpublic function get(int $id): ?array
\t{
\t\treturn $this->repository->getById($id);
\t}

\tpublic function list(array $filter = [], array $order = ['ID' => 'DESC'], int $limit = 50, int $offset = 0): array
\t{
\t\treturn $this->repository->list($filter, $order, $limit, $offset);
\t}

\tprivate function validateCreate(array $payload): Result
\t{
\t\t$result = new Result();
\t\t$name = trim((string)($payload['UF_NAME'] ?? ''));
\t\tif ($name === '')
\t\t{
\t\t\t$result->addError(new Error('Field UF_NAME is required.', 'UF_NAME_REQUIRED'));
\t\t}
\t\treturn $result;
\t}

\tprivate function validateUpdate(array $payload): Result
\t{
\t\t$result = new Result();
\t\tif (array_key_exists('UF_NAME', $payload) && trim((string)$payload['UF_NAME']) === '')
\t\t{
\t\t\t$result->addError(new Error('Field UF_NAME cannot be empty.', 'UF_NAME_EMPTY'));
\t\t}
\t\treturn $result;
\t}

\tprivate function mapPayloadToFields(array $payload): array
\t{
\t\t$fields = [];
\t\tif (array_key_exists('UF_NAME', $payload))
\t\t{
\t\t\t$fields['UF_NAME'] = trim((string)$payload['UF_NAME']);
\t\t}
\t\tif (array_key_exists('UF_ACTIVE', $payload))
\t\t{
\t\t\t$fields['UF_ACTIVE'] = ($payload['UF_ACTIVE'] === 'N' ? 'N' : 'Y');
\t\t}
\t\tif (array_key_exists('UF_SORT', $payload))
\t\t{
\t\t\t$fields['UF_SORT'] = (int)$payload['UF_SORT'];
\t\t}
\t\tif (array_key_exists('UF_NOTE', $payload))
\t\t{
\t\t\t$fields['UF_NOTE'] = (string)$payload['UF_NOTE'];
\t\t}
\t\treturn $fields;
\t}

\tprivate function fail(string $message, string $code): Result
\t{
\t\t$result = new Result();
\t\t$result->addError(new Error($message, $code));
\t\treturn $result;
\t}
}
"""


def write_file(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def targets_for_storage(storage: str) -> Iterable[str]:
    if storage == "both":
        return ("iblock", "hlblock")
    return (storage,)


def main() -> int:
    args = parse_args()
    validate_args(args)

    project_root = Path(args.project_root).resolve()
    module_root = project_root / "local" / "modules" / args.module_id
    entity_pascal = pascal_case(args.entity)
    namespace = args.namespace.strip("\\")

    replacements = {
        "NAMESPACE": namespace,
        "ENTITY_PASCAL": entity_pascal,
        "IBLOCK_ID": str(args.iblock_id),
        "HL_ID": str(args.hl_id),
    }

    files: Dict[Path, str] = {}
    for storage in targets_for_storage(args.storage):
        if storage == "iblock":
            files[module_root / "lib" / "Iblock" / f"{entity_pascal}Repository.php"] = fill(
                iblock_repository_template(), replacements
            )
            files[module_root / "lib" / "Iblock" / f"{entity_pascal}Service.php"] = fill(
                iblock_service_template(), replacements
            )
        elif storage == "hlblock":
            files[module_root / "lib" / "Hl" / f"{entity_pascal}Repository.php"] = fill(
                hl_repository_template(), replacements
            )
            files[module_root / "lib" / "Hl" / f"{entity_pascal}Service.php"] = fill(
                hl_service_template(), replacements
            )

    created = 0
    skipped = 0
    for path, content in files.items():
        if write_file(path, content, overwrite=args.overwrite):
            created += 1
            print(f"created: {path}")
        else:
            skipped += 1
            print(f"skipped: {path} (exists)")

    print(f"done: created={created}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
