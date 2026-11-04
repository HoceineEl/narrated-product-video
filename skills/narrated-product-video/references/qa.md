# QA before sending

Run every check on the final file, not on intermediate renders.

```bash
python3 scripts/qa.py --script script.json --video final.mp4 --lang en
```

It transcribes the film (Parakeet) and fails on:

- a script sentence not heard, or heard twice (clipped or repeated lines);
- a pause between words longer than `--max-gap` (default 2.5 s);
- runs of flat frames (white or black flashes);
- a flat frame 0 (it is the thumbnail; a near-empty frame 0 is a warning);
- picture frozen longer than `--max-still` (1.5 s) anywhere before the last `--end-card` seconds (2.5 s), with total frozen time reported;
- a double cut (two cuts under `--min-shot`, 0.2 s, apart; fades are not counted as cuts);
- dead air (below −50 dBFS for over 1.2 s) and an audio track that ends at full level;
- a true peak above −1 dBTP, measured again after an AAC re-encode (AAC overshoots; a −1.1 dBTP master measured +1.1 after it).

Warnings: single-frame pops, mid-film sounds cut off, more than 25 % frozen, even shot lengths, and with `--cues cues.json` any sound under +3 dB or over +20 dB against the bed around it. Without `--script` it runs the picture and audio checks only (showreels, silent cuts). Tours with deliberate freezes can raise `--max-still`.

It matches letters in order, so transcription quirks ("480" for "four hundred eighty", "pick code" for "PickCode") do not fail the check, while a missing sentence does.

## Look at it

- Contact sheet at scene changes: `ffmpeg -i final.mp4 -vf "fps=1/3,scale=480:-1,tile=4x4" sheet.png`, then look for wrong highlights, cut-off columns, placeholder data and text overflow.
- Snapshot each key word time (`npx hyperframes snapshot --at <t>` for a launch film) and check the picture shows what the voice says at that moment.

## Critic rounds

Taste is judged by fresh critic agents, not by the builder: see `review.md`.

## Optional second opinion

`python3 scripts/vqa.py final.mp4 "List every moment where the narration and the picture disagree, with timestamps."` asks Gemini to watch the film. Verify each claim against frames; it invents details.

## Report honestly

Tell the user what was measured (transcript diff, gaps, loudness, blank frames) and what was looked at, and say plainly what nobody has listened to or watched in full.
