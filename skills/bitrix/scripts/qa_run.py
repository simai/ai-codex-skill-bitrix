#!/usr/bin/env python3
"""Run Bitrix QA pipeline (static + integration) and build one Markdown report."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_NA = "N-A"

RISK_LOW = "low"
RISK_MED = "med"
RISK_HIGH = "high"


@dataclass
class StepResult:
    name: str
    status: str
    command: str
    exit_code: Optional[int]
    duration_sec: float
    note: str
    stdout: str
    stderr: str


@dataclass
class AreaResult:
    code: str
    title: str
    status: str
    evidence: str
    risk: str
    fix: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run static and integration QA checks for Bitrix projects and generate "
            "single markdown report."
        )
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to target project root.",
    )
    parser.add_argument(
        "--module-id",
        required=True,
        help="Bitrix module ID (example: vendor.module).",
    )
    parser.add_argument(
        "--bitrix-root",
        default=None,
        help=(
            "Bitrix document root for integration suite. "
            "If missing, integration step is marked N-A."
        ),
    )
    parser.add_argument(
        "--report",
        default=None,
        help=(
            "Output markdown report path. "
            "Default: <project-root>/tests/qa-run-report-YYYYMMDD-HHMMSS.md"
        ),
    )
    parser.add_argument(
        "--phpunit-bin",
        default=None,
        help=(
            "Path to phpunit executable. "
            "Default: <project-root>/vendor/bin/phpunit or phpunit from PATH"
        ),
    )
    parser.add_argument(
        "--static-script",
        default=None,
        help=(
            "Path to shell static-audit script. "
            "Default autodiscovery: qa-static-audit.sh or tests/qa-static-audit.sh"
        ),
    )
    parser.add_argument(
        "--skip-static-script",
        action="store_true",
        help="Do not run shell static-audit script even if found.",
    )
    parser.add_argument(
        "--skip-integration",
        action="store_true",
        help="Skip phpunit integration suite.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Per command timeout in seconds. Default: 1200",
    )
    return parser.parse_args()


def resolve_report_path(project_root: Path, report_arg: Optional[str]) -> Path:
    if report_arg:
        return Path(report_arg).expanduser().resolve()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return (project_root / "tests" / f"qa-run-report-{stamp}.md").resolve()


def discover_static_script(project_root: Path, arg_value: Optional[str]) -> Optional[Path]:
    if arg_value:
        raw = Path(arg_value).expanduser()
        return raw.resolve() if raw.is_absolute() else (project_root / raw).resolve()

    candidates = [
        project_root / "qa-static-audit.sh",
        project_root / "tests" / "qa-static-audit.sh",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def discover_phpunit(project_root: Path, arg_value: Optional[str]) -> Optional[str]:
    if arg_value:
        raw = Path(arg_value).expanduser()
        if raw.is_absolute():
            return str(raw.resolve())
        return str((project_root / raw).resolve())

    local_bin = project_root / "vendor" / "bin" / "phpunit"
    if local_bin.exists() and local_bin.is_file():
        return str(local_bin.resolve())

    from_path = shutil.which("phpunit")
    if from_path:
        return from_path

    return None


def render_command(parts: List[str]) -> str:
    return shlex.join(parts)


def trim_output(text: str, max_chars: int = 12000, max_lines: int = 140) -> str:
    stripped = text.strip()
    if not stripped:
        return "(empty)"

    lines = stripped.splitlines()
    if len(lines) > max_lines:
        lines = [f"[... trimmed, total lines: {len(stripped.splitlines())} ...]"] + lines[-max_lines:]
    compact = "\n".join(lines)

    if len(compact) > max_chars:
        compact = "[... trimmed ...]\n" + compact[-max_chars:]

    return compact


def run_command(
    name: str,
    cmd: List[str],
    project_root: Path,
    timeout: int,
    env_additions: Optional[Dict[str, str]] = None,
    note_on_success: str = "",
) -> StepResult:
    env = os.environ.copy()
    if env_additions:
        env.update(env_additions)

    started = datetime.now()
    command_str = render_command(cmd)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration = (datetime.now() - started).total_seconds()
        status = STATUS_PASS if proc.returncode == 0 else STATUS_FAIL
        note = note_on_success if status == STATUS_PASS else "Command returned non-zero exit code."
        return StepResult(
            name=name,
            status=status,
            command=command_str,
            exit_code=proc.returncode,
            duration_sec=duration,
            note=note,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        duration = (datetime.now() - started).total_seconds()
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return StepResult(
            name=name,
            status=STATUS_FAIL,
            command=command_str,
            exit_code=None,
            duration_sec=duration,
            note=f"Command timed out after {timeout}s.",
            stdout=stdout,
            stderr=stderr,
        )


def make_na_step(name: str, note: str) -> StepResult:
    return StepResult(
        name=name,
        status=STATUS_NA,
        command="(not executed)",
        exit_code=None,
        duration_sec=0.0,
        note=note,
        stdout="",
        stderr="",
    )


def detect_skips(stdout: str, stderr: str) -> Optional[int]:
    merged = "\n".join([stdout or "", stderr or ""])
    matches = re.findall(r"(\d+)\s+skipped", merged, flags=re.IGNORECASE)
    if not matches:
        return None
    return sum(int(item) for item in matches)


def clip_text(text: str, limit: int = 180) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "-"
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def md_cell(text: str, limit: int = 220) -> str:
    return clip_text(text, limit=limit).replace("|", "\\|")


def extract_step_evidence(step: Optional[StepResult]) -> str:
    if step is None:
        return "No automated step executed."
    if step.status == STATUS_PASS:
        return f"{step.name}: PASS"
    if step.status == STATUS_NA:
        return clip_text(step.note)

    merged = "\n".join([step.stdout or "", step.stderr or ""])
    lines = [line.strip() for line in merged.splitlines() if line.strip()]
    if not lines:
        return clip_text(step.note or "Step failed without output.")

    patterns = [
        r"forbidden",
        r"failed",
        r"error",
        r"exception",
        r"skipped",
        r"assert",
        r"fatal",
        r"warning",
        r"timeout",
    ]
    for line in lines:
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in patterns):
            return clip_text(f"{step.name}: {line}")
    return clip_text(f"{step.name}: {lines[0]}")


def combine_step_statuses(steps: List[Optional[StepResult]]) -> str:
    statuses = [step.status for step in steps if step is not None and step.status != STATUS_NA]
    if not statuses:
        return STATUS_NA
    if STATUS_FAIL in statuses:
        return STATUS_FAIL
    return STATUS_PASS


def combine_step_evidence(steps: List[Optional[StepResult]]) -> str:
    fail = next((step for step in steps if step is not None and step.status == STATUS_FAIL), None)
    if fail:
        return extract_step_evidence(fail)

    passed = next((step for step in steps if step is not None and step.status == STATUS_PASS), None)
    if passed:
        return extract_step_evidence(passed)

    na = next((step for step in steps if step is not None and step.status == STATUS_NA), None)
    if na:
        return extract_step_evidence(na)

    return "No automated evidence."


def default_fix_for_area(code: str, status: str) -> str:
    if status == STATUS_PASS:
        return "No action required."
    if status == STATUS_NA:
        return "Manual verification required in QA cycle."

    fixes = {
        "A": "Validate install/uninstall/reinstall/update path on stage and confirm module registration + savedata behavior.",
        "B": "Replace debug leftovers, localize UI strings, and move magic numbers to named constants/config.",
        "C": "Fix failing business flow and rerun top 5-10 E2E scenarios with evidence.",
        "D": "Run performance profiling on large dataset and optimize bottlenecks (SQL, cache, batch size).",
        "E": "Improve list/filter/pagination UX and add progress feedback for long actions.",
        "F": "Fix rights checks, CSRF/session checks, and unsafe path handling; rerun static and integration tests.",
        "G": "Add/verify locks, idempotency, and retry-safe behavior for parallel operations.",
        "H": "Add actionable diagnostics and explicit error handling; remove silent failures.",
        "I": "Re-check behavior on PHP 8+/MySQL 8+ and target platform matrix (Site/Box/Cloud REST).",
    }
    return fixes.get(code, "Fix issue and rerun QA checks.")


def risk_for_area(code: str, status: str) -> str:
    if status != STATUS_FAIL:
        return RISK_LOW
    if code in {"A", "F", "G"}:
        return RISK_HIGH
    if code in {"B", "C", "H", "I"}:
        return RISK_MED
    return RISK_LOW


def derive_area_results(results: List[StepResult]) -> List[AreaResult]:
    by_name = {item.name: item for item in results}
    static_shell = by_name.get("Static Shell Audit")
    static_phpunit = by_name.get("PHPUnit Static Suite")
    integration = by_name.get("PHPUnit Integration Suite")

    area_rows: List[AreaResult] = []

    def add_area(code: str, title: str, status: str, evidence: str) -> None:
        area_rows.append(
            AreaResult(
                code=code,
                title=title,
                status=status,
                evidence=evidence,
                risk=risk_for_area(code, status),
                fix=default_fix_for_area(code, status),
            )
        )

    add_area(
        "A",
        "Install/Uninstall/Update",
        integration.status if integration else STATUS_NA,
        extract_step_evidence(integration),
    )
    add_area(
        "B",
        "Code quality (localization, magic numbers, debug)",
        combine_step_statuses([static_phpunit, static_shell]),
        combine_step_evidence([static_phpunit, static_shell]),
    )
    add_area(
        "C",
        "Core E2E scenarios",
        integration.status if integration else STATUS_NA,
        extract_step_evidence(integration),
    )
    add_area(
        "D",
        "Performance and scaling",
        STATUS_NA,
        "No automated benchmark in qa_run.py; requires manual/perf suite execution.",
    )
    add_area(
        "E",
        "UX on large datasets",
        STATUS_NA,
        "No automated UI load checks in qa_run.py; requires manual QA validation.",
    )
    add_area(
        "F",
        "Security (rights, CSRF, path traversal)",
        static_phpunit.status if static_phpunit else STATUS_NA,
        extract_step_evidence(static_phpunit),
    )
    add_area(
        "G",
        "Reliability (locks, resume, parallelism)",
        integration.status if integration else STATUS_NA,
        extract_step_evidence(integration),
    )
    add_area(
        "H",
        "Diagnostics and logs",
        combine_step_statuses([integration, static_shell]),
        combine_step_evidence([integration, static_shell]),
    )
    add_area(
        "I",
        "Compatibility",
        integration.status if integration else STATUS_NA,
        extract_step_evidence(integration),
    )

    return area_rows


def build_backlog(area_rows: List[AreaResult]) -> Dict[str, List[AreaResult]]:
    buckets: Dict[str, List[AreaResult]] = {
        RISK_HIGH: [],
        RISK_MED: [],
        RISK_LOW: [],
    }
    for row in area_rows:
        if row.status != STATUS_FAIL:
            continue
        bucket = row.risk if row.risk in buckets else RISK_MED
        buckets[bucket].append(row)
    return buckets


def build_recommendations(
    results: List[StepResult],
    project_root: Path,
    module_id: str,
) -> List[str]:
    recs: List[str] = []
    by_name = {item.name: item for item in results}

    static_shell = by_name.get("Static Shell Audit")
    if static_shell and static_shell.status == STATUS_NA:
        recs.append(
            "Optional static shell audit was not found. Generate QA gate files: "
            "`python3 skills/bitrix/scripts/scaffold_qa_gate.py --out ./qa --module-id "
            f"{module_id}`."
        )

    static_phpunit = by_name.get("PHPUnit Static Suite")
    if static_phpunit and static_phpunit.status == STATUS_NA:
        if "phpunit executable not found" in static_phpunit.note:
            recs.append(
                "Install dev dependencies before rerun: `composer install` in project root."
            )
        elif "phpunit.xml.dist not found" in static_phpunit.note:
            recs.append(
                "Static PHPUnit suite is not available. Scaffold root tests: "
                "`python3 skills/bitrix/scripts/scaffold_root_tests.py --project-root "
                f"\"{project_root}\" --module-id \"{module_id}\"`."
            )
        else:
            recs.append("Static PHPUnit suite was not executed. Check prerequisites and rerun.")
    elif static_phpunit and static_phpunit.status == STATUS_FAIL:
        recs.append(
            "Fix static audit findings and rerun `vendor/bin/phpunit -c phpunit.xml.dist --testsuite static`."
        )

    integration = by_name.get("PHPUnit Integration Suite")
    if integration and integration.status == STATUS_NA:
        recs.append(
            "Integration suite was skipped. Set `BITRIX_ROOT` and ensure module + socialservices are installed."
        )
    elif integration and integration.status == STATUS_FAIL:
        recs.append(
            "Fix integration/runtime issues and rerun `vendor/bin/phpunit -c phpunit.xml.dist --testsuite integration`."
        )

    if not recs:
        recs.append("No blocking findings. Keep this report with release artifacts.")

    return recs


def compute_overall(results: List[StepResult]) -> str:
    statuses = [item.status for item in results]
    if any(status == STATUS_FAIL for status in statuses):
        return STATUS_FAIL
    if all(status == STATUS_NA for status in statuses):
        return STATUS_NA
    return STATUS_PASS


def build_report(
    results: List[StepResult],
    report_path: Path,
    project_root: Path,
    module_id: str,
    bitrix_root: Optional[str],
) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overall = compute_overall(results)

    static_names = {"Static Shell Audit", "PHPUnit Static Suite"}
    static_indexes = [idx for idx, item in enumerate(results) if item.name in static_names and item.status != STATUS_NA]
    integration_indexes = [idx for idx, item in enumerate(results) if item.name == "PHPUnit Integration Suite" and item.status != STATUS_NA]
    if not integration_indexes:
        flow_label = "N-A"
    elif not static_indexes:
        flow_label = "No"
    else:
        flow_label = "Yes" if max(static_indexes) < min(integration_indexes) else "No"

    lines: List[str] = []
    lines.append("# QA Run Report")
    lines.append("")
    lines.append("## Header")
    lines.append("")
    lines.append(f"- Generated: {generated}")
    lines.append(f"- Project root: `{project_root}`")
    lines.append(f"- Module ID: `{module_id}`")
    lines.append(f"- Bitrix root: `{bitrix_root or 'not provided'}`")
    lines.append(f"- Report file: `{report_path}`")
    lines.append(f"- Overall status: **{overall}**")
    lines.append("")
    lines.append("## Flow")
    lines.append("")
    lines.append(f"- Static before integration: {flow_label}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Step | Status | Exit code | Duration (s) | Command |")
    lines.append("|---|---|---:|---:|---|")
    for item in results:
        exit_code = "-" if item.exit_code is None else str(item.exit_code)
        lines.append(
            f"| {item.name} | {item.status} | {exit_code} | {item.duration_sec:.2f} | `{item.command}` |"
        )

    area_rows = derive_area_results(results)
    backlog = build_backlog(area_rows)

    lines.append("")
    lines.append("## A-I Summary (Auto)")
    lines.append("")
    lines.append("| Area | Status | Evidence | Risk | Concrete fix |")
    lines.append("|---|---|---|---|---|")
    for row in area_rows:
        area_label = f"{row.code}. {row.title}"
        lines.append(
            f"| {md_cell(area_label, limit=90)} | {row.status} | {md_cell(row.evidence)} | "
            f"{row.risk} | {md_cell(row.fix)} |"
        )

    lines.append("")
    lines.append("## Fix Backlog (Risk Sorted)")
    lines.append("")
    for risk, label, prefix in [
        (RISK_HIGH, "High", "H"),
        (RISK_MED, "Medium", "M"),
        (RISK_LOW, "Low", "L"),
    ]:
        lines.append(f"### {label}")
        lines.append("")
        bucket = backlog[risk]
        if not bucket:
            lines.append("- No items.")
            lines.append("")
            continue

        lines.append("| ID | Area | Issue | Evidence | Fix |")
        lines.append("|---|---|---|---|---|")
        for idx, row in enumerate(bucket, start=1):
            issue = f"{row.code} failed"
            lines.append(
                f"| {prefix}-{idx:03d} | {row.code}. {md_cell(row.title, limit=80)} | {md_cell(issue, limit=90)} | "
                f"{md_cell(row.evidence)} | {md_cell(row.fix)} |"
            )
        lines.append("")

    recommendations = build_recommendations(results, project_root, module_id)
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for rec in recommendations:
        lines.append(f"- {rec}")

    lines.append("")
    lines.append("## Details")
    lines.append("")
    for item in results:
        lines.append(f"### {item.name}")
        lines.append("")
        lines.append(f"- Status: {item.status}")
        lines.append(f"- Note: {item.note or '-'}")
        lines.append(f"- Command: `{item.command}`")
        lines.append("")
        lines.append("stdout:")
        lines.append("```text")
        lines.append(trim_output(item.stdout))
        lines.append("```")
        lines.append("")
        lines.append("stderr:")
        lines.append("```text")
        lines.append(trim_output(item.stderr))
        lines.append("```")
        lines.append("")

        if item.name == "PHPUnit Integration Suite":
            skipped = detect_skips(item.stdout, item.stderr)
            if skipped is not None:
                lines.append(f"- Skipped tests detected: {skipped}")
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise SystemExit(f"Project root does not exist: {project_root}")

    report_path = resolve_report_path(project_root, args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    bitrix_root = args.bitrix_root or os.getenv("BITRIX_ROOT")
    static_script = discover_static_script(project_root, args.static_script)

    phpunit_bin = discover_phpunit(project_root, args.phpunit_bin)
    phpunit_config = project_root / "phpunit.xml.dist"

    results: List[StepResult] = []

    if args.skip_static_script:
        results.append(make_na_step("Static Shell Audit", "Skipped by --skip-static-script."))
    elif static_script is None:
        results.append(
            make_na_step(
                "Static Shell Audit",
                "No static shell script found (qa-static-audit.sh).",
            )
        )
    else:
        results.append(
            run_command(
                name="Static Shell Audit",
                cmd=["bash", str(static_script)],
                project_root=project_root,
                timeout=args.timeout,
                note_on_success="Static shell audit completed.",
            )
        )

    if not phpunit_config.exists():
        results.append(
            make_na_step(
                "PHPUnit Static Suite",
                "phpunit.xml.dist not found in project root.",
            )
        )
    elif phpunit_bin is None:
        results.append(
            make_na_step(
                "PHPUnit Static Suite",
                "phpunit executable not found. Run composer install or set --phpunit-bin.",
            )
        )
    else:
        results.append(
            run_command(
                name="PHPUnit Static Suite",
                cmd=[phpunit_bin, "-c", "phpunit.xml.dist", "--testsuite", "static"],
                project_root=project_root,
                timeout=args.timeout,
                note_on_success="Static PHPUnit suite completed.",
            )
        )

    if args.skip_integration:
        results.append(make_na_step("PHPUnit Integration Suite", "Skipped by --skip-integration."))
    elif not phpunit_config.exists():
        results.append(
            make_na_step(
                "PHPUnit Integration Suite",
                "phpunit.xml.dist not found in project root.",
            )
        )
    elif phpunit_bin is None:
        results.append(
            make_na_step(
                "PHPUnit Integration Suite",
                "phpunit executable not found. Run composer install or set --phpunit-bin.",
            )
        )
    elif not bitrix_root:
        results.append(
            make_na_step(
                "PHPUnit Integration Suite",
                "BITRIX_ROOT is not set (use --bitrix-root or environment variable).",
            )
        )
    else:
        integration_result = run_command(
            name="PHPUnit Integration Suite",
            cmd=[phpunit_bin, "-c", "phpunit.xml.dist", "--testsuite", "integration"],
            project_root=project_root,
            timeout=args.timeout,
            env_additions={
                "BITRIX_ROOT": bitrix_root,
                "BITRIX_MODULE_ID": args.module_id,
            },
            note_on_success="Integration PHPUnit suite completed.",
        )
        skipped = detect_skips(integration_result.stdout, integration_result.stderr)
        if integration_result.status == STATUS_PASS and skipped:
            integration_result.status = STATUS_NA
            integration_result.note = (
                f"Integration suite contains skipped tests ({skipped}); treated as N-A."
            )
        results.append(integration_result)

    report = build_report(
        results=results,
        report_path=report_path,
        project_root=project_root,
        module_id=args.module_id,
        bitrix_root=bitrix_root,
    )
    report_path.write_text(report, encoding="utf-8")

    overall = compute_overall(results)
    print(f"Report: {report_path}")
    for item in results:
        code = "-" if item.exit_code is None else str(item.exit_code)
        print(f"{item.status}: {item.name} (exit={code})")
    print(f"Overall: {overall}")

    return 1 if overall == STATUS_FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
