---
name: narrated-product-video
description: Produce narrated product videos for a web app end to end — a short punchy launch video (HyperFrames motion design, word-synced to a voice-over) and a long narrated app tour (Playwright screen recordings paced by the narration). Covers script writing with zero false claims, Gemini TTS voice-over (male/female, French/Arabic/English), Parakeet word alignment, recording with a fake cursor/captions, assembly with silence removal, SFX mixing, and automated QA. Use whenever the user asks for a launch video, promo, demo video, app tour, walkthrough, feature video, explainer with real app footage, or voice-over for a product video — even if they only say "make a video of the app" or "record a tour".
---

# Narrated Product Video

Two deliverables, one pipeline:

| | Launch video | App tour |
|---|---|---|
| Length | 60–75 s | 5–8 min |
| Visuals | HyperFrames composition (screenshots, motion, text) | Playwright recordings of the real app |
| Sync | every visual keyed to a spoken word | each narration beat drives a recorded action |
| Voice | one continuous energetic take | 3–5 group takes, calm "colleague showing a tool" |

Scripts in `scripts/` and `recorder/` are the proven implementation from a shipped project. Paths inside them point at that project's workspace (`$VIDEO_ROOT`, default `~/Downloads/my-app-videos`) — adapt `ROOT` and file names, keep the logic.

## The rules users enforced (read first)

These came from real rejections. Breaking any of them means a redo.

1. **Zero false claims.** Before recording, have a subagent fact-check every narration sentence against the code (labels, statuses, what a feature really does). Typical traps: a button that only validates vs "validate and post"; optional vs always; counts vs amounts; "one click" when it's two taps; features that need a binary (Ghostscript) absent locally. Use the app's exact UI labels in quotes.
2. **Never mention**: free trials, pricing, internal/dev pages (API playgrounds, admin), export formats the target user doesn't need, exclusivity lines ("reserved for X customers"). End on a punchy CTA ("Contactez-nous").
3. **No silence.** Voice talks continuously. Between lines the pause is ≤0.6 s median, ≤2.5 s max. Breaths between sentences are cut; breaths inside a clip are muted.
4. **Voice and picture in sync.** Text on screen appears on the word that says it. In the tour, the action happens while the line describes it.
5. **No clipped sentences, no repeated sentences.** Verify by transcribing the final mix and diffing against the script.
6. **Visual polish**: no italic serif accents (plain bold in brand color, optional underline sweep), no blank/white frames, highlight boxes from real DOM rects (never guessed), no crop that cuts a table column, no confusing data on screen (e.g. columns whose meaning needs explaining).
7. **One viewpoint per section** — e.g. the client side is shown entirely on the phone, not phone then desktop.
8. **Show the funny literal thing**: if the voice says "blurry photos" or "plastic bags", animate blurry crooked photos and an actual bag — not generic invoices.
9. **Most-used features first**; include onboarding (creating a client) and anything recently shipped (check `git log` for the client/app area before scripting).
10. Make demo data look real and complete (realistic invoices with stamps, multi-rate VAT, full entries).

## Pipeline

### 1. Research + script
- Read the app (routes, lang files, Livewire/Filament pages). `git log --since` for recent features.
- Write `script.json` (see `references/tour-script.example.json`): chapters → beats `{id, text}` + a `voice_style`. Launch: 8–10 lines, ~190 words, hook → problem → reveal → client POV → cabinet POV → bridge → CTA.
- Spell acronyms for TTS ("I.C.E.", "T.V.A.", "F.S. Compta") via a `norm()` map; keep brand spelling on screen.
- Fact-check subagent (rule 1) → fix lines → only then generate voice.

### 2. Voice (Gemini TTS) — `scripts/tts38.py`, `scripts/tts31.py`
- `gemini-3.8-flash-tts` via `POST /v1beta/interactions`; voice in `generation_config.speech_config[{voice}]` (e.g. `fr-fr-podcaster-4` launch, `fr-fr-podcaster-2` tour); style via `annotations:[{type:"speech_metadata",style}]`; audio in `steps[].content[].data` (base64 WAV 24 kHz). Timeout 900 s for long takes.
- `gemini-3.1-flash-tts-preview`: no `response_format` (returns L16 PCM → ffmpeg s16le), no speech_metadata.
- Free tier = 10 requests/day/key/model, 3/min. **Never retry a daily 429** (it burns quota). Batch API needs billing. Generate long group takes (a chapter group per request), not per sentence.
- Every take: master (`highpass 70, EQ, deesser, compressor, loudnorm -16`), transcribe, diff vs script. TTS hallucinates ("C'est vraiment puissant", "Prêt.", mangled brand names) and stumbles on brand-after-brand phrases — rephrase that sentence and regenerate. Fillers at beat edges ("Voilà") are trimmed by the aligner.
- To change only the ending, regenerate just that line and splice it at the word boundary instead of redoing the whole take.

### 3. Alignment — `scripts/align.py`
- Transcribe with `npx hyperframes transcribe file.wav -e parakeet -l fr` (Parakeet: accurate word times; whisper drifts and mislabels breaths).
- `align.py <script.json> <group> <audio> <transcript> <outdir>`: difflib-match script tokens to transcript words; cut each beat **at the midpoint before the next beat's first word** (never at the "last matched word" — mismatched acronyms make it cut mid-sentence); drop trailing fillers; mute inter-word gaps >0.22 s (breaths); apply `atempo=0.95` if the voice is rushed. **Seek on the input** (`-ss/-to` before `-i`) — filters like atempo shift output-side cuts.

### 4a. Launch video (HyperFrames) — `scripts/launch_build.py`, `references/launch-timeline.example.js`
- Composition template with `{{sN_start}}`/`{{sN_dur}}` placeholders; `launch_build.py` maps word onsets to keys (`T.fin`, `T.whats`…), fills scene bounds, inlines `window.T` + `RECTS` + timeline into `index.html` (lint needs the `__timelines` registration inline).
- Every tween is `at("word", offset)`. Spotlights: dim overlay `box-shadow: 0 0 0 4000px rgba(..,.4)` + 2px brand ring, placed from DOM rects captured in the **same session** as the screenshot (`getBoundingClientRect`, scaled to the image wrap).
- Initial states: use `tl.set(el,{opacity:0},0)` + `immediateRender:false` on later `fromTo`s. A `fromTo` with default immediateRender applies its start state at t=0 (a white flash layer covered the whole opening once).
- `npx hyperframes check` → snapshot key times → render `-q delivery`.
- SFX: `scripts/launch_cues.py` keys every cue to `T` (whoosh on scene change, clicks on taps, pops on chips, impact on logo). Synthesize missing sounds with ffmpeg (shutter = two filtered noise clicks; plastic bag = band-passed modulated noise). Mix with `scripts/mix.py` (sidechain duck, room tone, two-pass loudnorm). No music unless asked.

### 4b. App tour (Playwright) — `recorder/`, `scripts/tour_edit.py`, `scripts/tour_final.sh`
- `director.mjs`: recording context (patched recorder: x264, CRF 12, 30 fps), fake cursor, ripple, captions, chips, covers, spotlight, magenta **sync flash** + timestamped marks. Init scripts: `QUIET` (dismiss push/backup prompts) and a text-rewrite script that hides trial/pricing on the landing page.
- `common.mjs`: `beat(d, id, fn)` waits `beat_duration × 1.12 + 450 ms` (durations from the aligned `*.beats.json`), so recordings are paced by the real voice. Record **after** the voice exists.
- Phone scenes: render the app in an iframe inside a phone frame (`stageHtml`) with an iPhone UA (needed for "Prendre une photo"/capture inputs).
- Gotchas: `.filter({visible:true})` on every locator (hidden duplicates); `open()` without a cover must still uncover (it once left a blank card for a whole scene); uploads are dedup-hashed — re-encode a fresh copy for each re-recording; local missing binaries (Ghostscript) can be shimmed via env for recording only.
- `tour_edit.py` per take: detect flash → offset; start just after the chapter card uncovers; voice at `mark + 0.12 s`; if voice > room → freeze-frame pad; idle tail after voice → speed up to leave 0.25 s (cap per beat in `SPEED_CAP` for moments that must be seen, e.g. OCR status change); gaps between beats → ≤0.4 s; **fast-forward blank frames** (std < 6 on 64×36 gray); **overrun beats** (room ≫ voice): never tail-speed them — actions after the voice (dark toggle, menus) get crushed at 24×; instead fast-forward only static stretches (frame diff < 0.35 on 160×90 gray) and apply ≤2.2× uniform speed to the rest; zooms as an output-time `zoompan` post-pass (scale+crop on variable frame size gets clamped); push any overlapping voice later.
- `tour_final.sh` = master → transcribe → align all groups → edit → concat sting + takes + lock clip (cut from the launch render) → `tour_mix.py` → mux.

### 5. QA (always, before sending)
- Transcribe the final mix; diff vs script → no missing/clipped/repeated sentences.
- Voice-gap stats from `events.json` (median, max).
- Blank-frame scan of the final MP4.
- Contact sheets at scene changes (`ffmpeg -vf fps=1/15,scale,tile`); eyeball highlights and crops.
- Optional Gemini video QA (`scripts/vqa.py`) — verify its claims against frames; it invents things (e.g. "background music").
- Report what was checked by measurement vs watched.

## Learned on later projects (keep adding)

- **Voice is the default, never skip it.** If `GEMINI_API_KEY` is not in the env, load it the way earlier projects do: `a key file in an earlier video workspace or a project `.env` (a second key gives a separate quota). Validate with a free `GET /v1beta/models` before spending a TTS call. English voice that works: `en-us-podcaster-2` on `gemini-3.8-flash-tts`; a ~95-word launch script came back as one clean 36 s take.
- **Male, human-sounding English voice**: audition 3–4 voices on one short line first (cheap), then pick with earshot `rank` ("a man speaking casually and naturally") + `realness` + a quick autocorrelation f0 (male ≈ 90–130 Hz). Result 2026-10-29: `en-us-podcaster-1` (male, 110 Hz, most natural), `Charon` (95 Hz, more announcer), `en-us-podcaster-4` (127 Hz), `en-us-podcaster-3` reads female. Style prompt that kills the AI-announcer tone: "A senior front-end developer showing a tool to a friend at his desk, screen sharing. Relaxed, a little dry… real human pauses… Never an announcer, never salesy, no radio voice." Write the script like a dev talks: contractions, fragments, one dry punchline ("Yeah, no."), "Your call." Gemini then adds natural fillers ("uh") on its own.
- **No background music when the user says so**: drop the pad beds entirely; voice plus foley still scores launch-grade in earshot (−14.8 LUFS, onset density 3.9/s).
- **DNS flake**: if `curl` to `generativelanguage.googleapis.com` fails with exit 6 while `dig` resolves it, pin the IP in Python (`socket.getaddrinfo` override) instead of giving up.
- **Overlapping pane fades**: a pane's own fade-in must finish before the first switch fades it out, or the later `fromTo` wins and the pane stays visible (check reports `content_overlap`).
- **Give the payoff room**: splice ~1.2 s of silence into the take right before the claim line (`atrim` + `anullsrc` + `concat`) instead of rushing the before/after shot.
- **Retime the film to the voice**, not the other way round: scene `data-start` = anchor word onset + VO offset, and every in-scene event (hover, click, tab switch, counter landing) set to its word's local time.
- **Chrome extension subjects**: capture real states with Playwright `launchPersistentContext` loading the built `.output/chrome-mv3`, stub `chrome.runtime`/`chrome.storage`, inject the content script, and shoot at 1600×900 @2x so every rect maps to 1080p at ×1.2 (camera math stays exact). Pull real numbers from the page (e.g. `getComputedStyle` count) and real output (`window.<app>.output`) for code scenes; replace localhost hrefs.
- **No music catalog**: use the long mixkit pads from mixkit.co (long strings or synth uplifts) as beds at 0.05–0.13 under voice, plus foley from earshot (`sfx_render`: `swipe/glide`, `pro_hover_tick/soft`, `pro_typing_key/soft`, `pro_typing_run/soft`, `pro_pop/tink`, `pro_click/mouse`, `whoosh_fast/tight`, `pro_impact/air`). Skip `pro_logo_sting/sweep_hit`: earshot flags its rising glide as cheap.
- **Score the mix with earshot `critique`** after each render and fix its "FIX FIRST" items (silent opening, holes > 1.9 s, unsounded visual events) until it says launch-grade. Without voice an SFX-only film tops out at "close" on onset density; the voice fixes that.
- **HyperFrames audio**: give every `<audio>` an explicit `data-duration` (file length) and its own `data-track-index`, or check reports `duplicate_audio_track` because clips run to the film end. Initial hidden states go in `gsap.set` outside the timeline, not `tl.set(..., 0)`.
- **Master for social**: `acompressor` (−26 dB, 3:1, +4 dB makeup) → `volume` → `alimiter` at limit 0.78 so AAC overshoot stays under 0 dBTP; target −16 to −14 LUFS.

## Cost discipline
Batch voice by group, regenerate only changed groups, rebuild with cached alignment (`SKIPALIGN=1`), and fix with targeted re-records of single scenes. Keep the user posted with one line per milestone.
