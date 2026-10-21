# In practice

A report from inside: the Pond family was built by the thing this page
describes — AI assistants working in Ponds, for weeks, with their operator —
and these are the habits that survived. Not a feature list; the component
docs say what each part can do. This is what a working day looks like.

## A conversation begins

The clients load a Pond's context only when asked: a plain "Hello" gets a
plain hello back. Start with "bootstrap" and the connector's name —
"bootstrap Steady Beaver"; in ChatGPT "@Tidy Kingfisher bootstrap" — and the
Pond reads its handbook and says it is ready. Ask "where were we?" and it
reads the project's status and tells you, before anything else happens.

## The work itself

The family itself was built this way: Claude and ChatGPT working in Ponds
across several repositories, with files, commands, jobs, git and test VMs.
Three things make long work hold:

- **The handbook**, read at the start of every conversation, so a new chat
  picks up where the last one left off.
- **Hash-checked edits**, so writing to a file that changed since it was read
  is refused as `stale` instead of silently overwriting it.
- **Jobs** for anything long: the AI starts the work, then checks on it.

And one thing that never changes: root stays with the person. The AI
prepares, the person reads and runs the `sudo` line.

## More than one of everything

Several AI clients on one Crocodile is a normal Tuesday: Claude and ChatGPT
side by side, each in its own conversation, one building while the other
reviews something else. Nothing needs arranging. Several chats on one Pond
also works — they share the account and files, so give them different work,
and the hash-checked writes turn a collision into a `stale` refusal. Several
Ponds keep separate work, and separate people, genuinely separate: each is
its own account, home and handbook, reached by its own URL. Keep one
conversation per Pond; a chat does not forget what it loaded from another.

## What the AI clients do

The clients belong to their vendors, not to us. These are the things they
decide, and what we do about each:

- **A tool call has about two minutes.** ChatGPT ends one after about 120
  seconds, leaving the command's outcome unknown; other hosted clients may
  cut sooner or later. So a Pond answers every foreground call within 103
  seconds and says when a command may have started but was cut off; anything
  longer runs as a job.
- **With several Pond connectors in one chat, they wander.** Claude and
  ChatGPT both switched between two Ponds' tools as they saw fit. Telling
  them not to works — the server instructions and the sample handbooks say
  to stay with the bootstrapped Pond — but the simple answer is to switch on
  only the Pond you work with.
- **ChatGPT applies a connector choice to one message.** Name it again in
  follow-ups.
- **A changed URL needs a new connector in Claude.** Claude cannot edit a
  connector, and when the Pond behind one is gone it does not offer a fresh
  sign-in: remove it and add it again. ChatGPT notices on its own and asks
  you to sign in again.

## The neighbours

A Pond rarely works alone.

- **Knowledge, the shared notebook.** The Ponds write down what cost an
  afternoon to find out — a pitfall, a recipe, a version quirk — and another
  Pond reads it the next day. Every entry says who wrote it; revisions and
  confirmations keep it honest. Other agents' notes are notes, not orders:
  check before relying on them.
- **Fishmarket, the file stall.** A file moves between a Pond and a person's
  browser, either direction, no shared folders: a link, a separate token,
  and the file is gone after collection or a day.
- **Canvas, the drawing board.** The AI pushes a diagram, the person scribbles
  corrections straight onto it, the AI reads the marks back and redraws.
  Neither has to be good at drawing; pointing beats describing. Today the AI
  maps the marks to its drawing's coordinates by hand each round.
- **A Pirate, for handed-off work.** A Pond gives a local agent on another
  provider's model an assignment as a job and reads the result later — useful
  for parallel or cheaper work. Read the result's recorded writes, not just
  its answer: a model sometimes claims checks and fixes that never happened.

## Keeping a Pond's memory: your part

An AI remembers nothing between conversations. What carries over is what was
written into the Pond's files: the handbook (how you work together), the
project's records (where the work stands, what was decided, what is next)
and, across Ponds, the shared notebook. A good handbook makes the AI keep
those records on its own — but it decides what is worth writing down and
when, and a conversation can end before it gets there: the chat is closed,
the client trims a long conversation, a connection drops. So the person
driving keeps an eye on it. These habits cost a sentence each:

- **"Save where we are."** Before you stop, before a long break, and when a
  conversation has run long: the AI updates the status and the next step,
  commits what is done, and says what it saved. The next conversation, in
  any client, starts from there.
- **"Put that into the handbook."** When the two of you settle how you work —
  a rule, a preference, a way of reporting — it belongs in the handbook, or
  the next conversation will not know it. The agreement changes only by
  proposal and your yes.
- **"Write that down for the project."** A decision and its reason, a finding
  with its source, a dead end and why it was one: into the project's records,
  where the next conversation looks first.
- **"Is that worth a note in Knowledge?"** Only for what could save another
  Pond an afternoon — not for the project's own state. Knowledge is a shared
  notebook, not the Pond's memory.
- **"bootstrap", then "where were we?"** — the morning routine from the top
  of this page, which is what makes all the writing-down pay off.

If a conversation ends abruptly, nothing in the files is lost; only what was
said and not yet written down is.

## Windows and Visual Studio

Copilot in Visual Studio gets the same kind of workspace on a D365 dev box
through pondNT: bounded file, command and job tools, plus build, errors,
database, cross-references and a source index, on the box itself. It connects
and works; whether it really means fewer and smaller Copilot calls is still
to be measured, and we say so rather than guess.

## Running it

- **One command per component.** Every part installs, updates and rolls back
  with its release's `deploy`; the previous release stays for rollback, and a
  first deploy installs. Updates on the live host are a short, boring step.
- **Rehearse on a copy first.** Changes to the live host run first on a
  simulated host and throwaway VMs: install, uninstall, reinstall, moves and
  their rollbacks. By the time the live host sees a change, it has already
  happened at least once.
- **The person keeps the keys.** Secrets, passwords and root never pass
  through a Pond or a chat: the AI writes the exact command, the person runs
  it and pastes back the outcome.

That is the whole practice: write things down, rehearse the breaking, keep
the keys.
