# Trust and boundaries

**A Pond is trusted like a person with an account on your host.** An AI
working in it can do whatever that Unix account can do, and nothing more. The family adds sign-in and checks in front of that account; it
does not add a sandbox inside it. This page says who is trusted with what,
what each credential opens, and what follows when something goes wrong.
[Architecture](architecture.md) shows the path of one command; the
Crocodile's [ARCHITECTURE](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/ARCHITECTURE.md)
lists every check on it.

## Who is trusted with what

| Who | Trusted to | Holds |
|---|---|---|
| **You**, the operator | everything: you are root, you run every `sudo` line | the approval secrets, root, the configuration |
| **An AI client** (Claude, ChatGPT, Copilot) and its vendor | act in one Pond on your behalf, and see what it reads there | an access token for that Pond |
| **A Pond** | its own files and commands, as its own Unix account | its home; the services and Pirates granted to it |
| **The Crocodile's controller** | check every request and route it to the right Pond | the sign-in store, enabled Ponds' approval secrets and a path to each enabled worker |
| **A worker** | run one Pond's operations as that Pond's account | nothing beyond that account |
| **A service** (Canvas, Knowledge, Fishmarket, Sourcecache) | its own data and its own caller policy | its data; credentials to ask the Crocodile whether a token is valid |
| **A Pirate** and its model provider | do assignments a Pond hands it, as its own account | its API key; what the assignment gives it |
| **Your reverse proxy** | terminate TLS and pass requests to 127.0.0.1 | your certificate |

Every frame in that list that has an account is a boundary the kernel
enforces. Setup creates each Pond's home owned by that Pond, mode 0700. Pond
accounts never join each other's private groups. The controller's generated
unit carries the enabled Ponds' groups in SupplementaryGroups; this does not
add the controller to their Unix membership lists. Pirate clients share one
site-wide `pirate-clients` group: it permits connections to Pirate sockets.
The Crocodile description's `[pirate_services.callers.NAME]` owns that
Pirate's `uid` and admitted `ponds`. Workers admit only the Pirate/Pond pair;
Pirates trust only accepted live registration sockets whose owner and peer
UID the configured controller vouches for. Socket removal or replacement
revokes trust; each request also checks current controller admission.
Separate Pirate accounts and work folders separate their files. Park saves
and removes pairs, bring-back restores them, and retirement drops them. Setup never adds a Pond to `docker` or `sudo`;
either would make it root in effect.

Every command runs in its own systemd unit with memory and task limits
(its time limit is the task runner's, which the worker asks for), and by default with `ProtectSystem=strict`, `/home` read-only apart
from the Pond's own tree, and `NoNewPrivileges`. A Pond you widen for host
administration (`no_new_privileges = false` plus a sudo grant) runs without
those restrictions; its limits stay. [PERMISSIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/PERMISSIONS.md)
says how to narrow or widen either.

"Read-only" stops writing, not reading. A Pond reads whatever its account may
read. The main `/etc/boring-crocodile/config.toml` is root:root 0644 and
contains no secrets. The `ponds/` directory is root:controller-group 0751:
workers may traverse it, while only the controller may list it. Each Pond's
directory and file are root:Pond-group 0750 and 0640. A worker reads its own
declaration; the controller reads the enabled set through its unit's groups.
Retirement seals a retained declaration root:root 0700/0600 before freeing its
identity. Later group or ACL changes can deliberately share the home; your
own home and other people's remain governed by their modes and ACLs. File
tools and commands default to umask 0027 for new files. MCP file roots
restrict file tools, while command reads also face
the task unit's mount and namespace policy. A readable host path can still
be hidden by that unit. Check with
`ls -ld /home/*` and `getfacl`; check a service's home and a Pirate's
configuration folder the same way. The approval secrets sit in
`/etc/boring-crocodile/credentials`, root's, mode 0700. To
show a Pond nothing but its own home, PERMISSIONS has the systemd lever
(`TemporaryFileSystem=/home` with `BindPaths=`).

A Pond has the network its account has: the internet, and your local network
too, including the router, the NAS and every service on it that does not ask
for a password. If that is more than you want, block it per Pond with
`IPAddressDeny=` and `IPAddressAllow=` ([PERMISSIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/PERMISSIONS.md)).
Render plans show root-owned drop-ins verbatim and flag settings that the
description also owns. Keep secrets in files referenced by `LoadCredential=`
and keep their contents out of drop-ins. There is no directive allow-list. Symlinks, masks
and unsafe files are refused. systemd owns precedence; site-check and status
compare effective task policy with the description and report a mismatch as
irregular/degraded. Render never rewrites or deletes external drop-ins.

The controller's listener is held by a root-owned systemd socket unit, so
restarting the controller keeps its port occupied. Pond and Pirate command
slices deny TCP binds to the controller port, the service ports
(18510–18519), Ferry ports (18520–18529) and tunnel ports (18530–18539) on
IPv4 and IPv6. Add custom loopback service ports to the root-owned site's
`server.protected_ports` and apply a site render before using them.
A service registered by its public URL and proxied to a custom loopback port
has bind protection in those slices only if the port is in `server.protected_ports`.
These rules require cgroup/BPF socket-bind support. An account outside the
Pond and Pirate slices can still bind a free port, including one protected
inside those slices. The operator owns the service listeners, routes and
other local accounts. Full site stops and upgrades from the old self-binding
controller follow the [update procedure](updating.md).

## What each credential opens

| Credential | Opens | Lives |
|---|---|---|
| A Pond's **approval secret** | lets a client sign in to that Pond (five wrong tries cancel that sign-in; the secret's length protects against guessing) | until you change it; root-only file |
| **Access token** | that one Pond's URL (`/mcp/POND`), nothing else | one hour |
| **Refresh token** | a new access token for the same Pond | 14 days, rotated on use |
| **Service-call token**, minted by the controller | one Pond calling one service | one hour, renewed by the controller with 15 minutes left; never valid as an access token |
| A pondNT **access key** | one pondNT server on 127.0.0.1 of one Windows machine | fixed 100-year expiry; retained on rerun; replaced only with explicit `-RotateKeys` |

Tokens are stored only as SHA-256 hashes. A token is bound to the resource it
was issued for, so a token for one Pond is refused by every other Pond and
every service. Details: the Crocodile's [OAUTH](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OAUTH.md).

## When something goes wrong

**The AI is talked into something by what it read.** A web page, a mail or a
file can carry instructions; an AI client may follow them. It can then do what
the Pond's account can do: read and change that Pond's files, run commands as
that account, use the services and Pirates granted to it. It cannot reach
other Ponds' homes, become root or widen its own grants. Keep secrets and
anything precious out of a Pond that reads untrusted content, and narrow such
a Pond further where you need to. The handbooks treat mail, web pages and
notes from other Ponds as data, never as orders; that helps, it is not a
guarantee.

**A token leaks.** The holder can act within that token's scope until it
expires or its grant is revoked. An access token lasts one hour; a refresh
token can obtain new access and rotates on use. Revoke the affected client's
grant promptly. To revoke every client's current grant in one Pond:

```bash
sudo boring-crocodile-admin oauth revoke --pond NAME --all-clients
sudo boring-crocodile-admin oauth revoke --pond NAME --all-clients --apply
```

The first command only shows a plan. The second shows the fresh scope and
waits for typed `APPLY` in a terminal. If the store changes during review,
run it again and review the new plan. Revocation
blocks further authenticated calls; it cannot undo work already dispatched.
For a single affected client use `--client ID` instead of `--all-clients`
([admin reference](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/ADMIN.md#oauth-commands)).

**An approval secret leaks.** Anyone who also reaches your sign-in page can
connect a client to that Pond. Open the approval page only from the client
you are connecting. Never approve from a link someone sent you. Replace the secret and revoke the Pond's
clients ([replacing an approval secret](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#replacing-an-approval-secret)).

**A Pond's account is compromised.** It is like a compromised user account
on the host: that Pond's files and whatever the account may do. Other Ponds
and root stay out of reach, as long as you have not widened the account.

**The controller is compromised.** It can act through every enabled worker
and read every enabled Pond's approval secret. Recover the controller,
replace every approval secret and revoke the affected grants. The controller
runs as its own account, its configuration is root-owned, and it checks
authentication before forwarding requests to a worker.

**A service is compromised.** It has what its account has: its data, its
configuration and the credentials in it, and whatever else that account may
read. On Windows core and the four D365 servers run with the installing
person's elevated token. The other services use the person's ordinary token. Tokens a Pond presents to it are valid only for that service, for an
hour. A service that signs people in itself (its own OAuth or access keys)
holds those sign-ins too: access tokens for an hour, keys until they expire.

**A Pirate misbehaves.** It acts as its own account with its own grants, and
whatever an assignment gives it goes to its model provider. Each worker checks
its kernel UID against the description's admitted Pirate/Pond pairs before
reading registration. Shared `pond-pirates` membership grants transport
access, not admission beyond that list. A forged worker acceptance cannot
replace the independent controller proof required by the Pirate.

## What leaves your machine

- What an AI client receives from a Pond is available to that client and its
  configured model provider. Hosted clients (Anthropic, OpenAI, Microsoft)
  handle it under their terms; a local client's destination follows its
  configuration.
- A Pirate sends assignments and the file/tool results it uses to its
  configured model provider. Its `view_image` sends the original image bytes,
  including embedded EXIF/GPS metadata. The Crocodile's `file_read_image`
  instead returns a pixel-only preview with metadata removed.
- To recognize Claude and ChatGPT, the Crocodile fetches their published
  client descriptions from `claude.ai` and `chatgpt.com` (configurable).
  The Crocodile itself performs no telemetry or update checks.
- Configured services contact the destinations needed by their tools:
  D365 tools contact the configured Entra and D365 endpoints; a D365Data DMF
  import sends package bytes to the storage destination supplied by D365.
  Ferry forwards requests to its configured backends, such as Nextcloud or
  Home Assistant. A file reference can travel directly from the Pond to a
  service without its bytes passing through the AI client.
- Knowledge and Canvas persist their local stores on the service host.
  Data returned to a requester follows that requester's client/provider path.
  The configured service and requested tool determine where bytes are sent.

## On Windows: pondNT

pondNT's servers listen on 127.0.0.1 only and each wants its own access key.
That keeps other machines out; it does not separate pondNT from the person at
the keyboard. Every normal service starts at the installing person's desktop
logon. Sourcecache, Knowledge, Canvas and Ferry use ordinary tokens. Core
and the four D365 servers request elevation. Normal services do not run as SYSTEM or start before
logon. The optional tunnel has its own window and separate server processes;
closing that window ends that process group.

Use a disposable development box. Give core keys only to trusted callers:
even its reader tools can read writer keys in the installing person's
profile. A program running as that person can read those keys and call
elevated core. UAC and reader keys do not isolate another program running
as the same person. Setup warns about writable or unchecked release paths
but never repairs their ACLs. On a shared machine, independently review
service identities and writable configuration before installing: [pondNT INSTALL](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md).

## Not goals

No sandbox inside a Pond, no per-command approval for `exec`, no root
through MCP (unless you give a Pond host administration on purpose:
[widening](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/PERMISSIONS.md#widening-host-administration-by-a-pond)),
no public multi-tenancy. A Pond site is for you and the people
and agents you give accounts to.
