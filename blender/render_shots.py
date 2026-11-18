"""Render EDL shots of the dining set with Blender (Cycles; OptiX on GPU when available).

blender -b --factory-startup --python render_shots.py -- --edl ../video01/edl.json --t0 0 --t1 30 \
        --out ../video01/renders --res 1920x1080 --samples 24 [--gpu] [--only N,N]

Each renderable shot -> <out>/shot_NNN/0001.png ... (24 fps, exact frame count).
Shots whose set-up is not in this set (title cards, other locations) are listed in <out>/skipped.json.
"""
import bpy, sys, os, json, math, argparse
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dining_set as ds

a = argparse.ArgumentParser()
a.add_argument("--edl"); a.add_argument("--t0", type=float, default=0); a.add_argument("--t1", type=float, default=30)
a.add_argument("--out"); a.add_argument("--res", default="1920x1080"); a.add_argument("--samples", type=int, default=24)
a.add_argument("--gpu", action="store_true"); a.add_argument("--encode", action="store_true"); a.add_argument("--only", default="")
args = a.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
FPS = 24

# extra set-ups that can be framed in this set (aliases to camera presets + character focus)
ALIAS = {"ECU_MOM_EYES": ("MCU_MOM_SPOON", 120, "mom_head"), "CU_MOM_SMILE": ("MCU_MOM_SPOON", 60, "mom_head"),
         "CU_DAD_TALK": ("CU_DAD", 55, "dad_head"), "ECU_DAD_TV_REFLECT": ("CU_DAD", 110, "dad_head"),
         "CU_YOU_MOUTH": ("WIDE_TABLE_POV", 24, None), "WIDE_POV_STARE": ("WIDE_TABLE_POV", 24, None),
         "ECU_SIS_EYES": ("WIDE_TABLE_POV", 110, "sis_head"), "WIDE_TABLE_YOU": ("WIDE_TABLE", 22, None),
         "LIVING_TV_DAD": ("CU_DAD", 40, "dad_head"), "SIS_STARE_CONTEST": ("CU_SIS", 70, "sis_head"),
         "SIS_LAUGH": ("CU_SIS", 45, "sis_head")}

# ---------- simple toon stand-in characters (replaced by AI art billboards later) ----------
CHAR = {"dad": dict(seat=(-0.45, 1.05), yaw=180, body=(0.17, 0.33, 0.62), skin=(0.30, 0.17, 0.10), h=1.0),
        "mom": dict(seat=(0.45, 1.05), yaw=180, body=(0.15, 0.45, 0.25), skin=(0.36, 0.21, 0.12), h=0.96),
        "sis": dict(seat=(0.45, -1.05), yaw=0, body=(0.45, 0.25, 0.60), skin=(0.33, 0.19, 0.11), h=0.80)}
def make_char(n, c):
    sx, sy = c["seat"]; h = c["h"]; face = -1 if c["yaw"] == 180 else 1
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.55 * h, location=(sx, sy, 0.5 + 0.28 * h))
    body = bpy.context.object; body.name = f"{n}_body"; body.data.materials.append(ds._mat(f"{n}_shirt", c["body"])); ds._outline(body)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(sx, sy, 0.5 + 0.55 * h + 0.17))
    head = bpy.context.object; head.name = f"{n}_head"; head.data.materials.append(ds._mat(f"{n}_skin", c["skin"]))
    bpy.ops.object.shade_smooth(); ds._outline(head, 0.008)
    lids = []
    for ex in (-0.055, 0.055):
        ey = sy + face * 0.135; ez = head.location.z + 0.02
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.042, location=(sx + ex, ey, ez)); w = bpy.context.object
        w.data.materials.append(ds._mat("eye_white", (0.97, 0.97, 0.95))); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=(sx + ex, ey + face * 0.032, ez)); p = bpy.context.object
        p.data.materials.append(ds._mat("pupil", (0.02, 0.02, 0.02)))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.046, location=(sx + ex, ey, ez)); lid = bpy.context.object
        lid.name = f"{n}_lid"; lid.data.materials.append(ds._mat(f"{n}_skin", c["skin"])); lid.scale = (1, 1, 0.02)
        lid.location.z = ez + 0.03; lids.append(lid)
    return head, lids

def blink(lids, f):
    """Lids close and open over 5 frames starting at frame f."""
    for lid in lids:
        z0 = lid.location.z
        for df, sz, dz in ((0, 0.02, 0), (2, 1.0, -0.03), (5, 0.02, 0)):
            lid.scale.z = sz; lid.location.z = z0 + dz
            lid.keyframe_insert("scale", frame=f + df); lid.keyframe_insert("location", frame=f + df)
        lid.location.z = z0

def mood_for(si):
    if si < 12: return "warm"
    if si >= 164: return "warm"
    return "dark" if 68 <= si <= 72 or 104 <= si <= 106 else "frozen"

def animate_camera(cam, motion, f0, f1, base_loc, base_rot, base_lens, target):
    m = motion.lower(); loc0, rot0 = Vector(base_loc), base_rot.copy(); lens0 = base_lens
    loc1, rot1, lens1 = loc0.copy(), rot0.copy(), lens0
    to_t = (Vector(target) - loc0)
    if "micro-change" in m:  # cut-level change: start already offset, keep a small drift
        if "punch-in" in m: lens0 = lens1 = base_lens * 1.12
        elif "angle shift" in m: loc0 = loc0 + Vector((0.18, 0.05, 0.04)); loc1 = loc0.copy()
        elif "snap-zoom out" in m: lens0 = lens1 = base_lens * 0.85
        elif "dutch" in m: rot0.y += math.radians(5); rot1 = rot0.copy()
        elif "parallax" in m: loc1 = loc0 + Vector((0.08, 0, 0))
        elif "reverse drift" in m: loc1 = loc0 - to_t.normalized() * 0.06
        if "rack focus" in m or "light flicker" in m: loc1 = loc0 + to_t.normalized() * 0.03
        lens1 = lens1 * 1.02
    elif "snap-zoom" in m: lens0, lens1 = base_lens, base_lens * 1.6
    elif "pull" in m: loc1 = loc0 - to_t.normalized() * 0.25
    elif "orbit" in m:
        v = loc0 - Vector(target); ang = math.radians(20)
        loc1 = Vector(target) + Vector((v.x * math.cos(ang) - v.y * math.sin(ang), v.x * math.sin(ang) + v.y * math.cos(ang), v.z))
    elif "whip" in m: rot0 = rot0.copy(); rot0.z += math.radians(35); loc1 = loc0 + to_t.normalized() * 0.1
    elif "dolly" in m: loc0 = loc0 - to_t.normalized() * 0.6; loc1 = loc0 + to_t.normalized() * 0.5
    elif "freeze" in m or "static" in m: loc1 = loc0 + to_t.normalized() * 0.01
    else: loc1 = loc0 + to_t.normalized() * 0.18  # default: slow push-in (life in every shot)
    for f, L, R, Ln in ((f0, loc0, rot0, lens0), (f1, loc1, rot1, lens1)):
        cam.location = L; cam.rotation_euler = R; cam.data.lens = Ln
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    if "whip" in m:  # fast settle in 6 frames
        cam.rotation_euler = rot1; cam.keyframe_insert("rotation_euler", frame=min(f1, f0 + 6))
    if "rack focus" in m:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 1.4
        cam.data.dof.focus_distance = 0.3; cam.data.dof.keyframe_insert("focus_distance", frame=f0)
        cam.data.dof.focus_distance = to_t.length; cam.data.dof.keyframe_insert("focus_distance", frame=f0 + min(12, f1 - f0))

def main():
    edl = [s for s in json.load(open(args.edl)) if s["end"] > args.t0 and s["start"] < args.t1]
    only = {int(x) for x in args.only.split(",") if x}
    sc = ds.build(); cams = ds.add_cameras()
    w, h = map(int, args.res.split("x")); sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.cycles.samples = args.samples; sc.render.image_settings.file_format = "PNG"
    # speed: adaptive sampling, keep scene in memory between frames, denoise on GPU when available
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
    sc.render.use_persistent_data = True
    if hasattr(sc.cycles, "denoising_use_gpu"): sc.cycles.denoising_use_gpu = True
    if args.gpu:
        pr = bpy.context.preferences.addons["cycles"].preferences
        for dev in ("OPTIX", "CUDA"):
            try:
                pr.compute_device_type = dev; pr.get_devices()
                if any(d.type == dev for d in pr.devices):
                    for d in pr.devices: d.use = d.type == dev
                    sc.cycles.device = "GPU"; print("GPU:", dev); break
            except TypeError: pass
    heads = {n: make_char(n, c) for n, c in CHAR.items()}
    os.makedirs(args.out, exist_ok=True); skipped = []
    for s in edl:
        if only and s["n"] not in only: continue
        setup = s["setup"]; alias = ALIAS.get(setup)
        cam_name = alias[0] if alias else setup
        if cam_name not in cams: skipped.append(s["n"]); continue
        cam = cams[cam_name]; sc.camera = cam
        base = ds.CAMS[cam_name]; target = base[1]; lens = base[2]
        if alias:
            lens = alias[1]
            if alias[2]: target = tuple(bpy.data.objects[alias[2]].location)
        d = Vector(target) - Vector(base[0])
        cam.animation_data_clear(); cam.data.animation_data_clear()
        rot = d.to_track_quat("-Z", "Y").to_euler()
        nf = max(1, round(s["end"] * FPS) - round(s["start"] * FPS))
        sc.frame_start, sc.frame_end = 1, nf
        animate_camera(cam, s["motion"], 1, nf, base[0], rot, lens, target)
        ds.mood(mood_for(s["sentence"]))
        for n, (hd, lids) in heads.items():  # family blinks only before the freeze / after the unfreeze
            for l in lids: l.animation_data_clear()
            if mood_for(s["sentence"]) == "warm" and nf > 20: blink(lids, 8 + hash(n) % 10)
        for o in bpy.data.objects:
            if o.name.startswith("chair_you"): o.hide_render = cam_name == "WIDE_TABLE_POV"
        sc.render.filepath = os.path.join(args.out, f"shot_{s['n']:03d}", "")
        bpy.ops.render.render(animation=True)
        if args.encode:  # pack each shot as a small high-quality mp4 for download
            d = os.path.join(args.out, f"shot_{s['n']:03d}")
            os.system(f"ffmpeg -v error -y -framerate {FPS} -i {d}/%04d.png -c:v libx264 -crf 14 -preset fast -pix_fmt yuv420p {args.out}/shot_{s['n']:03d}.mp4")
        print(f"rendered shot {s['n']} {setup} ({nf} frames)", flush=True)
    json.dump(skipped, open(os.path.join(args.out, "skipped.json"), "w"))
    print("skipped (2D/other sets):", skipped)

main()
