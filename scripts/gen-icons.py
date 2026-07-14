#!/usr/bin/env python3
"""Generate Kitchen Planner PWA icons (180, 192, 512).

Draws a dark rounded square with a teal L-shaped floor plan and warm wood
counter accent. Uses Pillow when available; otherwise a pure-Python PNG writer.
"""

from __future__ import annotations

import os
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "icons"
SIZES = (180, 192, 512)

# Colors from task brief
BG = (0x1B, 0x20, 0x24, 0xFF)
ACCENT = (0x6A, 0xA6, 0xD9, 0xFF)
WOOD = (0xC6, 0x89, 0x3F, 0xFF)


def try_pillow() -> bool:
    try:
        from PIL import Image, ImageDraw  # type: ignore
    except ImportError:
        return False

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        _draw_icon(draw, size)
        path = OUT_DIR / f"icon-{size}.png"
        img.save(path, "PNG")
        print(f"wrote {path} (Pillow)")
    return True


def _draw_icon(draw, size: int) -> None:
    """Draw icon geometry using an ImageDraw-like interface (rectangle, rounded_rectangle)."""
    m = size / 512.0
    r = max(8, int(96 * m))
    # Background rounded square
    try:
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BG)
    except AttributeError:
        draw.rectangle([0, 0, size - 1, size - 1], fill=BG)

    # L-shaped floor plan (teal): outer L from top-left wall run + bottom run
    # Vertical arm
    x0, y0 = int(96 * m), int(96 * m)
    thick = max(12, int(72 * m))
    long_v = int(320 * m)
    long_h = int(300 * m)
    # Vertical segment of L
    draw.rectangle([x0, y0, x0 + thick, y0 + long_v], fill=ACCENT)
    # Horizontal segment of L
    draw.rectangle([x0, y0 + long_v - thick, x0 + long_h, y0 + long_v], fill=ACCENT)

    # Warm wood counter rectangle (island / counter block)
    cx0 = int(220 * m)
    cy0 = int(160 * m)
    cw = int(180 * m)
    ch = int(96 * m)
    draw.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=WOOD)


# --- Pure Python PNG (no deps) ---

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, rgba_pixels: list[tuple[int, int, int, int]]) -> None:
    """Write a valid RGBA PNG from a flat list of (r,g,b,a) length width*height."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter None
        row = y * width
        for x in range(width):
            raw.extend(rgba_pixels[row + x])
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", compressed) + _png_chunk(b"IEND", b"")
    path.write_bytes(png)


def fill_rect(pix: list, w: int, h: int, x0: int, y0: int, x1: int, y1: int, color: tuple) -> None:
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    for y in range(y0, y1):
        base = y * w
        for x in range(x0, x1):
            pix[base + x] = color


def rounded_bg(pix: list, size: int, radius: int, color: tuple) -> None:
    r2 = radius * radius
    for y in range(size):
        for x in range(size):
            # distance to nearest corner region
            cx = x if x < radius else (x if x >= size - radius else radius)
            cy = y if y < radius else (y if y >= size - radius else radius)
            # only check corners
            if x < radius and y < radius:
                dx, dy = radius - x, radius - y
                if dx * dx + dy * dy > r2:
                    continue
            elif x >= size - radius and y < radius:
                dx, dy = x - (size - 1 - radius), radius - y
                if dx * dx + dy * dy > r2:
                    continue
            elif x < radius and y >= size - radius:
                dx, dy = radius - x, y - (size - 1 - radius)
                if dx * dx + dy * dy > r2:
                    continue
            elif x >= size - radius and y >= size - radius:
                dx, dy = x - (size - 1 - radius), y - (size - 1 - radius)
                if dx * dx + dy * dy > r2:
                    continue
            pix[y * size + x] = color


def pure_python_icons() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        pix: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (size * size)
        m = size / 512.0
        r = max(8, int(96 * m))
        rounded_bg(pix, size, r, BG)

        x0, y0 = int(96 * m), int(96 * m)
        thick = max(12, int(72 * m))
        long_v = int(320 * m)
        long_h = int(300 * m)
        fill_rect(pix, size, size, x0, y0, x0 + thick, y0 + long_v, ACCENT)
        fill_rect(pix, size, size, x0, y0 + long_v - thick, x0 + long_h, y0 + long_v, ACCENT)

        cx0 = int(220 * m)
        cy0 = int(160 * m)
        cw = int(180 * m)
        ch = int(96 * m)
        fill_rect(pix, size, size, cx0, cy0, cx0 + cw, cy0 + ch, WOOD)

        path = OUT_DIR / f"icon-{size}.png"
        write_png(path, size, size, pix)
        print(f"wrote {path} (pure Python)")


def main() -> None:
    if try_pillow():
        return
    pure_python_icons()


if __name__ == "__main__":
    main()
