# Connecting an MCP client

Choose the endpoint before configuring the client:

| Endpoint | Sign-in |
|---|---|
| Crocodile Pond, such as `https://crocodile-url.example.test/mcp/pond` | OAuth for that Pond |
| Standalone service with its own issuer | OAuth for that service |
| pondNT on the Windows development box | Loopback HTTP with the access key installed by setup |

A service that trusts a Crocodile uses that issuer instead of running its own.
Use the issuer advertised by the endpoint. The controller's OAuth store and a
standalone service's store are different; register a client with the one that
will sign it in. See [Crocodile OAuth](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OAUTH.md)
and [service configuration](https://github.com/the-boring-crocodile/boring-services/blob/main/docs/CONFIGURATION.md).

Client names alone do not select a registration method. The issuer accepts a
pre-registered ID, a metadata-document URL on an allowed host, or dynamic
registration when explicitly enabled. A client using a supported metadata
document can start with the endpoint URL alone. Other clients need a registered
ID or an enabled dynamic-registration flow. Keep the issuer's existing policy
unless changing it is a deliberate site decision.

## Claude.ai and ChatGPT

For their metadata-document sign-in flow, add the Pond's MCP URL, such as
`https://crocodile-url.example.test/mcp/pond`, and complete OAuth in the browser.
The default Crocodile configuration accepts client metadata from `claude.ai`
and `chatgpt.com`; this path needs no separate `oauth client-add` command.
Enter the Pond's approval secret only on its approval page. A site that has
changed its allowed metadata hosts must check that policy first.

## VS Code with a registered client

VS Code1.123 introduced `oauth.clientId`; the
[current configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
documents it in the VS Code server format. With that field set, the client
uses the supplied ID rather than obtaining a new registration.
[Release note](https://code.visualstudio.com/updates/v1_123#_configure-oauth-client-credentials-in-mcpjson).

An administrator first creates a public client with PKCE. **These commands
create a record immediately.** Choose the command for the endpoint's issuer,
on the machine holding its store.

For a Crocodile Pond, in a private administrator terminal:

```bash
sudo boring-crocodile-admin oauth client-add --name "VS Code" --auth none --redirect-uri http://127.0.0.1:33418/ --redirect-uri https://vscode.dev/redirect
```

For a standalone service, run its installed CLI as the service account, with
`STORE` replaced by its configured issuer database:

```bash
boring-service-oauth --db STORE client-add --name "VS Code" --auth none --redirect-uri http://127.0.0.1:33418/ --redirect-uri https://vscode.dev/redirect
```

The [VS Code developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp#authorization)
lists these callback destinations. Confirm the callback used by the particular
desktop, web or remote session. The Pond issuer allows the HTTP loopback port
to vary; scheme, host, path and query must still match. `localhost` and
`127.0.0.1` are different hosts.

Put the returned public `client_id` into the relevant VS Code `mcp.json`
entry, keeping unrelated servers:

```json
{
  "servers": {
    "pond": {
      "type": "http",
      "url": "https://crocodile-url.example.test/mcp/pond",
      "oauth": {
        "clientId": "REPLACE_WITH_RETURNED_CLIENT_ID"
      }
    }
  }
}
```

Use the service's MCP URL when connecting directly to a standalone service.
The public client above has no client secret. VS Code's
[1.123 release note](https://code.visualstudio.com/updates/v1_123#_configure-oauth-client-credentials-in-mcpjson)
also describes secret storage for confidential clients; that is a different
registration choice. The issuer's approval secret belongs only on its approval
page, never in this JSON.

This is the VS Code format. Visual Studio and other Copilot harnesses have
their own configuration rules; do not copy the `oauth` object into them
without checking their documentation.

## Visual Studio and Claude variants

Our [Visual Studio notes](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/VISUAL_STUDIO_COPILOT.md)
record a Visual Studio2022 17.14 test that needed dynamic registration.
Microsoft's [current Visual Studio guide](https://learn.microsoft.com/en-us/visualstudio/ide/mcp-servers)
documents remote OAuth and Manage Authentication but does not establish that
every current build requires that same registration method. Retest the actual
build before changing issuer policy. pondNT's local access-key setup does not
depend on that OAuth observation.

Claude.ai, Claude Desktop and Claude Code are separate test targets.
The [Claude Code reference](https://code.claude.com/docs/en/mcp#use-pre-configured-oauth-credentials)
documents both metadata-document discovery and explicit client credentials.
A successful protocol fixture or one Claude product does not establish another
product's sign-in and refresh behavior.

## Claude Code with a registered client

Use Claude Code's
[pre-configured OAuth credentials](https://code.claude.com/docs/en/mcp#use-pre-configured-oauth-credentials)
path. Obtain the callback URI used by your installed client, then have the
administrator register a public client with `oauth client-add --name
"Claude Code" --auth none --redirect-uri CALLBACK_URI`. Configure the returned
client ID using that client's documented option. Keep the approval secret
for the approval page.

This uses the existing registered-ID policy; it does not require enabling
dynamic registration or adding a metadata host. Do not assume the callback
from a different Claude product. The [OAuth reference](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OAUTH.md)
owns the issuer rules.

## Check the connection

Sign in, bootstrap, and make a harmless call that confirms the intended
identity. If sign-in fails, compare the configured client ID and callback
with the issuer's registration. Keep secrets, tokens and callback query
strings out of chat and logs. Then return to
[Getting started](getting-started.md#5-sign-in-and-make-one-call).
