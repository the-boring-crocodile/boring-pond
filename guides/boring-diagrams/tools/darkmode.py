"""Write the dark-mode twin of a kit diagram.

    python3 darkmode.py light.svg dark.svg

GitHub picks a picture per reader theme with
<picture><source media="(prefers-color-scheme: dark)" srcset="x-dark.svg"><img src="x.svg"></picture>.

Every colour goes through one rule, the one Excalidraw (our canvas) uses for its
dark theme: CSS invert(93%) then hue-rotate(180deg), in sRGB. Lightness flips,
hue stays, so box kinds, line kinds and key colours keep their meaning and the
picture matches what the canvas shows in its dark theme. White becomes
#121212. No palette table to keep in step with the kit.

Text without a fill (Graphviz leaves titles black by default) gets the twin of
black. Named colours other than none/transparent are refused (exit 2): write
them as hex.
"""
import re
import sys

COLOUR = re.compile(r"#[0-9a-fA-F]{6}\b")
NAMED = re.compile(r'(?:fill|stroke|color)="(?!none"|transparent")([a-zA-Z]+)"')

# hue-rotate(180deg): the CSS Filter Effects matrix with cos = -1, sin = 0.
HUE_180 = ((-0.574, 1.430, 0.144),
           (0.426, 0.430, 0.144),
           (0.426, 1.430, -0.856))


def twin(hex_colour):
    """Dark twin of '#rrggbb': invert(0.93), then hue-rotate(180deg), clamped."""
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    inv = [0.93 - 0.86 * c for c in rgb]
    out = [min(1.0, max(0.0, sum(m * c for m, c in zip(row, inv)))) for row in HUE_180]
    return "#" + "".join(f"{round(c * 255):02x}" for c in out)


def darken(svg):
    """Return the dark twin; raise ValueError naming any named colour."""
    named = sorted(set(NAMED.findall(svg)))
    if named:
        raise ValueError("named colours (write them as hex): " + ", ".join(named))
    svg = COLOUR.sub(lambda m: twin(m.group(0)), svg)
    return re.sub(r"<text(?![^>]*\bfill=)", f'<text fill="{twin("#000000")}"', svg)


def main(argv):
    if len(argv) != 3:
        print("usage: python3 darkmode.py light.svg dark.svg", file=sys.stderr)
        return 2
    try:
        dark = darken(open(argv[1], encoding="utf-8").read())
    except ValueError as e:
        print(f"{argv[1]}: {e}", file=sys.stderr)
        return 2
    open(argv[2], "w", encoding="utf-8").write(dark)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
