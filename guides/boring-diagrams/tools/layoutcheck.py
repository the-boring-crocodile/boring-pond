#!/usr/bin/env python3
"""What a picture's geometry says, for someone who cannot look at it.

    dot -Tjson diagram.dot | python3 layoutcheck.py
    (or: python3 layoutcheck.py diagram.json)

Reports, from the laid-out graph (points, origin bottom left):
  - box sizes: which visible boxes differ from the most common size;
  - rows: boxes whose centres share a height, and near misses (off by < 6 pt);
  - edges through boxes: a visible edge passing over a box that is not its end;
  - edge crossings: pairs of visible edges that cross;
  - arrows as read: every visible edge as the picture states it, "A -> B"
    meaning the arrowhead sits at B (dir=back and dir=both resolved), to
    compare line by line with the relationships it should show;
  - overall size.
Exit status 1 if an edge runs through a box, else 0. Crossings are reported,
not failed: a fan-out between rows can need them (approved MCP example).
Approximate (polyline sampling of the drawn splines); it does not replace a
human look at the rendered picture.
"""
import json
import sys
from collections import Counter

data = json.load(open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin)
objs = data.get("objects", [])
nodes = {}
for o in objs:
    if "nodes" in o or "pos" not in o or o.get("style", "") == "invis" or o.get("shape") == "point":
        continue
    x, y = map(float, o["pos"].split(","))
    w, h = float(o["width"]) * 72, float(o["height"]) * 72
    nodes[o["_gvid"]] = {"name": o["name"], "x": x, "y": y, "w": w, "h": h, "shape": o.get("shape", "")}


def points(edge):
    pts = []
    for op in edge.get("_draw_", []):
        if op.get("op") in ("b", "B"):
            p = op["points"]
            for i in range(0, len(p) - 3, 3):
                (a, b, c, d) = p[i:i + 4]
                for k in range(21):
                    t = k / 20
                    u = 1 - t
                    pts.append((u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0],
                                u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1]))
    return pts


edges = []
for e in data.get("edges", []):
    if e.get("style", "") == "invis":
        continue
    pts = points(e)
    if pts:
        tail_name = nodes.get(e["tail"], {}).get("name", str(e["tail"]))
        head_name = nodes.get(e["head"], {}).get("name", str(e["head"]))
        direction = e.get("dir", "forward")
        reads = {"back": f"{head_name} -> {tail_name}", "both": f"{tail_name} <-> {head_name}",
                 "none": f"{tail_name} -- {head_name} (no arrowhead)"}.get(direction, f"{tail_name} -> {head_name}")
        edges.append({"tail": e["tail"], "head": e["head"], "pts": pts, "reads": reads,
                      "name": f'{nodes.get(e["tail"], {}).get("name", e["tail"])} -> '
                              f'{nodes.get(e["head"], {}).get("name", e["head"])}'})

boxes = {k: n for k, n in nodes.items() if n["shape"] not in ("plain", "plaintext", "none")}
sizes = Counter((round(n["w"]), round(n["h"])) for n in boxes.values())
if sizes:
    common = sizes.most_common(1)[0][0]
    odd = [f'{n["name"]} {round(n["w"])}x{round(n["h"])}' for n in boxes.values()
           if (round(n["w"]), round(n["h"])) != common]
    print(f"boxes: {len(boxes)}, most common size {common[0]}x{common[1]} pt;",
          "different:", ", ".join(odd) if odd else "none")

rows, near = {}, []
for n in boxes.values():
    rows.setdefault(round(n["y"]), []).append(n["name"])
keys = sorted(rows)
for a, b in zip(keys, keys[1:]):
    if 0 < b - a < 6:
        near.append(f"{rows[a]} vs {rows[b]} ({b - a} pt)")
print("rows (top first):", " | ".join(", ".join(rows[k]) for k in reversed(keys)))
print("near-miss rows:", "; ".join(near) if near else "none")
above = None
for k in reversed(keys):
    xs = sorted(n["x"] for n in boxes.values() if round(n["y"]) == k)
    middle = (xs[0] + xs[-1]) / 2
    note = ""
    if above is not None:
        off = round(middle - above)
        note = "; centred under the row above" if abs(off) < 2 else f"; {off:+} pt off the row above's middle"
    print(f"  row at {k} pt: centres x = {', '.join(str(round(x)) for x in xs)}{note}")
    above = middle

through = []
for e in edges:
    for k, n in boxes.items():
        if k in (e["tail"], e["head"]):
            continue
        x0, x1 = n["x"] - n["w"] / 2 + 2, n["x"] + n["w"] / 2 - 2
        y0, y1 = n["y"] - n["h"] / 2 + 2, n["y"] + n["h"] / 2 - 2
        if any(x0 < px < x1 and y0 < py < y1 for px, py in e["pts"]):
            through.append(f'{e["name"]} through {n["name"]}')
print("edges through boxes:", "; ".join(through) if through else "none")


def cross(p, q, r, s):
    def o(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    return o(p, q, r) * o(p, q, s) < 0 and o(r, s, p) * o(r, s, q) < 0


crossings = []
for i, a in enumerate(edges):
    for b in edges[i + 1:]:
        if {a["tail"], a["head"]} & {b["tail"], b["head"]}:
            continue
        sa, sb = list(zip(a["pts"], a["pts"][1:])), list(zip(b["pts"], b["pts"][1:]))
        if any(cross(p, q, r, s) for p, q in sa for r, s in sb):
            crossings.append(f'{a["name"]} x {b["name"]}')
print("edge crossings:", "; ".join(crossings) if crossings else "none")

print("arrows as read (arrowhead at the right-hand name):")
for e in sorted(edges, key=lambda e: e["reads"]):
    print("  " + e["reads"])

bb = [float(v) for v in data.get("bb", "0,0,0,0").split(",")]
print(f"picture: {round(bb[2] - bb[0])} x {round(bb[3] - bb[1])} pt")
sys.exit(1 if through else 0)
