# The three styles, on one page

Read before every diagram. Three schools, three jobs, no overlap:

| Layer | School | Decides | Question it answers |
|---|---|---|---|
| The model | **C4** (Simon Brown) | what the diagram claims | Is it true? |
| The picture | **Moody**, *Physics of Notations* (2009) | which visual variables carry meaning | Can it be read without error? |
| The look | **Swiss style** (International Typographic Style) | everything that carries no meaning | Is it calm and easy on the eye? |

Moody owns every property that *means* something. Swiss sets every property
that means nothing, and never takes one of Moody's. C4 says nothing about
either.

## C4: what the diagram claims

Levels, one per diagram: **context** (the system, its users, other systems),
**containers** (applications and data stores), **components** (inside one
container), **code** (left to UML or the IDE). Supplementary: deployment and
dynamic views. Building blocks: person, software system, container,
component, relationship. A **container** is a runtime boundary (an
application or data store that must run), not a Docker container and not a
package; each queue or topic is its own container, never one "bus". C4 sees
readability drop at about 20 elements; our working target is 5-9.

The notation rules (c4model.com, "Notation"):

- **Title** stating the diagram's type and scope.
- **Key** explaining every shape, colour, border, line style and arrowhead,
  even for a "standard" notation.
- **Elements** name their type, carry a short description of their
  responsibility, and (containers, components) their technology.
- **Relationships** are one-directional lines, each labelled to match its
  direction and intent, specific rather than "uses"; between containers, name
  the technology or protocol.
- **Acronyms** understandable to all readers, or explained in the key.
- **Colour** is free, but consistent within and across diagrams; survive
  black-and-white printing and colour blindness.
- The diagram **stands alone**, understood without someone talking it through.

Ours on top: where a label per arrow crowds the picture, the key may say what
each line style carries -- the meaning must still be
written down somewhere on the picture.

## Moody: what may carry meaning

Moody separates *information-carrying* visual variables from *free* ones.
Per diagram we decide which variables carry meaning; every other one stays
constant, and that constant setting is the Swiss layer's job. Varying a
free variable anyway is symbol excess.

Nine principles for notations people read correctly:

1. **Semiotic clarity** -- one symbol per concept, one concept per symbol. No
   *overload* (one colour meaning two things), no *redundancy* (two symbols
   for one thing), no *excess* (symbols meaning nothing), no *deficit* (a
   meaning with no symbol -- allowed on purpose when text carries it).
2. **Perceptual discriminability** -- different meanings look clearly
   different, ideally in more than one variable (colour *and* dash). Shape is
   the strongest variable; label text alone is zero visual distance.
3. **Semantic transparency** -- a symbol suggests its meaning (a person icon
   for a person); never one that suggests the wrong thing.
4. **Complexity management** -- split into several diagrams, modules or
   levels rather than one crowded one.
5. **Cognitive integration** -- several diagrams fit together: same names,
   same symbols, a way to see where one sits in another.
6. **Visual expressiveness** -- use the visual variables deliberately:
   position, size, value (brightness), colour, texture, shape, orientation
   (Bertin; hue and shape suit categories, size and value suit order).
7. **Dual coding** -- text complements every graphic symbol; nothing is
   colour-only.
8. **Graphic economy** -- few symbol types, so a reader can hold them all;
   Moody puts the limit around six per variable.
9. **Cognitive fit** -- a dialect suited to the reader and task (novices need
   more text, experts can take denser symbols).

Ours on top: like things are drawn alike -- arrows into one box end the same
way, pairs share one spacing, columns and the key align.

## Swiss style: everything else

The International Typographic Style (Zürich and Basel, 1950s-60s; Keller,
Müller-Brockmann, Hofmann, Ruder; Tschichold's *Die neue Typographie*, 1928):

- **Grid** -- a mathematical grid anchors every element; one spacing unit.
- **Sans-serif type** -- one family (Helvetica, Univers, Akzidenz-Grotesk),
  few sizes; hierarchy by size and weight.
- **Flush left, ragged right** -- not centred, not justified.
- **Asymmetry and white space** -- balance through empty space rather than
  mirroring; more space around groups than inside them.
- **Objectivity** -- the content speaks; no decoration, no persuasion, no
  personal flourish. Illustration was avoided as too subjective.
- **Colour** sparse and purposeful.

In our Graphviz: Helvetica at 18/12/10; title and box text flush left; boxes
of one kind one size and in columns; straight lines; explicit white
background; colour only where Moody gave it a meaning; quiet outline
pictograms that repeat the element type in words, never replace it.

## Sources

- [C4 model, "Notation"](https://c4model.com/diagrams/notation) and
  [Wikipedia, "C4 model"](https://en.wikipedia.org/wiki/C4_model)
- D. Moody, "The 'Physics' of Notations", IEEE TSE 35(6), 2009; principle
  definitions as summarised in
  [arXiv 2304.08654](https://arxiv.org/pdf/2304.08654) (Table II). The terms
  overload/redundancy/excess/deficit, free variables and the limit of about
  six are checked against secondary sources (the paper is paywalled); the
  authoring project keeps longer references on all three schools.
- [Wikipedia, "Visual variable"](https://en.wikipedia.org/wiki/Visual_variable) (Bertin)
- [Wikipedia, "Swiss Style (design)"](https://en.wikipedia.org/wiki/Swiss_Style_(design))
  and [Lumen, "International Typographic Style"](https://courses.lumenlearning.com/suny-graphicdesign/chapter/1-6-international-typographic-style/)
