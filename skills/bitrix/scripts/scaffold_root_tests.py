#!/usr/bin/env python3
"""Scaffold root-level static and integration testing toolkit for Bitrix projects."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


README_MARKER_START = "<!-- codex:testing:start -->"
README_MARKER_END = "<!-- codex:testing:end -->"
MODULE_ID_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")

GITIGNORE_ENTRIES = [
    "vendor/",
    ".phpunit.result.cache",
    ".idea/",
    ".vscode/",
    "*.log",
    "/bitrix/cache/",
    "/bitrix/managed_cache/",
    "/bitrix/stack_cache/",
    "/bitrix/logs/",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate root-level test toolkit: PHPUnit config, static audit test, "
            "Bitrix integration test, docs, and hygiene files."
        )
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to project root.",
    )
    parser.add_argument(
        "--module-id",
        required=True,
        help="Bitrix module ID (example: vendor.module).",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Project name for README/composer metadata. Default: folder name.",
    )
    parser.add_argument(
        "--force-bitrix",
        action="store_true",
        help="Generate BitrixIntegrationTest.php even if /bitrix is not found in project root.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files that already exist.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not MODULE_ID_RE.match(args.module_id):
        raise ValueError(
            "Invalid --module-id. Expected vendor.code with lowercase letters, numbers or underscore."
        )


def write_file(path: Path, content: str, overwrite: bool) -> str:
    existed_before = path.exists()
    if existed_before and not overwrite:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "updated" if existed_before else "created"


def create_or_update_composer(path: Path, project_name: str) -> str:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid composer.json: {exc}") from exc
        status = "updated"
    else:
        data = {
            "name": f"local/{project_name.lower().replace(' ', '-')}",
            "description": f"{project_name} test toolkit",
            "type": "project",
            "require": {},
            "require-dev": {},
            "scripts": {},
        }
        status = "created"

    require_dev = data.setdefault("require-dev", {})
    scripts = data.setdefault("scripts", {})

    require_dev.setdefault("phpunit/phpunit", "^10.5 || ^11.0")
    scripts.setdefault("test", "vendor/bin/phpunit -c phpunit.xml.dist")
    scripts.setdefault("test:static", "vendor/bin/phpunit -c phpunit.xml.dist --testsuite static")
    scripts.setdefault("test:integration", "vendor/bin/phpunit -c phpunit.xml.dist --testsuite integration")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status


def update_gitignore(path: Path) -> str:
    existed_before = path.exists()
    existing = []
    if existed_before:
        existing = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]

    changed = False
    for entry in GITIGNORE_ENTRIES:
        if entry not in existing:
            existing.append(entry)
            changed = True

    if not existed_before or changed:
        path.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")
        return "updated" if existed_before else "created"
    return "skipped"


def upsert_readme(path: Path, project_name: str, module_id: str) -> str:
    section = build_readme_testing_section(module_id)
    if not path.exists():
        content = build_new_root_readme(project_name, module_id, section)
        path.write_text(content, encoding="utf-8")
        return "created"

    current = path.read_text(encoding="utf-8")
    if README_MARKER_START in current and README_MARKER_END in current:
        prefix = current.split(README_MARKER_START, 1)[0]
        suffix = current.split(README_MARKER_END, 1)[1]
        updated = prefix.rstrip() + "\n\n" + section + "\n" + suffix.lstrip()
    else:
        updated = current.rstrip() + "\n\n" + section + "\n"

    if updated == current:
        return "skipped"

    path.write_text(updated, encoding="utf-8")
    return "updated"


def build_readme_testing_section(module_id: str) -> str:
    return f"""<!-- codex:testing:start -->
## Testing

Root-level testing toolkit is stored outside module folder.

### Structure

- `tests/bootstrap.php`
- `tests/StaticAuditTest.php`
- `tests/BitrixIntegrationTest.php` (Bitrix projects)
- `phpunit.xml.dist`

### Run tests

```bash
composer install
vendor/bin/phpunit -c phpunit.xml.dist
```

Integration mode:

```bash
BITRIX_ROOT=/absolute/path/to/site \
BITRIX_MODULE_ID={module_id} \
BITRIX_REQUIRED_MODULES="iblock,highloadblock" \
vendor/bin/phpunit -c phpunit.xml.dist --testsuite integration
```

### Testing docs

- [Tests Guide](tests/README.md)
- [QA Checklist](tests/QA_CHECKLIST.md)
<!-- codex:testing:end -->"""


def build_new_root_readme(project_name: str, module_id: str, testing_section: str) -> str:
    return f"""# {project_name}

## Description

Project with root-level automated test toolkit for static and integration verification.

## Structure

- `tests/` - PHPUnit tests and docs
- `phpunit.xml.dist` - PHPUnit configuration
- `composer.json` - dev dependencies and test scripts

{testing_section}
"""


def build_phpunit_xml(has_bitrix: bool) -> str:
    integration_block = ""
    if has_bitrix:
        integration_block = """
        <testsuite name="integration">
            <file>tests/BitrixIntegrationTest.php</file>
        </testsuite>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<phpunit
    bootstrap="tests/bootstrap.php"
    colors="true"
    cacheResultFile=".phpunit.result.cache"
    failOnWarning="false"
>
    <testsuites>
        <testsuite name="static">
            <file>tests/StaticAuditTest.php</file>
        </testsuite>{integration_block}
    </testsuites>

    <php>
        <ini name="display_errors" value="1"/>
        <ini name="error_reporting" value="-1"/>
    </php>
</phpunit>
"""


def build_bootstrap() -> str:
    return """<?php
declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '1');

$autoload = dirname(__DIR__) . '/vendor/autoload.php';
if (is_file($autoload))
{
    require_once $autoload;
}
"""


def build_static_audit_test() -> str:
    return """<?php
declare(strict_types=1);

use PHPUnit\\Framework\\TestCase;

final class StaticAuditTest extends TestCase
{
    private string $projectRoot;
    private array $excludedPrefixes = [
        'vendor/',
        'bitrix/cache/',
        'bitrix/managed_cache/',
        'bitrix/stack_cache/',
        'bitrix/logs/',
    ];

    protected function setUp(): void
    {
        $this->projectRoot = realpath(dirname(__DIR__)) ?: dirname(__DIR__);
    }

    public function testNoDangerousPractices(): void
    {
        $patterns = [
            '/\\bexec\\s*\\(/i' => 'exec() is forbidden',
            '/\\bshell_exec\\s*\\(/i' => 'shell_exec() is forbidden',
            '/\\bsystem\\s*\\(/i' => 'system() is forbidden',
            '/\\bpassthru\\s*\\(/i' => 'passthru() is forbidden',
            '/\\bproc_open\\s*\\(/i' => 'proc_open() is forbidden',
            '/\\bpopen\\s*\\(/i' => 'popen() is forbidden',
            '/CURLOPT_SSL_VERIFYPEER\\s*=>\\s*false/i' => 'SSL verification must not be disabled',
            '/CURLOPT_SSL_VERIFYHOST\\s*=>\\s*0/i' => 'SSL host verification must not be disabled',
        ];

        $hits = [];
        foreach ($this->phpFiles() as $file)
        {
            $lines = file($file, FILE_IGNORE_NEW_LINES) ?: [];
            foreach ($lines as $index => $line)
            {
                foreach ($patterns as $pattern => $message)
                {
                    if (preg_match($pattern, $line))
                    {
                        $hits[] = sprintf('%s:%d: %s', $this->relative($file), $index + 1, $message);
                    }
                }
            }
        }

        $this->assertSame([], $hits, "Dangerous practices found:\\n" . implode("\\n", $hits));
    }

    public function testNoShortOpenTags(): void
    {
        $hits = [];
        $pattern = '/<\\?(?!php|xml)/i';

        foreach ($this->phpFiles() as $file)
        {
            $lines = file($file, FILE_IGNORE_NEW_LINES) ?: [];
            foreach ($lines as $index => $line)
            {
                if (preg_match($pattern, $line))
                {
                    $hits[] = sprintf('%s:%d: short open tag found', $this->relative($file), $index + 1);
                }
            }
        }

        $this->assertSame([], $hits, "Short open tags found:\\n" . implode("\\n", $hits));
    }

    private function phpFiles(): \\Generator
    {
        $it = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($this->projectRoot, FilesystemIterator::SKIP_DOTS)
        );

        foreach ($it as $fileInfo)
        {
            if (!$fileInfo instanceof SplFileInfo || !$fileInfo->isFile())
            {
                continue;
            }

            $fullPath = $fileInfo->getPathname();
            if (strtolower(pathinfo($fullPath, PATHINFO_EXTENSION)) !== 'php')
            {
                continue;
            }

            $relative = $this->relative($fullPath);
            if ($this->isExcluded($relative))
            {
                continue;
            }

            yield $fullPath;
        }
    }

    private function isExcluded(string $relativePath): bool
    {
        $normalized = str_replace('\\\\', '/', ltrim($relativePath, '/'));
        foreach ($this->excludedPrefixes as $prefix)
        {
            if (str_starts_with($normalized, $prefix))
            {
                return true;
            }
        }
        return false;
    }

    private function relative(string $path): string
    {
        $base = rtrim(str_replace('\\\\', '/', $this->projectRoot), '/');
        $full = str_replace('\\\\', '/', $path);
        if (str_starts_with($full, $base . '/'))
        {
            return substr($full, strlen($base) + 1);
        }
        return $full;
    }
}
"""


def build_bitrix_integration_test(module_id: str) -> str:
    return f"""<?php
declare(strict_types=1);

use PHPUnit\\Framework\\TestCase;

final class BitrixIntegrationTest extends TestCase
{{
    private static string $bitrixRoot = '';
    private static string $moduleId = '{module_id}';
    private static array $requiredModules = [];

    public static function setUpBeforeClass(): void
    {{
        self::$bitrixRoot = (string)getenv('BITRIX_ROOT');
        $moduleFromEnv = (string)getenv('BITRIX_MODULE_ID');
        if ($moduleFromEnv !== '')
        {{
            self::$moduleId = $moduleFromEnv;
        }}
        $requiredModulesFromEnv = (string)getenv('BITRIX_REQUIRED_MODULES');
        if ($requiredModulesFromEnv !== '')
        {{
            $required = array_map('trim', explode(',', $requiredModulesFromEnv));
            $required = array_values(array_unique(array_filter($required, static fn(string $value): bool => $value !== '')));
            self::$requiredModules = $required;
        }}

        if (self::$bitrixRoot === '')
        {{
            self::markTestSkipped('BITRIX_ROOT is not set.');
        }}

        if (!is_dir(self::$bitrixRoot . '/bitrix'))
        {{
            self::markTestSkipped('BITRIX_ROOT does not point to valid Bitrix project.');
        }}

        $_SERVER['DOCUMENT_ROOT'] = self::$bitrixRoot;
        if (!defined('NO_KEEP_STATISTIC')) {{ define('NO_KEEP_STATISTIC', true); }}
        if (!defined('NOT_CHECK_PERMISSIONS')) {{ define('NOT_CHECK_PERMISSIONS', true); }}
        if (!defined('BX_NO_ACCELERATOR_RESET')) {{ define('BX_NO_ACCELERATOR_RESET', true); }}

        require_once self::$bitrixRoot . '/bitrix/modules/main/include/prolog_before.php';

        if (!\\Bitrix\\Main\\Loader::includeModule(self::$moduleId))
        {{
            self::markTestSkipped('Module is not installed: ' . self::$moduleId);
        }}

        foreach (self::$requiredModules as $requiredModule)
        {{
            if (!\\Bitrix\\Main\\Loader::includeModule($requiredModule))
            {{
                self::markTestSkipped('Required module is not installed: ' . $requiredModule);
            }}
        }}
    }}

    public function testBitrixKernelLoaded(): void
    {{
        $this->assertTrue(class_exists(\\Bitrix\\Main\\Application::class));
    }}

    public function testTargetModuleLoaded(): void
    {{
        $this->assertTrue(\\Bitrix\\Main\\Loader::includeModule(self::$moduleId));
    }}

    public function testRequiredModulesLoadedOrNotConfigured(): void
    {{
        if (empty(self::$requiredModules))
        {{
            $this->addToAssertionCount(1);
            $this->assertTrue(true);
            return;
        }}

        foreach (self::$requiredModules as $requiredModule)
        {{
            $this->assertTrue(
                \\Bitrix\\Main\\Loader::includeModule($requiredModule),
                'Required module is not loaded: ' . $requiredModule
            );
        }}
    }}
}}
"""


def build_tests_readme(module_id: str, has_bitrix: bool) -> str:
    integration_block = ""
    if has_bitrix:
        integration_block = f"""
## Bitrix Integration Tests

Environment variables:

- `BITRIX_ROOT` — absolute path to site document root.
- `BITRIX_MODULE_ID` — module ID under test (default: `{module_id}`).
- `BITRIX_REQUIRED_MODULES` — optional comma-separated module IDs required by your project.

Skip rules:

- tests are skipped if `BITRIX_ROOT` is missing
- tests are skipped if module is not installed
- tests are skipped if any module from `BITRIX_REQUIRED_MODULES` is not installed

Run integration suite:

```bash
BITRIX_ROOT=/absolute/path/to/site \\
BITRIX_MODULE_ID={module_id} \\
BITRIX_REQUIRED_MODULES="iblock,highloadblock" \\
vendor/bin/phpunit -c phpunit.xml.dist --testsuite integration
```
"""

    return f"""# Tests Guide

This test toolkit is root-level and does not place test code into module folder.

## Structure

- `tests/bootstrap.php`
- `tests/StaticAuditTest.php`
{"- `tests/BitrixIntegrationTest.php`" if has_bitrix else "- `tests/BitrixIntegrationTest.php` (not generated: Bitrix not detected)"}
- `phpunit.xml.dist`

## Requirements

- PHP 8+
- Composer installed
- `composer install` completed

## Static Tests

Run:

```bash
vendor/bin/phpunit -c phpunit.xml.dist --testsuite static
```

This suite checks:

- dangerous practices (`exec`, disabled SSL verification, etc.)
- short open tags (`<?`)

## Console and Manual Run

Console:

```bash
vendor/bin/phpunit -c phpunit.xml.dist
```

Manual (IDE):

1. Set working directory to project root.
2. Load `phpunit.xml.dist`.
3. Run static or integration suite.
{integration_block}
## Module Installation Requirement

For integration checks the module must be installed in target Bitrix environment.
"""


def build_qa_checklist() -> str:
    return """# QA Checklist (A-I)

For each section mark status: PASS / FAIL / N-A and attach evidence.

## A) Install / Uninstall / Update
- [ ] Fresh install
- [ ] Uninstall
- [ ] Reinstall
- [ ] Update path

## B) Code Quality
- [ ] Localization
- [ ] No magic-number risks
- [ ] No debug leftovers

## C) Core E2E (5-10)
- [ ] Scenarios listed and verified

## D) Performance
- [ ] Large data behavior
- [ ] Slow query risks

## E) UX on large data
- [ ] List/filter/pagination usability

## F) Security
- [ ] Rights
- [ ] CSRF/session checks
- [ ] Path traversal safety

## G) Reliability
- [ ] Locks/concurrency
- [ ] Resume/retry/idempotency

## H) Diagnostics
- [ ] Actionable logging
- [ ] No silent failures

## I) Compatibility
- [ ] PHP/MySQL baseline
- [ ] Platform compatibility
"""


def main() -> int:
    args = parse_args()
    validate_args(args)
    project_root = Path(args.project_root).resolve()
    project_name = args.project_name or project_root.name
    has_bitrix = args.force_bitrix or (project_root / "bitrix").exists()

    files: Dict[Path, str] = {
        project_root / "phpunit.xml.dist": build_phpunit_xml(has_bitrix),
        project_root / "tests" / "bootstrap.php": build_bootstrap(),
        project_root / "tests" / "StaticAuditTest.php": build_static_audit_test(),
        project_root / "tests" / "README.md": build_tests_readme(args.module_id, has_bitrix),
        project_root / "tests" / "QA_CHECKLIST.md": build_qa_checklist(),
    }

    if has_bitrix:
        files[project_root / "tests" / "BitrixIntegrationTest.php"] = build_bitrix_integration_test(
            args.module_id
        )

    summary: List[str] = []
    for path, content in files.items():
        status = write_file(path, content, overwrite=args.overwrite)
        summary.append(f"{status}: {path}")

    composer_status = create_or_update_composer(project_root / "composer.json", project_name)
    summary.append(f"{composer_status}: {project_root / 'composer.json'}")

    gitignore_status = update_gitignore(project_root / ".gitignore")
    summary.append(f"{gitignore_status}: {project_root / '.gitignore'}")

    readme_status = upsert_readme(project_root / "README.md", project_name, args.module_id)
    summary.append(f"{readme_status}: {project_root / 'README.md'}")

    for line in summary:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
