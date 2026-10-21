# Boring Diagrams

Readable diagrams, explicit claims, editable sources.

Boring Diagrams is a small practical guide and Graphviz toolkit for humans
and AI collaborators. It helps turn project documents and implementation
into diagrams that explain a system: consistent boxes, restrained colour,
quiet pictograms and compact legends, with evidence behind the arrows.

Developed through hands-on work in the Pond, it can be used independently.
No Pond runtime, Canvas service, model vendor or account is required to draw
and check a diagram. It is intended to accompany the Pond family as a
standalone guide.

## Start drawing

Read [HOWTO.md](HOWTO.md). It contains the complete working procedure and
acceptance checklist. You do not need to read the project history first.

1. Define the reader's question and identify the source facts.
2. Create a separate working directory. Copy [TEMPLATE.dot](TEMPLATE.dot)
   there as diagram.dot; replace its invented system with your own.
3. Follow HOWTO.md to render, check relationships and geometry, and inspect
   the actual picture. Keep the kit unchanged while drawing.
4. Deliver editable DOT, SVG, any reproduction assets and a short evidence
   note stating the basis, omissions and checks performed.

Required: Graphviz with SVG/JSON output and Python 3. Visual review needs an
SVG viewer or a rasterizer and image viewer. The optional PNG tiling tool
also needs Pillow. Fonts and renderer versions can affect layout.

## What is included

| File | Purpose |
| --- | --- |
| HOWTO.md | Facts, composition, pictograms, legends, checks and delivery |
| TEMPLATE.dot | Editable syntax for a small invented system |
| tools/textcheck.py | Approximate edge/text collision checks |
| tools/layoutcheck.py | Box intersections, alignment, crossings and rendered arrow directions |
| tools/icons.py | Optional quiet pictograms in boxes that ask for one |
| tools/badges.py | Optional numbered circles on straight dynamic edges |
| tools/divider.py | Optional labelled line across lane frames |
| tools/darkmode.py | The dark-mode twin of a drawing, for GitHub's `<picture>` |
| tools/tiles.py | Optional overlapping PNG crops for visual inspection |
| ORIGINS.md | How the approach developed and what the trials established |
| SHA256SUMS | Integrity manifest; run `sha256sum -c SHA256SUMS` here (after changing a file of your own copy, regenerate it) |

## What checking means

A successful render proves syntax. Geometry tools catch some defects.
Neither establishes that the system description is true or the picture is
pleasant to read. Compare every relationship with the source facts and look
at the final render. Human visual review remains part of the process.

The fuller guide was exercised in fresh-chat backup-diagram trials, with
human feedback refining the visual style. This condensed edition has passed
template rendering and geometry smoke checks; a fresh-chat drawing trial of
this edition is still pending. These are practical trials, not a benchmark
or a guarantee across models and environments.

## Background and release status

[The short origin story](ORIGINS.md) explains the iterations behind the kit,
including what failed. The approach draws on C4 for software views, Moody's
Physics of Notations for visual meaning, and Swiss typography and composition.
The resulting house style is a practical application, not a certification or
endorsement by those sources.

Licence: part of The Boring Pond. The text is under CC BY-SA 4.0, the scripts
in `tools/` under the GNU AGPL, version 3 or later, and `TEMPLATE.dot` is
public domain (CC0). The diagrams you draw with it are yours.

Simple. Boring. Effective. <^==>
