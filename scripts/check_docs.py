#!/usr/bin/env python3
"""Product docs name nothing in our own records.

    python scripts/check_docs.py [REPO ...] [--with NAME=PATH ...] [--doc FILE ...]

Our own records live in the private checkout `boring-records` beside the
products (until 2026-11-07 each repository's `pond/` folder), never released.
A published page that links or points there leads nowhere, so this fails on
any `pond/...` path (a link written before the move) in a tracked Markdown or
SVG file. `boring-pond/` and URL paths such as `/mcp/pond/` are not matches.

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

The pinned download examples must match the documented family release set.
Generic examples may use placeholders. Literal versioned download URLs are
flagged so the archive and tag come from the same checked variables.
Dated release evidence in prose is allowed. Diagram captions describe the view
and source without release numbers.

Literal Unicode escape sequences in Markdown are flagged, including inside
code blocks; write the intended character instead of an accidentally pasted escape.

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
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[2]
REPOS = ["boring-pond", "boring-pond-common", "boring-crocodile", "boring-pirates",
         "boring-services", "boring-pondnt"]
PRIVATE = re.compile(r"(?<![\w/.-])pond/")
UNICODE_ESCAPE = re.compile(r"\\u[0-9a-fA-F]{4}")
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


def markdown_escape_hits(doc: Path, where: str) -> list[str]:
    return [f"{where}:{number}: literal Unicode escape in Markdown: {line.strip()[:160]}"
            for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1)
            if UNICODE_ESCAPE.search(line)]


def unicode_hits(repo: Path) -> list[str]:
    return [hit for rel in tracked_docs(repo) if rel.endswith(".md")
            for hit in markdown_escape_hits(repo / rel, f"{repo.name}/{rel}")]


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
    """The repository's private STATUS page, when the records checkout sits beside it."""
    status = repo.parent / "boring-records" / repo.name / "STATUS.md"
    if not status.exists():
        return []
    lines = len(status.read_text(encoding="utf-8").splitlines())
    if lines > STATUS_MAX_LINES:
        return [f"boring-records/{repo.name}/STATUS.md: {lines} lines, at most {STATUS_MAX_LINES}: "
                f"a current-state page; move dated text to boring-records/{repo.name}/history/STATUS_HISTORY.md"]
    return []


# Keep these pins at the published release when source versions advance.
RELEASES = {
    "crocodile": "0.5.0", "pirates": "0.4.0", "pondnt": "0.3.0",
    "canvas": "0.3.0", "knowledge": "0.3.0", "fishmarket": "0.2.0",
    "sourcecache-d365": "0.2.0", "mcp-ferry": "0.2.0",
}
RECIPE_COMPONENTS = {
    ("boring-pond", "docs/getting-started.md"): "crocodile",
    ("boring-pond", "docs/add-pirate.md"): "pirates",
    ("boring-pond", "docs/install-service.md"): "knowledge",
    ("boring-pond", "box/README.md"): "crocodile",
    ("boring-pirates", "README.md"): "pirates",
    ("boring-pondnt", "docs/INSTALL.md"): "pondnt",
}
VERSION = r"\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)"
RELEASE_PIN = re.compile(r"(?<!\w)(\$v|\$tag|V|CROCODILE|PIRATES|CANVAS)\s*=\s*['\"]?(v?" + VERSION + ")")
SERVICE_NAME = re.compile(r"\bS=([a-z0-9-]+)\b")
DOWNLOAD_PIN = re.compile(r"releases/download/(?:[a-z0-9-]+-)?v?" + VERSION)
RELEASE_NUMBER = re.compile(r"(?<![\w.])v?" + VERSION + r"(?![\w.])")


def release_pin_hits(repo: Path) -> list[str]:
    """Check the stable release versions and tag spelling in download recipes."""
    found = []
    for rel in tracked_docs(repo):
        if not rel.endswith(".md"):
            continue
        for number, line in enumerate((repo / rel).read_text(encoding="utf-8").splitlines(), 1):
            where = f"{repo.name}/{rel}:{number}"
            if DOWNLOAD_PIN.search(line):
                found.append(f"{where}: hard-coded release number; use a version placeholder")
            for variable, value in RELEASE_PIN.findall(line):
                component = RECIPE_COMPONENTS.get((repo.name, rel))
                if (repo.name, rel) == ("boring-pond", "docs/updating.md") and variable.isupper():
                    component = variable.lower()
                if (repo.name, rel) == ("boring-services", "README.md"):
                    service = SERVICE_NAME.search(line)
                    component = service[1] if service else None
                expected = RELEASES.get(component) if component else None
                if expected is None:
                    found.append(f"{where}: hard-coded release number; use a version placeholder")
                else:
                    expected = "v" + expected if variable == "$tag" else expected
                    if value != expected:
                        found.append(f"{where}: {variable}={value}, the release set says {expected}")
    return found


def diagram_version_hits(repo: Path) -> list[str]:
    """Product diagram captions describe their source/view without release numbers."""
    found = []
    for rel in tracked_docs(repo):
        if not rel.endswith(".svg"):
            continue
        where = f"{repo.name}/{rel}"
        try:
            svg = ET.parse(repo / rel)
        except (OSError, ET.ParseError) as error:
            found.append(f"{where}: cannot read diagram: {error}")
            continue
        texts = list(svg.iter("{http://www.w3.org/2000/svg}text"))
        caption = " ".join("".join(t.itertext()) for t in texts[:3])
        if RELEASE_NUMBER.search(caption):
            found.append(f"{where}: release number in diagram caption")
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
    escapes = [h for n in names for h in unicode_hits(FAMILY / n)]
    escapes += [h for d in args.doc for h in markdown_escape_hits(d, str(d))]
    long = [h for n in names for h in status_hits(FAMILY / n)]
    pins = [h for n in names for h in release_pin_hits(FAMILY / n)]
    diagrams = [h for n in names for h in diagram_version_hits(FAMILY / n)]
    for h in found + links + escapes + long + pins + diagrams:
        print(h)
    print(f"docs: {len(found)} path(s) into pond/" if found else "docs: no path into pond/")
    print(f"docs: {len(links)} broken or cross-repository link(s)" if links else "docs: every link resolves")
    print(f"docs: {len(long)} STATUS page(s) too long" if long else
          f"docs: every STATUS page within {STATUS_MAX_LINES} lines")
    print(f"docs: {len(pins)} invalid release pin(s)" if pins else
          "docs: download pins match the release set")
    print(f"docs: {len(diagrams)} diagram caption problem(s)" if diagrams else
          "docs: diagram captions have no release numbers")
    print(f"docs: {len(escapes)} line(s) with literal Unicode escapes" if escapes else
          "docs: no literal Unicode escapes in Markdown")
    return 1 if found or links or escapes or long or pins or diagrams else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
