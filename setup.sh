#!/usr/bin/env bash
# One-time setup for a RunPod Ubuntu 24.04 pod. Run from the repo root:
#   bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"
export DEBIAN_FRONTEND=noninteractive

SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

echo "==> System packages"
$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends \
  ca-certificates curl git tmux ffmpeg fontconfig \
  libnss3 libdbus-1-3 libatk1.0-0t64 libatk-bridge2.0-0t64 libasound2t64 \
  libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 libgbm1 \
  libcups2t64 libcairo2 libpango-1.0-0 libegl1 libgles2

echo "==> Fonts"
for pkg in fonts-inter fonts-dejavu-core fonts-noto-color-emoji; do
  $SUDO apt-get install -y --no-install-recommends "$pkg" || echo "   (skipped $pkg)"
done
fc-cache -f >/dev/null

echo "==> Node.js"
node_major=0
if command -v node >/dev/null 2>&1; then
  node_major=$(node -p 'process.versions.node.split(".")[0]')
fi
if [ "$node_major" -lt 20 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash -
  $SUDO apt-get install -y nodejs
fi
echo "   node $(node -v), npm $(npm -v)"

echo "==> Project dependencies"
cd video
npm ci
npx remotion browser ensure

echo "==> Checks"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sed 's/^/   GPU: /'
else
  echo "   GPU: nvidia-smi not found (rendering will still work on CPU)"
fi

echo
echo "Setup complete. Render with:  bash render.sh"
