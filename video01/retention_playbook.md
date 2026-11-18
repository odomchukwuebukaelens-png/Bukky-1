# High-retention editing playbook

The target is 80% average view duration or higher. Every rule below is applied in `shotlist.md` and `edl.json`.

## 1. The 2-second law (visual change at least every 2.0 seconds)
`build.py` enforces this automatically. The current edit has **467 shots in 10:07, averaging 1.35s, with none longer than 2.0s**. When a single idea needs to stay on screen longer, it isn't held. The software adds a *micro-change* instead, cycling through these:

| Micro-change | What it looks like |
|---|---|
| Punch-in 112% | Instant tighter crop on the same shot (a "jump-zoom") |
| Angle shift | Cut to a second camera on the same moment |
| Rack focus | Focus pulls from foreground to background |
| Reverse drift | The camera's slow move reverses direction |
| Light flicker / exposure dip | The lamp stutters; the frame darkens for 3 frames |
| Snap-zoom out | Fast pull back that reveals more of the room |
| Parallax slide | Foreground and background layers slide at different speeds |
| Dutch tilt 5° | The frame tilts slightly. Used only in tense beats |

Even "static" shots always have **life inside them**: steam, dust motes, candle flicker, a tear sliding, breathing. A frame is never fully frozen. The only exception is the deliberate HARD FREEZE at 0:35, where the stillness *is* the scare.

## 2. The first 30 seconds (where most viewers decide to stay or leave)
- **Frame 1 is the scariest image in the video** (mom's unblinking eyes). No logo, no "hey guys", no intro animation.
- **The title is answered within 3 seconds.** "If your family ever stops blinking at dinner, keep eating."
- **A sharp tonal switch at 0:11.** Two comedic "I'm not talking about…" shots with a warm palette, then a smash cut to black. The contrast makes the horror hit harder.
- **0:35 is the pattern break.** Every sound cuts out (music, room tone, chatter) and the colour drains to sick green. The silence is the hook.

## 3. Open loops (reasons to stay)
| When it opens | Loop | When it closes |
|---|---|---|
| 1:12 | "Most people break the **second** rule in the first ten seconds" | 2:24 (Rule 2) |
| 1:12 | "The **last** rule only works if you've eaten slowly your whole life" | 8:21 (Rule 7) |
| 1:12 | The menu card shows rule 7 **redacted** on screen | 8:21, when the redaction burns away |
| 0:07 | "Don't look at the empty chair": who is sitting there? | 9:34 (five chairs) |
| 4:11 | "Whatever you eat, you owe the guest": what happens if you do? | 5:00–6:00 (the twins story) |

Never close a loop without opening the next one first.

## 4. Progress cues (they reduce mid-video drop-off)
- A persistent **HUD** at the top: `SUNDAY DINNER // RULE 3 OF 7`. Viewers always know how far along they are.
- **Rule cards** ("Tonight's Menu", course N) with a stinger sound each time. They work as chapter resets.
- YouTube **chapters** in the description, named to create curiosity ("Rule 7: [Not for you yet]").

## 5. Pattern interrupts (roughly every 20–40 seconds)
- **Kinetic text slams:** "DON'T.", "RUDE.", "SLOW DOWN.", always with an impact sound.
- **Format switches:** blueprint diagrams (explainer mode), VHS home video (memories), case-file folder (the twins), receipt print-out (comedy), triptych split screens (eyes).
- **Colour-mood switches:** warm (normal), sick green (frozen), candle-dark (late night), sepia/VHS (memories).
- **Comedy beats every 1–2 minutes** release tension so the next scare lands: the 2x-speed eating gag, cutting a single grain of rice, "BALANCE OWED: 1 SPOONFUL".
- **Silence drops** before big lines ("Dinner is over." is followed by 1.2s of nothing).

## 6. Sound design rules
- Narration sits on top, always clear. Music sits about −20 dB under the voice and ducks a further 6 dB while words are spoken.
- **Every cut that matters gets a sound:** whoosh on whip-pans, stamp on stamps, stinger on rule cards, tick on the rice grain.
- **Music cues by section:**

  | Time | Cue |
  |---|---|
  | 0:22–0:35 | Warm Sunday |
  | 0:35 onwards | Dread bed |
  | Rules 4–6 | Tension pulse |
  | 7:31 twist | Memory piano |
  | Final 30 seconds | End lullaby |

- The rice grain landing, the chair scraping and the chewing are mixed **louder than realistic**. In horror, small sounds are the scares.

## 7. Captions
- Burned-in, bold, ALL CAPS, 1–4 words per chunk, bottom centre, with a thick outline.
- **The word currently being spoken is lit in our acid green.** Eyes track the colour, which keeps them on screen.
- The first word of each chunk pops in slightly (108% to 100% scale).

## 8. The ending (it protects the average view duration *and* drives the next view)
- There's no "thanks for watching" outro. The last line is the sting ("count the chairs"), then a hard cut to black.
- The end screen sits over the final ~10 seconds of black and points to the next rules video, so viewers carry on instead of leaving.

## 9. Before every upload
- [ ] No shot longer than 2.0s (`build.py` prints `over2s 0`)
- [ ] Frame 1 is a scare, not a logo
- [ ] Every rule card has a stinger and updates the HUD
- [ ] At least one open loop is always active
- [ ] Comedy beat at least every 2 minutes
- [ ] Captions line up with the voice (check 3 random points)
- [ ] Audience set to "not made for kids"; AI disclosure on
