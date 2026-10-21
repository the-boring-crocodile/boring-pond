# Installing a Pond

A whole Pond site on a Linux host, from nothing. This page is the order and
what to decide before you start; each part's own page has the commands. The
shortest way to two working Ponds, step by step with every command:
[getting started](getting-started.md).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="site-context-dark.svg">
  <img alt="A Pond site at a glance: you work with an AI client, which connects over MCP and sign-in through your reverse proxy to the Crocodile; the Crocodile hands each connection to its Pond, a Unix account; the Pond hands assignments to Pirates, local AI agents that register with it; the Pond and its Pirates call the services granted to them, and an AI client can also use a service directly through the proxy; services register with the Crocodile and have it check their tokens." src="site-context.svg">
</picture>

At the end you have the picture above: the **Crocodile**, the MCP server an
AI client connects to; one or more **Ponds**, each a Unix account with its
own files, commands and jobs; any of the **services** (Canvas, Knowledge,
Fishmarket, Sourcecache); and, if you want them, **Pirates**, local AI agents
a Pond can give work to. More in the [glossary](glossary.md).

All pages use one [example site](example-site.md): a Crocodile at
`crocodile-url.example.test` with the Ponds `pond` and `garden`, the service
`canvas` and the Pirate `parrot`. Read them in the order below and the story
runs through.

## What you need

- A Linux host with systemd and cgroup v2, sudo, and `python3` 3.11 or newer
  (only to run the deploys; each part brings its own Python).
- Docker, for the services.
- A domain, and your own reverse proxy in front of it with TLS. DNS, TLS, the
  proxy and the firewall stay yours; nothing here changes them.
- The release artifacts, from a trusted source with their published
  checksums. Each part installs, updates and rolls back with its own
  `deploy`: [boring-deploy](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md).
- For a Pirate: an API key of its model provider.

## Decide first

- **Will the site have Pirates?** A site with Pirates accepts guests
  (`service_registration_enabled` in its activation file), and that is
  chosen when the site is activated; a running site cannot be switched
  later.
- **Which Ponds, for whom?** Each Pond is its own account and home: separate
  work and separate people get separate Ponds. Services and Pirates are
  granted to the Ponds that exist when they are added; a Pond added later is
  offered them in a second step.

## The order

1. **The Crocodile and its first Pond:** deploy, create the Pond, activate
   the site, connect a client
   ([boring-crocodile INSTALL](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md)). After
   this step an AI client can already work in the Pond.
2. **More Ponds** on the same Crocodile: `--add-pond`, then `--site-extend`
   (Crocodile INSTALL, [Adding to a running site](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#adding-to-a-running-site)).
3. **Services**, any of them: the Crocodile registers each one first
   (`boring-crocodile-admin service-add`), then the service's first deploy
   installs it ([boring-services](https://github.com/the-boring-crocodile/boring-services/blob/main/README.md#installing-on-linux)).
4. **Pirates**, one per provider instance: one deploy installs a Pirate and
   has the Crocodile admit it
   ([boring-pirates](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#installing-a-pirate)).

## Your reverse proxy

It forwards the Crocodile's paths (sign-in, `/mcp/POND`, and two paths the
services use) and each service's own paths, unchanged, to the ports they
listen on: Crocodile INSTALL,
[The reverse proxy](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#the-reverse-proxy),
and the [services README](https://github.com/the-boring-crocodile/boring-services/blob/main/README.md#installing-on-linux).
Services reach the Crocodile through it as well, so the name must resolve and
TLS must be trusted from inside their containers.

## Afterwards

- Bringing the site to a new release: [updating](updating.md).
- Running it, backing it up, taking a Pond out: Crocodile
  [OPERATIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md).
- How we use it day to day: [in practice](in-practice.md).

On Windows, pondNT gives Visual Studio's Copilot core and D365 tools, and the
services run natively: [boring-pondnt](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/README.md),
[service configuration](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md).

To try a Pond without touching your host: [Pond in a box](../box/README.md).
