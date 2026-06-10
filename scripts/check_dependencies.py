#!/usr/bin/env python3
"""Check runtime and companion dependencies for template-to-slide.

The script is intentionally read-only: it never installs packages. Use
setup_environment.py after user approval to perform network installation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED_COMMANDS = ["python3", "node"]
PACKAGE_MANAGERS = ["npm", "pnpm"]
REQUIRED_NODE_PACKAGES = ["dom-to-pptx", "pptxgenjs", "playwright"]
OPTIONAL_COMMANDS = ["npx", "zip", "unzip", "libreoffice", "soffice", "magick", "convert"]
COMPANION_SKILLS = ["frontend-slides", "dom-to-pptx", "dom-to-pptx-skill"]


def run(cmd: list[str], cwd: Path, timeout: int = 12) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


def command_info(name: str, version_args: list[str] | None = None, cwd: Path | None = None) -> dict[str, Any]:
    path = shutil.which(name)
    info: dict[str, Any] = {"name": name, "found": bool(path), "path": path, "version": None}
    if path and version_args:
        code, out = run([name, *version_args], cwd or Path.cwd())
        if code == 0 and out:
            info["version"] = out.splitlines()[0]
    return info


def node_module_roots(cwd: Path) -> list[Path]:
    candidates = [cwd / "node_modules"]

    env_roots = os.environ.get("NODE_REPL_NODE_MODULE_DIRS", "")
    candidates.extend(Path(p) for p in env_roots.split(os.pathsep) if p)

    # Common Codex/ChatGPT runtime cache location. It is optional.
    candidates.append(
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "node"
        / "node_modules"
    )

    # Parent workspaces sometimes keep node_modules one level above the skill.
    candidates.append(cwd.parent / "node_modules")

    seen: set[str] = set()
    roots: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        key = str(resolved)
        if key not in seen and resolved.exists():
            seen.add(key)
            roots.append(resolved)
    return roots


def node_package_info(package: str, cwd: Path) -> dict[str, Any]:
    roots = node_module_roots(cwd)
    roots_js = json.dumps([str(root) for root in roots])
    script = (
        "const { createRequire } = require('module');"
        f"const roots = {roots_js};"
        "for (const root of roots) {"
        "  try {"
        "    const req = createRequire(root + '/');"
        f"    console.log(req.resolve('{package}'));"
        "    process.exit(0);"
        "  } catch (e) {}"
        "}"
        "try {"
        f"  console.log(require.resolve('{package}'));"
        "  process.exit(0);"
        "} catch (e) {"
        "  console.error(e.message);"
        "  process.exit(1);"
        "}"
    )
    code, out = run(["node", "-e", script], cwd)
    return {"name": package, "found": code == 0, "path": out if code == 0 else None, "error": None if code == 0 else out}


def skill_locations(cwd: Path) -> list[Path]:
    roots: list[Path] = []
    env_vars = ["CODEX_HOME", "OPENAI_SKILLS_HOME", "CHATGPT_SKILLS_HOME"]
    for name in env_vars:
        value = os.environ.get(name)
        if value:
            roots.append(Path(value) / "skills")
    roots.extend(
        [
            cwd / "skills",
            cwd.parent / "skills",
            Path.home() / ".codex" / "skills",
            Path.home() / ".chatgpt" / "skills",
        ]
    )
    seen: set[str] = set()
    result: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            resolved = root
        key = str(resolved)
        if key not in seen:
            seen.add(key)
            result.append(resolved)
    return result


def companion_skill_info(name: str, cwd: Path) -> dict[str, Any]:
    matches: list[str] = []
    for root in skill_locations(cwd):
        candidate = root / name
        if (candidate / "SKILL.md").exists() or (candidate / "skill.md").exists():
            matches.append(str(candidate))
    return {"name": name, "found": bool(matches), "paths": matches}


def build_report(cwd: Path) -> dict[str, Any]:
    commands = {
        "python3": command_info("python3", ["--version"], cwd),
        "node": command_info("node", ["--version"], cwd),
        "npm": command_info("npm", ["--version"], cwd),
        "npx": command_info("npx", ["--version"], cwd),
        "pnpm": command_info("pnpm", ["--version"], cwd),
    }
    optional_commands = {name: command_info(name, ["--version"], cwd) for name in OPTIONAL_COMMANDS if name not in commands}

    if commands["node"]["found"]:
        node_packages = {name: node_package_info(name, cwd) for name in REQUIRED_NODE_PACKAGES}
    else:
        node_packages = {
            name: {"name": name, "found": False, "path": None, "error": "node missing"}
            for name in REQUIRED_NODE_PACKAGES
        }

    companion_skills = {name: companion_skill_info(name, cwd) for name in COMPANION_SKILLS}

    missing_required: list[str] = []
    for name in REQUIRED_COMMANDS:
        if not commands[name]["found"]:
            missing_required.append(name)
    if not any(commands[name]["found"] for name in PACKAGE_MANAGERS):
        missing_required.append("npm-or-pnpm")
    for name, info in node_packages.items():
        if not info["found"]:
            missing_required.append(name)

    warnings: list[str] = []
    if not companion_skills["frontend-slides"]["found"]:
        warnings.append("frontend-slides companion skill not found; innovation preview mode will use local design rules only")
    if not (companion_skills["dom-to-pptx"]["found"] or companion_skills["dom-to-pptx-skill"]["found"]):
        warnings.append("dom-to-pptx companion skill not found; local DOM contract will be used")

    return {
        "cwd": str(cwd),
        "node_module_roots": [str(root) for root in node_module_roots(cwd)],
        "skill_roots_checked": [str(root) for root in skill_locations(cwd)],
        "commands": commands,
        "optional_commands": optional_commands,
        "node_packages": node_packages,
        "companion_skills": companion_skills,
        "missing_required": missing_required,
        "warnings": warnings,
        "ok": not missing_required,
    }


def print_text_report(report: dict[str, Any]) -> None:
    print(f"Project: {report['cwd']}")
    print("Required commands:")
    for name in ["python3", "node", "npm", "pnpm", "npx"]:
        info = report["commands"].get(name)
        if not info:
            continue
        version = f" ({info['version']})" if info.get("version") else ""
        print(f"  {name}: {'found' if info['found'] else 'missing'}{version}")

    print("Required node packages:")
    for name, info in report["node_packages"].items():
        suffix = f" -> {info['path']}" if info.get("path") else ""
        print(f"  {name}: {'found' if info['found'] else 'missing'}{suffix}")

    print("Companion skills:")
    for name, info in report["companion_skills"].items():
        paths = f" -> {', '.join(info['paths'])}" if info.get("paths") else ""
        print(f"  {name}: {'found' if info['found'] else 'missing'}{paths}")

    print("Optional commands:")
    for name, info in report["optional_commands"].items():
        print(f"  {name}: {'found' if info['found'] else 'missing'}")

    if report["warnings"]:
        print("Warnings:")
        for warning in report["warnings"]:
            print(f"  - {warning}")

    if report["missing_required"]:
        print("Missing required:", ", ".join(report["missing_required"]))
    else:
        print("All required runtime dependencies found.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check template-to-slide runtime dependencies")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON only")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when required dependencies are missing")
    parser.add_argument("--cwd", default=".", help="Project directory to inspect for local node_modules")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    report = build_report(cwd)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text_report(report)

    return 1 if args.strict and report["missing_required"] else 0


if __name__ == "__main__":
    sys.exit(main())
