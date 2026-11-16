# Bukky-1

2D motion-graphics video built as code with [Remotion](https://www.remotion.dev), rendered headlessly on a RunPod pod.

## On the pod

Clone into the persistent volume so the work survives a pod stop:

```bash
cd /workspace && git clone -b claude/quirky-galileo-7o2pi3 https://github.com/odomchukwuebukaelens-png/Bukky-1.git && cd Bukky-1
```

```bash
bash setup.sh
```

```bash
tmux new -s render 'bash render.sh; bash'
```

The finished file is `video/out/video.mp4`.

## Layout

- `setup.sh` installs system libraries, fonts, Node.js, project dependencies and the headless browser.
- `render.sh` renders with one worker per CPU thread, using the GPU for drawing when available.
- `video/script/` holds the narration scripts; `video/tools/voiceover.py` turns a script into per-scene audio and word timings.
- `video/src/octopus/` holds the scenes for the giant Pacific octopus video; `video/src/kit/` holds the shared characters, text and timing helpers.
