# Our site

We build the Pond from inside a Pond. Several workspaces share a Linux host;
each has its own Unix account, home and handbook. AI clients reach them through
a TLS reverse proxy and the Crocodile.

An engineering Pond writes code and keeps project records. A second workspace
reviews changes. Other Ponds handle research and application work. Shared
services hold notebooks, drawings, source indexes and file transfers; each
service decides what its callers may use.

Pirates take assignments under their own Unix accounts. Some call an external
model provider; others call a local model. An assignment and its tool results
go to the configured provider.

A Windows development machine runs pondNT. Its local client uses those tools
directly. An optional SSH tunnel exposes separate server copies to the Linux
side while its window is open. Ferry fronts selected external MCP services.

We exercise installation and recovery on disposable machines before updating
the working site. The human holds root and runs the reviewed privileged steps.

Use the [architecture](architecture.md) for the request path,
the [example site](example-site.md) for invented installation names, and
[getting started](getting-started.md) to build your own.
