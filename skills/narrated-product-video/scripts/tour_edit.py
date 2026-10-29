#!/usr/bin/env python3
"""Assemble a narrated app tour from Playwright takes and per-beat voice clips.

  tour_edit.py --takes takes/ --beats beats/ --config tour.json --out-dir build/

Each take is takes/<name>.mkv plus takes/<name>.json (the Director's timestamped marks: sync, ready,
beat:<id>, end:<id>, sfx:<kind>, out). tour.json:
  {"order": ["tour-intro", "tour-clients", ...],      takes in film order (required)
   "end_mark": {"tour-bulk": "end:c07b"},             cut a take at a mark instead of "out"
   "end_time": {"tour-validate": 48.3},               or at a fixed time in the take
   "speed_cap": {"c04b": 4.0},                        max fast-forward for a beat whose action must be seen
   "zoom": {"c04b": [1.55, 1080, 420]},               zoom factor and centre (1920x1080 px) during a beat
   "no_trim_intro": ["tour-intro", "tour-outro"]}     takes that keep their opening cover

Per take: find the magenta sync flash, start just after the chapter cover lifts, place each beat's voice
at its mark + 0.12 s, freeze-pad when the voice is longer than the action, fast-forward idle tails,
gaps and blank frames, then apply zooms as an output-time zoompan pass.
Writes <out-dir>/<take>.mp4, tour-silent.mp4 and events.json ({voice, sfx, duration}) for the mix.
"""
import argparse
import json
import os
import subprocess

import numpy as np

CFG = {}
TAKES = ''
def zexpr(wins):
    if not wins:
        return None
    def ramp(a, b):
        u = f'clip((T-{a:.3f})/0.7,0,1)'
        v = f'clip(({b:.3f}-T)/0.7,0,1)'
        return f'({u}*{u}*(3-2*{u}))*({v}*{v}*(3-2*{v}))'
    z = '1' + ''.join(f'+{Z - 1:.3f}*{ramp(a, b)}' for a, b, Z, cx, cy in wins)
    def pick(idx):
        e = '960' if idx == 3 else '540'
        for a, b, Z, cx, cy in reversed(wins):
            val = cx if idx == 3 else cy
            e = f'if(between(T,{a - 0.8:.3f},{b + 0.8:.3f}),{val},{e})'
        return e
    return z, pick(3), pick(4)

FPS = 30
LEAD = 0.12
TAIL = 0.25
GAP = 0.4


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)


def flash_time(video, search=40):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-t', str(search), '-i', video, '-vf', f'fps={FPS},crop=16:16:2:2,scale=1:1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    px = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(int)
    hits = [i for i, (r, g, b) in enumerate(px) if r > 200 and b > 200 and g < 80]
    if not hits:
        raise SystemExit(f'no sync flash in {video}')
    return hits[0] / FPS


def blank_runs(video, off, a, b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a + off:.3f}', '-to', f'{b + off:.3f}', '-i', video, '-vf', 'fps=10,scale=160:90,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    std = np.frombuffer(raw, np.uint8).reshape(-1, 160 * 90).std(1)
    runs, start = [], None
    for i, v in enumerate(list(std) + [99]):
        if v < 2 and start is None:
            start = i
        elif v >= 2 and start is not None:
            if i - start >= 3:
                runs.append((a + start / 10 + 0.05, a + i / 10 - 0.05))
            start = None
    return runs


def first(marks, label, after=-1):
    for m in marks:
        if m['label'] == label and m['t'] > after:
            return m['t']
    return None


def build(beats_dir, work):
    os.makedirs(work, exist_ok=True)
    segs, voice, sfx = [], [], []
    cursor = 0.0
    ORDER, END, END_T = CFG['order'], CFG.get('end_mark', {}), CFG.get('end_time', {})
    SPEED_CAP, ZOOM = CFG.get('speed_cap', {}), CFG.get('zoom', {})
    keep_intro = set(CFG.get('no_trim_intro', []))
    for name in ORDER:
        video = f'{TAKES}/{name}.mkv'
        if not os.path.exists(video):
            print('skip missing', name)
            continue
        marks = json.load(open(f'{TAKES}/{name}.json'))
        sync = first(marks, 'sync')
        off = flash_time(video) - sync
        ready = first(marks, 'ready')
        cover = first(marks, 'sfx:cover', ready)
        fb = min([x['t'] for x in marks if x['label'].startswith('beat:')] or [ready + 1])
        unc = max([x['t'] for x in marks if x['label'] == 'sfx:uncover' and ready <= x['t'] <= fb] or [None], key=lambda v: v or 0)
        start_m = unc + 0.45 if (unc is not None and name not in keep_intro) else ready + 0.25
        end_m = END_T[name] if name in END_T else (first(marks, END[name]) + 0.3) if name in END else first(marks, 'out') + 0.5
        le = [x['t'] for x in marks if x['label'].startswith('end:') and x['t'] <= end_m + 0.01]
        if le and name not in END_T:
            end_m = min(end_m, max(le) + 0.25)
        ops_f, ops_s, zwins = [], [], []
        for m in marks:
            if not m['label'].startswith('beat:'):
                continue
            bid = m['label'][5:]
            e = first(marks, f'end:{bid}', m['t'])
            if e is None or m['t'] > end_m - 0.6:
                continue
            e = min(e, end_m)
            wav = f'{beats_dir}/{bid}.wav'
            if not os.path.exists(wav):
                print('  no audio for', bid)
                continue
            d = dur(wav)
            voice.append({'mark': m['t'], 'file': wav, 'take': name})
            room = e - m['t']
            need = LEAD + d + 0.35 - room
            if need > 0:
                ops_f.append((e, need))
            else:
                cap = SPEED_CAP.get(bid, 24.0)
                a, b = m['t'] + LEAD + d + 0.15, e
                if cap > 1 and b - a > TAIL + 0.1:
                    ops_s.append((a, b, min(cap, (b - a) / TAIL)))
            if bid in ZOOM:
                Z, cx, cy = ZOOM[bid]
                zwins.append((m['t'] + 0.4, e - 0.2, Z, cx, cy))
        beat_marks = sorted(x['t'] for x in marks if x['label'].startswith('beat:') and start_m <= x['t'] <= end_m)
        ends = sorted(first(marks, f"end:{x['label'][5:]}", x['t']) or x['t'] for x in marks if x['label'].startswith('beat:'))
        for bm in beat_marks:
            prev = max([x for x in ends if x <= bm] + [start_m])
            if bm - prev > GAP + 0.2:
                ops_s.append((prev, bm, min(8.0, (bm - prev) / GAP)))
        for x, y in blank_runs(video, off, start_m, end_m):
            ops_s[:] = [o for o in ops_s if o[1] <= x or o[0] >= y]
            ops_s.append((x, y, max(1.0, (y - x) / 0.1)))
        bps = sorted({start_m, end_m, *[f[0] for f in ops_f], *[x for o in ops_s for x in o[:2]]})
        pieces = []
        for a, b in zip(bps[:-1], bps[1:]):
            sp = next((o[2] for o in ops_s if o[0] <= a and b <= o[1]), 1.0)
            pad = next((f[1] for f in ops_f if abs(f[0] - b) < 1e-6), 0.0)
            pieces.append((a, b, sp, pad))
        fc, parts = [], []
        for i, (a, b, sp, pad) in enumerate(pieces):
            fc.append(f'[0:v]trim=start={a + off:.3f}:end={b + off:.3f},setpts=(PTS-STARTPTS)/{sp},fps={FPS}' + (f',tpad=stop_mode=clone:stop_duration={pad:.3f}' if pad else '') + f'[v{i}]')
            parts.append(f'[v{i}]')
        fc.append(''.join(parts) + f'concat=n={len(parts)}:v=1:a=0,format=yuv420p[o]')
        seg = f'{work}/{name}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-filter_complex', ';'.join(fc), '-map', '[o]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-r', str(FPS), seg], check=True)

        def tmap(t, pieces=pieces, base=cursor):
            acc = base
            for a, b, sp, pad in pieces:
                if t < a:
                    break
                if t <= b:
                    return acc + (t - a) / sp
                acc += (b - a) / sp + pad
            return acc

        ze = zexpr([(tmap(a, base=0.0), tmap(b, base=0.0), Z, cx, cy) for a, b, Z, cx, cy in zwins])
        if ze:
            z, x, y = (q.replace('T', 'it') for q in ze)
            raw = seg.replace('.mp4', '-raw.mp4')
            os.replace(seg, raw)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-vf', f"zoompan=z='{z}':x='clip(({x})-iw/zoom/2,0,iw-iw/zoom)':y='clip(({y})-ih/zoom/2,0,ih-ih/zoom)':d=1:s=1920x1080:fps={FPS},format=yuv420p", '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-r', str(FPS), seg], check=True)
            os.remove(raw)

        for v in [v for v in voice if v['take'] == name]:
            v['t'] = tmap(v['mark']) + LEAD
        for m in marks:
            lab = m['label']
            if not lab.startswith('sfx:') or m['t'] < start_m or m['t'] > end_m:
                continue
            sfx.append({'kind': lab[4:], 't': tmap(m['t'])})
        freezes = ops_f
        d_seg = dur(seg)
        segs.append(seg)
        print(f'{name}: {d_seg:.1f}s, offset {off:.2f}, freezes {[round(f[1], 2) for f in freezes]}, speedups {[(round(o[1]-o[0],1), round(o[2],1)) for o in ops_s]}')
        cursor += d_seg
    vs = sorted(voice, key=lambda v: v['t'])
    for a, b in zip(vs, vs[1:]):
        b['t'] = max(b['t'], a['t'] + dur(a['file']) + 0.12)
    lst = f'{work}/list.txt'
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    silent = f'{work}/tour-silent.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', silent], check=True)
    json.dump({'voice': voice, 'sfx': sfx, 'duration': cursor}, open(f'{work}/events.json', 'w'), indent=1)
    print('total', round(cursor, 1), 's ->', silent)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--takes', required=True)
    p.add_argument('--beats', required=True)
    p.add_argument('--config', required=True)
    p.add_argument('--out-dir', required=True)
    a = p.parse_args()
    CFG.update(json.load(open(a.config)))
    TAKES = os.path.abspath(a.takes)
    build(os.path.abspath(a.beats), os.path.abspath(a.out_dir))
