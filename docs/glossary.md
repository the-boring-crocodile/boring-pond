# Glossary

The family uses house names. Each one, with what it plainly is:

| Name | Plainly | Where |
|---|---|---|
| **MCP** | the Model Context Protocol: how AI clients such as Claude, ChatGPT and Copilot call tools on a server | everywhere |
| **D365** | Microsoft Dynamics 365 Finance and Supply Chain Management, an ERP system; pondNT and Sourcecache help develop for it, nothing else in the family needs it | boring-pondnt, boring-services |
| **Pond** | one person's or agent's workspace on a host: a Unix account with its files, commands, jobs and the services granted to it | boring-crocodile |
| **Crocodile** | the MCP server that gives an AI client (Claude, ChatGPT) a Pond: files, commands, jobs, services; also the sign-in for its Ponds | boring-crocodile |
| **control plane** | the Crocodile's HTTP side: MCP endpoint, OAuth sign-in, approval page, service registration | boring-crocodile |
| **worker** | the Crocodile's per-Pond process for file operations and service access; command jobs go to its task runner, under the same account | boring-crocodile |
| **job** | long work started in a Pond and waited for separately (`job_start`, `job_wait`); its result is kept for a while | boring-crocodile |
| **approval secret** | the per-Pond (or per-server) secret a person types on the approval page to let a client in | boring-crocodile, boring-service-kit |
| **service** | an independent MCP server with its own data and caller policy (Canvas, Knowledge, Fishmarket, Sourcecache) | boring-services |
| **Canvas** | a shared drawing board (Excalidraw) agents push SVGs to and read edits from | boring-services |
| **Knowledge** | a notebook agents keep for each other, with attributed, append-only history | boring-services |
| **Fishmarket** | temporary file handovers between a browser and an agent | boring-services |
| **Sourcecache** | a read-only search index over Dynamics 365 source code and labels | boring-services |
| **Ferry / gateway** | one MCP front end over several backends; its four tools discover and call backend tools as needed, keeping the client's initial tool list small | [mcp-ferry](https://github.com/the-boring-crocodile/boring-services/blob/main/mcp-ferry/README.md) |
| **Pirate** | a local AI agent with its own Unix account that takes assignments from a Pond (backed by a model provider such as Mistral) | boring-pirates |
| **parrot** | the Pirate in the examples ([example site](example-site.md)) | boring-pirates |
| **flavour** | one configuration of a Pirate: model, tools, file roots, context; same account | boring-pirates |
| **pondNT** | the Windows side: an MCP server for Visual Studio Copilot with core tools and Dynamics 365 tools | boring-pondnt |
| **persona** | pondNT's optional assistant voice, described in the kit's `persona.md`; "Plain, please" turns it off for a session | boring-pondnt |
| **kit** | pondNT's handbook (agreement, persona, task guides); installed by setup, with local edits preserved when later releases update it | boring-pondnt |
| **Common** | the shared Python libraries every part depends on, released as versioned wheels | boring-pond-common |
| **family check** | one runner for the repositories' own checks, using each consumer's declared Common revision and frozen runtime dependencies | boring-pond |
| **issuer** | the OAuth authorization server inside a server (Crocodile or a lone service): who may sign in, approval, tokens | boring-service-kit |
| **site** | one host's Crocodile with its Ponds, services and Pirates; *activated* once, which writes its configuration and systemd units | boring-crocodile |
| **handbook** | what the AI reads at the start of every conversation in a Pond: its welcome, agreement and project context; pondNT's core hands over its `bootstrap.md` the same way | boring-crocodile, boring-pondnt |
| **guest** | a Pirate registered with a Pond that accepts guests; an operator can enable this at activation or later with [`--site-render --guests`](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#updating) | boring-crocodile |
| **service token** | what a Pond or a Pirate calls a service with; issued by the Crocodile | boring-crocodile |
| **access key** | on pondNT, the per-server credential sent by an authorized caller (the client for a direct server, Ferry for a backend) | boring-pondnt |
| `<^==>` | the Crocodile | everywhere |
| **The Engineer** | the sample engineering Pond; its handbook's character is the Steady Beaver `('')##=` | [handbooks](../handbooks/README.md) |
| **The Consultant** | the sample research and concepts Pond; its handbook's character is the Tidy Kingfisher `--<o)` | [handbooks](../handbooks/README.md) |
