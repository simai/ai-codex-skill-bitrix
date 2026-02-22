# Bitrix Skill

Codex skill for 1C-Bitrix development:
- module development
- component development
- integrations
- feature work (dorabotka)
- fixes and debugging
- update planning by diff/commits
- release and marketplace preparation
- QA/smoke/regression planning
- Bitrix24 REST app integration (webhook/OAuth/events/scopes) for cloud and box

Platform split:
- 1C-Bitrix Site Management and Bitrix24 box: full scope (modules/components/integrations/updates/QA/release).
- Bitrix24 cloud: REST-app integration scope only (no filesystem module/component development).

Repository layout:
- `skills/bitrix/SKILL.md`
- `skills/bitrix/agents/openai.yaml`
- `skills/bitrix/references/`
- `skills/bitrix/references/template-*.md`
- `skills/bitrix/references/bitrix24-rest-integration.md`
- `skills/bitrix/references/bitrix24-marketplace-publication.md`
- `skills/bitrix/references/qa-gate-checklist.md`
- `skills/bitrix/references/external-knowledge.md`
- `skills/bitrix/scripts/scaffold_artifacts.py`
- `skills/bitrix/scripts/scaffold_module_admin.py`
- `skills/bitrix/scripts/scaffold_data_layer.py`
- `skills/bitrix/scripts/scaffold_qa_gate.py`
- `skills/bitrix/scripts/scaffold_root_tests.py`
- `skills/bitrix/scripts/qa_run.py`
- `skills/bitrix/scripts/search_reference_dump.py`
- `skills/bitrix/references/troubleshooting.md`
- `skills/bitrix/examples/`
- `skills/bitrix/examples/seeds/`
- `skills/bitrix/examples/ci/`
- `.github/workflows/bitrix-qa-example.yml`
- root files: `README.md`, `.gitattributes`, `.git/`

Install target:
- macOS/Linux: `~/.codex/skills/bitrix`
- Windows: `%USERPROFILE%\.codex\skills\bitrix`

## 1) Install (macOS/Linux)

Copy:

```bash
SRC="/path/to/ai-codex-skill-bitrix/skills/bitrix"
DST="$HOME/.codex/skills/bitrix"
mkdir -p "$HOME/.codex/skills"
rm -rf "$DST"
cp -R "$SRC" "$DST"
```

Symlink (recommended for active development):

```bash
SRC="/path/to/ai-codex-skill-bitrix/skills/bitrix"
DST="$HOME/.codex/skills/bitrix"
mkdir -p "$HOME/.codex/skills"
rm -rf "$DST"
ln -s "$SRC" "$DST"
```

## 2) Install (Windows, PowerShell)

Copy:

```powershell
$src = "C:\path\to\ai-codex-skill-bitrix\skills\bitrix"
$dstRoot = "$env:USERPROFILE\.codex\skills"
$dst = "$dstRoot\bitrix"
New-Item -ItemType Directory -Force $dstRoot | Out-Null
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
Copy-Item -Recurse -Force $src $dst
```

Symlink (recommended for active development, may require admin/developer mode):

```powershell
$src = "C:\path\to\ai-codex-skill-bitrix\skills\bitrix"
$dstRoot = "$env:USERPROFILE\.codex\skills"
$dst = "$dstRoot\bitrix"
New-Item -ItemType Directory -Force $dstRoot | Out-Null
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
New-Item -ItemType SymbolicLink -Path $dst -Target $src
```

## 3) Restart Codex

After install or update, restart Codex so skills are reloaded.

## 4) Verify install

Expected files:
- `~/.codex/skills/bitrix/SKILL.md`
- `~/.codex/skills/bitrix/references/`
- `~/.codex/skills/bitrix/agents/openai.yaml`

Quick check:

```bash
ls -la ~/.codex/skills/bitrix
python3 ~/.codex/skills/bitrix/scripts/scaffold_artifacts.py --help
python3 ~/.codex/skills/bitrix/scripts/scaffold_module_admin.py --help
python3 ~/.codex/skills/bitrix/scripts/scaffold_data_layer.py --help
python3 ~/.codex/skills/bitrix/scripts/scaffold_qa_gate.py --help
python3 ~/.codex/skills/bitrix/scripts/scaffold_root_tests.py --help
python3 ~/.codex/skills/bitrix/scripts/qa_run.py --help
python3 ~/.codex/skills/bitrix/scripts/search_reference_dump.py --help
```

Windows:

```powershell
Get-ChildItem "$env:USERPROFILE\.codex\skills\bitrix"
```

## 5) How to use in prompts

Call explicitly:

```text
$bitrix Build new module vendor.module for Site Management on PHP 8+/MySQL 8+
$bitrix Refactor existing component local/components/vendor/catalog.list and keep backward compatibility
$bitrix Implement retry-safe integration with external API for Bitrix24 box
$bitrix Fix production bug in order sync and provide rollback steps
$bitrix Prepare update from commit range <start>..<end> with migration notes and upgrade notes
$bitrix Run QA checklist for module update and produce risk-ranked QA report
$bitrix Build Bitrix24 OAuth integration with least-privilege scopes and safe event handling
$bitrix Implement Bitrix24 cloud app install callback with secure token storage and event safety checks
```

## 6) VS Code / remote environments

- Install skill in the same runtime environment where Codex works (local, WSL, container, remote).
- If your `AGENTS.md` has an allowlist, include `bitrix`.
- Restart Codex session after install/update.

## 7) Optional search in external docs dump

If you have a local Bitrix knowledge dump:

```bash
python3 skills/bitrix/scripts/search_reference_dump.py \
  --root "/path/to/bitrix-dump" \
  --query "batch limit pagination next start oauth webhook" \
  --limit 10
```

## 8) Optional module admin scaffold

```bash
python3 skills/bitrix/scripts/scaffold_module_admin.py \
  --project-root "/path/to/bitrix-project" \
  --module-id "vendor.module" \
  --entity "employee" \
  --namespace "Vendor\\Module"
```

## 9) Optional data-layer scaffold (IBlock/HL)

```bash
python3 skills/bitrix/scripts/scaffold_data_layer.py \
  --project-root "/path/to/bitrix-project" \
  --module-id "vendor.module" \
  --entity "employee" \
  --storage both \
  --iblock-id 10 \
  --hl-id 12 \
  --namespace "Vendor\\Module"
```

## 10) Optional QA gate scaffold (A-I)

```bash
python3 skills/bitrix/scripts/scaffold_qa_gate.py \
  --out "/path/to/reports/qa-2026-02-22" \
  --module-id "vendor.module" \
  --module-path "local/modules/vendor.module" \
  --version "1.2.3" \
  --environment "stage"
```

## 11) Optional root test toolkit scaffold

```bash
python3 skills/bitrix/scripts/scaffold_root_tests.py \
  --project-root "/path/to/bitrix-project" \
  --module-id "vendor.module"
```

## 12) Optional unified QA run (static + integration + one report)

```bash
python3 skills/bitrix/scripts/qa_run.py \
  --project-root "/path/to/bitrix-project" \
  --module-id "vendor.module" \
  --bitrix-root "/absolute/path/to/site"
```

Report output includes:
- A-I summary table (`PASS/FAIL/N-A`, evidence, risk, concrete fix)
- fix backlog sorted by risk (`High`, `Medium`, `Low`)

## 13) CI workflow example (artifact publishing)

Repository includes ready workflow:

- `.github/workflows/bitrix-qa-example.yml`

Template for target Bitrix repositories:

- `skills/bitrix/examples/ci/github-actions-bitrix-qa.yml`

Both variants run `qa_run.py` and upload QA markdown report as artifact.

## 14) Scenario examples

- `skills/bitrix/examples/new-module-site-management.md`
- `skills/bitrix/examples/existing-project-fix.md`
- `skills/bitrix/examples/bitrix24-cloud-rest-app.md`

## 15) Large dataset seeds (UX/perf)

- `skills/bitrix/examples/seeds/mysql_large_list_seed.sql`
- `skills/bitrix/examples/seeds/mysql_large_list_cleanup.sql`
- `skills/bitrix/examples/seeds/seed_iblock_employees.php`
- `skills/bitrix/examples/seeds/seed_hlblock_employees.php`
- `skills/bitrix/examples/seeds/README.md`

Troubleshooting runbook:

- `skills/bitrix/references/troubleshooting.md`
