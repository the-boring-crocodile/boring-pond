#!/usr/bin/env python3
"""Put a small outline pictogram at the right of each box that asks for one.

A node with class="icon-NAME" in the DOT gets the pictogram NAME, centred in
the space its label leaves at the right of the box, drawn in the box's own
border colour. The text says what the box is; the pictogram only repeats it.

Usage: dot -Tsvg diagram.dot | python3 icons.py | python3 badges.py > diagram.svg
"""
import re
import sys

SIZE = 26.0    # pt, the pictogram's square
PAD = 14.0     # pt, from the box's right edge
STROKE = 1.5   # in the 24-unit drawing grid

# 24 x 24 outline drawings: lines only, no fills.
ICONS = {
    "person": "M12 3.5a4 4 0 1 1 0 8a4 4 0 1 1 0-8z M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7",
    "code": "M9 6.5 3.5 12 9 17.5 M15 6.5 20.5 12 15 17.5",
    "file": "M6 2.5h8.5l4 4v15H6z M14.5 2.5v4h4 M9 12h6 M9 15.5h6",
    "folder": "M2.5 6h7l2 2.5h10v11.5h-19z",
    "link": "M10.5 13.5l3-3 M8.5 11.5 6 14a3.2 3.2 0 0 0 4.5 4.5l2.5-2.5 M15.5 12.5 18 10a3.2 3.2 0 0 0-4.5-4.5L11 8",
    "running": "M12 2.5a9.5 9.5 0 1 1 0 19a9.5 9.5 0 1 1 0-19z M10 8l6 4-6 4z",
    "chat": "M3.5 4.5h17v11.5H10l-5 4v-4H3.5z M7.5 9h9 M7.5 12h6",
    "route": "M3.5 8h14 M14.5 5l3 3-3 3 M20.5 16h-14 M9.5 13l-3 3 3 3",
    "container": "M12 2.5l8.5 4.75v9.5L12 21.5l-8.5-4.75v-9.5z M3.5 7.25 12 12l8.5-4.75 M12 12v9.5",
    "agent": "M5.5 8.5h13v11h-13z M12 4.5v4 M9.5 13.5v1 M14.5 13.5v1 M9.5 17h5 M3 13v3 M21 13v3",
    "system": "M12 8.5a3.5 3.5 0 1 1 0 7a3.5 3.5 0 1 1 0-7z M12 2.5v3 M12 18.5v3 M2.5 12h3 M18.5 12h3 M5.3 5.3l2.1 2.1 M16.6 16.6l2.1 2.1 M5.3 18.7l2.1-2.1 M16.6 7.4l2.1-2.1",
}


def place(match):
    group = match.group(0)
    name = match.group(1)
    if name not in ICONS:
        raise SystemExit(f"icons.py: no pictogram called {name!r}")
    box = re.search(r'<polygon fill="[^"]*" stroke="(#[0-9a-f]{6})"[^>]* points="([^"]+)"', group)
    if not box:
        return group
    xs, ys = zip(*((float(x), float(y)) for x, y in (p.split(",") for p in box.group(2).split())))
    x = max(xs) - PAD - SIZE
    y = (min(ys) + max(ys)) / 2 - SIZE / 2
    icon = (f'<g transform="translate({x:.2f},{y:.2f}) scale({SIZE / 24:.4f})" fill="none" '
            f'stroke="{box.group(1)}" stroke-width="{STROKE}" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{ICONS[name]}"/></g>')
    return group[:-len("</g>")] + icon + "</g>"


svg = sys.stdin.read()
sys.stdout.write(re.sub(r'<g id="node\d+" class="node icon(?:-|&#45;)([a-z]+)">.*?</g>', place, svg, flags=re.S))
