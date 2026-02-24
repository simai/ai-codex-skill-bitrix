#!/usr/bin/env python3
"""Generate Bitrix release/testing/REST artifacts from skill templates."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


TEMPLATE_MAP = {
    "migration": ("template-migration-notes.md", "migration-notes.md"),
    "rollback": ("template-migration-rollback-notes.md", "migration-rollback-notes.md"),
    "upgrade": ("template-upgrade-notes.md", "upgrade-notes.md"),
    "release": ("template-release-notes.md", "release-notes.md"),
    "changelog": ("template-changelog-fragment.md", "changelog-fragment.md"),
    "regression": ("template-regression-checklist.md", "regression-checklist.md"),
    "qa": ("template-qa-report.md", "qa-report.md"),
    "moderator_precheck": ("template-moderator-precheck.md", "moderator-precheck.md"),
    "rest_crm_pack": (
        "template-rest-domain-crm-artifact-pack.md",
        "rest-domain-crm-artifact-pack.md",
    ),
    "rest_tasks_pack": (
        "template-rest-domain-tasks-artifact-pack.md",
        "rest-domain-tasks-artifact-pack.md",
    ),
    "rest_user_pack": (
        "template-rest-domain-user-artifact-pack.md",
        "rest-domain-user-artifact-pack.md",
    ),
    "rest_disk_pack": (
        "template-rest-domain-disk-artifact-pack.md",
        "rest-domain-disk-artifact-pack.md",
    ),
}

PRESETS = {
    "update": ["migration", "rollback", "upgrade", "changelog", "regression"],
    "release": ["release", "changelog", "regression"],
    "marketplace": ["release", "changelog", "regression", "moderator_precheck"],
    "qa": ["qa", "regression"],
    "rest_crm": ["rest_crm_pack"],
    "rest_tasks": ["rest_tasks_pack"],
    "rest_user": ["rest_user_pack"],
    "rest_disk": ["rest_disk_pack"],
    "rest_all": [
        "rest_crm_pack",
        "rest_tasks_pack",
        "rest_user_pack",
        "rest_disk_pack",
    ],
    "full": list(TEMPLATE_MAP.keys()),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold Bitrix artifacts (release/update/qa/rest-domain) from skill templates."
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for generated files.",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        default="full",
        help="Artifact group to generate. Default: full",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    references_dir = script_dir.parent / "references"
    output_dir = Path(args.out).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for artifact in PRESETS[args.preset]:
        template_name, output_name = TEMPLATE_MAP[artifact]
        src = references_dir / template_name
        dst = output_dir / output_name

        if not src.exists():
            raise FileNotFoundError(f"Template not found: {src}")

        if dst.exists() and not args.overwrite:
            continue

        shutil.copyfile(src, dst)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
