# Development

The family has six repositories. Keep them side by side so the family runner
can resolve each component's frozen dependencies and check links between their
docs. A change still belongs to its owning repository; neighbouring checkouts
are not imported as live dependencies.

Clone them into one folder:

```bash
mkdir pond-family && cd pond-family
for r in boring-pond boring-pond-common boring-crocodile boring-pirates boring-services boring-pondnt; do
    git clone https://github.com/the-boring-crocodile/$r.git
done
```

You need Python 3.10 or newer (the code supports 3.10 to 3.14; only a
production deploy asks for 3.11), [uv](https://docs.astral.sh/uv/) and Git;
the diagrams also want Graphviz. The maintained checks create fresh environments.
They need access to the package index or a populated cache; native Windows,
systemd and browser acceptance still require their respective platforms.

## How the parts fit

[Pond Common](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/README.md)
is the shared ground, and it is consumed the careful way: never as a sibling
import, always as built wheels pinned by hash in each consumer's
`requirements.lock`. The Common commit those wheels come from is named in the
consumer's `.common-ref`, and Common's build is reproducible, so building
that commit yields exactly the locked hashes. CI relies on this: it checks
out Common at the ref, builds it, and the locks must match. The whole family
builds on one Common release: a new Common release means relocking every
consumer, and the family check refuses differing refs.

pondNT also records its bundled Services source in `.services-ref`. Its CI
and the family runner use that commit. When changing the bundled services,
select and test the Services commit with pondNT's locked Common wheels,
then update `.services-ref`. That Services commit names the same Common
release as pondNT itself.

Changing Common therefore goes in one order: edit Common, build its wheels
(`python boring-pond-common/scripts/build.py --out DIST`), then in each
affected consumer relock (`python scripts/lock.py --common-wheels DIST`) and
point `.common-ref` at the new Common commit. The family check below refuses
a ref that does not match the locks, so forgetting this is loud, not quiet.

## One check per repository

Each repository owns `scripts/check.py`. For an ordinary component change, the
family runner supplies that component's frozen dependencies:

```bash
python boring-pond/scripts/check.py --only pondnt
```

Use the relevant check name (`crocodile`, `pirates`, `services`, `pondnt` or
`common`). To run a consumer directly, from that consumer's repository root,
with deliberately prepared inputs:

```bash
python scripts/check.py --common-wheels /absolute/common-dist
# pondNT additionally requires --services-root /absolute/selected-services
```

That direct command is for Crocodile, Pirates, Services or pondNT. Common's
own `python scripts/check.py` builds and tests its packages; it does not take
`--common-wheels`.

Consumer checks install locked runtime dependencies into fresh environments
and test copies of tracked files. Test tools (pytest, mypy) come from the
repository's `requirements-dev.txt`, pinned by version: they never reach a
runtime. pondNT is the one exception: its tests ship in its tests bundle and
run on the target, so they install from a hash lock like the runtime. CI invokes these same owners, but a local
pass covers the interpreter, platform and selected tests that actually ran.
Skipped native checks and another CI platform remain separate evidence.

The whole family in one go:

```bash
python boring-pond/scripts/check.py
```

The runner validates the selected dependency refs, refuses differing Common
refs, builds that one Common commit once and supplies its wheels to every
consumer check. pondNT
receives a detached Services checkout at its recorded ref. Temporary worktrees
are removed on success or failure; sibling branches and existing distributions
stay unchanged. Common's own check still tests the current Common checkout.

It checks the runner, documents (every link resolves), licences (`reuse lint`
and package licence copies), dependency refs and, in the private
working copies, that no private name appears in any product tree, then runs the component
checks and prints one summary. Exit 0 means all of it passed. `--only` selects
checks. `--common-wheels DIST` uses an explicit distribution instead of
building; the consumers still enforce their wheel hashes.

The component checks run on the runner's own Python unless told otherwise.
`--python PY [PY ...]` runs each component check once per interpreter (the
family's own checks and the Common build use the first); `--ci-pythons` takes
the Pythons of the CI matrices, 3.14, 3.12 and 3.10, as `uv python find`
reports them. Run that before a release: a 3.14-only pass has missed a test
that hung on 3.12 and a real bug on 3.10.

```bash
python boring-pond/scripts/check.py --ci-pythons
```

For a documentation-only change, start with the document checks:

```bash
python boring-pond/scripts/check.py --only docs licences
```

Those check file links, private-record boundaries and licence consistency.
They do not prove that heading fragments resolve or that the pages read well;
inspect the rendered result too.

## Writing docs

- **One topic per page, every fact in one place.** Link instead of repeating.
  How deploy works is [boring-deploy](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md)'s;
  the whole Pond's install order is [installation](installation.md)'s.
- **One example site.** Every example uses [the example site](example-site.md);
  a page that shows commands or configuration says so once, near its first
  example.
- **Current behaviour only.** Product docs describe what the code does now,
  checked against the code. Plans, dated records and retired pages stay in
  our own records, which are never released.
- **Explain the choice:** the reader's problem, what this feature changes and
  what it enables. Put the trade-off beside the benefit; a smaller tool list
  or one shared runtime is a mechanism, not the reason to want it.
- **For a person reading it start to finish:** what it is, then how to do it,
  then the details. Pictures are drawn with
  [Boring Diagrams](../guides/boring-diagrams/README.md), the method behind
  every diagram in these docs.

README and licence content can become wheel metadata. Keep accepted artifacts
immutable after a documentation edit; a future rebuild needs a deliberately
selected source revision and release identity, not the old label on new bytes.

[CONTRIBUTING](https://github.com/the-boring-crocodile/boring-pond/blob/main/CONTRIBUTING.md)
has the short version of everything else: inbound = outbound licensing, run
the check for what you touched, and a pull request runs the same check again
in CI.
