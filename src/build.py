#!/usr/bin/env python3
"""Build public/ from src/data.json + src/template.html.

- Inlines data.json into index.html (the page renders only from it).
- Writes manifest.webmanifest, sw.js (versioned by content hash) and app icons.
Run: python3 src/build.py
"""
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PUB = ROOT / "public"
NAVY = (11, 27, 58)
ACCENT = "#0b1b3a"


def png(path, size, pad=0.0):
    """Navy square with a white tennis-ball outline (ring plus two seams)."""
    s = size
    c = s / 2
    r = s * (0.30 - pad)
    w = s * 0.034
    seam_r = r * 1.05
    off = r * 1.62
    rows = []
    for y in range(s):
        row = bytearray([0])
        for x in range(s):
            cov = 0.0
            for sy in (0.25, 0.75):
                for sx in (0.25, 0.75):
                    px, py = x + sx - c, y + sy - c
                    d = math.hypot(px, py)
                    hit = abs(d - r) < w / 2
                    if not hit and d < r:
                        for ox in (-off, off):
                            if abs(math.hypot(px - ox, py) - seam_r) < w / 2:
                                hit = True
                    cov += 0.25 if hit else 0
            col = [round(NAVY[i] + (255 - NAVY[i]) * cov) for i in range(3)]
            row += bytes(col)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", s, s, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)


def main():
    data = json.loads((SRC / "data.json").read_text())
    # Every referenced image must exist locally (no hotlinks).
    imgs = sorted({x["img"] for k in ("ph", "jp") for x in data[k] if x.get("img")})
    missing = [i for i in imgs if not (PUB / "img" / i).exists()]
    if missing:
        raise SystemExit(f"missing images: {missing}")

    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (SRC / "template.html").read_text().replace("__DATA__", blob)
    (PUB / "index.html").write_text(html)

    icons = PUB / "icons"
    icons.mkdir(exist_ok=True)
    for name, size in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)):
        if not (icons / name).exists():
            png(icons / name, size)

    manifest = {
        "name": "Tennis Trip",
        "short_name": "Tennis Trip",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#e9eef6",
        "theme_color": ACCENT,
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (PUB / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2))

    shell = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png",
             "icons/apple-touch-icon.png"] + [f"img/{i}" for i in imgs]
    h = hashlib.sha1(html.encode())
    for i in imgs:
        h.update((PUB / "img" / i).read_bytes())
    version = h.hexdigest()[:10]
    sw = (SRC / "sw.template.js").read_text()
    sw = sw.replace("__VERSION__", version).replace("__SHELL__", json.dumps(shell))
    (PUB / "sw.js").write_text(sw)
    print(f"built: {len(data['ph'])} ph, {len(data['jp'])} jp, {len(data['plan'])} plan, {len(imgs)} images, sw {version}")


if __name__ == "__main__":
    main()
