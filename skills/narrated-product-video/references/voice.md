# Voice-over with Gemini TTS

`scripts/tts.py` wraps the Gemini interactions API. Validate the key first; it is free:

```bash
python3 scripts/tts.py --check
```

If `GEMINI_API_KEY` is not in the environment, look for one the user already has (a project `.env`, an earlier video workspace) before asking. Never print the key.

## Models

| Model | Output | Style direction |
|---|---|---|
| `gemini-3.8-flash-tts` (default) | 24 kHz WAV | `speech_metadata` annotation, follows direction well |
| `gemini-3.1-flash-tts-preview` | raw L16 PCM, converted by the script | style is prepended to the text |

Free tier: about 10 requests per day per key per model, 3 per minute. Never retry a daily 429; it burns quota. Generate one take per launch film, or one take per chapter group for a tour, not one per sentence.

## Picking a voice

Audition 3–4 voices on one short line (cheap), then choose by listening tools, not by name:

```bash
for v in en-us-podcaster-1 en-us-podcaster-4 Charon; do
  python3 scripts/tts.py --voice $v --style "$STYLE" --text "Hit Alt, Shift, C. That's the whole trick." --out aud-$v.wav
done
```

If an audio-analysis tool is available (for example the earshot MCP), rank the auditions against "a man speaking casually and naturally" and check realness. A quick pitch estimate separates male (≈ 90–130 Hz) from female voices.

Known results:

| Voice | Notes |
|---|---|
| `en-us-podcaster-1` | male, ~110 Hz, most natural and casual; best for a developer voice |
| `en-us-podcaster-2` | neutral, clean single take for a 95-word script |
| `Charon` | male, ~95 Hz, more announcer |
| `en-us-podcaster-4` | male, ~127 Hz |
| `en-us-podcaster-3` | reads female |
| `fr-fr-podcaster-4` | French, energetic launch read |
| `fr-fr-podcaster-2` | French, calm tour read |

## Style direction

Describe a person in a situation, not adjectives. This one removed the AI-announcer tone:

> A senior front-end developer showing a tool to a friend at his desk, screen sharing. Relaxed, a little dry, genuinely amused by how annoying the old way is. Conversational, with real human pauses and small emphasis on the punchlines. Never an announcer, never salesy, no radio voice.

## After every take

1. Master: `python3 scripts/master.py voice take.wav take-m.wav` (highpass, EQ, de-ess, compression, −16 LUFS, 48 kHz).
2. Transcribe: `npx hyperframes transcribe take-m.wav -e parakeet -l en` (Parakeet gives accurate word times; Whisper drifts and labels breaths as words).
3. Diff the transcript against the script. TTS sometimes adds lines ("It's really powerful."), drops a word, or mangles a brand. Rephrase that sentence and regenerate.

## Fixing part of a take

- To change one line, regenerate only that line with the same voice and style, and splice it at a word boundary from the transcript.
- To give a payoff room, splice ~1.2 s of silence before the claim line: `atrim` the take at the word boundary, `anullsrc` for the gap, `concat`.
- If the read is rushed, slow beats with `align.py --tempo 0.95`.

## Network

If `curl` to `generativelanguage.googleapis.com` fails with exit 6 while `dig` resolves it, pass `--pin-ip <address from dig>`; the script overrides DNS for that host only.
