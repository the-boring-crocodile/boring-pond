#!/usr/bin/env python3
"""Each consumer's `.common-ref` names the Common its locks pin.

    python scripts/check_common_ref.py

Hosted CI builds Pond Common from the commit in a consumer's `.common-ref` and
installs the consumer's hash lock against those wheels. A ref left behind after
a relock (refs at 0.7.1, locks at 0.7.3, say) fails
only there, after publication. This check fails here instead: the ref must be a
commit of the sibling boring-pond-common whose VERSION equals every Common
package version pinned in the consumer's tracked locks (pond/ excluded).
"""
import re
import subprocess
import sys
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
COMMON = FAMILY / "boring-pond-common"
CONSUMERS = ("boring-crocodile", "boring-pirates", "boring-services", "boring-pondnt")
PINNED = re.compile(r"^boring-(?:registry|file-core|service-kit|worker-kit|deploy)==(\S+)", re.M)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def problems(repo: str) -> list[str]:
    root = FAMILY / repo
    ref_file = root / ".common-ref"
    if not ref_file.is_file():
        return [f"{repo}: no .common-ref"]
    ref = ref_file.read_text(encoding="utf-8").strip()
    try:
        version = git(COMMON, "show", f"{ref}:VERSION").strip()
    except subprocess.CalledProcessError:
        return [f"{repo}: .common-ref {ref} is not a commit of boring-pond-common with a VERSION"]
    locks = [p for p in git(root, "ls-files").split() if p.endswith(".lock") and not p.startswith("pond/")]
    pinned = {v for p in locks for v in PINNED.findall((root / p).read_text(encoding="utf-8"))}
    if not pinned:
        return [f"{repo}: no Common package pinned in {locks}"]
    if pinned != {version}:
        return [f"{repo}: .common-ref {ref[:7]} is Common {version}; the locks pin {', '.join(sorted(pinned))}"]
    return []


def main() -> int:
    found = [p for repo in CONSUMERS for p in problems(repo)]
    for line in found:
        print(line)
    print("common-ref: " + ("FAILED" if found else "every .common-ref matches its locks"))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
