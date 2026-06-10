#!/usr/bin/env python3
"""Install project-local npm runtime dependencies after explicit approval.

This script does not install ChatGPT Skills. It only installs npm runtime
packages used by the export path. Companion Skills must be installed through
ChatGPT's skill installation flow or the relevant local skill manager.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNTIME_PACKAGES = ["dom-to-pptx", "pptxgenjs", "playwright"]


def run(cmd: list[str], cwd: Path, check: bool = False) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}")
    return proc.returncode, proc.stdout.strip()


def choose_package_manager(cwd: Path, explicit: str | None = None) -> str:
    if explicit:
        if not shutil.which(explicit):
            raise RuntimeError(f"Package manager not found: {explicit}")
        return explicit
    if (cwd / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
        return "pnpm"
    if shutil.which("npm"):
        return "npm"
    if shutil.which("pnpm"):
        return "pnpm"
    raise RuntimeError("Neither npm nor pnpm is available")


def ensure_package_json(cwd: Path) -> None:
    package_json = cwd / "package.json"
    if package_json.exists():
        return
    package_json.write_text(
        json.dumps(
            {
                "name": "template-to-slide-runtime",
                "version": "0.2.0",
                "private": True,
                "type": "module",
                "dependencies": {name: "latest" for name in RUNTIME_PACKAGES},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def install_packages(cwd: Path, manager: str) -> list[dict[str, Any]]:
    ensure_package_json(cwd)
    commands: list[list[str]] = []
    if manager == "pnpm":
        commands.append(["pnpm", "add", *RUNTIME_PACKAGES])
        commands.append(["pnpm", "exec", "playwright", "install", "chromium"])
    else:
        commands.append(["npm", "install", *RUNTIME_PACKAGES])
        commands.append(["npx", "playwright", "install", "chromium"])

    results: list[dict[str, Any]] = []
    for cmd in commands:
        code, out = run(cmd, cwd)
        results.append({"command": cmd, "returncode": code, "output": out})
        if code != 0:
            break
    return results


def run_check(cwd: Path) -> dict[str, Any]:
    script = Path(__file__).with_name("check_dependencies.py")
    code, out = run([sys.executable, str(script), "--cwd", str(cwd), "--json"], cwd)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        data = {"ok": False, "error": out, "returncode": code}
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up template-to-slide project-local runtime dependencies")
    parser.add_argument("--cwd", default=".", help="Project directory")
    parser.add_argument("--install", action="store_true", help="Actually install npm dependencies. Without this flag, only print the planned actions.")
    parser.add_argument("--package-manager", choices=["npm", "pnpm"], default=None)
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    before = run_check(cwd)
    report: dict[str, Any] = {
        "cwd": str(cwd),
        "before": before,
        "installed": False,
        "package_manager": None,
        "install_results": [],
        "after": None,
        "notes": [
            "This script installs npm runtime packages only.",
            "Install frontend-slides and dom-to-pptx companion Skills separately through the ChatGPT skill flow.",
        ],
    }

    try:
        manager = choose_package_manager(cwd, args.package_manager)
        report["package_manager"] = manager
        if args.install:
            report["install_results"] = install_packages(cwd, manager)
            report["installed"] = all(item["returncode"] == 0 for item in report["install_results"])
            report["after"] = run_check(cwd)
        else:
            report["planned_commands"] = [
                [manager, "add", *RUNTIME_PACKAGES] if manager == "pnpm" else ["npm", "install", *RUNTIME_PACKAGES],
                [manager, "exec", "playwright", "install", "chromium"] if manager == "pnpm" else ["npx", "playwright", "install", "chromium"],
            ]
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Project: {report['cwd']}")
        if report.get("error"):
            print(f"Error: {report['error']}")
        elif args.install:
            for item in report["install_results"]:
                print("$", " ".join(item["command"]))
                print(item["output"])
            print("Installed:", report["installed"])
        else:
            print("Planned commands; rerun with --install after user approval:")
            for cmd in report.get("planned_commands", []):
                print("  " + " ".join(cmd))
        for note in report["notes"]:
            print("Note:", note)

    return 1 if report.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
