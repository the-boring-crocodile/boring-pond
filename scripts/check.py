#!/usr/bin/env python3
"""The family check: every repository's own check, one after the other.

    python scripts/check.py [--only crocodile pirates ...] [--python PY [PY ...] | --ci-pythons]

Sibling checkouts live next to this repository. The family builds on one
Common release, so every consumer's .common-ref names the same commit (mixed
refs are refused before anything runs); the runner builds that Common once,
in a detached temporary worktree. pondNT gets Services from its .services-ref.
Sibling branches and existing distributions stay untouched; the owner checks
still enforce lock hashes. Common's own check runs on the current checkout.

--common-wheels DIST uses an explicit distribution instead of building.

Each product check (Common and the consumers) runs once per --python; the
family's own checks and the Common build use the first. --ci-pythons takes
the Pythons the public CI matrices use (CI_PYTHONS), found through uv; the
public CI found what a 3.14-only local run missed (2026-10-31).
"""
import argparse
import os
import shutil
from contextlib import ExitStack, contextmanager
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import check_common_ref as refs

FAMILY = Path(__file__).resolve().parents[2]
CHECKS = {
    "runner": ("boring-pond", "scripts/test_check.py"),
    "docs": ("boring-pond", "scripts/check_docs.py"),
    "licences": ("boring-pond", "scripts/check_licences.py"),
    "common-ref": ("boring-pond", "scripts/check_common_ref.py"),
    # Private names in any product tree; pond/checks is absent from a published copy.
    "names": ("boring-pond", "pond/checks/check_names.py"),
    "common": ("boring-pond-common", "scripts/check.py"),
    "crocodile": ("boring-crocodile", "scripts/check.py"),
    "pirates": ("boring-pirates", "scripts/check.py"),
    "services": ("boring-services", "scripts/check.py"),
    "pondnt": ("boring-pondnt", "scripts/check.py"),
}
CONSUMERS = ("crocodile", "pirates", "services", "pondnt")
PRODUCTS = ("common", *CONSUMERS)
CI_PYTHONS = ("3.14", "3.12", "3.10")  # the products' CI matrices; first one runs the family checks


def ci_pythons() -> list[str]:
    """Interpreter paths for CI_PYTHONS, as uv finds them (UV or uv on PATH)."""
    uv = os.environ.get("UV") or shutil.which("uv")
    if not uv:
        raise ValueError("--ci-pythons needs uv: put it on PATH or set UV=/path/to/uv")
    found = []
    for version in CI_PYTHONS:
        run = subprocess.run([uv, "python", "find", "--no-project", version], capture_output=True, text=True)
        if run.returncode:
            raise ValueError(f"no Python {version} found by uv (uv python install {version})")
        found.append(run.stdout.strip())
    return found


def label(name: str, python: str, pythons: list[str]) -> str:
    if name not in PRODUCTS or len(pythons) == 1:
        return name
    version = subprocess.run([python, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
                             capture_output=True, text=True, check=True).stdout.strip()
    return f"{name}@{version}"


def inputs(names: list[str], common_wheels: Path | None) -> tuple[str | None, str | None]:
    """Resolve and validate all selected inputs before starting owner checks."""
    selected = {name: refs.frozen_ref(FAMILY / CHECKS[name][0], ".common-ref",
                                     FAMILY / "boring-pond-common")
                for name in names if name in CONSUMERS}
    found = [p for name in selected for p in refs.problems(CHECKS[name][0])]
    found += refs.one_common(selected)
    if found:
        raise ValueError("\n".join(found))
    if common_wheels is not None and not common_wheels.is_dir():
        raise ValueError(f"--common-wheels is not a directory: {common_wheels}")
    services_ref = (refs.frozen_ref(FAMILY / "boring-pondnt", ".services-ref",
                                   FAMILY / "boring-services") if "pondnt" in selected else None)
    return next(iter(selected.values()), None), services_ref


@contextmanager
def worktree(repo: Path, ref: str, path: Path):
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", str(path), ref], check=True)
    try:
        yield path
    finally:
        # Only this invocation's detached checkout; builds may leave __pycache__.
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(path)], check=True)


def command(name: str, python: str, wheels: Path | None, services: Path | None) -> list[str]:
    repo, script = CHECKS[name]
    cmd = [python, str(FAMILY / repo / script)]
    if name in ("common", *CONSUMERS):
        cmd += ["--python", python]
    if name in CONSUMERS:
        assert wheels is not None
        cmd += ["--common-wheels", str(wheels)]
    if name == "pondnt":
        assert services is not None
        cmd += ["--services-root", str(services)]
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--common-wheels", type=Path)
    parser.add_argument("--only", nargs="+", choices=list(CHECKS), default=list(CHECKS))
    parser.add_argument("--python", nargs="+", default=[sys.executable])
    parser.add_argument("--ci-pythons", action="store_true", help="the Pythons of the CI matrices")
    args = parser.parse_args()
    try:
        pythons = ci_pythons() if args.ci_pythons else args.python
        first = pythons[0]
        common_ref, services_ref = inputs(args.only, args.common_wheels)
        results = []
        with tempfile.TemporaryDirectory(prefix="pond-family-check-") as tmp, ExitStack() as stack:
            tmp = Path(tmp)
            wheels = None
            if common_ref is not None:
                print(f"input: Common {common_ref}", flush=True)
                if args.common_wheels is not None:
                    wheels = args.common_wheels.resolve()
                else:
                    tree = stack.enter_context(worktree(FAMILY / "boring-pond-common", common_ref, tmp / "common"))
                    wheels = tmp / "common-dist"
                    subprocess.run([first, str(tree / "scripts/build.py"), "--out", str(wheels)],
                                   cwd=tree, check=True)
            services = None
            if services_ref is not None:
                print(f"input pondnt: Services {services_ref}", flush=True)
                services = stack.enter_context(worktree(FAMILY / "boring-services", services_ref, tmp / "services"))
            for name in args.only:
                for python in (pythons if name in PRODUCTS else [first]):
                    shown = label(name, python, pythons)
                    print(f"=== {shown}", flush=True)
                    if name == "names" and not (FAMILY / "/".join(CHECKS[name])).is_file():
                        print("pond/checks absent: skipped")
                        continue
                    started = time.monotonic()
                    code = subprocess.run(command(name, python, wheels, services),
                                          cwd=FAMILY / CHECKS[name][0]).returncode
                    results.append((shown, code, time.monotonic() - started))
        print("\n=== summary")
        for name, code, seconds in results:
            print(f"  {name:16} {'passed' if code == 0 else f'FAILED ({code})'}  {seconds:.0f} s")
        return 0 if all(code == 0 for _, code, _ in results) else 1
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"family check: FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
