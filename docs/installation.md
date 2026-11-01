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

- A Linux host on **x86_64** with systemd and cgroup v2, sudo, and `python3`
  3.11 or newer (only to run the deploys; each part brings its own Python).
  Releases are built for linux-x86_64 only.
- **Memory.** Each Pond gets a memory ceiling, a cgroup limit on its worker
  and commands: setup proposes a quarter of the host's RAM, at least 512 MiB
  and at most 8 GiB, and you can set another. A ceiling reserves nothing; it
  stops one Pond from taking the host. Size the host for the Ponds busy at
  the same time, plus the services, Pirates and whatever else it runs. One
  data point, not a minimum: [our host](our-site.md) runs five Ponds, two
  Pirates and five service containers beside a full Home Assistant, a
  Nextcloud and other unrelated services, comfortably, on 32 GB.
- **Disk.** An installed Crocodile or Pirates release takes about 210 MB, and
  each keeps its previous release beside it; services add their Docker
  images. Then whatever the Ponds store.
- **Docker** only for services installed by their Linux deploy: Docker
  Engine with the Compose v2 plugin (Debian and Ubuntu: the packages
  `docker.io` and `docker-compose-v2`). The
  Crocodile and Pirates run as systemd units; services can also run
  [without Docker](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md#native-installation).
- **A domain with HTTPS** and your own reverse proxy in front of it. The
  Crocodile's public URL must be an HTTPS origin. Hosted clients (claude.ai,
  ChatGPT) connect from their providers' clouds, so the name must resolve on
  the internet and the certificate be publicly trusted. DNS, TLS, the proxy
  and the firewall stay yours; nothing here changes them.
- **The release artifacts** with their `.sha256` files: where to find them
  and the tested combination are in [updating](updating.md#releases-and-versions).
  Each part installs, updates and rolls back with its own
  `deploy`: [boring-deploy](https://github.com/the-boring-crocodile/boring-pond-common/blob/main/packages/boring-deploy/README.md).
- **Money, possibly.** Remote MCP connectors depend on the client's plan, and
  a Pirate's model calls are billed by its provider. A Pirate executes its
  tools locally, as its own account; its inference goes to the provider you
  configure: Mistral's API with an API key, or any OpenAI-compatible endpoint
  such as Ollama, on the same host, another machine of yours or remote
  ([providers](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#providers)).

## Decide first

- **Will the site have Pirates?** Enable guest reception with
  `service_registration_enabled` during activation, or later through
  `--site-render --guests POND`. The later change can interrupt running
  work; use the [planned site-render procedure](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#updating).
- **Which Ponds, for whom?** Each Pond is its own account and home: separate
  work and separate people get separate Ponds. Services and Pirates are
  granted to the Ponds that exist when they are added; a Pond added later is
  offered them in a second step.

## The order

1. **The Crocodile and its first Pond:** deploy, create the Pond, activate
   the site, connect a client
   ([boring-crocodile INSTALL](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md)). After
   this step an AI client can already work in the Pond.
   [Client setup](clients.md) covers registered IDs, VS Code configuration
   and version-specific OAuth observations.
2. **More Ponds** on the same Crocodile: `--add-pond`, then `--site-extend`
   (Crocodile INSTALL, [Adding to a running site](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#adding-to-a-running-site)).
3. **Services**, any of them: the Crocodile registers each one first
   (`boring-crocodile-admin service-add`), then the service's first deploy
   installs it ([boring-services](https://github.com/the-boring-crocodile/boring-services/blob/main/README.md#installing-on-linux)).
4. **Pirates**, one per provider instance: one deploy installs a Pirate and
   has the Crocodile admit it. Pirates and services are installed by their
   deploys, as root, which say what they do but take no digest
   ([boring-pirates](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#installing-a-pirate)).

## Your reverse proxy

It forwards the Crocodile's paths (sign-in, `/mcp/POND`, and two paths the
services use) and each service's own paths, unchanged, to the ports they
listen on: Crocodile INSTALL,
[The reverse proxy](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#the-reverse-proxy),
and the [services README](https://github.com/the-boring-crocodile/boring-services/blob/main/README.md#installing-on-linux).
Services reach the Crocodile through it as well, so the name must resolve and
TLS must be trusted from inside their containers.

The Crocodile and Canvas on one domain, as one complete Caddy site block
(Caddy 2.11's `caddy validate` accepts it; the ports are the defaults used on
these pages):

```caddy
crocodile-url.example.test {
    @crocodile path /mcp/* /.well-known/oauth-protected-resource/mcp/* /.well-known/oauth-authorization-server /authorize /token /revoke /register /approve /introspect /services/register
    handle @crocodile {
        reverse_proxy 127.0.0.1:8503
    }
    handle /canvas/* {
        reverse_proxy 127.0.0.1:18510
    }
    handle /services/canvas/mcp {
        reverse_proxy 127.0.0.1:18511
    }
    handle /.well-known/oauth-protected-resource/services/canvas/mcp {
        reverse_proxy 127.0.0.1:18511
    }
}
```

Another service adds its own `handle` blocks the same way: its MCP path and
that path's `/.well-known/oauth-protected-resource/...` metadata. Do not add a
catch-all `/services/*` rule that would take `/services/register` from the
Crocodile.

## Afterwards

- Bringing the site to a new release: [updating](updating.md).
- Running it, backing it up, taking a Pond out: Crocodile
  [OPERATIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md).
- How we use it day to day: [in practice](in-practice.md).

On Windows, pondNT gives Visual Studio's Copilot core and D365 tools, and the
services run natively: [boring-pondnt](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/README.md),
[service configuration](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md).

To try a Pond without touching your host: [Pond in a box](../box/README.md).
