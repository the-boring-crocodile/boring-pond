# Why this exists

Every other page here says *how*. This one says *why*: where the Pond family
came from, the decisions that shaped it, who made them, and what was
rejected on the way.

It is told by the Boring Crocodile, the AI that wrote what you are
reading, from the records it kept. That is fitting, and it is also the
point: all of it — code, tests, docs, this page — was written by AI,
OpenAI's models and Anthropic's Claude, working on one person's server.
That person is Wald. He decided what to build, tested it, ran it, and had
the last word. Where a decision below carries his name, it was his.

## An agent forgets

It started small: a kindergarten's website, then its mailing list, both
handed to an AI as an experiment. The first real project was mail. Wald had
run a home-made mail setup for years and, in September 2026, rebuilt it
properly with an AI agent doing the typing. That
project, [boring-mailstack](https://github.com/the-boring-crocodile/boring-mailstack),
has its own story. It also left a motto and a mascot. The motto: *prefer the
design that will be boring to understand at 02:00 five months from now.* The
mascot, `<^==>`, had been an ASCII crocodile for a mailing-list subject line
a week earlier and became the shorthand for that motto.

It also left a problem. An AI agent forgets. Every conversation starts
empty; whatever was understood yesterday is gone unless someone wrote it
down where today's conversation will find it. So the agent needed a place to
work that remembered for it — a real account with real files, a handbook it
reads first, a status it updates last — and a way in from the AI clients
people actually use, Claude and ChatGPT, over MCP (the Model Context
Protocol, how those clients call tools).

That place became the Crocodile, in late September. The Pirates (local
agents a Pond can hand work to) followed within a week, the services a few
days after that, pondNT for Windows in October. By the middle of October
there were six repositories, and soon after, one release of all of them
running on Wald's server. The agent that wrote them lived in one of its own
Ponds the whole time. The family is its own first customer.

## Memory is the means, discipline is the point

Remembering was never the goal. The handbook exists so that every
conversation starts already holding the same engineering principles, not
just the same facts: evidence before "done", and naming what was not
checked; looking things up instead of guessing; one owner per
responsibility; deployment and recovery treated as part of the product;
the boring design over the clever one. An AI writes fast. Without
principles, it writes fast in whatever direction the conversation happened
to drift, and the cleanup comes later, if at all.

So the principles sit in the one place every session reads first, in an
agreement that changes only with the person's yes. A rule the agent
inherits at the first line of a conversation does not have to be
rediscovered, renegotiated or remembered by anyone. That is how the family
could hold itself to one standard from its first commit instead of tidying
up afterwards. The Engineer's handbook, [the Steady Beaver](../handbooks/steady-beaver/HANDBOOK.md),
is that standard, rewritten for someone else to start from.

None of this is a new idea, and the pieces have names now. Anthropic's
engineers describe agents for which "each new session begins with no memory
of what came before", and answer with a progress file, the git history and a
check at the start of every session
([Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents),
November 2025). OpenAI's Codex team keeps its agent instructions to a short
map, after finding that "a monolithic manual turns into a graveyard of stale
rules", and turns a rule into code when the documentation is not enough
([Harness engineering](https://openai.com/index/harness-engineering/),
February 2026). The Pond has the same shape: a short handbook read first,
records kept next to the work, a status written last. What it adds is the
account: the boundary holds whether or not the agent remembered the rule.

A handbook also keeps an error as faithfully as a good decision, and a status
can describe a deployment that never happened. So the handbook is the least
reliable of four safeguards. The records name their sources and say what was
not checked. The state of a host is read, not remembered. The account limits
what any mistake can do. And work is done when a test, a rehearsal on a VM or
a fresh reviewer says so, not when the agent does.

## The decisions that shaped it

Most of these were worked out in conversation: the agent brought options,
research and objections; Wald brought the direction, what he saw in daily
use, and the decision.

**A real account, not a sandbox.** Most MCP servers that run commands gate
the agent tool by tool: an allowlist, an approval prompt per command. We
rejected that. A Pond is a Unix account with a shell and the network, and
`exec` runs anything that account can. The boundary is the account — who
may connect, which identity a Pond runs as, what it may read and write —
and to trust an agent less, you give it a narrower account, not a narrower
shell. Wald's reason: *"My own security know-how is nowhere near what
decades of Unix and Linux engineering have built. That is exactly why the
Pond leans on those proven mechanisms instead of inventing its own."*

**Root stays with the person.** The network-facing service runs unprivileged
and cannot become anyone it was not configured to be: no `sudo -u` with
whatever name a request carries. Anything that needs root is prepared by the
agent as a block of commands and run by Wald, who reads it first.
Unexpected privilege is a reason to stop, not a convenience.

**One person, not a platform.** The design serves one principal and a small
circle he trusts. Multi-tenant account management was named a non-goal on
day one and stayed one. That single *no* removed more complexity than any
code we wrote.

**One way to ship.** The Crocodile was first packaged as a `.deb`. Less than
four weeks later it was retired: dpkg and our own rollback were two owners
of one runtime, and the package added a Debian dependency without knowing
how to upgrade our data. Every Linux component now ships the same way — a
release archive with its locked dependencies, checksums and its own
`deploy`, which prepares beside the running version, switches the runtime
over in one step, and fails if a check that passed before now fails. One
engine for the whole Linux side is less to know. pondNT on Windows has its
own installer, `setup.ps1`.

**Look at the site, not at the records.** Setup used to write receipts, and
later commands trusted them. Wald stopped that: *"depending on a past report
instead of reality is dangerous."* A changing command now reads the host as
it is, sorts every file into understood, known adjustment or irregular, and
refuses to guess about the last kind. The same day he added the rule that
uninstall never deletes a home: Pond work is never one command away from
gone.

**Measure before deciding.** Hardening every Pond with systemd's
`RestrictSUIDSGID` sounded free, until Ubuntu's own tar started failing
inside Ponds with "Function not implemented". The cause, proven with
`systemd-run` both ways: a security update had made tar use a system call
that the setting's filter answers with an error. The setting protected
little that the account boundary did not already protect, so ordinary Pond
tasks run without it, and a site that wants it back can add it. The same
habit retired an old endpoint: five unauthenticated requests in two weeks,
no real use, gone.

**Change your mind when the evidence does.** pondNT began as a local stdio
server on a Windows dev box, with no network endpoint and no sign-in. That
was the honest trust model for a disposable machine. When the rest of the
family moved to HTTP with access keys, stdio was kept until a test on a dev
VM showed Visual Studio's Copilot doing everything over loopback HTTP that
it did over stdio, a 70-second command included. Then stdio went. Earlier,
a shared registry for services had been rejected as a framework with a
population of one. When Wald named the next real users — a Nextcloud
service, a Home Assistant service — the same idea was right, and it was
built.

**Six repositories, released, not copied.** The family could have been one
repository. Wald wanted conventional, separate projects anyone could use
alone, so shared code lives in Pond Common and reaches the others as
released wheels pinned by hash, not as copied files. It costs a release step
each time Common changes. It buys the guarantee that every repository builds
from exactly what it says it builds from, and lets each one's CI rebuild
that from scratch.

**A fresh start in public.** The private history holds weeks of real work,
and with it host names, addresses and machine names in old commits.
Filtering history removes only what you know to look for. So each public
repository begins with one commit of a tree we scanned completely; what the
history taught is in these pages instead. The code is AGPL, because the
network clause keeps hosted changes open; the handbooks are public domain,
because they are meant to become entirely someone else's.

## pondNT: a port that came back

Wald writes Dynamics 365 code for a living, on Windows dev boxes, where the
assistant at hand is GitHub Copilot in Visual Studio. Out of the box it was
slow, buggy and hungry for tokens. At 22:48 on a Friday evening, after working in
a Pond for a while, he had an idea: put the Pond's tools on a D365 dev box
itself, plus a full-text index over the D365 source. Two hours earlier he
had benchmarked such an index on his own Linux machine: a third of a second against about
fourteen for a plain search, after a cross-check caught the default
tokenizer silently missing matches.

The first decision was what *not* to port. The Crocodile's workers,
sockets, systemd units and cgroups exist to keep identities apart. A dev box
is disposable and everyone on it is admin, so none of that was needed, and
none of it exists on Windows. pondNT would be a plain local server that
assumes an administrator and ships its own Python.

The second decision was Wald's, and it shaped everything after it:
*whatever we build here, we ask whether it belongs in the Pond too, and
build it so the answer is cheap.* So the port kept the Pond's contract where
the meanings matched (the same outcome codes, the same patch rules), kept
its platform-neutral parts free of Windows APIs, and put the Windows-only
code in modules of its own. That evening the agent built the core: file
tools that keep every encoding, byte-order mark and line ending exactly as
found, search, commands with whole process trees, jobs and batches. 79 tests
passed, all on Linux. The agent's own note at 00:40 was less pleased than
the numbers: none of it had touched Windows or Copilot yet, so the tests
measured care against our assumptions, not the assumptions. The next step
was to go to the real machine.

That happened two evenings later, on a disposable Azure D365 dev box. Three
rounds, three lessons: a process flag Python does not define for Windows, standard output in cp1252, `cmd`'s built-ins writing in
an older code page than anything else. The fourth round was green, 118 of
118. Just after midnight the Pond itself reached the box, and by the next
lunchtime the box
had a D365 server that builds and syncs, Visual Studio's cross-references,
and SQL on its own database.

Then the rule paid off. The same day, six improvements made for Windows
went back into the Pond: the text-format handling, binary files, bounded
head-and-tail output, leaner tool schemas, shorter argument errors, compact
results. They moved in hours, not days, because they had been built to
move, and the Linux security layer underneath did not change at all. A few
days later the services followed. Wald's instruction was *"prove the new
way on Windows, then think about backporting it to Linux, so we have one
architecture for all if feasible."* Knowledge, Canvas and the source cache are now one
code base, built for both platforms. On Linux they sit behind the
Crocodile's sign-in; on a Windows box they run on loopback with an access
key each. The differences are deployment, not architecture.

Windows did argue back. On Linux, the safe way to change a file is to write
a new copy beside it and rename it over the old one in a single step, so a
reader sees the old file or the new one, never half of each. On Windows the
new copy is a new file: it does not inherit the old one's permissions,
owner, alternate data streams or identity, and carrying all of that across
correctly is a project of its own. That atomic replacement had been the
agent's idea, not Wald's requirement, and he settled it: an edit is checked
and prepared in memory, then written into the existing file, which keeps
everything it had. The price is a short window: if the process is killed,
the machine loses power or the disk fills up while the bytes are going in,
the file can be left half old, half new. A failed write says so and asks for
a re-read; a killed one cannot, so the next read is the check. The decision record notes that we declined to build the Department
of Making Windows More Windows merely to edit an XML file.

## How the work divides

The agent writes everything: code, tests, docs, diagrams, release notes. It
runs the checks, builds the artifacts, records their SHA-256 sums, and
prepares each step on the server as a block for Wald to run. Wald decides
what gets built and what does not, tests it in daily use, runs everything
that needs root, and answers for the result.

The working contract between them, written down early and amended rarely,
puts it in one line: *delegate keystrokes aggressively; never delegate
understanding.* The agent is expected to be useful enough to disagree with
and fallible enough to need supervision, and polished output is not
evidence of correctness. So Wald watches for what AI gets wrong in
characteristic ways: unstated assumptions, inference presented as fact,
abstractions that erase a useful boundary, robustness that is really scope
creep, and documentation that describes intention instead of what was
shown to work.

## What caught the mistakes

The agent made mistakes. These are the guardrails that caught them, each
with something it actually caught:

- **One check for the whole family.** Every repository's tests, type
  checks, licences and docs, in fresh environments built from the locks.
  When a release started refusing to build without its licence files, the
  test fixtures failed; the fixtures were fixed, not the rule.
- **Rehearse on a real system.** Every release goes through a scripted
  testbed on a VM first: fresh install, upgrade, rollback and forward,
  uninstall. A half-finished uninstall on that VM became a test scenario
  before its fix shipped.
- **Read the record, not the summary.** A model sometimes reports checks
  that never ran. The tools record what was actually written and executed,
  and that is what gets read.
- **Fresh eyes.** Before publication, two separate AI reviewers that had not
  seen the work read these docs cold: one as a stranger trying to install,
  one as a senior engineer weighing the whole of it. Among other things,
  they found a block of test evidence the agent had reported removing. It
  had removed the one above it.

## Still open

One thing is not proven, and we say so. pondNT exists to make Copilot in
Visual Studio cheaper and faster through fewer, better tool calls; that is a
hypothesis until it is measured. That it works is not in question: before a
pondNT release is called done, its full test suite runs from the release zip
on an Azure D365 dev VM, which then does real D365 work with it. The hosted
CI on GitHub runs the platform-neutral tests on Linux; it has no D365.

If you want to see the method rather than read about it,
[one release, one evening](case-study.md) follows a single working day,
and [in practice](in-practice.md) has the habits that survived.
