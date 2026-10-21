#!/usr/bin/env python3
"""Draw one labelled boundary line across a lane diagram, between two steps.

A dynamic view drawn as lanes sometimes has a moment that matters more than
the others (a point of no return). Graphviz cannot draw a line across several
clusters, so this adds it to the rendered SVG: a dashed line across the full
width of the frames, halfway between the bottom of node A and the top of node
B, with its label at the right end above the line.

Usage: dot -Tsvg x.dot | python3 divider.py A B "Label text" [#colour] > x.svg
"""
import re
import sys

def box(svg, name):
    m = re.search(r'<title>' + re.escape(name) + r'</title>\s*<polygon[^>]*points="([^"]+)"', svg)
    if not m:
        sys.exit(f"divider.py: node {name!r} not found")
    ys = [float(p.split(",")[1]) for p in m.group(1).split()]
    return min(ys), max(ys)  # SVG y: min is the top

def frames(svg):
    xs = []
    for points in re.findall(r'class="cluster">.*?<polygon[^>]*points="([^"]+)"', svg, flags=re.S):
        xs += [float(p.split(",")[0]) for p in points.split()]
    return min(xs), max(xs)

def main():
    a, b, label = sys.argv[1:4]
    colour = sys.argv[4] if len(sys.argv) > 4 else "#9b784b"
    svg = sys.stdin.read()
    y = (box(svg, a)[1] + box(svg, b)[0]) / 2
    x0, x1 = frames(svg)
    mark = (f'<g class="divider"><line x1="{x0:.2f}" y1="{y:.2f}" x2="{x1:.2f}" y2="{y:.2f}" stroke="{colour}" '
            f'stroke-width="1.6" stroke-dasharray="6,4"/><text text-anchor="end" x="{x1 - 4:.2f}" y="{y - 5:.2f}" '
            f'font-family="Helvetica,sans-Serif" font-weight="bold" font-size="10.00" fill="{colour}">{label}</text></g>')
    end = svg.rindex("</g>\n</svg>")  # inside the graph group, so its transform applies
    sys.stdout.write(svg[:end] + mark + "\n" + svg[end:])

if __name__ == "__main__":
    main()
