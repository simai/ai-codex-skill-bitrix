# CI Example (GitHub Actions)

Use this template in target Bitrix repositories:

1. Copy `github-actions-bitrix-qa.yml` to `.github/workflows/bitrix-qa.yml`.
2. Set workflow inputs (`module_id`, `project_root`, `bitrix_root`).
3. Start manual run (`workflow_dispatch`) or rely on pull request triggers.

The workflow publishes QA markdown report as artifact.
