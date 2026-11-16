#!/usr/bin/env bash
# Render the video. Run from the repo root:  bash render.sh
# Output: video/out/video.mp4
set -euo pipefail
cd "$(dirname "$0")/video"

# "100%" lets Remotion use every CPU core the pod is actually allowed.
# Override with e.g. THREADS=4 bash render.sh
THREADS=${THREADS:-100%}
OUT="out/video.mp4"
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
   "$REMOTION" still Main out/gpu-test.jpg --frame=0 --gl=angle-egl >/dev/null 2>&1; then
  GL_FLAG="--gl=angle-egl"
  echo "Drawing with the GPU (angle-egl)."
else
  echo "Drawing on the CPU (GPU not reachable from Chrome)."
fi
rm -f out/gpu-test.jpg

start=$(date +%s)
"$REMOTION" render Main "$OUT" --concurrency="$THREADS" $GL_FLAG "$@"
end=$(date +%s)
echo "Rendered $OUT in $((end - start)) seconds."
