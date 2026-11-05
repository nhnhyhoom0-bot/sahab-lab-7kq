#!/usr/bin/env python3
"""Compatibility entry point; use distrolinux.py for the renamed tool."""

from distrolinux import main

if __name__ == "__main__":
    raise SystemExit(main())
