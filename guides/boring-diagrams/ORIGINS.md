# How Boring Diagrams took shape

Boring Diagrams began with a drawing that was supposed to explain a
development environment. The boxes were there, the connections were there,
and understanding it still took too much work. Lines crossed labels, routes
wandered across the page, and every adjustment to the hand-positioned SVG
created another set of coordinates to maintain.

Moving to Graphviz helped. Relationships became editable source, and an
engine took responsibility for placing and connecting the elements. That
made revision easier. Making the result clear and attractive still required
some learning.

## Finding a visual language

Ask an AI for a diagram without steering it and you get a mashup of
everything it has ever seen: a gradient from one tradition, icons from
another, five colours that mean nothing, and arrows in three styles. Each
part looks familiar; together they say little. We did not want a style that
was the average of all styles.

Wald's answer was to split the problem before anything was drawn. A diagram
that is good to read answers three separate questions, and each got one
owner:

- **Is it true?** What the picture claims about the system: which things
  exist, how they relate, where the boundaries are. C4 owns that.
- **Can it be read without error?** Which visual properties carry meaning,
  and how many distinct values each may have before readers confuse them.
  Daniel Moody's *Physics of Notations* owns that.
- **Is it calm?** Alignment, spacing, type, and restraint for everything that
  carries no meaning. Swiss typography and composition own that.

Every one of those questions has rival schools, each with devoted
followers. For each, we looked at the leading candidates and chose one. Not
the best of several, blended: a blend would have let the mashup back in
through the side door.

The owners do not overlap. Moody decides every property that *means*
something; Swiss styles only what means nothing and never takes one of
Moody's; C4 says nothing about looks. When a drawing goes wrong, the
question it fails tells you which owner to ask.

Those ideas became practical decisions: a manageable number of elements,
explicit boundaries, consistent colours, left-aligned text and comfortably
padded boxes. Service architectures and mail flows gave the approach real
work to do. A colour carrying several meanings had to be reconsidered. A
line crossing a label needed a layout correction. An explanation crowding
the page often meant the view was trying to answer too many questions.

The style emerged through that repeated exchange between source, rendered
picture and human review. Editable DOT and SVG made each correction something
we could preserve and reproduce.

## Learning to distrust a tidy result

Delegating drawings to AI collaborators revealed another problem. A diagram
could look plausible while reversing a relationship or leaving one out.
A confident report could claim that checks had passed even when the output
showed warnings or overflowing labels. Giving a model the ability to inspect
its picture helped some attempts, but did not make its judgement reliable.

That experience shaped the checking loop. Establish the relationships before
drawing. Compare them with the rendered arrows. Read the actual diagnostics.
Then look at the finished picture. Small geometry tools help find collisions
and expose arrow directions, while the author still has to establish what
the system does and whether the explanation makes sense.

It also made visual review a first-class part of the work. Correctness,
readability and appearance need attention throughout the process.

## Making the knowledge portable

Eventually the useful question became whether a new collaborator could draw
well using the written guidance alone. We copied the procedure into a kit
and used backup and recovery flows as a fresh subject. New chats were asked
to work without the original drawing project or earlier results, using the
same source snapshot so the drawings could be compared.

Their compositions differed, but the visual language carried across. The
comparison also sharpened it. Clean rectangles felt calmer than entire
boxes shaped as folders or databases. Small outline pictograms preserved
that calm while helping recognition. Three short legend columns were easier
to scan than a long stack of notes.

Even the space above a legend taught us something. Graphviz's row spacing
and table padding added together, pushing the explanation away from its
diagram. Bringing it closer restored the sense that they belonged together.
The guide now asks the drawer to judge that visible relationship.

The portable kit was then stripped back to the working instructions, a
template and a few tools. The research and historical examples stayed in
the authoring project. A new collaborator should be able to start drawing
without reconstructing the conversations that taught us how.

## A collaborative craft

Wald set the goals, challenged the results and supplied visual judgement.
OpenAI assistants and Anthropic's Claude both contributed substantially to
the diagram work under his direction. Their drawings, revisions and the
lessons from separate model trials became the material for this guide.

The result is a practical method developed through use. It still depends on
judgement: selecting the right facts, choosing a useful view and recognising
when a picture needs another pass. Boring Diagrams gives that work a small,
repeatable structure—and keeps the source available when the next person
needs to change it.
