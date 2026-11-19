# Add a Pirate

A Pirate is a local agent under its own Unix account. Its model calls go to
the configured provider; its tools run locally. Ponds admitted to the same
Pirate share its work folder. Use separate Pirates for work that must stay
apart.

Start with a running Pond and a compatible Pirates release. Every enabled
Pond already has a registration socket; reception alone admits nobody.
The release checks its Crocodile requirement before installation. Read its
upgrade notes; do not bypass a refusal.

Choose a name matching `[a-z][a-z0-9]{0,15}`: one to sixteen lowercase
ASCII letters or digits, starting with a letter. `parrot` is valid;
`parrot-blue` is not.

Installation restarts the Crocodile controller and every enabled Pond worker,
then updates the shared Pirates runtime and restarts the running Pirates.
Finish or stop affected assignments before starting.

## Download and install

On x86_64 Linux with systemd, glibc 2.39 or newer and Python 3.12+ for deploy,
use the Pirates 0.4.0 archive from the
[Pirates releases page](https://github.com/the-boring-crocodile/boring-pirates/releases).
To add another Pirate, use the installed release's deploy executable and
skip the download. At the default HOME it is
`/opt/boring-pirates/current/deploy`. Run its `--check` with the same name,
Ponds and provider settings, then rerun it with `--install` in place of
`--check`. The first-install block below runs in one Bash shell.

```bash
(
    set -eu
    V=0.4.0
    f=boring-pirates-$V-linux-x86_64.tar.gz
    u=https://github.com/the-boring-crocodile/boring-pirates/releases/download/v$V
    mkdir -p ~/Downloads
    cd ~/Downloads
    curl -fLO "$u/$f"
    curl -fLO "$u/$f.sha256"
    sha256sum -c "$f.sha256"
    sudo install -d -m 0700 /root/releases
    sudo tar xzf "$f" -C /root/releases
    sudo /root/releases/boring-pirates-$V/deploy --check --name parrot --ponds pond
    sudo /root/releases/boring-pirates-$V/deploy --install --name parrot --ponds pond
)
```

A checksum from the same release page detects damage, not independent
origin. The default provider is Mistral; the installer asks for its key at
the terminal. Keep it out of chat and logs. For another provider, model or
key file, use the
[installer settings](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#installing-a-pirate)
and [provider reference](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#providers).
Inference needs that provider's service or local model server.

The installer creates the dedicated account, home, config, state and units.
It asks the Crocodile to admit the Pirate. In the plan, check the Pirate
and its requested Ponds, existing service grants, the `config.toml` diff,
group additions or removals, and the restart and job interruption lines.
The plaintext HTTP warning reports a non-loopback Crocodile listener.
Restrict that listener to your trusted reverse proxy with the host firewall.
Type APPLY when the plan matches your intent.

Use a comma-separated Pond list, or `all` for the Ponds currently enabled.
Admission does not grant service access. Follow
[Let a Pirate call a service](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/SERVICES_AND_PIRATES.md#let-a-pirate-call-a-service)
for the caller grant and the flavour configuration example.

## Check it

In the Pond, call `pirate_list` and inspect availability. The Pirate
appears under its configured name `parrot`; `--account` chooses the
Unix identity without changing that registration name. Ask
`pirate_describe` for the selected flavour before giving it an assignment.
An assignment may spend provider money and use that Pirate's own service
grants.

Configuration then belongs to you. An existing Pirate takes updates
through its ordinary deploy; first-install settings are refused once it
exists. If it does not register, inspect its unit/config and the admission
before repeating installation. The
[Pirates reference](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md)
covers configuration, results and removal.

For a Pond added later, run
`sudo boring-crocodile-admin pirate-add parrot --ponds garden --apply`.
This adds the Pond to the existing Pirate's admission and restarts the
controller and every enabled Pond worker. Running jobs in those workers are
interrupted. The result reports local readiness and
`external_registration: not_checked`. Once the Pirate reconnects, use
`pirate_list` in the new Pond to verify availability. See the
[admission reference](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#a-pirate-parrot).

## Remove it

Run `sudo /opt/boring-pirates/current/uninstall --name parrot`, using the
Pirates HOME from `/etc/boring-pond/homes.json` if it differs from the default.
Answer the initial `[y/N]` prompt. The Crocodile then shows its admission
removal plan and asks for typed APPLY. This restarts the controller and
every enabled Pond worker; the removed Pirate and its tasks are stopped.
Other Pirate processes keep running, but lose their worker connections
during those worker restarts.

Plain uninstall retains home, state, credentials, the account and its
`pirate-clients` membership. It also retains `pirate/parrot` in each service's
caller map. To withdraw those grants before removal, use `service-grants`
with each service's previous complete caller/role map, keeping its other
callers. See [Add a service later](add-service.md).

To revoke all grants and issued service tokens with removal, run the
uninstaller with `--delete-data`, either now or after an earlier plain
uninstall. It seals home and state as root's, mode 0700, and removes the
account. Their contents stay on disk for your review.
The [removal reference](https://github.com/the-boring-crocodile/boring-pirates/blob/main/README.md#removing-a-pirate)
covers failures and retries.

Return to the [task map](installation.md).
