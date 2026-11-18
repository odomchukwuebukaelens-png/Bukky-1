"""Match today's ai33 tasks to asset names; download finished ones; resubmit only missing ones (slowly)."""
import sys, os, json, time, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools")); import ai33
D = os.path.dirname(os.path.abspath(__file__))
def load(n):
    s = importlib.util.spec_from_file_location(n, f"{D}/{n}.py"); m = importlib.util.module_from_spec(s)
    src = open(f"{D}/{n}.py").read().split("def ")[0]  # only the dicts, don't run generation
    exec(compile(src, n, "exec"), m.__dict__); return m
ga, gr = load("gen_audio"), load("gen_art")
SINCE = "2026-11-18T09:2"
items = []
for p in range(1, 4):
    r = ai33.get(f"/v1/tasks?page={p}&limit=100"); it = r.get("data") or r.get("tasks") or []
    items += it
    if len(it) < 100: break
items = [i for i in items if i["created_at"] >= SINCE]
def key(i):
    md = i.get("metadata") or {}
    if i["type"] == "elevenlabs_sound_effect":
        return next((("sfx", k) for k, (p, _) in ga.SFX.items() if p == i.get("text")), None)
    if i["type"] == "imagen2":
        return next((("art", k) for k, (p, _) in gr.ART.items() if (md.get("prompt") or "")[:150] == p[:150]), None)
    if i["type"] == "suno_music":
        pr = md.get("gpt_description_prompt") or i.get("text") or ""
        return next((("music", k) for k, p in ga.MUSIC.items() if p == pr), None)
by = {}
for i in sorted(items, key=lambda x: x["created_at"]):
    k = key(i)
    if k: by.setdefault(k, []).append(i)
unmatched = [i["type"] for i in items if not key(i)]
print("matched", len(by), "unmatched", unmatched)
def dl(kind, name, t):
    md = t.get("metadata") or {}
    if kind == "sfx":
        dst = f"{D}/audio/sfx/{name}.mp3"
        if not os.path.exists(dst): ai33.download(md["audio_url"], dst)
    elif kind == "music":
        urls = md.get("all_audio_urls") or [c["audio_url"] for c in (md.get("suno_result") or {}).get("clips", [])]
        for j, u in enumerate(urls[:2]):
            dst = f"{D}/audio/music/{name}_{'ab'[j]}.mp3"
            if not os.path.exists(dst): ai33.download(u, dst)
    elif kind == "art":
        urls = md.get("result_images") or md.get("images") or md.get("image_urls") or ([md.get("image_url") or md.get("audio_url")] if (md.get("image_url") or md.get("audio_url")) else [])
        urls = [u if isinstance(u, str) else (u.get("url") or u.get("image_url")) for u in urls]
        if not urls: print("art keys", name, list(md)); return
        for j, u in enumerate(urls):
            dst = f"{D}/art/{name}{'' if j == 0 else '_' + str(j)}.png"
            if not os.path.exists(dst): ai33.download(u, dst)
pending = []
for (kind, name), ts in by.items():
    done = [t for t in ts if t["status"] == "done"]
    if done: dl(kind, name, done[-1]); continue
    live = [t for t in ts if t["status"] not in ("error", "failed")]
    if live: pending.append((kind, name, live[-1]["id"]))
for kind, name, tid in pending:
    t = ai33.wait(tid, every=10, limit=240) if False else ai33.get(f"/v1/task/{tid}"); print("checked", kind, name, t["status"])
    if t["status"] == "done": dl(kind, name, t)
missing = [("sfx", k) for k in ga.SFX if not os.path.exists(f"{D}/audio/sfx/{k}.mp3")] + \
          [("music", k) for k in ga.MUSIC if not os.path.exists(f"{D}/audio/music/{k}_a.mp3")] + \
          [("art", k) for k in gr.ART if not os.path.exists(f"{D}/art/{k}.png")]
print("missing after recovery:", missing, flush=True)
if "--resubmit" in sys.argv:
    for kind, name in missing:
        if kind == "sfx":
            p, d = ga.SFX[name]; r = ai33.post_json("/v1/task/sound-effect", {"text": p, "duration_seconds": d, "prompt_influence": 0.6, "model_id": "eleven_text_to_sound_v3"})
        elif kind == "music":
            r = ai33.post_json("/v1s/task/music-generation", {"create_mode": "simple", "gpt_description_prompt": ga.MUSIC[name], "make_instrumental": True})
        else:
            p, ar = gr.ART[name]
            r = ai33.post_form("/v1i/task/generate-image", {"prompt": p, "model_id": "gpt-image-2.5-sunburst", "generations_count": "1",
                               "model_parameters": json.dumps({"aspect_ratio": ar, "resolution": "2K", "quality": "high"})})
        t = ai33.wait(r["task_id"], every=10); print("resubmitted", kind, name, t["status"], t.get("credit_cost"), flush=True)
        if t["status"] == "done": dl(kind, name, t)
        time.sleep(2)
print("credits", ai33.get("/v1/credits"))
