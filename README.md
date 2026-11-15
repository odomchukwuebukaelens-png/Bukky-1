# City Studio

Turns a short production brief into a 3D city time-lapse video (MP4).

This is the first working prototype: a small invented test city that grows
from forest to skyline, with a year counter and an orbiting camera.

## One-time setup on the RunPod

```bash
cd /workspace
git clone -b ccr-37255415-xvga7z https://github.com/odomchukwuebukaelens-png/Bukky-1.git city-studio
cd city-studio
```

If `/workspace/city-studio` already exists, use `cd /workspace/city-studio && git pull` instead.

## The three commands

| Command | What it does | Cost |
|---|---|---|
| `./studio check` | Confirms Blender can use the NVIDIA A40 | seconds |
| `./studio preview briefs/test_city.json` | Renders 3 still pictures to check the look | under a minute |
| `./studio run briefs/test_city.json` | Renders every frame and builds the MP4 | minutes on the A40 |

The finished video is saved at `output/test_city/test_city.mp4`.
Preview pictures are in `output/test_city/stills/`.

If a render is interrupted, run the same command again. It skips frames that
are already finished and carries on.

To start a render completely fresh, delete the old frames first:
`rm -rf output/test_city`

## Changing the video

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
| `sound` | `true` adds a soft generated wind bed, `false` gives a silent video |
| `city` | Number and size of street blocks |

## What is in this folder

- `studio` - the launcher
- `briefs/` - production briefs
- `citystudio/make_video.py` - plans the city, builds the scene, renders, assembles the MP4
- `output/` - renders (not stored in Git)

## Notes

- The test city is invented. Nothing in it is a factual reconstruction.
- Rendering uses Blender's Cycles engine on the GPU (OptiX or CUDA). Without a
  GPU it falls back to the CPU, which works but is slow.
- If Blender is not on the PATH, point to it:
  `BLENDER=/path/to/blender ./studio check`
