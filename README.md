# DistroLinux

DistroLinux is a lightweight command-line tool for checking whether a Linux environment is ready for development, builds, scripts, or automation.

## Checks

- Linux distribution, kernel, and architecture details
- User context and writable `/tmp` and home directory
- Common developer tools: `bash`, `git`, `curl`, `python3`, `gcc`, and `make`
- Available package manager
- Ping and HTTPS connectivity
- Hostname resolution

## Run from the repository

```bash
python3 distrolinux.py
python3 distrolinux.py --json
```

The command exits with `0` if every check passes, or `1` if one or more checks fail. Network checks may fail in restricted or offline environments; this does not necessarily mean the local Linux environment is unusable.

## Arch Linux / AUR

An Arch `PKGBUILD` and matching `.SRCINFO` are included. To build and install locally, from the repository root run:

```bash
makepkg -si
```

After the package is published to the AUR, install it with an AUR helper, for example:

```bash
yay -S distrolinux
```

`sudo pacman -S distrolinux` will only work if the package is added to an official or separately configured pacman repository; AUR packages are not installed directly by pacman. This repository change prepares the packaging files but does not publish an AUR package. To publish, create an AUR package repository and push the `PKGBUILD` and generated `.SRCINFO` there. Update the pinned source commit and package version in both files for each release.

The package currently declares `custom:UNLICENSED` because the project has not selected a software license. Choose a license and update the package metadata before public distribution.

## Debian / Ubuntu

Debian packaging metadata is in `debian/`. A generated `.deb` can be installed locally, but making `sudo apt install distrolinux` work requires publishing a signed APT repository and configuring it on user systems.

The old `linux_env_tester.py` filename remains as a compatibility entry point and forwards to DistroLinux.
