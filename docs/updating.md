# Updating a site

How to bring a whole site to a new family release, and back. Each part has
its own release artifact and updates with its own `deploy`; how one deploy
works, step by step, is [boring-deploy](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md).
This page is the order around them. Examples use the
[example site](example-site.md): the Crocodile, the Pirate `parrot` and the
service `canvas`.

## 1. Unpack each artifact as root

Copy the artifacts to the host and check them against the release's
checksums. Then unpack each, as root, into a folder only root can write:

    sudo mkdir -p /root/releases
    sudo tar xzf boring-crocodile-VERSION-linux-x86_64.tar.gz -C /root/releases
    sudo tar xzf boring-pirates-VERSION-linux-x86_64.tar.gz -C /root/releases
    sudo tar xzf boring-canvas-VERSION-linux-x86_64.tar.gz -C /root/releases

The unpacked folder is code that runs as root. Use the artifact, not a folder
a build left behind.

## 2. Check everything before changing anything

`deploy --check` is read-only. Run it for every part first:

    cd /root/releases
    sudo ./boring-crocodile-VERSION/deploy --check
    sudo ./boring-pirates-VERSION/deploy --check
    sudo ./boring-canvas-VERSION/deploy --check

Without a HOME argument a deploy uses the part's line in
`/etc/boring-pond/homes.json`, which its first install wrote. Go on only when
every check passes.

## 3. Deploy one part at a time

    sudo ./boring-crocodile-VERSION/deploy
    sudo ./boring-pirates-VERSION/deploy
    sudo ./boring-canvas-VERSION/deploy

Start each only when the one before says `is live`. A deploy that fails stops
the round: the parts after it stay on their old release.

The releases do not require an order. We deploy the Crocodile first because
the Pirates register with it and each service's check reaches it, so their
checks then see the new one.

What people notice while it runs:

- **Crocodile:** connections drop for up to a minute and a half, then clients
  reconnect; running commands end and their jobs are listed as `interrupted`
  ([OPERATIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#updating)).
- **Pirates:** each Pirate restarts; its running assignments fail.
- **A service:** a short restart of its container.

## 4. Rolling back

Each deploy prints its own rollback command when it finishes, for example:

    sudo /opt/boring-crocodile/previous/deploy /opt/boring-crocodile

Roll back in the reverse order, starting with the part that failed or was
deployed last. Only one previous release is kept per part. Data is not
rolled back: a part whose data format changed asks for a backup during its
deploy ([boring-deploy](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md#rollback)).

## pondNT on Windows

pondNT updates on its own, with its release's `setup.ps1`:
[INSTALL](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md).
