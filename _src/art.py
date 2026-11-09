"""Generated editorial graphics for aibriefing.io (no licensed photos; everything is drawn at build time)."""
import os, re, hashlib, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/truetype/google-fonts"
def font(name, size):
    for p in (os.path.join(FONT_DIR, name), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(p, size)
        except Exception: continue
    return ImageFont.load_default()
SERIF = "Lora-Variable.ttf"; SANS = "Poppins-Medium.ttf"; SANSB = "Poppins-Bold.ttf"; SANSR = "Poppins-Regular.ttf"

PALETTES = {  # (bg1, bg2, accent)
    "funding": ((6, 46, 40), (10, 92, 72), (120, 230, 190)),
    "IPO": ((6, 46, 40), (14, 84, 92), (120, 230, 210)),
    "M&A": ((20, 40, 70), (12, 78, 110), (130, 200, 255)),
    "models": ((28, 22, 70), (60, 40, 140), (170, 150, 255)),
    "pricing": ((40, 26, 70), (90, 40, 120), (230, 160, 255)),
    "security": ((70, 18, 18), (140, 40, 30), (255, 150, 120)),
    "policy": ((60, 40, 10), (120, 80, 20), (255, 200, 110)),
    "infrastructure": ((40, 36, 24), (96, 78, 40), (240, 210, 140)),
    "adoption": ((14, 34, 64), (20, 70, 130), (140, 190, 255)),
    "data": ((14, 34, 64), (20, 70, 130), (140, 190, 255)),
    "agents": ((40, 20, 60), (90, 40, 130), (220, 160, 255)),
    "consumer": ((20, 40, 50), (30, 90, 110), (150, 220, 240)),
    "geopolitics": ((50, 30, 20), (110, 60, 30), (255, 190, 140)),
    "research": ((20, 40, 44), (30, 90, 100), (150, 230, 230)),
    "regulation": ((60, 40, 10), (120, 80, 20), (255, 200, 110)),
    "default": ((20, 19, 17), (50, 46, 40), (122, 147, 255)),
}
VENDOR_TAGS = {"OpenAI", "Anthropic", "Google", "Nvidia", "Meta", "Microsoft", "Amazon", "Apple", "xAI", "Mistral", "DeepSeek"}

def palette(tags):
    for t in tags:
        if t in PALETTES: return PALETTES[t]
    return PALETTES["default"]

_STAT = re.compile(r"(\$\s?\d[\d.,]*\s?(?:trillion|billion|million|bn|m|k)?(?:\s?/\s?\$\s?\d[\d.,]*)?|\d[\d.,]*\s?%|\d+\+|\b(?:[A-Z][a-z]+ \d{1,2})\b|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\s?(?:trillion|billion|million)\b)")
def key_stat(text):
    m = _STAT.search(text)
    if not m: return None
    s = m.group(0).strip()
    s = re.sub(r"\s?trillion\b", "T", s); s = re.sub(r"\s?billion\b", "B", s); s = re.sub(r"\s?million\b", "M", s)
    s = s.replace("$ ", "$").replace(" / ", "/")
    return s if len(s) <= 12 else None

def _wrap(d, text, f, maxw):
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def _bg(W, H, pal, seed):
    bg1, bg2, acc = pal
    img = Image.new("RGB", (W, H), bg1)
    grad = Image.new("RGB", (W, H), bg1); gd = ImageDraw.Draw(grad)
    for i in range(H):
        t = i / H
        gd.line([(0, i), (W, i)], fill=tuple(int(bg1[k] * (1 - t) + bg2[k] * t) for k in range(3)))
    img = grad
    # seeded geometry: a few translucent circles and a dot grid
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(3):
        r = int(W * (0.18 + ((h >> (i * 7)) % 100) / 400)); cx = int(W * (0.55 + ((h >> (i * 5 + 3)) % 100) / 250)); cy = int(H * (0.1 + ((h >> (i * 9 + 1)) % 100) / 120))
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acc + (22 + i * 10,))
    step = 36
    for x in range(W - 380, W, step):
        for y in range(40, H - 40, step):
            if ((x // step + y // step + h) % 3) == 0: od.ellipse([x, y, x + 4, y + 4], fill=acc + (90,))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    return img

def story_card(out_path, title, tags, date_label, source_name, stat=None, W=1200, H=675):
    pal = palette(tags); acc = pal[2]
    img = _bg(W, H, pal, title); d = ImageDraw.Draw(img)
    pad = 64
    # top row: brand + category
    d.text((pad, 44), "AI BRIEFING", font=font(SANSB, 22), fill=(255, 255, 255))
    cat = next((t for t in tags if t not in VENDOR_TAGS), tags[0] if tags else "AI").upper()
    cf = font(SANSB, 20); cw = d.textlength(cat, font=cf) + 28
    d.rounded_rectangle([W - pad - cw, 38, W - pad, 72], radius=17, fill=acc)
    d.text((W - pad - cw + 14, 44), cat, font=cf, fill=pal[0])
    # stat or category word
    y = 120
    if stat:
        sf = font(SANSB, 150 if len(stat) <= 6 else 110)
        d.text((pad - 4, y), stat, font=sf, fill=acc); y += (170 if len(stat) <= 6 else 130)
    else:
        sf = font(SERIF, 120); d.text((pad, y), cat.title(), font=sf, fill=acc); y += 140
    # title
    tf = font(SERIF, 54)
    try: tf.set_variation_by_axes([650])
    except Exception: pass
    lines = _wrap(d, title, tf, W - 2 * pad)[:4]
    for ln in lines:
        d.text((pad, y), ln, font=tf, fill=(255, 255, 255)); y += 64
    # footer
    d.line([(pad, H - 70), (W - pad, H - 70)], fill=acc, width=2)
    d.text((pad, H - 56), f"{date_label}  ·  Source: {source_name}", font=font(SANSR, 22), fill=(230, 226, 218))
    img.save(out_path, quality=84, method=4)

def brief_og(out_path, headline, date_label, n_items):
    pal = PALETTES["default"]; img = _bg(1200, 630, pal, headline); d = ImageDraw.Draw(img); pad = 72
    d.text((pad, 52), "AI BRIEFING", font=font(SANSB, 24), fill=(255, 255, 255))
    d.text((pad, 92), f"{date_label}  ·  {n_items} stories  ·  4 minutes", font=font(SANSR, 22), fill=(200, 194, 181))
    tf = font(SERIF, 64)
    try: tf.set_variation_by_axes([650])
    except Exception: pass
    y = 170
    for ln in _wrap(d, headline, tf, 1200 - 2 * pad)[:4]:
        d.text((pad, y), ln, font=tf, fill=(255, 255, 255)); y += 76
    d.rectangle([pad, 630 - 92, 1200 - pad, 630 - 88], fill=pal[2])
    d.text((pad, 630 - 72), "aibriefing.io  ·  daily AI news, explained for your job", font=font(SANS, 24), fill=(250, 248, 244))
    img.save(out_path, optimize=True)

def explainer_cover(out_path, title, level, W=1200, H=675):
    pal = PALETTES["adoption"] if level == "beginner" else PALETTES["models"]
    img = _bg(W, H, pal, title); d = ImageDraw.Draw(img); pad = 64
    d.text((pad, 44), "AI BRIEFING  ·  LEARN", font=font(SANSB, 22), fill=(255, 255, 255))
    tf = font(SERIF, 66)
    try: tf.set_variation_by_axes([650])
    except Exception: pass
    y = 170
    for ln in _wrap(d, title, tf, W - 2 * pad)[:4]:
        d.text((pad, y), ln, font=tf, fill=(255, 255, 255)); y += 78
    d.text((pad, H - 56), f"Explainer  ·  {level}", font=font(SANSR, 22), fill=(230, 226, 218))
    img.save(out_path, quality=84, method=4)

def hub_cover(out_path, name, who, key, W=1200, H=675):
    pals = {"executives": "funding", "finance": "IPO", "security": "security", "ml": "models", "developers": "agents", "beginners": "adoption"}
    pal = PALETTES[pals.get(key, "default")]; img = _bg(W, H, pal, name); d = ImageDraw.Draw(img); pad = 64
    d.text((pad, 44), "AI BRIEFING  ·  FOR", font=font(SANSB, 22), fill=(255, 255, 255))
    tf = font(SERIF, 120)
    try: tf.set_variation_by_axes([700])
    except Exception: pass
    d.text((pad, 200), name, font=tf, fill=(255, 255, 255))
    d.text((pad, 360), who, font=font(SANSR, 34), fill=pal[2])
    img.save(out_path, quality=84, method=4)
