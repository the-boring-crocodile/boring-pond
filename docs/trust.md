# Trust and boundaries

The short version: **a Pond is trusted like a person with an account on your
host.** An AI working in it can do whatever that Unix account can do, and
nothing more. The family adds sign-in and checks in front of that account; it
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
| **The Crocodile's controller** | check every request and route it to the right Pond | the sign-in store; a path to every Pond's worker |
| **A worker** | run one Pond's operations as that Pond's account | nothing beyond that account |
| **A service** (Canvas, Knowledge, Fishmarket, Sourcecache) | its own data and its own caller policy | its data; credentials to ask the Crocodile whether a token is valid |
| **A Pirate** and its model provider | do assignments a Pond hands it, as its own account | its API key; what the assignment gives it |
| **Your reverse proxy** | terminate TLS and pass requests to 127.0.0.1 | your certificate |

Every frame in that list that has an account is a boundary the kernel
enforces. Setup creates each Pond's home owned by that Pond, mode 0700. Pond
accounts never join each other's groups; only the controller joins every
Pond's group. One exception you make yourself: a Pirate that serves several
Ponds puts each of their workers into its client group, so those Ponds share
that group; give each Pond its own Pirate where they must stay apart. Setup
never adds a Pond to `docker` or `sudo`; either would make it root in effect.

Every command runs in its own systemd unit with memory, task and time
limits, and by default with `ProtectSystem=strict`, `/home` read-only apart
from the Pond's own tree, and `NoNewPrivileges`. A Pond you widen for host
administration (`no_new_privileges = false` plus a sudo grant) runs without
those restrictions; its limits stay. [PERMISSIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/PERMISSIONS.md)
says how to narrow or widen either.

A Pond has the network its account has: the internet, and your local network
too, including the router, the NAS and every service on it that does not ask
for a password. If that is more than you want, block it per Pond with
`IPAddressDeny=` and `IPAddressAllow=` ([PERMISSIONS](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/PERMISSIONS.md)).

## What each credential opens

| Credential | Opens | Lives |
|---|---|---|
| A Pond's **approval secret** | lets a client sign in to that Pond (five wrong tries end the attempt) | until you change it; root-only file |
| **Access token** | that one Pond's URL (`/mcp/POND`), nothing else | one hour |
| **Refresh token** | a new access token for the same Pond | 14 days, rotated on use |
| **Service-call token**, minted by the controller | one Pond calling one service | 300 seconds; never valid as an access token |
| A pondNT **access key** | one pondNT server on 127.0.0.1 of one Windows machine | a year, renewed by setup |

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

**A token leaks.** The holder has that one Pond for up to an hour, or for 14
days with the refresh token. `boring-crocodile-admin oauth revoke --pond NAME
--all-clients` ends that at once.

**An approval secret leaks.** Anyone who also reaches your sign-in page can
connect a client to that Pond. Replace the secret and revoke the Pond's
clients ([replacing an approval secret](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#replacing-an-approval-secret)).

**A Pond's account is compromised.** It is like a compromised user account
on the host: that Pond's files and whatever the account may do. Other Ponds
and root stay out of reach, as long as you have not widened the account.

**The controller is compromised.** Then every Pond is: the controller can
reach every worker. That is why it runs as its own account, its configuration
is root-owned, and no request reaches a worker before it is authenticated and
checked.

**A service is compromised.** It has what its account has: its data, its
configuration and the credentials in it, and whatever else that account may
read; on Windows the general services run as SYSTEM, which is the whole
machine. Tokens a Pond presents to it are valid only for that service, for 300
seconds. A service that signs people in itself (its own OAuth or access keys)
holds those sign-ins too: access tokens for an hour, keys until they expire.

**A Pirate misbehaves.** It acts as its own account with its own grants, and
whatever an assignment gives it goes to its model provider.

## What leaves your machine

- Everything an AI client reads or writes in a Pond goes to that client's
  vendor (Anthropic, OpenAI, Microsoft), under the terms you have with them.
- A Pirate's assignments go to its model provider (for example Mistral).
- To recognize Claude and ChatGPT, the Crocodile fetches their published
  client descriptions from `claude.ai` and `chatgpt.com` (configurable).
- Nothing else: no telemetry, no update checks. Services keep their data
  on your host.

## On Windows: pondNT

pondNT's servers listen on 127.0.0.1 only and each wants its own access key.
That keeps other machines out; it does not separate pondNT from the person at
the keyboard. The core and the D365 server run as that person, elevated (the
D365 tools need administrator rights), and the general services run as SYSTEM.
pondNT is meant for a single-developer, disposable development box. On a
shared machine, set the services up separately with a reviewed service
account: [pondNT INSTALL](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md).

## Not goals

No sandbox inside a Pond, no per-command approval for `exec`, no root
through MCP, no public multi-tenancy. A Pond site is for you and the people
and agents you give accounts to.
