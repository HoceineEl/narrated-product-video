---
name: narrated-product-video
description: Produces product videos for a web app or browser extension, end to end - a narrated launch film, a music-cut showreel or promo, or a long app tour of the real product. HyperFrames motion design keyed to Gemini TTS word times or a shared beat grid, Playwright recordings with auto-zoom on clicks, a fact-checked script, sound, mastering, vertical 9:16 and 4:5 cutdowns with captions, an optional papercut (paper cut-out) look, fresh-critic review rounds and automated QA. Use when the user asks for a launch video, launch film, promo, showreel, sizzle reel, product demo, demo video, app tour, walkthrough, feature video, social cutdown, reel, or a papercut / paper cut-out explainer, even if they only say "make a video of the app" or "record a tour".
license: MIT
compatibility: Needs ffmpeg, Python 3 with numpy, Node 20+, and the Gemini API (GEMINI_API_KEY) for voice. Launch films and showreels need the HyperFrames CLI (npx hyperframes); app tours and brand capture need Playwright; caption burn-in needs Pillow.
metadata:
  version: "3.0.0"
  author: HoceineEL
---

# Narrated Product Video

Pick a clock, make every picture land on it, and show the real product. The voice is the clock in a launch film and a tour; the beat grid is the clock in a showreel.

| | Launch film | Showreel | App tour |
|---|---|---|---|
| Length | 45–75 s | 15–60 s (+ 9:16, 4:5 cutdowns) | 5–8 min |
| Clock | voice word times | beat grid shared by picture and music | each beat's audio |
| Picture | HyperFrames from real screenshots | HyperFrames, cut to bars | Playwright recordings of the real app |
| Guide | `references/launch-video.md` | `references/showreel.md` | `references/app-tour.md` |

If the request does not say which, make the launch film. "Promo", "sizzle", "reel" or "cut to music" means a showreel.

**Style:** default is clean product motion. Use `references/styles/papercut.md` only when the owner asks for papercut, paper, cut-out or papercraft.

## Workflow

Copy this checklist and keep it updated:

```
- [ ] 1. Research the app, write script.json                 references/script.md
- [ ] 2. Fact-check every sentence against the code (subagent)
- [ ] 3. Brand kit from the site, owner approves preview     launch-video.md (Brand kit)
- [ ] 4. Tone sentence, storyboard, shot ledger, variety     references/tone-and-variety.md
- [ ] 5. Voice: key, audition, take, master, transcribe      references/voice.md
- [ ] 6. Build the picture on its clock                      motion.md + the mode guide
- [ ] 7. Sound effects (and music in a showreel), mix        references/sound.md
- [ ] 8. QA, then fresh-critic review rounds                 references/qa.md, references/review.md
- [ ] 9. Cutdowns if asked; log the ledger to history        showreel.md, variety.py log
```

Report one line per milestone. Generate voice only after step 2; a false claim found later costs a retake.

## Rules that came from rejected cuts

1. **Every claim is true.** Exact UI labels; measure before saying "exact" or "one click".
2. **Never mention** prices, trials, plan limits, internal pages or exclusivity unless asked.
3. **No dead air.** Median pause ≤ 0.6 s, longest ≤ 2.5 s; no frozen picture over 1.5 s before the end card.
4. **In sync.** Text lands on its word (0–2 frames early); actions happen during their line; cuts sit on the clock.
5. **Nothing clipped or repeated**, proven by transcribing the final mix.
6. **Real picture.** Real screens, real numbers, rects from captured DOM, complete demo data, personal data redacted at the source. Never redraw the UI, in any style.
7. **Motion craft.** No crossfades between scenes, cut on motion with a carried object, shots enter moving, subject fills 60–85 %, readable text ≥ 0.024 of frame height after zoom (`motion.md`).
8. **Not like the last film.** One tone sentence, transitions from the library, `variety.py check` clean.
9. **Most used features first**, then onboarding and recent work (`git log`).
10. **No music unless asked** (a showreel request is an ask).

## Scripts

Run any script with `--help` first; they are meant to be called, not read.

| Script | Does |
|---|---|
| `scripts/tts.py` | Gemini TTS take (`--check` validates the key for free) |
| `scripts/master.py` | `voice` master a take, `film` master a video, `measure` loudness |
| `scripts/word_times.py` | transcript + `anchors.json` to `T.json`; fills `{{key}}` in a composition |
| `scripts/beats.py` | beat grid, template fill, snap words to beats, analyze/fit a track, `synth` a score |
| `scripts/align.py` | cut a take into one clean clip per beat (tour) |
| `scripts/mix.py` | voice + cue sheet to a ducked, loudness-normalized mix |
| `scripts/tour_edit.py` | assemble tour takes: sync, freeze-pad, load holds, auto-zoom, fast-forward |
| `scripts/cutdown.py` | 9:16 / 4:5 / 1:1 reframe with safe zones and burned captions |
| `scripts/variety.py` | shot-ledger audit against the film's tone and the last 3 films |
| `scripts/qa.py` | frame 0, frozen time, blanks, double cuts, dead air, peaks after AAC, transcript diff |
| `scripts/paper_sfx.py` | paper foley made in code for the papercut style |
| `scripts/vqa.py` | optional Gemini watch-through |
| `recorder/` | Playwright Director (cursor, press, ripple switch, redaction, act marks) and `brand_kit.mjs` |

Transcription: `npx hyperframes transcribe <file> -e parakeet -l <lang>`.

## Examples

- `examples/launch/`: shipped PickCode launch film script, anchors, word-keyed GSAP timeline, SFX cue sheet.
- `examples/tour/`: 14-chapter French tour script, `tour.json`, a Director take, events-to-mix step.
- `examples/showreel/`: a 12.5 s beat-grid showreel template (push-then-cursor, whip, anchor-match burst, end card on the final downbeat) and its shot ledger.

## Cost discipline

Batch voice by chapter group and regenerate only changed groups. Never retry a daily quota error. Re-record single scenes, re-render only changed ranges, and reuse cached transcripts when only the picture changes.
