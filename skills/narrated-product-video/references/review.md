# Review loop

The builder never grades its own film. Each round goes to a fresh critic agent that sees only the render, the brief and the owner's words: never your reasoning or your list of fixes. Run 2–4 rounds; stop when a round returns SHIP.

## Each round

1. **Machine checks first:** `python3 scripts/qa.py --video final.mp4 [--script script.json]`. Fix every hard failure before asking for taste.
2. **Frames for the critic:**
   ```bash
   ffmpeg -i final.mp4 -vf "fps=4,scale=480:-1,tile=6x6" sheet-%02d.png                   # contact sheets, 0.25 s apart
   ffmpeg -i final.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep pts_time  # cut times
   ffmpeg -ss <cut-0.1> -i final.mp4 -vf "trim=end_frame=8,scale=480:-1,tile=8x1" -frames:v 1 cut-<t>.png   # frames either side of each cut
   ```
   Add a 360 px wide sheet to judge phone-size legibility.
3. **Spawn a fresh critic** (a new subagent each round) with this brief:
   > You are reviewing a product film you did not make. Files: [sheets, cut strips, qa output, brief, owner's words]. Describe every contact-sheet frame in one sentence: what is on screen, what the hero is, whether it would pass as a slide. Check the frames either side of every cut for half states, text over text and a shot that starts from rest. Then name the **top 3 problems**, each with a timestamp, why it matters to a viewer, and a fix, scored 1–5 for severity. End with SHIP or ONE MORE PASS.
4. **Fix only those three**, one change per problem, in priority order: untrue or broken, then idea, connections between shots, hierarchy and scale, timing, surface, sound. Never tune eases while the idea is unclear.
5. Re-render into a new versioned file (never overwrite the last one) and rerun QA.

## Final pass

Give a fresh critic the previous round's report plus the new render. It marks each earlier problem FIXED, PARTLY or STILL THERE, lists any new regressions, and ends SHIP or ONE MORE PASS with at most 3 fixes. Keep a short ledger: round, file, problems, changes, result.

## Report to the owner

List the creative decisions you made on your own (so any can be overturned in one reply), what was measured, what a critic looked at, and plainly what nobody watched at full speed or listened to.
