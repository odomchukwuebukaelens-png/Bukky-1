#!/bin/bash
# Render the whole episode in parallel chunks, then join and mix audio.
cd "$(dirname "$0")/.."
DUR=$(python3 -I -c "import json;print(json.load(open('timeline.json'))['duration'])")
N=3; mkdir -p build/chunks
for i in $(seq 0 $((N-1))); do
  A=$(python3 -I -c "print(round($DUR*$i/$N,3))"); B=$(python3 -I -c "print(round($DUR*($i+1)/$N,3))")
  # snap chunk boundaries to whole frames
  A=$(python3 -I -c "print(round($A*30)/30)"); B=$(python3 -I -c "print(round($B*30)/30)")
  node tools/render.js chunk $A $B build/chunks/c$i.mp4 > build/chunks/c$i.log 2>&1 &
done
wait
printf "file 'c0.mp4'\nfile 'c1.mp4'\nfile 'c2.mp4'\n" > build/chunks/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/chunks/list.txt -c copy build/video_noaudio.mp4
ffmpeg -y -loglevel error -i build/video_noaudio.mp4 -i narration.wav -i build/sfx.wav \
  -filter_complex "[1:a]loudnorm=I=-15:TP=-1.5:LRA=11[v];[2:a]volume=1.0,aresample=44100,pan=stereo|c0=c0|c1=c0[s];[v][s]amix=inputs=2:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t "$DUR" EP01_How_Oil_Made_the_Dollar.mp4
echo DONE
