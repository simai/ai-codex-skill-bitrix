# Example Pack: REST Domain Artifacts

This folder contains filled examples for domain delivery artifacts:

- `crm.md`
- `tasks.md`
- `user.md`
- `disk.md`

Use them as reference output when preparing integration documentation and QA handoff.

## How to generate blank templates

Generate all domain templates:

```bash
python3 skills/bitrix/scripts/scaffold_artifacts.py \
  --out "skills/bitrix/examples/rest-domain-artifacts/_generated" \
  --preset rest_all \
  --overwrite
```

Generate one domain template:

```bash
python3 skills/bitrix/scripts/scaffold_artifacts.py \
  --out "skills/bitrix/examples/rest-domain-artifacts/_generated-crm" \
  --preset rest_crm \
  --overwrite
```

## Recommended usage

1. Pick the nearest domain example.
2. Copy structure into your project artifact folder.
3. Replace sample values with project-specific portal/method/evidence.
4. Run QA gate using `references/qa-gate-checklist.md`.

