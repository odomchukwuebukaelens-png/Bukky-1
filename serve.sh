#!/usr/bin/env bash
# Share the rendered video over the pod's web link so it can be opened on a phone.
# Run from anywhere:  bash /workspace/Bukky-1/serve.sh     (Ctrl+C to stop)
set -euo pipefail
cd "$(dirname "$0")/video/out"
PORT=${PORT:-8888}

if [ ! -f video.mp4 ]; then
  echo "No video yet. Run render.sh first."
  exit 1
fi

if python3 -c "import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1',$PORT))==0 else 1)"; then
  echo "Port $PORT is already in use (probably JupyterLab)."
  echo "Open JupyterLab from the pod's Connect menu and download"
  echo "workspace/Bukky-1/video/out/video.mp4 from its file browser,"
  echo "or pick another exposed port:  PORT=8000 bash serve.sh"
  exit 1
fi

cat > index.html <<'HTML'
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rendered video</title>
<body style="margin:0;padding:16px;background:#06161f;color:#fff;font-family:sans-serif">
<h3>Rendered video</h3>
<video src="video.mp4" controls playsinline style="width:100%;border-radius:8px"></video>
<p><a href="video.mp4" download style="color:#7fd4ff;font-size:20px">Download video.mp4</a></p>
</body>
HTML

if [ -n "${RUNPOD_POD_ID:-}" ]; then
  echo "Open this on your phone:"
  echo "  https://${RUNPOD_POD_ID}-${PORT}.proxy.runpod.net/"
else
  echo "Serving on port $PORT."
fi
echo "Press Ctrl+C to stop sharing."
exec python3 -m http.server "$PORT" --bind 0.0.0.0 >/dev/null 2>&1
