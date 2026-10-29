#!/bin/zsh
# tour_final.sh [scratch]  -> master g2/g3, Parakeet-align all groups, edit, mix, mux
set -e
R=${VIDEO_ROOT:-~/Downloads/my-app-videos}; V=$R/tour/vo
SRC=$V; [ "$1" = scratch ] && SRC=$V/scratch
for g in g0 g1 g2 g3 g5; do [ -s $V/beats-p/c00a.wav ] && [ "$SKIPALIGN" = 1 ] && continue;
  [ $g = g1 -a "$1" = scratch ] && continue
  [ -s $SRC/$g-m.wav -a "$1" = scratch ] || ffmpeg -v error -y -i $SRC/$g.wav -af "highpass=f=70,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 $SRC/$g-m.wav
done
for g in g0 g1 g2 g3 g5; do [ -s $V/beats-p/c00a.wav ] && [ "$SKIPALIGN" = 1 ] && continue;
  A=$SRC/$g-m.wav; [ $g = g1 -a "$1" = scratch ] && A=$V/g1-m-old.wav
  D=$R/tour/txp-$g$1; mkdir -p $D
  [ -s $D/transcript.json ] || (cd $D && cp $A in.wav && npx hyperframes transcribe in.wav -e parakeet -l fr >/dev/null 2>&1 && rm in.wav)
  python3 $R/tools/align.py $R/tour/script.json $g $A $D/transcript.json $V/beats-p$1 > $V/$g.beats$1.json
done
cd $R
python3 tools/tour_edit.py tour/vo/beats-p$1 | grep -E 'freezes|total'
cd tour/build && ffmpeg -v error -y -f concat -safe 0 -i full.txt -c copy tour-full-silent.mp4 && cd $R
python3 tools/tour_mix.py tour/vo/beats-p$1 tour/build/tour-mix.wav 2.4 5.19 | tail -1
OUT=$R/app-tour.mp4; [ "$1" = scratch ] && OUT=$R/tour/build/tour-preview$1.mp4
ffmpeg -v error -y -i tour/build/tour-full-silent.mp4 -i tour/build/tour-mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest $OUT
echo DONE $OUT
