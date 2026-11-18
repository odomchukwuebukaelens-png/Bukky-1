"""Generate music cues (Suno) and sound effects (ElevenLabs SFX) via ai33. Skips files that exist."""
import sys, os, json, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools")); import ai33
D = os.path.dirname(os.path.abspath(__file__))
MUSIC = {
 "m1_sunday_warm": "warm cozy acoustic family dinner music, gentle guitar and soft piano, homely Sunday evening, light and happy",
 "m2_dread_bed": "dark ambient horror underscore, slow eerie low drones, sparse detuned music box notes, unsettling quiet tension, cinematic",
 "m3_tension_pulse": "pulsing horror suspense, ticking clock rhythm, low staccato strings ostinato, slowly rising tension, cinematic thriller",
 "m4_memory_piano": "sad emotional solo piano, slow and tender, bittersweet childhood memories, intimate, cinematic",
 "m5_end_lullaby": "creepy dissonant music box lullaby, slow, haunting horror ending theme, fading out",
}
SFX = {
 "drone_hit": ("deep cinematic horror drone hit with sub boom", 3), "freeze_cut": ("tape stop effect, sound abruptly halting", 1.5),
 "tick_grain": ("a single tiny grain of rice landing on a tablecloth, crisp close tick", 1), "heartbeat": ("slow heavy muffled heartbeat, four beats", 4),
 "chair_scrape": ("wooden dining chair scraping slowly across a wooden floor", 2), "stinger_card": ("short eerie horror stinger, reversed cymbal into a soft metallic hit", 2.5),
 "whoosh": ("fast cinematic whoosh", 1), "text_slam": ("heavy short cinematic impact boom for a title slam", 1),
 "clink": ("a fork tapping a ceramic plate once", 1), "chew_wet": ("slow wet chewing, unsettling, close microphone", 3),
 "buzz": ("low eerie electrical hum buzzing", 3), "crickets": ("night crickets outside a suburban house, calm", 5),
 "walla": ("family dinner chatter with cutlery clinking, indistinct talking, warm room", 5), "laugh_family": ("a family laughing together at a dinner table", 3),
 "clock_tick": ("old wall clock ticking", 4), "candle_whoomp": ("candle flames suddenly flaring up, soft whoomp", 1.5),
 "door_open": ("front door creaking open at night with wind", 2.5), "door_close": ("front door closing with a heavy thud", 1.5),
 "footsteps": ("slow footsteps on carpet in a hallway", 3), "vhs_rewind": ("VHS tape rewinding", 2),
 "stamp": ("rubber stamp hitting paper", 1), "receipt": ("receipt printer printing a short receipt", 2),
 "gulp": ("a single swallowing gulp", 1), "kick_thud": ("a light kick against a shin under a table, soft thud", 1),
 "breath_gasp": ("a family gasping for air in relief", 2), "metronome": ("single metronome click", 1),
 "glitch": ("short digital glitch", 1), "room_tone_dread": ("quiet room tone with a faint unsettling low hum", 6),
}
def music(name, prompt):
    raise SystemExit("Music is NOT regenerated: reuse assets/music/ (see assets/music/README.md). Only SFX may be generated.")
    if os.path.exists(f"{D}/audio/music/{name}_a.mp3"): return name, "exists"
    r = ai33.post_json("/v1s/task/music-generation", {"create_mode": "simple", "gpt_description_prompt": prompt, "make_instrumental": True})
    t = ai33.wait(r["task_id"], every=10, limit=1500); md = t.get("metadata") or {}
    urls = md.get("all_audio_urls") or [md.get("audio_url")]
    for i, u in enumerate(u for u in urls if u): ai33.download(u, f"{D}/audio/music/{name}_{'ab'[i]}.mp3")
    return name, f"{t['status']} cost={t.get('credit_cost')} clips={len(urls)}"
def sfx(name, spec):
    if os.path.exists(f"{D}/audio/sfx/{name}.mp3"): return name, "exists"
    prompt, dur = spec
    r = ai33.post_json("/v1/task/sound-effect", {"text": prompt, "duration_seconds": dur, "prompt_influence": 0.6, "model_id": "eleven_text_to_sound_v3"})
    t = ai33.wait(r["task_id"], every=3); md = t.get("metadata") or {}
    u = md.get("audio_url") or md.get("url") or (md.get("output") or {}).get("url")
    if not u: return name, f"{t['status']} NO URL {json.dumps(md)[:300]}"
    ai33.download(u, f"{D}/audio/sfx/{name}.mp3"); return name, f"{t['status']} cost={t.get('credit_cost')}"
with cf.ThreadPoolExecutor(6) as ex:
    futs = [ex.submit(sfx, k, v) for k, v in SFX.items()]  # music comes from assets/music, never regenerated
    for f in cf.as_completed(futs):
        try: print(*f.result(), flush=True)
        except Exception as e: print("ERROR", repr(e), flush=True)
print("credits left", ai33.get("/v1/credits"), flush=True)
