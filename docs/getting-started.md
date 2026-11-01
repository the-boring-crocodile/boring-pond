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
| `kingfisher` (optional, step 6) | `https://crocodile-url.example.test/mcp/kingfisher` | `kingfisher-user` | [the Tidy Kingfisher](../handbooks/tidy-kingfisher/HANDBOOK.md) |

**The short route.** One Pond and one client first: steps 1 to 5, the first
line of step 7, step 8.1 and step 9, then [first success](#first-success-a-project-a-handoff-a-fresh-conversation):
the Pond reads a project, saves a handoff, and a fresh conversation picks it
up. That proves the part that matters. The second Pond (step 6), ChatGPT
(8.2), the diagram guide (step 10) and Pirates can follow any day.

## What you need

- A Linux host on x86_64 with systemd and cgroup v2, sudo, `git`, and
  `python3` 3.11 or newer (Debian 12 or Ubuntu 24.04 and later; only for the
  deploy, the runtime brings its own Python). The commands below are for Debian and Ubuntu; step 10 uses `apt`.
  You need sudo to set it up; the Ponds themselves run as restricted users
  without it. Memory, disk and costs: [installation](installation.md#what-you-need).
- A domain with DNS and a TLS certificate already working, and your own
  reverse proxy in front. The AI clients connect from their providers'
  clouds, so the domain must be reachable from the internet.
- A client account that supports remote MCP connections with OAuth.
  The walkthrough below uses Claude and ChatGPT; product plans and menus
  can change. [Client setup](clients.md) explains registration choices and
  how to verify the actual client you use.

## What setup will and will not do

You are about to give an AI an account on your own machine, and that is as
big as it sounds. So, before the first command, what this hour can and
cannot do (in short: don't panic):

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

You need the Crocodile's release archive with its `.sha256` file, from the
[Crocodile's releases](https://github.com/the-boring-crocodile/boring-crocodile/releases),
and a copy of boring-pond (this repository): it holds the two handbooks and
the diagram guide. `V` is the release; the one below is from the
[tested set](updating.md#releases-and-versions), and the newest is on the
releases page. Steps 1 and 2 are one block; run it in one shell:

```bash
V=0.4.20
f=boring-crocodile-$V-linux-x86_64.tar.gz
u=https://github.com/the-boring-crocodile/boring-crocodile/releases/download/v$V
mkdir -p ~/Downloads && cd ~/Downloads &&
curl -fLO "$u/$f" && curl -fLO "$u/$f.sha256" &&
sha256sum -c "$f.sha256" &&            # must print OK; if not, the block stops here
git clone --depth 1 https://github.com/the-boring-crocodile/boring-pond ~/boring-pond &&
sudo mkdir -p /root/releases &&
sudo tar xzf "$f" -C /root/releases &&
sudo install -d -m 0755 /opt/boring-crocodile &&
sudo /root/releases/boring-crocodile-$V/deploy &&
sudo ln -sfn /opt/boring-crocodile/current/bin/boring-crocodile-{setup,admin} /usr/local/bin/
```

The checksum catches a damaged download. It does not prove who built the
archive: it comes from the same page.

## 2. Deploy the runtime

The second half of the block. The release brings its own `deploy`, which
runs as root, so the archive is unpacked where only root can write.
`deploy` checks every file
against the release's manifest, copies it to `/opt/boring-crocodile` with
root-owned files, and installs the runtime and nothing else: no accounts, no
service yet. Its last lines say the release "is live" and suggest
`boring-crocodile-setup --wizard`: the runtime is in place, and this guide
creates the Pond from a file instead (step 3).
Details: Crocodile [INSTALL](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#1-deploy-the-runtime).

## 3. The Engineer: create the first Pond

Write `~/beaver.json`, naming the handbook folder in your copy of boring-pond
(replace `/home/you` with the folder you cloned it to, `/root` when you work
as root; setup reads the folder as root and copies
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
[what setup will and will not do](#what-setup-will-and-will-not-do), and the same for every change below.

Setup creates the accounts `beaver-user` (the Pond) and `crocodile-mcp` (the
Crocodile), the home with `handbook/` (the Engineer's two files), `work/` and
`lab/`.

## 4. Activate the site

This example enables **Pirates**, local agents your Ponds can hand work to,
by setting `service_registration_enabled`. It does not install a Pirate.

You can also enable reception later with `--site-render --guests POND`.
That is a planned site change which can interrupt running work; follow
[Crocodile operations](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#updating)
when the site is ready for it.

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

Create the group Pirates join (their account joins it to register with the
Pond's guest socket, which belongs to this group), then activate (plan, then
apply):

```bash
sudo groupadd --system pond-pirates
sudo boring-crocodile-setup --site-config ~/site-inputs.json
sudo boring-crocodile-setup --site-config ~/site-inputs.json --apply --approve-digest DIGEST
```

Activation writes the configuration (the Pond's home is its file root, so its
file tools work at once), the systemd units and the Pond's approval secret,
and starts the site.

To start without Pirate reception, the wizard does the same without the
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
curl -sSi https://crocodile-url.example.test/mcp/pond | head -1   # -S: a TLS or DNS error is shown
```

## 6. The Consultant: a second Pond (optional)

One Pond is a complete site; skip this step if that is all you want, and
skip the Consultant's lines in the steps after it. To add the Consultant,
write `~/kingfisher.json` like step 3's file, with the Consultant's folder:

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
# optional: the Consultant
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
sudo cat /etc/boring-crocodile/credentials/kingfisher-approval-secret   # optional: the Consultant (step 6)
```

## 8. Connect your AI clients

In this example the Engineer works with Claude and the Consultant, if you
added it, with ChatGPT.
Mix and match as you like: both Ponds can use Claude, both ChatGPT, and a
Pond can even be used from both at the same time, each in its own
conversation. For either Pond, use its own URL and approval secret. Client products can
differ in how they register with the issuer; use [client setup](clients.md)
if the client asks for an ID or cannot start sign-in. The interface steps
below are examples, not acceptance of every current client build.

### 8.1 Claude

In claude.ai or the Claude app (menu names change; the current steps are in
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

Shown with the optional Consultant; for the Engineer, use its URL and secret.
In chatgpt.com, web only (menu names change; the current steps are in
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
defaults and one question: *what are we building first?* (the optional Consultant:
*what do you want to think through or find out first?*). Answer it, and change
any default you do not like.

## First success: a project, a handoff, a fresh conversation

The AI forgets every conversation. What carries over is what the Pond wrote
into its files, so this is the test worth passing first. In the Engineer's
conversation:

1. **Give it a project.** "Clone https://github.com/the-boring-crocodile/boring-pond
   into `work/` and tell me how it is organised." The Pond has its account's
   network and `git`; it clones, reads and answers from the files.
2. **Save a handoff.** "Save where we are." The Engineer's handbook asks for
   goal, state, open questions and the next step in the project's
   `STATUS.md`. It says which files it wrote; read them yourself with
   `sudo ls -R /home/beaver-user/work` and `sudo cat` on the file it named.
3. **Recover.** Close the chat. In a new one: "bootstrap Steady Beaver", then
   "where were we?" It should name the project and the next step without the
   first chat. If it cannot, nothing was saved: ask what it wrote, and where.

That is the whole habit ([keeping a Pond's memory](in-practice.md#keeping-a-ponds-memory-your-part)).
From here: a second Pond (step 6), another client (8.2), the diagram guide
(step 10), Pirates ([installation](installation.md)).

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
