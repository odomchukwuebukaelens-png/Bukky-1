#!/usr/bin/env bash
# Render the video. Run from the repo root:  bash render.sh
# Output: video/out/video.mp4
set -euo pipefail
cd "$(dirname "$0")/video"

THREADS=$(nproc)
OUT="out/video.mp4"

# Use the GPU for drawing when Chrome can reach it; otherwise fall back to CPU.
GL_FLAG=""
if command -v nvidia-smi >/dev/null 2>&1 && \
   npx remotion still Main out/gpu-test.jpg --frame=0 --gl=angle-egl >/dev/null 2>&1; then
  GL_FLAG="--gl=angle-egl"
  echo "Drawing with the GPU (angle-egl)."
else
  echo "Drawing on the CPU (GPU not reachable from Chrome)."
fi
rm -f out/gpu-test.jpg

start=$(date +%s)
npx remotion render Main "$OUT" --concurrency="$THREADS" $GL_FLAG "$@"
end=$(date +%s)
echo "Rendered $OUT in $((end - start)) seconds."
