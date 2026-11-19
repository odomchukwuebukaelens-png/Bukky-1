# Channel production rules

## Audio
- **Background music is fixed. Never generate new music.** Reuse the tracks in `assets/music/`. Its README is the catalogue: mood, length and where each track was used. Vary start offsets and alternate `_a`/`_b` takes between videos.
- **Only sound effects may be regenerated** for a new video, with `videoNN/gen_audio.py` (ElevenLabs SFX via api.ai33.pro). Reuse existing ones in `video01/audio/sfx/` when they fit.
- Narration: ElevenLabs voice "Victor – Halloween Horror Calm Narrator" (`elevenlabs_GoV1V2hQd1doxcYR2SuA`), speed 0.93, via `/v3/text-to-speech`.

## Visuals
- Simple flat 2D line-art: white figures on black, drawn and animated in code with `anim2d/` (Skia). **No AI images, no zooming on still pictures, no 3D or GPU pod.**
- Every shot needs micro-actions (blink, breathe, tremble, talk, steam, flicker). The picture must change at least every 2 seconds.
- **Never repeat a shot to fill time.** No splitting one shot into "micro-change" copies. Every cut is a new composition (a different angle, subject, set area or format), and neighbouring shots must look clearly different. `video02/build.py` stops with an error if a planned shot would exceed 2 seconds: add a new shot to the plan.
- **Characters always have necks**, in full-body figures and close-ups (`anim2d/engine.py`).
- **Scenery is detailed and beautiful but simple:** layered skies, moon and clouds, tree lines, fences, plants, furniture, light spill, fireflies and moths (`anim2d/scenes.py`). No empty black voids, except deliberate pattern breaks.
- Top bar: "<VIDEO COMMAND> · NIGHT/SUNDAY NN · RULE n" with a red REC dot and timecode. Captions: bold caps with the spoken word in acid green.

## Scripts
- Follow `script-formula.md` (the "If… COMMAND" title, the 7-rule structure, the twist, the callback ending) and `video01/retention_playbook.md`.

## Pipeline per video
`narration.txt` → TTS → `shotplan.py` → `build.py` → `mix.py` (music from `assets/music/`) → `anim2d/render.py` (parallel `--raw` chunks) → final ffmpeg pass (grain, captions, audio).
