"""Example: turn the tour editor's events.json into a cue sheet and mix it.

  python3 mix_cues.py build/events.json build/cues.json mix.wav [intro_offset] [outro_tail]

events.json (from scripts/tour_edit.py) lists every voice clip and every Director sfx mark
(click, cover, uncover, chip, caption, done). Each kind maps to one family of sounds below.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(sys.argv[1]))
cues_path, out = sys.argv[2], sys.argv[3]
OFF = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
TAIL = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
clicks = ['brag/ui/click1.ogg', 'brag/ui/click2.ogg', 'brag/ui/click3.ogg', 'brag/ui/mouseclick1.ogg']
cues, k = [], 0
for s in ev['sfx']:
    t = s['t'] + OFF
    kind = s['kind']
    k += 1
    if kind == 'click':
        cues.append(dict(t=t, f=clicks[k % 4], g=-15, p=(k % 3) - 1))
    elif kind == 'cover':
        cues.append(dict(t=t - 0.05, f='lib/mixkit/1492.wav', g=-14, lp=6500, p=(k % 3) - 1))
        cues.append(dict(t=t + 0.75, f='brag/impact/impactSoft_medium_00%d.ogg' % (k % 5), g=-17))
    elif kind == 'uncover':
        cues.append(dict(t=t, f='lib/bsb/whoosh-179%d.wav' % (5 + k % 2), g=-17, lp=6500))
    elif kind == 'chip':
        cues.append(dict(t=t + 0.05, f='brag/interface/drop_002.ogg', g=-19, p=k % 4))
    elif kind == 'caption':
        cues.append(dict(t=t, f='lib/mixkit/166.wav', g=-22, lp=6000))
    elif kind == 'done':
        cues.append(dict(t=t, f='lib/kenney_interface-sounds/Audio/confirmation_002.ogg', g=-15))
voice = [dict(file=v['file'], t=v['t'] + OFF, gain=0) for v in ev['voice']]
if OFF:
    cues += [dict(t=0.05, f='brag/impact/impactBell_heavy_000.ogg', g=-10), dict(t=0.05, f='lib/kenney_sci-fi-sounds/Audio/lowFrequency_explosion_001.ogg', g=-13), dict(t=0.6, f='lib/bsb/whoosh-1795.wav', g=-15)]
total = ev['duration'] + OFF + TAIL
if TAIL:
    cues += [dict(t=ev['duration'] + OFF + 0.3, f='brag/impact/impactBell_heavy_004.ogg', g=-9)]
cfg = dict(duration=total, voice=voice, sfx=cues, room=-50, duck_db=6, target_lufs=-15)
json.dump(cfg, open(cues_path, 'w'), indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '../../scripts/mix.py'), cues_path, out], check=True)
