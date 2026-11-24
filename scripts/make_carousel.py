"""Carousel (Telegram album) for the Anvarov channel: cover + up to 9 slides, 1080x1080 each.

Usage: python3 make_carousel.py carousel.json out_dir
carousel.json = cover.json fields (tag, title, accent, date, scene) plus
  "slides": [{"title": "1-qadam: ...", "text": "short paragraph",
              "bullets": ["...", "..."], "prompt": "optional ready prompt"}]
Writes out_dir/01.png (cover, same as make_square) and 02.png ... per slide.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_scenes import font, wrap  # noqa: E402
from make_square import build as build_cover, hex2rgb  # noqa: E402

S = 1080


def background(acc):
    img = Image.new("RGB", (S, S), (10, 11, 20))
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((700, -360, 1460, 300), fill=acc)
    g.ellipse((-420, 760, 300, 1420), fill=tuple(int(v * 0.5) for v in acc))
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    img = Image.blend(img, glow, 0.45).convert("RGBA")
    grid = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, S, 60):
        gd.line((x, 0, x, S), fill=(255, 255, 255, 8))
    for y in range(0, S, 60):
        gd.line((0, y, S, y), fill=(255, 255, 255, 8))
    return Image.alpha_composite(img, grid)


def clean(t):
    """Drop emoji and other glyphs the slide fonts cannot draw."""
    return "".join(ch for ch in str(t) if ord(ch) < 0x2190 or 0x2190 <= ord(ch) <= 0x21FF or 0x2014 == ord(ch)).strip()


def slide(c, sl, idx, total, out):
    acc = hex2rgb(c.get("accent", "#A855F7"))
    img = background(acc)
    # big faded step number, bottom right
    num = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    nd = ImageDraw.Draw(num)
    fbig = font("bold", 380)
    label = f"{idx:02d}"
    nd.text((S - 60 - nd.textlength(label, font=fbig), S - 470), label, font=fbig, fill=acc + (38,))
    img = Image.alpha_composite(img, num)
    d = ImageDraw.Draw(img)
    sl = {k: ([clean(x) for x in v] if isinstance(v, list) else clean(v)) for k, v in sl.items()}
    pad = 70
    ft = font("semi", 24)
    tag = f"{c.get('tag', 'Qo`llanma').upper()}  ·  {idx}/{total}"
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle((pad, 64, pad + tw + 40, 110), radius=23, fill=acc + (255,))
    d.text((pad + 20, 72), tag, font=ft, fill=(255, 255, 255, 255))

    y = 150
    for size in (58, 52, 46, 42):
        fb = font("bold", size)
        lines = wrap(d, sl.get("title", ""), fb, S - 2 * pad)
        if len(lines) <= 3:
            break
    for ln in lines[:3]:
        d.text((pad, y), ln, font=fb, fill=(255, 255, 255, 255))
        y += int(size * 1.15)
    y += 24
    d.rounded_rectangle((pad, y, pad + 90, y + 6), radius=3, fill=acc + (255,))
    y += 36

    fbody = font("reg", 36)
    limit = S - 130
    if sl.get("text"):
        for ln in wrap(d, sl["text"], fbody, S - 2 * pad):
            if y > limit - 50:
                break
            d.text((pad, y), ln, font=fbody, fill=(220, 224, 238, 255))
            y += 50
        y += 18
    for b in sl.get("bullets", [])[:6]:
        blines = wrap(d, b, fbody, S - 2 * pad - 44)[:3]
        if y + 50 * len(blines) > limit:
            break
        d.ellipse((pad + 4, y + 17, pad + 20, y + 33), fill=acc + (255,))
        for ln in blines:
            d.text((pad + 44, y), ln, font=fbody, fill=(232, 234, 245, 255))
            y += 50
        y += 12
    if sl.get("prompt"):
        fm = font("mono", 27)
        plines = wrap(d, sl["prompt"], fm, S - 2 * pad - 60)
        y += 10
        max_lines = max(1, int((limit - y - 74) // 38))
        plines = plines[:max_lines]
        box_h = 74 + 38 * len(plines)
        d.rounded_rectangle((pad, y, S - pad, y + box_h), radius=22, fill=(26, 28, 42, 245),
                            outline=(60, 64, 90, 255), width=2)
        d.text((pad + 30, y + 20), "PROMPT", font=font("semi", 22), fill=acc + (255,))
        py = y + 58
        for ln in plines:
            d.text((pad + 30, py), ln, font=fm, fill=(210, 230, 210, 255))
            py += 38

    ff = font("bold", 28)
    d.ellipse((pad, S - 62, pad + 20, S - 42), fill=acc + (255,))
    d.text((pad + 32, S - 69), "ANVAROV", font=ff, fill=(255, 255, 255, 255))
    fm2 = font("med", 24)
    lab = "@anvarov_si" + ("  ·  davomi →" if idx < total else "")
    d.text((S - pad - d.textlength(lab, font=fm2), S - 66), lab, font=fm2, fill=(170, 175, 195, 255))
    img.convert("RGB").save(out, "PNG", optimize=True)


def build(c, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    slides = c.get("slides", [])[:9]
    total = len(slides) + 1
    files = [build_cover(c, os.path.join(out_dir, "01.png"))]
    for i, sl in enumerate(slides, start=2):
        p = os.path.join(out_dir, f"{i:02d}.png")
        slide(c, sl, i, total, p)
        files.append(p)
    return files


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    for f in build(data, sys.argv[2]):
        print("ok", f)
