# DistroLinux

DistroLinux is a lightweight command-line tool for checking whether a Linux environment is ready for development, builds, scripts, or automation.

## Checks

- Linux distribution, kernel, and architecture details
- User context and writable `/tmp` and home directory
- Common developer tools: `bash`, `git`, `curl`, `python3`, `gcc`, and `make`
- Available package manager
- Ping and HTTPS connectivity
- Hostname resolution

## Usage

```bash
python3 distrolinux.py
```

For machine-readable JSON output:

```bash
python3 distrolinux.py --json
```

The command exits with `0` if every check passes, or `1` if one or more checks fail. Network checks may fail in restricted or offline environments; this does not necessarily mean the local Linux environment is unusable.

The old `linux_env_tester.py` filename remains as a compatibility entry point and forwards to DistroLinux.
