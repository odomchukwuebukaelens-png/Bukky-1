# Abyss Theory video production

Channel: Abyss Theory (ocean animals, faceless, animated explainers). Videos are built with Remotion in `video/` and rendered on a RunPod pod with `render.sh`.

## Rules from the channel owner (16 Nov 2026)

- **No visual beat longer than 5 seconds.** Every 5 seconds or less, something on screen must change in step with the narration: a new shot, a new element, a camera move, a text change. Write scripts in beats of roughly 12–14 words and give each its own visual. `python3 tools/check_beats.py` (run from `video/`) must pass before a render is handed over.
- **Copy the formula, not the structure.** Study what makes a successful video work (hook type, pacing, payoff) and bend it to an adjacent angle. Never reproduce another channel's titles, thumbnail look, on-screen graphics or scene order one to one.
- Voiceover uses the owner's ai33.pro cloned voice "Deep sea" (`clone_2719063`) at speed 0.95; the owner has confirmed the rights to it.

## Channel identity (ours, keep it distinct)

Decided 16 Nov 2026 after studying two reference videos frame by frame (Depth Theory's sperm whale video and Ice Wild's elephant seal video). The first octopus cut looked too much like Depth Theory (flat diver and animal on dark teal, all-caps captions); do not repeat that look.

- **Framing:** second-person encounter, "What Happens When a ___ ___ You".
- **Signature device: the dive computer.** The viewer is the diver. The frame carries a heads-up display (depth, air remaining, dive time) and every fact arrives as an instrument readout or a "scan" of the animal. Air remaining drains across the video as a built-in tension and progress cue.
- **Evidence labels in our own words:** LOGGED (measured, sourced), REPORTED (credible but single-source), MYTH. Each carries its source on screen. No claim without one.
- **A new visual device every scene.** Do not reuse "character on a background plus a caption". Rotate through scans, gauges, scale comparisons, maps, counters, split screens, cutaways and licensed real footage.
- **Media mix:** licensed stock footage or photos for the real animal, animation for what cameras cannot show. Never use clips from other channels.
- **Open with a promise:** a hook in the first 15 seconds, the question by 30 seconds, then a short on-screen list of what the dive will reveal.
- **Sound:** a continuous music bed under the voice; both references have almost no silent moments.
- Type: Montserrat 800 for headlines, a monospace face for instrument readouts. Colour: deep teal, yellow accent, HUD cyan.

## Workflow

1. Script in `video/script/NN-name.md`, one `## N. Title` section per scene, `**Visual:**` notes, `[CHECK]` on any claim without a primary source.
2. `python3 tools/voiceover.py script/<file> <name>` generates per-scene audio and word timings.
3. Scenes cue visuals to spoken phrases with `makeCue`; `tools/check_cues.py` and `tools/check_beats.py` validate them.
4. Review stills with `tools/stills.mjs`, then the owner renders on the pod.
