"""Cue-sheet audio mixer: python3 mix.py cues.json out.wav
cues.json = {"duration": s, "sr": 48000, "voice": [{"file":..., "t":..., "gain":dB}],
             "sfx": [{"t":s, "f":path, "g":dB, "p":semitones, "rev":bool, "ss":start, "dur":s, "fade":s}],
             "room": dB, "duck_db": 6, "target_lufs": -14}"""
import json, subprocess, sys, os
import numpy as np
SR = 48000
LIB = {
    'brag': os.path.expanduser('~/.claude/plugins/cache/brag/brag/0.2.2/skills/brag/assets/sfx'),
    'lib': os.path.join(os.environ.get('VIDEO_ROOT', os.path.expanduser('~/Downloads/my-app-videos')), 'sfx-lib'),
}
_cache = {}
def load(path, ss=0, dur=None, af=None):
    for k, v in LIB.items():
        if path.startswith(k + '/'):
            path = v + path[len(k):]
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
        rng = np.random.default_rng(7)
        w = rng.standard_normal((n, 2)).astype(np.float32)
        # pink-ish: cumulative leaky integration then lowpass
        b = np.zeros_like(w); acc = np.zeros(2, np.float32)
        alpha = 0.985
        for s0 in range(0, n, 48000):
            seg = w[s0:s0 + 48000]
            out_seg = np.empty_like(seg)
            for i in range(len(seg)):
                acc = alpha * acc + (1 - alpha) * seg[i]
                out_seg[i] = acc
            b[s0:s0 + 48000] = out_seg
        b /= (np.sqrt(np.mean(b ** 2)) + 1e-9)
        sfx += b * (10 ** (cfg['room'] / 20))
    # sidechain duck sfx under voice
    duck = cfg.get('duck_db', 6)
    if duck and voice.any():
        env = np.abs(voice).max(1)
        win = int(0.03 * SR)
        env = np.convolve(env, np.ones(win) / win, 'same')
        on = (env > 0.02).astype(np.float32)
        # attack 20ms, release 250ms smoothing
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
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
