#!/usr/bin/env bash
# Render the video. Run from the repo root:  bash render.sh
# Output: video/out/video.mp4
set -euo pipefail
cd "$(dirname "$0")/video"

# Containers often report the host's CPU count; use the pod's real CPU allowance.
cpu_limit() {
  local n quota period
  n=$(nproc)
  if [ -r /sys/fs/cgroup/cpu.max ]; then
    read -r quota period < /sys/fs/cgroup/cpu.max
  elif [ -r /sys/fs/cgroup/cpu/cpu.cfs_quota_us ]; then
    quota=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us)
    period=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)
  fi
  if [[ "${quota:-}" =~ ^[0-9]+$ ]] && [ "$quota" -gt 0 ] && [ "${period:-0}" -gt 0 ]; then
    local lim=$(( (quota + period - 1) / period ))
    [ "$lim" -lt "$n" ] && n=$lim
  fi
  echo "$n"
}
THREADS=${THREADS:-$(cpu_limit)}
echo "Rendering with $THREADS parallel workers."
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
