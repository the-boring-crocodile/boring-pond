# Updating a site

A site has several independently running parts. Updating them one at a time
makes it clear which change failed and what needs recovery. This guide covers
the Linux Crocodile, Pirates and Services; [pondNT on Windows](#pondnt-on-windows)
uses its own installer.

Each Linux release has its own `deploy`. The shared
[deployment guide](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md)
explains that command's checks, switch and rollback. This page is the order
around them, using the [example site](example-site.md): the Crocodile, the
Pirate `parrot` and the service `canvas`.

## Releases and versions

Each part is released on its own repository's releases page, with one
archive for linux-x86_64 and a `.sha256` file beside it:

| Part | Releases | Tag | Archive |
|---|---|---|---|
| Crocodile | [boring-crocodile](https://github.com/the-boring-crocodile/boring-crocodile/releases) | `v0.4.20` | `boring-crocodile-0.4.20-linux-x86_64.tar.gz` |
| Pirates | [boring-pirates](https://github.com/the-boring-crocodile/boring-pirates/releases) | `v0.3.10` | `boring-pirates-0.3.10-linux-x86_64.tar.gz` |
| Services | [boring-services](https://github.com/the-boring-crocodile/boring-services/releases) | `SERVICE-vX.Y.Z`, e.g. `canvas-v0.2.19` | `boring-SERVICE-X.Y.Z-linux-x86_64.tar.gz`, e.g. `boring-canvas-0.2.19-linux-x86_64.tar.gz` |
| Common | [boring-pond-common](https://github.com/the-boring-crocodile/boring-pond-common/releases) | `v0.7.11` | wheels and `SHA256SUMS`; for development only |

The services' tag names are `canvas`, `knowledge`, `fishmarket`,
`sourcecache-d365` and `mcp-ferry`. A Linux site never installs Common by
hand: each archive carries the Common packages it was built with, pinned by
hash in its `requirements.lock`.

The current release set, run together on our own host: Crocodile 0.4.20,
Pirates 0.3.10, Canvas 0.2.19, Knowledge 0.2.15, Fishmarket 0.1.14,
Sourcecache 0.1.18 and Ferry 0.1.4, all built on Common 0.7.11; pondNT 0.2.9
on the Windows VM (its tunnel to the Pond still runs 0.2.8). That is a tested combination, not a rule: the parts need not
share a version number. Nothing checks a combination for you; each part's
CHANGELOG says what an upgrade needs from the others, and its deploy's
`--check` refuses what it can see on the host itself (old configuration
keys, a missing account).

`sha256sum -c` against the `.sha256` file catches a damaged download. It does
not prove who built the archive, since both come from the same page. The
releases carry no signatures or GitHub artifact attestations yet.

## 1. Unpack each artifact as root

Read the releases' compatibility and data-change notes before scheduling
the interruption. Then download each artifact on the host, check it, and
unpack it, as root, into a folder only root can write. Set the three
versions (here the tested set above); run this and the next two steps in the
same shell:

    CROCODILE=0.4.20 PIRATES=0.3.10 CANVAS=0.2.19
    gh=https://github.com/the-boring-crocodile
    get() { curl -fLO "$1" && curl -fLO "$1.sha256" && sha256sum -c "${1##*/}.sha256"; }
    mkdir -p ~/Downloads && cd ~/Downloads
    get $gh/boring-crocodile/releases/download/v$CROCODILE/boring-crocodile-$CROCODILE-linux-x86_64.tar.gz &&
    get $gh/boring-pirates/releases/download/v$PIRATES/boring-pirates-$PIRATES-linux-x86_64.tar.gz &&
    get $gh/boring-services/releases/download/canvas-v$CANVAS/boring-canvas-$CANVAS-linux-x86_64.tar.gz &&
    sudo mkdir -p /root/releases &&
    for f in boring-crocodile-$CROCODILE boring-pirates-$PIRATES boring-canvas-$CANVAS; do
        sudo tar xzf $f-linux-x86_64.tar.gz -C /root/releases
    done

`get` downloads one archive and its checksum file and checks it; each must
print OK, and if one does not, nothing is unpacked.

The unpacked folder is code that runs as root. Use the artifact, not a folder
a build left behind. The components need not share a version number.

## 2. Check everything before changing anything

Run the read-only preflight for every part first:

    sudo /root/releases/boring-crocodile-$CROCODILE/deploy --check
    sudo /root/releases/boring-pirates-$PIRATES/deploy --check
    sudo /root/releases/boring-canvas-$CANVAS/deploy --check

Without a HOME argument a deploy uses the part's line in
`/etc/boring-pond/homes.json`, which its first install wrote.

This checks the artifact and host, including required installed components
and data compatibility. It does not prepare the new release, run its
component check or prove it will start. Those checks follow during deploy,
with the component check before the switch.

Resolve each refusal before proceeding. If a release requires another
component to be updated first, follow that declared order and repeat the
dependent preflight after the prerequisite update. Do not bypass a version
or data-compatibility refusal.

## 3. Deploy one part at a time

When the releases' requirements allow it, update the Crocodile first:
Pirates register with it and service checks reach it, so their checks then
see the new controller.

    sudo /root/releases/boring-crocodile-$CROCODILE/deploy
    sudo /root/releases/boring-pirates-$PIRATES/deploy
    sudo /root/releases/boring-canvas-$CANVAS/deploy

Wait for each deploy to finish successfully before starting the next. For a
running installation, that includes its start and smoke checks. An intentionally
stopped installation stays stopped: `site is stopped: not started` records
an installed release without runtime acceptance. Verify it when you next
start it. A failed deploy stops the round; later parts stay on their old release.

What people notice when running components restart:

- **Crocodile:** connections drop. The controller can spend up to 90 seconds
  draining connections before stopping; this is not a bound on the whole
  outage or client reconnection. Running commands end and their jobs are
  listed as `interrupted`; nothing replays them
  ([Operations](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#updating)).
- **Pirates:** running Pirate services restart and their in-flight assignments
  fail. Inspect the retained result before resubmitting work.
- **A service:** its container restarts. Follow the service's guide for any
  work or browser session affected.

## 4. Rolling back

First inspect where the deploy stopped. A failure before the switch leaves
the old release selected; a failure after it needs recovery of the changed
component. Do not automatically deploy `previous` after every refusal.

A completed deploy prints its rollback command, for example:

    sudo /opt/boring-crocodile/previous/deploy /opt/boring-crocodile

If reversing several completed updates, work backwards through the components
you changed, respecting their version and data compatibility. Only one previous
release is kept per part.

Rollback changes code, not data or work the agents performed. A data-format
change prompts for a backup during deploy; that backup and any restoration
are separate from switching code. Follow the
[rollback guide](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md#rollback)
and the component's recovery instructions. The engine refuses an incompatible
downgrade rather than making old code read newer data.

## pondNT on Windows

pondNT updates with its release's `setup.ps1`, run over the old installation
with the complete service selection; going back is the old release's setup
run the same way.
[Update, and back](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md#10-update-and-back)
is the recipe, step by step.
