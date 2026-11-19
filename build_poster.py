#!/usr/bin/env python3
"""Build entry.png v1 — 'Thursday 19 November 2026' front page.

Own design, own code, own flat drawings. Distinct from the 18 Nov v3:
a crimson masthead, a full-width dominant hero for the Trump-Xi-Putin
trilateral (first-ever three-way meeting of the three largest nuclear
powers), three illustrated sub-leads (GTA VI launch, Anthropic's Nasdaq
debut, the ICJ Rohingya verdict), nine illustrated cards, a UTC timeline
with verified times only, a dotted world map with 12 pins, a two-column
also-list at 15px, and an explicit DATE CHECK box naming the 17-18 Nov
stories that are NOT 19 Nov news. 40 stories: 4 leads + 9 cards +
27 also-list items (the market-close line is split into two entries,
Dow/S&P/Nasdaq and Nvidia/Bitcoin, both from the supplied figures;
Amazon's $7bn renewables pledge sits in the also-list only, labelled
reported, because its sourcing is weak). No outcome is asserted for
the trilateral or the ICJ verdict; the Anthropic first-trade price is
not asserted (first trade 14:30 UTC). The world outline is Natural
Earth 110m land data (public domain) in map_data.py. Drawn with
Pillow, no network.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont
from map_data import LAND_POLYS

W, H = 1024, 1024
BG = (252, 248, 240)
INK = (22, 22, 22)
CRIMSON = (158, 22, 32)
CRIMSON_D = (120, 14, 24)
NAVY = (22, 32, 63)
RED = (178, 34, 34)
BLUE = (30, 80, 140)
TEAL = (0, 120, 110)
PURPLE = (90, 60, 140)
ORANGE = (214, 110, 20)
GREEN = (34, 130, 70)
GOLD = (217, 164, 65)
GOLDD = (170, 120, 25)
SKY = (190, 215, 235)
SEA = (150, 190, 215)
SAND = (238, 222, 180)
LAND = (232, 214, 170)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, max_w, fill=INK, leading=None, max_lines=None,
         what="text"):
    lh = leading or int(font.size * 1.18)
    lines = wrap(d, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"OVERFLOW in {what}: {lines!r} "
                         f"({len(lines)} lines, max {max_lines})")
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def one_line(d, text, font, max_w, what="text"):
    orig = text
    while text and d.textlength(text, font=font) > max_w:
        text = text.rsplit(" ", 1)[0]
    if text != orig:
        raise ValueError(f"TRUNCATED in {what}: {orig!r} -> {text!r}")
    return text


def rtext(d, x_right, y, text, font, fill):
    d.text((x_right - d.textlength(text, font=font), y), text,
           font=font, fill=fill)


def kicker(d, x, y, num, text, color=RED, max_w=984):
    fb = f(SANS_B, 11)
    tw = d.textlength(text.upper(), font=fb)
    if tw > max_w - 16:
        raise ValueError(f"KICKER OVERFLOW: {text!r} ({tw:.0f}px > "
                         f"{max_w - 16:.0f}px)")
    d.ellipse([x, y + 1, x + 12, y + 13], fill=color)
    d.text((x + 4 if num < 10 else x + 1.5, y + 2), str(num),
           font=f(SANS_B, 8), fill=(255, 255, 255))
    d.text((x + 16, y + 1.5), text.upper(), font=fb, fill=color)
    return y + 14


def draw_map(d, x0, y0, w, h, pins, dots):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(205, 225, 240),
                outline=(150, 150, 140), width=1)

    def px(lon, lat):
        return (x0 + (lon + 180) / 360.0 * w,
                y0 + (83 - lat) / 139.0 * h)

    for poly in LAND_POLYS:
        d.polygon([px(lo, la) for lo, la in poly], fill=LAND,
                  outline=(180, 165, 135))
    for lo, la in dots:
        x, y = px(lo, la)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(70, 70, 70))
    for pin in pins:
        n, lo, la, col = pin[0], pin[1], pin[2], pin[3]
        tx, ty = px(lo, la)
        if len(pin) > 4:
            x, y = px(pin[4], pin[5])
            d.line([tx, ty, x, y], fill=(60, 60, 60), width=1)
        else:
            x, y = tx, ty
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col,
                  outline=(255, 255, 255), width=1)
        d.text((x - 3 if n < 10 else x - 5, y - 5), str(n),
               font=f(SANS_B, 8), fill=(255, 255, 255))


def flag(d, x, y, w, h, kind):
    d.rectangle([x, y, x + w, y + h], outline=(90, 90, 90), width=1)
    if kind == "cn":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        for sx, sy, r in [(7, 6, 3), (16, 3, 2), (19, 8, 2), (16, 14, 2),
                          (10, 15, 2)]:
            d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                      fill=(255, 222, 0))
    elif kind == "ru":
        d.rectangle([x, y, x + w, y + h // 3], fill=(255, 255, 255))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 60, 180))
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(220, 30, 30))
    elif kind == "us":
        for i in range(7):
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                        fill=RED if i % 2 == 0 else (255, 255, 255))
        d.rectangle([x, y, x + w * 0.42, y + h * 0.55], fill=BLUE)
        for sx in range(3):
            for sy in range(2):
                d.ellipse([x + 3 + sx * 6, y + 3 + sy * 6,
                           x + 5 + sx * 6, y + 5 + sy * 6],
                          fill=(255, 255, 255))
    elif kind == "ca":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.rectangle([x, y, x + w // 4, y + h], fill=(220, 30, 30))
        d.rectangle([x + 3 * w // 4, y, x + w, y + h], fill=(220, 30, 30))
        d.polygon([(x + w // 2, y + 3), (x + w // 2 - 3, y + 8),
                   (x + w // 2 - 6, y + 7), (x + w // 2 - 4, y + 11),
                   (x + w // 2 - 7, y + 13), (x + w // 2 - 3, y + 14),
                   (x + w // 2 - 2, y + h - 3), (x + w // 2 + 2, y + h - 3),
                   (x + w // 2 + 3, y + 14), (x + w // 2 + 7, y + 13),
                   (x + w // 2 + 4, y + 11), (x + w // 2 + 6, y + 7),
                   (x + w // 2 + 3, y + 8)], fill=(220, 30, 30))


# ---------------- hero + lead panels --------------------------------------
def panel_trilateral(d, x, y, w, h):
    """Hero: three flags over a summit table, dusk skyline behind."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 28, 52))
    # dusk sky: warm band
    d.rectangle([x, y, x + w, y + 26], fill=(214, 130, 60))
    d.rectangle([x, y + 26, x + w, y + 34], fill=(170, 90, 70))
    # skyline silhouettes
    for bx, bw, bh in [(10, 26, 22), (44, 18, 34), (70, 30, 26),
                       (108, 20, 40), (136, 26, 30), (170, 18, 36)]:
        d.rectangle([x + bx, y + 34 + 22 - bh + 12, x + bx + bw, y + 68],
                    fill=(48, 44, 70))
    for bx, bw, bh in [(w - 190, 26, 30), (w - 156, 18, 40),
                       (w - 130, 30, 26), (w - 92, 20, 36),
                       (w - 64, 26, 28), (w - 30, 18, 34)]:
        d.rectangle([x + bx, y + 34 + 22 - bh + 12, x + bx + bw, y + 68],
                    fill=(48, 44, 70))
    # summit table, centre
    d.rectangle([x + w // 2 - 190, y + 44, x + w // 2 + 190, y + 52],
                fill=(120, 85, 50))
    d.rectangle([x + w // 2 - 190, y + 52, x + w // 2 + 190, y + 68],
                fill=(90, 60, 35))
    # three flags on poles above the table
    fw, fh, gap = 64, 34, 26
    total = 3 * fw + 2 * gap
    sx = x + (w - total) // 2
    for i, (kind, name) in enumerate([("cn", "CHINA"), ("us", "USA"),
                                      ("ru", "RUSSIA")]):
        fx = sx + i * (fw + gap)
        d.line([fx + fw // 2, y + 6, fx + fw // 2, y + 12], fill=GOLD, width=2)
        flag(d, fx, y + 12, fw, fh, kind)
        d.text((fx + fw // 2 - len(name) * 2.8, y + 48), name,
               font=f(SANS_B, 9), fill=(255, 255, 255))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=CRIMSON)
    d.text((x + 10, y + h - 15), "SHENZHEN  •  APEC",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "FIRST-EVER TRILATERAL  •  TODAY",
          f(SANS_B, 10), (255, 255, 255))


def panel_gta(d, x, y, w, h):
    """GTA VI: dusk skyline, palm, neon title bar."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 20, 66))
    d.rectangle([x, y, x + w, y + 30], fill=(232, 120, 60))
    d.ellipse([x + w - 52, y + 6, x + w - 22, y + 36], fill=(255, 210, 120))
    for bx, bw, bh in [(8, 22, 26), (36, 16, 38), (58, 26, 30),
                       (92, 18, 42), (116, 24, 28), (148, 16, 36),
                       (170, 22, 26), (198, 16, 34), (220, 24, 28),
                       (250, 16, 38), (272, 22, 26), (300, 14, 32)]:
        d.rectangle([x + bx, y + 58 - bh, x + bx + bw, y + 58],
                    fill=(30, 12, 40))
    # palm, left
    d.line([x + 26, y + 58, x + 26, y + 34], fill=(20, 60, 30), width=3)
    for dx, dy in [(-12, -4), (12, -4), (-8, 2), (8, 2)]:
        d.line([x + 26, y + 34, x + 26 + dx, y + 34 + dy],
               fill=(30, 110, 50), width=3)
    d.text((x + 60, y + 8), "GTA VI", font=f(SERIF_B, 26),
           fill=(255, 255, 255))
    d.text((x + 176, y + 36), "OUT TODAY", font=f(SANS_B, 12), fill=GOLD)
    d.rectangle([x, y + h - 18, x + w, y + h], fill=INK)
    d.text((x + 10, y + h - 15), "LEONIDA  •  PS5 / XBOX",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "$79.99", f(SANS_B, 10),
          (255, 255, 255))


def panel_ant(d, x, y, w, h):
    """Anthropic IPO: big $83, rising chart, Nasdaq bell."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 40, 44))
    d.text((x + 10, y + 6), "$83", font=f(SERIF_B, 34),
           fill=(255, 255, 255))
    d.text((x + 92, y + 12), "A SHARE", font=f(SANS_B, 11), fill=GOLD)
    d.text((x + 92, y + 26), "ABOVE $70–78 RANGE", font=f(SANS_B, 9),
           fill=(255, 255, 255))
    # rising chart line
    pts = [(x + 180, y + 48), (x + 210, y + 42), (x + 240, y + 44),
           (x + 270, y + 30), (x + 300, y + 20)]
    d.line(pts, fill=(80, 220, 160), width=3)
    d.polygon([(x + 300, y + 20), (x + 292, y + 18), (x + 296, y + 28)],
              fill=(80, 220, 160))
    # bell, bottom left
    d.pieslice([x + 14, y + 44, x + 40, y + 68], 180, 360, fill=GOLD)
    d.rectangle([x + 10, y + 66, x + 44, y + 70], fill=GOLD)
    d.text((x + 52, y + 52), "ANT  •  NASDAQ", font=f(SANS_B, 10),
           fill=(255, 255, 255))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=INK)
    d.text((x + 10, y + h - 15), "BIGGEST IPO EVER  •  $81.3BN",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "FIRST TRADE 14:30 UTC",
          f(SANS_B, 10), (255, 255, 255))


def panel_icj(d, x, y, w, h):
    """ICJ: courthouse columns, scales of justice."""
    d.rectangle([x, y, x + w, y + h], fill=(235, 232, 222))
    d.rectangle([x + 10, y + 46, x + 96, y + 58], fill=(255, 255, 255),
                outline=(150, 150, 150))
    for cx in [16, 30, 44, 58, 72]:
        d.rectangle([x + cx, y + 50, x + cx + 6, y + 58], fill=(180, 180, 180))
    d.pieslice([x + 28, y + 26, x + 78, y + 52], 180, 360,
               fill=(255, 255, 255), outline=(150, 150, 150))
    # scales
    d.line([x + 200, y + 14, x + 200, y + 56], fill=INK, width=3)
    d.line([x + 168, y + 22, x + 232, y + 22], fill=INK, width=2)
    for sx in [x + 168, x + 232]:
        d.line([sx, y + 22, sx - 10, y + 40], fill=INK, width=1)
        d.line([sx, y + 22, sx + 10, y + 40], fill=INK, width=1)
        d.pieslice([sx - 11, y + 38, sx + 11, y + 50], 0, 180, fill=GOLD)
    d.text((x + 110, y + 6), "GAMBIA v. MYANMAR", font=f(SANS_B, 10),
           fill=INK)
    d.rectangle([x, y + h - 18, x + w, y + h], fill=NAVY)
    d.text((x + 10, y + h - 15), "THE HAGUE  •  VERDICT 09:00 UTC",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "ICJ", f(SANS_B, 10),
          (255, 255, 255))

# ---------------- card illustrations (190 x 42) ---------------------------
def scene(d, x, y, w, h, kind):
    if kind == "bridge":
        d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        d.rectangle([x, y + 30, x + w, y + h], fill=SEA)
        # bridge deck with a gap in the middle
        d.rectangle([x + 6, y + 22, x + 82, y + 28], fill=(90, 90, 100))
        d.rectangle([x + 108, y + 22, x + w - 6, y + 28], fill=(90, 90, 100))
        # arch spans
        d.arc([x + 10, y + 2, x + 78, y + 30], 180, 360, fill=(60, 60, 70),
              width=3)
        d.arc([x + 112, y + 2, x + 180, y + 30], 180, 360, fill=(60, 60, 70),
              width=3)
        # blast in the gap
        d.polygon([(x + 95, y + 2), (x + 100, y + 12), (x + 106, y + 4),
                   (x + 102, y + 14), (x + 110, y + 16), (x + 100, y + 20),
                   (x + 96, y + 26), (x + 92, y + 16), (x + 84, y + 14),
                   (x + 90, y + 10)], fill=(255, 140, 0))
        d.text((x + 118, y + 2), "3RD HIT", font=f(SANS_B, 10), fill=RED)
        d.text((x + 118, y + 14), "THIS WEEK", font=f(SANS_B, 9), fill=INK)
    elif kind == "missile":
        d.rectangle([x, y, x + w, y + h], fill=(20, 24, 44))
        for sx, sy, r in [(30, 6, 1), (90, 10, 1), (150, 5, 1), (60, 14, 1),
                          (120, 18, 1), (170, 12, 1)]:
            d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                      fill=(255, 255, 255))
        # missile arc + intercept burst
        d.arc([x + 20, y - 6, x + 150, y + 46], 200, 330, fill=(255, 180, 60),
              width=3)
        d.polygon([(x + 150, y + 8), (x + 158, y + 16), (x + 148, y + 20),
                   (x + 154, y + 26), (x + 144, y + 24), (x + 142, y + 14)],
                  fill=(255, 200, 40))
        d.text((x + 8, y + 26), "RIYADH", font=f(SANS_B, 10),
               fill=(255, 255, 255))
        d.text((x + 62, y + 26), "INTERCEPTED ~03:00 UTC",
               font=f(SANS_B, 9), fill=(255, 200, 40))
    elif kind == "protest":
        d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
        # crowd silhouettes
        for cx in [18, 38, 58, 78, 98, 118, 138, 158, 178]:
            d.ellipse([x + cx - 5, y + 18, x + cx + 5, y + 28], fill=INK)
            d.rectangle([x + cx - 7, y + 28, x + cx + 7, y + h],
                        fill=(60, 60, 70))
        # banner
        d.rectangle([x + 30, y + 2, x + 160, y + 14], fill=RED)
        d.text((x + 36, y + 4), "LOCKDOWN", font=f(SANS_B, 9),
               fill=(255, 255, 255))
        d.text((x + 104, y + 4), "DHAKA", font=f(SANS_B, 9), fill=GOLD)
    elif kind == "methane":
        d.rectangle([x, y, x + w, y + h], fill=(225, 240, 230))
        # pipeline with valve
        d.rectangle([x + 8, y + 18, x + w - 8, y + 26], fill=(120, 130, 140))
        d.ellipse([x + 88, y + 8, x + 104, y + 24], fill=RED)
        d.line([x + 96, y + 8, x + 96, y + 2], fill=RED, width=3)
        # flame
        d.polygon([(x + 150, y + 4), (x + 158, y + 16), (x + 146, y + 16)],
                  fill=(255, 140, 0))
        d.text((x + 8, y + 30), "DELAYED 2 YEARS", font=f(SANS_B, 10),
               fill=GREEN)
        d.text((x + 118, y + 30), "02:57 UTC", font=f(SANS_B, 9), fill=INK)
    elif kind == "spy":
        d.rectangle([x, y, x + w, y + h], fill=(235, 235, 245))
        # laptop with chip
        d.rectangle([x + 10, y + 10, x + 90, y + 34], fill=(40, 40, 50))
        d.rectangle([x + 6, y + 34, x + 94, y + 38], fill=(120, 120, 130))
        d.rectangle([x + 36, y + 16, x + 64, y + 28], fill=(60, 160, 120))
        d.text((x + 40, y + 19), "CHIP", font=f(SANS_B, 8),
               fill=(255, 255, 255))
        # magnifier
        d.ellipse([x + 118, y + 2, x + 158, y + 30], outline=RED, width=3)
        d.line([x + 152, y + 26, x + 172, y + 36], fill=RED, width=3)
        d.text((x + 128, y + 9), "?", font=f(SANS_B, 14), fill=RED)
        d.text((x + 104, y + 32), "PALANTIR", font=f(SANS_B, 8), fill=INK)
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        d.rectangle([x, y + 28, x + w, y + h], fill=SEA)
        # cargo ship
        d.polygon([(x + 20, y + 28), (x + 150, y + 28), (x + 138, y + 40),
                   (x + 32, y + 40)], fill=(120, 40, 40))
        for cx in [34, 58, 82, 106]:
            d.rectangle([x + cx, y + 16, x + cx + 20, y + 28], fill=BLUE)
        d.line([x + 140, y + 28, x + 140, y + 10], fill=(60, 60, 60), width=2)
        d.rectangle([x + 140, y + 10, x + 162, y + 18], fill=(255, 255, 255),
                    outline=(90, 90, 90))
        d.text((x + 143, y + 11), "PA", font=f(SANS_B, 7), fill=INK)
        d.text((x + 8, y + 2), "DETAINED", font=f(SANS_B, 10), fill=RED)
        d.text((x + 76, y + 2), "PANAMA-FLAGGED", font=f(SANS_B, 9),
               fill=INK)
    elif kind == "bank":
        d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
        # bank building
        d.rectangle([x + 12, y + 22, x + 70, y + 38], fill=(255, 255, 255),
                    outline=(150, 150, 150))
        for cx in [18, 30, 42, 54]:
            d.rectangle([x + cx, y + 26, x + cx + 5, y + 38],
                        fill=(180, 180, 180))
        d.polygon([(x + 12, y + 22), (x + 41, y + 8), (x + 70, y + 22)],
                  fill=(255, 255, 255), outline=(150, 150, 150))
        # rising arrow
        d.line([(x + 92, y + 34), (x + 120, y + 22), (x + 148, y + 12)],
               fill=GREEN, width=3)
        d.polygon([(x + 148, y + 12), (x + 138, y + 10), (x + 144, y + 20)],
                  fill=GREEN)
        d.text((x + 152, y + 4), "+25bp", font=f(SANS_B, 12), fill=GREEN)
        d.text((x + 92, y + 30), "RATE HIKE", font=f(SANS_B, 9), fill=INK)
    elif kind == "handshake":
        d.rectangle([x, y, x + w, y + h], fill=(235, 240, 250))
        flag(d, x + 12, y + 6, 44, 24, "ca")
        d.text((x + 12, y + 32), "CANADA", font=f(SANS_B, 8), fill=INK)
        flag(d, x + 134, y + 6, 44, 24, "cn")
        d.text((x + 134, y + 32), "CHINA", font=f(SANS_B, 8), fill=INK)
        # clasped hands, centre
        d.ellipse([x + 78, y + 10, x + 112, y + 30], fill=(240, 200, 160),
                  outline=(120, 80, 50))
        d.line([x + 78, y + 20, x + 112, y + 20], fill=(120, 80, 50), width=2)
        d.text((x + 66, y + 32), "RESET", font=f(SANS_B, 9), fill=BLUE)
    elif kind == "fossil":
        d.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
        # rock strata with a gap (the missing billion years)
        for i, col in enumerate([(200, 170, 130), (180, 150, 110),
                                 (160, 130, 95)]):
            d.rectangle([x + 8, y + 6 + i * 9, x + 120, y + 14 + i * 9],
                        fill=col)
        d.rectangle([x + 120, y + 6, x + 128, y + 33], fill=(255, 255, 255))
        d.text((x + 132, y + 6), "1bn YEARS", font=f(SANS_B, 10), fill=RED)
        d.text((x + 132, y + 20), "MISSING", font=f(SANS_B, 10), fill=INK)
        d.text((x + 8, y + 34), "NATURE STUDY", font=f(SANS_B, 8), fill=INK)
    else:
        raise ValueError(f"unknown scene kind {kind!r}")


# ---------------- content -------------------------------------------------
REGIONS = [
    ("Asia", 9, PURPLE), ("N. America", 13, RED), ("Europe", 5, BLUE),
    ("Middle East", 8, ORANGE), ("Africa", 2, GREEN), ("Oceania", 2, TEAL),
    ("Global", 1, GOLDD),
]

LEADS = [
    ("N. AMERICA • GTA VI — REUTERS", RED, panel_gta,
     "GTA VI launches today",
     "PS5 and Xbox Series X|S; $79.99–$99.99, up to 212 GB; "
     "7.71m digital pre-orders."),
    ("N. AMERICA • ANTHROPIC IPO — REUTERS", RED, panel_ant,
     "Anthropic debuts on Nasdaq as ANT",
     "Priced at $83 — above the $70–78 range; 980m shares, $81.3bn; "
     "biggest IPO ever. First trade 14:30 UTC."),
    ("EUROPE • ICJ VERDICT — ICJ", BLUE, panel_icj,
     "ICJ to rule on Rohingya genocide case",
     "Gambia v. Myanmar; verdict due 09:00 UTC in The Hague; "
     "700,000+ displaced."),
]

# (num, kicker, colour, scene, headline, deck)
CARDS = [
    (5, "EUROPE • BRIDGE — REUTERS", BLUE, "bridge",
     "Crimean Bridge hit a third time this week",
     "Overnight attack; traffic suspended"),
    (6, "M. EAST • RIYADH — REUTERS", ORANGE, "missile",
     "Houthi missile at Riyadh intercepted",
     "Saudi defences hold at ~03:00 UTC"),
    (7, "ASIA • DHAKA — REUTERS", PURPLE, "protest",
     "Bangladesh lockdown turns violent",
     "Lockdown verified; toll unconfirmed"),
    (8, "EU • METHANE — REUTERS", BLUE, "methane",
     "EU delays methane rules two years",
     "Deal agreed 02:57 UTC today"),
    (9, "EUROPE • SPYING — BBC", BLUE, "spy",
     "Russian held for spying on Palantir",
     "Arrest reported by the BBC"),
    (10, "N. AMERICA • PANAMA — AP", RED, "ship",
     "US panel: punish China over ship seizures",
     "Panama-flagged ships detained"),
    (11, "ASIA • JAKARTA — REUTERS", PURPLE, "bank",
     "Bank Indonesia hikes rates 25bp",
     "Quarter-point rise announced today"),
    (12, "CANADA–CHINA — REUTERS", RED, "handshake",
     "Canada–China reset under Carney",
     "PM Carney moves to mend ties"),
    (13, "GLOBAL • NATURE — NATURE", GOLDD, "fossil",
     "Nature: Earth's 'missing billion years'",
     "Study explains the lost eon"),
]

# (num, region colour, text) — every line verified to fit one 15px line
ALSO = [
    (14, PURPLE, "India–Japan hold 2+2 dialogue"),
    (15, BLUE, "France minister hits out at Mélenchon"),
    (16, ORANGE, "Saudi: danger passed in south"),
    (17, GREEN, "Libya seizes cocaine and pills"),
    (18, RED, "Bukele acts on Haiti gang leader"),
    (19, RED, "Microsoft in AI talks with ByteDance"),
    (20, RED, "US senators warn of AI cyber threat"),
    (21, RED, "Trump on Fox on ex-Nvidia chief Huang"),
    (22, RED, "Liu Yunping elected caucus chair"),
    (23, PURPLE, "Taiwan amends Anti-Infiltration Act"),
    (24, BLUE, "McDonald's sex-abuse probe (BBC)"),
    (25, RED, "Oil: WTI −3.2% to $83.26"),
    (26, RED, "Markets (18 Nov close): Dow −561"),
    (27, RED, "Nvidia −2.9%; Bitcoin $63,454"),
    (28, ORANGE, "FIFA U17 World Cup: matchday 1"),
    (29, TEAL, "Cricket: India v NZ, 1st Test"),
    (30, TEAL, "Oceania bowls: Auckland 19–22 Nov"),
    (31, ORANGE, "UAE economy forecast +7.3% (IMF)"),
    (32, ORANGE, "Sharjah hotels recover after oil spill"),
    (33, RED, "World Para Surfing in Palm Desert"),
    (34, PURPLE, "APEC leaders pose in Shenzhen"),
    (35, ORANGE, "US–Iran: strikes of 17–18 Nov (context)"),
    (36, ORANGE, "CENTCOM chief meets IDF, Mossad"),
    (37, PURPLE, "Pakistan v Sri Lanka, 2nd Test"),
    (38, GREEN, "SA v Bangladesh, 1st Test day 5"),
    (39, ORANGE, "Yemen–Saudi war: truce broke 2022"),
    (40, PURPLE, "Amazon $7bn India renewables (reported)"),
]

PINS = [
    (1, 114.1, 22.5, PURPLE),            # Shenzhen
    (2, -80.2, 25.8, RED),               # Leonida / Florida
    (3, -74.0, 40.7, RED, -64, 46),      # New York, offset up-left
    (4, 4.3, 52.1, BLUE, 14, 58),        # The Hague, offset up-right
    (5, 36.5, 45.3, BLUE),               # Crimean Bridge
    (6, 46.7, 24.7, ORANGE),             # Riyadh
    (7, 90.4, 23.8, PURPLE),             # Dhaka
    (8, 4.4, 50.8, BLUE, -8, 57),        # Brussels, offset up-left
    (9, -79.5, 9.0, RED),                # Panama
    (10, 106.8, -6.2, PURPLE),           # Jakarta
    (11, -75.7, 45.4, RED),              # Ottawa
    (12, -0.1, 51.5, GOLDD, -14, 46),    # London (Nature), offset down-left
]

TIMELINE = ("UTC  18 NOV 23:36 3RD BRIDGE ATTACK  •  "
            "01:05 BRIDGE (BBC)  •  01:46 TRUMP–XI  •  "
            "02:57 EU METHANE DELAY  •  ~03:00 HOUTHI MISSILE DOWN  •  "
            "09:00 ICJ VERDICT  •  TRILATERAL  •  "
            "14:30 ANT FIRST TRADE")

DATE_CHECK = (
    "DATE CHECK — Not 19 November, so not on this page: Kerch Bridge "
    "collapse (16–17 Nov; only the 3rd attack is 19 Nov), Nvidia "
    "results (17 Nov), Fed minutes, Jeffries 251–11 vote, Pew report, "
    "Van Gogh $190.4m sale, Voyager 1 crossing (18 Nov; NASA confirms "
    "19 Nov), EU €45bn loan, COP31 draft, Cyclone Akvan, Amnesty El Obeid, "
    "Knesset vote, Mongolia president (18 Nov), Gaza op beyond the Yellow "
    "Line (from 18 Nov).")


def build(out="entry.png"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    mx = 20

    # ---- crimson masthead with calendar block ----
    d.rectangle([0, 0, W, 94], fill=CRIMSON)
    d.text((mx, 8), "THE WORLD TODAY  •  ONE DAY, IN ONE PICTURE",
           font=f(SANS_B, 13), fill=GOLD)
    d.text((mx, 26), "Thursday 19 November 2026",
           font=f(SERIF_B, 44), fill=(255, 255, 255))
    d.text((mx, 76), "40 STORIES  •  7 REGIONS  •  ONE PAGE",
           font=f(SANS_B, 12), fill=(255, 255, 255))
    cx0, cy0, cw, chh = 884, 8, 120, 78
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + chh], fill=(255, 255, 255))
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + 20], fill=CRIMSON_D)
    d.text((cx0 + 44, cy0 + 3), "NOV", font=f(SANS_B, 13),
           fill=(255, 255, 255))
    d.text((cx0 + 38, cy0 + 22), "19", font=f(SERIF_B, 32), fill=CRIMSON)
    d.text((cx0 + 24, cy0 + 58), "THU 2026", font=f(SANS_B, 12), fill=RED)

    # ---- region bar + legend (exact-fill segments) ----
    total = sum(c for _, c, _ in REGIONS)
    assert total == 40, f"region counts sum to {total}, not 40"
    bar_y, bar_h = 98, 14
    cum = 0
    for name, count, col in REGIONS:
        x0 = mx + 984 * cum // 40
        cum += count
        x1 = mx + 984 * cum // 40
        d.rectangle([x0, bar_y, x1, bar_y + bar_h], fill=col)
        d.text((x0 + (x1 - x0) // 2 - 3, bar_y + 1), str(count),
               font=f(SANS_B, 10), fill=(255, 255, 255))
    lx = mx
    ly = 114
    for i, (name, count, col) in enumerate(REGIONS):
        d.rectangle([lx, ly + 2, lx + 10, ly + 12], fill=col)
        lab = f"{name} {count}"
        d.text((lx + 13, ly), lab, font=f(SANS_B, 10), fill=INK)
        lx += 13 + d.textlength(lab, font=f(SANS_B, 10)) + 16

    # ---- day in numbers strip ----
    d.rectangle([0, 132, W, 150], fill=INK)
    nums = ("$81.3BN IPO  •  $83/SHARE  •  980M SHARES  •  212 GB GTA VI  •  "
            "7.71M PRE-ORDERS  •  227M BRIDGE SECTION DOWN  •  DOW −561  •  "
            "WTI $83.26  •  1,550 WARHEAD CAP")
    nums = one_line(d, nums, f(SANS_B, 12), W - 2 * mx, "numbers strip")
    d.text((mx, 136), nums, font=f(SANS_B, 12), fill=(255, 255, 255))

    # ---- hero: trilateral, full width ----
    panel_trilateral(d, mx, 156, 984, 76)
    kicker(d, mx, 236, 1, "ASIA • TRILATERAL — REUTERS • AP", PURPLE)
    d.text((mx, 250), "Trump, Xi and Putin meet in Shenzhen",
           font=f(SERIF_B, 20), fill=INK)
    deck = ("First-ever three-way meeting of the three largest nuclear "
            "powers; New START expired in February, its 1,550-warhead cap "
            "gone — outcome pending.")
    deck = one_line(d, deck, f(SERIF, 11), 984, "hero deck")
    d.text((mx, 274), deck, font=f(SERIF, 11), fill=INK)
    d.line([mx, 296, W - mx, 296], fill=INK, width=2)

    # ---- three sub-leads ----
    pw, ph, pg = 322, 72, 8
    for i, (kick, col, panel, head, deck) in enumerate(LEADS):
        x = mx + i * (pw + pg)
        panel(d, x, 306, pw, ph)
        kicker(d, x, 382, i + 2, kick, col)
        para(d, x, 396, head, f(SERIF_B, 17), pw, max_lines=2,
             leading=19, what=f"lead {i + 2} headline")
        para(d, x, 434, deck, f(SERIF, 11), pw, max_lines=2, leading=12.5,
             what=f"lead {i + 2} deck")
    d.line([mx, 460, W - mx, 460], fill=INK, width=2)

    # ---- nine cards: row of five, row of four (centred) ----
    cw, chh = 190, 42
    for idx, (num, kick, col, kind, head, deck) in enumerate(CARDS):
        if idx < 5:
            x = mx + idx * (cw + 8)
            y = 466
        else:
            x = mx + 100 + (idx - 5) * (cw + 8)
            y = 576
        scene(d, x, y, cw, chh, kind)
        kicker(d, x, y + 46, num, kick, col, max_w=cw)
        para(d, x, y + 64, head, f(SERIF_B, 13), cw, max_lines=2,
             leading=15, what=f"card {num} headline")
        deck = one_line(d, deck, f(SERIF, 10), cw, f"card {num} deck")
        d.text((x, y + 96), deck, font=f(SERIF, 10), fill=INK)

    # ---- UTC timeline (single navy band, label inside) ----
    d.rectangle([mx, 686, W - mx, 704], fill=NAVY)
    line = one_line(d, TIMELINE, f(SANS, 9), 984 - 16, "timeline")
    tx = mx + (984 - d.textlength(line, font=f(SANS, 9))) // 2
    d.text((tx, 691), line, font=f(SANS, 9), fill=(255, 255, 255))

    # ---- map + also list ----
    d.line([mx, 712, W - mx, 712], fill=INK, width=2)
    d.text((mx, 716), "WHERE IT HAPPENED", font=f(SANS_B, 12), fill=RED)
    d.text((mx + 360, 716), "ALSO ON THURSDAY 19 NOVEMBER",
           font=f(SANS_B, 12), fill=RED)
    y0 = 734
    draw_map(d, mx, y0, 330, 120, PINS, [])
    d.text((mx, 858), "Pins: stories 1–12",
           font=f(SANS, 10), fill=(90, 90, 90))
    lx = mx + 360
    colw = 310
    for i, (n, col, item) in enumerate(ALSO):
        c, row = divmod(i, 14)
        x = lx + c * (colw + 14)
        yy = y0 + row * 16
        d.ellipse([x, yy + 4, x + 7, yy + 11], fill=col)
        d.ellipse([x + 10, yy + 1, x + 23, yy + 14], fill=PURPLE)
        d.text((x + 12 if n < 10 else x + 10.5, yy + 2.5), str(n),
               font=f(SANS_B, 8), fill=(255, 255, 255))
        item = one_line(d, item, f(SERIF, 15), colw - 32,
                        f"also {n}")
        d.text((x + 28, yy), item, font=f(SERIF, 15), fill=INK)

    # ---- date check box + sources ----
    d.line([mx, 962, W - mx, 962], fill=INK, width=2)
    d.rectangle([mx, 968, W - mx, 1008], outline=RED, width=2,
                fill=(255, 250, 245))
    d.text((mx + 8, 972), "DATE CHECK", font=f(SANS_B, 11), fill=RED)
    para(d, mx + 8, 984, DATE_CHECK, f(SANS, 10), W - 2 * mx - 8,
         max_lines=2, leading=12, what="date check")
    d.text((mx, 1012),
           "Sources: Reuters, BBC, AP, ICJ, Nature, IMF — 19 November 2026. "
           "All drawings original.",
           font=f(SANS, 9), fill=(90, 90, 90))

    # ---- count verification ----
    n_total = 1 + len(LEADS) + len(CARDS) + len(ALSO)
    assert n_total == 40, f"total stories {n_total}, not 40"
    assert len(ALSO) == 27 and [n for n, _, _ in ALSO] == list(range(14, 41))
    assert len(PINS) == 12, f"{len(PINS)} pins, need 12"

    img.save(out, optimize=True)
    print(out, img.size, len(open(out, "rb").read()), "bytes")


if __name__ == "__main__":
    build(os.path.join(HERE, "entry.png"))
