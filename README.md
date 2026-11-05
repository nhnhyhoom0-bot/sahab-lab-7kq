# Linux Environment Tester

This repository contains a lightweight CLI utility for testing a Linux environment before running builds, scripts, or automation tasks.

## What it checks

- OS and kernel details
- User context and writable home/temp directories
- Common developer tools (`bash`, `git`, `curl`, `python3`, `gcc`, `make`)
- Installed package manager
- Ping and HTTP connectivity
- DNS / hostname resolution

## Usage

```bash
python3 linux_env_tester.py
```

JSON output:

```bash
python3 linux_env_tester.py --json
```

## Example result

```text
Linux Environment Test
========================
System: Linux 6.8.0-52-generic (x86_64)
Distribution: Ubuntu

[PASS] user_context: user=root, root=True
[PASS] tmp_writable: /tmp writable
[PASS] tool_bash: bash available
[FAIL] tool_gcc: gcc missing
...

Summary: 11/12 checks passed
```

## Exit codes

- `0`: all checks passed
- `1`: one or more checks failed

## License

This project is intentionally minimal and ready to extend for your own lab/test environment requirements.
