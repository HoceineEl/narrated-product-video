---
name: narrated-product-video
description: Produces narrated product videos for a web app or browser extension, end to end. Makes a short launch film (HyperFrames motion design, every visual synced to a word of the voice-over) and a long app tour (Playwright recordings of the real app, paced by the narration). Covers a fact-checked script, a natural Gemini TTS voice-over (English, French, Arabic), word alignment, sound effects, mixing, mastering and automated QA. Use when the user asks for a launch video, promo, demo video, product video, app tour, walkthrough, feature video, explainer with real app footage, or a voice-over for one, even if they only say "make a video of the app" or "record a tour".
license: MIT
compatibility: Needs ffmpeg, Python 3 with numpy, Node 20+, and network access to the Gemini API (GEMINI_API_KEY). Launch films need the HyperFrames CLI (npx hyperframes); app tours need Playwright.
metadata:
  version: "2.0.0"
  author: HoceineEL
---

# Narrated Product Video

The voice is the clock. Write a script that is true, record the voice, then build the picture so every action lands on the word that describes it.

| | Launch film | App tour |
|---|---|---|
| Length | 45–75 s | 5–8 min |
| Picture | HyperFrames composition from real screenshots | Playwright recordings of the real app |
| Sync | each visual keyed to a word time | each beat's action waits for its audio |
| Voice | one continuous take | one take per group of chapters |
| Guide | `references/launch-video.md` | `references/app-tour.md` |

If the request does not say which, make the launch film.

## Workflow

Copy this checklist and keep it updated:

```
- [ ] 1. Research the app and write script.json          references/script.md
- [ ] 2. Fact-check every sentence against the code (subagent)
- [ ] 3. Voice: check key, audition, take, master         references/voice.md
- [ ] 4. Transcribe and diff against the script
- [ ] 5. Build the picture on the voice's word times      launch-video.md or app-tour.md
- [ ] 6. Sound effects, mix, master                       references/sound.md
- [ ] 7. QA the final file                                references/qa.md
```

Report one line per milestone to the user. Generate voice only after step 2; a false claim found later costs a retake.

## Rules that came from rejected cuts

1. **Every claim is true.** Use the app's exact UI labels; measure before saying "exact" or "one click".
2. **Never mention** prices, trials, plan limits, internal or developer pages, or exclusivity lines unless asked.
3. **No dead air.** Median pause between lines ≤ 0.6 s, longest ≤ 2.5 s; breaths inside a clip are muted.
4. **In sync.** Text appears on the word that says it; in a tour, the action happens during its line.
5. **Nothing clipped or repeated.** Proven by transcribing the final mix.
6. **Real picture.** Real screens, real numbers, highlights from captured DOM rects, demo data that looks complete. No blank frames, no crop that cuts a column.
7. **One viewpoint per section** (all phone or all desktop).
8. **Show the literal thing** the voice names, not a generic stand-in.
9. **Most used features first**, then onboarding and anything shipped recently (`git log`).
10. **No music unless asked.** Voice plus sound on visible actions.

## Scripts

Run any script with `--help` first; they are meant to be called, not read.

| Script | Does |
|---|---|
| `scripts/tts.py` | Gemini TTS take (`--check` validates the key for free) |
| `scripts/master.py` | `voice` master a take, `film` master a finished video, `measure` loudness |
| `scripts/word_times.py` | transcript + `anchors.json` to `T.json`; fills `{{key}}` placeholders in a composition |
| `scripts/align.py` | cut a take into one clean clip per beat (tour) |
| `scripts/mix.py` | voice + cue sheet to a ducked, loudness-normalized mix |
| `scripts/tour_edit.py` | assemble tour takes: sync, freeze-pad, fast-forward idle, zoom |
| `scripts/qa.py` | transcript diff, pauses, blank frames, loudness; exits 1 on failure |
| `scripts/vqa.py` | optional Gemini watch-through of the final film |
| `recorder/` | Playwright Director: fake cursor, captions, covers, spotlights, sync marks |

Transcription uses `npx hyperframes transcribe <file> -e parakeet -l <lang>`.

## Examples

- `examples/launch/`: the shipped PickCode launch film script (male developer voice), its anchors, a GSAP timeline keyed to words, and a full SFX cue sheet.
- `examples/tour/`: a 14-chapter French tour script, a `tour.json` editor config, a Director take, and the events-to-mix step.

## Cost discipline

Batch voice by chapter group and regenerate only changed groups. Never retry a daily quota error. Re-record single scenes rather than whole tours. Reuse cached transcripts and beat clips when only the picture changes.
