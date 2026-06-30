"""One-off helper: writes a placeholder TechCorp logo (pure stdlib, no Pillow).

Run once with `python generate_logo.py`. Replace techcorp_logo.png with the
real brand asset whenever the team has one; app.py falls back to a CSS badge
if this file is missing.
"""
import struct
import zlib
from pathlib import Path

SIZE = 128
TOP = (34, 197, 94)     # #22c55e
BOTTOM = (21, 128, 61)  # #15803d


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def build_png(path: Path) -> None:
    rows = []
    for y in range(SIZE):
        t = y / (SIZE - 1)
        r = _lerp(*TOP[0:1], t) if False else _lerp(TOP[0], BOTTOM[0], t)
        g = _lerp(TOP[1], BOTTOM[1], t)
        b = _lerp(TOP[2], BOTTOM[2], t)
        row = bytearray([0])  # filter type 0
        for _x in range(SIZE):
            row += bytes([r, g, b, 255])
        rows.append(bytes(row))
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data))
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.write_bytes(png)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "techcorp_logo.png"
    build_png(out)
    print(f"wrote {out}")
