#!/usr/bin/env python3
"""Product docs name nothing in our own records.

    python scripts/check_docs.py [REPO ...] [--with NAME=PATH ...] [--doc FILE ...]

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
A link's `#anchor` into a Markdown page must name one of that page's headings
(GitHub's anchors: lower case, punctuation dropped, spaces to hyphens, `-1`
for a repeated heading) or an explicit `id`/`name`; so must `#anchor` alone
(this page) and https://github.com/the-boring-crocodile/<repo>#anchor (the
repository's README). A heading renamed in one repository breaks the links
from the others; this finds it before a publication does.

`--with NAME=PATH` adds a checkout that links may point into without being
checked itself (another published repository, e.g. boring-mailstack).
`--doc FILE` checks one more Markdown file's links (a page published elsewhere,
e.g. an account profile), its relative links against its own folder.

The tested release set: boring-pond's copy-paste blocks pin versions
(`V=` for the Crocodile in getting-started, `CROCODILE=`, `PIRATES=`,
`CANVAS=` in updating), and boring-services' blocks (`V=X S=NAME`). Each must
equal the release set in docs/updating.md (its table, and for the services
its sentence naming the current set), so a new release set cannot leave a
block behind.

Our own records: each repository's private STATUS page (when present; a
published copy has none) is a current-state page of at most STATUS_MAX_LINES
lines, edited in place; dated text goes to its history.

Without arguments it checks the family's sibling checkouts. Exit 0: clean;
1: each hit printed as REPO/FILE:LINE: TEXT; 2: a repository is missing.
"""
import argparse
import re
import subprocess
import sys
import unicodedata
from functools import cache
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
REPOS = ["boring-pond", "boring-pond-common", "boring-crocodile", "boring-pirates",
         "boring-services", "boring-pondnt"]
PRIVATE = re.compile(r"(?<![\w/.-])pond/")
OWNER = "the-boring-crocodile"
FENCE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
RELATIVE = re.compile(r'(?:\]\(|(?:href|src|srcset)=")(?![a-z][a-z0-9+.-]*:|#|/)([^)"\s]+)')
SAME_PAGE = re.compile(r'(?:\]\(|href=")#([^)"\s]+)')
STATUS_MAX_LINES = 80
GITHUB = re.compile(r"https://github\.com/" + OWNER
                    + r"/(boring-[a-z-]+)/(?:blob|tree)/main/([^)#\s\"'>]*)(?:#([^)\s\"'>]+))?")
REPO_ANCHOR = re.compile(r"https://github\.com/" + OWNER + r"/([a-z0-9-]+)/?#([^)\s\"'>]+)")
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$", re.M)
EXPLICIT = re.compile(r'<a\s[^>]*(?:id|name)="([^"]+)"')
INLINE_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def github_slug(text: str) -> str:
    """GitHub's heading anchors: lower case, punctuation dropped, spaces to hyphens."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


@cache
def anchors(page: Path) -> frozenset[str]:
    """The anchors GitHub gives a Markdown page: its headings (a repeat gets -1, -2, ...)
    and explicit <a id/name>. Setext headings (underlined) are not used in our docs."""
    text = FENCE.sub("", page.read_text(encoding="utf-8", errors="replace"))
    seen: dict[str, int] = {}
    found = set(EXPLICIT.findall(text))
    for heading in HEADING.findall(text):
        slug = github_slug(INLINE_LINK.sub(r"\1", heading))
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        found.add(slug if count == 0 else f"{slug}-{count}")
    return frozenset(a.lower() for a in found)


def anchor_hit(where: str, link: str, page: Path, anchor: str | None) -> list[str]:
    if not anchor or page.suffix != ".md" or not page.is_file():
        return []
    if anchor.lower() in anchors(page):
        return []
    return [f"{where}: {link} names no heading #{anchor} in {page.name}"]


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


def doc_link_hits(doc: Path, root: Path, where: str, checkouts: dict[str, Path]) -> list[str]:
    """One Markdown page's links: relative ones inside `root`, sibling ones into `checkouts`."""
    found = []
    text = FENCE.sub("", doc.read_text(encoding="utf-8", errors="replace"))
    for match in RELATIVE.finditer(text):
        path, _, anchor = match.group(1).partition("#")
        target = (doc.parent / path).resolve()
        if not target.is_relative_to(root.resolve()):
            found.append(f"{where}: {match.group(1)} points into another repository; "
                         f"link https://github.com/{OWNER}/<repo>/blob/main/<path>")
        elif not target.exists():
            found.append(f"{where}: {match.group(1)} does not exist")
        else:
            found += anchor_hit(where, match.group(1), target, anchor)
    for match in SAME_PAGE.finditer(text):
        found += anchor_hit(where, "#" + match.group(1), doc, match.group(1))
    for match in GITHUB.finditer(text):
        sibling, path, anchor = match.group(1), match.group(2).rstrip("/"), match.group(3)
        base = checkouts.get(sibling)
        if base is None or path.split("/")[0] == "pond" or not (base / path).exists():
            found.append(f"{where}: {match.group(0)} has no target in {sibling}")
        else:
            found += anchor_hit(where, match.group(0), base / path, anchor)
    for match in REPO_ANCHOR.finditer(text):
        base = checkouts.get(match.group(1))
        if base is not None:  # a repository we have no checkout of is not checked here
            found += anchor_hit(where, match.group(0), base / "README.md", match.group(2))
    return found


def link_hits(repo: Path, checkouts: dict[str, Path] | None = None) -> list[str]:
    checkouts = checkouts if checkouts is not None else {n: FAMILY / n for n in REPOS}
    found = []
    for rel in tracked_docs(repo):
        if rel.endswith(".md"):
            found += doc_link_hits(repo / rel, repo, f"{repo.name}/{rel}", checkouts)
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


RELEASE_ROWS = {"CROCODILE": r"\| Crocodile \|[^\n]*?`v([0-9.]+)`",
                "PIRATES": r"\| Pirates \|[^\n]*?`v([0-9.]+)`",
                "CANVAS": r"`canvas-v([0-9.]+)`"}
PINNED = re.compile(r"\b(V|CROCODILE|PIRATES|CANVAS)=([0-9][0-9.]*)\b")


def release_set_hits(repo: Path) -> list[str]:
    """Versions pinned in boring-pond's blocks that differ from docs/updating.md's release set table."""
    table = repo / "docs" / "updating.md"
    if repo.name != "boring-pond" or not table.exists():
        return []
    text = table.read_text(encoding="utf-8")
    tested = {}
    for name, rx in RELEASE_ROWS.items():
        m = re.search(rx, text)
        if not m:
            return [f"{repo.name}/docs/updating.md: no {name.lower()} version in the release set table"]
        tested[name] = m.group(1)
    tested["V"] = tested["CROCODILE"]
    found = []
    for rel in tracked_docs(repo):
        if not rel.endswith(".md"):
            continue
        for n, line in enumerate((repo / rel).read_text(encoding="utf-8").splitlines(), 1):
            for name, version in PINNED.findall(line):
                if version != tested[name]:
                    found.append(f"{repo.name}/{rel}:{n}: {name}={version}, the release set says {tested[name]}")
    return found


SERVICE_LABELS = {"canvas": "Canvas", "knowledge": "Knowledge", "fishmarket": "Fishmarket",
                  "sourcecache-d365": "Sourcecache", "mcp-ferry": "Ferry"}
SERVICE_PIN = re.compile(r"\bV=([0-9][0-9.]*) S=([a-z0-9-]+)\b")


def services_set_hits(repo: Path) -> list[str]:
    """boring-services' blocks (`V=X S=NAME`) against the release set sentence in boring-pond's updating.md."""
    table = FAMILY / "boring-pond" / "docs" / "updating.md"
    if repo.name != "boring-services" or not table.exists():
        return []
    text = " ".join(table.read_text(encoding="utf-8").split())
    found = []
    for rel in tracked_docs(repo):
        if not rel.endswith(".md"):
            continue
        for n, line in enumerate((repo / rel).read_text(encoding="utf-8").splitlines(), 1):
            for version, name in SERVICE_PIN.findall(line):
                label = SERVICE_LABELS.get(name)
                m = re.search(rf"\b{label} ([0-9][0-9.]*[0-9])", text) if label else None
                if not m:
                    found.append(f"{repo.name}/{rel}:{n}: no {name} version in boring-pond's release set")
                elif version != m.group(1):
                    found.append(f"{repo.name}/{rel}:{n}: {name} {version}, the release set says {m.group(1)}")
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Product docs: no pond/ paths, every link and anchor resolves.")
    parser.add_argument("repos", nargs="*", metavar="REPO")
    parser.add_argument("--with", dest="extra", action="append", default=[], metavar="NAME=PATH",
                        help="another checkout links may point into (not checked itself)")
    parser.add_argument("--doc", action="append", default=[], type=Path, metavar="FILE",
                        help="one more Markdown page to check the links of")
    args = parser.parse_args(argv)
    names = args.repos or REPOS
    checkouts = {n: FAMILY / n for n in REPOS}
    for item in args.extra:
        name, sep, path = item.partition("=")
        if not sep or not name:
            parser.error(f"--with wants NAME=PATH, not {item!r}")
        checkouts[name] = Path(path).expanduser()
    missing = [n for n in names if not (FAMILY / n / ".git").exists()]
    missing += [f"{n}={p}" for n, p in checkouts.items() if n not in REPOS and not p.is_dir()]
    missing += [str(d) for d in args.doc if not d.is_file()]
    if missing:
        print("missing checkouts: " + ", ".join(missing), file=sys.stderr)
        return 2
    found = [h for n in names for h in hits(FAMILY / n)]
    links = [h for n in names for h in link_hits(FAMILY / n, checkouts)]
    links += [h for d in args.doc for h in doc_link_hits(d, d.parent, str(d), checkouts)]
    long = [h for n in names for h in status_hits(FAMILY / n)]
    pins = [h for n in names for h in release_set_hits(FAMILY / n) + services_set_hits(FAMILY / n)]
    for h in found + links + long + pins:
        print(h)
    print(f"docs: {len(found)} path(s) into pond/" if found else "docs: no path into pond/")
    print(f"docs: {len(links)} broken or cross-repository link(s)" if links else "docs: every link resolves")
    print(f"docs: {len(long)} STATUS page(s) too long" if long else
          f"docs: every STATUS page within {STATUS_MAX_LINES} lines")
    print(f"docs: {len(pins)} pinned version(s) off the release set" if pins else
          "docs: pinned versions match the release set")
    return 1 if found or links or long or pins else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
