"""Generate narration per segment via the ai33 v3 TTS API (ElevenLabs voice), with word timestamps.
Writes audio/<id>.mp3 and audio/<id>.json. Skips segments whose audio already exists.
usage: python3 -I tools/tts.py script.json"""
import json, sys, time, subprocess, os, urllib.request

API = "https://api.ai33.pro"
HDR = ["-H", "xi-api-key: injected-by-proxy"]

def curl(*args):
    return subprocess.run(["curl", "-sS", "--max-time", "120", *args], capture_output=True, text=True, check=True).stdout

def synth(text, voice, speed):
    r = json.loads(curl("-X", "POST", f"{API}/v3/text-to-speech", *HDR, "-F", f"text={text}",
                        "-F", f"voice_id={voice}", "-F", f"speed={speed}", "-F", "with_transcript=true"))
    if not r.get("success"): raise RuntimeError(r)
    tid = r["task_id"]
    for _ in range(120):
        d = json.loads(curl(f"{API}/v3/task/{tid}", *HDR))["data"]
        if d["status"] == "done" and d["metadata"].get("transcript_status") in ("completed", None): return d
        if d["status"] == "error": raise RuntimeError(d)
        time.sleep(3)
    raise TimeoutError(tid)

if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    os.makedirs("audio", exist_ok=True)
    for seg in S["segments"]:
        mp3, js = f"audio/{seg['id']}.mp3", f"audio/{seg['id']}.json"
        if os.path.exists(mp3) and os.path.exists(js): continue
        d = synth(seg["text"], S["voice"], S.get("speed", 1))
        m = d["metadata"]
        curl("-o", mp3, m["audio_url"].split("?")[0])
        curl("-o", js, m["json_url"].split("?")[0])
        dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3], capture_output=True, text=True).stdout.strip()
        print(seg["id"], dur, "s", flush=True)
