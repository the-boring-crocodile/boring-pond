# Development

The family is six repositories that expect to live side by side in one
folder:

```bash
mkdir pond-family && cd pond-family
for r in boring-pond boring-pond-common boring-crocodile boring-pirates boring-services boring-pondnt; do
    git clone https://github.com/the-boring-crocodile/$r.git
done
```

You need Python 3.10 or newer (the code supports 3.10 to 3.14; only a
production deploy asks for 3.11), [uv](https://docs.astral.sh/uv/) and Git;
the diagrams also want Graphviz. Everything else the checks build for themselves,
fresh, every time.

## How the parts fit

[Pond Common](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/README.md)
is the shared ground, and it is consumed the careful way: never as a sibling
import, always as built wheels pinned by hash in each consumer's
`requirements.lock`. The Common commit those wheels come from is named in the
consumer's `.common-ref`, and Common's build is reproducible, so building
that commit yields exactly the locked hashes. CI relies on this: it checks
out Common at the ref, builds it, and the locks must match.

Changing Common therefore goes in one order: edit Common, build its wheels
(`python boring-pond-common/scripts/build.py --out DIST`), then in each
affected consumer relock (`python scripts/lock.py --common-wheels DIST`) and
point `.common-ref` at the new Common commit. The family check below refuses
a ref that does not match the locks, so forgetting this is loud, not quiet.

## One check per repository

Every repository answers one question the same way:

```bash
python scripts/check.py --common-wheels DIST     # boring-pondnt also wants --services-root ../boring-services
```

It builds a fresh virtual environment from the hash lock, installs the
repository from a copy of its tracked files, and runs the tests there. It is
exactly what CI runs, so green here means green there.

The whole family in one go:

```bash
python boring-pond/scripts/check.py --common-wheels DIST
```

That starts with the documents (no page points into records we do not
publish, every link resolves), the licences (`reuse lint`, and every package
carries its licence files), and the Common refs, then runs each repository's
own check and prints one summary. Exit 0 means all of it passed.

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
- **For a person reading it start to finish:** what it is, then how to do it,
  then the details. Pictures are drawn with
  [Boring Diagrams](../guides/boring-diagrams/README.md), the method behind
  every diagram in these docs.

[CONTRIBUTING](https://github.com/the-boring-crocodile/boring-pond/blob/main/CONTRIBUTING.md)
has the short version of everything else: inbound = outbound licensing, run
the check for what you touched, and a pull request runs the same check again
in CI.
