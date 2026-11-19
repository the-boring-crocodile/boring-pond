# Pond in a box

Run the Crocodile inside an Ubuntu system container, with systemd starting
its workers and tasks. Use a disposable Docker host: this is a way to try
the installation, not a boundary for untrusted code.

The container shares the host kernel. It needs SYS_ADMIN, unconfined
AppArmor/seccomp and a writable private cgroup tree. A dedicated VM contains
the experiment. For an ordinary lasting installation, use
[Getting started](../docs/getting-started.md).

## Build and start

From this repository's root, on the disposable host:

```bash
sudo docker build -t pond-box box/
sudo docker run -d -t --name pond --hostname pond \
    --cgroupns=private --cap-add SYS_ADMIN \
    --security-opt apparmor=unconfined --security-opt seccomp=unconfined \
    --tmpfs /run --tmpfs /run/lock \
    -v pond-home:/home -p 127.0.0.1:8503:8503 pond-box
sudo docker exec pond systemctl is-system-running
```

The image remounts its cgroup subtree writable before starting systemd.
The box uses ordinary group modes; no ACL package is needed.
Inspect a failed unit before continuing if systemd reports degraded.

## Install one Pond inside

Download the Crocodile 0.5.0 archive and its checksum from its
[release page](https://github.com/the-boring-crocodile/boring-crocodile/releases).
Verify the checksum and read that release's instructions. In the directory
holding the verified archive, run the following block.

```bash
(
    set -eu
    V=0.5.0
    f=boring-crocodile-$V-linux-x86_64.tar.gz
    sudo docker cp "$f" pond:/releases/
    sudo docker exec pond sh -c "cd /releases && tar xzf $f && install -d -m 0755 /opt/boring-crocodile && ./boring-crocodile-$V/deploy --no-backup"
)
sudo docker exec -it pond /opt/boring-crocodile/current/bin/boring-crocodile-setup --wizard --apply
sudo docker exec -it pond /opt/boring-crocodile/current/bin/boring-crocodile-setup --site-wizard --apply
```

Choose one dedicated account and a packaged handbook. At site activation,
enter your HTTPS public origin and **0.0.0.0** for the local bind address.
Docker forwards the published port to the container's network address;
binding only its loopback would make that route fail. Keep port 8503.
Review each plan and type APPLY.

## Check and connect

```bash
sudo docker exec pond /opt/boring-crocodile/current/bin/boring-crocodile-admin site-check
sudo docker exec pond /opt/boring-crocodile/current/bin/boring-crocodile-admin status --check
```

Your host's reverse proxy forwards the Crocodile paths to the published
loopback port. The [proxy section](../docs/getting-started.md#4-connect-the-reverse-proxy)
owns that configuration; the [client page](../docs/clients.md) owns sign-in.
Hosted clients still need reachable HTTPS. Read the approval secret in a
private administrator terminal inside the box, not in chat.

Connect a fresh client to `https://YOUR-DOMAIN/mcp/pond`, bootstrap, and
ask it to run `id -un; pwd`. Check the intended account and home.
A local health report does not test the public proxy or client.

## Keep or remove it

Only `/home` is on the named volume. The runtime, site configuration,
approval secrets and OAuth store are in the container's writable layer.
Removing the container loses those even if the home volume remains.
Preserve the whole site before treating any work there as valuable.

Stop it with `sudo docker stop pond`. When finished, the human may remove
the container and then the `pond-home` volume after inspecting what each
holds. Return to the [task map](../docs/installation.md) for the next step.
