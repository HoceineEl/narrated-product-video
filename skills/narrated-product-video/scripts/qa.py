#!/usr/bin/env python3
"""Check a finished video before anyone watches it.

  qa.py --video final.mp4 [--script script.json] [--transcript final-words.json] [--lang en] [--cues cues.json]

Picture (always):
  - frame 0 is a finished picture (it is the thumbnail): not flat, not far emptier than the rest of the film
  - frozen time: longest still stretch and total still time outside the end card (--end-card, --max-still)
  - blank frames: runs of flat frames (white or black flashes)
  - double cuts: two cuts closer than --min-shot (a cut, then another a frame or two later)
  - pops: single frames unlike both neighbours (warning)
Audio (when the file has sound):
  - dead air: stretches below -50 dBFS longer than --max-silence
  - abrupt stops: the film ending at full level, or sound falling 30 dB in 10 ms mid-film (warning)
  - loudness and true peak, then true peak again after an AAC re-encode (platforms re-encode; AAC overshoots)
  - with --cues (mix.py cue sheet, or a list of {t, label}): each sound's level over the bed around it (warning)
Voice (with --script): every sentence is heard once, in order; pauses between words stay under --max-gap.
Without --transcript, the voice check runs `npx hyperframes transcribe` (Parakeet) on the audio.
The script may be script.json (chapters/beats) or a plain .txt file. Exits 1 when a hard check fails.
"""
import argparse
import difflib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import unicodedata

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from master import measure  # noqa: E402

ONES = ('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen '
        'seventeen eighteen nineteen').split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()
FW, FH = 128, 72


def spell(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10 - 2] + (ONES[n % 10] if n % 10 else '')
    if n < 1000:
        return ONES[n // 100] + 'hundred' + (spell(n % 100) if n % 100 else '')
    return str(n)


def letters(text):
    t = unicodedata.normalize('NFKD', text.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'\d+', lambda m: spell(int(m.group())), t)
    return re.sub(r'[^a-z0-9؀-ۿ]', '', t)


def sentences(path):
    if path.endswith('.json'):
        data = json.load(open(path))
        text = ' '.join(b['text'] for ch in data['chapters'] for b in ch['beats'])
    else:
        text = open(path).read()
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if letters(s)]


def transcribe(video, lang):
    work = tempfile.mkdtemp(prefix='qa-')
    wav = os.path.join(work, 'mix.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
    subprocess.run(['npx', '--yes', 'hyperframes', 'transcribe', 'mix.wav', '-e', 'parakeet', '-l', lang],
                   cwd=work, check=True, capture_output=True)
    found = [f for f in os.listdir(work) if f.endswith('.json')]
    if not found:
        sys.exit('transcription produced no JSON')
    return os.path.join(work, found[0])


def probe(video):
    out = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,r_frame_rate:format=duration',
                                     '-of', 'json', video], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in out['streams'] if s['codec_type'] == 'video')
    num, den = (int(x) for x in v['r_frame_rate'].split('/'))
    return min(60.0, num / den), float(out['format']['duration']), any(s['codec_type'] == 'audio' for s in out['streams'])


def frames(video, fps):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps={fps},scale={FW}:{FH},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8)[:len(raw) // (FW * FH) * FW * FH].reshape(-1, FH, FW)


def runs(mask, min_len):
    out, start = [], None
    for i, m in enumerate(list(mask) + [False]):
        if m and start is None:
            start = i
        elif not m and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    return out


def picture_checks(video, a, fails, warns):
    fps, dur, _ = probe(video)
    f = frames(video, fps)
    n = len(f)
    if n < 3:
        fails.append('video has fewer than 3 frames')
        return
    fl = f.astype(np.int16)
    d = np.abs(np.diff(fl, axis=0)).mean(axis=(1, 2))
    std = f.reshape(n, -1).std(1)
    detail = np.abs(np.diff(fl, axis=2)).mean(axis=(1, 2)) + np.abs(np.diff(fl, axis=1)).mean(axis=(1, 2))

    med = float(np.median(detail))
    if std[0] < 6:
        fails.append('frame 0 is flat (blank or a solid colour): the thumbnail shows nothing')
    elif detail[0] < 0.35 * med:
        warns.append(f'frame 0 is not a finished picture (detail {detail[0]:.1f} vs film median {med:.1f}): it is the thumbnail')
    print(f'frame 0: contrast {std[0]:.1f}, detail {detail[0]:.1f} (film median {med:.1f})')

    blank = runs(std < 2, max(1, int(0.3 * fps)))
    print('blank frames:', ', '.join(f'{x / fps:.1f}-{y / fps:.1f}s' for x, y in blank) or 'none')
    fails += [f'blank frames {x / fps:.1f}-{y / fps:.1f}s' for x, y in blank]

    end_card = max(0.0, dur - a.end_card)
    still = d < a.still_threshold
    stills = [(x + 1, y + 1) for x, y in runs(still, max(1, int(0.2 * fps)))]
    outside = [(x / fps, min(y / fps, end_card)) for x, y in stills if x / fps < end_card]
    outside = [(x, y) for x, y in outside if y - x > 0]
    frozen = sum(y - x for x, y in outside)
    longest = max(outside, key=lambda r: r[1] - r[0], default=(0.0, 0.0))
    print(f'frozen time: {frozen:.1f}s of {end_card:.1f}s before the end card ({100 * frozen / max(end_card, 1e-9):.0f}%), '
          f'longest {longest[1] - longest[0]:.1f}s at {longest[0]:.1f}s')
    for x, y in outside:
        if y - x > a.max_still:
            fails.append(f'picture frozen {y - x:.1f}s at {x:.1f}-{y:.1f}s (max {a.max_still}s outside the end card)')
    if end_card > 0 and frozen / end_card > a.max_still_ratio:
        warns.append(f'{100 * frozen / end_card:.0f}% of the film is frozen before the end card (aim under {100 * a.max_still_ratio:.0f}%)')

    win = int(max(3, fps // 2))
    local = np.array([np.median(d[max(0, i - win):i + win + 1]) for i in range(len(d))])
    big = d > np.maximum(12, 4 * local)
    dp = np.concatenate([[0], d[:-1]])
    dn = np.concatenate([d[1:], [0]])
    dn2 = np.concatenate([d[2:], [0, 0]])
    spike = big & (d > 3 * np.maximum(dp, dn))
    twin = big & np.roll(big, -1) & (d > 3 * np.maximum(dp, dn2)) & (dn > 3 * np.maximum(dp, dn2))
    cuts = sorted({i + 1 for i in np.where(spike)[0]} | {j for i in np.where(twin)[0] for j in (i + 1, i + 2)})
    pops = []
    for i in range(1, n - 1):
        if d[i - 1] > 12 and d[i] > 12:
            back = np.abs(fl[i + 1] - fl[i - 1]).mean()
            if back < 0.25 * min(d[i - 1], d[i]):
                pops.append(i)
    real = [c for c in cuts if c not in pops and c - 1 not in pops]
    doubles = [(x, y) for x, y in zip(real, real[1:]) if (y - x) / fps < a.min_shot]
    print(f'cuts: {len(real)}', '| double cuts: ' + (', '.join(f'{x / fps:.2f}s+{(y - x)}f' for x, y in doubles) or 'none'))
    fails += [f'double cut at {x / fps:.2f}s: a second cut {y - x} frame(s) later' for x, y in doubles]
    if pops:
        warns.append('single-frame pops at ' + ', '.join(f'{p / fps:.2f}s' for p in pops[:8]))
    if len(real) >= 4:
        shots = np.diff([0] + real + [n]) / fps
        cv = float(np.std(shots) / np.mean(shots))
        print(f'shot lengths: {len(shots)} shots, {shots.min():.2f}-{shots.max():.2f}s, variation {cv:.2f}')
        if cv < 0.25:
            warns.append(f'shot lengths vary little (variation {cv:.2f}, aim 0.25+): the cut reads as a metronome')


def audio(video, sr=48000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def level_db(x, sr, win=0.02, hop=0.01):
    w, h = int(win * sr), int(hop * sr)
    if len(x) < w:
        return np.array([-120.0])
    sq = np.convolve(x.astype(np.float64) ** 2, np.ones(w) / w, 'valid')[::h]
    return 10 * np.log10(sq + 1e-12)


def aac_peak(video):
    work = tempfile.mkdtemp(prefix='qa-aac-')
    m4a = os.path.join(work, 'check.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vn', '-c:a', 'aac', '-b:a', '128k', m4a], check=True)
    return measure(m4a)[1]


def cue_list(path):
    data = json.load(open(path))
    items = data.get('sfx', []) if isinstance(data, dict) else data
    return [(float(c['t']), c.get('label') or os.path.basename(str(c.get('f', 'cue')))) for c in items]


def audio_checks(video, a, fails, warns):
    sr = 48000
    x = audio(video, sr)
    if not len(x) or np.abs(x).max() < 1e-5:
        fails.append('the audio track is silent')
        return
    db = level_db(x, sr)
    hop = 0.01
    end = len(db) * hop
    quiet = runs(db < -50, int(a.max_silence / hop) + 1)
    holes = [(s * hop, e * hop) for s, e in quiet if e * hop < end - 0.5]
    print('dead air:', ', '.join(f'{s:.1f}-{e:.1f}s' for s, e in holes) or 'none')
    fails += [f'dead air {e - s:.1f}s at {s:.1f}s' for s, e in holes]
    tail = db[-3:].max()
    if tail > -35:
        fails.append(f'audio ends abruptly at {tail:.0f} dBFS: give it a tail or a fade')
    drops = [i * hop for i in range(1, len(db) - 1) if db[i - 1] > -25 and db[i + 1] < db[i - 1] - 30 and i * hop < end - 0.2]
    merged = [t for k, t in enumerate(drops) if k == 0 or t - drops[k - 1] > 0.1]
    if merged:
        warns.append('sound cut off abruptly at ' + ', '.join(f'{t:.2f}s' for t in merged[:6]))
    print(f'audio end: last 30 ms at {tail:.0f} dBFS; mid-film abrupt stops: {len(merged)}')

    lufs, peak = measure(video)
    print(f'loudness: {lufs:.1f} LUFS, true peak {peak:.1f} dBTP')
    if peak > -1.0:
        fails.append(f'true peak {peak:.1f} dBTP')
    if not a.no_aac_check:
        p2 = aac_peak(video)
        print(f'true peak after an AAC re-encode: {p2:.1f} dBTP')
        if p2 > -1.0:
            fails.append(f'true peak {p2:.1f} dBTP after AAC re-encode (lower the limiter ceiling)')

    if a.cues:
        rows = []
        for t, label in cue_list(a.cues):
            i0, i1 = int((t - 0.02) / hop), int((t + 0.2) / hop)
            b0, b1 = int((t - 0.5) / hop), int((t - 0.05) / hop)
            if i0 < 0 or i1 >= len(db) or b0 < 0:
                continue
            hit, bed = db[i0:i1].max(), np.median(db[b0:b1])
            rows.append((t, label, hit - bed))
        buried = [r for r in rows if r[2] < 3]
        spiky = [r for r in rows if r[2] > 20]
        print(f'sound levels: {len(rows)} cues measured, {len(buried)} buried (< +3 dB over the bed), {len(spiky)} spiky (> +20 dB)')
        for t, label, delta in buried[:8]:
            warns.append(f'cue at {t:.2f}s ({label}) is only {delta:+.1f} dB over the bed: inaudible')
        for t, label, delta in spiky[:8]:
            warns.append(f'cue at {t:.2f}s ({label}) jumps {delta:+.1f} dB over the bed: too loud')


def voice_checks(a, fails):
    words = json.load(open(a.transcript or transcribe(a.video, a.lang)))
    words = words if isinstance(words, list) else words['words']
    heard = letters(' '.join(w['text'] for w in words))
    print('script coverage (letters heard, in order)')
    cursor = 0
    for s in sentences(a.script):
        said = letters(s)
        m = difflib.SequenceMatcher(None, heard, said, autojunk=False)
        anchor = m.find_longest_match(cursor, len(heard), 0, len(said))
        lo = max(cursor, anchor.a - anchor.b - 4)
        window = heard[lo:lo + len(said) + 12]
        blocks = difflib.SequenceMatcher(None, window, said, autojunk=False).get_matching_blocks()
        ratio = sum(n for *_, n in blocks) / len(said)
        repeats = heard.count(said) if len(said) >= 20 else 0
        ok = ratio >= 0.75 and repeats <= 1
        if ok:
            cursor = lo + max((b.a + b.size for b in blocks if b.size), default=0)
        else:
            fails.append(s)
        note = f' (said {repeats}x)' if repeats > 1 else ''
        print(f"  {'ok  ' if ok else 'FAIL'} {ratio:4.0%}{note}  {s[:90]}")
    gaps = [y['start'] - x['end'] for x, y in zip(words, words[1:])]
    if gaps:
        longest = max(gaps)
        at = words[gaps.index(longest)]['end']
        print(f'silence: median gap {statistics.median(gaps):.2f}s, longest {longest:.2f}s at {at:.1f}s')
        if longest > a.max_gap:
            fails.append(f'pause of {longest:.1f}s at {at:.1f}s')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--video', required=True)
    p.add_argument('--script', help='script.json or .txt; enables the voice checks')
    p.add_argument('--transcript', help='Parakeet word list of the final film (skips transcription)')
    p.add_argument('--lang', default='en')
    p.add_argument('--max-gap', type=float, default=2.5, help='longest pause between words (s, default 2.5)')
    p.add_argument('--end-card', type=float, default=2.5, help='seconds at the end allowed to hold still (default 2.5)')
    p.add_argument('--max-still', type=float, default=1.5, help='longest frozen stretch before the end card (s, default 1.5)')
    p.add_argument('--max-still-ratio', type=float, default=0.25, help='warn when more of the film than this is frozen')
    p.add_argument('--still-threshold', type=float, default=0.3, help='mean frame difference (0-255) below which a frame is still')
    p.add_argument('--min-shot', type=float, default=0.2, help='two cuts closer than this fail as a double cut (s)')
    p.add_argument('--max-silence', type=float, default=1.2, help='dead air longer than this fails (s, default 1.2)')
    p.add_argument('--cues', help='cue sheet (mix.py JSON, or [{t, label}]) for per-sound level checks')
    p.add_argument('--no-aac-check', action='store_true', help='skip the true-peak check after an AAC re-encode')
    a = p.parse_args()

    fails, warns = [], []
    _, _, has_audio = probe(a.video)
    picture_checks(a.video, a, fails, warns)
    if has_audio:
        audio_checks(a.video, a, fails, warns)
    else:
        print('audio: none (silent file)')
    if a.script:
        voice_checks(a, fails)

    for w in warns:
        print('  warn', w)
    if fails:
        print(f'\n{len(fails)} problem(s):')
        for f in fails:
            print('  -', f)
        sys.exit(1)
    print('\nall checks passed')


if __name__ == '__main__':
    main()
