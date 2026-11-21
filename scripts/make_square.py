"""Square 1080x1080 cover for the Anvarov Telegram channel.

Usage: python3 make_square.py cover.json out.png

cover.json:
{
  "tag": "Yangi model",            # rubric, short, Uzbek
  "title": "Gemini 4 hamma uchun ochildi",   # <= ~60 chars
  "accent": "#4C8DFF",
  "date": "21.11.2026",
  "scene": {"type": "chat", "app": "Gemini 4", "items": [...]}
}
Top: rubric pill + title. Bottom: mockup of the AI tool itself (make_scenes.py).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_scenes import font, wrap, render_scene  # noqa: E402

S = 1080


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def build(c, out):
    acc = hex2rgb(c.get("accent", "#7C5CFF"))
    img = Image.new("RGB", (S, S), (10, 11, 20))
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((620, -300, 1400, 420), fill=acc)
    g.ellipse((-380, 560, 420, 1360), fill=tuple(int(v * 0.6) for v in acc))
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    img = Image.blend(img, glow, 0.55).convert("RGBA")

    grid = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, S, 60):
        gd.line((x, 0, x, S), fill=(255, 255, 255, 9))
    for y in range(0, S, 60):
        gd.line((0, y, S, y), fill=(255, 255, 255, 9))
    img = Image.alpha_composite(img, grid)
    d = ImageDraw.Draw(img)
    pad = 70

    # rubric pill
    ft = font("semi", 26)
    tag = c.get("tag", "Yangilik").upper()
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle((pad, 64, pad + tw + 44, 114), radius=25, fill=acc + (255,))
    d.text((pad + 22, 73), tag, font=ft, fill=(255, 255, 255, 255))
    if c.get("date"):
        fdt = font("med", 24)
        dw = d.textlength(c["date"], font=fdt)
        d.text((S - pad - dw, 76), c["date"], font=fdt, fill=(175, 180, 200, 255))

    # title (max 3 lines)
    for size in (68, 62, 56, 50, 46):
        fb = font("bold", size)
        lines = wrap(d, c["title"], fb, S - 2 * pad)
        if len(lines) <= 3:
            break
    lines = lines[:3]
    y = 146
    for ln in lines:
        d.text((pad, y), ln, font=fb, fill=(255, 255, 255, 255))
        y += int(size * 1.16)

    # mockup window
    top = max(y + 34, 380)
    bottom = S - 96
    ww, wh = S - 2 * pad, bottom - top
    win = render_scene(c.get("scene", {}), ww, wh, acc)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((pad + 10, top + 24, pad + ww + 10, bottom + 24), radius=30,
                                             fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    img = Image.alpha_composite(img, shadow)
    img.alpha_composite(win, (pad, top))

    # footer
    d = ImageDraw.Draw(img)
    ff = font("bold", 28)
    d.ellipse((pad, S - 62, pad + 20, S - 42), fill=acc + (255,))
    d.text((pad + 32, S - 69), "ANVAROV", font=ff, fill=(255, 255, 255, 255))
    fm = font("med", 24)
    lab = "Sun'iy intellekt yangiliklari · @anvarov_si"
    d.text((S - pad - d.textlength(lab, font=fm), S - 66), lab, font=fm, fill=(170, 175, 195, 255))
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    print("ok", build(data, sys.argv[2]))
