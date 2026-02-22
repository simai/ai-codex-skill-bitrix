# Root-Level Test Toolkit (Static + Integration)

Use this reference when preparing project-level test infrastructure.

Important boundary:

- Testing tools must be placed in project root.
- Do not place test framework files inside module folders.

## Target Structure

```text
<project-root>/
  composer.json
  phpunit.xml.dist
  tests/
    bootstrap.php
    StaticAuditTest.php
    BitrixIntegrationTest.php   # if Bitrix
    README.md
    QA_CHECKLIST.md
```

## Required Behaviors

### 1) Static tests

Must verify:

- dangerous practices (`exec`, `shell_exec`, SSL verify off)
- short open tags (`<?` non-`<?php`)
- debug leftovers where applicable

### 2) Bitrix integration tests (if Bitrix)

Must skip when:

- `BITRIX_ROOT` is not set
- target module is not installed
- `socialservices` module is not installed

### 3) Root docs

Root `README.md` must include:

- project/testing description
- test structure
- how to run static/integration suites
- links to testing docs in `tests/`

`tests/README.md` must include:

- how to set `BITRIX_ROOT`
- module installation requirement
- run examples for CLI/manual/IDE

### 4) Root `.gitignore` hygiene

Must include:

- `vendor/`
- `.phpunit.result.cache`
- `.idea/`
- `.vscode/`
- `*.log`
- `/bitrix/cache/`
- `/bitrix/managed_cache/`
- `/bitrix/stack_cache/`
- `/bitrix/logs/`

## Automation Tool

Use:

```bash
python3 skills/bitrix/scripts/scaffold_root_tests.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module"
```

This generates/updates root testing files without polluting module directories.

Unified run with one QA report:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --bitrix-root "/absolute/path/to/site"
```

Output report path (default):

- `<project-root>/tests/qa-run-report-YYYYMMDD-HHMMSS.md`
- report contains auto `A-I` summary and `Fix Backlog (Risk Sorted)` sections.

Supporting materials:

- troubleshooting: `references/troubleshooting.md`
- large-data seeds: `examples/seeds/README.md`
- CI template with artifact upload: `examples/ci/github-actions-bitrix-qa.yml`
