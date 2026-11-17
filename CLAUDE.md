# Abyss Theory video production

Channel: Abyss Theory (ocean animals, faceless, animated explainers). Videos are built with Remotion in `video/` and rendered on a RunPod pod with `render.sh`.

## Rules from the channel owner (16 Nov 2026)

- **No visual beat longer than 5 seconds.** Every 5 seconds or less, something on screen must change in step with the narration: a new shot, a new element, a camera move, a text change. Write scripts in beats of roughly 12–14 words and give each its own visual. `python3 tools/check_beats.py` (run from `video/`) must pass before a render is handed over.
- **Copy the formula, not the structure.** Study what makes a successful video work (hook type, pacing, payoff) and bend it to an adjacent angle. Never reproduce another channel's titles, thumbnail look, on-screen graphics or scene order one to one.
- Voiceover uses the owner's ai33.pro cloned voice "Deep sea" (`clone_2719063`) at speed 0.95; the owner has confirmed the rights to it.

## Channel identity (ours, keep it distinct)

The owner approved this style on 16 Nov 2026 for all videos after the octopus one (the octopus video stays as rendered). Decided after studying two reference videos frame by frame (Depth Theory's sperm whale video and Ice Wild's elephant seal video). The first octopus cut looked too much like Depth Theory (flat diver and animal on dark teal, all-caps captions); do not repeat that look.

- **Framing:** second-person encounter, "What Happens When a ___ ___ You".
- **Signature device: the dive computer.** The viewer is the diver. The frame carries a heads-up display (depth, air remaining, dive time) and every fact arrives as an instrument readout or a "scan" of the animal. Air remaining drains across the video as a built-in tension and progress cue.
- **Evidence labels in our own words:** LOGGED (measured, sourced), REPORTED (credible but single-source), MYTH. Each carries its source on screen. No claim without one.
- **Animation is the main style (owner, 17 Nov 2026).** Most of every video is flat 2D animation of the animal and the action, in the manner of Depth Theory's animated explainers: characters moving in a scene, cutaways, scale comparisons, diagrams. This is the fallback whenever live footage is not available. Text-on-a-grid cards are not a substitute for animation.
- **Order of use:** animation most; then live footage or photorealistic video clips, used occasionally; then still photos, only a few per video. The first crocodile cut overused stills and text cards; do not repeat that.
- **Footage sources:** free-to-use only (Pexels via its API, NOAA, Wikimedia Commons CC0/public domain/CC BY, Pixabay). Record every clip's source and licence in `video/footage/SOURCES.md`. Never use clips from other channels.
- **Keep it ours:** the animated scenes still use our own characters, colours, dive-computer instruments and evidence labels, never Depth Theory's own graphics, titles or scene order.
- **Open with a promise:** a hook in the first 15 seconds, the question by 30 seconds, then a short on-screen list of what the dive will reveal.
- **Sound:** a continuous instrumental music bed under the voice (no human voice in the music); both references have almost no silent moments. For the crocodile video the owner allowed music from ai33.pro (17 Nov 2026); for later videos the owner generates the music and sends it, so do not spend ai33.pro credits on music unless told to.
- Type: Montserrat 800 for headlines, a monospace face for instrument readouts. Colour: deep teal, yellow accent, HUD cyan.

## Workflow

1. Script in `video/script/NN-name.md`, one `## N. Title` section per scene, `**Visual:**` notes, `[CHECK]` on any claim without a primary source.
2. `python3 tools/voiceover.py script/<file> <name>` generates per-scene audio and word timings.
3. Scenes cue visuals to spoken phrases with `makeCue`; `tools/check_cues.py` and `tools/check_beats.py` validate them.
4. Review stills with `tools/stills.mjs`, then the owner renders on the pod with `bash render.sh <Composition>` (`Main` = octopus, `Croc` = crocodile).
5. Checks take the video name: `python3 tools/check_cues.py --video=croc` and `python3 tools/check_beats.py --video=croc 5`.
