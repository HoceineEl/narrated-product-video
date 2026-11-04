#!/usr/bin/env python3
"""Make a small paper foley kit in code (no sample files, no licences): pops, slides, rips, tape, stamps.

  paper_sfx.py --out-dir sfx/paper [--seed 3] [--variants 3]

Writes 48 kHz mono WAVs: pop (a card lands), pop3 (three quick lands), slide (paper over paper),
rip (a tear), tape (a strip peeled and slapped), stamp (rubber stamp), flip (page turn), swish (soft air
for a hard cut), drop (a small pile lands), scribble (a marker circle). Each sound gets --variants takes
with small pitch and timing changes, named pop-1.wav, pop-2.wav, ...; use them in mix.py cue sheets
(--lib paper=sfx/paper, then "f": "paper/pop-2.wav"). Peaks are normalised to -3 dBFS.
"""
import argparse
import os
import wave

import numpy as np

SR = 48000


def shape(x, fc_lo=None, fc_hi=None):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = np.ones_like(f)
    if fc_hi:
        h /= np.sqrt(1 + (f / fc_hi) ** 4)
    if fc_lo:
        h /= np.sqrt(1 + (fc_lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(np.fft.rfft(x) * h, len(x))


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * decay)


class Kit:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)

    def noise(self, dur):
        return self.rng.standard_normal(int(dur * SR))

    def tap(self, dur=0.09, lo=300, hi=3500, decay=60, body=180):
        n = int(dur * SR)
        t = np.arange(n) / SR
        thud = np.sin(2 * np.pi * body * t * (1 - 0.3 * t / dur)) * env(n, 0.0008, decay * 0.8) * 0.6
        return shape(self.noise(dur), lo, hi) * env(n, 0.0006, decay) + thud

    def pop(self, k):
        return self.tap(0.12, 250, 3200 + 300 * k, 55, 170 + 12 * k)

    def pop3(self, k):
        out = np.zeros(int(0.42 * SR))
        for i, at in enumerate((0.0, 0.11 + 0.01 * k, 0.24 + 0.015 * k)):
            s = self.tap(0.12, 250, 3000 + 400 * i, 55, 160 + 20 * i)
            j = int(at * SR)
            out[j:j + len(s)] += s[:len(out) - j] * (1 - 0.12 * i)
        return out

    def slide(self, k):
        dur = 0.38 + 0.05 * k
        n = int(dur * SR)
        t = np.linspace(0, 1, n)
        grit = shape(self.noise(dur), 900, 6500)
        flutter = 1 + 0.35 * np.sin(2 * np.pi * (18 + 4 * k) * t * dur)
        return grit * np.sin(np.pi * t) ** 1.5 * flutter * 0.7

    def rip(self, k):
        dur = 0.55 + 0.08 * k
        n = int(dur * SR)
        out = shape(self.noise(dur), 1200, 9000) * np.linspace(0.6, 1, n) * 0.25
        pos = 0
        while pos < n - 400:
            step = int(self.rng.uniform(0.004, 0.018) * SR)
            g = self.rng.uniform(0.4, 1.0)
            burst = shape(self.noise(0.008), 1500, 8000) * env(int(0.008 * SR), 0.0002, 500) * g
            out[pos:pos + len(burst)] += burst[:n - pos]
            pos += step
        return out * np.minimum(1, (n - np.arange(n)) / (0.05 * SR))

    def tape(self, k):
        peel = self.rip(k)[: int(0.3 * SR)] * np.linspace(0.3, 1, int(0.3 * SR)) * 0.8
        slap = self.tap(0.15, 120, 2500, 40, 120)
        out = np.zeros(len(peel) + int(0.05 * SR) + len(slap))
        out[:len(peel)] += peel
        out[len(peel) + int(0.05 * SR):] += slap * 1.1
        return out

    def stamp(self, k):
        body = self.tap(0.22, 60, 1800, 28, 95 + 8 * k) * 1.2
        n = len(body)
        squeak = np.sin(2 * np.pi * (900 + 60 * k) * np.arange(n) / SR) * env(n, 0.03, 30) * 0.05
        return body + squeak

    def flip(self, k):
        dur = 0.5
        n = int(dur * SR)
        t = np.linspace(0, 1, n)
        air = shape(self.noise(dur), 300, 4500) * np.sin(np.pi * t) ** 2 * 0.5
        snap = np.zeros(n)
        s = self.tap(0.06, 800, 6000, 120, 300)
        j = int((0.36 + 0.02 * k) * SR)
        snap[j:j + len(s)] = s[:n - j] * 0.8
        return air + snap

    def swish(self, k):
        dur = 0.28 + 0.03 * k
        n = int(dur * SR)
        t = np.linspace(0, 1, n)
        return shape(self.noise(dur), 400, 3000 + 600 * k) * (t ** 1.5) * np.exp(-((t - 0.75) ** 2) / 0.02) * 0.9

    def drop(self, k):
        out = np.zeros(int(0.5 * SR))
        for i in range(5 + k):
            s = self.tap(0.1, 200, 3000, 60, 140 + 25 * self.rng.random())
            j = int(self.rng.uniform(0, 0.2) * SR)
            out[j:j + len(s)] += s * self.rng.uniform(0.4, 1)
        return out

    def scribble(self, k):
        dur = 0.32
        n = int(dur * SR)
        t = np.arange(n) / SR
        strokes = 0.5 + 0.5 * np.sin(2 * np.pi * (11 + k) * t) ** 2
        return shape(self.noise(dur), 2000, 9000) * strokes * np.sin(np.pi * t / dur) * 0.6


def write(path, x):
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (-3 / 20)
    fade = min(len(x), int(0.004 * SR))
    x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out-dir', required=True)
    p.add_argument('--seed', type=int, default=3)
    p.add_argument('--variants', type=int, default=3)
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    kit = Kit(a.seed)
    names = ['pop', 'pop3', 'slide', 'rip', 'tape', 'stamp', 'flip', 'swish', 'drop', 'scribble']
    for name in names:
        for k in range(a.variants):
            write(os.path.join(a.out_dir, f'{name}-{k + 1}.wav'), getattr(kit, name)(k))
    print(f'wrote {len(names) * a.variants} sounds to {a.out_dir}: {", ".join(names)}')


if __name__ == '__main__':
    main()
