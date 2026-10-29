#!/usr/bin/env python3
"""Mix a voice-over and sound effects from a cue sheet, duck the effects under the voice, normalize loudness.

  mix.py cues.json out.wav [--lib ui=~/sfx/kenney --lib pads=~/sfx/mixkit]

cues.json:
  {"duration": 49.7,
   "voice": [{"file": "vo.wav", "t": 0.3, "gain": 0}],
   "sfx":   [{"t": 3.1, "f": "ui/click1.ogg", "g": -12, "p": 2, "rev": false, "ss": 0, "dur": null,
              "fade": 0.03, "lp": 7000}],
   "room": -48, "duck_db": 6, "target_lufs": -14}

t = seconds in the film, g = gain dB, p = pitch semitones, ss/dur = trim the source, lp = lowpass Hz,
room = pink room tone level (omit for none). "f" may start with a --lib name, e.g. "ui/click1.ogg".
Libraries can also come from SFX_LIBS="ui=/path,pads=/path".
"""
import argparse
import json
import os
import subprocess

import numpy as np

SR = 48000
LIB = {}
_cache = {}


def load(path, ss=0, dur=None, af=None):
    for k, v in LIB.items():
        if path.startswith(k + '/'):
            path = v + path[len(k):]
    if not os.path.exists(path):
        raise SystemExit(f'sound not found: {path} (register its folder with --lib name=path or SFX_LIBS)')
    key = (path, ss, dur, af)
    if key in _cache:
        return _cache[key]
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(dur)] if dur else []) + ['-i', path] + (['-af', af] if af else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2).copy()
    _cache[key] = a
    return a


def pitch(a, semis):
    if not semis:
        return a
    r = 2 ** (semis / 12)
    n = int(len(a) / r)
    idx = np.linspace(0, len(a) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], 1).astype(np.float32)


def place(bus, a, t, g):
    i = int(t * SR)
    if i < 0:
        a = a[-i:]; i = 0
    j = min(len(bus), i + len(a))
    if j > i:
        bus[i:j] += a[: j - i] * (10 ** (g / 20))


def room_tone(n, db):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'anoisesrc=color=pink:seed=7:r={SR}:d={n / SR + 0.1:.2f}',
                          '-af', 'lowpass=f=6000', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    b = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)[:n].copy()
    b = np.pad(b, ((0, n - len(b)), (0, 0)))
    return b / (np.sqrt(np.mean(b ** 2)) + 1e-9) * (10 ** (db / 20))


def main(cfg_path, out):
    cfg = json.load(open(cfg_path))
    n = int(cfg['duration'] * SR)
    voice = np.zeros((n, 2), np.float32); sfx = np.zeros((n, 2), np.float32)
    for v in cfg.get('voice', []):
        place(voice, load(v['file']), v['t'], v.get('gain', 0))
    for c in cfg.get('sfx', []):
        af = c.get('af') or (f"lowpass=f={c['lp']}" if c.get('lp') else None)
        a = load(c['f'], c.get('ss', 0), c.get('dur'), af)
        if c.get('rev'):
            a = a[::-1].copy()
        a = pitch(a, c.get('p', 0))
        fd = c.get('fade', 0.03)
        k = min(len(a), int(fd * SR))
        if k > 1:
            a[-k:] *= np.linspace(1, 0, k)[:, None]
            a[:min(len(a), 64)] *= np.linspace(0, 1, min(len(a), 64))[:, None]
        place(sfx, a, c['t'], c.get('g', -10))
    if cfg.get('room') is not None:
        sfx += room_tone(n, cfg['room'])
    duck = cfg.get('duck_db', 6)
    if duck and voice.any():
        env = np.abs(voice).max(1)
        win = int(0.03 * SR)
        env = np.convolve(env, np.ones(win) / win, 'same')
        on = (env > 0.02).astype(np.float32)
        g = np.empty_like(on); cur = 0.0
        a_k = 1 - np.exp(-1 / (0.02 * SR)); r_k = 1 - np.exp(-1 / (0.25 * SR))
        for i in range(len(on)):
            k = a_k if on[i] > cur else r_k
            cur += (on[i] - cur) * k
            g[i] = cur
        sfx *= (1 - g * (1 - 10 ** (-duck / 20)))[:, None]
    mix = voice + sfx
    tmp = out + '.raw.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.astype(np.float32).tobytes(), check=True)
    lufs = cfg.get('target_lufs', -14)
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', f'loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', f"loudnorm=I={lufs}:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000", '-ar', '48000', out], check=True)
    os.remove(tmp)
    print('mixed', out, 'input', js['input_i'], 'LUFS')


def libs(pairs):
    for pair in pairs:
        name, _, path = pair.partition('=')
        LIB[name.strip()] = os.path.expanduser(path.strip())


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('cues')
    p.add_argument('out')
    p.add_argument('--lib', action='append', default=[], help='name=path of a sound library folder')
    a = p.parse_args()
    libs([x for x in os.environ.get('SFX_LIBS', '').split(',') if '=' in x] + a.lib)
    main(a.cues, a.out)
