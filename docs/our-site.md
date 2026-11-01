# Our site

The [example site](example-site.md) is invented. This page is the real one:
the installation the family was written in and runs on, with its real names.
It is a map, not a template. Where we set something up our own way rather
than as the docs describe, it is marked **★ Custom** with the reason, so you
can tell what to copy and what to leave. The versions are the current
release set ([releases and versions](updating.md#releases-and-versions)).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="our-site-dark.svg">
  <img alt="Our site. Chat clients (Claude, ChatGPT; Wald, a coworker, a friend) reach Caddy on ubahn (Core i7-7600U, 32 GB, a USB 3 SSD taped to the lid), which forwards to the Crocodile, which serves five Ponds: pond, otter, tim, brog (a coworker's) and pondering-toad (a friend's). From the Ponds: GitHub through a bot account, the Crocodile's own mailbox, the funkturm Zigbee host over SSH, the Pirates Mademoiselle Em (calls the Mistral API) and Captain Watt (calls Ollama on the desktop's RTX 4070 over the LAN), the test VM ubuntu-sim, Ferry, and the services Canvas, Knowledge, Fishmarket and Sourcecache. Ferry fronts the ha-mcp and nextcloud-mcp servers, which reach Home Assistant and Nextcloud. On Wald's Windows 11 desktop (Ryzen 7 7800X3D, 32 GB, RTX 4070) a Hyper-V D365 development VM runs the pondNT servers, used by Copilot in Visual Studio locally and by the Pond through an SSH tunnel the VM dials. Starred, dashed boxes are set up our own way." src="our-site.svg">
</picture>

## How we use it

Wald talks to the Crocodile from Claude and ChatGPT, on the desktop or the
phone. The Crocodile does the engineering: this family, the mailstack, the
host's own tooling. It reads and edits in its home, runs tests on `ubuntu-sim`,
and hands Wald every root step as a block he reads and runs himself. Otter
works beside it as developer and second reviewer; a finding from one is
checked by the other before it counts.

The Pirates take the side jobs. Mademoiselle Em draws first drafts of
diagrams and gives second opinions from a different model family. Captain
Watt runs on Wald's own GPU, so experiments that would cost API money go to
him first.

TIM is the D365 Pond: it researches, writes specifications and reviews,
reads the indexed D365 source in Sourcecache, and drives the development VM
through pondNT. On that same VM, Wald uses Copilot in Visual Studio with the
same pondNT servers while he codes.

The services are where the Ponds meet. Canvas holds the drawings Wald and the
Ponds work on together, Knowledge the notebook every Pond can read and the
Crocodile curates, Fishmarket the files that go to and come from people.
Through Ferry, `tim` changes the house in Home Assistant and `pond` looks
things up there and in the family's shared recipes in Nextcloud.

Brog and the Pondering Toad belong to other people, a coworker and a friend.
They sign in to their own Pond and cannot open the others' homes. What any
Pond puts into a shared service (Knowledge, Canvas) or hands to a Pirate is
shared with whoever else uses that service or Pirate.

## The host

`ubahn`, a home server: Ubuntu 26.04 LTS on an Intel Core i7-7600U (two
cores, four threads) with 32 GB of RAM, and a USB 3 SSD taped to the lid. It also runs mail, Nextcloud, Home Assistant and other things that have
nothing to do with the Pond, mostly in Docker. Wald works there as his own
user with sudo; every deploy below is a command he reads and runs.

Next to it on the home LAN: Wald's Windows 11 desktop (Ryzen 7 7800X3D, 32 GB,
RTX 4070), which hosts the D365 VM and Ollama, and `funkturm`, an ODROID-C4 with
Armbian that carries the Zigbee radio for Home Assistant.

**★ Custom: older than the installer.** Updates run exactly as on any
site: each part's release and its `deploy`, Crocodile, Pirates and services
alike ([updating](updating.md)). What differs is the start: the site and its
five Ponds existed before the setup commands did, so setup never created
them. A one-time normalisation brought every unit to what setup renders
today, with the site's own settings in drop-ins, so the site check sees a
regular site. What it lacks are setup's receipts, the record setup writes of
each account and folder it creates; uninstall deletes data only where a
receipt says setup made it, so here it would leave the Ponds' data alone.
*Why:* the Crocodile ran here before there was an installer; rebuilding a
working host to collect receipts would have bought nothing.

## The front door

One public name, `crocodile.walds.domain`, behind Caddy. Caddy runs in
Docker and owns ports 80 and 443 for every site on the host.

**★ Custom: the Crocodile listens on the LAN address.** It listens on the
host's LAN address, port 18503, not on 127.0.0.1 as
[getting started](getting-started.md#5-your-reverse-proxy) recommends, and a
narrow firewall rule lets only the proxy reach it. *Why:* Caddy runs in a
container, and a container cannot reach the host's loopback.

| Path on `crocodile.walds.domain` | Goes to |
|---|---|
| `/mcp/POND` and the sign-in paths | the Crocodile |
| `/introspect`, `/services/register` | the Crocodile, only from the service containers' networks; from outside, 404 |
| `/canvas/*`, `/services/canvas/mcp` | Canvas |
| `/services/knowledge/mcp` | Knowledge |
| `/services/sourcecache-d365/mcp` | Sourcecache |
| `/fishmarket/*` | Fishmarket |
| `/services/homeassistant/mcp`, `/services/nextcloud/mcp` | Ferry, in front of Home Assistant's and Nextcloud's MCP servers |

Every MCP path also has its `/.well-known/oauth-protected-resource/...`
route. The Caddyfile lives in its own repository and reaches the host only
by being copied and reloaded.

## The Ponds

Five Ponds on one Crocodile, each its own Unix account and handbook:

| Pond | Account | Who | Works on |
|---|---|---|---|
| `pond` | `boring-crocodile` | The Boring Crocodile `<^==>` | engineering: this family, the mailstack, the host's own tooling |
| `otter` | `methodical-otter` | The Methodical Otter | development and QA beside the Crocodile |
| `brog` | `brog` | The Unassuming Brog | a coworker's Pond: general collaboration and office work; started empty |
| `tim` | `tim` | The Inquisitive Mudskipper, TIM | D365 research, specifications and reviews |
| `pondering-toad` | `pondering-toad` | The Pondering Toad `(@_@)` | a friend's Pond: research, an indoor garden and its automation, Home Assistant, philosophy; its handbook is German |

The Consultant's sample handbook is modelled on how TIM works.

The Crocodile is used from Claude and from ChatGPT, where it began; Wald's
Claude account also carries the connectors for Otter and TIM. Each connector
belongs to one Pond, and the Crocodile's handbook tells it never to call
another Pond's tools that happen to be in the same chat.

**★ Custom: four members read each other's folders.** Homes are closed to
each other, with one deliberate exception: a Unix group shared by the
Crocodile, Otter, Mademoiselle Em and Wald lets its members read selected
handbook and work folders of each other. Nobody can write another's files;
each clones what it needs into its own home. *Why:* Otter reviews the
Crocodile's work and Em draws from its sources, and both should read the
original rather than a copy pasted into a chat. Wald is in the group so he
can read along from his own account without sudo. Brog, TIM and the Toad
stay out: their Ponds hold other people's or a customer's work.

## The Pirates

| Pirate | Account | Inference | Flavours | Serves |
|---|---|---|---|---|
| Mademoiselle Em | `mademoiselle-em` | Mistral's API | active: `default` (Mistral Small) and three diagram flavours (Medium, Large) | `pond`, `otter`, `tim` |
| Captain Watt | `pirate-watt` | Ollama on Wald's desktop (GPU: RTX 4070), OpenAI-compatible | active: `gemma`, `gemma-diagrams`, `lab` (Gemma 4 12B) | `pond`, `tim` |

Both execute on `ubahn` as their own accounts; only the model calls leave
the host, to Mistral or to the desktop next door. Em costs API money, Watt
costs electricity.

**★ Custom: Watt's model calls are plain HTTP on the LAN.** *Why:* the GPU is
in the desktop, not in the server, and the calls never leave the home
network. The price: Watt only works while the desktop is on, and anyone on
the LAN could talk to that Ollama.

## The services

Canvas, Knowledge, Fishmarket, Sourcecache and Ferry run as Docker stacks
under `/opt/docker/boring-SERVICE`, each with its own account; their state
lives there too, so the nightly backup captures it with the stack.

`service_list` in `pond` shows ten services: canvas, knowledge, fishmarket,
sourcecache-d365, the two Ferry routes (homeassistant, nextcloud) and four
`devbox` services from Windows.

**★ Custom: Ferry in front of other people's MCP servers.** Home Assistant's
and Nextcloud's MCP servers each run as their own container with one
credential of their own. Ferry puts the Crocodile's sign-in in front of them
and decides per Pond: in Home Assistant `tim` may write and `pond` only read;
Nextcloud is read-only for both and goes through a Nextcloud user, `pond-mcp`,
that sees only what Wald shares with it, the cookbook. *Why:* neither server
knows our Ponds. Without Ferry, every Pond would hold the same full
credential.

## The Windows side

pondNT runs on a D365 development VM (Hyper-V, 8 vCPU, 14 GB, D365 10.0.49)
on Wald's desktop, where Copilot in Visual Studio uses it directly. Through
the tunnel below, `pond` reaches `devbox` (core tools), `devbox-d365`,
`devbox-d365web` (browser automation) and `devbox-d365whsapp` (warehouse app
flows). Work machines in Azure have their own pondNT and are never reached
from here.

**★ Custom: the VM dials the Pond.** The VM opens an SSH connection out to
`ubahn` as the account `pondnt-tunnel`, which has no shell and may only hold
the forwards ([the tunnel](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/DEVBOX_TUNNEL.md)).
*Why:* the VM sits behind the desktop and opens no port to the network; the
connection is only there while someone on the desktop wants it. Closing the
tunnel's window cuts the Pond off.

## Other things the Pond uses

- **GitHub**, through a bot account that holds the family's public
  repositories. The Crocodile prepares; nothing is pushed, tagged or
  released without Wald's go.
- **Its own mailbox** on a mail host: the Crocodile reads and sends mail as
  itself, for reports and for talking to people, never as Wald.
- **★ Custom: `funkturm` over SSH.** The Pond administers the Zigbee host
  with an SSH key. *Why:* it is a small appliance with no MCP server of its
  own, and an SSH key the Pond holds is the simplest bounded way in.

## Updates and test machines

A candidate release is first installed and exercised on `ubuntu-sim`, an
Incus VM on `ubahn` with a site of its own: upgrade, rollback, forward
again. Throwaway VMs test journeys from a public release.
Then the Crocodile writes the rollout, one block per part, and Wald runs it
on `ubahn`: Crocodile first, then Pirates, then services, each deploy waiting
for the last ([updating](updating.md)). Each part keeps its previous release
for rollback. Nothing goes to GitHub without Wald's go.

## Backups

Every night at 03:00 a backup job stops one Docker stack at a time for a
cold, checksum-verified copy to a local backup disk, copies the homes and
system configuration live (SQLite through online snapshots), uploads the
result with Borg to off-site storage and mails a report. An isolated restore
of the whole host has not been demonstrated yet; until it has, the backup is
a strong hope with receipts.

## Next

Build your own from [getting started](getting-started.md); the
[example site](example-site.md) holds the names the docs use instead of ours.
