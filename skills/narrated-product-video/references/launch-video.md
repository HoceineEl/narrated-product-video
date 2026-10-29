# Launch film (HyperFrames)

A 45–75 s film where every visual lands on the word that says it. Built as a HyperFrames composition (HTML rendered to video). Read the `hyperframes` skill for the composition contract if it is installed; this file covers what is specific to a voice-driven film.

## Order of work

1. Script, fact-check, voice take, master (see `script.md`, `voice.md`).
2. Transcribe the mastered take with Parakeet.
3. Capture real product states (screenshots + DOM rects) in one browser session.
4. Name the words that drive the picture (`anchors.json`), compute their times.
5. Build scenes whose `data-start` and in-scene tweens come from those times.
6. Sound effects keyed to the same times, mix, master (see `sound.md`).
7. `npx hyperframes check`, snapshots at key times, render `-q delivery`, QA.

## Retime the picture to the voice

Never stretch the voice to fit the picture. The voice is the clock.

```bash
python3 scripts/word_times.py --transcript transcript.json --anchors anchors.json --out T.json --offset 0.3
```

`anchors.json` is an ordered list of `[key, word]`. Anchor to words as the transcript spells them, not as the script does: Parakeet writes "480" for "four hundred eighty" and "pick code" for "PickCode", so the anchors are `["count", "480"]` and `["name", "pick"]`. See `examples/launch/anchors.json`.

- Scene start = its anchor word time (voice offset included), minus 0.1–0.4 s so the cut lands just before the word.
- Every in-scene event (hover, click, tab switch, a counter landing, a highlight) sits at its own word's time.
- With `--template index.tpl.html`, every `{{key}}` placeholder is filled with that time, so the composition never holds hand-typed timings.
- In GSAP, write every tween as `at("word", offset)`: `const at = (k, o = 0) => T[k] + o;`. See `examples/launch/timeline.js`.

## Capturing real states

- Use Playwright on the real app with demo data that looks complete and believable (real-looking names, full records, no "test123").
- Capture each screenshot together with the `getBoundingClientRect()` of every element you will highlight, in the same session and viewport. Rects from another session drift.
- Shoot at 1600×900 with `deviceScaleFactor: 2`: every rect maps to 1080p at ×1.2, so camera moves and spotlights stay pixel exact.
- Pull real numbers and real output from the page (`getComputedStyle` counts, generated code), never invented ones.

### Chrome extension subjects

Launch Chromium with `launchPersistentContext` and `--load-extension=<build dir>` (for WXT, `.output/chrome-mv3`). Stub `chrome.runtime` and `chrome.storage` where a content script expects them, inject the content script into a local demo page, and capture each state (hover card, panel, each tab). Replace localhost links in captured code.

## Visual rules

- Spotlights: a dim overlay (`box-shadow: 0 0 0 4000px rgba(0,0,0,.4)`) plus a 2 px brand ring, placed from captured rects, never guessed.
- No blank or white frames; no crop that cuts a table column; no data on screen that needs explaining.
- Emphasis in titles is bold in the brand color (an underline sweep is fine), not an italic serif.
- One viewpoint per scene.

## HyperFrames pitfalls seen in practice

- Hidden initial states: set them with `gsap.set` outside the timeline. A `fromTo` with default `immediateRender` applies its start state at t=0 and once covered the whole opening with a white layer.
- A pane's own fade-in must finish before the first switch fades it out, or the later tween wins and the pane stays visible (`check` reports `content_overlap`).
- Every `<audio>` needs an explicit `data-duration` (the file length) and its own `data-track-index`, or clips run to the film end and `check` reports `duplicate_audio_track`.
- Intentional overlaps and overflows need `data-layout-allow-overlap` / `data-layout-allow-overflow`.

## Pacing

- Give the payoff shot room: ~1.2 s of silence spliced before the claim line beats a rushed before/after.
- End card holds 2–3 s after the last word.
