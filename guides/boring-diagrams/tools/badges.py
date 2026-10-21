#!/usr/bin/env python3
"""Put each edge's number on its arrow, in a small circle at the midpoint.

Graphviz places edge labels wherever there is room, so their sides and
distances vary. This moves every edge label of a rendered SVG onto the
middle of its (straight) edge instead: one rule for all. When an arrow
crosses a frame (cluster) line near its middle, the badge slides along the
arrow to the nearest point clear of every frame line, so it never sits on one.

Usage: dot -Tsvg diagram.dot | python3 badges.py > diagram.svg
"""
import re
import sys

R = 7.5  # badge radius, pt
CLEAR = R + 4  # minimum distance from a badge centre to a frame line, pt
FRAMES = []  # (x0, x1, y0, y1) of every cluster rectangle, filled in main


def frames(svg):
    found = []
    for points in re.findall(r'class="cluster">.*?<polygon[^>]*points="([^"]+)"', svg, flags=re.S):
        xy = [tuple(map(float, p.split(","))) for p in points.split()]
        xs, ys = [x for x, _ in xy], [y for _, y in xy]
        found.append((min(xs), max(xs), min(ys), max(ys)))
    return found


def clear(x, y):
    for x0, x1, y0, y1 in FRAMES:
        if x0 - CLEAR < x < x1 + CLEAR and (abs(y - y0) < CLEAR or abs(y - y1) < CLEAR):
            return False
        if y0 - CLEAR < y < y1 + CLEAR and (abs(x - x0) < CLEAR or abs(x - x1) < CLEAR):
            return False
    return True


def place(x0, y0, x1, y1):
    """The middle of the line, or the nearest point along it clear of frame lines."""
    for step in range(0, 46):
        for t in ((0.5 + step / 100, 0.5 - step / 100) if step else (0.5,)):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if clear(x, y):
                return x, y
    return (x0 + x1) / 2, (y0 + y1) / 2

def badge(m):
    g = m.group(0)
    path = re.search(r'<path[^>]* stroke="(#[0-9a-f]{6})"[^>]* d="M([-\d.]+),([-\d.]+)[^"]*?([-\d.]+),([-\d.]+)"', g)
    tip = re.search(r'<polygon[^>]* points="[^"]*?([-\d.]+),([-\d.]+) [-\d.]+,[-\d.]+ [-\d.]+,[-\d.]+"', g)
    text = re.search(r'<text [^>]*fill="(#[0-9a-f]{6})"[^>]*>([^<]*)</text>', g)
    if not (path and text):
        return g
    color = path.group(1)
    x0, y0 = float(path.group(2)), float(path.group(3))
    x1, y1 = float(path.group(4)), float(path.group(5))
    if tip:  # the arrowhead tip is the real end of the line
        x1, y1 = float(tip.group(1)), float(tip.group(2))
    cx, cy = place(x0, y0, x1, y1)
    label = text.group(2).replace("&#160;", "").strip()
    b = (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R}" fill="#ffffff" stroke="{color}" stroke-width="1.2"/>'
         f'<text text-anchor="middle" x="{cx:.2f}" y="{cy + 3.6:.2f}" font-family="Helvetica,sans-Serif" '
         f'font-weight="bold" font-size="10.00" fill="{text.group(1)}">{label}</text>')
    return g.replace(text.group(0), b)

svg = sys.stdin.read()
FRAMES.extend(frames(svg))
sys.stdout.write(re.sub(r'<g id="edge\d+" class="edge">.*?</g>', badge, svg, flags=re.S))
