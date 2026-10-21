# Glossary

The family uses house names. Each one, with what it plainly is:

| Name | Plainly | Where |
|---|---|---|
| **MCP** | the Model Context Protocol: how AI clients such as Claude, ChatGPT and Copilot call tools on a server | everywhere |
| **D365** | Microsoft Dynamics 365 Finance and Supply Chain Management, an ERP system; pondNT and Sourcecache help develop for it, nothing else in the family needs it | boring-pondnt, boring-services |
| **Pond** | one person's or agent's workspace on a host: a Unix account with its files, commands, jobs and the services granted to it | boring-crocodile |
| **Crocodile** | the MCP server that gives an AI client (Claude, ChatGPT) a Pond: files, commands, jobs, services; also the sign-in for its Ponds | boring-crocodile |
| **control plane** | the Crocodile's HTTP side: MCP endpoint, OAuth sign-in, approval page, service registration | boring-crocodile |
| **worker** | the Crocodile's per-Pond process that runs file operations and commands as that Pond's account | boring-crocodile |
| **job** | long work started in a Pond and waited for separately (`job_start`, `job_wait`); its result is kept for a while | boring-crocodile |
| **approval secret** | the per-Pond (or per-server) secret a person types on the approval page to let a client in | boring-crocodile, boring-service-kit |
| **service** | an independent MCP server with its own data and caller policy (Canvas, Knowledge, Fishmarket, Sourcecache) | boring-services |
| **Canvas** | a shared drawing board (Excalidraw) agents push SVGs to and read edits from | boring-services |
| **Knowledge** | a notebook agents keep for each other, with attributed, append-only history | boring-services |
| **Fishmarket** | temporary file handovers between a browser and an agent | boring-services |
| **Sourcecache** | a read-only search index over Dynamics 365 source code and labels | boring-services |
| **Pirate** | a local AI agent with its own Unix account that takes assignments from a Pond (backed by a model provider such as Mistral) | boring-pirates |
| **parrot** | the Pirate in the examples ([example site](example-site.md)) | boring-pirates |
| **flavour** | one configuration of a Pirate: model, tools, file roots, context; same account | boring-pirates |
| **pondNT** | the Windows side: an MCP server for Visual Studio Copilot with core tools and Dynamics 365 tools | boring-pondnt |
| **persona** | pondNT's optional assistant voice, described in the kit's `persona.md`; "Plain, please" turns it off for a session | boring-pondnt |
| **kit** | pondNT's handbook (agreement, persona, task guides); copied to the box once at setup and kept there across releases | boring-pondnt |
| **Common** | the shared Python libraries every part depends on, released as versioned wheels | boring-pond-common |
| **family check** | one command that runs every repository's checks in fresh environments from their hash locks | boring-pond |
| **issuer** | the OAuth authorization server inside a server (Crocodile or a lone service): who may sign in, approval, tokens | boring-service-kit |
| **site** | one host's Crocodile with its Ponds, services and Pirates; *activated* once, which writes its configuration and systemd units | boring-crocodile |
| **handbook** | what the AI reads at the start of every conversation in a Pond: its welcome, agreement and project context; pondNT's core hands over its `bootstrap.md` the same way | boring-crocodile, boring-pondnt |
| **guest** | a Pirate registered with a Pond; only a site activated to accept guests (`service_registration_enabled`) takes them, and that cannot be switched on later | boring-crocodile |
| **service token** | what a Pond or a Pirate calls a service with; issued by the Crocodile | boring-crocodile |
| **access key** | on pondNT, the per-server key Copilot sends with every call over loopback | boring-pondnt |
| `<^==>` | the Crocodile | everywhere |
| **The Engineer** | the sample engineering Pond; its handbook's character is the Steady Beaver `('')##=` | [handbooks](../handbooks/README.md) |
| **The Consultant** | the sample research and concepts Pond; its handbook's character is the Tidy Kingfisher `--<o)` | [handbooks](../handbooks/README.md) |
