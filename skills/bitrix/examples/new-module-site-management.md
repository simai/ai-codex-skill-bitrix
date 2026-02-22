# Example: New Module (1C-Bitrix Site Management)

Use when starting a new module with admin UI, data layer, and root QA toolkit.

## Input profile

- Platform: Site Management
- Task: module
- Project state: new
- Runtime: PHP 8+, MySQL 8+
- Module ID: `vendor.module`
- Entity code: `employee`

## Recommended flow

1. Scaffold admin skeleton:

```bash
python3 skills/bitrix/scripts/scaffold_module_admin.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --entity "employee" \
  --namespace "Vendor\\Module"
```

2. Scaffold IBlock/HL repositories and services:

```bash
python3 skills/bitrix/scripts/scaffold_data_layer.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --entity "employee" \
  --storage both \
  --iblock-id 10 \
  --hl-id 12 \
  --namespace "Vendor\\Module"
```

3. Add root test toolkit:

```bash
python3 skills/bitrix/scripts/scaffold_root_tests.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module"
```

4. Run unified QA and generate one report:

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --bitrix-root "/absolute/path/to/site"
```

## Expected deliverables

- Module skeleton (`local/modules/vendor.module/*`)
- Root QA toolkit (`tests/*`, `phpunit.xml.dist`, `composer.json`)
- QA report with A-I summary + risk backlog (`tests/qa-run-report-*.md`)
