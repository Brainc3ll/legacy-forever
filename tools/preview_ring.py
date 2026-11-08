#!/usr/bin/env python3
"""Proposal previews for #313: the zone completion corner with its percent in a round progress ring.

The ring is the client's own circular progress widget, the Journeys renown ring (Blizzard_Journeys.xml): the
UI-Journeys-renown-radial-bar track with a Cooldown over it whose swipe is UI-Journeys-renown-radial-fill,
reverse, rotation 180, so the fill starts at the track's notch at the bottom and runs clockwise
(CooldownFrame_SetDisplayAsPercentage). The fill takes NORMAL_FONT_COLOR, GREEN_FONT_COLOR once the zone is done.

    python3 tools/preview_ring.py        # writes docs/previews/zone-ring-*.png

Variant a sits on the corner's existing Shade wash; variant b sits in DialogBorderTranslucentTemplate.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import screenshots as s
from PIL import Image, ImageChops, ImageDraw
from wowmock import FONTS, dialog_border, scene

OUT = s.ROOT / "docs" / "previews"
RING = 52  # the Journeys card draws its 96-pixel ring at 60; 52 holds "100%" in GameFontNormal
GAP = 8


def swipe(ui, size_px, percent, color):
    """The fill atlas tinted, cut to a wedge from the bottom notch clockwise over `percent` of the circle."""
    fill = ui.atlas("UI-Journeys-renown-radial-fill").image.resize((size_px, size_px), Image.LANCZOS)
    mask = Image.new("L", (size_px * 4, size_px * 4), 0)
    if percent >= 100:
        mask.paste(255, (0, 0, mask.width, mask.height))
    elif percent > 0:
        # PIL angles run clockwise from 3 o'clock; the notch is at 6 o'clock (90).
        ImageDraw.Draw(mask).pieslice((0, 0, mask.width - 1, mask.height - 1), 90, 90 + 360 * percent / 100, fill=255)
    mask = mask.resize((size_px, size_px), Image.LANCZOS)
    r, g, b = (round(c * 255) for c in color[:3])
    # The fill is a grey ramp: SetSwipeColor multiplies its luminance into the colour.
    lum = fill.convert("L")
    channels = [Image.eval(lum, lambda v, c=c: v * c // 255) for c in (r, g, b)]
    tinted = Image.merge("RGBA", [*channels, ImageChops.multiply(fill.getchannel("A"), mask)])
    return tinted


def ring(ui, canvas, x, y, result):
    percent = result["percent"] or 0
    color = ui.global_color("GREEN_FONT_COLOR" if result["complete"] else "NORMAL_FONT_COLOR")
    canvas.draw(ui.atlas("UI-Journeys-renown-radial-bar"), x, y, RING, RING)
    canvas.draw(swipe(ui, canvas.px(x + RING) - canvas.px(x), percent, color), x, y, RING, RING)
    font = FONTS["GameFontNormal"]
    text = f"{percent}%"
    canvas.text(x, y + RING / 2 - font.height / 2, text, font, color=color, justify="CENTER", width=RING)


def block_size(ui, canvas, result, name):
    title, counts = FONTS["GameFontNormalLarge"], FONTS["GameFontHighlight"]
    text_w = max(canvas.text_width(name, title), canvas.text_width(s.counts_text(ui, result, 16), counts))
    return RING + GAP + text_w, RING


def make_corner(variant):
    def corner(ui, canvas, rects, art, zone, result, name, pins, collapsed=False):
        width, height = block_size(ui, canvas, result, name)
        left, top = s.corner_origin(rects, art, zone, pins, width, height)
        cx, cy, _, _ = rects["container"]
        x, y = cx + left, cy + top
        if variant == "a":
            shade = Image.open(s.ROOT / "media" / "Shade.tga").convert("RGBA")
            canvas.draw(shade, x - 48, y - 22, width + 48 + 64, height + 44, (1, 1, 1, 0.6))
        else:
            dialog_border(canvas, x - 18, y - 18, width + 40, height + 36)
        ring(ui, canvas, x, y, result)
        title, counts = FONTS["GameFontNormalLarge"], FONTS["GameFontHighlight"]
        tx = x + RING + GAP
        canvas.text(tx, y + RING / 2 - title.height - 2, name, title)
        canvas.text(tx, y + RING / 2 + 4, s.counts_text(ui, result, 16), counts)

    return corner


def main():
    ui = s.make_ui(scale=2)
    data = s.load_data()
    live = s.Live(ui, data)
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in ("a", "b"):
        s.completion_corner = make_corner(variant)
        for label, ui_map in (("ashenvale", s.ASHENVALE), ("felwood", s.FELWOOD)):
            canvas, _ = s.world_map(ui, data, live, ui_map)
            path = OUT / f"zone-ring-{variant}-{label}.png"
            scene(ui, [(canvas, 0, 0)]).save(path)
            print(f"wrote {path}")
        # The finished state: Ashenvale's own counts, every category complete.
        result = dict(live.model.completion[s.ASHENVALE])
        result = {
            k: ({**v, "done": v["total"], "complete": True} if isinstance(v, dict) and "total" in v else v)
            for k, v in result.items()
        }
        result.update(percent=100, complete=True)
        live.model.completion[s.ASHENVALE], saved = result, live.model.completion[s.ASHENVALE]
        canvas, _ = s.world_map(ui, data, live, s.ASHENVALE)
        live.model.completion[s.ASHENVALE] = saved
        path = OUT / f"zone-ring-{variant}-complete.png"
        scene(ui, [(canvas, 0, 0)]).save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
