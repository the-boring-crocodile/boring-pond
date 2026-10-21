#!/usr/bin/env python3
"""The licence check of the family: every file has a licence, and the copies agree.

    python scripts/check_licences.py

For each repository (siblings of this one): `reuse lint` on its tracked files
without pond/ (the private material never published); LICENSE equals
LICENSES/AGPL-3.0-or-later.txt; every pyproject declares
`license = "AGPL-3.0-or-later"` with LICENSE and COPYING.md as license-files,
and a sub-package's copies of those two equal the repository's. Needs uv
(PATH or $UV) to run reuse; exit status 0 means every repository passed.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
REPOS = ("boring-pond", "boring-pond-common", "boring-crocodile", "boring-pirates",
         "boring-services", "boring-pondnt")
REUSE = "reuse==6.2.0"
DECLARED = ('license = "AGPL-3.0-or-later"', 'license-files = ["LICENSE", "COPYING.md"]')


def tracked(root: Path) -> list[str]:
    names = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True,
                           check=True).stdout.decode().split("\0")
    return [n for n in names if n and not n.startswith("pond/")]


def problems(repo: str, uv: str) -> list[str]:
    root, found = FAMILY / repo, []
    files = tracked(root)
    if (root / "LICENSE").read_bytes() != (root / "LICENSES/AGPL-3.0-or-later.txt").read_bytes():
        found.append("LICENSE differs from LICENSES/AGPL-3.0-or-later.txt")
    for name in (n for n in files if n.endswith("pyproject.toml")):
        text = (root / name).read_text()
        found += [f"{name}: lacks {line}" for line in DECLARED if line not in text]
        package = (root / name).parent
        if package != root:
            for copy in ("LICENSE", "COPYING.md"):
                if not (package / copy).is_file() or (package / copy).read_bytes() != (root / copy).read_bytes():
                    found.append(f"{(package / copy).relative_to(root)} is not a copy of the repository's {copy}")
    with tempfile.TemporaryDirectory() as tmp:
        for name in files:
            (Path(tmp) / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, Path(tmp) / name, follow_symlinks=False)
        lint = subprocess.run([uv, "tool", "run", "--quiet", "--from", REUSE, "reuse", "--root", tmp, "lint"],
                              capture_output=True, text=True)
        if lint.returncode != 0:
            found.append("reuse lint:\n" + lint.stdout[-3000:] + lint.stderr[-1000:])
    return found


def main() -> int:
    uv = os.environ.get("UV") or shutil.which("uv")
    if not uv:
        raise SystemExit("uv not found: put it on PATH or set UV=/path/to/uv")
    failed = False
    for repo in REPOS:
        found = problems(repo, uv)
        print(f"{repo}: {'ok' if not found else 'FAILED'}")
        for line in found:
            print("  " + line)
        failed = failed or bool(found)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
