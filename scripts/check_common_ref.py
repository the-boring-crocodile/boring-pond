#!/usr/bin/env python3
"""Each consumer's `.common-ref` names the Common its locks pin.

    python scripts/check_common_ref.py

Hosted CI builds Pond Common from the commit in a consumer's `.common-ref` and
installs the consumer's hash lock against those wheels. A ref left behind after
a relock (refs at 0.7.1, locks at 0.7.3, say) fails
only there, after publication. This check fails here instead: the ref must be a
commit of the sibling boring-pond-common whose VERSION equals every Common
package version pinned in the consumer's tracked locks (pond/ excluded).
pondNT also names the Services commit used for its bundled packages in
.services-ref. Dependency refs must be full commit IDs available locally.

The whole family builds on one Common release (Wald, 2026-10-30): every
consumer's `.common-ref` names the same commit, and the Services commit pondNT
bundles names it too.
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


def frozen_ref(root: Path, filename: str, source: Path) -> str:
    try:
        ref = (root / filename).read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ValueError(f"{root.name}: cannot read {filename}: {error}") from error
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", ref):
        raise ValueError(f"{root.name}: {filename} must name a full commit ID")
    try:
        commit = git(source, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    except subprocess.CalledProcessError as error:
        raise ValueError(f"{root.name}: {filename} {ref} is not an available commit of {source.name}") from error
    if commit != ref:
        raise ValueError(f"{root.name}: {filename} must name a commit, not a tag object")
    return ref


def problems(repo: str) -> list[str]:
    root = FAMILY / repo
    try:
        ref = frozen_ref(root, ".common-ref", COMMON)
        version = git(COMMON, "show", f"{ref}:VERSION").strip()
        if repo == "boring-pondnt":
            frozen_ref(root, ".services-ref", FAMILY / "boring-services")
    except (ValueError, subprocess.CalledProcessError) as error:
        return [f"{repo}: dependency ref failed: {error}"]
    locks = [p for p in git(root, "ls-files").split() if p.endswith(".lock") and not p.startswith("pond/")]
    pinned = {v for p in locks for v in PINNED.findall((root / p).read_text(encoding="utf-8"))}
    if not pinned:
        return [f"{repo}: no Common package pinned in {locks}"]
    if pinned != {version}:
        return [f"{repo}: .common-ref {ref[:7]} is Common {version}; the locks pin {', '.join(sorted(pinned))}"]
    return []


def one_common(refs: dict[str, str]) -> list[str]:
    """Every consumer, and the Services commit pondNT bundles, name the same Common commit."""
    if len(set(refs.values())) <= 1:
        return []
    return ["Common refs differ: " + ", ".join(f"{name} {ref[:7]}" for name, ref in sorted(refs.items()))]


def family_refs() -> dict[str, str]:
    refs = {repo: (FAMILY / repo / ".common-ref").read_text(encoding="utf-8").strip() for repo in CONSUMERS}
    services = (FAMILY / "boring-pondnt" / ".services-ref").read_text(encoding="utf-8").strip()
    refs["boring-pondnt's bundled Services"] = git(FAMILY / "boring-services", "show", f"{services}:.common-ref").strip()
    return refs


def main() -> int:
    found = [p for repo in CONSUMERS for p in problems(repo)]
    if not found:
        found = one_common(family_refs())
    for line in found:
        print(line)
    print("common-ref: " + ("FAILED" if found else "every .common-ref matches its locks and names the same Common; pondNT Services ref resolves"))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
