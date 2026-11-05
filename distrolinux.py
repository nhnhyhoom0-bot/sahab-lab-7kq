#!/usr/bin/env python3
"""DistroLinux: inspect a Linux environment and run basic readiness checks."""

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
        output = result.stdout.strip() or result.stderr.strip()
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
        if line and "=" in line:
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
        if any(shutil.which(command) for command in commands):
            return name
    return "unknown"


def check_command(command_name):
    return shutil.which(command_name) is not None


def summary_from_results(results):
    passed = sum(1 for item in results if item["ok"])
    return {"passed": passed, "failed": len(results) - passed, "total": len(results)}


def build_report():
    environment = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "os_release": read_os_release(),
    }
    results = []

    user = pwd.getpwuid(os.getuid()).pw_name if hasattr(os, "getuid") else "unknown"
    root_user = os.geteuid() == 0 if hasattr(os, "geteuid") else False
    results.append({"name": "user_context", "ok": True, "detail": f"user={user}, root={root_user}"})

    tmp_writable = os.access("/tmp", os.W_OK)
    results.append({
        "name": "tmp_writable",
        "ok": tmp_writable,
        "detail": "/tmp writable" if tmp_writable else "/tmp not writable",
    })

    home = os.path.expanduser("~")
    results.append({
        "name": "home_directory",
        "ok": os.path.isdir(home),
        "detail": f"home={home}",
    })

    for tool in ["bash", "sh", "git", "curl", "python3", "gcc", "make"]:
        available = check_command(tool)
        results.append({
            "name": f"tool_{tool}",
            "ok": available,
            "detail": f"{tool} {'available' if available else 'missing'}",
        })

    pkg_manager = detect_package_manager()
    results.append({
        "name": "package_manager",
        "ok": pkg_manager != "unknown",
        "detail": f"package_manager={pkg_manager}",
    })

    ping_ok, ping_message = run_command(["ping", "-c", "1", "-W", "2", "8.8.8.8"])
    curl_ok, curl_message = run_command(["curl", "-I", "--max-time", "5", "https://example.com"])
    results.append({"name": "network_ping", "ok": ping_ok, "detail": ping_message or "ping ok"})
    results.append({"name": "network_http", "ok": curl_ok, "detail": curl_message or "HTTP connectivity ok"})

    try:
        hostname = socket.gethostname()
        address = socket.gethostbyname(hostname)
        dns_ok, dns_detail = True, f"hostname={hostname}, ip={address}"
    except Exception as exc:
        dns_ok, dns_detail = False, str(exc)
    results.append({"name": "dns_hostname", "ok": dns_ok, "detail": dns_detail})

    return {
        "environment": environment,
        "checks": results,
        "summary": summary_from_results(results),
    }


def main():
    parser = argparse.ArgumentParser(description="DistroLinux: test a Linux environment for common development needs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["summary"]["failed"] == 0 else 1

    print("DistroLinux — Linux Environment Test")
    print("=" * 36)
    env = report["environment"]
    print(f"System: {env['system']} {env['release']} ({env['machine']})")
    os_info = env.get("os_release", {})
    if os_info:
        name = os_info.get("PRETTY_NAME") or os_info.get("NAME") or "Linux"
        print(f"Distribution: {name}")
    print()

    for item in report["checks"]:
        status = "PASS" if item["ok"] else "FAIL"
        print(f"[{status}] {item['name']}: {item['detail']}")

    summary = report["summary"]
    print(f"\nSummary: {summary['passed']}/{summary['total']} checks passed")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
