#!/usr/bin/env python3
"""Copy common Visual C++ runtime DLLs into a PyInstaller `dist/` folder.

This helper searches the local Python installation and site-packages for
candidate runtime DLLs (vcruntime140*, msvcp*, concrt140, vccorlib140) and
copies any it finds into the provided `dist` directory. It's conservative and
only copies files that exist; it prints a summary of copied files.

Usage:
    python tools/bundle_vcruntime.py --dist dist
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import site
import sys
from typing import List, Set


RUNTIME_PATTERNS = [
    "**/vcruntime*.dll",
    "**/msvcp*.dll",
    "**/concrt140.dll",
    "**/vccorlib140.dll",
]

# Curated list of allowed runtime DLL basenames. This avoids copying
# hashed/artifact-named variants like 'msvcp140-<hash>.dll'. Only files
# with these exact basenames will be copied.
ALLOWED_BASENAMES = {
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "msvcp140.dll",
    "concrt140.dll",
    "vccorlib140.dll",
}


def find_runtime_dlls() -> List[str]:
    roots: List[str] = []
    # Python installation roots
    roots.append(sys.base_prefix)
    roots.append(sys.exec_prefix)

    # Add site-packages locations
    try:
        roots.extend(site.getsitepackages())
    except Exception:
        pass
    # Add user site-packages
    try:
        user = site.getusersitepackages()
        roots.append(user)
    except Exception:
        pass

    found: Set[str] = set()
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for pattern in RUNTIME_PATTERNS:
            path_pattern = os.path.join(root, pattern)
            for p in glob.glob(path_pattern, recursive=True):
                if os.path.isfile(p):
                    # Only include candidates whose basename is in the allowed set
                    b = os.path.basename(p).lower()
                    if b in ALLOWED_BASENAMES:
                        found.add(os.path.abspath(p))

    # Also check current directory as a last resort
    for pattern in RUNTIME_PATTERNS:
        for p in glob.glob(os.path.join(os.getcwd(), pattern), recursive=True):
            if os.path.isfile(p):
                b = os.path.basename(p).lower()
                if b in ALLOWED_BASENAMES:
                    found.add(os.path.abspath(p))

    return sorted(found)


def copy_to_dist(dll_paths: List[str], dist_dir: str) -> List[str]:
    os.makedirs(dist_dir, exist_ok=True)
    copied: List[str] = []
    for src in dll_paths:
        name = os.path.basename(src)
        dest = os.path.join(dist_dir, name)
        try:
            shutil.copy2(src, dest)
            copied.append(dest)
        except Exception:
            # Ignore copy errors for safety
            pass
    return copied


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Copy VC runtime DLLs into dist folder")
    p.add_argument("--dist", required=True, help="Path to the PyInstaller dist folder")
    args = p.parse_args(argv)

    dist_dir = os.path.abspath(args.dist)
    dlls = find_runtime_dlls()
    if not dlls:
        print("No candidate VC runtime DLLs found on this system.")
        return 0

    copied = copy_to_dist(dlls, dist_dir)
    if copied:
        print(f"Copied {len(copied)} runtime DLL(s) into: {dist_dir}")
        for c in copied:
            print(" -", c)
    else:
        print("Found runtime DLLs but none were copied (permissions?).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
