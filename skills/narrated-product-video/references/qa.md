# QA before sending

Run every check on the final file, not on intermediate renders.

```bash
python3 scripts/qa.py --script script.json --video final.mp4 --lang en
```

It transcribes the film (Parakeet) and fails on:

- a script sentence not heard, or heard twice (clipped or repeated lines);
- a pause between words longer than `--max-gap` (default 2.5 s);
- runs of flat frames (white or black flashes);
- a true peak above −1 dBTP.

It matches letters in order, so transcription quirks ("480" for "four hundred eighty", "pick code" for "PickCode") do not fail the check, while a missing sentence does.

## Look at it

- Contact sheet at scene changes: `ffmpeg -i final.mp4 -vf "fps=1/3,scale=480:-1,tile=4x4" sheet.png`, then look for wrong highlights, cut-off columns, placeholder data and text overflow.
- Snapshot each key word time (`npx hyperframes snapshot --at <t>` for a launch film) and check the picture shows what the voice says at that moment.

## Optional second opinion

`python3 scripts/vqa.py final.mp4 "List every moment where the narration and the picture disagree, with timestamps."` asks Gemini to watch the film. Verify each claim against frames; it invents details.

## Report honestly

Tell the user what was measured (transcript diff, gaps, loudness, blank frames) and what was looked at, and say plainly what nobody has listened to or watched in full.
