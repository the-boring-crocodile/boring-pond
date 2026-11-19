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

Each part has its own releases page, with a Linux x86_64 archive and a
`.sha256` file beside it. Choose published artifacts there and read their
upgrade notes. The names follow these patterns:

| Part | Releases | Tag | Archive |
|---|---|---|---|
| Crocodile | [boring-crocodile](https://github.com/the-boring-crocodile/boring-crocodile/releases) | `vX.Y.Z` | `boring-crocodile-X.Y.Z-linux-x86_64.tar.gz` |
| Pirates | [boring-pirates](https://github.com/the-boring-crocodile/boring-pirates/releases) | `vX.Y.Z` | `boring-pirates-X.Y.Z-linux-x86_64.tar.gz` |
| Services | [boring-services](https://github.com/the-boring-crocodile/boring-services/releases) | `SERVICE-vX.Y.Z` | `boring-SERVICE-X.Y.Z-linux-x86_64.tar.gz` |
| Common | [boring-pond-common](https://github.com/the-boring-crocodile/boring-pond-common/releases) | `vX.Y.Z` | wheels and `SHA256SUMS`; for development only |

The services' tag names are `canvas`, `knowledge`, `fishmarket`,
`sourcecache-d365` and `mcp-ferry`. A Linux site never installs Common by
hand: each archive carries the Common packages it was built with, pinned by
hash in its `requirements.lock`.

The 0.5 family release set pairs Common 0.8.0, Crocodile 0.5.0 and Pirates
0.4.0 with Canvas and Knowledge 0.3.0, Fishmarket, Sourcecache and MCP Ferry
0.2.0, Boring Tunnel 0.1.0 and pondNT 0.3.0. Read each selected release's
notes and requirements before updating.

Earlier published combinations and their evidence are recorded below.

| Recorded combination | Common | Scope of evidence |
|---|---|---|
| Crocodile 0.4.21 + Pirates 0.3.11 + Canvas 0.2.20, Knowledge 0.2.16, Fishmarket 0.1.15, Sourcecache 0.1.19, Ferry 0.1.5 | 0.7.13 | Linux deploy smoke/registration and provider calls; each component's CHANGELOG describes its release |
| pondNT 0.2.10 + the preceding row's service versions | 0.7.13 | Native Windows suites, installer journey and live D365 checks of its last candidate, which differs only in version numbers; see pondNT's [evidence](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/EVIDENCE.md) |

These are recorded combinations, not a requirement to give every part the
same version number. pondNT's Services pin is its `.services-ref`, not the
latest Services main branch.
Dependency ranges describe compatibility; the release lock pins the actual
packages. Each part's CHANGELOG says what an upgrade needs from the others.
Deploy's `--check` refuses incompatible installed components and data it can
inspect. Keep the guide matched to the release you selected.

`sha256sum -c` against the `.sha256` file catches a damaged download. It does
not authenticate the archive's origin, since both come from the same page.
Any independent provenance verification is a separate step.

## Choose the configuration path first

Inspect the installed Crocodile version and the main description before
running the deployment sequence:

| Current description | Path |
|---|---|
| Main config has a `site` table and per-Pond files | Normal preflight and deployment below |
| Published 0.4.21 single file with `environments`, without `site` | [Stopped-site adoption](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#adopting-a-pre-description-site) |
| Another legacy or customized layout | Stop and review the release's supported inputs; do not force the importer |

Description adoption hands the existing store to the controller's normal
[transactional schema-5-to-6 startup upgrade](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OAUTH.md#schema-and-backup).
Existing callers become readers; clients, credentials and tokens are retained.
Take the matching stopped snapshot first. After adoption, run each
`service-grants` preview printed by the Services check. It suggests the old
role only for callers present in both the legacy list and the Crocodile's
membership. A caller present in just one list needs an explicit decision. If
any differ, the check leaves the complete command for the operator to assemble
after reviewing every difference. Preview the resulting complete caller map,
run the same command with `--apply` and type `APPLY`. Decide any custom author
aliases before replacing the old access block. Verify that an
intended reader can read and an intended writer can perform a harmless write.

For the loopback bind protection update, pause Pond and Pirate work and
close tunnel windows while updating the Crocodile and Pirates. Add any custom loopback
service ports to `server.protected_ports`, then preview and apply the
Crocodile site render. Run `boring-crocodile-admin site-check` and run
`deploy --check` for each installed tunnel instance before reopening work.
The default tunnel ports are 18530–18539. To change a tunnel port in this
release, remove the installed tunnel and install it again with the new port.
Use the new installation's handoff for the Windows forward.

The importer supports the published 0.4.21 format. For that path, the
component procedure owns the dry-run, private stopped snapshot, conversion,
deployment, render and checks. Reserve the window for the compatible
Crocodile/Pirates pair. Keep the old artifact and matching snapshot.

Crossing adoption also changes the way back: use
[matching-snapshot recovery](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#way-back-across-adoption),
with consumers stopped. The printed runtime rollback command alone does
not restore the legacy description. After the component procedure has checked
the adopted Crocodile/Pirates pair, return at
[Post-adoption resume: Services](#post-adoption-resume-services); those two
runtime updates are already complete.

## 1. Unpack each artifact as root

Read the releases' compatibility and data-change notes before scheduling
the interruption. Then download each artifact on the host, check it, and
unpack it, as root, into a folder only root can write. The example uses
Crocodile 0.5.0, Pirates 0.4.0 and Canvas 0.3.0. Run this and the next two
steps in the same shell.

    CROCODILE=0.5.0 PIRATES=0.4.0 CANVAS=0.3.0
    (
        set -eu
        gh=https://github.com/the-boring-crocodile
        get() { curl -fLO "$1" && curl -fLO "$1.sha256" && sha256sum -c "${1##*/}.sha256"; }
        mkdir -p ~/Downloads
        cd ~/Downloads
        get $gh/boring-crocodile/releases/download/v$CROCODILE/boring-crocodile-$CROCODILE-linux-x86_64.tar.gz
        get $gh/boring-pirates/releases/download/v$PIRATES/boring-pirates-$PIRATES-linux-x86_64.tar.gz
        get $gh/boring-services/releases/download/canvas-v$CANVAS/boring-canvas-$CANVAS-linux-x86_64.tar.gz
        sudo mkdir -p /root/releases
        for f in boring-crocodile-$CROCODILE boring-pirates-$PIRATES boring-canvas-$CANVAS; do
            sudo tar xzf $f-linux-x86_64.tar.gz -C /root/releases
        done
    )

`get` downloads one archive and its checksum file and checks it; each must
print OK, and if one does not, nothing is unpacked. Each parenthesised block
stops at its first failed command, including an extraction inside the loop.
Proceed to the next block only after the previous block succeeds.

The unpacked folder is code that runs as root. Use the artifact, not a folder
a build left behind. The components need not share a version number.

## 2. Check the runtime pair before changing it

Run the read-only preflight for the Crocodile first. Pirates 0.4 requires
Crocodile 0.5, so its check refuses until the Crocodile is updated; it runs in
step 3, between the two deploys. Services have their own
backup/edit/check/deploy sequence below: older services reject the new proxy
key, so their edit belongs immediately before their update.

    sudo /root/releases/boring-crocodile-$CROCODILE/deploy --check

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

Crocodile 0.5 and Pirates 0.4 must be updated together in one maintenance
window. Keep Pirate work stopped until both updates complete; there is no
supported mixed-version window. When the releases' requirements allow it,
update the Crocodile first: Pirates register with it and service checks reach
it, so their checks then see the new controller.

    (
        set -eu
        sudo /root/releases/boring-crocodile-$CROCODILE/deploy
        sudo /root/releases/boring-pirates-$PIRATES/deploy --check
        sudo /root/releases/boring-pirates-$PIRATES/deploy
    )

Wait for each deploy to finish successfully before starting the next. For a
running installation, that includes its start and smoke checks. An intentionally
stopped installation stays stopped: `site is stopped: not started` records
an installed release without runtime acceptance. Verify it when you next
start it. A failed deploy stops the round; later parts stay on their old release.

Deploy updates the runtime; it does not render host policy. Once both runtimes
match, preview `sudo boring-crocodile-setup --site-render`. If generated units
or permissions need updating, run `sudo boring-crocodile-setup --site-render --apply`,
review the plan and type APPLY. Applying also repairs the runtime and restarts
the controller and enabled workers. Keep an intentionally stopped site stopped
until its paired update is complete; its start procedure owns the running intent.

If Crocodile succeeds and Pirates fails, keep Pirate work stopped and leave
Canvas and later parts untouched. Inspect the failed step and the Pirates
release's Upgrade notes, fix the cause, then rerun Pirates' `deploy --check`
and its deploy. Continue with Canvas only after Pirates succeeds. If Pirates
cannot be recovered, keep both sides stopped while choosing recovery.
After adoption, restore the matching legacy snapshot and runtime through the
component procedure above. Without a description conversion, follow the
runtime rollback limits below. Resume Pirate work only with a compatible pair.

### Post-adoption resume: Services

Resume here after the component adoption procedure has completed and checked
the Crocodile/Pirates pair. Normal updates continue here after that pair's
deploys. Keep the selected service version in `CANVAS`. If its archive is not
yet unpacked, use step 1's Canvas download/check/extraction lines only (in the
extraction loop, select only `boring-canvas-$CANVAS`), then return here.

For Canvas, find the actual HOME and make a private configuration recovery
copy before editing. Choose a new recovery directory; an existing one stops
this block so a retry cannot overwrite the earlier backup:

```bash
SERVICE_HOME=$(python3 -c 'import json; print(json.load(open("/etc/boring-pond/homes.json"))["boring-canvas"])')
RECOVERY=/root/canvas-before-update
(
    set -eu
    test -n "$SERVICE_HOME"
    sudo mkdir -m 0700 "$RECOVERY"
    sudo cp -a "$SERVICE_HOME/config" "$RECOVERY/config"
    sudo cp -p "$SERVICE_HOME/compose.yaml" "$RECOVERY/compose.yaml"
)
```

Repeat the procedure for each service using its recorded HOME and a distinct
recovery directory. For Ferry, include every selected backend/gateway service
JSON; explicitly copy any referenced file outside HOME/config too.

Before changing an existing installation, review its settings against the
selected release's [configuration contract](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md).
Keep the service stopped while changing formats. Select exactly one
authentication mode. In Crocodile mode, use one authority/credential block;
the Crocodile grant now owns caller roles. Do not guess roles from old
membership lists or replace an existing service secret by re-registering it.
Let the Crocodile's normal startup complete its transactional store upgrade first.

For container runs, remove JSON bind/port/behind_proxy. Review the existing
compose.yaml against the release template: Compose supplies
BORING_SERVICE_LISTENERS for each selected absolute config path. The deploy
accepts loopback publications, or no publications plus a boring.proxy-network
label naming an attached network; a public publication is refused. Existing
Compose files are operator-owned and are not rewritten by deploy.
Ferry needs a listener entry for every selected frontend. Canvas has one
listener: remove its old browser port/flags and route MCP, metadata and browser
paths to that listener; its resource URL determines the browser path prefix.
Preserve ownership/modes and private credentials. Then run:

```bash
(
    set -eu
    sudo /root/releases/boring-canvas-$CANVAS/deploy "$SERVICE_HOME" --check
    sudo /root/releases/boring-canvas-$CANVAS/deploy "$SERVICE_HOME"
)
```

After each service, make an authenticated call through the Pond. If the
update began with that service stopped, deploy leaves it stopped: explicitly
start the reviewed Compose stack before the runtime check. Keep the recovery
copy until the update is accepted. A configuration-only change may require
a restart even when the image is unchanged; the candidate's source-file
preflight is separate from proving the running container uses it.

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

When reversing the adopted Crocodile/Pirates pair, follow the matching-snapshot
recovery above. Services updated in that window also need the service rollback
steps below. Inspect where each deploy stopped.
A failure before the switch leaves
the old release selected; a failure after it needs recovery of the changed
component. Do not automatically deploy `previous` after every refusal.

A completed deploy prints its rollback command, for example:

    sudo /opt/boring-crocodile/previous/deploy /opt/boring-crocodile

If reversing several completed updates, work backwards through the components
you changed, respecting their version and data compatibility. Only one previous
release is kept per part.

Rollback changes code, not data or work the agents performed. On a
data-generation change, interactive deploy asks about a backup. A scripted
deploy must pass `--backup` to take one, or `--no-backup` when you already took
the reviewed stopped-site snapshot. That backup and any restoration are
separate from switching code. Follow the
[rollback guide](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md#rollback)
and the component's recovery instructions. The engine refuses an incompatible
downgrade rather than making old code read newer data.

### Before rolling a service back

Use the service HOME and private recovery directory from its update. Stop
the candidate service first. Before the old release's preflight, restore its
matching configuration, Compose listener/exposure settings and any changed
external credentials or proxy routes. The old release cannot read the new
authentication/container-listener format. For the Canvas example:

```bash
sudo cp -p "$RECOVERY/config/config.json" "$SERVICE_HOME/config/config.json"
sudo cp -p "$RECOVERY/compose.yaml" "$SERVICE_HOME/compose.yaml"
```

Restore every edited Ferry frontend too, including external files preserved
separately. The reverse edit must precede the old release's preflight, as
must the environment-file preparation below.

A service deployer built on Common before 0.8 rewrites `.env` as 0644.
Before invoking it, keep HOME inaccessible to unrelated local accounts and
record its original directory permissions. Save any operator `.env` outside
HOME in a new private recovery subdirectory:

```bash
(
    set -eu
    sudo mkdir -m 0700 "$RECOVERY/old-deploy"
    sudo cp -p "$SERVICE_HOME/.env" "$RECOVERY/old-deploy/operator.env"
)
```

Skip the copy only if no operator `.env` exists. Set the new
`boring-image.env` aside in that recovery directory for the old runtime.
Run the old deployer's check and deploy. If it rewrote `.env`, retain its
exact `BORING_IMAGE=` line privately before restoring the operator file with
`sudo cp -p "$RECOVERY/old-deploy/operator.env" "$SERVICE_HOME/.env"`, including
after a failed deploy. Put that retained image line back in the restored file
without changing its private mode; the old runtime needs its image choice in
`.env`. Without an earlier operator file, keep the image-only `.env` the
old deployer creates. Do not let the newer `boring-image.env` override it. If the attempt stops
before the image switch and you retain the newer runtime, restore its saved
`boring-image.env` before using it again.

Check the selected old image, the restored owner/mode and an authenticated
service call before declaring recovery complete. Restore HOME's original
directory permissions only after the private file is restored. A failed
attempt still needs that permission restoration; a backup alone does not
protect a 0644 live copy.

## pondNT on Windows

pondNT updates with the new release's `setup.ps1`. Setup reads the selection
and Sourcecache index from recognized person/logon tasks. For the published
0.2.10 SYSTEM/cmd layout, record the complete service selection and existing
index before removing legacy registrations, then pass both explicitly to the
preview and apply commands. Setup generates the fixed gateway from the
selected services. Operator configs and bearers persist; `-RotateKeys`
explicitly replaces keys. Keep the old release and task definitions for rollback.
[Update, and back](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md#10-update-and-back)
is the recipe, step by step.
