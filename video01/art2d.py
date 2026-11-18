"""2D shots from the Google Flow art: panel crops, background removal, Ken Burns, blinks, lip flaps."""
import os, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)); ART = os.path.join(D, "art", "flow")
W, H = 1920, 1080
# panel boxes on the 1376x768 sheets: (sheet, cx, cy, half_w, half_h)
PANELS = {
    "mom_smile": ("02_mom_faces", 222, 200, 150, 170), "mom_blink": ("02_mom_faces", 537, 200, 150, 170),
    "mom_stare": ("02_mom_faces", 846, 200, 150, 170), "mom_stare2": ("02_mom_faces", 1161, 200, 150, 170),
    "mom_tears": ("02_mom_faces", 222, 560, 150, 170), "mom_talk": ("02_mom_faces", 537, 560, 150, 170),
    "mom_relief": ("02_mom_faces", 846, 560, 150, 170),
    "dad_blink": ("03_dad_faces", 552, 152, 140, 150), "dad_midword": ("03_dad_faces", 860, 152, 140, 150),
    "dad_stare": ("03_dad_faces", 1168, 152, 140, 150), "dad_tear": ("03_dad_faces", 552, 490, 140, 150),
    "dad_talk": ("03_dad_faces", 860, 490, 140, 150), "dad_laugh": ("03_dad_faces", 1168, 490, 140, 150),
    "sis_grin": ("04_sister_faces", 200, 300, 95, 130), "sis_blink": ("04_sister_faces", 430, 300, 95, 130),
    "sis_stare": ("04_sister_faces", 630, 300, 88, 130), "sis_tear": ("04_sister_faces", 774, 300, 88, 130),
    "sis_laugh": ("04_sister_faces", 946, 300, 95, 130), "sis_contest": ("04_sister_faces", 1168, 300, 95, 130),
    "you_neutral": ("05_you_faces", 225, 190, 130, 150), "you_blink": ("05_you_faces", 560, 140, 120, 140),
    "you_chew": ("05_you_faces", 560, 520, 120, 140), "you_scared": ("05_you_faces", 1160, 160, 130, 150),
    "you_speak": ("05_you_faces", 1180, 520, 130, 150),
}
_cache = {}
def sheet(name):
    if name not in _cache: _cache[name] = Image.open(os.path.join(ART, name + ".jpg")).convert("RGB")
    return _cache[name]

def panel(key, cut=True):
    s, cx, cy, hw, hh = PANELS[key]
    im = sheet(s).crop((cx - hw, cy - hh, cx + hw, cy + hh)).convert("RGBA")
    if cut:  # remove the flat light-grey sheet background by flood fill from the borders
        mask = Image.new("L", im.size, 255); rgb = im.convert("RGB")
        for seed in [(0, 0), (im.width - 1, 0), (0, im.height // 2), (im.width - 1, im.height // 2), (im.width // 2, 0)]:
            ImageDraw.floodfill(rgb, seed, (255, 0, 255), thresh=28)
        px = rgb.load(); m = mask.load()
        for y in range(im.height):
            for x in range(im.width):
                if px[x, y] == (255, 0, 255): m[x, y] = 0
        mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
        im.putalpha(mask)
    return im

def backdrop(kind="warm"):
    """Blurred, darkened dining-room plate from the key art, tinted by mood."""
    bg = sheet("06_keyframe_frozen_dinner").resize((W, H)).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.55 if kind == "warm" else 0.35)
    if kind == "frozen":
        g = Image.new("RGB", (W, H), (60, 110, 20)); bg = Image.blend(bg, g, 0.25)
    return bg

def kenburns(img, n, path, z0=1.0, z1=1.08, focus=(0.5, 0.5), start=0, overlay=None):
    """Write n frames of a slow push from z0 to z1 toward focus (fractions of the image)."""
    iw, ih = img.size
    for f in range(n):
        t = f / max(1, n - 1); z = z0 + (z1 - z0) * (t * t * (3 - 2 * t))
        cw, ch = iw / z, ih / z
        cx = min(max(focus[0] * iw, cw / 2), iw - cw / 2); cy = min(max(focus[1] * ih, ch / 2), ih - ch / 2)
        fr = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)
        if overlay: fr = overlay(fr, f)
        fr.save(f"{path}/{start + f:04d}.png")

def face_shot(keys, n, path, mood="warm", scale=0.95, z=(1.0, 1.07), focus=(0.5, 0.45), swap=None):
    """Character close-up: cutout panel over a blurred set plate. keys[0] is the base face;
    swap(f) may return another panel key for frame f (blinks, lip flaps)."""
    bg = backdrop(mood); faces = {}
    def frame_img(k):
        if k not in faces:
            p = panel(k); s = scale * H / p.height; p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
            c = bg.copy(); c.paste(p, ((W - p.width) // 2, H - p.height), p); faces[k] = c
        return faces[k]
    for f in range(n):
        k = (swap(f) if swap else None) or keys[0]
        t = f / max(1, n - 1); zz = z[0] + (z[1] - z[0]) * (t * t * (3 - 2 * t))
        img = frame_img(k); cw, ch = W / zz, H / zz
        cx, cy = focus[0] * W, focus[1] * H
        cx = min(max(cx, cw / 2), W - cw / 2); cy = min(max(cy, ch / 2), H - ch / 2)
        img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS).save(f"{path}/{f:04d}.png")

if __name__ == "__main__":
    import sys
    out = sys.argv[1]; ims = [panel(k, cut=False).convert("RGB").resize((200, 220)) for k in PANELS]
    cols = 8; rows = math.ceil(len(ims) / cols); sheet_im = Image.new("RGB", (cols * 200, rows * 240), (40, 40, 40))
    d = ImageDraw.Draw(sheet_im)
    for i, (k, im) in enumerate(zip(PANELS, ims)):
        x, y = (i % cols) * 200, (i // cols) * 240; sheet_im.paste(im, (x, y)); d.text((x + 4, y + 222), k, fill=(255, 255, 0))
    sheet_im.save(out)


# ---------------- shot recipes used by comp_test.py ----------------
def _blur_box(im, box, r=14):
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(r)); im.paste(reg, box); return im

def dad_tv_plate():
    im = sheet("08_dad_tv").copy()
    return _blur_box(im, (895, 40, 1255, 270)).resize((W, H), Image.LANCZOS)  # hide garbled TV text

def tv_flicker(fr, f):
    k = 0.92 + 0.10 * math.sin(f * 1.7) + (0.08 if f % 11 == 0 else 0)
    return ImageEnhance.Brightness(fr).enhance(k)

def split_contest(n, path, z=(1.0, 1.04)):
    left = panel("sis_contest"); right = panel("you_neutral"); bg = backdrop("warm")
    canvas = bg.copy()
    for im, x0 in ((left, 0), (right, W // 2)):
        s = 1.0 * H / im.height; im2 = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        canvas.paste(im2, (x0 + (W // 2 - im2.width) // 2, H - im2.height), im2)
    ImageDraw.Draw(canvas).rectangle([W // 2 - 4, 0, W // 2 + 4, H], fill=(182, 255, 59))
    kenburns(canvas, n, path, z[0], z[1])

def recipe(setup, motion, n, path):
    """Return True if this set-up is produced from the 2D art."""
    micro = motion.startswith("micro-change")
    if setup == "ECU_MOM_EYES":
        face_shot(["mom_stare"], n, path, mood="frozen", scale=1.7, z=(1.25, 1.4) if micro else (1.0, 1.25), focus=(0.5, 0.36))
    elif setup == "WIDE_TABLE_POV":
        kenburns(sheet("06_keyframe_frozen_dinner").resize((W, H), Image.LANCZOS), n, path,
                 *((1.12, 1.18) if micro else (1.0, 1.1)), focus=(0.55, 0.45))
    elif setup == "CU_YOU_MOUTH":
        face_shot(["you_scared"], n, path, mood="frozen", scale=1.5, focus=(0.5, 0.5),
                  swap=lambda f: "you_speak" if f < n * 0.45 else None)
    elif setup == "LIVING_TV_DAD":
        kenburns(dad_tv_plate(), n, path, 1.0, 1.08, focus=(0.45, 0.55), overlay=tv_flicker)
    elif setup == "ECU_DAD_TV_REFLECT":
        kenburns(dad_tv_plate(), n, path, *((1.9, 2.0) if micro else (1.6, 1.8)), focus=(0.34, 0.33), overlay=tv_flicker)
    elif setup == "SIS_STARE_CONTEST":
        split_contest(n, path, (1.08, 1.12) if micro else (1.0, 1.05))
    elif setup == "SIS_LAUGH":
        face_shot(["sis_laugh"], n, path, mood="warm", scale=1.0, z=(1.1, 1.18) if micro else (1.0, 1.1),
                  swap=lambda f: "sis_grin" if (f // 5) % 3 == 2 else None)
    elif setup == "EXT_HOUSE_NIGHT":
        kenburns(sheet("07_ext_house_night").resize((W, H), Image.LANCZOS), n, path, 1.0, 1.14, focus=(0.3, 0.62))
    elif setup == "CU_MOM_SMILE":
        face_shot(["mom_smile"], n, path, mood="warm", scale=1.05, z=(1.08, 1.14) if micro else (1.0, 1.07),
                  swap=lambda f: "mom_blink" if 9 <= f <= 11 else ("mom_talk" if (f // 4) % 2 and f > 13 else None))
    elif setup == "CU_DAD_TALK":
        face_shot(["dad_talk"], n, path, mood="warm", scale=1.05, z=(1.0, 1.08),
                  swap=lambda f: "dad_stare" if (f // 3) % 2 else None)
    else:
        return False
    return True
