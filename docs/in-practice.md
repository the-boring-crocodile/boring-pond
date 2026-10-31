# In practice

A report from inside: the Pond family was built by the thing this page
describes — AI assistants working in Ponds, for weeks, with their operator —
and these are the habits that survived. Not a feature list; the component
docs say what each part can do. This is what a working day looks like.

## A conversation begins

Start by asking the assistant to read the Pond's context: "bootstrap Steady
Beaver", for example, naming the connector you intend to use. It should read
the handbook and say whether anything is missing before claiming readiness.
Then ask "where were we?" so it reads the project's status before starting
work. This makes the handoff explicit; a greeting alone is no check that
the right context was loaded.

## The work itself

The family itself was built this way: Claude and ChatGPT working in Ponds
across several repositories, with files, commands, jobs, git and test VMs.
Three things make long work hold:

- **The handbook**, read at the start of every conversation, so a new chat
  knows how you work together and where to find the project's state.
- **Hash-checked edits**, so writing to a file that changed since it was read
  is refused as `stale` instead of silently overwriting it.
- **Jobs** for anything long: the AI starts the work, then checks on it.

Our operating rule is that root stays with the person. The AI prepares, the
person reads and runs the `sudo` line. That is a working agreement, not a
claim that every command the account can run is harmless.

## More than one of everything

Several AI clients on one Crocodile is a normal Tuesday: Claude and ChatGPT
side by side, each in its own conversation, one building while the other
reviews something else. Chats on one Pond share the account and files, so
give them different work. Hash-checked file tools catch stale edits; they
do not coordinate shell commands, builds or deployments. Agree who owns
those before two conversations work in the same checkout.

Separate Ponds have separate accounts, homes and handbooks, each reached
through its own URL. That separation still depends on the host and
controller: see [Trust](trust.md) for the boundary. Keep one conversation
per Pond; a chat does not forget what it loaded from another.

## What the AI clients do

The clients belong to their vendors, not to us, and change independently.
The [client guide](clients.md) keeps setup paths and compatibility checks.
Three habits have proved more durable than a particular client UI:

- **Use jobs for long work.** A foreground worker request has at most 103
  seconds, including queueing, startup and cleanup; a client can cut off
  earlier. A missing answer does not mean nothing ran. Inspect the receipt
  or resulting state before repeating a command.
- **Make the selected Pond unambiguous.** We have seen clients switch between
  two enabled Ponds' tools in one conversation. Enable only the Pond you
  intend to use when the client permits it, and check the bootstrap identity.
- **Check a reconnection with a read-only tool call.** After changing a URL
  or sign-in, an authenticated indicator alone does not establish that the
  right server and identity are in use. Follow the installed client's
  reconnect procedure, then verify them.

## The neighbours

A Pond rarely works alone.

- **Knowledge, the shared notebook.** The Ponds write down what cost an
  afternoon to find out — a pitfall, a recipe, a version quirk — and another
  Pond reads it the next day. Every entry says who wrote it; revisions and
  confirmations keep it honest. Other agents' notes are notes, not orders:
  check before relying on them. Sometimes a nudge helps: "Try looking in
  the knowledge base first."
- **Fishmarket, the file stall.** A file moves between a Pond and a person's
  browser, either direction, without a shared folder. Links and tokens
  grant temporary access; collection and expiry differ by direction.
  Keep the received file where it belongs, and read the
  [handover lifecycle](https://github.com/the-boring-crocodile/boring-services/blob/main/fishmarket/README.md#how-it-works)
  before relying on a link remaining available.
- **Canvas, the drawing board.** The AI pushes a diagram, the person scribbles
  corrections straight onto it, the AI reads the marks back and redraws.
  Neither has to be good at drawing; pointing beats describing. Supported
  placements return the marks in the current SVG's coordinates; otherwise
  Canvas gives a reason it cannot map them. The
  [coordinate rules](https://github.com/the-boring-crocodile/boring-services/blob/main/canvas/README.md#what-it-offers)
  keep marks on an old or transformed drawing from becoming guessed edits.
- **A Pirate, for handed-off work.** A Pond gives a local agent on another
  provider's model an assignment as a job and reads the result later — useful
  for parallel or cheaper work. Read the result's recorded writes, not just
  its answer: a model sometimes claims checks and fixes that never happened.

## Keeping a Pond's memory: your part

The memory you can inspect and carry between clients lives in the Pond's
files: the handbook (how you work together), the project's records (where
the work stands, what was decided, what is next) and, across Ponds, the shared
notebook. Do not depend on a client's conversational memory to preserve the
working state. A good handbook asks the AI to keep these records, but it
still decides what to write and when. A chat can close, lose context or
disconnect before that happens. These habits cost a sentence each:

- **"Save where we are."** Before you stop, before a long break, and when a
  conversation has run long: the AI updates the status and the next step,
  commits what is done, and says what it saved. The next conversation, in
  any client, starts from there.
- **"Put that into the handbook."** When the two of you settle how you work —
  a rule, a preference, a way of reporting — it belongs in the handbook, or
  the next conversation may not know it. The agreement changes only by
  proposal and your yes.
- **"Write that down for the project."** A decision and its reason, a finding
  with its source, a dead end and why it was one: into the project's records,
  where the next conversation looks first.
- **"Is that worth a note in Knowledge?"** Only for what could save another
  Pond an afternoon — not for the project's own state. Knowledge is a shared
  notebook, not the Pond's memory.
- **"bootstrap", then "where were we?"** — the morning routine from the top
  of this page, which is what makes all the writing-down pay off.

A broken conversation does not erase saved files. It can leave work running,
though: the next conversation should recover retained jobs as well as read
the handoff.

## Windows and Visual Studio

Copilot in Visual Studio gets the same kind of workspace on a D365 dev box
through pondNT: bounded file, command and job tools, plus build, errors,
database, cross-references and a source index, on the box itself.
The [recommended setup](https://github.com/the-boring-crocodile/boring-pondnt/blob/main/docs/INSTALL.md#the-short-way-setupps1)
keeps core and Knowledge direct, with the other selected services behind
Ferry. Workspace and notes are immediately available; specialist tools are
discovered when needed. Whether that means fewer or cheaper Copilot calls
still needs measurement.

## Running it

- **One update path per component.** Linux components use their release's
  `deploy`; pondNT uses `setup.ps1`. Follow [Updating a site](updating.md)
  for preflight, interruptions and rollback. Keeping a previous release
  makes recovery possible; it does not undo changes to data.
- **Rehearse on a copy first.** Use simulated hosts and throwaway VMs for
  installs, removals, updates and recovery. Record the release and cases
  that actually passed: one successful rehearsal is evidence for that path,
  not every machine or client.
- **The person keeps the keys.** Enter credentials through the intended
  sign-in or operator command, not in project files or pasted chat output.
  The AI can prepare the command and interpret a result with secrets removed.

That is the whole practice: write things down, rehearse the breaking, keep
the keys.
