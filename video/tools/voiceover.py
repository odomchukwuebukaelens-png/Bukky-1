#!/usr/bin/env python3
"""Generate per-scene voiceover from a script file with the ai33.pro API.

Usage: python3 tools/voiceover.py script/04-giant-pacific-octopus.md octopus [scene numbers...]

Writes public/audio/<name>/NN.mp3 and src/<name>/timing.json.
Reads the API key from AI33_API_KEY.
"""
import json, os, re, subprocess, sys, time, urllib.request, urllib.error, uuid

API = "https://api.ai33.pro"
KEY = os.environ.get("AI33_API_KEY", "placeholder")
VOICE = os.environ.get("AI33_VOICE", "clone_2719063")
SPEED = os.environ.get("AI33_SPEED", "0.95")


def parse(path):
    text = open(path).read()
    scenes = []
    for m in re.finditer(r"^## (\d+)\. (.+?)\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S):
        lines = [l.strip() for l in m.group(3).split("\n")]
        lines = [l for l in lines if l and not l.startswith("**Visual") and l != "---"]
        body = "\n\n".join(re.sub(r"\s*\[CHECK[^\]]*\]", "", l) for l in lines)
        scenes.append({"n": int(m.group(1)), "title": m.group(2).strip(), "text": body})
    return scenes


def request(method, url, fields=None):
    headers = {"xi-api-key": KEY}
    data = None
    if fields is not None:
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in fields.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n')
        parts.append(f"--{boundary}--\r\n")
        data = "".join(parts).encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    for attempt in range(12):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=90) as r:
                out = json.loads(r.read())
            if out.get("code") == "server_busy":
                raise RuntimeError("busy")
            return out
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise SystemExit(f"{url}: HTTP {e.code} {e.read()[:300]!r}")
            wait = float(e.headers.get("Retry-After") or 0) or min(30, 2 ** attempt)
        except (RuntimeError, urllib.error.URLError, TimeoutError, OSError):
            wait = min(30, 2 ** attempt)
        time.sleep(wait)
    raise SystemExit(f"{url}: gave up after retries")


def fetch(url):
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(min(30, 2 ** attempt))
    raise SystemExit(f"{url}: download failed")


def download(url, dest):
    with open(dest, "wb") as f:
        f.write(fetch(url))


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.strip())


def main():
    script, name = sys.argv[1], sys.argv[2]
    only = {int(a) for a in sys.argv[3:]}
    scenes = parse(script)
    audio_dir = f"public/audio/{name}"
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(f"src/{name}", exist_ok=True)
    timing_path = f"src/{name}/timing.json"
    timing = json.load(open(timing_path)) if os.path.exists(timing_path) else {}

    for s in scenes:
        key = f"{s['n']:02d}"
        dest = f"{audio_dir}/{key}.mp3"
        if only and s["n"] not in only:
            continue
        if not only and os.path.exists(dest) and key in timing:
            continue
        created = request("POST", f"{API}/v3/text-to-speech", {
            "text": s["text"], "voice_id": VOICE, "speed": SPEED,
            "with_transcript": "true", "file_name": f"{name}-{key}"})
        task_id = created["task_id"]
        while True:
            time.sleep(4)
            task = request("GET", f"{API}/v1/task/{task_id}")
            if task.get("status") in ("done", "error"):
                break
        if task["status"] != "done":
            raise SystemExit(f"scene {key} failed: {task.get('error_message')}")
        meta = task["metadata"]
        raw = f"{audio_dir}/{key}.raw.mp3"
        download(meta["audio_url"], raw)
        # Mono 96 kbps keeps the repository small without audible loss for speech.
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ac", "1", "-b:a", "96k", dest])
        os.remove(raw)
        entry = {"title": s["title"], "duration": round(duration(dest), 3),
                 "credits": task.get("credit_cost"), "words": []}
        if meta.get("json_url"):
            # Word-level timings let the animation cue visuals to the narration.
            tr = json.loads(fetch(meta["json_url"]))
            for seg in tr:
                for w in seg.get("words", []):
                    if w.get("type") == "word":
                        entry["words"].append([w["text"], round(w["start"], 2), round(w["end"], 2)])
        timing[key] = entry
        json.dump(timing, open(timing_path, "w"), indent=1)
        print(key, s["title"], entry["duration"], "s,", task.get("credit_cost"), "credits,", len(entry["words"]), "words", flush=True)


if __name__ == "__main__":
    main()
