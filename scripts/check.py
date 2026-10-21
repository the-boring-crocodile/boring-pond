#!/usr/bin/env python3
"""The family check: every repository's own check, one after the other.

    python scripts/check.py --common-wheels DIST [--only crocodile pirates ...] [--python PY]

Runs the docs check (scripts/check_docs.py: no product page points into
pond/), the licence check (scripts/check_licences.py: reuse lint and the
licence copies; needs uv), the Common ref check (scripts/check_common_ref.py:
each consumer's .common-ref is the Common its locks pin, which hosted CI
builds), then Common's check (versions, build, tests on its built wheels), then each
consumer's `scripts/check.py --common-wheels DIST` (a fresh environment from
its hash lock, its tests, its type gate): Crocodile, Pirates, services,
pondNT. DIST is the Common dist the consumers' locks pin; after a family
relock that is the one Common release. Sibling checkouts are expected next to
this repository. Exit status 0 means every check passed; a summary lists each.
This is what a CI job would run.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
CHECKS = {  # name: (repository, extra arguments)
    "docs": ("boring-pond", ["--docs"]),
    "licences": ("boring-pond", ["--licences"]),
    "common-ref": ("boring-pond", ["--common-ref"]),
    "common": ("boring-pond-common", []),
    "crocodile": ("boring-crocodile", ["--common-wheels"]),
    "pirates": ("boring-pirates", ["--common-wheels"]),
    "services": ("boring-services", ["--common-wheels"]),
    "pondnt": ("boring-pondnt", ["--common-wheels", "--services-root"]),
}


def command(name: str, args: argparse.Namespace) -> list[str]:
    repo, extra = CHECKS[name]
    if "--docs" in extra:
        return [args.python, str(FAMILY / repo / "scripts/check_docs.py")]
    if "--licences" in extra:
        return [args.python, str(FAMILY / repo / "scripts/check_licences.py")]
    if "--common-ref" in extra:
        return [args.python, str(FAMILY / repo / "scripts/check_common_ref.py")]
    cmd = [args.python, str(FAMILY / repo / "scripts/check.py"), "--python", args.python]
    if "--common-wheels" in extra:
        cmd += ["--common-wheels", str(args.common_wheels.resolve())]
    if "--services-root" in extra:
        cmd += ["--services-root", str(FAMILY / "boring-services")]
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--common-wheels", type=Path, required=True)
    parser.add_argument("--only", nargs="+", choices=list(CHECKS), default=list(CHECKS))
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    results = []
    for name in args.only:
        print(f"=== {name}", flush=True)
        started = time.monotonic()
        code = subprocess.run(command(name, args), cwd=FAMILY / CHECKS[name][0]).returncode
        results.append((name, code, time.monotonic() - started))
    print("\n=== summary")
    for name, code, seconds in results:
        print(f"  {name:11} {'passed' if code == 0 else f'FAILED ({code})'}  {seconds:.0f} s")
    return 0 if all(code == 0 for _, code, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
