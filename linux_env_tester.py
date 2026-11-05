#!/usr/bin/env python3
"""Linux environment test utility.

This script inspects a Linux host and reports whether common developer tools,
network access, and basic permissions are available.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import pwd
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout or stderr
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, "command not found"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as exc:
        return False, str(exc)


def read_os_release():
    data = {}
    path = Path("/etc/os-release")
    if not path.exists():
        return data

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def detect_package_manager():
    managers = [
        ("apt", ["apt-get", "apt"]),
        ("dnf", ["dnf"]),
        ("yum", ["yum"]),
        ("pacman", ["pacman"]),
        ("apk", ["apk"]),
        ("zypper", ["zypper"]),
    ]
    for name, commands in managers:
        for cmd in commands:
            if shutil.which(cmd):
                return name
    return "unknown"


def check_command(command_name):
    return shutil.which(command_name) is not None


def summary_from_results(results):
    passed = sum(1 for item in results if item["ok"])
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "total": len(results)}


def build_report():
    environment = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "os_release": read_os_release(),
    }

    results = []

    # Basic environment checks
    user = pwd.getpwuid(os.getuid()).pw_name if hasattr(os, "getuid") else "unknown"
    root_user = os.geteuid() == 0 if hasattr(os, "geteuid") else False
    results.append({
        "name": "user_context",
        "ok": True,
        "detail": f"user={user}, root={root_user}",
    })

    results.append({
        "name": "tmp_writable",
        "ok": os.access("/tmp", os.W_OK),
        "detail": "/tmp writable" if os.access("/tmp", os.W_OK) else "/tmp not writable",
    })

    results.append({
        "name": "home_directory",
        "ok": os.path.isdir(os.path.expanduser("~")),
        "detail": f"home={os.path.expanduser('~')}",
    })

    # Shell / tools
    for tool in ["bash", "sh", "git", "curl", "python3", "gcc", "make"]:
        results.append({
            "name": f"tool_{tool}",
            "ok": check_command(tool),
            "detail": f"{tool} {'available' if check_command(tool) else 'missing'}",
        })

    # Package manager
    pkg_manager = detect_package_manager()
    results.append({
        "name": "package_manager",
        "ok": pkg_manager != "unknown",
        "detail": f"package_manager={pkg_manager}",
    })

    # Network access
    ping_ok, ping_message = run_command(["ping", "-c", "1", "-W", "2", "8.8.8.8"])
    curl_ok, curl_message = run_command(["curl", "-I", "--max-time", "5", "https://example.com"])
    results.append({
        "name": "network_ping",
        "ok": ping_ok,
        "detail": ping_message or "ping ok",
    })
    results.append({
        "name": "network_http",
        "ok": curl_ok,
        "detail": curl_message or "HTTP connectivity ok",
    })

    # DNS / hostname
    try:
        hostname = socket.gethostname()
        addr = socket.gethostbyname(hostname)
        dns_ok = True
        dns_detail = f"hostname={hostname}, ip={addr}"
    except Exception as exc:
        dns_ok = False
        dns_detail = str(exc)
    results.append({
        "name": "dns_hostname",
        "ok": dns_ok,
        "detail": dns_detail,
    })

    report = {
        "environment": environment,
        "checks": results,
        "summary": summary_from_results(results),
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Test a Linux environment for common development needs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    report = build_report()

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["summary"]["failed"] == 0 else 1

    print("Linux Environment Test")
    print("=" * 24)
    env = report["environment"]
    print(f"System: {env['system']} {env['release']} ({env['machine']})")
    os_info = env.get("os_release", {})
    if os_info:
        name = os_info.get("NAME") or os_info.get("PRETTY_NAME") or "Linux"
        print(f"Distribution: {name}")
    print()

    for item in report["checks"]:
        status = "PASS" if item["ok"] else "FAIL"
        print(f"[{status}] {item['name']}: {item['detail']}")

    print()
    summary = report["summary"]
    print(f"Summary: {summary['passed']}/{summary['total']} checks passed")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
