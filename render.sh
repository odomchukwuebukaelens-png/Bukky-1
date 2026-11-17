#!/usr/bin/env bash
# Render a video. Run from the repo root:  bash render.sh [Composition]
# Output: video/out/video.mp4 (Main) or video/out/<composition>.mp4
set -euo pipefail
cd "$(dirname "$0")/video"

# "100%" lets Remotion use every CPU core the pod is actually allowed.
# Override with e.g. THREADS=4 bash render.sh
THREADS=${THREADS:-100%}
# Which video to render: "Main" is the octopus video, "Croc" the crocodile one.
COMP=${1:-Main}
[ $# -gt 0 ] && shift
if [ "$COMP" = "Main" ]; then OUT="out/video.mp4"; else OUT="out/$(echo "$COMP" | tr '[:upper:]' '[:lower:]').mp4"; fi
REMOTION="./node_modules/.bin/remotion"

# Reinstall dependencies if they are missing or an install was interrupted.
if [ ! -x "$REMOTION" ]; then
  echo "Dependencies missing; installing them first."
  npm ci
fi
"$REMOTION" browser ensure >/dev/null 2>&1 || echo "Could not pre-download the browser; the render will try again."

# Use the GPU for drawing when Chrome can reach it; otherwise fall back to CPU.
GL_FLAG=""
if command -v nvidia-smi >/dev/null 2>&1 && \
   "$REMOTION" still "$COMP" out/gpu-test.jpg --frame=0 --gl=angle-egl >/dev/null 2>&1; then
  GL_FLAG="--gl=angle-egl"
  echo "Drawing with the GPU (angle-egl)."
else
  echo "Drawing on the CPU (GPU not reachable from Chrome)."
fi
rm -f out/gpu-test.jpg

start=$(date +%s)
"$REMOTION" render "$COMP" "$OUT" --concurrency="$THREADS" $GL_FLAG "$@"
end=$(date +%s)
echo "Rendered $OUT in $((end - start)) seconds."
