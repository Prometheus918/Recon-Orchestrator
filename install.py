#!/usr/bin/env python3
"""
Dependency installer for recon_orchestrator.py on Kali Linux.

What it does:
- Checks required external tools.
- Installs missing packages using apt/go/npm.
- Performs a final verification pass.

Usage:
  python3 install.py
  python3 install.py --dry-run
  python3 install.py --no-upgrade
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolSpec:
    name: str
    checker: Callable[[], bool]
    install_steps: list[list[str]]
    note: str = ""


def run_cmd(cmd: list[str], dry_run: bool = False, check: bool = True) -> int:
    print(f"[cmd] {' '.join(cmd)}")
    if dry_run:
        return 0
    proc = subprocess.run(cmd, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.returncode


def has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def has_any_cmd(names: list[str]) -> bool:
    return any(has_cmd(name) for name in names)


def ensure_root_or_sudo() -> bool:
    return os.geteuid() == 0 or has_cmd("sudo")


def npm_global_bin_contains(name: str) -> bool:
    return has_cmd(name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install recon_orchestrator dependencies on Kali Linux")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--no-upgrade", action="store_true", help="Skip apt update/upgrade")
    args = parser.parse_args()

    if not ensure_root_or_sudo():
        print("[-] Need root privileges or sudo available.", file=sys.stderr)
        return 1

    sudo_prefix = [] if os.geteuid() == 0 else ["sudo"]

    apt_prelude = []
    if not args.no_upgrade:
        apt_prelude = [
            [*sudo_prefix, "apt-get", "update"],
            [*sudo_prefix, "apt-get", "-y", "upgrade"],
        ]

    base_apt_packages = [
        "ca-certificates",
        "curl",
        "git",
        "python3",
        "python3-pip",
        "nmap",
        "masscan",
        "rustscan",
        "whatweb",
        "wafw00f",
        "amass",
        "golang-go",
        "nodejs",
        "npm",
        "eyewitness",
    ]

    print("[+] Installing base system dependencies via apt...")
    try:
        for c in apt_prelude:
            run_cmd(c, dry_run=args.dry_run)
        run_cmd([*sudo_prefix, "apt-get", "install", "-y", *base_apt_packages], dry_run=args.dry_run)
    except Exception as exc:
        print(f"[-] apt stage failed: {exc}", file=sys.stderr)
        return 1

    go_path = os.path.expanduser("~/go/bin")
    if go_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{os.environ.get('PATH', '')}:{go_path}"

    go_specs = [
        ToolSpec(
            name="subfinder",
            checker=lambda: has_cmd("subfinder"),
            install_steps=[["go", "install", "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"]],
        ),
        ToolSpec(
            name="httpx",
            checker=lambda: has_cmd("httpx"),
            install_steps=[["go", "install", "github.com/projectdiscovery/httpx/cmd/httpx@latest"]],
        ),
        ToolSpec(
            name="httprobe",
            checker=lambda: has_cmd("httprobe"),
            install_steps=[["go", "install", "github.com/tomnomnom/httprobe@latest"]],
        ),
        ToolSpec(
            name="assetfinder",
            checker=lambda: has_cmd("assetfinder"),
            install_steps=[["go", "install", "github.com/tomnomnom/assetfinder@latest"]],
        ),
    ]

    print("[+] Checking Go-based tools...")
    for spec in go_specs:
        if spec.checker():
            print(f"[ok] {spec.name} already installed")
            continue
        print(f"[+] Installing {spec.name}...")
        try:
            for c in spec.install_steps:
                run_cmd(c, dry_run=args.dry_run)
        except Exception as exc:
            print(f"[!] Failed to install {spec.name}: {exc}")

    print("[+] Checking npm-based tools...")
    if not npm_global_bin_contains("wappalyzer"):
        try:
            run_cmd([*sudo_prefix, "npm", "install", "-g", "wappalyzer"], dry_run=args.dry_run, check=False)
        except Exception as exc:
            print(f"[!] Wappalyzer install attempt failed: {exc}")

    print("[+] Verifying required tools...")
    required = [
        "subfinder",
        "amass",
        "assetfinder",
        "httpx",
        "httprobe",
        "wafw00f",
        "nmap",
        "masscan",
        "rustscan",
        "whatweb",
        "wappalyzer",
        "eyewitness",
    ]

    missing: list[str] = []
    for tool in required:
        if tool == "eyewitness":
            if not has_any_cmd(["eyewitness", "EyeWitness", "EyeWitness.py"]):
                missing.append(tool)
        elif not has_cmd(tool):
            missing.append(tool)

    print("\n=== Dependency Check Summary ===")
    for tool in required:
        status = "OK" if tool not in missing else "MISSING"
        print(f"- {tool}: {status}")

    if go_path not in os.environ.get("PATH", ""):
        print(f"[!] Ensure {go_path} is in PATH for Go-installed tools.")

    if missing:
        print("\n[!] Some tools are still missing.")
        print("    On Kali, this is usually PATH or package availability related.")
        print("    Try adding ~/go/bin to PATH and re-run this installer.")
        return 2

    print("\n[+] All required tools are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
