"""align.py <script.json> <group> <audio.wav> <transcript.json> <outdir> -> cuts beat wavs + prints json"""
import json, re, subprocess, sys, difflib, unicodedata, os
script, group, audio, tx, outdir = sys.argv[1:6]
GROUPS = {'g5': ['c12'], 'g0': ['cc0'], 'g1': ['c00', 'c01', 'c02', 'c03'], 'g2': ['c04', 'c05', 'c06'], 'g3': ['c07', 'c08', 'c09', 'c10', 'c11', 'c12']}
S = json.load(open(script))
beats = [b for ch in S['chapters'] if ch['id'] in GROUPS[group] for b in ch['beats']]
def toks(t):
    t = unicodedata.normalize('NFKD', t.lower()); t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t)
st, owner = [], []
for i, b in enumerate(beats):
    tk = toks(b['text']); st += tk; owner += [i] * len(tk)
w = json.load(open(tx)); w = w if isinstance(w, list) else w['words']
wt, wtime, wend = [], [], []
for x in w:
    for t in toks(x['text']):
        wt.append(t); wtime.append(x['start']); wend.append(x['end'])
sm = difflib.SequenceMatcher(None, st, wt, autojunk=False)
first, last = {}, {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        i = owner[a + k]
        first.setdefault(i, wtime[b + k])
        last[i] = wend[b + k]
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio], capture_output=True, text=True).stdout)
for i, b in enumerate(beats):
    if i not in first:
        raise SystemExit(f"beat {b['id']} not found")
FILLERS = {'voila', 'pret', 'bon', 'alors', 'donc'}


def cut(t):
    j = next(k for k, x in enumerate(w) if x['start'] >= t - 1e-6)
    prev = w[j - 1]['end'] if j else 0.0
    return max((prev + w[j]['start']) / 2, w[j]['start'] - 0.25)


res = []
os.makedirs(outdir, exist_ok=True)
for i, b in enumerate(beats):
    s = max(0.0 if i == 0 else cut(first[i]), first[i] - 0.06)
    e = dur if i == len(beats) - 1 else cut(first[i + 1])
    if i < len(beats) - 1:
        tail = [x for x in w if first[i] < x['start'] < first[i + 1]]
        while tail and toks(tail[-1]['text']) and toks(tail[-1]['text'])[0] in FILLERS:
            e = min(e, (tail[-2]['end'] + tail[-1]['start']) / 2 if len(tail) > 1 else e)
            tail.pop()
    out = f"{outdir}/{b['id']}.wav"
    ws = [x for x in w if s <= x['start'] and x['end'] <= e]
    mutes = [(a['end'] - s + 0.05, c['start'] - s - 0.04) for a, c in zip(ws, ws[1:]) if c['start'] - a['end'] > 0.22]
    vol = ''.join(f"volume=enable='between(t,{x:.3f},{y:.3f})':volume=0.06," for x, y in mutes if y > x)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{s:.3f}', '-to', f'{e:.3f}', '-i', audio, '-af', vol + 'areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.02,atempo=0.95,areverse,afade=t=in:d=0.06,areverse', out], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    res.append({'id': b['id'], 'start': round(s, 2), 'end': round(e, 2), 'dur': round(d, 2)})
print(json.dumps(res))
