#!/usr/bin/env python3
"""One beat grid for picture and sound: make it, fill it into a composition, lock music to it, or make music from it.

  beats.py grid --bpm 120 --bars 6 [--tail 2] [--offset 0] [--cue drop=1 --cue burst=3.2] --out grid.json
  beats.py fill --grid grid.json --template index.tpl.html --out index.html
  beats.py snap --grid grid.json --times T.json [--window 0.15] --out T-beat.json
  beats.py analyze track.wav [--out analysis.json]
  beats.py fit track.wav --card 12.0 [--hit last|drop|<sec>] [--tail 2] --out grid.json
  beats.py synth --grid grid.json [--key D --mode minor --groove half --seed 7] --out score.wav

Cue values are bar or bar.beat, 0-based ("3.2" = bar 3, beat 2), or seconds with an "s" suffix ("6.25s").
The grid always gets a "card" cue on the final downbeat: the end card and the music's last hit land there.
fill replaces {{GRID}} (JSON), {{duration}}, {{tail}}, {{bpm}}, {{cue:name}}, {{bar:N}} and {{beat:N}} in the template.
Name the template index.html.tpl: HyperFrames treats every root-level .html with a composition id as an entry.
Grooves for synth: four (four on the floor), half (half-time), broken, none (pulse only).
"""
import argparse
import json
import math
import re
import subprocess
import sys
import wave

import numpy as np

SR = 48000
NOTES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7,
         'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
SCALES = {'minor': [0, 2, 3, 5, 7, 8, 10], 'major': [0, 2, 4, 5, 7, 9, 11]}
PROGRESSIONS = {'minor': [0, 5, 2, 6], 'major': [0, 4, 5, 3]}
GROOVES = {
    'four': {'kick': [0, 4, 8, 12], 'snare': [4, 12], 'hat': [2, 6, 10, 14], 'ghost': [15]},
    'half': {'kick': [0, 7, 10], 'snare': [8], 'hat': [0, 2, 4, 6, 8, 10, 12, 14], 'ghost': [14]},
    'broken': {'kick': [0, 6, 10], 'snare': [4, 12], 'hat': list(range(16)), 'ghost': [7, 15]},
    'none': {'kick': [], 'snare': [], 'hat': [0, 2, 4, 6, 8, 10, 12, 14], 'ghost': []},
}


def r3(x):
    return round(float(x), 3)


def cue_time(value, g):
    value = str(value).strip()
    if value.endswith('s'):
        return float(value[:-1])
    bar, _, beat = value.partition('.')
    return g['offset'] + (int(bar) * g['beats_per_bar'] + (int(beat) if beat else 0)) * g['beat']


def make_grid(bpm, bars, offset=0.0, tail=2.0, beats_per_bar=4, cues=()):
    beat = 60.0 / bpm
    bar = beat * beats_per_bar
    g = {'bpm': bpm, 'beats_per_bar': beats_per_bar, 'beat': r3(beat), 'bar': r3(bar), 'offset': r3(offset),
         'bars': bars, 'tail': tail}
    card = offset + bars * bar
    g['beat_times'] = [r3(offset + i * beat) for i in range(bars * beats_per_bar + 1)]
    g['bar_times'] = [r3(offset + i * bar) for i in range(bars + 1)]
    g['cues'] = {}
    for c in cues:
        name, _, value = c.partition('=')
        g['cues'][name] = r3(cue_time(value, {**g, 'beat': beat}))
    g['cues']['card'] = r3(card)
    g['duration'] = r3(card + tail)
    return g


def fill(grid, template, out):
    text = open(template).read()
    text = text.replace('{{GRID}}', json.dumps({k: v for k, v in grid.items() if k not in ('beat_times',)}))
    text = text.replace('{{duration}}', f"{grid['duration']:.3f}").replace('{{bpm}}', str(grid['bpm']))
    text = text.replace('{{tail}}', f"{grid['duration'] - grid['cues']['card']:.3f}")

    def sub(m):
        kind, arg = m.group(1), m.group(2)
        if kind == 'cue':
            if arg not in grid['cues']:
                sys.exit(f'unknown cue {arg}; have {sorted(grid["cues"])}')
            return f"{grid['cues'][arg]:.3f}"
        n = float(arg)
        step = grid['bar'] if kind == 'bar' else grid['beat']
        return f"{grid['offset'] + n * step:.3f}"

    text = re.sub(r'\{\{(cue|bar|beat):([\w.\-]+)\}\}', sub, text)
    left = re.findall(r'\{\{[^}]+\}\}', text)
    if left:
        print('unfilled placeholders:', ', '.join(sorted(set(left))))
    open(out, 'w').write(text)
    print('wrote', out)


def snap(grid, times, window):
    beats = np.array(grid['beat_times'])
    out = {}
    for k, t in times.items():
        if not isinstance(t, (int, float)):
            out[k] = t
            continue
        i = int(np.argmin(np.abs(beats - t)))
        d = beats[i] - t
        out[k] = r3(beats[i]) if abs(d) <= window else t
        if abs(d) <= window and abs(d) > 0.001:
            print(f'  {k}: {t:.3f} -> {beats[i]:.3f} ({d * 1000:+.0f} ms)')
    return out


def load_mono(path, sr):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def analyze(path):
    sr, hop, n = 22050, 512, 2048
    x = load_mono(path, sr)
    if len(x) < n * 4:
        sys.exit('track too short to analyze')
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    mag = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    logm = np.log1p(100 * mag)
    flux = np.maximum(0, np.diff(logm, axis=0)).sum(1)
    low = np.maximum(0, np.diff(logm[:, freqs < 150], axis=0)).sum(1)
    env = flux - np.convolve(flux, np.ones(16) / 16, 'same')
    env = np.maximum(env, 0)
    fps = sr / hop

    ac = np.correlate(env - env.mean(), env - env.mean(), 'full')[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm_of = lambda lag: 60 * fps / lag
    cand = [(lag, ac[lag] * math.exp(-0.5 * (math.log2(bpm_of(lag) / 120) / 0.9) ** 2))
            for lag in lags[int(60 * fps / 185):int(60 * fps / 68) + 1]]
    lag = max(cand, key=lambda c: c[1])[0]
    lo, hi = max(1, lag - 1), lag + 1
    if hi < len(ac) and ac[lo] != ac[hi]:
        lag = lag + 0.5 * (ac[lo] - ac[hi]) / (ac[lo] - 2 * ac[lag] + ac[hi] + 1e-9)
    period = float(lag)
    bpm = 60 * fps / period

    def score(sig, phase, every=1):
        idx = np.round(np.arange(phase, len(sig) - 2, period * every)).astype(int)
        return sum(sig[max(0, i - 1):i + 2].max() for i in idx)

    phases = np.linspace(0, period, 48, endpoint=False)
    pulse = low / (low.max() + 1e-9) + 0.5 * env / (env.max() + 1e-9)
    phase = phases[int(np.argmax([score(pulse, p) for p in phases]))]
    accent = np.where(low > np.percentile(low, 98), low, 0)
    down = max(range(4), key=lambda j: score(accent, phase + j * period, 4))
    lat = (hop + n / 2) / sr
    first_down = (phase + down * period) / fps + lat
    beat = 60 / bpm
    while first_down - 4 * beat >= -0.05:
        first_down -= 4 * beat
    first_down = max(0.0, first_down)

    rms_hop = int(sr * beat * 4)
    starts = np.arange(int(first_down * sr), len(x) - rms_hop + 1, rms_hop)
    spec_low = []
    for s in starts:
        seg = x[s:s + rms_hop]
        f = np.abs(np.fft.rfft(seg))
        fr = np.fft.rfftfreq(len(seg), 1 / sr)
        spec_low.append(float(10 * np.log10((f[fr < 150] ** 2).sum() / len(seg) + 1e-12)))
    drop_bar = None
    for i in range(1, len(spec_low)):
        prev = np.mean(spec_low[max(0, i - 2):i])
        if spec_low[i] - prev >= 6 and spec_low[i] > np.max(spec_low) - 12:
            drop_bar = i
            break

    thr = env.mean() + 2.5 * env.std()
    hits, last = [], -1e9
    for i in range(1, len(env) - 1):
        if env[i] > thr and env[i] >= env[i - 1] and env[i] >= env[i + 1] and i / fps - last > 0.25:
            hits.append(r3(i / fps + lat))
            last = i / fps
    win = int(0.05 * sr)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))
    loud = np.where(20 * np.log10(rms + 1e-9) > -50)[0]
    end_audible = loud[-1] / sr if len(loud) else len(x) / sr
    lthr = np.percentile(low, 95)
    lows = [i / fps + lat for i in range(1, len(low) - 1)
            if low[i] > lthr and low[i] >= low[i - 1] and low[i] >= low[i + 1] and i / fps + lat < end_audible - 0.3]
    last_hit = lows[-1] if lows else (hits[-1] if hits else 0.0)
    return {'file': path, 'duration': r3(len(x) / sr), 'bpm': round(bpm, 2), 'beat': r3(beat),
            'first_downbeat': r3(first_down), 'drop_bar': drop_bar,
            'drop': r3(first_down + drop_bar * 4 * beat) if drop_bar is not None else None,
            'hits': hits[:200], 'last_hit': r3(last_hit), 'tail_after_last_hit': r3(end_audible - last_hit),
            'bar_low_db': [round(v, 1) for v in spec_low]}


def fit(a, card, hit, tail, at):
    h = a['last_hit'] if hit == 'last' else a['drop'] if hit == 'drop' else float(hit)
    if h is None:
        sys.exit('no drop found in the track; pass --hit <seconds>')
    target = card if at is None else at
    start = target - h
    ss, t = (-start, 0.0) if start < 0 else (0.0, start)
    beat = 60 / a['bpm']
    bar = 4 * beat
    d0 = a['first_downbeat'] + start
    offset = d0 % bar
    bars = max(1, int(round((card - offset) / bar)))
    g = make_grid(a['bpm'], bars, offset, tail)
    g['cues']['card'] = r3(card)
    if a['drop'] is not None:
        g['cues']['drop'] = r3(a['drop'] + start)
    g['duration'] = r3(card + tail)
    g['music'] = {'file': a['file'], 't': r3(t), 'ss': r3(ss)}
    left = a['duration'] - (card - start)
    if left < tail:
        print(f'warning: the track has only {left:.2f}s after the end card, tail asked {tail}s (abrupt stop)')
    if abs(card - offset - bars * bar) > 0.05:
        print(f'note: the end card sits {card - offset - bars * bar:+.3f}s off the nearest downbeat of the detected grid')
    return g


def lp(x, fc, order=2):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(np.fft.rfft(x) / np.sqrt(1 + (f / max(fc, 1)) ** (2 * order)), len(x))


def hp(x, fc, order=2):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(np.fft.rfft(x) / np.sqrt(1 + (max(fc, 1) / np.maximum(f, 1e-3)) ** (2 * order)), len(x))


def env_ar(n, attack, release_rate):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * release_rate)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(f, n, harmonics=10, detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, harmonics + 1):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * (1 + detune) * k * t + phase * k) / k
    return out


class Bus:
    def __init__(self, n):
        self.x = np.zeros((n, 2))

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if i >= len(self.x) or i + len(sig) <= 0:
            return
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(len(self.x), i + len(sig))
        left, right = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.x[i:j, 0] += sig[:j - i] * gain * left * 1.414
        self.x[i:j, 1] += sig[:j - i] * gain * right * 1.414


def synth(g, key, mode, groove, seed, out):
    rng = np.random.default_rng(seed)
    beat, bpb = g['beat'], g['beats_per_bar']
    step = beat / 4
    n = int((g['duration'] + 0.5) * SR)
    drums, bass, pad, keys, fx = (Bus(n) for _ in range(5))
    root = NOTES[key] + 36
    scale = SCALES[mode]
    prog = PROGRESSIONS[mode]
    card = g['cues']['card']
    drop = g['cues'].get('drop', g['offset'] + g['bar'] * min(2, g['bars'] // 3))
    hole = (drop - beat / 2, drop)
    hits = [v for k, v in g['cues'].items() if k.startswith('hit')]

    def deg(d, octave=0):
        return root + 12 * (octave + d // 7) + scale[d % 7]

    def noise(dur):
        return rng.standard_normal(int(dur * SR))

    kick_n = int(0.45 * SR)
    tk = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(45 + 85 * np.exp(-tk * 32)) / SR) * np.exp(-tk * 8)
    kick[:96] += noise(0.002)[:96] * np.linspace(0.6, 0, 96)
    snare = lp(hp(noise(0.25), 900), 7000) * env_ar(int(0.25 * SR), 0.001, 20) \
        + 0.5 * np.sin(2 * np.pi * 190 * np.arange(int(0.25 * SR)) / SR) * env_ar(int(0.25 * SR), 0.001, 28)
    hat = hp(noise(0.09), 7000, 4) * env_ar(int(0.09 * SR), 0.0005, 55)

    pat = GROOVES[groove]
    for b in range(g['bars']):
        t0 = g['offset'] + b * g['bar']
        after = t0 >= drop - 1e-6
        build = (not after) and t0 + g['bar'] > drop - 1e-6
        for s in range(16):
            t = t0 + s * step + rng.normal(0, 0.003)
            if hole[0] - 1e-6 <= t < hole[1] or t >= card - 1e-6:
                continue
            vel = 0.85 + 0.15 * rng.random()
            if s in pat['kick'] and (after or (s == 0 and not build)):
                drums.add(kick, t, 0.9 * vel)
            if after and s in pat['snare']:
                drums.add(snare, t, 0.45 * vel, 0.05)
            if after and s in pat['ghost']:
                drums.add(snare, t, 0.12 * vel, -0.05)
            if s in pat['hat'] and (after or s % 4 == 2):
                drums.add(hat, t, (0.18 if s % 4 == 2 else 0.1) * vel * (1 if after else 0.6), 0.3)
            if build and s >= 8:
                drums.add(snare, t, 0.06 + 0.25 * (s - 8) / 8, 0.0)

        chord = prog[b % len(prog)]
        notes = [deg(chord + i, 2) for i in (0, 2, 4)]
        dur = g['bar'] + 0.6
        m = int(dur * SR)
        cutoff = 900 if not after else 2600
        if build:
            cutoff = 900
        p = np.zeros(m)
        for k, note in enumerate(notes):
            for det in (-0.004, 0.004):
                p += saw(midi_hz(note), m, 12, det, phase=k + det * 100)
        shape = np.minimum(1, np.arange(m) / (0.35 * SR)) * np.clip((dur - np.arange(m) / SR) / 0.6, 0, 1)
        p = lp(p * shape, cutoff, 2)
        if build:
            sweep = np.linspace(0, 1, m) ** 2
            p = p * (1 - sweep) + lp(p, 4000) * sweep * 1.3
        pad.add(p * 0.05, t0, 1.0, -0.25)
        pad.add(p * 0.05, t0 + 0.012, 1.0, 0.25)

        bass_note = deg(chord, 0)
        for s in range(0, 16, 2 if after else 8):
            t = t0 + s * step
            if hole[0] - 1e-6 <= t < hole[1] or t >= card - 1e-6:
                continue
            ln = int((step * (2 if after else 6)) * SR)
            note = bass_note + (12 if after and s in (6, 14) else 0)
            b_sig = lp(saw(midi_hz(note), ln, 8), 500 if after else 300) * env_ar(ln, 0.004, 6)
            bass.add(b_sig, t, 0.35 if after else 0.22)

        if after:
            arp = [deg(chord + i, 3) for i in (0, 2, 4, 7)]
            for s in range(0, 16, 2):
                t = t0 + s * step
                if t >= card - 1e-6:
                    continue
                ln = int(0.5 * SR)
                f = midi_hz(arp[(s // 2) % 4])
                tt = np.arange(ln) / SR
                pl = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (6 + 5 * h)) / h for h in (1, 2, 3, 4))
                keys.add(pl, t + rng.normal(0, 0.003), 0.07 * (0.8 + 0.2 * rng.random()), 0.35 if s % 4 else -0.35)

    def impact(t, gain):
        ln = int(1.6 * SR)
        tt = np.arange(ln) / SR
        sub = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-tt * 12)) / SR) * np.exp(-tt * 2.6)
        body = lp(noise(1.6), 1800) * np.exp(-tt * 9) * 0.5
        fx.add(sub + body, t, gain)
        drums.add(kick, t, 0.9)

    impact(drop, 0.55)
    for h in hits:
        impact(h, 0.35)
    impact(card, 0.6)
    for k, interval in enumerate((7, 12)):
        ln = int(2.2 * SR)
        tt = np.arange(ln) / SR
        f = midi_hz(root + 36 + interval)
        bell = sum(np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) * a for r, d, a in ((1, 2.2, 1), (2.76, 4, 0.35), (5.4, 7, 0.15)))
        keys.add(bell, card + k * beat * 1.5, 0.11, -0.2 + 0.4 * k)
    tail_len = int((g['duration'] - card + 0.5) * SR)
    tonic = np.zeros(tail_len)
    for note in (deg(prog[0], 2), deg(prog[0] + 2, 2), deg(prog[0] + 4, 2)):
        tonic += saw(midi_hz(note), tail_len, 10)
    fade = np.minimum(1, np.arange(tail_len) / (0.08 * SR)) * np.exp(-np.arange(tail_len) / SR * 2.2)
    pad.add(lp(tonic * fade, 1400) * 0.05, card)

    ir_n = int(1.4 * SR)
    ti = np.arange(ir_n) / SR
    ir = lp(rng.standard_normal(ir_n), 5000) * np.exp(-ti / 0.32)
    ir /= np.sqrt((ir ** 2).sum())
    send = pad.x * 0.5 + keys.x * 0.8 + drums.x * 0.15
    size = 1 << int(math.ceil(math.log2(n + ir_n)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(send[:, c], size) * np.fft.rfft(ir, size), size)[:n] for c in (0, 1)], 1)
    mix = drums.x + bass.x + pad.x + keys.x + fx.x + wet * 0.35
    mix[:, :] = np.column_stack([hp(mix[:, 0], 30), hp(mix[:, 1], 30)])
    mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.4) * 0.84
    end = int(g['duration'] * SR)
    mix = mix[:end]
    k = int(0.02 * SR)
    mix[-k:] *= np.linspace(1, 0, k)[:, None]
    with wave.open(out, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())
    print(f"wrote {out}: {g['duration']:.2f}s, {g['bpm']} BPM, {key} {mode}, groove {groove}, drop {drop:.2f}s, card {card:.2f}s")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('grid', help='make a beat grid')
    s.add_argument('--bpm', type=float, required=True)
    s.add_argument('--bars', type=int, required=True, help='bars before the end card')
    s.add_argument('--offset', type=float, default=0.0, help='film time of bar 0 (default 0)')
    s.add_argument('--tail', type=float, default=2.0, help='seconds the end card holds after the final downbeat')
    s.add_argument('--beats-per-bar', type=int, default=4)
    s.add_argument('--cue', action='append', default=[], help='name=bar[.beat] or name=<sec>s')
    s.add_argument('--out', required=True)
    s = sub.add_parser('fill', help='fill grid placeholders into a composition template')
    s.add_argument('--grid', required=True)
    s.add_argument('--template', required=True)
    s.add_argument('--out', required=True)
    s = sub.add_parser('snap', help='snap word times to the nearest beat within a window')
    s.add_argument('--grid', required=True)
    s.add_argument('--times', required=True, help='T.json from word_times.py')
    s.add_argument('--window', type=float, default=0.15)
    s.add_argument('--out', required=True)
    s = sub.add_parser('analyze', help='tempo, first downbeat, drop, hits and last hit of a track')
    s.add_argument('track')
    s.add_argument('--out')
    s = sub.add_parser('fit', help='place a track so one of its hits lands on a film time')
    s.add_argument('track')
    s.add_argument('--card', type=float, required=True, help='film time of the end card (final hit)')
    s.add_argument('--hit', default='last', help='last, drop, or a time in the track (seconds)')
    s.add_argument('--at', type=float, help='film time for the chosen hit when it is not the card (e.g. --hit drop --at 2)')
    s.add_argument('--tail', type=float, default=2.0)
    s.add_argument('--out', required=True)
    s = sub.add_parser('synth', help='original music in code from the grid')
    s.add_argument('--grid', required=True)
    s.add_argument('--key', default='D', choices=sorted(NOTES))
    s.add_argument('--mode', default='minor', choices=sorted(SCALES))
    s.add_argument('--groove', default='half', choices=sorted(GROOVES))
    s.add_argument('--seed', type=int, default=7)
    s.add_argument('--out', required=True)
    a = p.parse_args()

    if a.cmd == 'grid':
        g = make_grid(a.bpm, a.bars, a.offset, a.tail, a.beats_per_bar, a.cue)
        json.dump(g, open(a.out, 'w'), indent=1)
        print(f"wrote {a.out}: {a.bars} bars at {a.bpm} BPM, bar {g['bar']}s, card {g['cues']['card']}s, duration {g['duration']}s")
        print('cues:', ', '.join(f'{k} {v}' for k, v in g['cues'].items()))
    elif a.cmd == 'fill':
        fill(json.load(open(a.grid)), a.template, a.out)
    elif a.cmd == 'snap':
        out = snap(json.load(open(a.grid)), json.load(open(a.times)), a.window)
        json.dump(out, open(a.out, 'w'), indent=1)
        print('wrote', a.out)
    elif a.cmd == 'analyze':
        res = analyze(a.track)
        brief = {k: v for k, v in res.items() if k not in ('hits', 'bar_low_db')}
        print(json.dumps(brief, indent=1))
        print(f"{len(res['hits'])} strong hits; low band per bar (dB): {res['bar_low_db'][:24]}")
        if a.out:
            json.dump(res, open(a.out, 'w'), indent=1)
    elif a.cmd == 'fit':
        g = fit(analyze(a.track), a.card, a.hit, a.tail, a.at)
        json.dump(g, open(a.out, 'w'), indent=1)
        m = g['music']
        print(f"wrote {a.out}: {g['bpm']} BPM, bar 0 at {g['offset']}s, card {g['cues']['card']}s")
        print(f'mix.py cue: {{"t": {m["t"]}, "f": "{m["file"]}", "ss": {m["ss"]}, "g": -8}}')
    elif a.cmd == 'synth':
        synth(json.load(open(a.grid)), a.key, a.mode, a.groove, a.seed, a.out)


if __name__ == '__main__':
    main()
