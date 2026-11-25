#!/bin/bash
# usage: tools/render_all.sh <W> <H> <from> <to> <out.mp4> <chunks>
cd "$(dirname "$0")/.."
W=$1; H=$2; A=$3; B=$4; OUT=$5; N=${6:-3}
mkdir -p build/chunks_$W
for i in $(seq 0 $((N-1))); do
  a=$(python3 -I -c "print(round(($A+($B-$A)*$i/$N)*30)/30)"); b=$(python3 -I -c "print(round(($A+($B-$A)*($i+1)/$N)*30)/30)")
  W=$W H=$H node tools/render.js chunk $a $b build/chunks_$W/c$i.mp4 > build/chunks_$W/c$i.log 2>&1 &
done
wait
for i in $(seq 0 $((N-1))); do echo "file 'c$i.mp4'"; done > build/chunks_$W/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/chunks_$W/list.txt -c copy build/video_${W}.mp4
D=$(python3 -I -c "print(round($B-$A,3))")
ffmpeg -y -loglevel error -i build/video_${W}.mp4 -ss $A -t $D -i narration.wav -ss $A -t $D -i build/sfx.wav \
  -filter_complex "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,apad[v];[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,apad[s];[v][s]amix=inputs=2:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t $D -movflags +faststart $OUT
echo DONE $OUT
