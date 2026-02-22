# External Knowledge Usage

Use this guide when user provides external Bitrix knowledge dumps (JSON/JSONL/Markdown/PDF exports).

For full box source code drops, also apply `references/bitrix24-box-source-analysis.md`.

## What to Extract

Extract only reusable rules that improve implementation quality:

- API constraints and edge cases.
- Installation/update lifecycle behaviors.
- Security and permissions requirements.
- Performance and operational guardrails.

Ignore:

- Vendor-specific legal/commercial policy text unless task explicitly targets that area.
- Duplicated high-level descriptions with no implementation impact.
- Environment-specific hardcoded paths.
- Minified/generated code dumps that do not define actionable integration rules.

## Integration Policy

- Keep `SKILL.md` concise; store extracted details in dedicated references.
- Prefer rule summaries over long copied text.
- Mark uncertain or version-sensitive rules as assumptions when source is incomplete.
- Do not hardcode personal/local absolute paths in skill instructions.

## Optional Local Search

For large knowledge dumps, use:

- `scripts/search_reference_dump.py --root <path> --query "<terms>"`

This script scans `.json`, `.jsonl`, `.md`, and `.txt` files and prints ranked matches with snippets.

When dump contains both docs and code/module exports:

- Prefer searching targeted subfolders first (for example API/helpdesk/market docs).
- De-prioritize module archives dominated by minified JS/base64 payloads.
