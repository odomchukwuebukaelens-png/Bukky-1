"""Low-poly people, armies and vehicles in period dress.

Everything is built from simple boxes so thousands of figures stay cheap to
render. Each group of figures is one mesh with a "stride" shape key, so the
legs swing while the group walks or marches along a path.

Costumes are chosen per era: see COSTUMES.
"""
import math
import random

import bpy
from mathutils import Vector

# (tunic/body colours, legs, robe?, headgear, shield, weapon, cloak)
SKIN = [(0.78, 0.56, 0.42), (0.62, 0.42, 0.30), (0.45, 0.30, 0.20), (0.86, 0.66, 0.52)]
COSTUMES = {
    # early Latins and ordinary Romans
    "latin": {"body": [(0.48, 0.38, 0.26), (0.55, 0.47, 0.34), (0.40, 0.30, 0.22)], "robe": True},
    "roman": {"body": [(0.92, 0.90, 0.84), (0.78, 0.62, 0.36), (0.62, 0.30, 0.20), (0.50, 0.42, 0.30),
                       (0.85, 0.80, 0.70)], "robe": True},
    "senator": {"body": [(0.97, 0.96, 0.92)], "robe": True, "stripe": (0.45, 0.08, 0.25)},
    "legionary": {"body": [(0.62, 0.08, 0.06)], "legs": (0.55, 0.40, 0.28), "helmet": (0.72, 0.62, 0.38),
                  "shield": (0.62, 0.08, 0.06), "shield_rim": (0.85, 0.70, 0.25), "weapon": "pilum",
                  "armour": (0.55, 0.55, 0.58)},
    "gaul": {"body": [(0.25, 0.42, 0.22), (0.30, 0.35, 0.55), (0.55, 0.40, 0.20)], "legs": (0.35, 0.28, 0.20),
             "shield": (0.30, 0.45, 0.25), "round": True, "weapon": "spear"},
    "goth": {"body": [(0.40, 0.30, 0.22), (0.30, 0.26, 0.22), (0.45, 0.36, 0.26)], "legs": (0.25, 0.22, 0.18),
             "shield": (0.40, 0.25, 0.15), "round": True, "weapon": "spear", "helmet": (0.45, 0.45, 0.48)},
    "medieval": {"body": [(0.30, 0.25, 0.20), (0.45, 0.20, 0.15), (0.25, 0.30, 0.40), (0.50, 0.45, 0.35)],
                 "robe": True, "hood": True},
    "monk": {"body": [(0.22, 0.16, 0.12), (0.10, 0.10, 0.10)], "robe": True, "hood": True},
    "landsknecht": {"body": [(0.75, 0.15, 0.12), (0.85, 0.75, 0.20), (0.20, 0.30, 0.60), (0.95, 0.95, 0.90)],
                    "legs": (0.85, 0.75, 0.20), "helmet": (0.62, 0.62, 0.66), "weapon": "pike"},
    "renaissance": {"body": [(0.45, 0.10, 0.12), (0.12, 0.20, 0.40), (0.20, 0.35, 0.20), (0.10, 0.10, 0.10)],
                    "legs": (0.12, 0.12, 0.14), "hat": (0.10, 0.10, 0.10)},
    "c19": {"body": [(0.10, 0.10, 0.12), (0.22, 0.20, 0.18), (0.30, 0.22, 0.16)], "legs": (0.15, 0.15, 0.16),
            "hat": (0.08, 0.08, 0.08), "dress": [(0.45, 0.15, 0.20), (0.20, 0.25, 0.45), (0.35, 0.30, 0.25)]},
    "bersaglieri": {"body": [(0.12, 0.16, 0.30)], "legs": (0.12, 0.16, 0.30), "hat": (0.05, 0.05, 0.05),
                    "plume": True, "weapon": "rifle"},
    "papal": {"body": [(0.45, 0.48, 0.50)], "legs": (0.45, 0.48, 0.50), "hat": (0.30, 0.32, 0.34),
              "weapon": "rifle"},
    "french1849": {"body": [(0.15, 0.20, 0.45)], "legs": (0.65, 0.10, 0.10), "hat": (0.60, 0.10, 0.10),
                   "weapon": "rifle"},
    "garibaldini": {"body": [(0.80, 0.10, 0.08)], "legs": (0.45, 0.45, 0.48), "hat": (0.10, 0.10, 0.10),
                    "weapon": "rifle"},
    "c1940": {"body": [(0.22, 0.22, 0.24), (0.35, 0.30, 0.25), (0.55, 0.50, 0.42)], "legs": (0.20, 0.20, 0.22),
              "hat": (0.18, 0.16, 0.14), "dress": [(0.50, 0.25, 0.20), (0.25, 0.35, 0.45)]},
    "modern": {"body": [(0.90, 0.20, 0.20), (0.15, 0.40, 0.75), (0.95, 0.95, 0.95), (0.10, 0.10, 0.10),
                        (0.95, 0.75, 0.20), (0.30, 0.60, 0.35)], "legs": (0.20, 0.25, 0.40),
               "dress": [(0.85, 0.30, 0.45), (0.95, 0.85, 0.70)]},
}


class Mesh:
    def __init__(self):
        self.v, self.f, self.c, self.swing = [], [], [], []

    def box(self, cx, cy, z0, hx, hy, h, col, swing=0.0, yaw=0.0, ox=0.0, oy=0.0):
        """Box centred on (cx, cy), rotated by yaw around the figure centre (ox, oy)."""
        ca, sa = math.cos(yaw), math.sin(yaw)
        base = len(self.v)
        for zz in (z0, z0 + h):
            for a, b in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
                lx, ly = cx - ox + a, cy - oy + b
                self.v.append((ox + lx * ca - ly * sa, oy + lx * sa + ly * ca, zz))
                # legs swing more at the feet than at the hips
                self.swing.append(swing * (1.0 if zz == z0 else 0.0))
        for f in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)):
            self.f.append(tuple(base + i for i in f))
            self.c.append(col)


def add_person(m, x, y, z, yaw, kind, rng, scale=1.0):
    c = COSTUMES[kind]
    s = scale
    skin = rng.choice(SKIN)
    body = rng.choice(c["body"])
    dressed = c.get("dress") and rng.random() < 0.45
    if dressed:
        body = rng.choice(c["dress"])
    legs = c.get("legs", body)
    robe = c.get("robe") or dressed
    if robe:
        m.box(x, y, z, 0.20 * s, 0.14 * s, 1.0 * s, body, yaw=yaw, ox=x, oy=y)
        m.box(x, y + 0.02, z + 0.02, 0.06 * s, 0.05 * s, 0.30 * s, legs if not robe else body, swing=0.18 * s,
              yaw=yaw, ox=x, oy=y)
    else:
        for side, sw in ((-1, 1.0), (1, -1.0)):
            m.box(x + side * 0.08 * s, y, z, 0.06 * s, 0.07 * s, 0.82 * s, legs, swing=sw * 0.28 * s,
                  yaw=yaw, ox=x, oy=y)
    m.box(x, y, z + 0.80 * s, 0.19 * s, 0.11 * s, 0.62 * s, c.get("armour", body) if c.get("armour") else body,
          yaw=yaw, ox=x, oy=y)
    if c.get("stripe"):
        m.box(x + 0.12 * s, y, z + 0.80 * s, 0.03 * s, 0.115 * s, 0.62 * s, c["stripe"], yaw=yaw, ox=x, oy=y)
    for side, sw in ((-1, -1.0), (1, 1.0)):
        m.box(x + side * 0.25 * s, y, z + 0.82 * s, 0.05 * s, 0.06 * s, 0.58 * s, body, swing=sw * 0.12 * s,
              yaw=yaw, ox=x, oy=y)
    m.box(x, y, z + 1.43 * s, 0.10 * s, 0.10 * s, 0.22 * s, skin, yaw=yaw, ox=x, oy=y)
    if c.get("helmet"):
        m.box(x, y, z + 1.60 * s, 0.12 * s, 0.12 * s, 0.10 * s, c["helmet"], yaw=yaw, ox=x, oy=y)
        if kind == "legionary":
            m.box(x, y, z + 1.70 * s, 0.02 * s, 0.10 * s, 0.08 * s, (0.65, 0.05, 0.05), yaw=yaw, ox=x, oy=y)
    elif c.get("hood"):
        m.box(x, y, z + 1.52 * s, 0.13 * s, 0.13 * s, 0.18 * s, body, yaw=yaw, ox=x, oy=y)
    elif c.get("hat") and not dressed:
        m.box(x, y, z + 1.64 * s, 0.15 * s, 0.15 * s, 0.03 * s, c["hat"], yaw=yaw, ox=x, oy=y)
        m.box(x, y, z + 1.66 * s, 0.09 * s, 0.09 * s, 0.14 * s if kind == "c19" else 0.06 * s, c["hat"],
              yaw=yaw, ox=x, oy=y)
        if c.get("plume"):
            m.box(x - 0.12 * s, y, z + 1.62 * s, 0.10 * s, 0.03 * s, 0.10 * s, (0.02, 0.06, 0.02), yaw=yaw, ox=x, oy=y)
    if c.get("shield"):
        if c.get("round"):
            m.box(x - 0.32 * s, y + 0.05, z + 0.75 * s, 0.03 * s, 0.30 * s, 0.60 * s, c["shield"], yaw=yaw, ox=x, oy=y)
        else:
            m.box(x - 0.32 * s, y + 0.05, z + 0.50 * s, 0.04 * s, 0.32 * s, 1.0 * s, c["shield"], yaw=yaw, ox=x, oy=y)
            m.box(x - 0.36 * s, y + 0.05, z + 0.95 * s, 0.01 * s, 0.09 * s, 0.10 * s, c.get("shield_rim", c["shield"]),
                  yaw=yaw, ox=x, oy=y)
    w = c.get("weapon")
    if w in ("spear", "pilum", "pike"):
        length = {"spear": 2.2, "pilum": 2.0, "pike": 4.5}[w]
        m.box(x + 0.30 * s, y, z + 0.4 * s, 0.025 * s, 0.025 * s, length * s, (0.40, 0.30, 0.18), yaw=yaw, ox=x, oy=y)
        m.box(x + 0.30 * s, y, z + (0.4 + length) * s, 0.04 * s, 0.04 * s, 0.25 * s, (0.75, 0.75, 0.78),
              yaw=yaw, ox=x, oy=y)
    elif w == "rifle":
        m.box(x + 0.28 * s, y, z + 0.9 * s, 0.025 * s, 0.025 * s, 1.1 * s, (0.15, 0.12, 0.10), yaw=yaw, ox=x, oy=y)


def add_horse(m, x, y, z, yaw, col=(0.36, 0.22, 0.12)):
    for dx in (-0.6, 0.6):
        for dy, sw in ((-0.18, 1.0), (0.18, -1.0)):
            m.box(x + dx, y + dy, z, 0.06, 0.06, 0.9, col, swing=sw * 0.3 * (1 if dx > 0 else -1), yaw=yaw, ox=x, oy=y)
    m.box(x, y, z + 0.9, 0.9, 0.25, 0.55, col, yaw=yaw, ox=x, oy=y)
    m.box(x + 1.0, y, z + 1.25, 0.25, 0.12, 0.55, col, yaw=yaw, ox=x, oy=y)
    m.box(x + 1.2, y, z + 1.55, 0.25, 0.10, 0.18, col, yaw=yaw, ox=x, oy=y)


def add_vehicle(m, x, y, z, yaw, kind, rng):
    if kind == "chariot":
        add_horse(m, x + 2.2, y, z, yaw)
        m.box(x, y, z + 0.4, 0.5, 0.55, 0.7, (0.55, 0.35, 0.15), yaw=yaw, ox=x, oy=y)
        m.box(x, y - 0.62, z, 0.45, 0.04, 0.9, (0.25, 0.18, 0.10), yaw=yaw, ox=x, oy=y)
        m.box(x, y + 0.62, z, 0.45, 0.04, 0.9, (0.25, 0.18, 0.10), yaw=yaw, ox=x, oy=y)
        add_person(m, x, y, z + 0.4, yaw, "legionary", rng, 0.9)
    elif kind == "cart":
        add_horse(m, x + 2.6, y, z, yaw, (0.30, 0.20, 0.12))
        m.box(x, y, z + 0.6, 1.2, 0.7, 0.5, (0.45, 0.32, 0.18), yaw=yaw, ox=x, oy=y)
        m.box(x, y, z + 1.1, 1.0, 0.6, 0.4, rng.choice([(0.7, 0.6, 0.35), (0.35, 0.45, 0.20)]), yaw=yaw, ox=x, oy=y)
    elif kind == "carriage":
        add_horse(m, x + 3.0, y, z, yaw, (0.12, 0.10, 0.08))
        m.box(x, y, z + 0.6, 1.3, 0.75, 1.3, (0.08, 0.08, 0.10), yaw=yaw, ox=x, oy=y)
    elif kind == "tram":
        m.box(x, y, z + 0.3, 6.5, 1.1, 2.8, (0.85, 0.65, 0.20), yaw=yaw, ox=x, oy=y)
        m.box(x, y, z + 3.1, 6.3, 1.0, 0.2, (0.30, 0.30, 0.30), yaw=yaw, ox=x, oy=y)
    elif kind == "car":
        col = rng.choice([(0.75, 0.10, 0.10), (0.92, 0.92, 0.92), (0.10, 0.10, 0.12), (0.20, 0.35, 0.60),
                          (0.55, 0.55, 0.58), (0.95, 0.80, 0.15)])
        m.box(x, y, z + 0.25, 2.1, 0.85, 0.65, col, yaw=yaw, ox=x, oy=y)
        m.box(x - 0.2, y, z + 0.9, 1.2, 0.78, 0.55, (0.12, 0.15, 0.20), yaw=yaw, ox=x, oy=y)
    elif kind == "vespa":
        col = rng.choice([(0.55, 0.80, 0.75), (0.85, 0.15, 0.12), (0.92, 0.92, 0.88), (0.95, 0.75, 0.20)])
        m.box(x, y, z + 0.2, 0.8, 0.3, 0.6, col, yaw=yaw, ox=x, oy=y)
        add_person(m, x, y, z + 0.4, yaw, "modern", rng, 0.9)


def finish(m, name, mat, collection):
    me = bpy.data.meshes.new(name)
    me.from_pydata(m.v, [], m.f)
    attr = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
    data = []
    for poly, c in zip(me.polygons, m.c):
        data.extend((c[0], c[1], c[2], 0.0) * poly.loop_total)
    attr.data.foreach_set("color", data)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    # stride shape key: feet swing forward/back along the figure's facing direction
    ob.shape_key_add(name="rest")
    key = ob.shape_key_add(name="stride")
    for i, sw in enumerate(m.swing):
        if sw:
            key.data[i].co.x += sw
    return ob


def make_group(spec, ground, mat, collection, seed):
    """spec: {"kind": costume or vehicle, "count", "formation": "block"|"crowd"|"line",
    "path": [[x, y], ...] (metres), "from"/"to" (film seconds), "speed" (m/s), "width"}"""
    rng = random.Random(seed)
    m = Mesh()
    n = spec.get("count", 100)
    form = spec.get("formation", "crowd")
    width = spec.get("width", 20.0)
    yaw = 0.0
    vehicles = spec["kind"] in ("chariot", "cart", "carriage", "tram", "car", "vespa")
    for k in range(n):
        if form == "block":
            cols = max(1, int(width / 1.2))
            dx, dy = -(k // cols) * 1.3, (k % cols) * 1.2 - width / 2
        elif form == "line":
            dx, dy = -k * (8.0 if vehicles else 1.5), rng.uniform(-width / 2, width / 2) if not vehicles else 0
        else:
            dx, dy = rng.uniform(-width, width), rng.uniform(-width, width)
        f_yaw = yaw if form != "crowd" else rng.uniform(0, 2 * math.pi)
        if vehicles:
            add_vehicle(m, dx, dy, 0.0, f_yaw, spec["kind"], rng)
        else:
            add_person(m, dx, dy, 0.0, f_yaw, spec["kind"], rng, spec.get("scale", 1.0))
    ob = finish(m, "group_" + spec["kind"], mat, collection)
    ob.hide_render = True
    return {"ob": ob, "spec": spec, "ground": ground}


def place_group(g, t):
    """Move a group along its path for film time t."""
    sp = g["spec"]
    ob = g["ob"]
    if not (sp["from"] <= t <= sp["to"]):
        ob.hide_render = True
        return
    ob.hide_render = False
    path = [Vector(p) for p in sp["path"]]
    dist = (t - sp["from"]) * sp.get("speed", 1.4)
    total = sum((b - a).length for a, b in zip(path, path[1:])) if len(path) > 1 else 0
    if total > 0 and sp.get("loop"):
        dist %= total
    pos, heading = path[0], Vector((1, 0))
    for a, b in zip(path, path[1:]):
        seg = (b - a).length
        if seg <= 0:
            continue
        heading = (b - a).normalized()
        if dist <= seg:
            pos = a + (b - a) * (dist / seg)
            break
        dist -= seg
        pos = b
    ob.location = (pos.x, pos.y, g["ground"](pos.x, pos.y))
    ob.rotation_euler.z = math.atan2(heading.y, heading.x)
    moving = len(path) > 1 and sp.get("speed", 1.4) > 0
    if ob.data.shape_keys:
        ob.data.shape_keys.key_blocks["stride"].value = math.sin(t * 2 * math.pi * 1.6) if moving else 0.0
