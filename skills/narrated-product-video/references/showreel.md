# Showreel mode (music-first promo)

A 15–60 s product promo cut to music: a showreel, a social promo, a feature sizzle. Picture and sound read one **beat grid**, so every cut, hit and sound lands on the same clock. A voice is optional; when there is one, the voice still wins and the cuts snap to beats near its words.

Read `motion.md` and `tone-and-variety.md` first; this file adds the music clock, structure and cutdowns.

## 1. Length and structure by bars

One bar = 240 / BPM seconds (2 s at 120 BPM). Scenes are whole bars; neighbouring scenes overlap by up to a beat, and the transition lives in that overlap.

| Length | Bars at ~120 BPM | Shape |
|---|---|---|
| 15 s | 6 + tail | hook 1 · reveal 1 · proof 2 · lockup 2 |
| 30 s | 14 + tail | hook 2 · reveal 2 · proof 6 · turn 2 · lockup 2 |
| 45 s | 21 + tail | hook 2 · reveal 2 · how it works 6 · proof 6 · turn 2 · lockup 3 |
| 60 s | 28 + tail | as 45 s, plus a breakdown and a second drop that adds a layer |

- **Hook**: the pain or the promise in 3–6 words, moving from frame 1. Never a logo over black.
- **Reveal** lands on the drop: product name + the first real screen.
- **Proof**: real screenshots or recordings, one feature per shot, the product working on one example. Proof starts before 50 % of the film.
- **Burst** at 60–80 % of the runtime: 3+ quick hits on beats.
- **Lockup**: the last visual change lands on the final downbeat; the end card holds through the music's tail (1.5–2.5 s), with a slow push.

## 2. The beat grid

```bash
python3 scripts/beats.py grid --bpm 120 --bars 6 --tail 2 --cue drop=1 --cue burst=3.2 --out grid.json
```

`grid.json` holds BPM, bar and beat times, named cues and the film duration. Cue values are `bar` or `bar.beat` (0-based), so `burst=3.2` is bar 3, beat 2. The final downbeat (`card`) is added for you: it is where the end card lands and where the music's last hit sits.

In the composition, fill the grid in with a template (no hand-typed seconds anywhere):

```bash
python3 scripts/beats.py fill --grid grid.json --template index.html.tpl --out index.html
```

Name the template `index.html.tpl`: HyperFrames treats every root-level `.html` with a composition id as an entry. `{{GRID}}` becomes the JSON, `{{cue:drop}}` the cue's time, `{{beat:N}}`/`{{bar:N}}` beat and bar times, `{{duration}}` and `{{tail}}` the film and end-card lengths. Worked example: `examples/showreel/`. In GSAP:

```js
const G = {{GRID}};
const b = (n) => G.offset + n * G.beat;          // beat n
const bar = (n, k = 0) => b(n * G.beats_per_bar + k);
tl.fromTo('#reveal', { scale: 1.12 }, { scale: 1, duration: 0.5, ease: 'expo.out' }, G.cues.drop);
```

Rules: cut on downbeats, hit on beats. Cutting on every beat reads as a music video; hits on beats with cuts every bar or two reads as a film. A hard cut may lead its beat by 1–2 frames so it feels like the hit. Compute beat *n* from its index, never by adding a rounded beat repeatedly (it drifts).

**With a voice:** the voice is still the clock. Snap each scene cut to the nearest beat within ±0.15 s of its anchor word, and leave it on the word otherwise:

```bash
python3 scripts/beats.py snap --grid grid.json --times T.json --window 0.15 --out T-beat.json
```

## 3. Music: library track or made in code

**Default: a licensed library track, locked to the picture.** A real recording edited to picture beat code-made scores in client rounds. **Option: original music generated in code** (`beats.py synth`), for a stylised film, a draft, or when no track is licensed. Ask which the owner wants; if music was not requested at all, a narrated film stays voice + foley (rule 10).

**Locking a library track (onset locking):**

```bash
python3 scripts/beats.py analyze track.wav                          # tempo, first downbeat, drop bar, strong hits, last hit
python3 scripts/beats.py fit track.wav --card 12.0 --out grid.json  # place the track so its last hit lands on the end card
```

- `fit` moves the track, not the picture: it computes where the track starts (`ss` trim or a delay) so its final hit lands exactly on `--card`, plays it as one piece from frame 0, and writes a grid in film time. Pass `--hit drop` with `--at 2.0` to lock the drop to the reveal instead.
- Do not trust an automatic beat grid for the drop; `analyze` finds it from the bar where the low band (< 150 Hz) jumps 6 dB or more. Look at its numbers and check by ear (or with an audio-analysis tool).
- Never cut or loop a track to make it fit; move picture cuts onto its grid. If it must be shortened, cut on a bar line with 20 ms fades, outside the exposed intro.
- The music steps out 0.1 s before the logo (80 ms ramp) so the sonic logo or the final hit lands in near silence, then the tail rings.

**Music made in code:**

```bash
python3 scripts/beats.py synth --grid grid.json --key D --mode minor --groove half --seed 7 --out score.wav
```

It reads the same grid: kick and hats on the groove, bass and pad on a four-chord loop in key, a filtered build before `drop`, a half-beat hole and an impact on `drop`, extra layers after it, a two-note sonic logo and the final hit on `card`, then a ringing tail. Grooves: `four` (four on the floor), `half` (half-time), `broken`, `none` (pulse only). Choose the groove first from the tone row, then tempo and key; never the last film's (`variety.py` checks). Treat the result as a stylised choice or a draft and listen before shipping.

**Mix:** music goes into `mix.py` as one long cue (`{"t": 0, "f": "score.wav", "ss": 0, "g": -8}`); keep it 14–18 dB under a voice, and let effects sit 3 dB under the music in-band. A calm film can master at −16 LUFS (`master.py film --lufs -16`).

## 4. Ending on the end card

- The last visual change happens on `card` (the final downbeat), together with the music's last hit.
- After it: logo + one line + where to get it, held through the tail with a slow push. Nothing new enters.
- The audio has a tail: no hard stop. `qa.py` fails an abrupt end and a frozen picture outside the end card.

## 5. Cutdowns: 9:16 and 4:5

Placement decides the format: Reels, TikTok and Shorts are 9:16, sound on, 10–30 s; feeds (LinkedIn, Facebook, Instagram feed) are 4:5 or 1:1 and mostly muted, so words carry the story and **frame 0 is the thumbnail**.

**Best path: render natively.** Duplicate the composition with a vertical root (`data-width="1080" data-height="1920"`), re-lay the shots for the tall frame (UI fills the width, words above and below), and render. Keep the grid and the voice; cut whole bars.

**Fast path: reframe the master.**

```bash
python3 scripts/cutdown.py final.mp4 --aspect 9:16 --captions words.json --range 0-15 --out reel-9x16.mp4
python3 scripts/cutdown.py final.mp4 --aspect 4:5 --captions words.json --out feed-4x5.mp4
python3 scripts/cutdown.py final.mp4 --aspect 9:16 --safe-sheet 6.5 --out check.png   # safe-zone overlay at 6.5 s
```

It places the 16:9 picture inside the safe area over a blurred, darkened copy of itself (or `--bg "#hex"`), burns word-timed captions for muted feeds, fades audio at the cut points and re-encodes for upload (H.264 High, yuv420p, bt709, `+faststart`, AAC).

**Safe zones** (1080-wide frames):

| Format | Keep words and logos inside | Why |
|---|---|---|
| 9:16 (1080×1920) | y 220–1600, x 60–960 | platform UI covers the top ~220 px, the bottom ~320 px and a right-side button column |
| 4:5 (1080×1350) | y 90–1260, x 60–1020 | feed chrome and the crop to 1:1 in some grids |
| 1:1 (1080×1080) | inset 60 px | |

**Captions for muted feeds:** 1–3 words per chunk for reels, 4–7 for calm feeds, each chunk on screen at least 1/3 s, breaking on punctuation or a pause over 0.25 s. The spoken word lights in the accent colour. Captions sit inside the safe zone, above everything, never over the product's key UI. Every stretch with voice has words on screen; a stretch without voice needs on-screen text that carries the idea alone.

Run the same QA on each cutdown (`qa.py --video reel.mp4`), and look at it at phone size (360 px wide).
