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

## 1. Unpack each artifact as root

Copy the artifacts to the host and check them against the release's
checksums. Read their compatibility and data-change notes before scheduling
the interruption. Then unpack each, as root, into a folder only root can write:

    sudo mkdir -p /root/releases
    sudo tar xzf boring-crocodile-VERSION-linux-x86_64.tar.gz -C /root/releases
    sudo tar xzf boring-pirates-VERSION-linux-x86_64.tar.gz -C /root/releases
    sudo tar xzf boring-canvas-VERSION-linux-x86_64.tar.gz -C /root/releases

The unpacked folder is code that runs as root. Use the artifact, not a folder
a build left behind. Replace each `VERSION` below with that component's
release version; the components need not share a version number.

## 2. Check everything before changing anything

Run the read-only preflight for every part first:

    sudo /root/releases/boring-crocodile-VERSION/deploy --check
    sudo /root/releases/boring-pirates-VERSION/deploy --check
    sudo /root/releases/boring-canvas-VERSION/deploy --check

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

    sudo /root/releases/boring-crocodile-VERSION/deploy
    sudo /root/releases/boring-pirates-VERSION/deploy
    sudo /root/releases/boring-canvas-VERSION/deploy

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

pondNT updates with its release's `setup.ps1`. Preview the intended services
and Ferry layout before applying; retain the complete service selection on
an existing installation. Follow
[INSTALL](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md)
for task ownership, client configuration and recovery.
