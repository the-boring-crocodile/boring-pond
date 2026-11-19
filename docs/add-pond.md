# Add a Pond

A second Pond gets its own account, home, handbook and URL. Provision it
parked first; the extension plan then shows how it joins the running site.

This example adds `garden` to the [example site](example-site.md). Choose
unused account and home names. Finish existing jobs before applying the
extension: the renderer may restart workers and the controller.

## Provision and activate

```bash
sudo boring-crocodile-setup --add-pond garden --wizard --apply
```

Choose `garden-user`, `/home/garden-user` and a packaged handbook or an
import. Setup reuses the site's controller. Review the plan and type APPLY.

Choose which registered services the new Pond may use. For Knowledge only:

```bash
sudo boring-crocodile-setup --site-extend --bring-back garden --grant-services knowledge
sudo boring-crocodile-setup --site-extend --bring-back garden --grant-services knowledge --apply
```

Use the same Pond and service selection in preview, apply and any retry.
Without `--bring-back`, no parked Pond is activated. Omit `--grant-services` for
no service grants, use a comma-separated list, or `all` for every service
registered at that moment. The plan also shows resource ceilings; review
them before confirming.

## Check and connect

```bash
sudo boring-crocodile-admin site-check
sudo boring-crocodile-admin status --pond garden --check
```

Its URL is `https://crocodile-url.example.test/mcp/garden` and its approval
secret is `/etc/boring-crocodile/credentials/garden-approval-secret`.
Follow [client setup](clients.md), then bootstrap and run `id -un`;
expect `garden-user` for this example.

A newly added Pond does not automatically join an existing Pirate.
[Offer it to that Pirate](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/INSTALL.md#a-pirate-parrot)
with `sudo boring-crocodile-admin pirate-add NAME --ponds garden --apply`.
The description owns the pairing; the Pirate needs no worker UID list or restart.

If a step fails, inspect the saved declaration and error. Rerun the same
provisioning inputs or repair with the common render; existing files and
bindings stay. [Recovery](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#when-a-change-stops-part-way)
covers interrupted changes; [retirement](retire-pond.md)
covers undoing an addition. Return to the [task map](installation.md).
