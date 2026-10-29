#!/usr/bin/env python3
"""Turn a transcript into named word times, so every visual can be keyed to the word that says it.

  word_times.py --transcript transcript.json --anchors anchors.json --out T.json [--offset 0.3]
  word_times.py ... --template index.tpl.html --html index.html

anchors.json is an ordered list of [key, word] pairs, e.g. [["hook", "steal"], ["devtools", "devtools"],
["shortcut", "alt"]]. Words are matched in order, so a repeated word ("click" twice) gets two keys.
Matching ignores case, accents and punctuation. --offset adds the voice-over start time in the film.

With --template, every {{key}} in the file is replaced by its time in seconds, and {{end}} by the
last word's end, so scene data-start values come straight from the voice.
"""
import argparse
import json
import re
import sys
import unicodedata


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9؀-ۿ]', '', ''.join(c for c in s if not unicodedata.combining(c)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--transcript', required=True)
    p.add_argument('--anchors', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--offset', type=float, default=0.0)
    p.add_argument('--template')
    p.add_argument('--html')
    a = p.parse_args()

    words = json.load(open(a.transcript))
    words = words if isinstance(words, list) else words['words']
    times, i = {}, 0
    for key, word in json.load(open(a.anchors)):
        target = norm(word)
        start = i
        while i < len(words) and norm(words[i]['text']) != target:
            i += 1
        if i == len(words):
            context = ' '.join(w['text'] for w in words[start:start + 12])
            sys.exit(f'anchor {key!r}: word {word!r} not found after word {start} ("{context} ...")')
        times[key] = round(words[i]['start'] + a.offset, 3)
        i += 1
    times['end'] = round(words[-1]['end'] + a.offset, 3)
    json.dump(times, open(a.out, 'w'), indent=1)

    if a.template:
        html = open(a.template).read()
        html = re.sub(r'\{\{(\w+)\}\}', lambda m: f'{times[m.group(1)]:.2f}' if m.group(1) in times else m.group(0), html)
        left = re.findall(r'\{\{\w+\}\}', html)
        if left:
            sys.exit(f'unfilled placeholders: {sorted(set(left))}')
        open(a.html or a.template.replace('.tpl', ''), 'w').write(html)
    print(json.dumps(times))


if __name__ == '__main__':
    main()
