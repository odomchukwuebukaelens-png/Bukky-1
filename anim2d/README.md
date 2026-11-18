# anim2d: the channel's 2D animation engine

Flat white line-art characters on black, drawn and animated entirely in code with Skia. There are no AI images and no GPU.

| File | What it does |
|---|---|
| `engine.py` | Palette, drawing pen, the family figures (mom, dad, sis, you, Tola, Tobi, grandma, toddler), faces and micro-actions (blink, breathe, tremble, talk, tears, bloodshot eyes), props, sets, the top bar, text slams |
| `shots01.py` | Hand-tuned opening shots (0:00–0:30) |
| `shots_all.py` | Reusable scene builders (table view, close-ups, blueprint diagrams, hallway, twins, VHS memories, inserts, menu rule cards) and a map from every shot name in the edit to its drawing |
| `render.py` | Renders a time range of a video from its `edl.json`. Use `--raw` for parallel chunks |

**Rendering the full video** (about 3 minutes on 4 cores, then one final encode of about 10 minutes):

```bash
for r in "0 152" "152 304" "304 456" "456 607.546"; do set -- $r; python3 render.py --t0 $1 --t1 $2 --raw --out ../video01/full_tmp/part_$1.mp4 & done; wait
```

Then join the chunks and add grain, captions and audio. See the ffmpeg line in the session notes, or `video01/README.md`.
