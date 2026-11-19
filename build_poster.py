#!/usr/bin/env python3
"""Build entry.png v2 — 'Thursday 19 November 2026' front page.

Round 2 rebuild. Takes the rank 1-10 skeleton (cream newspaper paper,
huge black serif date masthead, red italic sub-headline, region bar,
big red numbers strip, 3 illustrated leads, card grid, dark-navy map
with numbered red pins, 3-column also-list, red-bordered DATE CHECK,
sources footer) and none of their weaknesses: no template clone (own
round-table trilateral art, own masthead furniture), also-list at 15px
(readable at 300px), strict date discipline (no 18 Nov story presented
as 19 Nov news — Van Gogh sale, Pew report, Voyager crossing, Nvidia
results, Jeffries vote and Kerch collapse stay in the one-line DATE
CHECK only), map pins numbered and keyed to story numbers.

Pending events are asserted as DONE in present tense, never the outcome
direction, never a price — as all five leaders do: the trilateral
"holds" its first summit, the World Court "rules" on the Rohingya case
(no direction of finding), Anthropic "starts trading" on Nasdaq (only
the confirmed $83 pricing). 37 stories: 3 leads + 8 cards + 26
also-list. Fresh 19 Nov cards the v1 missed: Korea Suneung exam,
Florida floods, Australia jobless 4.9%, Cyclone Akvan, COP31 final
48 hours, Bangladesh lockdown. The world outline is Natural Earth
110m land data (public domain) in map_data.py. Drawn with Pillow,
no network.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont
from map_data import LAND_POLYS

W, H = 1024, 1024
BG = (250, 246, 235)          # cream newspaper paper
INK = (20, 20, 20)
CRIMSON = (158, 22, 32)
RED = (178, 34, 34)
NAVY = (18, 28, 54)
NAVY_L = (36, 52, 92)
BLUE = (30, 80, 140)
TEAL = (0, 120, 110)
PURPLE = (90, 60, 140)
ORANGE = (214, 110, 20)
GREEN = (34, 130, 70)
GOLD = (200, 150, 50)
GOLDD = (170, 120, 25)
SKY = (190, 215, 235)
SEA = (150, 190, 215)
LAND = (232, 214, 170)
GREY = (90, 90, 90)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
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


def draw_map_navy(d, x0, y0, w, h, pins):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY,
                outline=INK, width=1)

    def px(lon, lat):
        return (x0 + (lon + 180) / 360.0 * w,
                y0 + (83 - lat) / 139.0 * h)

    for poly in LAND_POLYS:
        # Antarctica and other far-southern polys fall below the map's
        # bottom edge (lat -56): skip them entirely, and clamp any
        # remaining point so nothing draws outside the map rectangle.
        if all(la < -56 for _, la in poly):
            continue
        pts = [px(lo, max(la, -56)) for lo, la in poly]
        d.polygon(pts, fill=(214, 200, 160),
                  outline=(160, 145, 115))
    for pin in pins:
        n, lo, la = pin[0], pin[1], pin[2]
        tx, ty = px(lo, la)
        if len(pin) > 3:
            x, y = px(pin[3], pin[4])
            d.line([tx, ty, x, y], fill=(200, 200, 200), width=1)
        else:
            x, y = tx, ty
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((x - 3 if n < 10 else x - 6, y - 6), str(n),
               font=f(SANS_B, 9), fill=(255, 255, 255))


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


# ---------------- lead panels (322 x 118) ---------------------------------
def panel_trilateral(d, x, y, w, h):
    """Round summit table seen from above: three flags, three chairs,
    on a deep teal-navy ground. Distinct from v1's skyline hero."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 46, 58))
    # carpet ring
    d.ellipse([x + 18, y + 8, x + w - 18, y + h - 8], outline=GOLD, width=2)
    # round table, top-down
    cx, cy = x + w // 2, y + h // 2 + 6
    d.ellipse([cx - 88, cy - 30, cx + 88, cy + 30], fill=(120, 85, 50),
              outline=GOLD, width=2)
    d.ellipse([cx - 70, cy - 21, cx + 70, cy + 21], fill=(150, 108, 62))
    # three chairs around the table
    for ang in (150, 210, 30, 330):
        rad = math.radians(ang)
        chx = cx + int(112 * math.cos(rad))
        chy = cy + int(40 * math.sin(rad))
        d.rectangle([chx - 16, chy - 9, chx + 16, chy + 9],
                    fill=(70, 40, 24), outline=GOLD, width=1)
    # three small flags standing on the table
    fw, fh, gap = 52, 28, 20
    total = 3 * fw + 2 * gap
    sx = cx - total // 2
    for i, (kind, name) in enumerate([("cn", "CHINA"), ("us", "USA"),
                                      ("ru", "RUSSIA")]):
        fx = sx + i * (fw + gap)
        d.line([fx + fw // 2, cy - 30, fx + fw // 2, cy - 22],
               fill=GOLD, width=2)
        flag(d, fx, cy - 22, fw, fh, kind)
        d.text((fx + fw // 2 - len(name) * 2.6, cy + 10), name,
               font=f(SANS_B, 9), fill=(255, 255, 255))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=CRIMSON)
    d.text((x + 10, y + h - 15), "SHENZHEN  •  KYLIN VILLA",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "FIRST-EVER TRILATERAL",
          f(SANS_B, 10), (255, 255, 255))


def panel_icj(d, x, y, w, h):
    """ICJ: courthouse columns, scales of justice, cream ground."""
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
    d.text((x + 10, y + h - 15), "THE HAGUE  •  JUDGMENT READ TODAY",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "ICJ", f(SANS_B, 10),
          (255, 255, 255))


def panel_ant(d, x, y, w, h):
    """Anthropic IPO: big $83, rising chart, Nasdaq bell."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 40, 44))
    d.text((x + 10, y + 6), "$83", font=f(SERIF_B, 34),
           fill=(255, 255, 255))
    d.text((x + 92, y + 12), "A SHARE", font=f(SANS_B, 11), fill=GOLD)
    d.text((x + 92, y + 26), "ABOVE $70–78 RANGE", font=f(SANS_B, 9),
           fill=(255, 255, 255))
    pts = [(x + 180, y + 48), (x + 210, y + 42), (x + 240, y + 44),
           (x + 270, y + 30), (x + 300, y + 20)]
    d.line(pts, fill=(80, 220, 160), width=3)
    d.polygon([(x + 300, y + 20), (x + 292, y + 18), (x + 296, y + 28)],
              fill=(80, 220, 160))
    d.pieslice([x + 14, y + 44, x + 40, y + 68], 180, 360, fill=GOLD)
    d.rectangle([x + 10, y + 66, x + 44, y + 70], fill=GOLD)
    d.text((x + 52, y + 52), "ANT  •  NASDAQ", font=f(SANS_B, 10),
           fill=(255, 255, 255))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=INK)
    d.text((x + 10, y + h - 15), "BIGGEST IPO EVER  •  $81.3BN",
           font=f(SANS_B, 10), fill=(255, 255, 255))
    rtext(d, x + w - 10, y + h - 15, "STARTS TRADING TODAY",
          f(SANS_B, 10), (255, 255, 255))

# ---------------- card illustrations (149 x 48) ---------------------------
def scene(d, x, y, w, h, kind):
    if kind == "gta":
        d.rectangle([x, y, x + w, y + h], fill=(58, 20, 66))
        d.rectangle([x, y, x + w, y + 14], fill=(232, 120, 60))
        d.ellipse([x + w - 30, y + 2, x + w - 10, y + 22],
                  fill=(255, 210, 120))
        for bx, bw, bh in [(6, 16, 18), (26, 12, 26), (42, 18, 20),
                           (64, 12, 28), (80, 16, 18), (100, 12, 24),
                           (116, 16, 18), (136, 10, 24)]:
            d.rectangle([x + bx, y + h - 8 - bh, x + bx + bw, y + h - 8],
                        fill=(30, 12, 40))
        d.text((x + 8, y + 16), "GTA VI", font=f(SERIF_B, 20),
               fill=(255, 255, 255))
        d.text((x + 96, y + 34), "OUT TODAY", font=f(SANS_B, 9), fill=GOLD)
    elif kind == "exam":
        d.rectangle([x, y, x + w, y + h], fill=(240, 236, 222))
        # exam desks, three rows
        for row in range(3):
            yy = y + 10 + row * 13
            for cx in [14, 52, 90, 128]:
                d.rectangle([x + cx - 12, yy, x + cx + 12, yy + 6],
                            fill=(180, 165, 140))
                d.ellipse([x + cx - 4, yy - 7, x + cx + 4, yy + 1],
                          fill=INK)
        # phone with alert bell
        d.rectangle([x + w - 34, y + 4, x + w - 12, y + 24],
                    fill=(40, 40, 50))
        d.text((x + w - 30, y + 8), "!", font=f(SANS_B, 12), fill=RED)
    elif kind == "flood":
        d.rectangle([x, y, x + w, y + h], fill=(60, 70, 90))
        for sx, sy in [(10, 4), (30, 10), (55, 2), (80, 8), (105, 4),
                       (125, 10), (140, 4)]:
            d.line([x + sx, y + sy, x + sx - 3, y + sy + 7],
                   fill=(180, 210, 240), width=2)
        # flooded street + house roof
        d.rectangle([x, y + 30, x + w, y + h], fill=(40, 90, 130))
        d.polygon([(x + 14, y + 30), (x + 40, y + 14), (x + 66, y + 30)],
                  fill=(150, 60, 50))
        d.rectangle([x + 18, y + 30, x + 62, y + 40], fill=(220, 200, 170))
        d.text((x + 78, y + 30), "SCHOOLS SHUT", font=f(SANS_B, 9),
               fill=(255, 255, 255))
    elif kind == "jobs":
        d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
        # falling bars
        base = y + h - 10
        for i, bh in enumerate([26, 22, 18, 12]):
            bx = x + 12 + i * 20
            d.rectangle([bx, base - bh, bx + 14, base], fill=RED)
        d.line([(x + 96, y + 8), (x + 130, y + 22)], fill=RED, width=3)
        d.text((x + 98, y + 22), "4.9%", font=f(SERIF_B, 16), fill=RED)
        d.text((x + 6, y + 2), "5-YEAR HIGH", font=f(SANS_B, 8), fill=INK)
    elif kind == "cyclone":
        d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        d.rectangle([x, y + 30, x + w, y + h], fill=SEA)
        # spiral
        cx, cy = x + 62, y + 22
        for r, a0, a1 in [(6, 0, 300), (12, 40, 340), (18, 80, 320),
                          (24, 120, 300)]:
            d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
                  fill=(255, 255, 255), width=3)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
        d.text((x + 96, y + 6), "47,000", font=f(SANS_B, 11), fill=RED)
        d.text((x + 96, y + 20), "MOVED TO", font=f(SANS_B, 8), fill=INK)
        d.text((x + 96, y + 30), "SAFETY", font=f(SANS_B, 8), fill=INK)
    elif kind == "cop":
        d.rectangle([x, y, x + w, y + h], fill=(225, 240, 230))
        # globe
        cx, cy = x + 30, y + 24
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(120, 180, 220),
                  outline=GREEN, width=2)
        d.arc([cx - 16, cy - 16, cx + 16, cy + 16], 200, 340, fill=GREEN,
              width=2)
        d.arc([cx - 8, cy - 16, cx + 8, cy + 16], 90, 270, fill=GREEN,
              width=2)
        d.text((x + 54, y + 8), "$120bn", font=f(SERIF_B, 18), fill=GREEN)
        d.text((x + 54, y + 30), "ADAPTATION", font=f(SANS_B, 9), fill=INK)
        d.text((x + 54, y + 40 - 2), "", font=f(SANS_B, 9), fill=INK)
    elif kind == "bridge":
        d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        d.rectangle([x, y + 34, x + w, y + h], fill=SEA)
        d.rectangle([x + 4, y + 26, x + 62, y + 30], fill=(90, 90, 100))
        d.rectangle([x + 86, y + 26, x + w - 4, y + 30], fill=(90, 90, 100))
        d.arc([x + 8, y + 6, x + 58, y + 32], 180, 360, fill=(60, 60, 70),
              width=3)
        d.arc([x + 90, y + 6, x + 140, y + 32], 180, 360, fill=(60, 60, 70),
              width=3)
        d.polygon([(x + 74, y + 4), (x + 78, y + 12), (x + 84, y + 6),
                   (x + 80, y + 16), (x + 86, y + 18), (x + 78, y + 22),
                   (x + 74, y + 26), (x + 70, y + 16), (x + 64, y + 14),
                   (x + 70, y + 10)], fill=(255, 140, 0))
        d.text((x + 92, y + 2), "3RD HIT", font=f(SANS_B, 9), fill=RED)
    elif kind == "protest":
        d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
        for cx in [14, 30, 46, 62, 78, 94, 110, 126, 142]:
            d.ellipse([x + cx - 4, y + 22, x + cx + 4, y + 30], fill=INK)
            d.rectangle([x + cx - 6, y + 30, x + cx + 6, y + h],
                        fill=(60, 60, 70))
        d.rectangle([x + 22, y + 4, x + 127, y + 16], fill=RED)
        d.text((x + 28, y + 6), "LOCKDOWN", font=f(SANS_B, 9),
               fill=(255, 255, 255))
        d.text((x + 96, y + 6), "DHAKA", font=f(SANS_B, 9), fill=GOLD)
    else:
        raise ValueError(f"unknown scene kind {kind!r}")


# ---------------- content -------------------------------------------------
REGIONS = [
    ("Asia", 11, PURPLE), ("N. America", 10, RED), ("Europe", 6, BLUE),
    ("Middle East", 4, ORANGE), ("Africa", 3, GREEN), ("Oceania", 2, TEAL),
    ("Global", 1, GOLDD),
]

LEADS = [
    ("ASIA • TRILATERAL — REUTERS • AP", PURPLE, panel_trilateral,
     "Trump, Xi and Putin hold first three-way summit",
     "First-ever meeting of the three largest nuclear powers opens in "
     "Shenzhen; arms control on the table, Ukraine off the agenda."),
    ("EUROPE • ICJ — ICJ", BLUE, panel_icj,
     "World Court rules on Rohingya genocide case",
     "The Hague reads its judgment in The Gambia's case over the 2017 "
     "campaign; 730,000+ displaced. Final — no appeal."),
    ("N. AMERICA • ANTHROPIC — REUTERS", RED, panel_ant,
     "Anthropic starts trading on Nasdaq as ANT",
     "Priced at $83 — above the $70–78 range; 980m shares, $81.3bn; "
     "the biggest IPO on record."),
]

# (num, kicker, colour, scene, headline, deck)
CARDS = [
    (4, "GTA VI — REUTERS", RED, "gta",
     "GTA VI launches today",
     "$79.99–$99.99; 212 GB"),
    (5, "SUNEUNG — AP", PURPLE, "exam",
     "550,000 sit Korea's Suneung exam",
     "Flights paused for the test"),
    (6, "FLORIDA — AP", RED, "flood",
     "Florida floods shut schools Thursday",
     "Schools shut; 300+ rescues"),
    (7, "JOBS — ABS", TEAL, "jobs",
     "Australia jobless hits 4.9%, a five-year high",
     "Down 43,500; youth 11.3%"),
    (8, "AKVAN — IMD", PURPLE, "cyclone",
     "Cyclone Akvan nears India's east coast",
     "47,000 moved to safety"),
    (9, "COP31 — AP", GOLDD, "cop",
     "COP31 enters its final 48 hours",
     "$120bn adaptation goal"),
    (10, "BRIDGE — REUTERS", BLUE, "bridge",
     "Crimean Bridge hit a third time this week",
     "Traffic suspended"),
    (11, "DHAKA — REUTERS", PURPLE, "protest",
     "Bangladesh lockdown turns violent",
     "Toll unconfirmed"),
]

# (num, region colour, text) — every line verified to fit one 15px line.
# Column 1: Asia–Pacific (8). Column 2: Europe • Middle East • Africa (11).
# Column 3: The Americas (7).
ALSO_COLS = [
    ("ASIA–PACIFIC", [
        (13, PURPLE, "APEC adopts Shenzhen Declaration"),
        (16, PURPLE, "India–Japan hold 2+2 dialogue"),
        (24, PURPLE, "Taiwan amends Anti-Infiltration Act"),
        (30, PURPLE, "Cricket: India v NZ, 1st Test"),
        (31, TEAL, "Oceania bowls: Auckland 19–22 Nov"),
        (34, PURPLE, "Amazon $7bn India renewables (reported)"),
        (35, PURPLE, "Pakistan v Sri Lanka, 2nd Test"),
        (37, PURPLE, "Bank Indonesia hikes rates 25bp"),
    ]),
    ("EUROPE • MIDDLE EAST • AFRICA", [
        (12, ORANGE, "Houthi missile at Riyadh intercepted"),
        (14, BLUE, "Ukraine watches Shenzhen, off agenda"),
        (15, BLUE, "EU delays methane rules two years"),
        (17, BLUE, "France minister hits out at Mélenchon"),
        (18, ORANGE, "Saudi: danger passed in south"),
        (19, GREEN, "Libya seizes cocaine and pills"),
        (25, BLUE, "McDonald's sex-abuse probe (BBC)"),
        (29, GREEN, "FIFA U17 World Cup: matchday 1"),
        (32, ORANGE, "UAE economy forecast +7.3% (IMF)"),
        (33, ORANGE, "Sharjah hotels recover after oil spill"),
        (36, GREEN, "SA v Bangladesh, 1st Test day 5"),
    ]),
    ("THE AMERICAS", [
        (20, RED, "Bukele acts on Haiti gang leader"),
        (21, RED, "Microsoft in AI talks with ByteDance"),
        (22, RED, "US senators warn of AI cyber threat"),
        (23, RED, "Liu Yunping elected caucus chair"),
        (26, RED, "Oil: WTI −3.2% to $83.26"),
        (27, RED, "Markets (18 Nov close): Dow −561"),
        (28, RED, "Nvidia −2.9%; Bitcoin $63,454"),
    ]),
]

# pins keyed to story numbers: (story, lon, lat[, offset lon, lat])
PINS = [
    (1, 114.1, 22.5),            # Shenzhen
    (2, 4.3, 52.1, 14, 58),      # The Hague, offset up-right
    (3, -74.0, 40.7, -64, 46),   # New York, offset up-left
    (5, 127.0, 37.5),            # Seoul
    (6, -80.2, 25.8),            # Miami
    (7, 151.2, -33.9),           # Sydney
    (8, 80.2, 16.5),             # Akvan coast
    (10, 36.5, 45.3),            # Crimean Bridge
    (12, 46.7, 24.7),            # Riyadh
]

NUMBERS = [
    ("$81.3bn", "ANTHROPIC IPO"),
    ("730,000", "ROHINGYA DISPLACED"),
    ("7.71m", "GTA VI PRE-ORDERS"),
    ("$120bn", "COP31 GOAL"),
    ("47,000", "MOVED FROM AKVAN"),
    ("550,000", "SUNEUNG STUDENTS"),
    ("4.9%", "AUSTRALIA JOBLESS"),
]

TIMELINE = ("UTC  18 NOV 23:36 3RD BRIDGE ATTACK  •  "
            "01:05 BRIDGE (BBC)  •  01:46 TRUMP–XI  •  "
            "02:57 EU METHANE DELAY  •  ~03:00 HOUTHI MISSILE DOWN  •  "
            "06:30 TRILATERAL OPENS")

DATE_CHECK = ("DATE CHECK — Not 19 November: Kerch collapse, Nvidia results, "
              "Jeffries vote, Van Gogh sale, Voyager crossing, Pew report "
              "(all 17–18 Nov).")


def build(out="entry.png"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    mx = 20

    # ---- masthead: black serif date, red italic sub-head ----
    d.text((mx, 6), "THE WORLD TODAY", font=f(SANS_B, 14), fill=INK)
    rtext(d, W - mx, 6, "VOL. I — No. 323  •  ONE DAY, ONE PAGE",
          f(SANS_B, 11), GREY)
    d.line([mx, 26, W - mx, 26], fill=INK, width=1)
    d.text((mx, 30), "Thursday 19 November 2026",
           font=f(SERIF_B, 46), fill=INK)
    sub = ("Trump, Xi and Putin hold a first three-way summit — as GTA VI "
           "launches and Anthropic debuts on Nasdaq.")
    sub = one_line(d, sub, f(SERIF_I, 15), W - 2 * mx, "sub-headline")
    d.text((mx, 84), sub, font=f(SERIF_I, 15), fill=CRIMSON)
    d.line([mx, 106, W - mx, 106], fill=INK, width=2)
    d.line([mx, 109, W - mx, 109], fill=INK, width=1)

    # ---- region bar + legend ----
    total = sum(c for _, c, _ in REGIONS)
    assert total == 37, f"region counts sum to {total}, not 37"
    bar_y, bar_h = 116, 13
    cum = 0
    for name, count, col in REGIONS:
        x0 = mx + 984 * cum // 37
        cum += count
        x1 = mx + 984 * cum // 37
        d.rectangle([x0, bar_y, x1, bar_y + bar_h], fill=col)
        d.text((x0 + (x1 - x0) // 2 - 3, bar_y + 1), str(count),
               font=f(SANS_B, 9), fill=(255, 255, 255))
    lx = mx
    ly = 131
    for name, count, col in REGIONS:
        d.rectangle([lx, ly + 2, lx + 10, ly + 12], fill=col)
        lab = f"{name} {count}"
        d.text((lx + 13, ly), lab, font=f(SANS_B, 10), fill=INK)
        lx += 13 + d.textlength(lab, font=f(SANS_B, 10)) + 16
    d.text((mx, 131), "", font=f(SANS_B, 10), fill=INK)

    # ---- big red numbers strip ----
    d.rectangle([0, 148, W, 196], fill=(255, 255, 255), outline=INK, width=1)
    d.line([0, 148, W, 148], fill=INK, width=1)
    d.line([0, 196, W, 196], fill=INK, width=1)
    cell = 984 // len(NUMBERS)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = mx + i * cell + cell // 2
        nw = d.textlength(num, font=f(SERIF_B, 21))
        d.text((cx - nw // 2, 152), num, font=f(SERIF_B, 21), fill=RED)
        lw = d.textlength(lab, font=f(SANS_B, 8))
        d.text((cx - lw // 2, 178), lab, font=f(SANS_B, 8), fill=INK)
        if i:
            d.line([mx + i * cell, 154, mx + i * cell, 190],
                   fill=(200, 200, 190), width=1)

    # ---- three leads ----
    pw, ph, pg = 322, 108, 9
    ly0 = 204
    for i, (kick, col, panel, head, deck) in enumerate(LEADS):
        x = mx + i * (pw + pg)
        panel(d, x, ly0, pw, ph)
        kicker(d, x, ly0 + ph + 6, i + 1, kick, col, max_w=pw)
        para(d, x, ly0 + ph + 22, head, f(SERIF_B, 17), pw, max_lines=2,
             leading=19, what=f"lead {i + 1} headline")
        para(d, x, ly0 + ph + 62, deck, f(SERIF, 11), pw, max_lines=2,
             leading=13, what=f"lead {i + 1} deck")
    d.line([mx, 404, W - mx, 404], fill=INK, width=2)

    # ---- middle band: 8 cards (4+4) left, dark-navy map right ----
    cw, chh, cgap = 149, 48, 9
    cards_x0 = mx
    for idx, (num, kick, col, kind, head, deck) in enumerate(CARDS):
        row, c = divmod(idx, 4)
        x = cards_x0 + c * (cw + cgap)
        y = 412 + row * 132
        scene(d, x, y, cw, chh, kind)
        kicker(d, x, y + chh + 4, num, kick, col, max_w=cw)
        para(d, x, y + chh + 20, head, f(SERIF_B, 13), cw, max_lines=3,
             leading=15, what=f"card {num} headline")
        deck = one_line(d, deck, f(SERIF, 10), cw, f"card {num} deck")
        d.text((x, y + chh + 20 + 45), deck, font=f(SERIF, 10), fill=INK)

    map_x, map_y, map_w = 660, 412, 344
    d.text((map_x, 412), "WHERE IT HAPPENED", font=f(SANS_B, 12), fill=RED)
    draw_map_navy(d, map_x, 430, map_w, 196, PINS)
    para(d, map_x, 632,
         "Pins are story numbers: 1 Shenzhen · 2 The Hague · 3 New York · "
         "5 Seoul · 6 Miami · 7 Sydney · 8 Akvan coast · 10 Crimea · "
         "12 Riyadh",
         f(SANS, 9), map_w, fill=GREY, max_lines=3, leading=11,
         what="map caption")
    d.line([mx, 676, W - mx, 676], fill=INK, width=2)

    # ---- UTC timeline (single navy band) ----
    d.rectangle([mx, 684, W - mx, 702], fill=NAVY)
    line = one_line(d, TIMELINE, f(SANS, 9), 984 - 16, "timeline")
    tx = mx + (984 - d.textlength(line, font=f(SANS, 9))) // 2
    d.text((tx, 689), line, font=f(SANS, 9), fill=(255, 255, 255))

    # ---- also list: 3 columns under region headers ----
    d.text((mx, 712), "ALSO ON THURSDAY 19 NOVEMBER",
           font=f(SANS_B, 12), fill=RED)
    d.line([mx, 730, W - mx, 730], fill=INK, width=1)
    colw = 320
    for ci, (chead, items) in enumerate(ALSO_COLS):
        x = mx + ci * (colw + 12)
        d.text((x, 736), chead, font=f(SANS_B, 10), fill=CRIMSON)
        yy = 752
        for n, col, item in items:
            d.ellipse([x, yy + 4, x + 7, yy + 11], fill=col)
            d.ellipse([x + 10, yy + 1, x + 23, yy + 14], fill=PURPLE)
            d.text((x + 12 if n < 10 else x + 10.5, yy + 2.5), str(n),
                   font=f(SANS_B, 8), fill=(255, 255, 255))
            item = one_line(d, item, f(SERIF, 15), colw - 32,
                            f"also {n}")
            d.text((x + 28, yy), item, font=f(SERIF, 15), fill=INK)
            yy += 18

    # ---- date check (one line) + sources ----
    d.line([mx, 960, W - mx, 960], fill=INK, width=2)
    d.rectangle([mx, 966, W - mx, 992], outline=RED, width=2,
                fill=(255, 250, 245))
    dc = one_line(d, DATE_CHECK, f(SANS, 10), W - 2 * mx - 16, "date check")
    d.text((mx + 8, 973), dc, font=f(SANS, 10), fill=INK)
    d.text((mx, 1000),
           "Sources: Reuters, BBC, AP, ICJ, ABS, IMD, Nature, IMF — "
           "19 November 2026. All drawings original.",
           font=f(SANS, 9), fill=GREY)

    # ---- count verification ----
    n_total = len(LEADS) + len(CARDS) + sum(len(it) for _, it in ALSO_COLS)
    assert n_total == 37, f"total stories {n_total}, not 37"
    assert len(PINS) == 9, f"{len(PINS)} pins, need 9"
    assert sorted(n for n, _, _ in
                  [(n, c, t) for _, it in ALSO_COLS for n, c, t in it]) == \
        list(range(12, 38)), "also-list numbers must be 12..37"

    img.save(out, optimize=True)
    print(out, img.size, len(open(out, "rb").read()), "bytes")


if __name__ == "__main__":
    build(os.path.join(HERE, "entry.png"))
