# Install one service

A working Crocodile can install Knowledge for `pond` with one command.
Its grant owns both access and the caller's role.

You need Docker Engine and Compose v2, a compatible Knowledge archive already
checked and unpacked under `/root/releases`, and a proxy route the container
can reach and trust. Forward `/services/knowledge/mcp` and
`/.well-known/oauth-protected-resource/services/knowledge/mcp` to
`127.0.0.1:18512`. Keep the Crocodile's routes in place.
[Downloads and networking](https://github.com/the-boring-crocodile/boring-services/blob/main/README.md#installing-on-linux)
covers the archive and the other services.

The host firewall must let the stack's subnet reach the proxy on TCP port
443. The following UFW rule on the proxy host allows Knowledge's default
subnet, `172.16.43.0/24`.

    sudo ufw allow from 172.16.43.0/24 to PROXY_IP port 443 proto tcp

Replace PROXY_IP with the proxy address the container uses. For another
service or a customized network, use its actual subnet. On a default-deny
host, the first deploy stops at the reach check until this path is open.

After unpacking Knowledge 0.3.0, replace the example domain with yours.

```bash
V=0.3.0
sudo "/root/releases/boring-knowledge-$V/deploy" --install --url https://crocodile-url.example.test/services/knowledge/mcp --callers pond=writer
```

The installer reads the local Crocodile inventory, shows the registration
plan and asks for typed APPLY. It writes the returned credential directly
into HOME/credentials and generates the service's one Crocodile authority
block. There is no prepared auth JSON or secret-capture step. Compose owns
the container's listener; deploy checks its actual exposure.

A successful deploy includes endpoint and registration checks. In the Pond,
inspect `service_list`, then `service_describe`, and make a small call using
the returned schema. To share Knowledge with another caller, use
[Add a service later](add-service.md).

If a command fails, inspect the named step, `boring-crocodile-admin service-list`
and the installed files before retrying. Registration may have succeeded
before a later failure. Keep credentials private; the installer refuses to
overwrite a once-only secret. Uninstall with `--delete-data` removes matching
registrations through a reviewed plan and seals the retained files; it does
not delete persistent data.
