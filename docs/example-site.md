# The example site

Every example in the Pond family's docs uses this one site, so the pages read
as one story: the same domain, the same Ponds, the same names from the first
install to the last service. Put your own values where these appear.

| In the examples | What it is | Yours |
|---|---|---|
| `crocodile-url.example.test` | the public domain of the Linux host's Crocodile | your domain |
| `127.0.0.1:8503` | where the Crocodile listens; the reverse proxy forwards to it | any loopback port |
| `crocodile-mcp` | the account the Crocodile runs as | any name |
| `pond`, `crocodile-user` | the first Pond (always named `pond`; the name is the path in its URL, `/mcp/pond`) and its account, home `/home/crocodile-user` | the account |
| `garden`, `garden-user` | a second Pond and its account, URL `/mcp/garden` | your names |
| `robin` | the operator, a person: sudo on the host, signs in to services as `robin` | you |
| `parrot`, `pirate-parrot` | a Pirate and its account | your names |
| `canvas` | Canvas: web pages at `https://crocodile-url.example.test/canvas/ID`, MCP at `https://crocodile-url.example.test/services/canvas/mcp` (container ports 18510, 18511 on loopback) | |
| `knowledge` | Knowledge at `https://crocodile-url.example.test/services/knowledge/mcp`, port 18512 | |
| `fishmarket` | Fishmarket at `https://crocodile-url.example.test/fishmarket/mcp` | |
| `sourcecache` | Sourcecache at `https://crocodile-url.example.test/services/sourcecache-d365/mcp`, port 18513 | |
| `knowledge-url.example.test` | a service on its own, signing people in itself | your service's domain |
| `identity-url.example.test` | an external sign-in (Keycloak, Entra) | your issuer |
| `devbox`, `203.0.113.7` | a Windows dev box with pondNT, and its public address | your box |
| `VERSION` | a release version in file names and commands | the version you install |

One exception: [getting started](getting-started.md) installs two sample
handbooks and names the accounts after their characters. The first Pond is
still `pond`, but its account is `beaver-user` there and `crocodile-user` in
the reference pages; the second Pond is `kingfisher` with `kingfisher-user`
there, `garden` with `garden-user` elsewhere. Account names are free; only
the first Pond's name is fixed.

A real installation with real names, for comparison: [our site](our-site.md).
