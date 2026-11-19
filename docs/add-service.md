# Add a service later

For a new service, follow [Install one service](install-service.md).
A running service can gain a caller or change its role without a restart:
the Crocodile grant owns both facts.

Inspect `boring-crocodile-admin service-list` and preserve every caller that
should retain access, including any `pirate/NAME` caller. This command
replaces the complete caller/role map. It gives garden read access while
keeping pond's write access:

```bash
sudo boring-crocodile-admin service-grants knowledge --callers pond=writer,garden=reader --apply
```

Review the plan and type APPLY. Knowledge reads the role from authenticated
introspection; a cached token reflects a grant or role change within at most
60 seconds. No local access list, render or service restart is needed.

A Pirate caller is written `pirate/NAME=ROLE`. Its flavours may use every
service the Pirate is granted, unless its own config narrows that set.
The flavour still needs permission for the relevant service tools.

From the new caller, inspect `service_list` and `service_describe`, then
make a small call appropriate to its role. Check that existing callers retain
their intended access. To reverse the change, review/apply the previous
complete caller/role map and allow the same cache bound.
Return to the [task map](installation.md).
