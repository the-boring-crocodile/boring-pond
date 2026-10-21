# Pond in a box (prototype)

Try the Pond without installing it on your host: an Ubuntu system container
with systemd as init, the Pond's homes on a volume, and the components deployed
inside with their own release artifacts, exactly as on a host. AI clients
still reach it from outside, so it needs your domain and a reverse proxy with
TLS in front, as on a host. A native install remains the way to run a Pond
for real.

## Build and start

    docker build -t pond-box box/
    docker run -d -t --name pond --hostname pond \
        --cgroupns=private --cap-add SYS_ADMIN \
        --security-opt apparmor=unconfined --security-opt seccomp=unconfined \
        --tmpfs /run --tmpfs /run/lock \
        -v pond-home:/home -p 127.0.0.1:8503:8503 pond-box

Why these options: the Crocodile runs every command as the Pond's own account
in its own systemd unit and cgroup, with a private /tmp and a read-only system
(`ProtectSystem=`). That needs systemd as PID 1 with a writable cgroup subtree
(`--cgroupns=private`: only the container's own tree; the image remounts it
writable) and mount namespaces (CAP_SYS_ADMIN, which Docker's default AppArmor
and seccomp profiles block). This is far less than `--privileged` (no host
devices, no other capabilities, the host's cgroup tree stays out of reach),
but it is not a hardened sandbox: treat the box like a VM you trust, not like
an application container.

## Install the Crocodile inside

    docker cp boring-crocodile-VERSION-linux-x86_64.tar.gz pond:/releases/
    docker exec pond sh -c 'cd /releases && tar xzf boring-crocodile-*.tar.gz \
        && mkdir /opt/boring-crocodile && ./boring-crocodile-*/deploy --no-backup'
    docker exec -it pond /opt/boring-crocodile/current/bin/boring-crocodile-setup --wizard --apply
    docker exec -it pond /opt/boring-crocodile/current/bin/boring-crocodile-setup --site-wizard --apply

Then the rest of the Crocodile's `docs/INSTALL.md` from step 4 (check and connect), with `docker exec pond`
in front of each command. The site listens on the published loopback port;
a reverse proxy with TLS in front of it is the operator's, as on a host.
Updates are the same deploy with the next artifact.
