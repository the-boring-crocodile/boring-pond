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
| `canvas` | Canvas: web pages at `https://crocodile-url.example.test/services/canvas/canvas/ID`, MCP at `https://crocodile-url.example.test/services/canvas/mcp` (one container listener, port 18511 on loopback) | |
| `knowledge` | Knowledge at `https://crocodile-url.example.test/services/knowledge/mcp`, port 18512 | |
| `fishmarket` | Fishmarket at `https://crocodile-url.example.test/fishmarket/mcp`; the example keeps its existing public proxy route | |
| `sourcecache` | Sourcecache at `https://crocodile-url.example.test/services/sourcecache-d365/mcp`, port 18513 | |
| `knowledge-url.example.test` | a service on its own, signing people in itself | your service's domain |
| `devbox`, `203.0.113.7` | a Windows dev box with pondNT, and its public address | your box |
| `VERSION` | a release version in file names and commands | the version you install |

[Getting started](getting-started.md) creates the first Pond with these
names. [Add a Pond](add-pond.md) uses garden for the next one.
Account names are free; only the first Pond's URL name is fixed.

For how we use the parts together, see [our site](our-site.md).
