#!/usr/bin/env python3
"""The World in One Image -- Wednesday 25 November 2026.

A deterministic program that draws a newspaper-front-page style infographic
summarising the world news of Wednesday 25 November 2026, and writes it to
/output/entry.png (1024x1024 PNG).

No randomness, no clock, no network: every run produces byte-identical
output. All artwork is drawn with PIL primitives (rectangles, ellipses,
polygons, lines); all text uses system DejaVu / Liberation fonts.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------
W = H = 1024
BG = (247, 243, 234)          # warm paper white
INK = (26, 26, 26)            # near-black ink
RED = (179, 32, 42)           # accent red
DARK_RED = (140, 22, 32)
SEA = (43, 74, 94)            # slate sea
SEA_DARK = (33, 58, 74)
SKY_TOP = (203, 216, 220)
SKY_BOT = (226, 231, 228)
SHIP = (30, 33, 38)           # silhouette
SHIP2 = (52, 57, 63)
FLAME_O = (232, 100, 30)
FLAME_Y = (242, 176, 53)
SMOKE1 = (105, 109, 112)
SMOKE2 = (154, 158, 160)
PANEL_BG = (255, 253, 247)
BORDER = (26, 26, 26)

OUT_PATH = "/output/entry.png"

FONT_DIR_DEJAVU = "/usr/share/fonts/truetype/dejavu"
FONT_DIR_LIB = "/usr/share/fonts/truetype/liberation"


def font(path_candidates, size):
    for p in path_candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise FileNotFoundError(path_candidates)


def dejavu_bold(size):
    return font([os.path.join(FONT_DIR_DEJAVU, "DejaVuSans-Bold.ttf"),
                 os.path.join(FONT_DIR_LIB, "LiberationSans-Bold.ttf")], size)


def lib_bold(size):
    return font([os.path.join(FONT_DIR_LIB, "LiberationSans-Bold.ttf"),
                 os.path.join(FONT_DIR_DEJAVU, "DejaVuSans-Bold.ttf")], size)


def lib_regular(size):
    return font([os.path.join(FONT_DIR_LIB, "LiberationSans-Regular.ttf"),
                 os.path.join(FONT_DIR_DEJAVU, "DejaVuSans.ttf")], size)


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------
def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def draw_centered(draw, cx, y, s, fnt, fill):
    w = text_w(draw, s, fnt)
    draw.text((cx - w / 2, y), s, font=fnt, fill=fill)


def draw_spaced_centered(draw, cx, y, s, fnt, fill, tracking):
    """Draw text with manual letter tracking, centred on cx."""
    widths = [text_w(draw, ch, fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap by measured pixel width. Fully deterministic."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# Icons (simple silhouettes in a box at x, y of size s)
# --------------------------------------------------------------------------
def icon_riyadh(d, x, y, s):
    # tall tower + side building + flame on top
    d.rectangle([x + s * 0.34, y + s * 0.28, x + s * 0.62, y + s * 0.98], fill=INK)
    d.rectangle([x + s * 0.66, y + s * 0.55, x + s * 0.94, y + s * 0.98], fill=INK)
    d.rectangle([x + s * 0.06, y + s * 0.70, x + s * 0.30, y + s * 0.98], fill=INK)
    fx, fy = x + s * 0.48, y + s * 0.30
    d.polygon([(fx - s * 0.13, fy), (fx, fy - s * 0.30), (fx + s * 0.13, fy)], fill=RED)
    d.polygon([(fx - s * 0.07, fy), (fx, fy - s * 0.17), (fx + s * 0.07, fy)], fill=FLAME_Y)


def icon_markets(d, x, y, s):
    # axes + plunging red line with arrowhead
    d.line([x + s * 0.10, y + s * 0.08, x + s * 0.10, y + s * 0.90], fill=INK, width=4)
    d.line([x + s * 0.10, y + s * 0.90, x + s * 0.95, y + s * 0.90], fill=INK, width=4)
    pts = [(x + s * 0.16, y + s * 0.22), (x + s * 0.38, y + s * 0.36),
           (x + s * 0.54, y + s * 0.30), (x + s * 0.86, y + s * 0.78)]
    d.line(pts, fill=RED, width=6, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - s * 0.16, ay - s * 0.02), (ax - s * 0.03, ay - s * 0.16)], fill=RED)


def icon_ukraine(d, x, y, s):
    # drone: body + four rotor discs
    cx, cy = x + s * 0.5, y + s * 0.52
    for dx, dy in [(-0.30, -0.26), (0.30, -0.26), (-0.30, 0.26), (0.30, 0.26)]:
        rx, ry = cx + s * dx, cy + s * dy
        d.line([cx, cy, rx, ry], fill=INK, width=4)
        d.ellipse([rx - s * 0.13, ry - s * 0.06, rx + s * 0.13, ry + s * 0.06], outline=INK, width=4)
    d.rectangle([cx - s * 0.13, cy - s * 0.10, cx + s * 0.13, cy + s * 0.10], fill=INK)
    d.ellipse([cx - s * 0.05, cy - s * 0.05, cx + s * 0.05, cy + s * 0.05], fill=RED)


def icon_huawei(d, x, y, s):
    # microchip: body, core, pins
    bx0, by0, bx1, by1 = x + s * 0.24, y + s * 0.24, x + s * 0.76, y + s * 0.76
    for t in (0.34, 0.50, 0.66):
        px, py = x + s * t, y + s * t
        d.line([px, y + s * 0.06, px, by0], fill=INK, width=4)
        d.line([px, by1, px, y + s * 0.94], fill=INK, width=4)
        d.line([x + s * 0.06, py, bx0, py], fill=INK, width=4)
        d.line([bx1, py, x + s * 0.94, py], fill=INK, width=4)
    d.rectangle([bx0, by0, bx1, by1], fill=INK)
    d.rectangle([x + s * 0.40, y + s * 0.40, x + s * 0.60, y + s * 0.60], fill=RED)


def icon_climate(d, x, y, s):
    # thermometer with red mercury
    tx = x + s * 0.44
    d.rounded_rectangle([tx - s * 0.09, y + s * 0.06, tx + s * 0.09, y + s * 0.68],
                        radius=s * 0.09, outline=INK, width=5)
    d.ellipse([tx - s * 0.17, y + s * 0.58, tx + s * 0.17, y + s * 0.92], outline=INK, width=5)
    d.rectangle([tx - s * 0.045, y + s * 0.34, tx + s * 0.045, y + s * 0.70], fill=RED)
    d.ellipse([tx - s * 0.10, y + s * 0.65, tx + s * 0.10, y + s * 0.85], fill=RED)
    for t in (0.18, 0.32, 0.46):
        d.line([tx + s * 0.13, y + s * t, tx + s * 0.26, y + s * t], fill=INK, width=4)
    # sun behind
    sx, sy = x + s * 0.76, y + s * 0.24
    d.ellipse([sx - s * 0.11, sy - s * 0.11, sx + s * 0.11, sy + s * 0.11], fill=FLAME_Y)


def icon_space(d, x, y, s):
    # rocket with red fin/flame
    cx = x + s * 0.5
    d.polygon([(cx, y + s * 0.04), (cx + s * 0.15, y + s * 0.30),
               (cx + s * 0.15, y + s * 0.62), (cx - s * 0.15, y + s * 0.62),
               (cx - s * 0.15, y + s * 0.30)], fill=INK)
    d.ellipse([cx - s * 0.06, y + s * 0.26, cx + s * 0.06, y + s * 0.38], fill=BG)
    d.polygon([(cx - s * 0.15, y + s * 0.50), (cx - s * 0.30, y + s * 0.74),
               (cx - s * 0.15, y + s * 0.74)], fill=RED)
    d.polygon([(cx + s * 0.15, y + s * 0.50), (cx + s * 0.30, y + s * 0.74),
               (cx + s * 0.15, y + s * 0.74)], fill=RED)
    d.polygon([(cx - s * 0.07, y + s * 0.98), (cx, y + s * 0.74), (cx + s * 0.07, y + s * 0.98)],
              fill=FLAME_O)


ICONS = {
    "RIYADH": icon_riyadh,
    "MARKETS": icon_markets,
    "UKRAINE": icon_ukraine,
    "HUAWEI": icon_huawei,
    "CLIMATE": icon_climate,
    "SPACE": icon_space,
}

PANELS = [
    ("RIYADH", "Houthi strike hits tower and oil refinery; 11 injured"),
    ("MARKETS", "Asia stocks plunge: KOSPI \u22126.2%, Nikkei \u22122.8%; Dow tops 50,000"),
    ("UKRAINE", "Drones strike Rosneft refineries; Kyiv and Odesa hit"),
    ("HUAWEI", "US jury convicts Huawei of bank fraud, trade-secret theft"),
    ("CLIMATE", "COP31 ends without a deal; Pope warns on extreme weather"),
    ("SPACE", "Shenzhou-24 docks with Tiangong space station"),
]


# --------------------------------------------------------------------------
# Scene: Strait of Hormuz
# --------------------------------------------------------------------------
def tanker(d, x, y, scale, hull_col, burning):
    """Draw a tanker silhouette with its keel line at y."""
    hull_w, hull_h = 340 * scale, 34 * scale
    # hull (bow to the right)
    d.polygon([(x, y - hull_h), (x + hull_w * 0.86, y - hull_h),
               (x + hull_w, y - hull_h * 0.35), (x + hull_w * 0.94, y),
               (x + hull_w * 0.08, y), (x, y - hull_h * 0.3)], fill=hull_col)
    # deck line and cargo hatches
    d.rectangle([x + hull_w * 0.10, y - hull_h - 8 * scale,
                 x + hull_w * 0.62, y - hull_h], fill=hull_col)
    # bridge / superstructure at the stern (left)
    d.rectangle([x + hull_w * 0.06, y - hull_h - 52 * scale,
                 x + hull_w * 0.20, y - hull_h - 8 * scale], fill=hull_col)
    d.rectangle([x + hull_w * 0.09, y - hull_h - 66 * scale,
                 x + hull_w * 0.17, y - hull_h - 52 * scale], fill=hull_col)
    # mast amidships
    d.line([x + hull_w * 0.45, y - hull_h - 8 * scale,
            x + hull_w * 0.45, y - hull_h - 58 * scale], fill=hull_col, width=max(2, int(4 * scale)))
    if burning:
        fx = x + hull_w * 0.38
        fy = y - hull_h - 6 * scale
        # smoke plume (kept inside the scene box: max rise 195 units)
        for (sx, sy, r, col) in [(0.46, -118, 30, SMOKE2), (0.52, -140, 38, SMOKE1),
                                 (0.60, -160, 46, SMOKE2), (0.70, -178, 52, SMOKE1),
                                 (0.82, -195, 58, SMOKE2)]:
            cx, cy = x + hull_w * sx, y + sy * scale
            d.ellipse([cx - r * scale, cy - r * 0.62 * scale,
                       cx + r * scale, cy + r * 0.62 * scale], fill=col)
        # flames: layered teardrops
        for (dx, hgt, wid, col) in [(0.0, 120, 30, RED), (26, 150, 34, FLAME_O),
                                    (54, 105, 26, RED), (30, 92, 22, FLAME_Y),
                                    (8, 70, 18, FLAME_Y)]:
            cx = fx + dx * scale
            d.polygon([(cx - wid * scale, fy), (cx, fy - hgt * scale),
                       (cx + wid * scale, fy)], fill=col)
            d.ellipse([cx - wid * scale, fy - wid * 0.5 * scale,
                       cx + wid * scale, fy + wid * 0.5 * scale], fill=col)


def draw_headline_scene(d):
    x0, y0, x1, y1 = 36, 208, 988, 428
    # sky: two flat bands (deterministic gradient feel)
    d.rectangle([x0, y0, x1, 350], fill=SKY_BOT)
    d.rectangle([x0, y0, x1, 282], fill=SKY_TOP)
    # sea
    d.rectangle([x0, 350, x1, y1], fill=SEA)
    d.rectangle([x0, 350, x1, 358], fill=SEA_DARK)
    for i, wy in enumerate((374, 394, 412)):
        off = 60 if i % 2 else 0
        for wx in range(x0 + 40 + off, x1 - 60, 170):
            d.line([wx, wy, wx + 52, wy], fill=(86, 122, 140), width=3)
    # burning tanker (hero, left-centre) and intact tanker (right)
    tanker(d, 120, 392, 0.92, SHIP, burning=True)
    tanker(d, 618, 386, 0.66, SHIP2, burning=False)
    d.rectangle([x0, y0, x1, y1], outline=BORDER, width=3)


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------
def draw_panel(d, x, y, w, h, region, title):
    d.rectangle([x, y, x + w, y + h], fill=PANEL_BG, outline=BORDER, width=2)
    d.rectangle([x, y, x + 6, y + h], fill=RED)
    pad = 16
    icon_s = 48
    ICONS[region](d, x + pad + 4, y + 12, icon_s)
    f_region = lib_bold(28)
    d.text((x + pad + icon_s + 18, y + 22), region, font=f_region, fill=RED)
    # Title: start at 30px; shrink only as far as needed so the full
    # title fits the panel (no clipped words).
    size = 30
    while size > 20:
        f_title = lib_bold(size)
        lines = wrap(d, title, f_title, w - pad * 2 - 6)
        if len(lines) <= 4:
            break
        size -= 1
    ty = y + 62
    for ln in lines[:4]:
        d.text((x + pad + 4, ty), ln, font=f_title, fill=INK)
        ty += size + 5


# --------------------------------------------------------------------------
# Main composition
# --------------------------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # ---- Masthead -------------------------------------------------------
    d.rectangle([36, 14, 988, 16], fill=INK)
    draw_spaced_centered(d, cx, 24, "THE WORLD IN ONE IMAGE", lib_bold(26), RED, 10)
    draw_centered(d, cx, 54, "WEDNESDAY", dejavu_bold(80), INK)
    draw_centered(d, cx, 130, "25 NOVEMBER 2026", dejavu_bold(70), INK)
    d.rectangle([36, 196, 988, 200], fill=INK)

    # ---- Headline scene + caption --------------------------------------
    draw_headline_scene(d)
    cap_y = 436
    d.rectangle([36, cap_y, 44, 518], fill=RED)
    d.text((60, cap_y + 2), "STRAIT OF HORMUZ", font=dejavu_bold(44), fill=INK)
    d.text((60, cap_y + 54),
           "Two oil tankers hit naval mines and burst into flames",
           font=lib_regular(28), fill=INK)

    # ---- Six panels ------------------------------------------------------
    panel_w, panel_h, gap = 309, 200, 10
    top = 528
    for i, (region, title) in enumerate(PANELS):
        col, row = i % 3, i // 3
        px = 36 + col * (panel_w + gap)
        py = top + row * (panel_h + gap)
        draw_panel(d, px, py, panel_w, panel_h, region, title)

    # ---- Bottom banner ---------------------------------------------------
    by0, by1 = 948, 1002
    d.rectangle([36, by0, 988, by1], fill=RED)
    banner_lines = [
        "ALSO TODAY: Gaza strike kills Hamas security chief \u2022 "
        "Dell posts record AI-server sales",
        "Colombia frees supermarket hostages \u2022 "
        "Shenzhou-24 crew arrives at Tiangong",
    ]
    size = 23
    while size > 12 and any(text_w(d, s, lib_bold(size)) > 936 for s in banner_lines):
        size -= 1
    f_banner = lib_bold(size)
    draw_centered(d, cx, by0 + 4, banner_lines[0], f_banner, (255, 255, 255))
    draw_centered(d, cx, by0 + 29, banner_lines[1], f_banner, (255, 255, 255))

    return img


def main():
    img = build()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.save(OUT_PATH, format="PNG", optimize=False)
    print(f"wrote {OUT_PATH}: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
