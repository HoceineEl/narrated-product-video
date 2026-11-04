# Motion craft

How things move, cut and read in every mode. Read it before building any HyperFrames scene, and again during review. Numbers are at 30 fps; double the frames at 60.

Contents: timing table · easing vocabulary · cuts and carries · camera · cursor · framing and legibility · rhythm · holds · look (blur, grain, grade) · never ship.

## Timing table

| Move | Frames | Seconds | Ease |
|---|---|---|---|
| Entry (translate or scale + opacity) | 10–12 | 0.33–0.40 | `power3.out` / `expo.out` |
| Entry tied to a spoken word | 8–11 | 0.24–0.38 | `power3.out` |
| Opacity helper under an entry | 4–6 | 0.12–0.20 | linear |
| Blur resolve (12 → 0 px) | 4–7 | 0.13–0.23 | `power2.out` |
| Exit | 6–9 | 0.20–0.30 | `power2.in` (accelerate away) |
| Word exit in a phrase swap | 3–4 | 0.10–0.13 | `power2.in` |
| Sibling stagger (rows, tiles) | 1–3, uneven | | |
| Word stagger | 2–5 (8–12 when the voice leads) | | |
| Camera push | 18 | 0.60 | `expo.out` |
| Camera pull | 21 | 0.70 | `power2.inOut` |
| Whip (peak around the cut) | 9–13 | 0.30–0.45 | `power2.in` → `power3.out` |
| Press: cursor down, up | 2, 3 | 0.07, 0.10 | `power2.out`, `back.out(1.7)` |
| CTA hero (logo, button) | 18–24 | 0.6–0.8 | `expo.out` snap |
| CTA supporting entries | 6 | 0.20 | `power3.out` |
| Last phrase fade | 10 | 0.33 | linear |

- An exit is 40–50 % shorter than its entry. Exits get new motion, never the entry reversed (a reversed entry reads as undo).
- Entries move on two channels at once: offset (10–28 px) or scale (0.86–0.99) plus a short opacity helper. Opacity alone has no direction and reads as a dissolve.
- Identity objects (logo, hero word, cursor) arrive from oversize and settle down to 1.0. Never grow a logo from zero.
- The next element starts when the previous one is 30–60 % done. Fully sequential looks robotic; all at once looks cheap.

## Easing vocabulary

Name the ease by its job, and use at least three per film:

| Job | GSAP | Shape |
|---|---|---|
| settle (text, panels) | `power3.out` | fast start, long tail |
| land (hero, CTA) | `expo.out` / `power4.out` | 80 % done by a quarter of the time |
| leave | `power2.in` / `power3.in` | ends at peak speed |
| reposition, camera | `power2.inOut` | S-curve |
| drift, counters, parallax | `none` / `sine.inOut` | constant or breathing |
| late lean (rare) | `back.out(1.4)` | overshoot after 35 % of the move |

**Default: one visible spring per film** (a cursor recovering from a press, or one state flip), because measured professional films overshoot on under 9 % of moves. **Option:** springs on all UI for a playful tone (damping 0.72–0.9, never on type, opacity or camera). The tone matrix in `tone-and-variety.md` decides.

Never the same `power2.out` at 0.5 s on everything; that is the flat default that makes a film feel generated.

## Cuts and carries

**No crossfades between scenes.** A dissolve between two UI plates ghosts text over text. Use a hard cut, a wipe in B's ground colour, a carried object, or a camera move.

**Default: cut on motion.** End A at peak velocity (a card mid-open, a whip at full speed) and open B already moving along the same vector. Never cut after everything has settled; settled-then-cut is a slide change. The meaning must have landed before the cut: cut while things move, not while the viewer is still reading. **Option:** one continuous morphing shape that never cuts, for a single-object story.

**Every boundary carries an object.** Something on screen survives the cut and moves into B: the cursor, the clicked card that becomes the next screen, a colour field, a caret, a string of text. Write a handoff table before building:

| Cut at | Carried object | A's last frame | B's first frame |
|---|---|---|---|
| 4.50 s | "New listing" card | x 1210, y 640, scale 1.0, moving right | x 1210, y 640, scale 1.0, growing to full screen |

Match the carried object's position (within ~2 % of frame), scale, colour and velocity on both sides. Bare cuts without a carry are for bursts of hits and the end card.

**Shots enter already moving.** Frame 1 of every shot has motion in progress: a push already 20 % in, a word half-risen. A shot that starts from rest after a cut doubles the stop.

**Transitions overlap the voice.** A transition starts 3–6 frames before the line ends; the next hero enters 3 frames before the transition completes.

## Camera

- One camera group per scene owns the UI's transform. Backgrounds drift on their own; headlines are not parented to the camera.
- **Push to the target, then move the cursor.** Push 0.6 s (`expo.out`, `transform-origin` exactly on the control), the cursor starts 0.1 s after the push settles, hold dead still through the click, pull back 0.7–0.85 s after the result appears. A camera moving during a click steals the click.
- Zoom multiplier by duration: 1.25× for a 6-frame punch, 1.4× for 12–18 frames, 1.5× for 20–45 frames. Above 2× only for a slow dive. Interpolate scale in log space for dives: tween a proxy `{ lz: Math.log(z0) }` to `Math.log(z1)` and set `scale: Math.exp(p.lz)` in `onUpdate`.
- Every hold carries a slow drift: 1–3 % scale over the hold, or 1–3 px/frame pan. A frozen camera on a held frame reads as a stalled render.
- Rack focus instead of dimming when one panel matters: blur the backdrop UI 4–7 px, never the type being read. Give blurred elements an explicit `filter: blur(0px)` start value.

## Cursor (launch films and tours)

- Draw it as a prop: about 44×54 px at 1080p, white fill, dark 1.6-unit stroke, real drop shadow. A life-size 24 px pointer vanishes.
- Duration from distance: `250 ms + 0.45 ms/px`, clamped 280–900 ms. The path bows sideways by ~8 % of its length (straight lines are the clearest fake-cursor tell; keep them for drags).
- Park 2–5 frames before pressing. Press: cursor to 0.86 scale about its tip in 2 frames, back in 3. The target reacts in the same frame: a colour step, a 3–6 % depress, or a tint.
- The word-locked moment is the click, not the departure; start travel 0.3–0.9 s before the word.
- Remove the cursor when its work is done: accelerate it off-frame or shrink it out in ~9 frames.
- Click feedback is a switch (see `app-tour.md`): the target's own reaction is always on; the ripple is `soft` in tours, `off` in launch films where the target squash is drawn.

## Framing and legibility

- **The subject fills 60–85 % of the frame** in feature beats. A small card in an empty field reads as cheap. A wide establishing shot is fine for under 1 s and is followed by a push.
- One close-up per operation: each step (pick, type, send) gets its own framing, and the camera follows the hand between them.
- **Readable text is arithmetic.** On-screen height = font px × capture scale × camera zoom × (output height / composition height). Floors, relative to frame height H:
  - anything the voice names or the viewer must read: ≥ 0.024 H (26 px at 1080, 46 px in a 1920-tall vertical);
  - proof text read in under a second: ≥ 0.04 H;
  - headlines 0.07–0.11 H; one hero number per film at 0.22–0.29 H.
  Magnify with the camera, not by inflating the type.
- Never enlarge past native pixels. A 2× capture holds up to 2× zoom on a 1080 frame; past that, recapture at a higher device scale or rebuild that one control from the app's own captured DOM and CSS.
- Crop to whole units: a button with its label, a row with its value, never half a column.

## Rhythm

- **No metronome.** The coefficient of variation of shot lengths is at least 0.25, and shot lengths span 4× or more (0.4 s hits beside 2 s reads).
- Never end two shots the same way in a row (alternate settle-and-cut, whip, carry, wipe).
- Cut every 0.3–2.3 s inside a busy beat; proof shots run 2–4 s of changing picture; scenes shorten toward the payoff; the last one lingers.
- A new element at most every 0.3 s on average, a major event at most every 0.8 s.
- Reading time: 0.3 s per word + 0.5 s, at least 1.2 s for anything that must be read, and no new text in the last 15 frames before a cut.
- Place one burst (3+ big changes inside 1.5 s, irregularly spaced) and one designed breath (0.6–1.5 s of near-stillness right before the payoff). Rests make bursts land.

## Holds

Something stays alive on every hold longer than 3 frames: a camera drift, a counter tick, a caret, a light moving across the hero. The only true stills are the designed breath before the payoff and the end card's last frames. `qa.py` measures still time and fails long frozen stretches outside the end card.

**End card: default 2–2.5 s after its last element lands, with a slow push**, landing on the last word or the music's final hit. A voice-led film needs that time for the call to action to be read. Option: ≤ 1.4 s for looping social clips, where a long card reads as a web footer.

## Look: motion blur, grain, grade

- **Motion blur, default:** put `data-motion-blur="on"` on the HyperFrames root (render-time blur along each element's real path; opt a subtree out with `data-motion-blur="off"`). Use it on films with whips or fast pushes. Never blur text that is being read.
- **Fallback blur** for a single fast move: a directional SVG blur (`feGaussianBlur stdDeviation="24 0"`) on frame 1 of the move, halving each frame for 3 frames.
- **Global shutter from frames:** render at 4× the target rate and average: `npx hyperframes render --fps 120 -o raw.mp4`, then `ffmpeg -i raw.mp4 -vf "tmix=frames=4,framestep=4" -r 30 -c:v libx264 -crf 16 -pix_fmt yuv420p blurred.mp4`. Four samples leave double edges on very fast moves; use 8 (`--fps 240`, `tmix=frames=8,framestep=8`) for whips.
- **Grain:** about 3 % temporal grain kills gradient banding. In the composition, a full-frame SVG `feTurbulence` layer at 0.06–0.1 opacity whose `seed` changes on a 12 Hz step derived from time (never per frame: per-frame grain multiplies file size). Post fallback: `ffmpeg -vf "noise=c0s=4:c0f=t"` and re-encode; never `-c:v copy` a graded master.
- **Grade restraint:** vignette at ~0.15 corner alpha, lifted blacks (ink near `#101014`, not `#000`), `contrast(1.04) saturate(1.06)` at most. If a viewer can name the effect, it is too strong.
- No `mix-blend-mode` or `backdrop-filter` across HyperFrames tracks; each track composites separately and the result can turn white. Use plain alpha.

## Never ship

- A crossfade between two UI scenes, or a white flash between scenes.
- A shot that starts from rest after a cut, or settles completely and then cuts.
- Scene counters, "01 / 06" labels, progress bars, timecodes, HUD corners, corner brand names on every shot.
- A held deck layout: headline left, device right, for more than one shot.
- Stat slides (a big centred number over a small label) or stat walls.
- Slogan triplets ("Fast. Simple. Powerful."), "Not just X, it's Y", "Unlock", "Meet X", "the future of".
- A circle wipe or colour flood on every beat; particles, confetti, glows on everything, gradient text.
- Text under 0.024 H that the voice names; a crop that cuts a row or a column.
- A spinner, skeleton, cookie banner, scrollbar or real personal data on screen.
- Frame 0 that is not a finished picture (it is the thumbnail).
- A film nobody looked at frame by frame (see `review.md`).
