# Case study: one release, one evening

How a release of the whole family came together in one evening, told from
the records it left. It shows how the work divides between a person and an
AI working in a Pond, and what the rehearsals caught that the tests did not.
[In practice](in-practice.md) describes the habits; this is one day of them.

## The cast

The operator, with root on the host. One Claude conversation working in the
operator's engineering Pond, with the six repositories, a lab folder and
Incus test VMs on the same host. A second AI client, used once in the
afternoon to review a kit. The family's own services: Fishmarket for handing
files to a Windows box, Knowledge for notes.

## The request

In the afternoon the operator asked to fix the rest before the release
rather than release twice. What was left was small and spread over
all six repositories: licence files inside every package and release
archive, an uninstall that sometimes gave up halfway, display names for
Ponds, a misleading hint in the setup wizard, a testbed that picked the
wrong archive when two packages shared a version number, and a contribution
policy (decided in one line: inbound equals outbound, no CLA).

## Who did what

The AI did the mechanical work and said where judgment was needed: it
changed code, docs and tests, ran each repository's checks, built every
artifact once and wrote down their SHA-256 sums. The operator made the
calls, read every root command before running it, and ran it himself; the
AI never had root, and prepared those commands as one block to read.

## The family check

One command runs all six repositories' checks: each in a fresh virtual
environment built from its hash lock, with its tests and type checks, plus a
docs check (no product page may point into the private records) and a
licence check (`reuse lint`, and every package carries the licence). Its
first run failed in two repositories: a release now refused to build without
LICENSE and COPYING.md, and their test fixtures had none. Both
were fixed in the fixtures, not by loosening the rule.

## The rehearsal

The built archives went to a staging VM and through the scripted testbed:
a fresh install, an upgrade from the previous version with a rollback and
forward again, adding and removing a Pond, all four services installed,
redeployed, removed and reinstalled, two Pirates, and a site uninstall.
The Windows bundle went through its own test run on a Windows VM (419 tests
passed).

The uninstall scenario was there because of something earlier that day: tearing down the
staging VM's old site had stopped halfway ("Recorded user still has
processes after site stop") and left a site that a second run no longer
recognized. The fix stops the controller and the workers together with the
site and waits for them, and writes down what it is about to remove before
removing anything, so a second run can finish the job. The rehearsal forced
the bad case on purpose, a process held under the controller's account, and
the second run finished from the record.

## Going live

In the early evening the operator unpacked the archives as root, checked their sums,
ran a dry-run deploy of each, then the six deploys, about 90 seconds in all. The
AI checked from inside its Pond what it could see: no failed unit, every
service and Pirate answering its heartbeat, every endpoint giving the
expected answer to an unauthenticated request. Two deploy records were
readable only by root; the operator pasted their last lines, and the record
was complete.

## Afterwards, the same evening

The Windows side got the new pondNT through Fishmarket: one link, a hash
the operator compared, a dry-run plan, then setup. The release check there
was the assistant's first answer after "bootstrap", and it passed.

Preparing publication turned up one more thing no test had seen: hosted CI
builds the shared libraries from the commit each repository names in
`.common-ref`, and all four of those still named older versions than the
locks pinned. On a workstation the check never builds from that ref, so it
passed; on GitHub every repository would have failed. A new step in the
family check now compares the two, and a full rehearsal of the publication
(export, first commits, the family check on the fresh repositories) passed
before anything was published.

## What it shows

- Decisions stay with the person and take a sentence; the AI carries the
  volume and says where it needs one.
- A rehearsal on a real system catches what unit tests cannot: the order in
  which systemd stops things, an archive picked by the wrong name.
- A failure on a live system becomes a test scenario before the fix ships.
- Every claim of success points at evidence: a check's summary, a hash, a
  deploy line, a heartbeat.
