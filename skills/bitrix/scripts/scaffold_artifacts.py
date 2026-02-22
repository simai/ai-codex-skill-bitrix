#!/usr/bin/env python3
"""Generate Bitrix release/testing artifacts from skill templates."""

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
}

PRESETS = {
    "update": ["migration", "rollback", "upgrade", "changelog", "regression"],
    "release": ["release", "changelog", "regression"],
    "marketplace": ["release", "changelog", "regression", "moderator_precheck"],
    "qa": ["qa", "regression"],
    "full": list(TEMPLATE_MAP.keys()),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold Bitrix artifacts from skill templates."
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
