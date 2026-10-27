#!/usr/bin/env python3
"""
Generate a 1200x630 social preview image (Open Graph / Twitter card) for birds.cowneck.com
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def load_font(size, italic=False, bold=False):
    georgia_paths = [
        "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf" if (bold and italic)
        else "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Georgia Italic.ttf" if italic
        else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/NewYork.ttf",
        "/System/Library/Fonts/Times.ttc",
    ]
    for p in georgia_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def create_og_image():
    SCALE = 2
    W, H = 1200 * SCALE, 630 * SCALE

    # Diagonal forest green gradient matching header (#1a472a -> #2d7a4a)
    base = Image.new("RGBA", (W, H), (26, 71, 42, 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((int(W * 0.35), int(-H * 0.2), int(W * 1.15), int(H * 1.2)), fill=(45, 122, 74, 220))
    gdraw.ellipse((int(-W * 0.2), int(H * 0.3), int(W * 0.5), int(H * 1.1)), fill=(212, 165, 116, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(140 * SCALE))
    img = Image.alpha_composite(base, glow)

    # Right side: Cardinal photo card
    card_path = "optimized_images/cardinal.webp"
    if os.path.exists(card_path):
        bird = Image.open(card_path).convert("RGBA")
        bw, bh = bird.size
        # Crop a square centered on the cardinal (avoiding bottom-right corner watermark)
        crop_size = int(min(bw, bh) * 0.92)
        cx = int(bw * 0.58)
        cy = int(bh * 0.48)
        x0 = max(0, min(bw - crop_size, cx - crop_size // 2))
        y0 = max(0, min(bh - crop_size, cy - crop_size // 2))
        bird_crop = bird.crop((x0, y0, x0 + crop_size, y0 + crop_size))

        target_size = 430 * SCALE
        bird_resized = bird_crop.resize((target_size, target_size), Image.Resampling.LANCZOS)

        radius = 28 * SCALE
        mask = Image.new("L", (target_size, target_size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, target_size, target_size), radius=radius, fill=255)

        card_x = 670 * SCALE
        card_y = (H - target_size) // 2

        # Drop shadow
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        sdraw.rounded_rectangle(
            (card_x, card_y + 12 * SCALE, card_x + target_size, card_y + target_size + 12 * SCALE),
            radius=radius,
            fill=(0, 0, 0, 110),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(24 * SCALE))
        img = Image.alpha_composite(img, shadow)

        # Paste bird
        card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        card_layer.paste(bird_resized, (card_x, card_y), mask)

        # Warm gold border (#d4a574)
        bdraw = ImageDraw.Draw(card_layer)
        bdraw.rounded_rectangle(
            (card_x, card_y, card_x + target_size, card_y + target_size),
            radius=radius,
            outline=(212, 165, 116, 180),
            width=3 * SCALE,
        )
        img = Image.alpha_composite(img, card_layer)

    # Left side typography
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    f_title = load_font(64 * SCALE)
    f_sub = load_font(26 * SCALE, italic=True)

    left_x = 95 * SCALE
    # Warm gold (#d4a574) title
    draw.text((left_x, 195 * SCALE), "Birds of", font=f_title, fill=(212, 165, 116, 255))
    draw.text((left_x, 275 * SCALE), "Port Washington", font=f_title, fill=(212, 165, 116, 255))

    # Subtle gold divider line
    draw.line(
        [(left_x, 378 * SCALE), (left_x + 120 * SCALE, 378 * SCALE)],
        fill=(212, 165, 116, 140),
        width=2 * SCALE,
    )

    # Soft cream (#f5e6d3) italic subtitle
    draw.text(
        (left_x, 405 * SCALE),
        "A curated guide to our local avian visitors",
        font=f_sub,
        fill=(245, 230, 211, 240),
    )

    img = Image.alpha_composite(img, text_layer)
    final_img = img.resize((1200, 630), Image.Resampling.LANCZOS).convert("RGB")
    final_img.save("og-image.jpg", "JPEG", quality=92, subsampling=0, optimize=True)
    print("Created birds/og-image.jpg (1200x630)")


if __name__ == "__main__":
    create_og_image()
