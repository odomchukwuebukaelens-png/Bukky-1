#!/usr/bin/env bash
# Turn a YouTube video into review material: contact sheets of frames and a list of cuts.
# Run on the pod:  bash /workspace/Bukky-1/study.sh <youtube-url>
# Results land in /workspace/Bukky-1/study/ (download the sheet-*.jpg files and cuts.txt).
set -euo pipefail
URL=${1:?usage: bash study.sh <youtube-url or local video file>}
OUT="$(cd "$(dirname "$0")" && pwd)/study"
rm -rf "$OUT" && mkdir -p "$OUT" && cd "$OUT"

if [ -f "$URL" ]; then
  cp "$URL" video.mp4
else
  python3 -m pip install -q -U yt-dlp 2>/dev/null || python3 -m pip install -q -U --break-system-packages yt-dlp
  if ! python3 -m yt_dlp --no-playlist -f "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480]" \
        --merge-output-format mp4 -o video.mp4 "$URL"; then
    echo
    echo "YouTube refused the download from this machine. Nothing was produced."
    exit 1
  fi
fi

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4)
echo "Video length: ${DUR%.*} seconds"

# Every cut, with its time, so shot lengths can be measured.
ffmpeg -v error -i video.mp4 -vf "select='gt(scene,0.25)',metadata=print:file=-" -an -f null - \
  | grep -o "pts_time:[0-9.]*" | cut -d: -f2 > cut_times.txt || true
python3 - "$DUR" <<'PY'
import sys
dur = float(sys.argv[1])
cuts = [float(x) for x in open("cut_times.txt").read().split()]
pts = [0.0] + cuts + [dur]
shots = [b - a for a, b in zip(pts, pts[1:]) if b - a > 0.2]
shots_sorted = sorted(shots)
with open("cuts.txt", "w") as f:
    f.write(f"length {dur:.0f}s, shots {len(shots)}, average {sum(shots)/len(shots):.1f}s, "
            f"median {shots_sorted[len(shots)//2]:.1f}s, longest {max(shots):.1f}s, "
            f"over 5s: {sum(s > 5 for s in shots)}\n")
    f.write("cut times (s): " + " ".join(f"{c:.1f}" for c in cuts) + "\n")
print(open("cuts.txt").read().split("\n")[0])
PY

# One frame every 2 seconds, time-stamped, 6 x 6 per sheet (72 seconds of video per sheet).
ffmpeg -v error -i video.mp4 -vf "fps=1/2,scale=320:180,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6,tile=6x6" \
  -q:v 5 sheet-%02d.jpg
echo "Wrote $(ls sheet-*.jpg | wc -l) contact sheets and cuts.txt to $OUT"
