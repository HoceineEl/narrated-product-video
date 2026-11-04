# Tone and variety

Left alone, every film comes out the same: dark ground, one neon accent, fade-up titles, a whoosh on every cut. This file stops that. Do it before storyboarding, in this order: tone sentence, tone row, transitions, ledger, audit.

## 1. One tone sentence per film

Write it before any effect and put it at the top of the storyboard:

> I want to say **[the one idea]** in a **[tone]** tone, so the viewer feels **[feeling]**.

Example: "I want to say *your listings are finally in one place* in a *trustworthy* tone, so the viewer feels *relief, not hype*."

Tone may shift once on purpose (pain urgent, reveal bold, proof trustworthy, CTA warm). One tone held for a whole 60 s film usually goes flat.

## 2. Tone matrix

The row sets eases, cut rate, camera and sound. Pick the row from the tone sentence, not from the last film.

| Tone | Eases | Average shot | Camera | Transition families | Sound |
|---|---|---|---|---|---|
| calm | `sine.inOut`, `power1.out` | 2.5–4 s | slow push, long drift | carry, mask (soft wipe) | voice + soft foley; pad if music |
| trustworthy | `power2.out`, `power3.out` | 1.8–3 s | locked, gentle push | cut on motion, carry | clean clicks, one confirm tone |
| warm | `power2.out`, one `back.out(1.2)` | 1.5–2.5 s | handheld-feel drift | carry, material | wooden/marimba ticks, room tone |
| playful | springs (damping 0.6–0.8) | 0.8–1.6 s | bouncy push, snap zoom | material, cut, carry | pops tuned to a key, plucks |
| bold | `expo.out`, `power4.out` | 0.6–1.4 s | snap zoom, whip | cut, camera | one low impact per section |
| urgent | `expo.out`, `power3.in` exits | 0.4–1.0 s | whip, crash zoom | cut, camera, time | tight ticks, risers banned |
| premium | `power3.inOut`, `expo.out` | 2–3.5 s | dolly, rack focus | mask, camera (pull-back) | low drone or one piano note |
| technical | `power4.out`, `steps()` for counters | 1–2 s | snap to grid, pans | cut (match), mask (split) | mono blips, key runs |

Mismatches the audit flags: calm or premium cutting faster than 1.5 cuts/s, calm or premium using `back`/`elastic`, urgent holding a shot over 2 s, trustworthy using glitch transitions, more than two accent colours in one shot.

## 3. Transition library

Six families. Plain hard cuts on motion are the quiet base; spend the named ones on story turns (hook, reveal, proof, CTA). Each named transition at most once per film unless it is a deliberate motif. Every transition must answer "why this one, here?".

**Cut**
- *Hard cut on motion*: A leaves at peak speed, B opens mid-move on the same vector. Default.
- *Anchor match*: one object (avatar, logo mark, button) sits at identical coordinates across several cuts while everything around it changes. Good for "works everywhere".
- *Graphic match*: a shape or colour in A's last frame matches one in B's first (round avatar to round badge). Needs real alignment, not approximate.
- *Beat hold*: a one-frame freeze on the downbeat, then the cut. Showreels only.

**Carry**
- *Object carry*: the thing just clicked grows, moves or unfolds into the next scene. The strongest product transition.
- *Cursor carry*: the cursor lands, clicks, and what it clicked is what the next scene is about. At most three per film, with a slow deliberate cursor.
- *Type carry*: one word stays on screen while the scene rebuilds around it.
- *Line carry*: a rule, chart line or divider stretches into the next scene's horizon or border.

**Camera**
- *Push-through*: dive into a screen or a card until it becomes the next ground (log-space zoom).
- *Whip*: 0.3–0.45 s directional move with motion blur; B continues the same direction. Never two in a row.
- *Pull-back reveal*: the close-up turns out to be part of something bigger.
- *Parallax slide*: three layers slide at ~0.3×, 1×, 1.4× speed.

**Mask**
- *Brand-shape mask*: B is revealed through the product's own shape (the logo mark, the app's corner radius, the brand angle).
- *Subject iris*: an opening that starts on the subject, never on the frame centre.
- *Split strips*: three strips of B slide in with uneven stagger.
- *Ground wipe*: a feathered wipe in B's ground colour that starts 0.1–0.2 s before A's line ends.

**Material** (pairs with the papercut style)
- *Tape pull*: a strip slaps across the top and yanks the sheet away.
- *Tear*: a jagged rip, halves fall. Once per film at most.
- *Page turn*: a corner curl. Once per film at most.
- *Colour bleed*: B's colour spreads from the clicked element.

**Time**
- *Freeze and label*: freeze the frame, a label lands, the action resumes.
- *Speed ramp*: real footage fast-forwards through the boring middle of a task, ramping in and out.
- *Rewind*: reverse the motion just seen to show the "before". Only when the viewer saw the "after".
- *Time-lapse tick*: a clock or counter jumps while the picture steps.

## 4. Variety ledger

Log every shot as you storyboard, in `film.ledger.json` next to the composition:

```json
{
  "film": "crosslisty-launch-v2",
  "mode": "launch",
  "tone": "trustworthy",
  "tone_sentence": "I want to say your listings are finally in one place in a trustworthy tone, so the viewer feels relief.",
  "look": "light product film",
  "palette": ["#F7F6F2", "#14171F", "#14B8A6"],
  "music": {"bpm": 104, "key": "D", "groove": "half-time", "source": "synth"},
  "shots": [
    {"start": 0.0, "dur": 1.6, "transition": "cut:hard", "entrance": "word-rise", "ease": "power3.out", "direction": "up", "camera": "push"},
    {"start": 1.6, "dur": 2.4, "transition": "carry:object", "entrance": "scale-settle", "ease": "expo.out", "direction": "in", "camera": "push", "surprise": true},
    {"start": 4.0, "dur": 0.9, "transition": "camera:whip", "entrance": "already-moving", "ease": "power2.in", "direction": "left", "camera": "pan", "motif": "whip-left"}
  ]
}
```

`transition` is `family:name` for the cut *into* the shot. Tag deliberate repeats with `motif`; a good motif appears 2–3 times and changes on its last appearance. Mark at least one `surprise` every 15 s.

## 5. Variety audit

```bash
python3 scripts/variety.py check film.ledger.json        # rules inside the film + against the last 3 films
python3 scripts/variety.py log film.ledger.json          # after delivery: append to the history file
python3 scripts/variety.py report                        # what you keep reaching for
```

History lives in `~/.narrated-product-video/history.jsonl` (`--history` or `NPV_HISTORY` to move it). `check` fails on:

- the same transition on two consecutive cuts (motifs excepted);
- fewer than 3 transition families once there are 5+ cuts, or no carry/camera/mask transition at all;
- the same entrance three times in a row, or three same-direction entrances in a row;
- fewer than 3 eases, or one ease on more than half the shots;
- shot-length variation under 0.25, or more than 60 % of shots at the same length (±0.25 s);
- a tone mismatch from the matrix above.

It warns on any named transition used more than twice in a film under 60 s, no `surprise` within 15 s, and, against the last three films: the same look, the same music groove at a tempo within 10 %, or more than half of this film's named transitions already used there. Fix warnings by changing the idea, not by renaming rows.
