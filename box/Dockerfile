# Pond in a box: an Ubuntu system container with systemd as init. The Pond's
# components are deployed inside with their own release artifacts, exactly as
# on a host. Prototype; see README.md.
FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus sudo ca-certificates \
      passwd adduser procps less python3 \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && systemctl mask systemd-udevd.service systemd-udevd-kernel.socket systemd-udevd-control.socket \
      systemd-modules-load.service sys-kernel-config.mount sys-kernel-debug.mount \
      getty.target console-getty.service systemd-firstboot.service \
 && mkdir -p /releases

# Docker mounts the container's own cgroup tree read-only; systemd (and the
# Crocodile's per-command cgroups) need it writable. With --cgroupns=private
# this is only the container's subtree.
STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/bin/sh", "-c", "mount -o remount,rw /sys/fs/cgroup && exec /sbin/init"]
