#!/usr/bin/env python3
"""Print manual installation guidance for template-to-slide.

This project intentionally avoids automatic installation. The script is kept as
an informational compatibility entrypoint only; it never installs software,
npm packages, browsers, or companion Skills.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MANUAL_COMMANDS = [
    "npm install",
    "npx playwright install chromium",
]

PNPM_COMMANDS = [
    "pnpm install",
    "pnpm exec playwright install chromium",
]


NOTES = [
    "Install Python 3.10+, Node.js 20+, and npm or pnpm manually.",
    "Install project npm dependencies manually from package.json.",
    "Install Playwright Chromium manually if browser-driven export is needed.",
    "Install frontend-slides and dom-to-pptx companion Skills manually through the ChatGPT/Codex skill flow.",
    "Run scripts/check_dependencies.py after installation to verify the environment.",
]


def build_report(cwd: Path) -> dict[str, object]:
    return {
        "cwd": str(cwd),
        "installed": False,
        "automatic_installation_supported": False,
        "manual_install_docs": "INSTALL.md",
        "npm_commands": MANUAL_COMMANDS,
        "pnpm_commands": PNPM_COMMANDS,
        "verify_command": "python3 scripts/check_dependencies.py --cwd . --strict --json",
        "notes": NOTES,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print manual setup guidance; does not install anything")
    parser.add_argument("--cwd", default=".", help="Project directory")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = build_report(Path(args.cwd).resolve())

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print("Automatic installation is not supported.")
    print(f"Project: {report['cwd']}")
    print("Manual npm setup:")
    for command in MANUAL_COMMANDS:
        print(f"  {command}")
    print("Manual pnpm setup:")
    for command in PNPM_COMMANDS:
        print(f"  {command}")
    print(f"Verify: {report['verify_command']}")
    print("See INSTALL.md for details.")
    for note in NOTES:
        print(f"Note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
