# App tour (Playwright recordings paced by the voice)

A 5–8 min walkthrough of the real app. The voice is recorded and aligned first; each recording then waits as long as its beat's audio, so the action happens while the line describes it.

## Order of work

1. Script with chapters and beats, fact-check, voice takes per chapter group, master.
2. Transcribe each take, cut beats: `python3 scripts/align.py --script script.json --audio g1-m.wav --transcript g1.json --out-dir beats --chapters c00,c01,c02 > g1.beats.json`
3. Record one take per chapter with the Director (below).
4. Assemble: `python3 scripts/tour_edit.py --takes takes --beats beats --config tour.json --out-dir build`
5. Sound and mix from `build/events.json` (see `examples/tour/mix_cues.py`), mux, QA.

## The recorder

`recorder/director.mjs` drives a Playwright page and draws an overlay (`recorder/overlay.js`) inside it: a smooth fake cursor, click ripples, captions, chapter covers, spotlights, check chips and a timer. It logs timestamped marks the editor uses.

```js
import { Director, launch, recordingContext } from '../recorder/director.mjs';
import { beat, loadBeats } from '../recorder/common.mjs';

loadBeats('g1.beats.json');
const context = await recordingContext(await launch(), { name: 'tour-clients', storageState: 'auth.json',
    theme: { accent: '#2563EB', ink: '#0F172A', paper: '#F8FAFC', brand: 'Ledgerly' } });
const d = new Director(await context.newPage(), 'tour-clients');
await d.open(url, { num: '02', title: 'Your <em>clients</em>', sub: '...' });
await beat(d, 'c01a', async () => { await d.click(page.getByRole('button', { name: 'New client' })); });
d.mark('out');
await d.finish();
```

Full example: `examples/tour/take.mjs`.

| Director method | Use |
|---|---|
| `open(url, cover?)` | load, show a chapter cover, flash the sync marker, uncover |
| `click(target)`, `moveTo(target)`, `type(locator, text)` | visible cursor actions with ripple |
| `spot(target)` / `unspot()` | dim everything but one element |
| `chip(target, text, {tone})` | small check or warning badge beside an element |
| `caption({kicker, title, sub})` / `hideCaption()` | lower-third caption |
| `scrollIntoView(locator)`, `smoothScroll(y)` | eased scrolling |
| `navigate(url, via?)` | SPA navigation (Livewire if present) with the cursor moving to the link |
| `mark(label)`, `finish()` | marks for the editor; saves `<TAKES_DIR>/<name>.mkv` + `.json` |

`recordingContext` options: `locale`, `timezoneId`, `zoom` (page zoom, default 1.25 for legibility), `userAgent`, `theme`, `logo`, `hide` (selectors to hide), `initScripts` (`rewriteText(...)` to swap trial or pricing copy, `presetStorage(...)` to pre-dismiss prompts).

## Pacing

`beat(d, id, fn)` runs the action, then waits until `beat_duration × SLACK + 450 ms` has passed (`SLACK` env, default 1.12). Record after the voice exists. `DRY=1` runs at quarter speed without the waits for a fast rehearsal.

## Authentication

Record with a saved `storageState`, created once: log in with Playwright and `context.storageState({ path: 'auth.json' })`. For a Laravel app, a signed dev-only login route (`URL::temporarySignedRoute`) created through `php artisan tinker` avoids typing passwords on camera.

## Phone scenes

Render the app inside an iframe in a phone frame with `stageHtml()` from `recorder/common.mjs`, and set an iPhone user agent so mobile-only inputs (camera capture) appear. Keep the whole chapter on the phone.

## Editing rules (`tour_edit.py`)

- Finds the magenta sync flash in each take to align marks with video time.
- Starts each take just after its chapter cover lifts; places each beat's voice at its mark + 0.12 s.
- Voice longer than the action: freeze-pads the last frame. Idle tail after the voice: fast-forwards to leave 0.25 s.
- Beats whose action must be seen get a `speed_cap` in `tour.json`; never tail-speed a beat whose action happens after the line (menus and toggles get crushed at 24×).
- Gaps between beats shrink to ≤ 0.4 s; runs of blank frames are skipped.
- Zooms (`zoom` in `tour.json`) are applied as an output-time `zoompan` pass, because scale+crop on variable frame sizes gets clamped.

## Gotchas

- Add `.filter({ visible: true })` to locators; responsive layouts often hold hidden duplicates.
- Uploads may be deduplicated by hash: re-encode a fresh copy of each file per recording.
- Playwright's built-in recorder writes low-bitrate VP8. For crisp text, record at 1920×1080 and re-encode the edit at CRF 16; a patched recorder (x264, CRF 12) is better still.
- A missing local binary can be shimmed for recording only; never let the film show a feature that fails without it.
