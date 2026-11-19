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
| **The Engineer** | Code, systems, releases | Builds things that hold, says plainly what it has not checked | [the Steady Beaver](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/src/boring_crocodile/handbooks/engineer/HANDBOOK.md) `('')##=` |
| **The Consultant** | Research and concepts: finding out, thinking through, writing up | Looks until it sees clearly, then answers once; every finding has a place, a source and a date | [the Tidy Kingfisher](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/src/boring_crocodile/handbooks/consultant/HANDBOOK.md) `--<o)` |

Each handbook has a character of its own, named in the last column. The
examples below use `beaver-user` and `engineer`; [getting started](../docs/getting-started.md)
uses `crocodile-user` and the neutral starter. Keep the character or rename
it as the Pond becomes yours.

The Crocodile release owns and ships these files. This repository keeps the
index and links. Each packaged choice has `HANDBOOK.md`, `WELCOME.md` and
the shared [Operating this Pond together](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/src/boring_crocodile/handbooks/OPERATING_TOGETHER.md)
page. None is a copy of a handbook in use.

## Installing one

**A new Pond.** Run `sudo boring-crocodile-setup --wizard --apply` and choose
`starter`, `engineer` or `consultant` at the handbook question. The release
supplies those files: no clone or JSON file is needed. For another Pond, use
`--add-pond NAME --wizard --apply`; the site's controller is reused.

Setup seeds missing files in the Pond's `handbook/` and records their reading
order and welcome filename. Existing files remain yours and are never replaced
by a setup rerun or software update. Importing your own selected files and saving
optional setup inputs remain available. The full walk:
[getting started](../docs/getting-started.md).

**An existing Pond.** Changing its handbook is a deliberate content change:
keep an archive, review the selected release-owned files and context settings,
and follow [context configuration](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/TOOLS.md#context-pond_bootstrap)
and [changing configuration](https://github.com/the-boring-crocodile/boring-crocodile/blob/main/docs/OPERATIONS.md#changing-configuration).

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
