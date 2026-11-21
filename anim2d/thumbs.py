"""Thumbnails in the owner's house style: black background, white + huge yellow command,
yellow line-art victim, white line-art threat from the right. Usage: python3 thumbs.py video02"""
import math, os, sys
import skia
from engine import C, Pen, font, FONTS, W, H, music_note

YEL, BLK, WHT = "#FFE000", "#000000", "#FFFFFF"
OUT = 12  # outline weight

def heavy(pen, text, x, y, size, color, stroke=0):
    f = font("ArchivoBlack-Regular.ttf", size)
    if stroke:
        p = skia.Paint(AntiAlias=True, Color4f=C(BLK)); p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeJoin(skia.Paint.kRound_Join)
        pen.c.drawString(text, x, y, f, p)
    pen.c.drawString(text, x, y, f, skia.Paint(AntiAlias=True, Color4f=C(color)))
    return f.measureText(text)

def fill_line(pen, build, fill, w=OUT):
    pen.path(build, fill=fill); pen.path(build, stroke=BLK, w=w)

def video02(pen):
    c = pen.c
    c.clear(C(BLK))
    # ---- text (top-left): DON'T CALL / HIM ----
    heavy(pen, "DON'T CALL", 50, 205, 168, WHT)
    heavy(pen, "HIM", 46, 520, 360, YEL)
    # ---- threat: doorway on the right + tall white thing leaning out ----
    pen.rect(1430, 60, 470, 1100, stroke=WHT, w=14)
    pen.poly([(1900, 60), (1990, 20), (1990, 1100), (1900, 1060)], stroke=WHT, w=12)  # door swung open
    body = lambda p: (p.moveTo(1520, 1100), p.cubicTo(1500, 760, 1470, 560, 1500, 470), p.cubicTo(1560, 420, 1700, 430, 1760, 480),
                      p.cubicTo(1800, 650, 1790, 900, 1800, 1100), p.close())
    pen.path(body, stroke=WHT, w=12)
    # long arm reaching left to just above the victim's shoulder, with long bony fingers
    arm = lambda p: (p.moveTo(1500, 500), p.cubicTo(1380, 520, 1240, 560, 1110, 600))
    pen.path(arm, stroke=WHT, w=34); pen.path(arm, stroke=BLK, w=14)
    pen.circle(1095, 605, 34, fill=WHT)
    for k in range(5):
        a = math.radians(160 + k * 13); L = 150 - abs(k - 2) * 18
        x1, y1 = 1095 + math.cos(a) * L * 0.55, 605 + math.sin(a) * L * 0.55
        x2, y2 = 1095 + math.cos(a + 0.35) * L, 605 + math.sin(a + 0.35) * L + 40
        pen.ln(1095, 605, x1, y1, WHT, 12); pen.ln(x1, y1, x2, y2, WHT, 9)
    # head: skull-like, tilted, huge grin
    hx, hy = 1610, 300
    pen.push(rot=-14, ox=hx, oy=hy)
    pen.oval(hx, hy, 150, 175, fill=WHT, stroke=WHT, w=4)
    for sx in (-1, 1):
        ex = hx + sx * 62
        pen.oval(ex, hy - 20, 52, 58, fill=BLK)
        pen.circle(ex, hy - 18, 34, fill=YEL); pen.circle(ex, hy - 18, 13, fill=BLK)
    pen.path(lambda p: (p.moveTo(hx - 140, hy + 30), p.quadTo(hx, hy + 230, hx + 145, hy + 20), p.quadTo(hx, hy + 110, hx - 140, hy + 30), p.close()), fill=BLK)
    for k in range(13):  # upper and lower teeth
        tx = hx - 125 + k * 21; top = hy + 52 + abs(k - 6) * -3 + (abs(k - 6) ** 2) * 1.2
        pen.poly([(tx, top), (tx + 10, top + 34), (tx + 20, top)], fill=WHT)
        bot = hy + 150 - abs(k - 6) * 6
        if 2 <= k <= 10: pen.poly([(tx, bot), (tx + 10, bot - 30), (tx + 20, bot)], fill=WHT)
    pen.pop()
    # ---- victim: you, yellow line art, cupped hands calling, eyes squeezed ----
    vx, vy, r = 760, 760, 200
    fill_line(pen, lambda p: (p.moveTo(vx - 330, 1090), p.cubicTo(vx - 300, 900, vx + 300, 900, vx + 330, 1090), p.close()), YEL)  # hoodie shoulders
    fill_line(pen, lambda p: p.addRect(skia.Rect.MakeXYWH(vx - 60, vy + 150, 120, 90)), YEL)  # neck
    for k in range(13):  # curly hair
        a = math.radians(200 + k * 11.5); pen.circle(vx + math.cos(a) * r * 0.95, vy + math.sin(a) * r * 0.95, 46, fill=YEL, stroke=BLK, w=OUT)
    for sx in (-1, 1): fill_line(pen, lambda p, sx=sx: p.addOval(skia.Rect.MakeXYWH(vx + sx * r - 34 - (0 if sx < 0 else 0), vy - 30, 68, 90)), YEL)  # ears
    fill_line(pen, lambda p: p.addCircle(vx, vy, r), YEL)
    for sx in (-1, 1):  # squeezed eyes (> <) and worried brows
        ex = vx + sx * 72
        pen.path(lambda p, ex=ex, sx=sx: (p.moveTo(ex - sx * 40, vy - 40), p.lineTo(ex + sx * 8, vy - 18), p.lineTo(ex - sx * 40, vy + 4)), stroke=BLK, w=13)
        pen.ln(ex - sx * 50, vy - 90, ex + sx * 30, vy - 74, BLK, 12)
    # hands cupped at the open mouth (calling)
    pen.oval(vx, vy + 105, 70, 46, fill=BLK)
    for sx in (-1, 1):
        pen.push(rot=sx * -28, ox=vx + sx * 70, oy=vy + 110)
        fill_line(pen, lambda p, sx=sx: p.addRoundRect(skia.Rect.MakeXYWH(vx + sx * 70 - 42, vy + 40, 84, 150), 42, 42), YEL)
        for j in range(3): pen.ln(vx + sx * 70 - 30, vy + 70 + j * 32, vx + sx * 70 + 30, vy + 70 + j * 32, BLK, 6)
        pen.pop()
    # alert ticks near the head
    for k, (a, L) in enumerate(((-60, 70), (-35, 80), (-10, 64))):
        ang = math.radians(a); x0, y0 = vx + 250 + k * 6, vy - 230
        pen.poly([(x0, y0), (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L), (x0 + math.cos(ang) * L + 12, y0 + math.sin(ang) * L + 10)], fill=WHT)
    # Bruno, small, out in the dark yard, looking back (real dog drawing, yellow)
    from engine import MOOD, dog
    MOOD["thumb"] = dict(white=YEL, line=BLK); pen.mood = "thumb"
    dog(pen, 250, 1060, 1.05, 0.4, facing=1, head_turn=0.7, tail=-1, ears=0.5)
    pen.mood = "normal"


def video03(pen):
    c = pen.c; c.clear(C(BLK))
    heavy(pen, "DON'T BUY", 50, 190, 150, WHT)
    heavy(pen, "ANYTHING", 40, 420, 205, YEL)
    # threat: the truck (white line art) on the right, dark serving window with a grinning face, long arm with a cone
    pen.rect(1250, 470, 700, 520, stroke=WHT, w=12, r=20)
    pen.rect(1300, 540, 380, 260, fill=BLK, stroke=WHT, w=10)
    for x in (1350, 1820): pen.circle(x, 1010, 70, stroke=WHT, w=12)
    pen.poly([(1500, 470), (1530, 400), (1600, 380), (1600, 470)], stroke=WHT, w=8)
    for k in range(3): music_note(pen, 1620 + k * 70, 360 - k * 30, 1.0, WHT)
    fx, fy = 1490, 650  # face in the window
    pen.oval(fx, fy, 120, 95, fill=WHT)
    for sx in (-1, 1):
        pen.oval(fx + sx * 50, fy - 20, 34, 36, fill=BLK); pen.circle(fx + sx * 50, fy - 18, 22, fill=YEL); pen.circle(fx + sx * 50, fy - 18, 8, fill=BLK)
    pen.path(lambda p: (p.moveTo(fx - 100, fy + 20), p.quadTo(fx, fy + 140, fx + 100, fy + 15), p.quadTo(fx, fy + 70, fx - 100, fy + 20), p.close()), fill=BLK)
    for k in range(10):
        tx = fx - 88 + k * 18; pen.poly([(tx, fy + 35), (tx + 8, fy + 62), (tx + 16, fy + 35)], fill=WHT)
    arm = lambda p: (p.moveTo(1310, 740), p.cubicTo(1200, 760, 1100, 700, 980, 640))
    pen.path(arm, stroke=WHT, w=30); pen.path(arm, stroke=BLK, w=12)
    for k in range(4): pen.ln(980, 640, 930, 600 + k * 22, WHT, 9)
    pen.poly([(900, 600), (960, 600), (930, 720)], fill=YEL, stroke=BLK, w=8); pen.circle(930, 575, 42, fill=WHT, stroke=BLK, w=6)
    # victim: you in yellow pyjamas, reaching for the cone, eyes wide
    vx, vy, r = 520, 700, 170
    fill_line(pen, lambda p: (p.moveTo(vx - 290, 1090), p.cubicTo(vx - 260, 920, vx + 260, 920, vx + 290, 1090), p.close()), YEL)
    fill_line(pen, lambda p: p.addRect(skia.Rect.MakeXYWH(vx - 50, vy + 120, 100, 110)), YEL)
    for k in range(13):
        a = math.radians(200 + k * 11.5); pen.circle(vx + math.cos(a) * r * 0.95, vy + math.sin(a) * r * 0.95, 40, fill=YEL, stroke=BLK, w=OUT)
    fill_line(pen, lambda p: p.addCircle(vx, vy, r), YEL)
    for sx in (-1, 1):
        pen.circle(vx + sx * 62, vy - 10, 38, fill=WHT, stroke=BLK, w=8); pen.circle(vx + sx * 62 + 14, vy - 10, 16, fill=BLK)
        pen.ln(vx + sx * 30, vy - 80, vx + sx * 100, vy - 66, BLK, 10)
    pen.oval(vx, vy + 85, 40, 30, fill=BLK)
    arm2 = lambda p: (p.moveTo(vx + 200, 980), p.cubicTo(vx + 330, 880, vx + 340, 760, 860, 690))
    pen.path(arm2, stroke=BLK, w=62); pen.path(arm2, stroke=YEL, w=46)
    fill_line(pen, lambda p: p.addCircle(870, 690, 34), YEL)
    for k, (a, L) in enumerate(((-60, 70), (-35, 80), (-10, 64))):
        ang = math.radians(a); x0, y0 = vx + 210 + k * 6, vy - 200
        pen.poly([(x0, y0), (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L), (x0 + math.cos(ang) * L + 12, y0 + math.sin(ang) * L + 10)], fill=WHT)

THUMBS = {"video02": video02, "video03": video03}


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "video02"
    surf = skia.Surface(W, H); pen = Pen(surf.getCanvas()); THUMBS[name](pen)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name)
    img = surf.makeImageSnapshot(); big = os.path.join(out_dir, "thumbnail_1920.png"); img.save(big, skia.kPNG)
    os.system(f"ffmpeg -v error -y -i {big} -vf scale=1280:720 -q:v 2 {os.path.join(out_dir, 'thumbnail.jpg')}")
    print("wrote", big, "and thumbnail.jpg")
