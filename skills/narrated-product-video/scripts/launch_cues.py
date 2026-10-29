"""python3 launch_cues.py -> launch/cues3.json (SFX keyed to word onsets in launch/T.json)"""
import json, os
ROOT = os.path.join(os.environ.get('VIDEO_ROOT', os.path.expanduser('~/Downloads/my-app-videos')), 'launch')
T = json.load(open(f'{ROOT}/T.json'))
C = []
W = ['lib/bsb/whoosh-1795.wav', 'lib/bsb/whoosh-1796.wav', 'lib/bsb/whoosh-1797.wav', 'lib/bsb/whoosh-1798.wav']


def at(k, o=0.0):
    return round(T[k] + o, 3)


def c(t, f, g, **kw):
    C.append(dict(t=max(0.0, t), f=f, g=g, **kw))


def whoosh(t, i=0, g=-14):
    c(t, W[i % 4], g, lp=7000, p=i % 3 - 1)


# S1 hook
c(0.0, 'lib/kenney_sci-fi-sounds/Audio/lowFrequency_explosion_000.ogg', -10)
c(0.0, 'lib/mixkit/2364.wav', -16)
whoosh(at('whats', -0.5), 2, -15)
for i in range(4):
    c(at('whats', -0.05 + i * 0.16), 'lib/mixkit/2357.wav', -13, p=[0, 2, -1, 3][i])
for i in range(3):
    c(at('email', i * 0.14), f'brag/casino/card-slide-{i + 1}.ogg', -9)
for o in (-0.15, 0.15):
    c(at('photos', o), 'lib/synth/shutter.wav', -8)
    c(at('photos', o + 0.02), 'brag/casino/card-place-1.ogg', -11)
c(at('photos', 0.55), 'brag/interface/error_005.ogg', -13)
c(at('sacs', -0.4), 'lib/bsb/whoosh-1797.wav', -15, lp=7000)
c(at('sacs', -0.3), 'lib/synth/bag.wav', -12)
c(at('sacs', 0.14), 'brag/impact/impactSoft_heavy_002.ogg', -6)
c(at('sacs', 0.16), 'lib/synth/bag.wav', -10)
for i in range(4):
    c(at('sacs', 0.22 + i * 0.07), f'brag/casino/card-slide-{i + 1}.ogg', -11, p=i % 3)
c(at('cab', -0.45), 'lib/mixkit/1492.wav', -10, lp=7000)
# S2 grind
c(at('cab', -0.1), 'brag/casino/card-slide-5.ogg', -9)
for i, k in enumerate(['saisit', 'verifie', 'relance']):
    c(at(k, -0.1), f'brag/impact/impactSoft_medium_00{i}.ogg', -6, p=i)
c(at('cab', 0.3), 'lib/mixkit/2531.wav', -22, ss=2.0, dur=at('recommence') - at('cab'), fade=0.4)
c(at('recommence', -0.2), 'lib/mixkit/1490.wav', -8, rev=True, lp=7000)
c(at('recommence', 0.25), 'brag/impact/impactSoft_heavy_001.ogg', -6)
whoosh(at('etsi', -0.3), 3, -15)
# S3 question
c(at('etsi', -0.1), 'lib/mixkit/3115.wav', -12, lp=7000)
c(at('fscompta', -0.1), 'brag/interface/drop_002.ogg', -13)
for i in range(5):
    c(at('pret', -0.4 + i * 0.1), f'brag/casino/card-place-{i % 4 + 1}.ogg', -9, p=2)
c(at('voici', -0.6), 'lib/mixkit/790.wav', -11, fade=0.05, lp=7000)
# S4 logo
c(at('voici', -0.05), 'brag/impact/impactBell_heavy_000.ogg', -7)
c(at('voici', -0.05), 'lib/kenney_sci-fi-sounds/Audio/lowFrequency_explosion_001.ogg', -9)
c(at('brand', -0.15), 'lib/mixkit/166.wav', -14, lp=7000)
c(at('compagnon', -0.1), 'brag/interface/drop_001.ogg', -14)
whoosh(at('client', -0.35), 0, -13)
# S5 client phone
c(at('client', -0.1), 'brag/interface/drop_002.ogg', -13)
c(at('telephone', -0.35), 'brag/ui/click3.ogg', -8)
c(at('telephone', 0.05), 'lib/mixkit/1489.wav', -12, lp=7000)
c(at('photo', -0.12), 'brag/ui/click1.ogg', -8)
c(at('photo', 0.0), 'brag/interface/switch_002.ogg', -5)
c(at('photo', 0.0), 'lib/mixkit/2364.wav', -12, p=-3)
c(at('envoyee', -0.25), 'brag/ui/click2.ogg', -8)
c(at('envoyee', -0.05), 'lib/bsb/whoosh-1798.wav', -12, lp=7000)
c(at('envoyee', 0.05), 'lib/kenney_interface-sounds/Audio/confirmation_001.ogg', -11)
c(at('suit', -0.1), 'brag/interface/drop_001.ogg', -13)
sg = (at('arabe') - 0.9 - at('suit')) / 2
for i in range(3):
    c(at('suit', 0.1 + i * (sg + 0.1)), 'brag/interface/select_008.ogg', -13, p=i * 2)
c(at('arabe', -0.3), 'brag/casino/card-slide-2.ogg', -11)
whoosh(at('cabinet2', -0.35), 1, -12)
# S6 cabinet
c(at('cabinet2', -0.2), 'lib/mixkit/3115.wav', -10, lp=7000)
c(at('facture2', -0.1), 'brag/interface/drop_002.ogg', -13)
tv = max(0.8, at('fournisseur') - at('lue') - 0.4)
n = int(tv / 0.12)
for i in range(n):
    c(at('lue', i * 0.12), 'brag/ui/click5.ogg', -26, p=i % 3)
c(at('lue', tv), 'lib/kenney_interface-sounds/Audio/confirmation_003.ogg', -13)
c(at('fournisseur', -0.35), 'lib/mixkit/1492.wav', -12, lp=7000)
for k, p in [('fournisseur', 0), ('ice', 2), ('ht', -2)]:
    c(at(k, -0.05), 'lib/mixkit/3124.wav', -13, p=p)
c(at('ice', 0.1), 'brag/impact/impactGlass_light_001.ogg', -15)
c(at('ht', -0.45), 'lib/bsb/whoosh-1797.wav', -14, lp=7000)
c(at('doublons', -0.1), 'brag/casino/card-slide-6.ogg', -11)
c(at('bloques', -0.05), 'brag/interface/error_005.ogg', -11)
c(at('montants', -0.05), 'lib/kenney_interface-sounds/Audio/confirmation_004.ogg', -13)
c(at('ecriture', -0.25), 'lib/mixkit/1490.wav', -13, lp=7000)
rs = (at('valider') - 0.6 - at('ecriture')) / 4
for i in range(3):
    c(at('ecriture', 0.2 + i * rs), 'brag/ui/click4.ogg', -14, p=i)
c(at('plan', -0.05), 'brag/interface/drop_003.ogg', -12)
c(at('ecriture', 0.25 + 3 * rs), 'brag/casino/chips-stack-1.ogg', -12)
c(at('valider', -0.75), 'lib/bsb/whoosh-1796.wav', -13, lp=7000)
c(at('valider', -0.05), 'brag/ui/mouseclick1.ogg', -5)
c(at('valider', 0.03), 'lib/kenney_interface-sounds/Audio/confirmation_004.ogg', -8)
c(at('valider', 0.43), 'brag/impact/impactSoft_heavy_002.ogg', -4)
c(at('valider', 0.43), 'brag/impact/impactBell_heavy_003.ogg', -12)
# S7 mosaic
c(at('suit2', -0.45), 'lib/mixkit/1492.wav', -11, lp=7000)
c(at('suit2', 0.0), 'brag/casino/card-fan-1.ogg', -8)
for i, k in enumerate(['decl', 'ventes', 'relances', 'echanges', 'equipe']):
    c(at(k, -0.08), f'brag/casino/card-place-{i % 4 + 1}.ogg', -14, p=i % 3)
    c(at(k, -0.06), 'brag/interface/drop_002.ogg', -18, p=i * 1.5)
whoosh(at('ensuite', -0.3), 2, -13)
# S8 bridge
c(at('ensuite', -0.1), 'brag/casino/card-slide-7.ogg', -12)
c(at('fscompta2', -0.1), 'brag/casino/card-slide-8.ogg', -12)
c(at('recupere', -0.2), 'lib/mixkit/166.wav', -12, lp=7000)
c(at('recupere', 0.2), 'lib/mixkit/645.wav', -19, ss=3.0, dur=at('ressaisie') - at('recupere'), lp=6000, fade=0.6)
fs = max(0.35, (at('ressaisie') - at('recupere') - 0.6) / 4)
for i in range(4):
    whoosh(at('recupere', 0.2 + i * fs), i, -16)
    c(at('recupere', 0.7 + i * fs), 'brag/ui/rollover2.ogg', -20, p=i)
c(at('ressaisie', 0.08), 'brag/impact/impactSoft_heavy_000.ogg', -3)
c(at('ressaisie', 0.08), 'brag/impact/impactPunch_medium_001.ogg', -12)
# S9 outro
c(at('reserve', -0.3), 'lib/mixkit/1490.wav', -11, lp=7000)
c(at('reserve', 0.0), 'brag/impact/impactSoft_medium_003.ogg', -8)
c(at('valide', -0.45), 'brag/impact/impactSoft_medium_004.ogg', -9)
c(at('recoit', -0.7), 'brag/impact/impactSoft_medium_001.ogg', -9)
c(at('recoit', -0.6), 'brag/interface/drop_001.ogg', -13)
whoosh(at('prochaine', -0.4), 1, -13)
c(at('prochaine', -0.05), 'brag/interface/drop_002.ogg', -15)
c(at('besoin', -0.1), 'brag/impact/impactSoft_medium_002.ogg', -9)
whoosh(at('brand', -0.4), 0, -12)
c(at('brand', -0.1), 'brag/impact/impactBell_heavy_004.ogg', -5)
c(at('brand', -0.1), 'lib/kenney_sci-fi-sounds/Audio/lowFrequency_explosion_000.ogg', -14)
c(at('brand', -0.1), 'brag/impact/impactSoft_heavy_003.ogg', -8)
c(at('contact', 0.3), 'lib/mixkit/3005.wav', -13)
c(at('contact', 0.8), 'brag/interface/drop_002.ogg', -14)
cfg = dict(duration=T['dur'], voice=[dict(file=f'{ROOT}/vo/take4-m.wav', t=0.0, gain=0)], sfx=sorted(C, key=lambda x: x['t']), room=-46, duck_db=5, target_lufs=-14)
json.dump(cfg, open(f'{ROOT}/cues3.json', 'w'), indent=1)
print(len(C), 'cues')
