# Installation and task map

Start with one Pond and one client. Add the other parts when the work needs
them. Each linked page owns its procedure.

| Task | Guide |
|---|---|
| Install the Crocodile and first Pond | [Getting started](getting-started.md) |
| Let the AI prepare later operations | [Operating together](operating-together.md) |
| Add another Pond | [Add a Pond](add-pond.md) |
| Add a Pirate | [Add a Pirate](add-pirate.md) |
| Install one service | [Install one service](install-service.md) |
| Give an existing service to another Pond | [Add a service later](add-service.md) |
| Update, adopt a legacy site, or recover | [Updating](updating.md) |
| Park or retire a Pond | [Park or retire](retire-pond.md) |
| Try the system container | [Pond in a box](../box/README.md) |
| Install on a Windows development machine | [pondNT](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md) |

## What you need

The Linux Crocodile and Pirates need x86_64, glibc 2.39 or newer, systemd,
cgroup v2 and Python 3.12 or newer for deploy. Their runtimes carry Python.
A human holds sudo. Ponds get dedicated accounts and homes.

Hosted clients need a public HTTPS origin. You own DNS, TLS, proxy routes
and firewall policy. Services need their own routes too, and their
containers must reach and trust the configured issuer.

Docker Engine and Compose v2 are needed for the Linux service deploys and
for the box. Native service configuration is also available in
[Services](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md#native-installation).
No service or model provider is required for the first Pond.

A Pond's memory ceiling covers its worker and commands together, without
reserving RAM. Size the host for concurrent work; retain disk space for
archives, previous runtimes and data. Model calls may cost money or need
local inference resources.

Use the [example site](example-site.md) for names, the
[trust page](trust.md) for boundaries, and the task page for the next change.
