"""Low-poly trees shared by the city styles.

add_tree() draws one tree with a trunk; tree_instancer() stores five tree
models once and lets every forest bucket copy them as instances, so a
dense forest of half a million trees needs very little memory.
Kinds: "broad" (leafy, two lumpy crowns), "con" (cedar / pine cones),
"umbrella" (Italian stone pine), "cypress" (tall dark spindle).
"""
import math
import random

import bpy

import style_historic as H

_PHI = (1 + 5 ** 0.5) / 2
_ICO_V = [(-1, _PHI, 0), (1, _PHI, 0), (-1, -_PHI, 0), (1, -_PHI, 0), (0, -1, _PHI), (0, 1, _PHI), (0, -1, -_PHI),
          (0, 1, -_PHI), (_PHI, 0, -1), (_PHI, 0, 1), (-_PHI, 0, -1), (-_PHI, 0, 1)]
_ICO_V = [tuple(c / math.sqrt(1 + _PHI * _PHI) for c in v) for v in _ICO_V]
_ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
          (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
          (8, 6, 7), (9, 8, 1)]
TRUNK = (0.16, 0.10, 0.06)


def add_tree(part, x, y, zb, r, rng, kind=None, shade=1.0):
    """A low-poly tree with a trunk: a broadleaf (two lumpy crowns) or a
    conifer (stacked cones), stone pine or cypress. r is the crown radius."""
    kind = kind or ("con" if rng.random() < 0.4 else "broad")
    g = rng.uniform(0.82, 1.18) * shade
    ang = rng.uniform(0, 2 * math.pi)
    tw = max(0.5, r * 0.11)
    th = r * (0.9 if kind == "broad" else 0.6)
    tv = [(x + math.cos(ang + k * 2.094) * tw, y + math.sin(ang + k * 2.094) * tw, zz)
          for zz in (zb - 0.5, zb + th) for k in range(3)]
    if kind in ("broad", "con", "cypress"):
        part.add(tv, [(0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], [TRUNK] * 3)
    if kind == "umbrella":                       # Italian stone pine: tall bare trunk, flat wide crown
        th = r * 1.5
        tv = [(x + math.cos(ang + k * 2.094) * tw, y + math.sin(ang + k * 2.094) * tw, zz)
              for zz in (zb - 0.5, zb + th) for k in range(3)]
        part.add(tv, [(0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], [TRUNK] * 3)
        dk = (0.05 * g, 0.17 * g, 0.05 * g)
        lt = (0.07 * g, 0.23 * g, 0.06 * g)
        part.add([(x + vx * r * 1.15, y + vy * r * 1.15, zb + th + r * 0.25 + vz * r * 0.38) for vx, vy, vz in _ICO_V],
                 _ICO_F, [dk] * 20)
        ox, oy = math.cos(ang) * r * 0.35, math.sin(ang) * r * 0.35
        part.add([(x + ox + vx * r * 0.7, y + oy + vy * r * 0.7, zb + th + r * 0.5 + vz * r * 0.3) for vx, vy, vz in _ICO_V],
                 _ICO_F, [lt] * 20)
        return
    if kind == "cypress":                        # Mediterranean cypress: a tall dark spindle
        dk = (0.035 * g, 0.12 * g, 0.04 * g)
        part.add([(x + vx * r * 0.42, y + vy * r * 0.42, zb + r * 1.55 + vz * r * 1.45) for vx, vy, vz in _ICO_V],
                 _ICO_F, [dk] * 20)
        return
    if kind == "broad":
        lo = (0.05 * g, 0.19 * g, 0.035 * g)
        hi = (0.08 * g, 0.27 * g, 0.05 * g)
        c1 = zb + th + r * 0.72
        part.add([(x + vx * r, y + vy * r, c1 + vz * r * 0.82) for vx, vy, vz in _ICO_V], _ICO_F, [lo] * 20)
        r2 = r * rng.uniform(0.55, 0.72)
        ox, oy = math.cos(ang + 2.5) * r * 0.38, math.sin(ang + 2.5) * r * 0.38
        part.add([(x + ox + vx * r2, y + oy + vy * r2, c1 + r * 0.55 + vz * r2 * 0.85) for vx, vy, vz in _ICO_V],
                 _ICO_F, [hi] * 20)
    else:
        dk = (0.03 * g, 0.13 * g, 0.04 * g)
        lt = (0.045 * g, 0.18 * g, 0.05 * g)
        for base, rad, top, c_ in ((th, r * 0.78, th + r * 1.7, dk), (th + r * 1.0, r * 0.52, th + r * 2.6, lt)):
            v = [(x + math.cos(ang + k * 1.0472) * rad, y + math.sin(ang + k * 1.0472) * rad, zb + base) for k in range(6)]
            v.append((x, y, zb + top))
            part.add(v, [(k, (k + 1) % 6, 6) for k in range(6)], [c_] * 6)


TREE_KINDS = [("broad", 0.85), ("broad", 1.0), ("broad", 1.18), ("con", 0.85), ("con", 1.08)]


def tree_instancer(tree_mat, collection, kinds=None):
    """Five tree models (e.g. 3 broadleaf, 2 conifer) stored once; every forest
    bucket is a cloud of points that copies them (very little memory)."""
    models = bpy.data.collections.new("TreeKinds")
    for n, (kind, shade) in enumerate(kinds or TREE_KINDS):
        part = H.Parts()
        add_tree(part, 0.0, 0.0, 0.0, 1.0, random.Random(40 + n), kind, shade)
        ob = part.to_object("treekind_%d" % n, tree_mat, models)
        ob.name = "treekind_%d" % n
    ng = bpy.data.node_groups.new("ForestInstances", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nn, ln = ng.nodes, ng.links
    gi, go = nn.new("NodeGroupInput"), nn.new("NodeGroupOutput")
    ci = nn.new("GeometryNodeCollectionInfo")
    ci.inputs["Collection"].default_value = models
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    iop = nn.new("GeometryNodeInstanceOnPoints")
    iop.inputs["Pick Instance"].default_value = True

    def named(name, dtype):
        a = nn.new("GeometryNodeInputNamedAttribute")
        a.data_type = dtype
        a.inputs["Name"].default_value = name
        return a.outputs["Attribute"]
    comb = nn.new("ShaderNodeCombineXYZ")
    ln.new(named("rz", "FLOAT"), comb.inputs["Z"])
    e2r = nn.new("FunctionNodeEulerToRotation")
    ln.new(comb.outputs[0], e2r.inputs[0])
    ln.new(gi.outputs[0], iop.inputs["Points"])
    ln.new(ci.outputs[0], iop.inputs["Instance"])
    ln.new(named("var", "INT"), iop.inputs["Instance Index"])
    ln.new(e2r.outputs[0], iop.inputs["Rotation"])
    ln.new(named("scl", "FLOAT"), iop.inputs["Scale"])
    ln.new(iop.outputs[0], go.inputs[0])

    def make(name, pts):
        me = bpy.data.meshes.new(name)
        me.from_pydata([(p[0], p[1], p[2]) for p in pts], [], [])
        for an, at, idx in (("scl", "FLOAT", 3), ("rz", "FLOAT", 4), ("var", "INT", 5)):
            a = me.attributes.new(an, at, "POINT")
            a.data.foreach_set("value", [p[idx] for p in pts])
        ob = bpy.data.objects.new(name, me)
        collection.objects.link(ob)
        ob.modifiers.new("forest", "NODES").node_group = ng
        return ob
    return make
