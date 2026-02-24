# CI Example (GitHub Actions)

Use this template in target Bitrix repositories:

1. Copy `github-actions-bitrix-qa.yml` to `.github/workflows/bitrix-qa.yml`.
2. Set workflow inputs (`module_id`, `project_root`, `bitrix_root`).
3. Start manual run (`workflow_dispatch`) or rely on pull request triggers.

The workflow publishes QA markdown report as artifact.

REST artifact generation template:

1. Copy `github-actions-bitrix-rest-artifacts.yml` to `.github/workflows/bitrix-rest-artifacts.yml`.
2. Pick preset: `rest_all`, `rest_crm`, `rest_tasks`, `rest_user`, or `rest_disk`.
3. Run `workflow_dispatch` and download generated markdown artifacts from workflow artifacts.

Combined REST + QA template:

1. Copy `github-actions-bitrix-rest-qa.yml` to `.github/workflows/bitrix-rest-qa.yml`.
2. Configure inputs for both QA (`module_id`, `project_root`, `bitrix_root`) and REST (`rest_preset`, `rest_output_dir`).
3. Run `workflow_dispatch` to generate REST artifact pack and QA report in one pipeline.
