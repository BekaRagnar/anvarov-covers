"""UI mockup scenes for Anvarov covers (no logos, no faces).

render_scene(spec, w, h, accent) -> RGBA image of an app window mockup.

spec = {"type": "chat|code|settings|image|voice|stats", "app": "Window title",
        "items": [...]}  (see README.md for the item format of every type)
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/opentype/inter/"
F = {
    "bold": FD + "InterDisplay-Bold.otf",
    "semi": FD + "Inter-SemiBold.otf",
    "med": FD + "InterDisplay-Medium.otf",
    "reg": FD + "Inter-Regular.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}


def font(kind, size):
    try:
        return ImageFont.truetype(F[kind], size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in str(text).split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


BG = (22, 24, 36)
PANEL = (30, 33, 48)
LINE = (52, 56, 78)
TXT = (232, 234, 245)
MUTED = (150, 156, 180)


def window(w, h, title, accent):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=BG + (255,), outline=LINE + (255,), width=2)
    d.rounded_rectangle((0, 0, w - 1, 64), radius=26, fill=PANEL + (255,))
    d.rectangle((0, 40, w - 1, 64), fill=PANEL + (255,))
    d.line((0, 64, w, 64), fill=LINE + (255,), width=2)
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse((24 + i * 30, 23, 42 + i * 30, 41), fill=c + (255,))
    ft = font("semi", 24)
    tw = d.textlength(title, font=ft)
    d.text(((w - tw) / 2, 18), title, font=ft, fill=TXT + (255,))
    return img, d


def scene_chat(d, w, h, items, acc, t=1.0):
    n = len(items)
    shown = t * n
    vis = []
    for i, it in enumerate(items):
        if shown <= i:
            break
        frac = min(1.0, shown - i)
        txt = it.get("text", "")
        if it.get("role", "ai") != "user" and frac < 1:
            txt = txt[:max(1, int(len(txt) * frac))]
        vis.append(dict(it, text=txt))
    items = vis
    y, pad = 92, 30
    fb = font("reg", 25)
    # sidebar
    d.rectangle((0, 65, 170, h - 2), fill=(26, 28, 42, 255))
    d.rounded_rectangle((18, 86, 152, 124), radius=12, fill=acc + (255,))
    d.text((34, 93), "+ Yangi chat", font=font("semi", 19), fill=(255, 255, 255, 255))
    for i in range(5):
        d.rounded_rectangle((18, 146 + i * 46, 152 - (i % 3) * 18, 166 + i * 46), radius=8, fill=LINE + (255,))
    x0, x1 = 170 + pad, w - pad
    maxw = (x1 - x0) * 0.78
    for it in items:
        role = it.get("role", "ai")
        lines = wrap(d, it.get("text", ""), fb, maxw - 40)[:5]
        bh = 24 + 34 * len(lines)
        bw = min(maxw, max(d.textlength(l, font=fb) for l in lines) + 44) if lines else 120
        if y + bh > h - 110:
            break
        if role == "user":
            bx = x1 - bw
            d.rounded_rectangle((bx, y, x1, y + bh), radius=20, fill=mix(BG, acc, 0.55) + (255,))
        else:
            d.ellipse((x0, y + 4, x0 + 34, y + 38), fill=acc + (255,))
            d.text((x0 + 10, y + 7), "✦", font=font("mono", 22), fill=(255, 255, 255, 255))
            bx = x0 + 48
            d.rounded_rectangle((bx, y, bx + bw, y + bh), radius=20, fill=PANEL + (255,))
        ty = y + 12
        for l in lines:
            d.text((bx + 22, ty), l, font=fb, fill=TXT + (255,))
            ty += 34
        y += bh + 20
    # input bar
    d.rounded_rectangle((x0, h - 88, x1, h - 28), radius=30, fill=PANEL + (255,), outline=LINE + (255,), width=2)
    d.text((x0 + 26, h - 72), "Xabar yozing...", font=font("reg", 23), fill=MUTED + (255,))
    d.ellipse((x1 - 54, h - 80, x1 - 10, h - 36), fill=acc + (255,))
    d.text((x1 - 41, h - 76), "↑", font=font("bold", 28), fill=(255, 255, 255, 255))


def scene_code(d, w, h, items, acc, t=1.0):
    total = sum(len(str(l)) + 1 for l in items[:12])
    budget = int(total * min(1.0, t * 1.15))
    typed = []
    for l in items[:12]:
        l = str(l)
        if budget <= 0:
            break
        typed.append(l[:budget])
        budget -= len(l) + 1
    items = typed
    fm = font("mono", 24)
    d.rectangle((0, 65, 64, h - 2), fill=(26, 28, 42, 255))
    kw = ("def", "return", "import", "from", "const", "async", "await", "function", "class", "if", "for", "in")
    y = 90
    split = int(w * 0.64)
    for n, line in enumerate(items[:12], 1):
        if y > h - 50:
            break
        d.text((18, y), f"{n:>2}", font=fm, fill=(90, 96, 124, 255))
        x = 84
        for tok in str(line).replace("\t", "    ").split(" "):
            col = TXT
            if tok.strip("():,") in kw:
                col = mix(acc, (255, 255, 255), 0.25)
            elif tok.startswith(("#", "//")):
                col = (110, 118, 150)
            elif tok.startswith(("'", '"')):
                col = (152, 222, 140)
            seg = tok + " "
            if x + d.textlength(seg, font=fm) > split - 16:
                break
            d.text((x, y), seg, font=fm, fill=col + (255,))
            x += d.textlength(seg, font=fm)
        y += 38
    # AI side panel
    d.rectangle((split, 65, w - 2, h - 2), fill=PANEL + (255,))
    d.line((split, 65, split, h), fill=LINE + (255,), width=2)
    d.text((split + 22, 86), "✦", font=font("mono", 22), fill=acc + (255,))
    d.text((split + 50, 86), "AI yordamchi", font=font("semi", 22), fill=acc + (255,))
    fs = font("reg", 21)
    yy = 128
    for l in wrap(d, "Kodni tahlil qildim va taklif tayyor:", fs, w - split - 44):
        d.text((split + 22, yy), l, font=fs, fill=TXT + (255,))
        yy += 30
    for i in range(4):
        d.rounded_rectangle((split + 22, yy + 14 + i * 34, w - 30 - (i % 2) * 60, yy + 30 + i * 34), radius=6,
                            fill=LINE + (255,))
    bx = split + 22
    d.rounded_rectangle((bx, h - 74, bx + 150, h - 28), radius=14, fill=acc + (255,))
    d.text((bx + 26, h - 66), "Qabul", font=font("semi", 22), fill=(255, 255, 255, 255))


def scene_settings(d, w, h, items, acc, t=1.0):
    k = len(items[:6])
    vis = []
    for i, it in enumerate(items[:6]):
        if t * (k + 1) < i + 0.3:
            break
        it = dict(it)
        local = t * (k + 1) - i
        v = it.get("value", True)
        if isinstance(v, bool) and local < 1:
            it["value"] = not v
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            it["value"] = float(v) * min(1.0, local)
        vis.append(it)
    items = vis
    pad, y = 40, 92
    fl, fv = font("semi", 26), font("reg", 22)
    for it in items[:6]:
        if y > h - 80:
            break
        label, val = it.get("label", ""), it.get("value", True)
        d.rounded_rectangle((pad, y, w - pad, y + 72), radius=18, fill=PANEL + (255,))
        d.text((pad + 24, y + 12), label, font=fl, fill=TXT + (255,))
        if it.get("hint"):
            d.text((pad + 24, y + 44), it["hint"], font=font("reg", 18), fill=MUTED + (255,))
        rx = w - pad - 24
        if isinstance(val, bool):
            on = val
            d.rounded_rectangle((rx - 76, y + 20, rx, y + 52), radius=16, fill=(acc if on else LINE) + (255,))
            cx = rx - 18 if on else rx - 58
            d.ellipse((cx - 13, y + 23, cx + 13, y + 49), fill=(255, 255, 255, 255))
        elif isinstance(val, (int, float)):
            sx0, sx1 = rx - 260, rx
            d.rounded_rectangle((sx0, y + 32, sx1, y + 40), radius=4, fill=LINE + (255,))
            px = sx0 + (sx1 - sx0) * max(0, min(1, float(val)))
            d.rounded_rectangle((sx0, y + 32, px, y + 40), radius=4, fill=acc + (255,))
            d.ellipse((px - 13, y + 23, px + 13, y + 49), fill=(255, 255, 255, 255))
        else:
            s = str(val)
            tw = d.textlength(s, font=fv)
            d.rounded_rectangle((rx - tw - 36, y + 16, rx, y + 56), radius=12, fill=mix(BG, acc, 0.35) + (255,))
            d.text((rx - tw - 18, y + 24), s, font=fv, fill=TXT + (255,))
        y += 86


def scene_image(d, w, h, items, acc, img, t=1.0):
    pad = 30
    d.rounded_rectangle((pad, 84, w - pad, 140), radius=28, fill=PANEL + (255,), outline=LINE + (255,), width=2)
    prompt = items[0] if items else "Prompt..."
    prompt = prompt[:max(1, int(len(prompt) * min(1.0, t * 2.5)))]
    fp = font("reg", 22)
    pl = wrap(d, prompt, fp, w - 2 * pad - 200)
    d.text((pad + 24, 99), (pl[0] if pl else "") + ("…" if len(pl) > 1 else ""), font=fp, fill=TXT + (255,))
    d.rounded_rectangle((w - pad - 150, 92, w - pad - 10, 132), radius=20, fill=acc + (255,))
    d.text((w - pad - 128, 99), "Yaratish", font=font("semi", 21), fill=(255, 255, 255, 255))
    gy0, gy1 = 160, h - 24
    cols = 4 if w > 800 else 2
    gap = 16
    tw = (w - 2 * pad - gap * (cols - 1)) / cols
    th = gy1 - gy0
    palettes = [((255, 140, 80), (120, 60, 200)), ((60, 200, 220), (30, 60, 160)),
                ((250, 210, 90), (220, 80, 120)), ((120, 230, 150), (40, 100, 140))]
    reveal = max(0.0, (t - 0.35) / 0.65) * cols
    for i in range(cols):
        if reveal <= i:
            x0 = int(pad + i * (tw + gap))
            d.rounded_rectangle((x0, gy0, x0 + tw, gy1), radius=18, fill=PANEL + (255,), outline=LINE + (255,), width=2)
            continue
        x0 = int(pad + i * (tw + gap))
        tile = Image.new("RGB", (int(tw), int(th)))
        td = ImageDraw.Draw(tile)
        a, b = palettes[i % 4]
        for yy in range(int(th)):
            td.line((0, yy, tw, yy), fill=mix(a, b, yy / th))
        # abstract shapes: sun + hills
        td.ellipse((tw * 0.25, th * 0.18, tw * 0.75, th * 0.18 + tw * 0.5), fill=mix(a, (255, 255, 255), 0.5))
        td.polygon([(0, th), (0, th * 0.7), (tw * 0.4, th * 0.55), (tw, th * 0.75), (tw, th)], fill=mix(b, (0, 0, 0), 0.45))
        tile = tile.filter(ImageFilter.GaussianBlur(2))
        mask = Image.new("L", tile.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, tile.size[0] - 1, tile.size[1] - 1), radius=18, fill=255)
        img.paste(tile, (x0, gy0), mask)
        if len(items) > i + 1:
            lab = str(items[i + 1])
            fl = font("semi", 18)
            lw = d.textlength(lab, font=fl)
            d.rounded_rectangle((x0 + 10, gy1 - 44, x0 + 30 + lw, gy1 - 12), radius=12, fill=(0, 0, 0, 150))
            d.text((x0 + 20, gy1 - 40), lab, font=fl, fill=(255, 255, 255, 255))


def scene_voice(d, w, h, items, acc, t=1.0):
    cx, cy = w // 2, 200
    for r, a in ((110, 40), (82, 80), (56, 255)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=acc + (a,))
    d.rounded_rectangle((cx - 14, cy - 30, cx + 14, cy + 14), radius=14, fill=(255, 255, 255, 255))
    d.arc((cx - 26, cy - 14, cx + 26, cy + 30), 0, 180, fill=(255, 255, 255, 255), width=4)
    bars = 46
    for i in range(bars):
        x = 50 + i * (w - 100) / bars
        ph = t * 2 * math.pi * 3
        amp = 10 + 46 * abs(math.sin(i * 0.55 + ph) * math.cos(i * 0.17 - ph * 0.5))
        d.rounded_rectangle((x, 360 - amp, x + 8, 360 + amp), radius=4, fill=mix(acc, (255, 255, 255), 0.3) + (255,))
    fy = 440
    fs = font("reg", 24)
    items = [x for j, x in enumerate(items[:3]) if t >= 0.3 + j * 0.25 or t >= 1.0]
    for it in items:
        for l in wrap(d, it, fs, w - 120)[:2]:
            if fy > h - 40:
                break
            d.text((60, fy), l, font=fs, fill=TXT + (255,))
            fy += 34
        fy += 10


def scene_stats(d, w, h, items, acc, t=1.0):
    e = 1 - (1 - min(1.0, t)) ** 3
    pad, y = 44, 96
    vals = [float(it.get("value", 0)) for it in items[:5]] or [1]
    mx = max(vals) or 1
    fl, fv = font("semi", 24), font("bold", 26)
    bar_h = min(56, (h - 140) / max(1, len(vals)) - 26)
    for i, it in enumerate(items[:5]):
        lab = str(it.get("label", ""))
        v = float(it.get("value", 0))
        hl = it.get("highlight", i == 0)
        d.text((pad, y), lab, font=fl, fill=TXT + (255,))
        y += 34
        x1 = pad + (w - 2 * pad - 110) * v / mx * e
        d.rounded_rectangle((pad, y, w - pad - 110, y + bar_h), radius=12, fill=PANEL + (255,))
        d.rounded_rectangle((pad, y, max(pad + 24, x1), y + bar_h), radius=12,
                            fill=(acc if hl else (88, 94, 124)) + (255,))
        s = it.get("text", f"{v:g}") if e > 0.97 else f"{v * e:.1f}"
        d.text((w - pad - 96, y + bar_h / 2 - 16), s, font=fv, fill=TXT + (255,))
        y += bar_h + 22


def render_scene(spec, w, h, accent, t=1.0):
    kind, prog = spec.get("type", "chat"), t
    img, d = window(w, h, spec.get("app", "AI"), accent)
    items = spec.get("items", [])
    if kind == "code":
        scene_code(d, w, h, items, accent, prog)
    elif kind == "settings":
        scene_settings(d, w, h, items, accent, prog)
    elif kind == "image":
        scene_image(d, w, h, items, accent, img, prog)
    elif kind == "voice":
        scene_voice(d, w, h, items, accent, prog)
    elif kind == "stats":
        scene_stats(d, w, h, items, accent, prog)
    else:
        scene_chat(d, w, h, items, accent, prog)
    return img
