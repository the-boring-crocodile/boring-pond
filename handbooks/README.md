# Sample Ponds

A Pond's **handbook** is what the AI reads at the start of every conversation:
who it is, what it may do, how it works and where things stand. Its real
job is the third: so that every conversation starts from the same
engineering principles, rather than from whatever the last one drifted
into ([why](../docs/story.md#memory-is-the-means-discipline-is-the-point)). A fresh Pond
gets a short, neutral starter. These two are complete handbooks, written
from what worked for us over weeks of real work. Install one, and the Pond
works that way from its first conversation.

| Sample | For | How it works | Handbook |
|---|---|---|---|
| **The Engineer** | Code, systems, releases | Builds things that hold, says plainly what it has not checked | [the Steady Beaver](steady-beaver/HANDBOOK.md) `('')##=` |
| **The Consultant** | Research and concepts: finding out, thinking through, writing up | Looks until it sees clearly, then answers once; every finding has a place, a source and a date | [the Tidy Kingfisher](tidy-kingfisher/HANDBOOK.md) `--<o)` |

Each handbook has a character of its own, named in the last column; the
examples below and in [getting started](../docs/getting-started.md) use
those names (`beaver-user`, `steady-beaver/`). Keep the character or rename
it as the Pond becomes yours.

Each folder holds two files: `HANDBOOK.md` and a short `WELCOME.md` that tells
the AI to read it and how to say it is ready. Neither is a copy of a handbook
in use.

## Installing one

**A new Pond.** Give setup the folder as the starting context. In the inputs
file for the first Pond (or for `--add-pond`), instead of the packaged starter:

```json
{
  "execution_user": "beaver-user",
  "control_user": "crocodile-mcp",
  "home": "/home/beaver-user",
  "context_mode": "import",
  "context_source": "/path/to/boring-pond/handbooks/steady-beaver",
  "context_files": ["HANDBOOK.md", "WELCOME.md"]
}
```

Setup copies both files into the Pond's `handbook/` and configures them as its
context. The whole walk from download to a first conversation:
[getting started](../docs/getting-started.md).

**An existing Pond.** Copy both files into its `handbook/`, keep the old
documents in an archive, and have the administrator set the Pond's context
files to `["HANDBOOK.md", "WELCOME.md"]` and reload
([context configuration](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/TOOLS.md#context-pond_bootstrap-pond_profile-pond_ping-pond_limits),
[changing configuration](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#changing-configuration)).

## The first conversation

No questionnaire. The handbook states its defaults (it stays in its home
folder; root, deploys, deleting and sending stay with you) and asks one thing:
*what are we building first?* or *what do you want to find out first?* Other
choices are asked when they come up and noted in the handbook.

To check it took: start a second, fresh conversation and ask for the
bootstrap by the connector's name ("bootstrap Steady Beaver"). It
should come back with its ready line, its boundaries and where things stand.

## Making it yours

The handbook changes as you work: state and practice freely, the agreement
only by proposal and with your yes, with the old wording kept in history. That
rule is what keeps it from drifting. Software updates never overwrite it.

It is working guidance, not a grant of access or a technical isolation
mechanism: tool permissions and host policy decide what the AI can do. Choose
what may be saved knowing that future conversations in this Pond can read it.
