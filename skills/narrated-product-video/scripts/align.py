#!/usr/bin/env python3
"""Cut a voice take into one clean clip per beat.

  align.py --script script.json --audio take-m.wav --transcript transcript.json --out-dir beats/ [--chapters c00,c01]

script.json: {"chapters": [{"id": "c00", "beats": [{"id": "c00a", "text": "..."}]}]}
transcript.json: word list from `npx hyperframes transcribe take.wav -e parakeet`, [{"text", "start", "end"}].

Each beat is cut at the midpoint of the silence before the next beat's first word, never at the last
matched word (a misheard acronym would cut mid-sentence). Trailing fillers are dropped, breaths longer
than --breath seconds are muted, and the clip is slowed by --tempo. Prints [{id, start, end, dur}] as JSON.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata

FILLERS = {'uh', 'um', 'so', 'okay', 'alright', 'voila', 'pret', 'bon', 'alors', 'donc', 'euh'}


def toks(text):
    t = unicodedata.normalize('NFKD', text.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.findall(r'[a-z0-9؀-ۿ]+', t)


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout
    return float(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--script', required=True)
    p.add_argument('--audio', required=True)
    p.add_argument('--transcript', required=True)
    p.add_argument('--out-dir', required=True)
    p.add_argument('--chapters', help='comma-separated chapter ids voiced in this take (default: all)')
    p.add_argument('--tempo', type=float, default=1.0, help='atempo factor, 0.95 slows a rushed read')
    p.add_argument('--breath', type=float, default=0.22, help='mute pauses longer than this (seconds)')
    a = p.parse_args()

    script = json.load(open(a.script))
    wanted = set(a.chapters.split(',')) if a.chapters else None
    beats = [b for ch in script['chapters'] if wanted is None or ch['id'] in wanted for b in ch['beats']]
    words = json.load(open(a.transcript))
    words = words if isinstance(words, list) else words['words']

    st, owner = [], []
    for i, b in enumerate(beats):
        tk = toks(b['text'])
        st += tk
        owner += [i] * len(tk)
    wt, wstart = [], []
    for w in words:
        for t in toks(w['text']):
            wt.append(t)
            wstart.append(w['start'])

    first = {}
    for x, y, n in difflib.SequenceMatcher(None, st, wt, autojunk=False).get_matching_blocks():
        for k in range(n):
            first.setdefault(owner[x + k], wstart[y + k])
    missing = [b['id'] for i, b in enumerate(beats) if i not in first]
    if missing:
        sys.exit(f'beats not found in transcript: {missing}')

    def cut(t):
        j = next(k for k, w in enumerate(words) if w['start'] >= t - 1e-6)
        prev = words[j - 1]['end'] if j else 0.0
        return max((prev + words[j]['start']) / 2, words[j]['start'] - 0.25)

    total = duration(a.audio)
    os.makedirs(a.out_dir, exist_ok=True)
    result = []
    for i, b in enumerate(beats):
        s = max(0.0 if i == 0 else cut(first[i]), first[i] - 0.06)
        e = total if i == len(beats) - 1 else cut(first[i + 1])
        if i < len(beats) - 1:
            tail = [w for w in words if first[i] < w['start'] < first[i + 1]]
            while len(tail) > 1 and toks(tail[-1]['text'])[:1] and toks(tail[-1]['text'])[0] in FILLERS:
                e = min(e, (tail[-2]['end'] + tail[-1]['start']) / 2)
                tail.pop()
        inside = [w for w in words if s <= w['start'] and w['end'] <= e]
        mutes = [(x['end'] - s + 0.05, y['start'] - s - 0.04) for x, y in zip(inside, inside[1:])
                 if y['start'] - x['end'] > a.breath]
        vol = ''.join(f"volume=enable='between(t,{x:.3f},{y:.3f})':volume=0.06," for x, y in mutes if y > x)
        tempo = f'atempo={a.tempo},' if a.tempo != 1.0 else ''
        out = os.path.join(a.out_dir, f"{b['id']}.wav")
        af = vol + 'areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.02,' \
            + tempo + 'areverse,afade=t=in:d=0.06,areverse'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{s:.3f}', '-to', f'{e:.3f}', '-i', a.audio, '-af', af, out],
                       check=True)
        result.append({'id': b['id'], 'start': round(s, 2), 'end': round(e, 2), 'dur': round(duration(out), 2)})
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
