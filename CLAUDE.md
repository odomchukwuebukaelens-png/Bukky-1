# Abyss Theory video production

Channel: Abyss Theory (ocean animals, faceless, animated explainers). Videos are built with Remotion in `video/` and rendered on a RunPod pod with `render.sh`.

## Rules from the channel owner (16 Nov 2026)

- **No visual beat longer than 5 seconds.** Every 5 seconds or less, something on screen must change in step with the narration: a new shot, a new element, a camera move, a text change. Write scripts in beats of roughly 12–14 words and give each its own visual. `python3 tools/check_beats.py` (run from `video/`) must pass before a render is handed over.
- **Copy the formula, not the structure.** Study what makes a successful video work (hook type, pacing, payoff) and bend it to an adjacent angle. Never reproduce another channel's titles, thumbnail look, on-screen graphics or scene order one to one.
- Voiceover uses the owner's ai33.pro cloned voice "Deep sea" (`clone_2719063`) at speed 0.95; the owner has confirmed the rights to it.

## Channel identity (ours, keep it distinct)

- Second-person encounter framing: "What Happens When a ___ ___ You".
- Deep teal backgrounds, yellow accent, Montserrat 800, flat animated characters.

## Workflow

1. Script in `video/script/NN-name.md`, one `## N. Title` section per scene, `**Visual:**` notes, `[CHECK]` on any claim without a primary source.
2. `python3 tools/voiceover.py script/<file> <name>` generates per-scene audio and word timings.
3. Scenes cue visuals to spoken phrases with `makeCue`; `tools/check_cues.py` and `tools/check_beats.py` validate them.
4. Review stills with `tools/stills.mjs`, then the owner renders on the pod.
