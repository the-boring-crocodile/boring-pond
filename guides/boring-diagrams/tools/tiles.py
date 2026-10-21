#!/usr/bin/env python3
"""Cut a wide (or tall) PNG into near-square pieces for looking at it.

    python3 tiles.py picture.png            -> picture.tile1.png, picture.tile2.png, ...

Vision models read near-square images best; a 4:1 diagram shrunk into one
image loses its arrowheads and small text. Each piece overlaps its neighbour
by 10 % so nothing is cut in half unseen. Prints one line per piece.
"""
import math
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    source = Path(sys.argv[1])
    image = Image.open(source)
    width, height = image.size
    long_side, short_side = max(width, height), min(width, height)
    count = max(1, math.ceil(long_side / (short_side * 1.3)))
    step = long_side / count
    overlap = int(step * 0.1)
    for index in range(count):
        start = max(0, int(index * step) - overlap)
        end = min(long_side, int((index + 1) * step) + overlap)
        box = (start, 0, end, height) if width >= height else (0, start, width, end)
        piece = image.crop(box)
        if max(piece.size) > 2048:
            piece.thumbnail((2048, 2048))
        target = source.with_name(f"{source.stem}.tile{index + 1}.png")
        piece.save(target, optimize=True)
        print(f"{target} {piece.size[0]}x{piece.size[1]} from x/y {start}-{end}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
