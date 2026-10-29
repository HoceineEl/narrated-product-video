# Writing the script

The script decides the film. Write it from the product's code, not from its marketing page, and get it fact-checked before any voice is generated.

## Research

- Read the routes, UI labels (lang files, components), and the screens a new user sees first.
- Run `git log --since="2 months ago" --oneline` on the app's user-facing areas. Recently shipped features belong in the film.
- Collect real numbers from the product itself (a count on the page, an output size, a time saved you can measure). A real number beats an adjective.
- Use the app's exact UI labels, in quotes when spoken: "click Validate", not "click the confirm button".

## Fact-check (required)

Before generating voice, have a subagent check every sentence against the code and answer per line: true, false or overstated, with the file that proves it. Typical traps:

- A button that only validates, described as "validate and post".
- "Optional" features described as always on, or the reverse.
- Counts described as amounts, "one click" when it takes two.
- Features that depend on a binary or service missing locally (Ghostscript, a paid API).
- Claims of exactness ("pixel perfect") when a measurement says otherwise. Measure, then phrase it ("looks just like the original").

Fix the lines, then generate voice. A false claim found after recording costs a full retake.

## Never say

- Prices, free trials, discounts or plan limits unless the user asks for them. They change and date the film.
- Internal or developer pages (admin, API playground, debug tools).
- Export formats or settings the target viewer does not need.
- Exclusivity lines ("reserved for X customers").

## Launch film shape (45–75 s, 90–190 words)

hook (a pain the viewer has felt) → the old way, shown literally → reveal (product name + one action) → 3–5 proof beats, most used feature first → the payoff shot → claim line → brand + call to action.

- One idea per sentence. Fragments are fine: "For one card." "Your call."
- One dry punchline, not five. ("Yeah, no.")
- Show the funny literal thing: if the voice says "plastic bags of receipts", animate an actual bag.
- End on a short call to action that names where to get it ("Free to start on Chrome.", "Contact us.").

## App tour shape (5–8 min)

intro → onboarding (create the first record) → the 4–6 most used flows in the order a new user meets them → one recent feature → integrations → outro with the call to action.

- Chapters hold 2–6 beats. A beat is one or two sentences and one on-screen action.
- One viewpoint per chapter (all phone, or all desktop).
- Calm, "colleague showing a tool" tone; no hype words.

## Writing for a voice

- Spell acronyms the way they should be said, with a `norm()` map for the TTS text only ("I.C.E.", "T.V.A."); keep the brand spelling on screen.
- Avoid two brand names back to back; TTS stumbles there. Rephrase.
- Numbers: write them as words if the exact reading matters ("four hundred eighty").
- For a human developer voice: contractions, short fragments, one aside ("Double click if you want to read it first."). The model then adds natural fillers on its own.

## Format

```json
{
  "voice": "en-us-podcaster-1",
  "voice_style": "A senior front-end developer showing a tool to a friend...",
  "chapters": [
    {"id": "c01", "title": "Clients", "beats": [{"id": "c01a", "text": "..."}]}
  ]
}
```

A launch film is one chapter. See `examples/launch/script.json` (English, shipped) and `examples/tour/script.fr.json` (French, 14 chapters).
