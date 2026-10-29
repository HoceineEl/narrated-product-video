# narrated-product-video

An agent skill that produces narrated product videos for a web app, end to end:

- **Launch video** (45–75 s): HyperFrames motion design, every visual keyed to a word of the voice-over.
- **App tour** (5–8 min): Playwright recordings of the real app, paced by the narration.

It covers the script (fact-checked against the code, no false claims), Gemini TTS voice-over in English, French or Arabic, Parakeet word alignment, a fake cursor with captions and spotlights, silence removal, SFX mixing, mastering for social, and QA by transcribing the final mix.

## Install

```bash
npx skills add HoceineEL/narrated-product-video
```

Or copy `skills/narrated-product-video` into `~/.claude/skills/`.

## Requirements

- `ffmpeg`, Node 20+, Python 3 with `numpy`
- [HyperFrames](https://hyperframes.dev) CLI (`npx hyperframes`) for launch videos and Parakeet transcription
- Playwright for app tours
- `GEMINI_API_KEY` for the voice-over
- Optional: `VIDEO_ROOT` for the video workspace (default `~/Downloads/my-app-videos`)

## Use

Ask your agent for "a launch video for this app", "a narrated tour of the dashboard" or "a voice-over for this promo". The skill reads the app, writes the script, generates the voice and builds the video.

## License

MIT
