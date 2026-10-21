# How to draw a boring diagram

A portable working recipe for a human or AI collaborator. Read this file
for the complete drawing procedure; the template and tools are execution aids. No Pond, Pirate, model vendor or
Canvas is required. This is a how-to, not an installed agent skill.

## The short loop

0. Read [STYLES](STYLES.md): C4 for the claim, Moody for meaning, Swiss for
   the look -- one page.
1. State the reader's question and establish the facts.
2. Choose one view; write its elements and directed relationships.
3. Compose a small grid using the visual grammar below.
4. Render, check the meaning and geometry, then look at the picture.
5. Correct the source and repeat; deliver source, picture and a short note.

A successful render proves syntax. Geometry checks find some collisions.
Neither proves the architecture or makes the picture readable.

## 1. Establish what the picture claims

Write a small brief before drawing:

- Reader and question: what should become easier to understand?
- View and scope: context, containers, components, deployment or one dynamic
  scenario. Keep one level of architectural detail.
- Basis: proposed design, source architecture at a named revision, or an
  observed deployment at a stated date. These are different claims.
- Elements: stable name, type, short responsibility, useful technology.
- Relationships: source, destination, meaning and protocol where known.
- Boundaries, deliberate omissions, and unresolved facts.

Check maintained project documents and relevant implementation. An attractive
old diagram is a style reference, not evidence of today's architecture.
If facts conflict, resolve them or mark the uncertainty. Never invent a
connection to improve the layout.

For a structural call view, arrows point caller to callee. For a mail or data
journey, they follow that flow. Explain the meaning in the key; do not quietly
switch between call direction and data direction. Two distinct directions
need two arrows. A dynamic view gives each step its own number and explanation.

Aim for roughly 5–9 meaningful elements. Split a crowded story into linked
views; retain required facts or explicitly state what the narrower view omits.
A tunnel or queue carrying several flows may need its own element. Do not
erase a real isolation boundary merely to reduce the box count.

## 2. Keep the three layers separate

Our software-diagram approach has three layers:

| Layer | Question | Our approach |
| --- | --- | --- |
| Model | Is the architectural claim true? | C4 views and explicit relationships |
| Picture | Can the reader distinguish meanings? | Moody: consistent symbols, words as well as visual cues |
| Look | Is the composition calm and readable? | Swiss: alignment, typography, spacing and restraint |

For maintained house-style diagrams, use editable Graphviz DOT and SVG.
For a small conversational diagram, the same reasoning can inform an available
inline renderer; follow its own syntax and inspection capabilities. Do not
pretend the Graphviz checkers validate another format. A sentence or table is
enough when a picture adds no understanding.

## 3. Borrow the grammar, not the topology

Use these starting values, then size for the actual content:

- White ground, dark text, one sans-serif family; Helvetica at 18 / 12 / 10
  points for title / names / detail is our established starting recipe.
- Left-aligned title and box text. A name, a type/technology line, then one
  or two lines explaining the job.
- Equal, comfortably padded boxes for comparable elements. Boundaries and
  legends have different jobs and need not share that size.
- Pale blue `#edf2fa`, sage `#edf5ef`, neutral `#f5f5f3`;
  text `#111111`. Give categories explicit meanings and explain them.
  Preserve mappings across related views; never rely on colour alone.
- Group by real ownership, deployment or responsibility. Label what each
  frame means. A deployment frame does not automatically mean one network.
- Use aligned rows/columns, generous frame margins (24–28 points is a useful
  start), and more space between groups than between related elements.
- Prefer straight connections following box centres, clipped at their borders.
  Minimise crossings without changing the relationships.
- Use colour plus line style for protocol families and explain the mapping
  once. Name grouped protocols explicitly; do not imply they are identical.
- Omit repetitive arrow text only where endpoints, direction and key make
  the meaning unambiguous. Otherwise use a short verb.
- Compose the key with the drawing. Default to three compact, aligned
  columns beneath the view; follow the legend guidance below.

Title the diagram with its subject, view, scope and the version or source it
describes; add a date only for an observed deployment, where the moment is the
point. State target versus observed status. Include a key for the visual vocabulary actually used.

[TEMPLATE.dot](TEMPLATE.dot) supplies editable syntax for an invented system.
Its shared HTTPS/SMTPS style denotes the stated TLS family. Replace its facts
and choose the topology from your source evidence. Icons are optional and
are not prebuilt in the template.

### A compact three-column legend

Use this compact arrangement by default for a landscape view:

| Read the picture | Connections | Scope and limits |
| --- | --- | --- |
| Box types, colours, boundaries and any non-obvious pictograms | Arrow direction, line styles and protocols | Essential omissions, evidence status and unresolved claims |

Use short headings and a few short, left-aligned lines per column; roughly
three to five lines is a starting budget, not a reason to omit a critical
qualification. Align the column tops, keep comfortable gutters, and use the
existing name/detail type sizes. Keep the key within the view's width.
Leave comfortable breathing room while keeping the legend visually attached
to its diagram. Judge the rendered gap: Graphviz rank spacing and table
padding can add together. Related views should use consistent headings.

The key explains how to read the picture. Put detailed source references,
test history, operational instructions and extended caveats in the companion
evidence note. Keep any qualification that changes the picture's meaning
visible in the drawing: for example, file recovery does not prove server
recovery. Do not hide such limits to make the legend shorter.

If the key becomes a paragraph wall, shorten repeated wording or split the
view. Do not shrink the type to make it fit. For a narrow output, fewer
columns are acceptable when they improve reading; three columns are a
composition default, not a rigid format.

Inspect the whole page: the diagram should remain the main visual focus.
The key must be readable at the same intended viewing size as the box detail.

### Quiet pictograms, clean boxes

Keep the calm, consistent rectangular boxes. Folder tabs and cylinders as
whole node silhouettes are not the default. Use a special outer shape only
when it materially helps the reader; a written type remains required.

An optional small pictogram inside the rectangle can reinforce recognition.
It is a decorative, redundant cue: the complete meaning must survive its
removal. Text first, pictogram second.

- Reserve a consistent space at the right of the text, with comfortable
  padding. Keep the text column clear; do not squeeze or overlap labels.
- Use one restrained outline icon per element, consistent optical size,
  position and stroke weight across comparable boxes. Start around 24–32
  points in a roughly 295-by-90-point box, then judge at reading size.
- Use a subdued version of the existing text or border colour with enough
  contrast to remain legible. No bright accents, badge backgrounds, shadows,
  emoji or vendor logos. The icons must not dominate the page.
- Choose truthful cues: folder for files, archive box for retained archives,
  cylinder for an actual database, code brackets for source code. A Borg
  repository is an archive store; do not imply that it is a database.
- Reuse the same cue for the same meaning. Omit an icon if its meaning is
  ambiguous. Explain any non-obvious cue briefly in the key.
- Keep the outer rectangles, alignment, spacing and typography consistent.
  Split views rather than packing more text around the decoration.

Use local, editable vector geometry. Keep icon assets and any deterministic
SVG insertion script with the DOT source; do not depend on an icon font,
remote asset or manual Canvas overlay. Graphviz should still lay out the
nodes and relationships. If icons are inserted after rendering, check and
visually inspect the final SVG, not only the intermediate output. Geometry
checkers do not prove icon/text clearance or visual restraint.

At whole-page size the composition should still read as the clean diagram;
at reading size the pictograms should gently help recognition. Compare a
version with and without them when uncertain. Approval of the style does
not establish the correctness or quality of a new drawing.

### Choose the form before the layout

Lessons from drawing the Pond family's documentation:

- **Draw for where it is read.** A GitHub page shows a picture about 660 pt
  wide at full size; a wider one is scaled down until its text is too small.
  Check the rendered width (layoutcheck prints it). Reshape a wider view (two
  columns instead of one long column, lanes instead of a spread) or split it.
  The deploy view went from 1330 pt to 555 pt this way.
- **Sequences as lanes.** A process over time (a deploy, a sign-in) reads
  better as a dynamic view in lanes than as boxes and arrows: one lane per
  place or actor, time running downward, each step a small numbered chip in
  its lane. Mark the moment that matters in the picture itself, with a
  labelled line across the lanes (`tools/divider.py`, for example "Point of no
  return"), not only in the key.
- **Not every view needs a picture.** When every relationship is the same (one
  client calling five servers alike), the picture makes a single claim: say it
  in a sentence and put the per-item facts (port, account, start) in a table.
  A table is easier to read, search and keep current.
- **Fewer colours.** Colour only what the reader needs for the question. When
  the lanes already say where something happens, a colour for the same
  distinction is noise.
- **Name box and line colours apart in the key** ("Pale blue box", "Blue
  line"). One word for two things is Moody's symbol overload.
- **Graphviz cannot draw overlaps.** A grouping picture (frames that overlap,
  a family picture) can be placed by hand: a small generator script on a grid,
  with the kit's icon paths (`ICONS` in `tools/icons.py`), palette and type
  sizes. textcheck still applies; layoutcheck needs Graphviz JSON and does not,
  so the visual review carries more of the weight.

## 4. Give Graphviz a composition

Start with `rankdir=TB, splines=line, newrank=true`. Rows, groups and
invisible constraints can express the composition while Graphviz lays it out.

| Problem | Technique and limit |
| --- | --- |
| Keep a column aligned | Give its boxes the same `group`; inspect the result. |
| Keep a row together | Use `{rank=same; a; b;}` in the appropriate frame. |
| A same-row arrow pulls boxes together | Try `weight=0` on that relationship. |
| A visible line bends unexpectedly | Avoid an invisible twin between the same endpoints; put the weight on the real edge. |
| Edge text spreads the ranks | Try `xlabel` for necessary short text; inspect placement. |
| Centre a box below two others | Two invisible zero-width spacers pinned beneath the upper boxes can hold it between them. |
| Put a callee above its caller | Prefer ordinary semantic edges first. If using `dir=back`, verify the rendered arrowhead, not the DOT statement order. |
| Labels overflow | Wrap the text or enlarge comparable boxes together; treat Graphviz warnings as defects. |

These are observed techniques, not guarantees for every graph. Avoid piling on
layout constraints when a different row order or a split view makes the story
simpler. Ports are an advanced exception for parallel opposing paths; HTML
ports can end inside padding. Inspect arrow tips at the visible box border;
keep opposing flows separate and check each direction after layout.

For numbered straight dynamic edges, keep step numbers in `xlabel` and use
`tools/badges.py` after rendering. It places circles on the arrows; it does
not determine whether the steps are correct.

Post-processors run in a pipe after `dot -Tsvg`; run the checks on the final
file:

| Tool | What it adds |
| --- | --- |
| `tools/icons.py` | A quiet pictogram at the right of each node with `class="icon-NAME"` (person, code, file, folder, link, running, chat, route, container, agent, system). |
| `tools/badges.py` | Step numbers from `xlabel` as circles on straight arrows; a badge that would sit on a frame line slides along its arrow until clear. |
| `tools/divider.py A B "Label" [#colour]` | A dashed, labelled line across all frames, halfway between nodes A and B (lane views). |
| `tools/darkmode.py light.svg dark.svg` | The dark twin (see section 6). |

A `dir=back` edge confuses badges.py, which takes the arrowhead end as the
start; prefer ports or `constraint=false` for a callee drawn above its caller.

## 5. Render and check three different things

Prerequisites: Graphviz with SVG/JSON output and Python 3 for the checkers.
Optional image inspection uses an SVG viewer, or a rasterizer and image viewer.
Keep the kit read-only and work in a separate directory. Set `diagram_kit`
to the absolute path of this kit, copy TEMPLATE.dot into your work directory
as diagram.dot, and edit that copy. From your work directory run this in Bash
(replace the example kit path):

```bash
(
set -euo pipefail
diagram_kit=/absolute/path/to/boring-diagrams
mkdir -p output
dot -Tsvg diagram.dot -o output/diagram.svg 2>output/render.log
cat output/render.log
test ! -s output/render.log
dot -Tjson diagram.dot -o output/diagram.json 2>output/layout-render.log
cat output/layout-render.log
test ! -s output/layout-render.log
python3 "$diagram_kit/tools/textcheck.py" output/diagram.svg
python3 "$diagram_kit/tools/layoutcheck.py" output/diagram.json
)
```

This stops on a failed command or renderer diagnostic. A later command's exit
status must never be reported as an earlier check's success. Keep failed
diagnostics, fix their cause, and rerun. If one check stops the block, subsequent
checks have not run.

For a dynamic drawing, render an intermediate SVG, then run
`python3 "$diagram_kit/tools/badges.py" < output/diagram.svg > output/diagram-numbered.svg`
with `diagram_kit` set in that shell;
text-check and visually inspect that final numbered file too.

**Meaning:** compare the expected relationship list with layoutcheck's
`arrows as read`, including both directions and repeated steps. Account for
every expected edge and every rendered edge: missing, extra and reversed are
all defects. The current tool prints directions; it does not compare them
against the brief. Its exit 0 is not proof that the arrows are correct.

**Geometry:** textcheck approximates edge/text collisions; layoutcheck
approximates edge/box intersections and reports sizes, alignment and crossings.
Layoutcheck exits non-zero for edge/box intersections, not for every reported
layout issue. Neither proves label fit, semantic correctness or visual quality.
Use the acceptance checklist below for the final review.

**Appearance:** actually open the final rendered picture. Inspect the whole
composition at intended reading size, then readable crops for labels and
arrowheads. Check clipping, overflow, crossings, frame labels, legend fit,
contrast and balance. Then look for broken patterns: like things are drawn
alike. Arrows into one box end the same way (all aimed at its centre, or all
at the same kind of port); paired arrows between two boxes share one spacing;
columns and the key line up. One exception among regular neighbours stands
out to a human reader at once, and the geometry checkers do not see it.
If a rasterizer is available, `tools/tiles.py` can split
a PNG into readable pieces (requires Pillow). Looking at tiles alone does not
establish that the whole composition works.

If image inspection is unavailable, say the visual review remains unverified.
Do not infer it from clean tool output. An AI saying “all arrows correct” or
“looks good” is also not evidence by itself.

Two or three focused corrections are often enough. If the drawing remains
crowded, revisit the view instead of endlessly nudging it.

## 6. Deliver and preserve

Keep editable DOT, final SVG and a brief note together in the owning project.
The note records the question/view, source revisions or observation date,
omissions, doubts, render command, tool versions when relevant, checks actually
run and visual-review limits. Record any post-processing needed to reproduce
the delivered SVG. Never claim human approval before it happens.

**Light and dark.** GitHub can show a different file per reader theme. Write
the dark twin with `python3 tools/darkmode.py diagram.svg diagram-dark.svg`.
It maps every colour by the rule Excalidraw uses for its dark theme (invert
93 %, then hue-rotate 180 degrees): lightness flips and hues stay, so the key
still holds. Embed both, with an alt text that tells the whole picture:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagram-dark.svg">
  <img alt="..." src="diagram.svg">
</picture>
```

Look at the dark twin too.

If using a shared canvas, discover its current API. For a new subject create a
new canvas; refine the same canvas for that subject. Read annotations against
the correct image revision, update the source, then render again. Tell the
reader whether to open a new URL or reload the existing one. A canvas is a
review surface; the repository owns the source.

When the architecture changes, update or retire its maintained diagram.
Preserve dated examples as history rather than silently presenting them as live.

## Final acceptance checklist

- [ ] The title states question/view, scope, and the version, source or observed deployment.
- [ ] Elements name their type and purpose; abbreviations suit the reader.
- [ ] Every expected relationship is present, with correct direction and meaning;
      no unexplained extra edges. Number each step in dynamic scenarios.
- [ ] Boundaries and omissions are truthful; important uncertainties stay visible.
- [ ] Colours, line styles and symbols have consistent, explained meanings;
      text supplies the meaning too. Related views use the same vocabulary.
- [ ] Comparable rectangles align and have comfortable padding; typography is
      consistent, and optional pictograms are quiet and clear of text.
- [ ] The compact legend belongs visually to its view; it does not dominate it.
- [ ] Like things look alike: arrows into one box end the same way, paired
      arrows share one spacing, columns and the key align.
- [ ] The drawing carries an explicit background. Check contrast in the actual
      viewer; dark-mode transformations can change its appearance.
- [ ] Renderer diagnostics are resolved, checker results inspected, and the
      final picture actually viewed at whole-page and readable-detail scales.
- [ ] DOT, SVG, reproduction assets and evidence note agree. State checks that
      were unavailable and leave human approval pending until given.
- [ ] Fits where it is read (about 660 pt wide for a GitHub page). A sequence
      is drawn as lanes; a view whose relationships are all alike is a table.
- [ ] The key names box colours and line colours apart; no colour repeats what
      position already says.
- [ ] Where shown on GitHub: dark twin written, viewed and embedded with
      `<picture>`.

## Taking this knowledge elsewhere

Copy this whole small kit, keeping its relative paths. Check Graphviz, Python
and fonts in the destination; optional tiles.py needs Pillow and a rendered
PNG. No original repository or Pond service is required. For a new assignment,
provide the reader's question, source facts or revision, allowed reads/writes,
output location and whether Canvas publication is requested. Read HOWTO.md;
use TEMPLATE.dot and tools only as needed.
