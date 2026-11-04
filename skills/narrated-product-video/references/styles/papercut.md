# Papercut style (opt-in)

Use only when the owner asks for "papercut", "paper", "cut-out", "papercraft" or "stop-motion paper". The product story is acted out by flat paper props in a small diorama, with a taped headline banner and torn word tags. Launch films and showreels only; an app tour stays real footage (papercut may wrap its intro and outro cards). The workflow does not change: script, fact-check, voice, word times, then build.

## Kit

`assets/styles/papercut/`:

- `filters.svg`: paste inline at the top of `<body>`. Filters `#pc-paper` (fibre grain + slightly wobbly edge), `#pc-paper-flat` (grain only, for tape), `#pc-torn` (rough torn edge for tags).
- `papercut.css`: paste into the composition's inline `<style>`. Palette roles as CSS variables, `.pc-stage/.pc-cam` (camera), `.pc-wall/.pc-floor`, `.pc-frame` (paper monitor with `.pc-bezel`, `.pc-mat`, `.pc-glint`), `.pc-card`, `.pc-tape`, `.pc-banner-wrap > .pc-banner`, `.pc-tag`, `.pc-label`, `.pc-marker`, `.pc-vignette`, `.pc-tape-strip`.
- `papercut.js`: paste into an inline `<script>` before the timeline script (external `src` scripts can be hoisted). Exposes `PC`: `rnd(key)` seeded random, `grainLayer(stage)`, `life(tl, root, {duration})` (2-frame jitter on `[data-boil]` elements + 12 Hz grain reseed, seek-safe), `pop(tl, el, at)`, `tags(tl, container, words)` (one torn tag per spoken word, from Parakeet times), `marker(tl, path, at)` (red marker ellipse drawing on), `tapePull`, `tear`, `push`.
- Paper foley: `python3 scripts/paper_sfx.py --out-dir sfx/paper` makes pops, slides, rips, tape, stamp, flip, swish, drop and scribble in code. They read as stylised; prefer recorded paper foley (Kenney CC0, an earshot render) when the owner wants realism.


## Rules of the look

1. **Everything is paper**: flat fill, fine grain, slightly rough edge, soft drop shadow. No gradients, no outlines.
2. **Depth from stacked pieces**: shade is a separate darker strip of the same hue, highlight a lighter strip. Light from the top left; shadows fall down right. Front or side views only, no perspective.
3. **Two motion layers**: the world and camera move smoothly every frame (a slow push of 6–10 % per scene toward the focal prop). Only screen-space paper (banner, tags, labels) boils: it holds 2 frames, then jumps ±1–2 px and ±0.25°. Never boil the product UI or the world.
4. **Two voices of type**: the banner is heavy caps on cream paper and states a fact the voice does *not* say (muted viewers read the banners as a fact sheet; every banner goes through the fact-check). Tags are a chunky serif on coral torn paper, one per spoken word, popping on its onset (4 frames, `back.out`), never over a key UI element.
5. **Earned saturation**: muted, dusty backgrounds; bright colour only on the hero prop, tags and state signals (go, stop, amber). Re-theme by roles: brand accent first (`--brand-accent`), then muted complementary grounds.

## Real product only

**Never redraw the UI.** Real screenshots sit inside a paper frame (`.pc-frame`) or are taped onto a paper card (`.pc-card` + `.pc-tape`). Grain and wobble go on the bezel and the card, never on the screenshot itself. Highlights come from measured rects and use the red marker ellipse instead of the brand ring.

## Timing (30 fps)

| Move | Frames |
|---|---|
| Prop pop-in (scale 0 → 1, tilt ±4° → 0) | 6–9 |
| Tag pop (scale 0.6 → 1, y −8 → 0) | 3–5 |
| Slide-in with a small overshoot | 8–12 |
| Marker ellipse draw | 8 |
| State flip (dim to lit) | 1–2, hard swap |
| Transition (tape pull, tear, whip) | 7–12, each with its paper sound |

One discrete event per stressed word (every 0.4–0.8 s). Default cut is a hard cut on a banner change, 1.8–3 s per set. At most one tear or page turn per film. Paper never squashes: use overshoot instead.

## Layout

16:9: banner at 8–16 % of height, stage 18–78 %, tags 80–92 %. 9:16: banner 14–21 %, stage 22–68 %, tags 68–80 %, bottom 20 % empty for platform UI.

## Performance

Many live SVG filters slow the render. If a snapshot is slow, snapshot static props once to PNG and keep live filters only on animated pieces. All randomness goes through `PC.rnd` so every frame renders the same way twice.
