"""python3 launch_build.py <transcript.json> <vo.wav rel to composition>  -> writes cues.js + index.html"""
import json, os, re, sys, unicodedata
ROOT = os.path.join(os.environ.get('VIDEO_ROOT', os.path.expanduser('~/Downloads/my-app-videos')), 'launch')
KEYS = [('fin', 'fin'), ('whats', 'whatsapp'), ('email', 'email'), ('photos', 'photo'), ('sacs', 'sac'),
        ('cab', 'au'), ('saisit', 'saisit'), ('verifie', 'verifie'), ('relance', 'relance'), ('recommence', 'recommence'),
        ('etsi', 'et'), ('avant', 'avant'), ('fscompta', 'fs'), ('arrivait', 'arrivait'), ('pret', 'pret'),
        ('voici', 'voici'), ('brand', 'fs'), ('compagnon', 'compagnon'),
        ('client', 'cote'), ('application', 'lapplication'), ('telephone', 'telephone'), ('photo', 'photo'), ('envoyee', 'envoyee'),
        ('suit', 'suit'), ('arabe', 'arabe'),
        ('cabinet2', 'cote'), ('facture2', 'facture'), ('lue', 'lue'), ('fournisseur', 'fournisseur'), ('ice', 'ice'), ('ht', 'hors'),
        ('plusieurs', 'plusieurs'), ('doublons', 'doublons'), ('bloques', 'bloques'), ('montants', 'montants'),
        ('ecriture', 'lecriture'), ('plan', 'plan'), ('valider', 'valider'),
        ('suit2', 'et'), ('decl', 'declaration'), ('ventes', 'facture'), ('relances', 'relance'), ('echanges', 'echange'), ('equipe', 'equipe'),
        ('ensuite', 'ensuite'), ('fscompta2', 'fs'), ('recupere', 'recupere'), ('pieces', 'leur'), ('ressaisie', 'ressaisie'),
        ('reserve', 'vos'), ('valide', 'valide'), ('recoit', 'recoit'), ('prochaine', 'votre'), ('besoin', 'besoin'), ('brand', 'fs'), ('contact', 'contacteznous')]


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


words = json.load(open(sys.argv[1]))
words = words if isinstance(words, list) else words['words']
T, i = {}, 0
for key, w in KEYS:
    while norm(words[i]['text']) != w:
        i += 1
    T[key] = round(words[i]['start'], 3)
    i += 1
T['end'] = round(words[-1]['end'], 3)
T['dur'] = round(T['end'] + 2.6, 2)
bounds = {'s1': (0, T['cab'] - 0.3), 's2': (T['cab'] - 0.4, T['etsi']), 's3': (T['etsi'] - 0.1, T['voici']),
          's4': (T['voici'] - 0.05, T['client'] - 0.1), 's5': (T['client'] - 0.2, T['cabinet2']),
          's6': (T['cabinet2'] - 0.2, T['suit2']), 's7': (T['suit2'] - 0.2, T['ensuite']),
          's8': (T['ensuite'] - 0.1, T['reserve']), 's9': (T['reserve'] - 0.1, T['dur'])}
html = open(f'{ROOT}/index.tpl.html').read()
for s, (a, b) in bounds.items():
    html = html.replace('{{%s_start}}' % s, f'{max(0, a):.2f}').replace('{{%s_dur}}' % s, f'{b - max(0, a):.2f}')
html = html.replace('{{dur}}', f"{T['dur']}").replace('{{vo}}', sys.argv[2]).replace('{{vo_start}}', '0')
assert '{{' not in html, re.findall(r'\{\{\w+\}\}', html)
rects = json.load(open(f'{ROOT}/rects.json'))
cues = f'window.T={json.dumps(T)};\nwindow.RECTS={json.dumps(rects)};\n'
tl = open(f'{ROOT}/timeline.js').read()
html = html.replace('<script src="cues.js"></script><script src="timeline.js"></script>', f'<script>\n{cues}{tl}</script>')
assert 'timeline.js' not in html
open(f'{ROOT}/composition/index.html', 'w').write(html)
json.dump(T, open(f'{ROOT}/T.json', 'w'), indent=1)
print(json.dumps(T))
