#!/usr/bin/env python3
"""Scaffold QA gate package (report, backlog, static audit, prompt)."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate QA gate files for Bitrix module verification "
            "(A-I checklist, static-first then dynamic flow)."
        )
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for QA gate files.",
    )
    parser.add_argument(
        "--module-id",
        required=True,
        help="Module ID (example: vendor.module).",
    )
    parser.add_argument(
        "--module-path",
        default=None,
        help=(
            "Path for static audit commands. "
            "Default: local/modules/<module-id>"
        ),
    )
    parser.add_argument(
        "--version",
        default="TBD",
        help="Version under test. Default: TBD",
    )
    parser.add_argument(
        "--environment",
        default="local",
        help="Environment label. Default: local",
    )
    parser.add_argument(
        "--test-levels",
        default="Smoke / Functional / Regression",
        help="Test levels string for report header.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser.parse_args()


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def patch_qa_report(
    content: str,
    module_id: str,
    version: str,
    environment: str,
    test_levels: str,
) -> str:
    content = content.replace("- Module ID:", f"- Module ID: {module_id}")
    content = content.replace("- Version under test:", f"- Version under test: {version}")
    content = content.replace("- Environment:", f"- Environment: {environment}")
    content = content.replace(
        "- Test level(s): Smoke / Functional / Regression / Load",
        f"- Test level(s): {test_levels}",
    )
    content = content.replace("- Date: YYYY-MM-DD", f"- Date: {date.today().isoformat()}")
    return content


def build_backlog(module_id: str) -> str:
    generated = date.today().isoformat()
    return f"""# QA Fix Backlog

## Header

- Module ID: {module_id}
- Generated: {generated}
- Sorting policy: High -> Medium -> Low

## High

| ID | Area (A-I) | Issue | Evidence | File/Location | Proposed fix (what/where/how) | Owner | ETA | Status |
|---|---|---|---|---|---|---|---|---|
| H-001 |  |  |  |  |  |  |  | Open |

## Medium

| ID | Area (A-I) | Issue | Evidence | File/Location | Proposed fix (what/where/how) | Owner | ETA | Status |
|---|---|---|---|---|---|---|---|---|
| M-001 |  |  |  |  |  |  |  | Open |

## Low

| ID | Area (A-I) | Issue | Evidence | File/Location | Proposed fix (what/where/how) | Owner | ETA | Status |
|---|---|---|---|---|---|---|---|---|
| L-001 |  |  |  |  |  |  |  | Open |

## Re-Test Checklist

- [ ] Re-run static audit commands.
- [ ] Re-run failed dynamic scenarios.
- [ ] Update QA report statuses from FAIL to PASS where fixed.
- [ ] Keep evidence links/log references for each closed item.
"""


def build_dynamic_checklist() -> str:
    return """# QA Dynamic Checklist (A-I)

Use after static audit is complete.

## Status Legend

- PASS: verified and acceptable
- FAIL: reproduced issue with evidence
- N-A: not applicable with reason

## A) Install / Uninstall / Update

- [ ] Fresh install
- [ ] Uninstall
- [ ] Reinstall
- [ ] Update from previous version

## B) Code Quality Follow-Up in Runtime

- [ ] Localized messages render correctly
- [ ] No debug output in UI/API responses

## C) Core E2E Scenarios (5-10)

- [ ] Scenario 1
- [ ] Scenario 2
- [ ] Scenario 3
- [ ] Scenario 4
- [ ] Scenario 5

## D) Performance / Scale

- [ ] List/filter behavior on large dataset
- [ ] Long operation behavior with progress

## E) UX on Large Data

- [ ] Pagination/filter/sort usability
- [ ] Mass actions predictability

## F) Security

- [ ] Rights enforcement
- [ ] CSRF/session protection
- [ ] Path traversal resilience

## G) Reliability

- [ ] Parallel actions safety
- [ ] Idempotent retries

## H) Diagnostics

- [ ] Actionable error logs
- [ ] No silent failures

## I) Compatibility

- [ ] PHP 8+ behavior
- [ ] MySQL 8+ behavior
- [ ] Platform boundaries (Site/Box/Cloud REST)
"""


def build_static_audit_script(module_id: str, module_path: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

TARGET="{module_path}"

echo "[QA-STATIC] Module: {module_id}"
echo "[QA-STATIC] Target path: $TARGET"

if [ ! -d "$TARGET" ]; then
  echo "[QA-STATIC] ERROR: target path does not exist: $TARGET"
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "[QA-STATIC] ERROR: rg is required."
  exit 1
fi

echo
echo "=== B) Code quality checks ==="
rg -n "var_dump|print_r\\(|die\\(|dd\\(" "$TARGET" || true
rg -n "Loc::getMessage|GetMessage\\(" "$TARGET" || true
rg -n "[^A-Z_]\\b(300|500|86400)\\b" "$TARGET" || true
rg -n "TODO|FIXME|@todo" "$TARGET" || true

echo
echo "=== F) Security checks ==="
rg -n "check_bitrix_sessid|bitrix_sessid_post|bitrix_sessid_get" "$TARGET" || true
rg -n "AuthForm|GetGroupRight|IsAdmin|isAdmin|HighloadBlockRightsTable" "$TARGET" || true
rg -n "\\.\\./|DOCUMENT_ROOT.*\\$_(GET|POST|REQUEST)" "$TARGET" || true
rg -n "chmod\\(|unlink\\(|fopen\\(|file_put_contents\\(" "$TARGET" || true

echo
echo "=== G/H) Reliability and diagnostics checks ==="
rg -n "CAgent::AddAgent|CAgent::RemoveModuleAgents|lock|mutex|retry|idempot" "$TARGET" || true
rg -n "AddMessage2Log|\\\Bitrix\\\\Main\\\\Diag|->addError\\(|CAdminMessage::ShowMessage|ShowError\\(" "$TARGET" || true

echo
echo "=== I) Compatibility checks ==="
rg -n "PHP_VERSION|version_compare|mysql|utf8mb4|Loader::includeModule" "$TARGET" || true

echo
echo "=== Optional PHP syntax check ==="
if command -v php >/dev/null 2>&1; then
  find "$TARGET" -type f -name "*.php" -print0 | xargs -0 -n1 php -l >/dev/null
  echo "[QA-STATIC] php -l passed."
else
  echo "[QA-STATIC] php not found; skipped php -l."
fi

echo "[QA-STATIC] Completed."
"""


def write_file(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    references_dir = script_dir.parent / "references"
    output_dir = Path(args.out).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    module_path = args.module_path or f"local/modules/{args.module_id}"

    qa_report_tpl = load_template(references_dir / "template-qa-report.md")
    qa_prompt_tpl = load_template(references_dir / "template-qa-audit-prompt.md")

    qa_report = patch_qa_report(
        content=qa_report_tpl,
        module_id=args.module_id,
        version=args.version,
        environment=args.environment,
        test_levels=args.test_levels,
    )
    qa_prompt = qa_prompt_tpl.replace("<module_id>", args.module_id)
    qa_backlog = build_backlog(module_id=args.module_id)
    qa_dynamic = build_dynamic_checklist()
    qa_static_sh = build_static_audit_script(
        module_id=args.module_id,
        module_path=module_path,
    )

    files = {
        output_dir / "qa-report.md": qa_report,
        output_dir / "qa-audit-prompt.md": qa_prompt,
        output_dir / "qa-fix-backlog.md": qa_backlog,
        output_dir / "qa-dynamic-checklist.md": qa_dynamic,
        output_dir / "qa-static-audit.sh": qa_static_sh,
    }

    created = 0
    skipped = 0
    for path, content in files.items():
        if write_file(path, content, overwrite=args.overwrite):
            created += 1
            print(f"created: {path}")
            if path.name.endswith(".sh"):
                path.chmod(0o755)
        else:
            skipped += 1
            print(f"skipped: {path} (exists)")

    print(f"done: created={created}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
