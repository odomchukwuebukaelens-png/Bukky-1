import json, subprocess, os
from concurrent.futures import ThreadPoolExecutor
rows = json.load(open('toons.json'))
def job(r):
    name, prompt, ref = r[4], r[5], r[6]
    out = f"art/{name}.png"
    if os.path.exists(out): return name, "skip"
    args = ["python3", "-I", "tools_img.py", out]
    args += ([f"Keep the same character design as in @img1. {prompt}", "16:9", "art/test_smuggler.png"] if ref == "ref" else [prompt, "16:9"])
    for attempt in range(3):
        p = subprocess.run(args, capture_output=True, text=True)
        if p.returncode == 0 and os.path.exists(out): return name, "ok"
    return name, "FAIL " + (p.stderr or p.stdout)[-200:]
with ThreadPoolExecutor(4) as ex:
    for name, st in ex.map(job, rows): print(name, st, flush=True)
print("GEN_DONE", flush=True)
