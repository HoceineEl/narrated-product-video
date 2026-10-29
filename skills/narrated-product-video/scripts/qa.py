#!/usr/bin/env python3
"""Check a finished video before anyone watches it.

  qa.py --script script.json --video final.mp4 [--transcript final-words.json] [--lang en]

Without --transcript it runs `npx hyperframes transcribe` on the video's audio (Parakeet).
Reports, and exits 1 when a hard check fails:
  - script coverage: every sentence of the script is heard, none is clipped or said twice
  - silence: pauses between words (median and longest)
  - blank frames: runs of flat frames (white or black flashes)
  - loudness: integrated LUFS and true peak
The script may be script.json (chapters/beats) or a plain .txt file.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from master import measure  # noqa: E402


ONES = ('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen '
        'seventeen eighteen nineteen').split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()


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


def blank_runs(video, min_len=0.3):
    size = 160 * 90
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', 'fps=10,scale=160:90,format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    frames = [raw[i:i + size] for i in range(0, len(raw) - size + 1, size)]
    runs, start = [], None
    for i, f in enumerate(frames + [bytes(range(256)) * (size // 256)]):
        flat = statistics.pstdev(f) < 2
        if flat and start is None:
            start = i
        elif not flat and start is not None:
            if (i - start) / 10 >= min_len:
                runs.append((start / 10, i / 10))
            start = None
    return runs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--script', required=True)
    p.add_argument('--video', required=True)
    p.add_argument('--transcript')
    p.add_argument('--lang', default='en')
    p.add_argument('--max-gap', type=float, default=2.5, help='longest allowed pause between words (seconds)')
    a = p.parse_args()

    words = json.load(open(a.transcript or transcribe(a.video, a.lang)))
    words = words if isinstance(words, list) else words['words']
    heard = letters(' '.join(w['text'] for w in words))
    failures = []

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
            failures.append(s)
        note = f' (said {repeats}x)' if repeats > 1 else ''
        print(f"  {'ok  ' if ok else 'FAIL'} {ratio:4.0%}{note}  {s[:90]}")

    gaps = [y['start'] - x['end'] for x, y in zip(words, words[1:])]
    if gaps:
        longest = max(gaps)
        at = words[gaps.index(longest)]['end']
        print(f'silence: median gap {statistics.median(gaps):.2f}s, longest {longest:.2f}s at {at:.1f}s')
        if longest > a.max_gap:
            failures.append(f'pause of {longest:.1f}s at {at:.1f}s')

    runs = blank_runs(a.video)
    print('blank frames:', ', '.join(f'{x:.1f}-{y:.1f}s' for x, y in runs) or 'none')
    failures += [f'blank frames {x:.1f}-{y:.1f}s' for x, y in runs]

    lufs, peak = measure(a.video)
    print(f'loudness: {lufs:.1f} LUFS, true peak {peak:.1f} dBTP')
    if peak > -1.0:
        failures.append(f'true peak {peak:.1f} dBTP')

    if failures:
        print(f'\n{len(failures)} problem(s):')
        for f in failures:
            print('  -', f)
        sys.exit(1)
    print('\nall checks passed')


if __name__ == '__main__':
    main()
