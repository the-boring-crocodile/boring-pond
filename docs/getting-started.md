# Getting started

Give your AI a Unix account, a home and a handbook. This walk installs one
Pond on a Linux host and connects one client. You hold root; the Pond runs
as its own account.

Use the documentation linked by the release you choose. This page describes
the setup interface with per-Pond descriptions and typed APPLY. A published
0.4.x release has its own tagged install guide. For an existing site, start
with [updating](updating.md), including its adoption decision.

## What you need

- Linux x86_64, glibc 2.39 or newer, systemd and cgroup v2.
- A human account with sudo, Python 3.12 or newer, curl, tar and sha256sum.
  The release supplies its runtime Python. No ACL package is needed.
- A domain, working HTTPS and a reverse proxy you control. Hosted clients
  reach the site from outside your network.
- An MCP client that supports the endpoint's OAuth registration method.

Start with one Pond. Its memory ceiling limits its worker and commands
together; it reserves no RAM. Leave room for the host and simultaneous
work. Services and local model inference need their own resources.
[Trust and boundaries](trust.md) explains what the account can reach.

The [example names](example-site.md) below are invented. Replace the domain,
account names and home with yours. The first Pond's URL name is always
`pond`.

## 1. Download and install the runtime

Check the host first:

```bash
getconf GNU_LIBC_VERSION
python3 --version
```

Read the notes for Crocodile 0.5.0 on the
[Crocodile releases page](https://github.com/the-boring-crocodile/boring-crocodile/releases).
Run the download and checksum block in one Bash shell.

```bash
(
    set -eu
    V=0.5.0
    f=boring-crocodile-$V-linux-x86_64.tar.gz
    u=https://github.com/the-boring-crocodile/boring-crocodile/releases/download/v$V
    mkdir -p ~/Downloads
    cd ~/Downloads
    curl -fLO "$u/$f"
    curl -fLO "$u/$f.sha256"
    sha256sum -c "$f.sha256"
    sudo install -d -m 0700 /root/releases
    sudo tar xzf "$f" -C /root/releases
    sudo install -d -m 0755 /opt/boring-crocodile
    sudo /root/releases/boring-crocodile-$V/deploy
    sudo ln -sfn /opt/boring-crocodile/current/bin/boring-crocodile-setup /usr/local/bin/
    sudo ln -sfn /opt/boring-crocodile/current/bin/boring-crocodile-admin /usr/local/bin/
)
```

The checksum must print OK. It detects damage; a checksum from the same
site is not an independent proof of origin. The deploy verifies its manifest
and installs the runtime under `/opt`. It creates no Pond or running site.

## 2. Create the Pond

```bash
sudo boring-crocodile-setup --wizard --apply
```

For this example choose account `crocodile-user`, controller
`crocodile-mcp`, home `/home/crocodile-user`, and the starter handbook.
Engineer and Consultant are also packaged choices; importing your own
selected files is another option.

Review the displayed account, home and file plan, then type APPLY.
Provisioning creates the dedicated accounts, home, private approval secret
and a parked declaration. It starts no worker. Existing accounts are not
silently adopted; a rerun retains recorded identities, secrets and files.

## 3. Activate the site

```bash
sudo boring-crocodile-setup --site-wizard --apply
```

Enter your HTTPS origin, for example
`https://crocodile-url.example.test`. With a proxy on the host, keep the
listener at `127.0.0.1:8503`. If the proxy runs in a container, choose an
address it can reach and restrict access to that listener.

The wizard proposes a memory ceiling: a quarter of host RAM, between
512 MiB and 8 GiB. Review it for your workload. The plan shows which units
and files change; type APPLY to render and start the site.

Every enabled Pond has a Pirate registration socket. That admits nobody:
Pirates still need explicit admission.

## 4. Connect the reverse proxy

Forward these paths unchanged to the configured listener. For Caddy with
the example loopback address:

```caddy
crocodile-url.example.test {
    @crocodile path /mcp/* /.well-known/oauth-protected-resource/mcp/* /.well-known/oauth-authorization-server /authorize /token /revoke /register /approve /introspect /services/register
    handle @crocodile {
        reverse_proxy 127.0.0.1:8503
    }
}
```

Keep `/services/register` on the Crocodile if services later add their own
routes. DNS, certificates, proxy reload and firewall rules remain yours.
A container's loopback address refers to that container, not its host.

Check local state, then the public endpoint:

```bash
sudo boring-crocodile-admin site-check
sudo boring-crocodile-admin status --check
curl -sSi https://crocodile-url.example.test/mcp/pond | head -1
```

Expect a regular site check, healthy status and HTTP 401 from the unsigned
public request: the endpoint is there and wants a sign-in.
A local status check cannot test the proxy or certificate.

## 5. Sign in and make one call

Add `https://crocodile-url.example.test/mcp/pond` to your client.
[Client setup](clients.md) explains metadata-document and registered-ID
paths, including Claude Code. Keep dynamic registration closed unless
changing it is a deliberate site decision.

Read the approval secret in a private administrator terminal:

```bash
sudo cat /etc/boring-crocodile/credentials/approval-secret
```

Open the approval page from the client you are connecting. Never use an
approval link someone sent you. Enter the secret on that page and keep it
out of chat, URLs and logs. Each Pond has its own URL and secret.

In a fresh conversation, select the connector and ask it to call
`pond_bootstrap`. Then ask for `exec` with `id -un; pwd`.
The example returns `crocodile-user` and `/home/crocodile-user`.

## Keep a handoff

Ask the Pond to write a short project status under its `work/` directory:
goal, what happened and the next step. Inspect that file. Start a fresh
conversation with the same connector, bootstrap, and ask it to read the
status. The file carries the work across conversations.

From here, [let your AI prepare the next change](operating-together.md).
The [task map](installation.md) covers another Pond, a Pirate, services,
updates and retirement. You continue to review and run the root steps.
