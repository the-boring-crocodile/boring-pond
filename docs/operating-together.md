# From here on, let your AI do the heavy lifting

Once your Pond works, its AI can prepare the next change. You keep root:
it writes the configuration and one reviewable script; you stage a root-owned
copy, read that copy and run it with sudo.

Start with a concrete request:

> Add a Knowledge service to this Pond. Follow the task pages, fetch and
> verify the release, and prepare the configuration and one script for me
> to review. Explain what it changes and how to get back. Verify afterwards.

The same pattern works for adding another Pond or Pirate, updating a site,
or planning retirement. The [installation map](installation.md) points to
the procedure for each task. The task page remains the recipe for both
of you; the AI does not invent a parallel installer.

Ask for the proposed files, a script path under the Pond's `~/tmp`, its
effects and the checks that show whether it worked. Before running it,
replace `SCRIPT` below with that full path:

```bash
sudo install -m 0700 -o root -g root SCRIPT /root/pond-change.sh
sudo less /root/pond-change.sh
sudo /root/pond-change.sh
```

The Pond can still change its own `~/tmp`, so review and run the root-owned
copy. Stage any sourced scripts and privileged configuration/artifact inputs
under root ownership too, verify staged artifacts, and review the copy's input
paths before running it. The AI needs no sudo access; product plans still ask
you to type APPLY at the terminal.

New packaged handbooks include
[Operating this Pond together](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/src/boring_crocodile/handbooks/OPERATING_TOGETHER.md),
written to the AI. Existing handbooks stay yours: read that page together
before adopting it. The first installation stays in
[getting started](getting-started.md), because there is no Pond to help yet.

Give it the next task. After the change, have it record what happened and
propose cleanup; leave deleting old files and backups to you.
