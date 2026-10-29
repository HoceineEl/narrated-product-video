# Sound

Voice first, then sound effects on visible actions, then (only if asked) music.

## Sound effects

Key every cue to a word time from `T.json`, the same clock as the picture:

| On screen | Sound |
|---|---|
| scene change | short whoosh 0.3 s before the cut, lowpassed (~7 kHz) |
| click or tap | soft mouse click, slightly pitched per click |
| chip, badge, check | small pop or tick |
| typing | soft key run |
| logo or claim | one low impact, no rising glide |
| long busy stretch | a quiet bed (−20 dB or lower) under the voice |

Vary pitch by a semitone or two between repeats so a run of clicks does not sound copied. `examples/launch/cues.py` is a full cue sheet from a shipped film.

Free sources: Kenney (UI, interface, impact packs, CC0), Mixkit (whooshes, pads), BigSoundBank. If an audio tool such as the earshot MCP is available, render foley to a target duration and check candidates by listening metrics instead of by filename; it flags cheap-sounding sweeps.

## Music

No music unless the user asks. A voice plus foley mix scores as launch-grade on its own. When music is wanted, keep the bed 14–18 dB under the voice and let the mixer duck it.

## Mixing

```bash
python3 scripts/mix.py cues.json mix.wav --lib ui=~/sfx/kenney --lib pads=~/sfx/mixkit
```

The mixer places voice and effects, adds optional pink room tone (fills dead air between clips), ducks effects under the voice (attack 20 ms, release 250 ms), and runs two-pass loudnorm. Cue fields are documented in `scripts/mix.py --help`.

## Mastering for social

```bash
python3 scripts/master.py film render.mp4 final.mp4      # -14 LUFS, true peak about -2 dBTP after AAC
```

Compression (−26 dB, 3:1, +4 dB makeup), two-pass loudnorm, then a limiter at 0.7 so AAC overshoot stays well under 0 dBTP. Target −16 to −14 LUFS.

## Review

When an audio-analysis tool is available, score the final mix and fix its first items: a silent opening, holes longer than ~1.9 s, visual events with no sound, loudness off target. Without one, at least run `qa.py` (silence and loudness) and listen to the first and last 5 seconds.
