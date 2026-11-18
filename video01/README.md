# Video 01: If Your Family Ever Stops Blinking At Dinner… KEEP EATING

| File | What it is |
|---|---|
| `narration.txt` | Final script (1,451 words) |
| `narration_raw.mp3` | AI voiceover (ElevenLabs "Victor", speed 0.93) |
| `narration_words.json` | Word-level timings for the raw voiceover |
| `shotplan.py` | The edit, hand-written: shots for each of the 176 sentences, plus the dramatic pauses |
| `build.py` | Inserts the pauses, cuts shots on word boundaries, enforces the 2-second rule. Writes `edl.json`, `shotlist.md`, `captions.ass` and `words_final.json` |
| `shotlist.md` | Readable shot list: 467 shots, 10:07, average 1.35s, maximum 2.0s |
| `audio/` | Music cues (Suno) and 28 sound effects (ElevenLabs) |
| `mix.py` | Mixes voice, music and sound effects into `mix.wav` at −14 LUFS (not committed; regenerate) |
| `animatic.py` → `animatic.mp4` | 10-minute timing draft: placeholder card per shot, real audio, captions |
| `retention_playbook.md` | The editing rules this video is cut to |
| `youtube_metadata.md` | Title, description, chapters, tags and upload checklist |
| `gen_audio.py`, `gen_art.py`, `recover.py` | Asset generation through api.ai33.pro |

To rebuild everything after changing the plan:

```bash
python3 build.py && python3 mix.py && python3 animatic.py
```

**3D:** `../blender/dining_set.py` builds the set. `../blender/render_shots.py` renders shots from `edl.json`, using the GPU on RunPod.
