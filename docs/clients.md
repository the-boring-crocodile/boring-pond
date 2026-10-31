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

## Check the connection

Record the client product/version, operating system, local or remote session,
server version, endpoint and registration method. Then:

1. Sign in through that client's UI, approving only the intended Pond or service.
2. Make one harmless read-only tool call and confirm the intended identity.
3. Confirm refresh after access-token expiry and reconnection after restarting
   the client. A first tool call alone does not test refresh.
4. In a disposable acceptance fixture, revoke only its grant and confirm access
   is refused while another grant still works. Keep ordinary working grants.
5. Remove fixture registrations with that issuer's admin command, and remove
   only the fixture client entry.

Keep approval secrets, tokens and callback query strings out of the report.
Vendor documentation supplies a supported setup path; retain the actual client
journey's result separately.
