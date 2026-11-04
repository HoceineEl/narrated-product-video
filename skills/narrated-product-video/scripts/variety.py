#!/usr/bin/env python3
"""Keep films from looking alike: audit a shot ledger, log it to a history file, report habits.

  variety.py check film.ledger.json [--history PATH] [--last 3]   rules inside the film + against recent films
  variety.py log film.ledger.json [--history PATH]                 append the film to the history
  variety.py report [--history PATH]                               what keeps coming back across films

Ledger format (see references/tone-and-variety.md):
  {"film": "...", "mode": "launch|showreel|tour", "tone": "trustworthy", "look": "light product film",
   "palette": ["#hex", ...], "music": {"bpm": 104, "key": "D", "groove": "half-time"} or null,
   "shots": [{"start": 0, "dur": 1.6, "transition": "cut:hard", "entrance": "word-rise",
              "ease": "power3.out", "direction": "up", "camera": "push", "motif": null, "surprise": false}]}

History defaults to ~/.narrated-product-video/history.jsonl (or $NPV_HISTORY). check exits 1 on a failure.
"""
import argparse
import collections
import datetime
import json
import os
import statistics
import sys

FAMILIES = {'cut', 'carry', 'camera', 'mask', 'material', 'time'}
NARRATIVE = {'carry', 'camera', 'mask'}
QUIET = {'cut:hard'}
TONES = {
    'calm': {'max_cps': 0.5, 'banned': ('back', 'elastic', 'bounce'), 'max_hold': None},
    'trustworthy': {'max_cps': 0.8, 'banned': ('elastic', 'bounce'), 'max_hold': None, 'banned_tr': ('glitch',)},
    'warm': {'max_cps': 0.9, 'banned': ('elastic',), 'max_hold': None},
    'playful': {'max_cps': 1.6, 'banned': (), 'max_hold': None},
    'bold': {'max_cps': 1.8, 'banned': ('sine',), 'max_hold': 3.0},
    'urgent': {'max_cps': 2.6, 'banned': ('sine',), 'max_hold': 2.0},
    'premium': {'max_cps': 0.6, 'banned': ('back', 'elastic', 'bounce'), 'max_hold': None},
    'technical': {'max_cps': 1.2, 'banned': ('elastic', 'bounce'), 'max_hold': None},
}


def history_path(arg):
    return os.path.expanduser(arg or os.environ.get('NPV_HISTORY') or '~/.narrated-product-video/history.jsonl')


def read_history(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def family(tr):
    return (tr or 'cut:hard').split(':')[0]


def runs(values, n):
    hits = []
    for i in range(len(values) - n + 1):
        window = values[i:i + n]
        if window[0] and all(v == window[0] for v in window):
            hits.append(i)
    return hits


def check_film(film):
    fails, warns = [], []
    shots = film.get('shots', [])
    if len(shots) < 2:
        return ['ledger has fewer than 2 shots'], warns
    durs = [s['dur'] for s in shots]
    total = sum(durs)
    cuts = shots[1:]
    trs = [s.get('transition', 'cut:hard') for s in cuts]

    for i in range(1, len(trs)):
        if trs[i] == trs[i - 1] and trs[i] not in QUIET and not cuts[i].get('motif'):
            fails.append(f"same transition '{trs[i]}' on two consecutive cuts at {cuts[i]['start']:.1f}s")
    bad = [t for t in trs if family(t) not in FAMILIES]
    if bad:
        warns.append(f'unknown transition families: {sorted(set(bad))} (use {sorted(FAMILIES)})')
    fams = {family(t) for t in trs}
    if len(cuts) >= 5 and len(fams) < 3:
        fails.append(f'only {len(fams)} transition families ({", ".join(sorted(fams))}) across {len(cuts)} cuts; use 3+')
    if len(cuts) >= 3 and not fams & NARRATIVE:
        fails.append('no carry, camera or mask transition: every cut is a plain swap')
    if total < 60:
        for t, n in collections.Counter(t for t in trs if t not in QUIET).items():
            if n > 2 and not all(c.get('motif') for c in cuts if c.get('transition') == t):
                warns.append(f"'{t}' used {n}x in a {total:.0f}s film (max 2 unless tagged motif)")

    ent = [s.get('entrance') for s in shots]
    for i in runs(ent, 3):
        fails.append(f"entrance '{ent[i]}' three times in a row from {shots[i]['start']:.1f}s")
    dirs = [s.get('direction') for s in shots]
    for i in runs(dirs, 3):
        fails.append(f"three '{dirs[i]}' entrances in a row from {shots[i]['start']:.1f}s")

    eases = collections.Counter(s.get('ease') for s in shots if s.get('ease'))
    if len(eases) < 3:
        fails.append(f'only {len(eases)} eases used; use at least 3')
    if eases:
        top, n = eases.most_common(1)[0]
        if n > len(shots) / 2:
            fails.append(f"ease '{top}' on {n}/{len(shots)} shots (max half)")

    if len(durs) >= 4:
        cv = statistics.pstdev(durs) / statistics.mean(durs)
        if cv < 0.25:
            fails.append(f'shot lengths too even (variation {cv:.2f}, need 0.25+): reads as a metronome')
        same = max(sum(1 for d in durs if abs(d - ref) <= 0.25) for ref in durs)
        if same > 0.6 * len(durs):
            fails.append(f'{same}/{len(durs)} shots share one length (±0.25 s)')

    last = 0.0
    for s in shots:
        if s.get('surprise'):
            last = s['start']
        if s['start'] - last > 15:
            warns.append(f"no surprise between {last:.0f}s and {s['start']:.0f}s")
            last = s['start']

    tone = TONES.get((film.get('tone') or '').lower())
    if film.get('tone') and not tone:
        warns.append(f"unknown tone '{film['tone']}' (known: {', '.join(TONES)})")
    if tone:
        cps = len(cuts) / total if total else 0
        if cps > tone['max_cps']:
            fails.append(f"{film['tone']} film cuts {cps:.2f}/s (max {tone['max_cps']})")
        for s in shots:
            e = (s.get('ease') or '').lower()
            if any(b in e for b in tone['banned']):
                fails.append(f"{film['tone']} film uses '{s['ease']}' at {s['start']:.1f}s")
            if tone['max_hold'] and s['dur'] > tone['max_hold'] and s is not shots[-1]:
                fails.append(f"{film['tone']} film holds a shot {s['dur']:.1f}s at {s['start']:.1f}s")
        for tr in trs:
            if any(b in tr for b in tone.get('banned_tr', ())):
                fails.append(f"{film['tone']} film uses transition '{tr}'")
    return fails, warns


def named(film):
    return {s.get('transition') for s in film.get('shots', [])[1:]} - QUIET - {None}


def check_history(film, past):
    warns = []
    if not past:
        return warns
    mine = named(film)
    used = set().union(*(named(p) for p in past))
    if mine and len(mine & used) > len(mine) / 2:
        warns.append(f'{len(mine & used)}/{len(mine)} named transitions were used in the last {len(past)} films: {sorted(mine & used)}')
    for p in past:
        if film.get('look') and p.get('look') == film.get('look'):
            warns.append(f"same look as '{p.get('film')}': {film['look']}")
        m, q = film.get('music') or {}, p.get('music') or {}
        if m.get('groove') and m.get('groove') == q.get('groove') and m.get('bpm') and q.get('bpm') \
                and abs(m['bpm'] - q['bpm']) <= 0.1 * q['bpm']:
            warns.append(f"same groove '{m['groove']}' at a similar tempo as '{p.get('film')}' ({q['bpm']} BPM)")
        if film.get('palette') and p.get('palette') and set(map(str.lower, film['palette'])) == set(map(str.lower, p['palette'])):
            warns.append(f"same palette as '{p.get('film')}'")
    return warns


def report(past):
    if not past:
        print('history is empty')
        return
    print(f'{len(past)} films logged')
    for key, label in (('transition', 'transitions'), ('entrance', 'entrances'), ('ease', 'eases'), ('camera', 'camera moves')):
        c = collections.Counter(s.get(key) for p in past for s in p.get('shots', []) if s.get(key))
        print(f'  {label}: ' + ', '.join(f'{k} {v}' for k, v in c.most_common(6)))
    for key in ('tone', 'look'):
        c = collections.Counter(p.get(key) for p in past if p.get(key))
        print(f'  {key}: ' + ', '.join(f'{k} {v}' for k, v in c.most_common(5)))
    g = collections.Counter((p.get('music') or {}).get('groove') for p in past if p.get('music'))
    if g:
        print('  music grooves: ' + ', '.join(f'{k} {v}' for k, v in g.most_common(5)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('action', choices=['check', 'log', 'report'])
    p.add_argument('ledger', nargs='?')
    p.add_argument('--history', help='history file (default ~/.narrated-product-video/history.jsonl)')
    p.add_argument('--last', type=int, default=3, help='films to compare against (default 3)')
    a = p.parse_args()
    hist = history_path(a.history)
    past = read_history(hist)
    if a.action == 'report':
        report(past)
        return
    if not a.ledger:
        p.error('ledger is required')
    film = json.load(open(a.ledger))
    if a.action == 'log':
        os.makedirs(os.path.dirname(hist), exist_ok=True)
        film = {**film, 'logged': datetime.date.today().isoformat()}
        with open(hist, 'a') as f:
            f.write(json.dumps(film) + '\n')
        print(f"logged '{film.get('film')}' to {hist}")
        return
    recent = [x for x in past if x.get('film') != film.get('film')][-a.last:]
    fails, warns = check_film(film)
    warns += check_history(film, recent)
    print(f"{film.get('film')}: {len(film.get('shots', []))} shots, tone {film.get('tone')}, compared with {len(recent)} earlier films")
    for w in warns:
        print('  warn', w)
    for f in fails:
        print('  FAIL', f)
    if fails:
        sys.exit(1)
    print('variety ok')


if __name__ == '__main__':
    main()
