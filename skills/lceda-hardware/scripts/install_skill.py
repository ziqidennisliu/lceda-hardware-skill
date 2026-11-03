#!/usr/bin/env python3
"""Install this skill without overwriting an existing different skill."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil


def files(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def install(source, destination, apply=False):
    target = destination / source.name
    if target.resolve() == source.resolve():
        return f"Already at {target}"
    if target.exists():
        if files(source) == files(target):
            return f"Already installed, identical: {target}"
        raise RuntimeError(f"Existing different skill preserved: {target}; choose another destination or review an update")
    if apply:
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if files(source) != files(target):
            raise RuntimeError("Installed copy failed hash comparison")
    return f"{'Installed' if apply else 'Would install'}: {target}"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--destination", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home()/'.codex'))) / 'skills')
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        print(install(Path(__file__).resolve().parent.parent, args.destination.expanduser().resolve(), args.apply))
    except (OSError, RuntimeError) as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
