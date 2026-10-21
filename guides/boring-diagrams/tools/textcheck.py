"""Does any edge pass through any text? Samples each edge's bezier, tests text boxes (approximate)."""
import re, sys
import xml.etree.ElementTree as ET
NS = "{http://www.w3.org/2000/svg}"
root = ET.parse(sys.argv[1]).getroot()
texts, edges = [], []
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))
for g in root.iter(NS + "g"):
    paths = [p for p in g.findall(NS + "path") if p.get("fill") == "none"]
    is_edge = any(p.tag == NS + "polygon" for p in g) and paths and len(g.findall(NS + "path")) == 1
    if is_edge:
        nums = [float(n) for n in re.findall(r"-?[\d.]+", paths[0].get("d"))]
        pts = list(zip(nums[0::2], nums[1::2]))
        own = {t.text for t in g.findall(NS + "text")}
        samples = []
        for i in range(0, len(pts) - 3, 3):
            samples += [bez(*pts[i:i + 4], k / 20) for k in range(21)]
        edges.append((samples[3:-3], own))  # not the end points on the nodes' borders
for t in root.iter(NS + "text"):
    if not (t.text or "").strip():
        continue
    x, y, size = float(t.get("x")), float(t.get("y")), float(t.get("font-size", "10"))
    w = len(t.text) * size * 0.55
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[t.get("text-anchor", "start")]
    texts.append((x0, y - size * 0.85, x0 + w, y + size * 0.2, t.text.strip()))
hits = []
for samples, own in edges:
    for (x0, y0, x1, y1, label) in texts:
        if label in {o.strip() for o in own if o}:
            continue
        if any(x0 <= px <= x1 and y0 <= py <= y1 for px, py in samples):
            hits.append(label)
print("edges", len(edges), "texts", len(texts), "edges through text:", sorted(set(hits)) or "none")
sys.exit(1 if hits else 0)
