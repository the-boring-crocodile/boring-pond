# Park or retire a Pond

Parking stops a Pond while keeping its account and description. Retirement
removes its admission and access, and locks its account while reserving its
UID/GID. Both leave home contents in place. Decide which outcome you want
before the maintenance window.

Finish its work and preserve any files you need. The initial Pond `pond`
owns the site; removing it requires the whole-site operation below.

## Park an added Pond

For the example `garden`:

```bash
sudo boring-crocodile-admin uninstall --pond garden
sudo boring-crocodile-admin uninstall --pond garden --apply
```

Review and type APPLY. The render disables that Pond and removes its
generated integration; its account, UUID, secret, grants and files stay.
Its name is removed from every Pirate's active list and saved for bring-back.
Other work may be affected by the displayed render stop/restart plan.

Bring that specific parked Pond back with:

```bash
sudo boring-crocodile-setup --site-extend --bring-back garden
sudo boring-crocodile-setup --site-extend --bring-back garden --apply
```

Bring-back restores exactly those saved Pirate pairs. Adding a different Pond
or Pirate still requires explicit admission.

## Retire its identity and access

```bash
sudo boring-crocodile-admin uninstall --pond garden --delete-data
sudo boring-crocodile-admin uninstall --pond garden --delete-data --apply
```

This is a separate destructive plan. It deactivates the Pond, seals retained
home/declaration paths, revokes selected access and removes credentials and
runtime paths. Its declaration is removed last. The account stays locked
and expired, and its group stays. Retirement drops the Pond from every
Pirate's active and saved lists. Its old registration socket grants no
continued access, and a new account reusing the UID gains no old pair.
Home contents are never recursively deleted; the top directory becomes
root-owned 0700. Any later deletion is the human's decision.

For the whole site, use `--site` instead of `--pond garden`, with
`--delete-data` only when identity/store retirement is intended.
Whole-site retirement also removes the OAuth store, locks and reserves the
controller's account/group, and retains removed-state descriptions for
explicit archival. Whole-site park also saves and removes the pairs.
Activation restores the initial Pond's saved pairs; use explicit bring-back
for each other parked Pond.

## Check and recover

```bash
sudo boring-crocodile-admin site-check
```

For an added Pond, also run a harmless command in a surviving Pond.
Repeating a completed added-Pond removal leaves its neighbours running. If retirement stopped part-way,
inspect its retained binding and error, then rerun the same approved scope.
Do not manually reuse its UID/GID or remove the sealed declaration to make
a retry pass.

Retirement has no automatic undo. Recovery requires the matching
identity/data backup; parking can instead be reversed by explicit activation.
Runtime files and PATH links are removed separately after whole-site
retirement if wanted.

## Release a reserved account later

The reserved account protects retained data and makes interrupted retirement
recoverable. Complete retirement and inspect the sealed files, remaining
processes and other uses of the account before releasing it. Pirate admission
has already been removed by retirement; there is no numeric worker grant to
edit in Pirate configuration.

Use the Unix account from the retirement plan (which may differ from the Pond
name), and record its binding before changing it:

```bash
retired_account=garden-user  # replace with the account in your plan
retired_uid=$(id -u "$retired_account")
retired_gid=$(id -g "$retired_account")
retired_group=$(id -gn "$retired_account")
```

Only then remove the account, without `-r` (the home and data stay):

```bash
sudo userdel "$retired_account"
getent group "$retired_group"
```

If that private group still exists, compare its GID with the recorded
`$retired_gid`. Once it matches and has no other users, remove it with
`sudo groupdel "$retired_group"`. Some systems remove the private group
with `userdel` already. Do this separately for each reserved worker and
controller account after whole-site retirement too. Sealed files remain
for the operator to archive or delete. Return to the [task map](installation.md).
