#!/usr/bin/env python3
"""Product docs name nothing in our own records.

    python scripts/check_docs.py [REPO ...]

Every repository keeps its own records in `pond/`, which is never released.
A published page that links or points there leads nowhere, so this fails on
any `pond/...` path in a tracked Markdown or SVG file outside `pond/`
(product docs never link into pond/). `boring-pond/`
and URL paths such as `/mcp/pond/` are not matches. Scripts may name
`pond/checks`: they skip it when it is absent.

Links, in tracked Markdown outside `pond/` (fenced code blocks are not
links): a relative link must resolve to a file in its own repository. On
GitHub each repository stands alone, so a link into a sibling is written as
https://github.com/the-boring-crocodile/<repo>/blob/main/<path> (tree/ for a
folder), and that path must exist in the sibling checkout, outside `pond/`.

Our own records: each repository's private STATUS page (when present; a
published copy has none) is a current-state page of at most STATUS_MAX_LINES
lines, edited in place; dated text goes to its history.

Without arguments it checks the family's sibling checkouts. Exit 0: clean;
1: each hit printed as REPO/FILE:LINE: TEXT; 2: a repository is missing.
"""
import re
import subprocess
import sys
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
REPOS = ["boring-pond", "boring-pond-common", "boring-crocodile", "boring-pirates",
         "boring-services", "boring-pondnt"]
PRIVATE = re.compile(r"(?<![\w/.-])pond/")
OWNER = "the-boring-crocodile"
FENCE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
RELATIVE = re.compile(r'(?:\]\(|(?:href|src|srcset)=")(?![a-z][a-z0-9+.-]*:|#|/)([^)"\s]+)')
STATUS_MAX_LINES = 80
GITHUB = re.compile(r"https://github\.com/" + OWNER + r"/(boring-[a-z-]+)/(?:blob|tree)/main/([^)#\s\"'>]*)")


def tracked_docs(repo: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--", "*.md", "*.svg"], cwd=repo,
                         check=True, capture_output=True).stdout.decode()
    return [p for p in out.split("\0") if p and not p.startswith("pond/")]


def hits(repo: Path) -> list[str]:
    found = []
    for rel in tracked_docs(repo):
        text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if PRIVATE.search(line):
                found.append(f"{repo.name}/{rel}:{number}: {line.strip()[:160]}")
    return found


def link_hits(repo: Path) -> list[str]:
    found = []
    for rel in tracked_docs(repo):
        if not rel.endswith(".md"):
            continue
        doc = repo / rel
        text = FENCE.sub("", doc.read_text(encoding="utf-8", errors="replace"))
        for match in RELATIVE.finditer(text):
            target = (doc.parent / match.group(1).partition("#")[0]).resolve()
            if not target.is_relative_to(repo.resolve()):
                found.append(f"{repo.name}/{rel}: {match.group(1)} points into another repository; "
                             f"link https://github.com/{OWNER}/<repo>/blob/main/<path>")
            elif not target.exists():
                found.append(f"{repo.name}/{rel}: {match.group(1)} does not exist")
        for match in GITHUB.finditer(text):
            sibling, path = match.group(1), match.group(2).rstrip("/")
            if sibling not in REPOS or path.split("/")[0] == "pond" or not (FAMILY / sibling / path).exists():
                found.append(f"{repo.name}/{rel}: {match.group(0)} has no target in {sibling}")
    return found


def status_hits(repo: Path) -> list[str]:
    status = repo / "pond" / "STATUS.md"
    if not status.exists():
        return []
    lines = len(status.read_text(encoding="utf-8").splitlines())
    if lines > STATUS_MAX_LINES:
        return [f"{repo.name}/pond/STATUS.md: {lines} lines, at most {STATUS_MAX_LINES}: "
                "a current-state page; move dated text to pond/history/STATUS_HISTORY.md"]
    return []


def main(argv: list[str]) -> int:
    names = argv or REPOS
    missing = [n for n in names if not (FAMILY / n / ".git").exists()]
    if missing:
        print("missing checkouts: " + ", ".join(missing), file=sys.stderr)
        return 2
    found = [h for n in names for h in hits(FAMILY / n)]
    links = [h for n in names for h in link_hits(FAMILY / n)]
    long = [h for n in names for h in status_hits(FAMILY / n)]
    for h in found + links + long:
        print(h)
    print(f"docs: {len(found)} path(s) into pond/" if found else "docs: no path into pond/")
    print(f"docs: {len(links)} broken or cross-repository link(s)" if links else "docs: every link resolves")
    print(f"docs: {len(long)} STATUS page(s) too long" if long else
          f"docs: every STATUS page within {STATUS_MAX_LINES} lines")
    return 1 if found or links or long else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
