# City Studio

Turns a short production brief into a 3D city time-lapse video (MP4).

This is the first working prototype: a small invented test city that grows
from forest to skyline, with a year counter and an orbiting camera.

## One-time setup on the RunPod

```bash
cd /workspace
git clone --single-branch -b ccr-37255415-xvga7z https://github.com/odomchukwuebukaelens-png/Bukky-1.git city-studio
cd city-studio
```

If `/workspace/city-studio` already exists, use `cd /workspace/city-studio && git pull` instead.

## The four commands

| Command | What it does | Cost |
|---|---|---|
| `./studio setup` | Installs Blender 4.2 into this folder, plus FFmpeg, fonts and two small Python libraries. Run it after every pod start | 1-3 minutes |
| `./studio check` | Confirms Blender can use the NVIDIA A40 and the fast renderer | seconds |
| `./studio preview briefs/test_city.json` | Renders 3 still pictures to check the look | under a minute |
| `./studio run briefs/test_city.json` | Renders every frame and builds the MP4 | printed at the end |

The finished video is saved at `output/test_city/test_city.mp4`.
Preview pictures are in `output/test_city/stills/`.

`run` prints seconds per frame and the total time, so you can see the real
cost before starting anything long.

If a render is interrupted, run the same command again. It skips the parts
that are already finished and carries on.

To start a render completely fresh, delete the old output first:
`rm -rf output/test_city`

## How rendering works

- The fast renderer (EEVEE) is used when the pod supports it. If not, the
  slower Cycles renderer is used automatically.
- On a GPU pod, three copies of Blender render side by side. Change this with
  `WORKERS=4 ./studio run ...`. Force a renderer with `ENGINE=cycles ./studio run ...`.
- Frames are turned into video in small chunks and then deleted, so a long
  video does not fill the disk.

## Two visual styles

| Brief | Style |
|---|---|
| `briefs/test_city.json` | Simple toy-model city (first prototype) |
| `briefs/nyc_test.json` | New York, building by building: every building standing in Manhattan today rises in its recorded year (NYC Open Data). Older, demolished buildings are reconstructions. 20-second test of Lower Manhattan |
| `briefs/port_varen_test.json` | Realistic historical time-lapse: terrain, sea, forest, farmland, a town growing street by street, on-screen year, captions, labels and generated music. The city is invented |

The realistic style adds:
- **On-screen graphics** drawn on every frame: big year and era (bottom left),
  ruler and coat of arms (top left), population and compass (top right),
  event captions (bottom centre), floating place labels and an opening title card.
- **Original music**, generated fresh for each video. No copyrighted music is used.

## Changing a realistic (historical) video

Everything that appears on screen is plain text in the brief file:

| Setting | Meaning |
|---|---|
| `year_keys` | Which year is shown at which second, e.g. `[4.6, 1626]` = 1626 at 4.6 s |
| `title_card` | Opening title, subtitle line and years |
| `events` | Captions. Each appears when its `year` is reached |
| `eras`, `rulers` | Era name, realm, ruler and coat of arms, from a given year |
| `population` | Year and population pairs; values in between are filled in |
| `labels` | Place names that float over landmarks |
| `camera` | Where the camera starts and ends, and what it looks at |
| `music` | `"generate"` for original music, or a path to your own audio file |

## Changing the toy-city video

Edit `briefs/test_city.json` (or copy it to a new file):

| Setting | Meaning |
|---|---|
| `name` | Folder and file name of the output |
| `title` | Small title under the year counter |
| `duration_seconds`, `fps` | Length and frame rate |
| `resolution` | Width and height in pixels, e.g. `[1920, 1080]` |
| `start_year`, `end_year` | The period the counter runs through |
| `samples` | Picture quality. Higher is cleaner and slower. 24 is fine for tests |
| `seed` | Change this number for a different random city |
| `chunk_frames` | Frames per chunk. Leave at 300 |
| `sound` | `true` adds a soft generated wind bed, `false` gives a silent video |
| `city` | Number and size of street blocks |

## What is in this folder

- `studio` - the launcher
- `briefs/` - production briefs
- `citystudio/make_video.py` - plans the city, builds the scene, renders, assembles the MP4
- `citystudio/style_historic.py` - the realistic historical style (landscape, town growth, landmarks)
- `citystudio/overlay.py` - draws the on-screen year, captions and labels onto each frame
- `citystudio/music.py` - generates the original background music
- `citystudio/style_nyc.py` - the New York style (real buildings, landfill shoreline, landmarks)
- `citystudio/nyc_prepare.py` - turns raw NYC Open Data downloads into `data/nyc/`
- `data/nyc/` - prepared New York data (building footprints, years, heights, land, streets, parks)
- `output/` - renders (not stored in Git)

## Notes

- The test city is invented. Nothing in it is a factual reconstruction.
- Blender lives in `tools/blender` inside this folder, so it survives pod
  restarts. FFmpeg does not, which is why `setup` is rerun after each start.
- If Blender is not on the PATH, point to it:
  `BLENDER=/path/to/blender ./studio check`
