# Example: Existing Project Fix (Feature/Bug)

Use when applying a minimal change in an existing module or component and preserving compatibility.

## Input profile

- Platform: Site Management or Bitrix24 box
- Task: fix/dorabotka
- Project state: existing
- Runtime: PHP 8+, MySQL 8+

## Recommended flow

1. Identify minimal change surface and update scope.
2. Apply patch only in touched paths.
3. Prepare QA gate package (optional but recommended):

```bash
python3 skills/bitrix/scripts/scaffold_qa_gate.py \
  --out "/path/to/project/qa/fix-2026-02-22" \
  --module-id "vendor.module" \
  --module-path "local/modules/vendor.module" \
  --environment "stage"
```

4. Run root QA (static first, integration second):

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/project" \
  --module-id "vendor.module" \
  --bitrix-root "/absolute/path/to/site"
```

## Expected deliverables

- Focused patch list
- Regression checks for touched flows
- One QA report with FAIL evidence and risk-sorted fix backlog
