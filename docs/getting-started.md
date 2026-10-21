# Getting started: an Engineer and a Consultant

From nothing to two working Ponds on one Linux host: the Engineer for
engineering and the Consultant for research and concepts, connected to
Claude and ChatGPT. About an hour once the domain and the proxy work, most
of it reading. Their handbooks have
characters of their own, the Steady Beaver and the Tidy Kingfisher, and the
examples are named after them (`beaver-user`, `kingfisher`).
The examples use the [example site](example-site.md): put your own domain and
names where these appear.

What you will have at the end:

| Pond | URL | Account | Handbook |
|---|---|---|---|
| `pond` (the first Pond is always called `pond`) | `https://crocodile-url.example.test/mcp/pond` | `beaver-user` | [the Steady Beaver](../handbooks/steady-beaver/HANDBOOK.md) |
| `kingfisher` | `https://crocodile-url.example.test/mcp/kingfisher` | `kingfisher-user` | [the Tidy Kingfisher](../handbooks/tidy-kingfisher/HANDBOOK.md) |

## What you need

- A Linux host on x86_64 with systemd and cgroup v2, sudo, `git`, and
  `python3` 3.11 or newer (Debian 12 or Ubuntu 24.04 and later; only for the
  deploy, the runtime brings its own Python). The commands below are for Debian and Ubuntu; step 10 uses `apt`.
  You need sudo to set it up; the Ponds themselves run as restricted users
  without it.
- A domain with DNS and a TLS certificate already working, and your own
  reverse proxy in front. The AI clients connect from their providers'
  clouds, so the domain must be reachable from the internet.
- An account with Claude or ChatGPT, or both. Tested with Claude Pro and
  Claude Max, and with ChatGPT Plus and ChatGPT Pro (custom connectors on the
  web).

## Don't panic

You are about to give an AI an account on your own machine, and that is as
big as it sounds. So, before the first command, what this hour can and
cannot do:

- **Nothing happens unseen.** Every setup and site change below prints its
  plan and a digest, and stops; you read the plan, then apply exactly that
  plan by its digest. (The wizards show their plan and wait for you to type
  `APPLY`.) The few plain commands in between, unpacking the release, the
  deploy, two links, one group and the packages in step 10, do only what
  they say.
- **What is yours stays yours.** Setup creates its own accounts, folders and
  services and refuses names that already exist. Your users, files and
  services are left alone; what it adds is its configuration under `/etc`,
  its systemd units and the Ponds' homes, beside the runtime the deploy put
  under `/opt`.
- **The AI gets its account and nothing more.** The account is the boundary,
  and root stays with you: the AI prepares commands that need it, you read
  them and press Enter ([trust and boundaries](trust.md)).
- **There is a door out.** `sudo boring-crocodile-admin uninstall --site`
  takes the site down again — plan first, like everything else — and never
  deletes the Ponds' homes: what was written there stays yours. With
  `--delete-data` it also removes the accounts, credentials and sign-ins;
  then `sudo rm -rf /opt/boring-crocodile` and the two links in
  `/usr/local/bin` remove the runtime ([uninstalling](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#uninstalling)).

## 1. Download and check

You need two things:

- the release archive `boring-crocodile-VERSION-linux-x86_64.tar.gz` and its
  SHA-256, both from the
  [Crocodile's releases](https://github.com/the-boring-crocodile/boring-crocodile/releases)
  (VERSION: the release you pick, the newest unless you have a reason);
- a copy of boring-pond (this repository): it holds the two handbooks and the
  diagram guide.

```bash
git clone https://github.com/the-boring-crocodile/boring-pond ~/boring-pond
sha256sum ~/Downloads/boring-crocodile-VERSION-linux-x86_64.tar.gz   # compare with the published value
```

The commands below assume the archive is in `~/Downloads`; adjust the path
if yours is elsewhere.

## 2. Deploy the runtime

The release brings its own `deploy`. It runs as root, so unpack it where
only root can write:

```bash
sudo mkdir -p /root/releases
sudo tar xzf ~/Downloads/boring-crocodile-VERSION-linux-x86_64.tar.gz -C /root/releases
sudo install -d -m 0755 /opt/boring-crocodile
sudo /root/releases/boring-crocodile-VERSION/deploy
sudo ln -sfn /opt/boring-crocodile/current/bin/boring-crocodile-{setup,admin} /usr/local/bin/
```

`deploy` checks every file
against the release's manifest, copies it to `/opt/boring-crocodile` with
root-owned files, and installs the runtime and nothing else: no accounts, no
service yet. Its last lines say the release "is live" and suggest
`boring-crocodile-setup --wizard`: the runtime is in place, and this guide
creates the Pond from a file instead (step 3).
Details: Crocodile [INSTALL](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#1-deploy-the-runtime).

## 3. The Engineer: create the first Pond

Write `~/beaver.json`, naming the handbook folder in your copy of boring-pond
(replace `/home/you` with your home; setup reads the folder as root and copies
the two files into the Pond):

```json
{
  "execution_user": "beaver-user",
  "control_user": "crocodile-mcp",
  "home": "/home/beaver-user",
  "context_mode": "import",
  "context_source": "/home/you/boring-pond/handbooks/steady-beaver",
  "context_files": ["HANDBOOK.md", "WELCOME.md"],
  "display_name": "The Steady Beaver"
}
```

`display_name` is optional: it is the name the sign-in page and the Pond's
own greeting show (without it, the first Pond is called "The Pond").

```bash
sudo boring-crocodile-setup --config ~/beaver.json                                  # shows the plan
sudo boring-crocodile-setup --config ~/beaver.json --apply --approve-digest DIGEST  # applies exactly that plan
```

DIGEST is the `plan_digest` the first command prints — the pattern from
[Don't panic](#dont-panic), and the same for every change below.

Setup creates the accounts `beaver-user` (the Pond) and `crocodile-mcp` (the
Crocodile), the home with `handbook/` (the Engineer's two files), `work/` and
`lab/`.

## 4. Activate the site

One decision first, because it cannot be changed later: **will this site
ever have Pirates** (local agents your Ponds hand work to)? A site takes
Pirates only if it was activated to accept them
(`service_registration_enabled`). If you might want them, say yes now; it
costs nothing until a Pirate is installed.

Write `~/site-inputs.json`, with your domain:

```json
{
  "public_base_url": "https://crocodile-url.example.test",
  "bind_host": "127.0.0.1",
  "bind_port": 8503,
  "runtime_root": "/opt/boring-crocodile/current",
  "memory_bytes": 2147483648,
  "swap_bytes": 0,
  "tasks_max": 256,
  "task_tasks_max": 128,
  "service_registration_enabled": true
}
```

Create the group Pirates join, then activate (plan, then apply):

```bash
sudo groupadd --system pond-pirates
sudo boring-crocodile-setup --site-config ~/site-inputs.json
sudo boring-crocodile-setup --site-config ~/site-inputs.json --apply --approve-digest DIGEST
```

Activation writes the configuration (the Pond's home is its file root, so its
file tools work at once), the systemd units and the Pond's approval secret,
and starts the site.

Sure you will never want Pirates? Then the wizard does the same without the
file and without the group: `sudo boring-crocodile-setup --site-wizard --apply`.
It needs a terminal, asks for the public URL (an HTTPS origin), the address
and port (keep `127.0.0.1` and `8503`) and the memory ceiling, shows what it
will install, waits for you to type `APPLY`, and ends by saying where the
approval secret is.

## 5. Your reverse proxy

Whatever proxy you use (nginx, Apache, Traefik, Caddy, ...), forward the
Crocodile's paths of your domain, unchanged, to `127.0.0.1:8503`. Here is an
example configuration for Caddy:

```caddy
crocodile-url.example.test {
    @crocodile path /mcp/* /.well-known/oauth-protected-resource/mcp/* /.well-known/oauth-authorization-server /authorize /token /revoke /register /approve /introspect /services/register
    handle @crocodile {
        reverse_proxy 127.0.0.1:8503
    }
}
```

The paths are `/mcp/*` (each Pond's endpoint), the two discovery paths
`/.well-known/oauth-protected-resource/mcp/*` and
`/.well-known/oauth-authorization-server`, the sign-in paths `/authorize`,
`/token`, `/revoke`, `/register` and `/approve`, and `/introspect` and
`/services/register` for services. Forward them unchanged.

If your proxy runs in a container, `127.0.0.1` inside it is the container,
not the host: give the proxy the host's network, or let the Crocodile listen
on the address the container can reach (`bind_host` in step 4).

Check on the host first: `sudo boring-crocodile-admin status --check` must
report the site healthy. Then check from outside:
`https://crocodile-url.example.test/mcp/pond`, the
Engineer's URL (setup always names the first Pond `pond`), must answer `401`
(it wants a sign-in):

```bash
curl -si https://crocodile-url.example.test/mcp/pond | head -1
```

## 6. The Consultant: a second Pond

Write `~/kingfisher.json` like step 3's file, with the Consultant's folder:

```json
{
  "execution_user": "kingfisher-user",
  "control_user": "crocodile-mcp",
  "home": "/home/kingfisher-user",
  "context_mode": "import",
  "context_source": "/home/you/boring-pond/handbooks/tidy-kingfisher",
  "context_files": ["HANDBOOK.md", "WELCOME.md"],
  "display_name": "The Tidy Kingfisher"
}
```

Create the Pond, then bring it into the running site. Each is a plan first,
then an apply with that plan's own digest:

```bash
sudo boring-crocodile-setup --add-pond kingfisher --config ~/kingfisher.json
sudo boring-crocodile-setup --add-pond kingfisher --config ~/kingfisher.json --apply --approve-digest DIGEST
sudo boring-crocodile-setup --site-extend
sudo boring-crocodile-setup --site-extend --apply --approve-digest DIGEST
```

Adding a Pond restarts the Crocodile briefly; open conversations reconnect.
Check from outside again: `https://crocodile-url.example.test/mcp/kingfisher`
now answers `401` (before this step, `404`).

## 7. The approval secrets

Each Pond has its own. You type it once per client on the sign-in page; read
it in a private terminal, never in a chat, a URL or a log:

```bash
sudo cat /etc/boring-crocodile/credentials/approval-secret              # the Engineer (first Pond)
sudo cat /etc/boring-crocodile/credentials/kingfisher-approval-secret   # the Consultant
```

## 8. Connect your AI clients

In this example the Engineer works with Claude and the Consultant with ChatGPT.
Mix and match as you like: both Ponds can use Claude, both ChatGPT, and a
Pond can even be used from both at the same time, each in its own
conversation. The steps are the same for any Pond; only the URL and its
approval secret change.

### 8.1 Claude

In claude.ai or the Claude app (steps as of 2026-10;
[Anthropic's guide](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)):

1. **Customize > Connectors**, then **+ Add > Add custom connector**. (Team
   and Enterprise: an owner adds it under **Organization settings >
   Connectors**; members then **Connect**.)
2. Name it, for example *Steady Beaver*, and enter
   `https://crocodile-url.example.test/mcp/pond`. **Continue**.
3. Keep the suggested sign-in settings and **Add**.
4. The Crocodile's sign-in page opens: enter the Engineer's approval secret.
5. In a chat: **+** at the lower left, **Connectors**, switch the Engineer on.

Claude cannot change a connector's URL, and disconnecting does not ask for a
new sign-in when the Pond behind the URL is gone. If the URL changes (another
Pond, a reinstalled site), remove the connector and add it again.

Claude Code: `claude mcp add --transport http beaver https://crocodile-url.example.test/mcp/pond`,
then `/mcp` to sign in.

### 8.2 ChatGPT

In chatgpt.com, web only (as of 2026-10;
[OpenAI's guide](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt)):

1. **Plugins**, the plus button, **Add custom MCP server**. (Business: admins
   and owners create it; Enterprise/Edu: admins, or members they allow.)
2. Name it, for example *Tidy Kingfisher*, and enter
   `https://crocodile-url.example.test/mcp/kingfisher` as the connection.
3. Choose OAuth; during the tool scan the Crocodile's sign-in page asks for
   the Consultant's approval secret.
4. Confirm, **Create as a plugin**, and check the tools it found
   (`pond_bootstrap`, `exec`, `file_read`, ...).
5. In a new chat, type **@** and pick it. ChatGPT applies the choice to one
   message: mention it again in follow-ups.

Each connection belongs to one Pond for good: one conversation per Pond. With
several Pond connectors switched on in one chat, an AI may wander between
them; switch on only the Pond you work with, or name it. Both handbooks tell
the AI to stay with its own Pond.

## 9. The first conversation

Start a new chat with the Pond's connector and ask for its bootstrap by the
connector's name: in Claude "bootstrap Steady Beaver", in ChatGPT "@Tidy
Kingfisher bootstrap". The AI clients do not load a connector's context on their own; a
plain "Hello" gets a plain hello back. The Pond reads its handbook and answers
with its ready line, *The Steady Beaver is ready.* `('')##=`, then its
defaults and one question: *what are we building first?* (the Consultant:
*what do you want to think through or find out first?*). Answer it, and change
any default you do not like.

To check the handbook works: later, open a second, fresh conversation and ask
for the bootstrap again. It should know its boundaries and where things stand
without the first chat.

## 10. Give the Engineer the diagram guide

The Engineer draws with [Boring Diagrams](../guides/boring-diagrams/README.md),
the method every picture in these docs was made with. It needs Graphviz and an
SVG rasterizer (root):

```bash
sudo apt update && sudo apt install -y graphviz librsvg2-bin python3-pil
sudo install -d -o beaver-user -g beaver-user /home/beaver-user/guides
sudo cp -r ~/boring-pond/guides/boring-diagrams /home/beaver-user/guides/
sudo chown -R beaver-user:beaver-user /home/beaver-user/guides
```

Its handbook already says to read `guides/boring-diagrams/HOWTO.md` before any
diagram. Then ask: "Draw the architecture of the project in `work/...`."

## Afterwards

- Make them yours: the handbook grows as you work; its agreement changes only
  by proposal and with your yes ([sample Ponds](../handbooks/README.md)).
- Keep their memory: from time to time, "save where we are"; when you settle
  something together, "put that into the handbook"
  ([your part](in-practice.md#keeping-a-ponds-memory-your-part)).
- What the AI clients do on their own (the time limit on one call, wandering
  connectors): [in practice](in-practice.md#what-the-ai-clients-do).
- Updates: [updating](updating.md). Services and Pirates:
  [installation](installation.md).
