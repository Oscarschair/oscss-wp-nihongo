import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_ogp_images():
    # We will generate two versions:
    # 1. 1200 x 630 (Standard SNS OGP, 1.91:1) -> assets/images/og-image.png
    # 2. 1200 x 900 (WordPress Theme Screenshot, 4:3) -> screenshot.png
    
    font_bold = 'C:/Windows/Fonts/meiryob.ttc'
    font_reg = 'C:/Windows/Fonts/meiryo.ttc'
    
    # Generate 1200x630 (OGP)
    img_ogp = render_canvas(1200, 630, font_bold, font_reg, is_ogp=True)
    
    # Generate 1200x900 (Theme Screenshot)
    img_screen = render_canvas(1200, 900, font_bold, font_reg, is_ogp=False)
    
    # Save local files
    ogp_path = 'assets/images/og-image.png'
    screen_path = 'screenshot.png'
    
    img_ogp.convert('RGB').save(ogp_path, 'PNG', quality=95)
    img_screen.convert('RGB').save(screen_path, 'PNG', quality=95)
    
    # Also save to artifact dir for preview
    art_dir = r'C:\Users\user\.gemini\antigravity-ide\brain\c0513cbd-8f44-41c6-8255-620c41a77cbd'
    img_ogp.convert('RGB').save(os.path.join(art_dir, 'preview_ogp_fixed.png'), 'PNG', quality=95)
    img_screen.convert('RGB').save(os.path.join(art_dir, 'preview_screenshot_fixed.png'), 'PNG', quality=95)
    
    print("Generated OGP and Screenshot successfully!")

def render_canvas(W, H, font_bold, font_reg, is_ogp=True):
    base = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(base)

    # 1. Background Gradient (Soft warm lavender-cream -> pastel sky blue)
    # Top: #f8f6fc, Bottom: #eef7fc
    for y in range(H):
        ratio = y / H
        r = int(250 - ratio * 16)
        g = int(246 + ratio * 3)
        b = int(254 - ratio * 2)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Subtle decorative seigaiha / wave patterns in background
    pattern_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pattern_layer)
    for cx in range(0, W + 100, 80):
        for cy in range(0, H + 100, 80):
            for radius in [15, 30, 45, 60]:
                pdraw.ellipse(
                    [cx - radius, cy - radius, cx + radius, cy + radius],
                    outline=(190, 180, 230, 14),
                    width=1
                )
    base = Image.alpha_composite(base, pattern_layer)

    # 3. Soft glow & pastel ambient blobs behind character & cards
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    
    # Warm character spotlight
    hero_center_y = 310 if is_ogp else 450
    gdraw.ellipse([680, hero_center_y - 280, 1220, hero_center_y + 260], fill=(255, 255, 255, 230))
    # Soft accent colors
    gdraw.ellipse([640, hero_center_y - 260, 820, hero_center_y - 80], fill=(254, 226, 226, 110))   # sakura pink
    gdraw.ellipse([1040, hero_center_y + 120, 1260, hero_center_y + 300], fill=(224, 242, 254, 140)) # soft sky
    gdraw.ellipse([700, hero_center_y + 140, 860, hero_center_y + 300], fill=(254, 243, 199, 120))  # soft lemon
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    base = Image.alpha_composite(base, glow)
    draw = ImageDraw.Draw(base)

    # 4. Oscar Hero Character & Soft Floor Shadow
    hero_path = 'assets/images/hero-oscar-v2.png'
    if os.path.exists(hero_path):
        hero = Image.open(hero_path).convert('RGBA')
        target_h = 520 if is_ogp else 620
        h_ratio = target_h / hero.height
        new_w = int(hero.width * h_ratio)
        new_h = target_h
        hero_resized = hero.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        pos_x = W - new_w - (35 if is_ogp else 50)
        pos_y = H - new_h - (15 if is_ogp else 60)

        # Soft contact shadow under desk
        shadow_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_layer)
        sdraw.ellipse(
            [pos_x + 30, pos_y + new_h - 25, pos_x + new_w - 30, pos_y + new_h + 15],
            fill=(100, 116, 139, 45)
        )
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(12))
        base = Image.alpha_composite(base, shadow_layer)
        draw = ImageDraw.Draw(base)

        base.paste(hero_resized, (pos_x, pos_y), hero_resized)

    # 5. Fonts
    font_badge = ImageFont.truetype(font_bold, 17)
    font_title = ImageFont.truetype(font_bold, 56 if is_ogp else 62)
    font_sub = ImageFont.truetype(font_bold, 21 if is_ogp else 24)
    font_desc = ImageFont.truetype(font_reg, 14 if is_ogp else 16)
    font_card_badge = ImageFont.truetype(font_bold, 15)
    font_card_lead = ImageFont.truetype(font_bold, 13)
    font_card_desc = ImageFont.truetype(font_reg, 12)
    font_author = ImageFont.truetype(font_bold, 17)
    font_url = ImageFont.truetype(font_reg, 15)

    # 6. Left Typography & Content Block
    bx = 65
    offset_y = 52 if is_ogp else 110

    # 6.1 Category Pill Badge
    badge_label = "外国人視点の日本語学習ノート"
    bbox_b = draw.textbbox((0, 0), badge_label, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    
    pad_x, pad_y = 18, 7
    badge_rect = [bx, offset_y, bx + bw + pad_x * 2, offset_y + bh + pad_y * 2]
    draw.rounded_rectangle(
        badge_rect,
        radius=14,
        fill=(79, 70, 229, 235), # modern indigo
        outline=(99, 102, 241, 120),
        width=1
    )
    draw.text((bx + pad_x, offset_y + pad_y - 2), badge_label, font=font_badge, fill=(255, 255, 255, 255))

    # 6.2 Main Title
    title_y = offset_y + bh + pad_y * 2 + 18
    # Subtle soft shadow behind title
    draw.text((bx + 2, title_y + 2), "オスカーの日本語学習帳", font=font_title, fill=(195, 190, 220, 130))
    draw.text((bx, title_y), "オスカーの日本語学習帳", font=font_title, fill=(15, 23, 42, 255))

    # Cute 3-color underline under title (Indigo, Coral Rose, Amber)
    underline_y = title_y + (72 if is_ogp else 82)
    draw.rounded_rectangle([bx, underline_y, bx + 190, underline_y + 6], radius=3, fill=(99, 102, 241, 255))
    draw.rounded_rectangle([bx + 200, underline_y, bx + 255, underline_y + 6], radius=3, fill=(244, 63, 94, 255))
    draw.rounded_rectangle([bx + 265, underline_y, bx + 295, underline_y + 6], radius=3, fill=(245, 158, 11, 255))

    # 6.3 Catchphrase / Subtitle
    sub_y = underline_y + 20
    draw.text((bx, sub_y), "「ことばのあや」や文化の違い、日常のカルチャーショック！", font=font_sub, fill=(30, 41, 59, 255))
    draw.text((bx, sub_y + (30 if is_ogp else 36)), "香港出身Webディレクターが外国人視点から分かりやすくお届けします。", font=font_desc, fill=(100, 116, 139, 255))

    # 6.4 Three Category Feature Cards
    cards_y = sub_y + (68 if is_ogp else 85)
    cards_info = [
        {
            "tag": "くらべてみました",
            "lead": "言葉の違いを徹底比較",
            "desc": "「さようなら」VS「またね」\n「知る」VS「わかる」など",
            "border": (14, 165, 233, 160),
            "bg": (240, 249, 255, 245),
            "tag_bg": (14, 165, 233, 235),
            "icon_char": "VS"
        },
        {
            "tag": "ことばのあや",
            "lead": "助詞・ニュアンス解説",
            "desc": "「いいです」の真意や\n終助詞「よね」の距離感",
            "border": (139, 92, 246, 160),
            "bg": (245, 243, 255, 245),
            "tag_bg": (124, 58, 237, 235),
            "icon_char": "文"
        },
        {
            "tag": "カルチャーショック",
            "lead": "日本と海外の習慣",
            "desc": "散髪代やチップ、主食文化\n日常で驚いた発見の数々",
            "border": (245, 158, 11, 160),
            "bg": (255, 251, 235, 245),
            "tag_bg": (217, 119, 6, 235),
            "icon_char": "驚"
        }
    ]

    card_w = 205
    card_h = 104 if is_ogp else 114
    gap = 14
    for i, c in enumerate(cards_info):
        cx = bx + i * (card_w + gap)
        # Card outline & background
        draw.rounded_rectangle(
            [cx, cards_y, cx + card_w, cards_y + card_h],
            radius=12,
            fill=c["bg"],
            outline=c["border"],
            width=2
        )
        
        # Tag Badge auto-width calculation
        bbox_tag = draw.textbbox((0, 0), c["tag"], font=font_card_badge)
        tw = bbox_tag[2] - bbox_tag[0]
        th = bbox_tag[3] - bbox_tag[1]
        
        # Little icon pill
        icon_box_w = 24
        draw.rounded_rectangle(
            [cx + 10, cards_y + 10, cx + 10 + tw + 22, cards_y + 10 + th + 10],
            radius=6,
            fill=c["tag_bg"]
        )
        draw.text((cx + 18, cards_y + 13), c["tag"], font=font_card_badge, fill=(255, 255, 255, 255))
        
        # Lead
        draw.text((cx + 12, cards_y + 45), c["lead"], font=font_card_lead, fill=(30, 41, 59, 255))
        
        # Desc lines
        d_lines = c["desc"].split('\n')
        draw.text((cx + 12, cards_y + 65), d_lines[0], font=font_card_desc, fill=(100, 116, 139, 255))
        if len(d_lines) > 1:
            draw.text((cx + 12, cards_y + 82), d_lines[1], font=font_card_desc, fill=(100, 116, 139, 255))

    # 6.5 Author & Site Branding Bar (Bottom Left)
    auth_y = cards_y + card_h + (25 if is_ogp else 40)
    avatar_path = 'assets/images/my-icon.png'
    if os.path.exists(avatar_path):
        av = Image.open(avatar_path).convert('RGBA')
        av_size = 54
        av_resized = av.resize((av_size, av_size), Image.Resampling.LANCZOS)
        
        # Circular mask
        mask = Image.new('L', (av_size, av_size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0, 0, av_size, av_size), fill=255)
        
        # Avatar border & shadow
        draw.ellipse([bx - 2, auth_y - 2, bx + av_size + 2, auth_y + av_size + 2], fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
        base.paste(av_resized, (bx, auth_y), mask)
        
        text_start_x = bx + av_size + 14
        draw.text((text_start_x, auth_y + 4), "オスカー", font=font_author, fill=(15, 23, 42, 255))
        draw.text((text_start_x, auth_y + 28), "Site: https://nihongo.oscarchair.jp", font=font_url, fill=(79, 70, 229, 255))

    return base

if __name__ == '__main__':
    create_ogp_images()
