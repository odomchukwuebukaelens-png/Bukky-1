"""Generate style/key art via ai33 image models. Usage: python3 gen_art.py [name ...]"""
import sys, os, json, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools")); import ai33
D = os.path.dirname(os.path.abspath(__file__))
STYLE = ("Flat 2D cartoon illustration for an animated horror YouTube channel. Clean thick dark outlines, flat cel shading with one soft shadow tone, "
         "simple rounded shapes, large expressive eyes with glossy highlights, limited palette of deep navy, muted teal and warm wood browns with "
         "sickly acid-green (#B6FF3B) and mustard-yellow accent light. Subtle film grain. No text, no watermark, no logo.")
ART = {
 "charsheet_family": ("Character model sheet on a plain light-grey background: a Black family of four standing in a row, full body, front view, "
     "neutral relaxed pose, each separated by space. Left to right: DAD (early 40s, short beard, blue button-up shirt, khaki trousers), "
     "MOM (around 40, warm face, hair wrapped in a mustard-yellow headwrap, green patterned blouse, apron), "
     "YOU the main kid (12 years old, short curly hair, oversized teal hoodie, jeans, sneakers), "
     "SISTER (9 years old, two puffs hairstyle, purple t-shirt with a star, shorts, striped socks). " + STYLE, "16:9"),
 "keyframe_frozen_dinner": ("Wide shot from the viewer's seat at a family dinner table at night in a cosy dining room. Dad, mom and a little sister sit "
     "around the table completely frozen mid-action: dad's mouth half open mid-word, mom holding a serving spoon in mid-air with one grain of rice "
     "falling, sister mid-kick. All three stare straight at the viewer with wide unblinking wet eyes. Steam rises from a pot of red-orange rice. "
     "At the far end of the table one empty wooden chair is pulled out a few inches with a clean plate in front of it. Warm lamp light turning "
     "to sickly green at the edges. " + STYLE, "16:9"),
 "thumb_art": ("YouTube thumbnail artwork, right two-thirds of the frame only, the left third is a plain flat acid-green area left empty for text. "
     "Close-up of a mom at a dinner table frozen with a spoon of rice in mid-air, huge unblinking bloodshot eyes with tears, staring straight at the "
     "viewer, while behind her at the end of the table a dark shadowy figure sits politely in an empty chair with a napkin tucked in, two small "
     "glowing acid-green eyes and an oversized thin grin. High contrast, dramatic, readable at small size. " + STYLE, "16:9"),
}
MODEL = os.environ.get("ART_MODEL", "gpt-image-2.5-sunburst")
PARAMS = json.loads(os.environ.get("ART_PARAMS", "{}"))
def gen(name):
    prompt, ar = ART[name]
    r = ai33.post_form("/v1i/task/generate-image", {"prompt": prompt, "model_id": MODEL, "generations_count": "1",
                       "model_parameters": json.dumps(PARAMS or {"aspect_ratio": ar, "resolution": "2K", "quality": "high"})})
    if not r.get("task_id"): return name, f"FAILED {r}"
    t = ai33.wait(r["task_id"], every=5); md = t.get("metadata") or {}
    urls = md.get("result_images") or md.get("images") or md.get("image_urls") or ([md.get("image_url") or md.get("audio_url")] if (md.get("image_url") or md.get("audio_url")) else [])
    urls = [u if isinstance(u, str) else (u.get("url") or u.get("image_url")) for u in urls]
    for i, u in enumerate(urls): ai33.download(u, f"{D}/art/{name}{os.environ.get('ART_SUFFIX', '')}{'' if i == 0 else '_' + str(i)}.png")
    return name, f"{t['status']} cost={t.get('credit_cost')} n={len(urls)} keys={list(md)[:12]}"
names = sys.argv[1:] or list(ART)
with cf.ThreadPoolExecutor(3) as ex:
    for f in cf.as_completed([ex.submit(gen, n) for n in names]):
        try: print(*f.result(), flush=True)
        except Exception as e: print("ERROR", repr(e), flush=True)
