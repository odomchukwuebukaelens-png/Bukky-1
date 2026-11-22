# Abyss Theory retention playbook

How every video is written and edited to keep people watching. Written 19 Nov 2026 after the octopus video averaged under a minute of a 15-minute runtime.

## What the numbers say

- **Typical retention is low.** Published benchmarks are vendor and creator figures, not YouTube's, and they disagree, but they cluster around 25–50% average percentage viewed for long-form. One 2025 study of 10,000+ videos put the average near 24%, with only about 17% of videos holding past 50%. 60–70% on a 10-minute video is exceptional and not guaranteed by editing alone.
- **The first 30 seconds decide most of it.** YouTube's own "Intro" metric is the share still watching at 30 seconds; it counts 50% or more as an above-typical intro. Most of a video's drop happens there. MrBeast's production notes call the first minute "the most important minute of each video".
- **Average view duration is what matters, not length.** A shorter, tighter video with a higher percentage usually beats a padded long one.

## What our own analytics show

**Crocodile video (22 Nov 2026).** Average view duration was 3:36, 31.2%, on about 60 views, so the curve is noisy. That is far better than the octopus video, but well short of the owner's 60–70% target.
- **The intro is the big leak.** Retention fell from 100% to about 62% in the first 20 seconds, during the opening.
- **Real stories hold people.** The only rise in the curve is around 4:45–5:20, the Val Plumwood death-roll story; people rewatched or skipped to it. There was a smaller bump at the Ramree Island myth.
- **Statistics and history lose them.** The steepest mid-video drop is around 7:35–8:15, the attack-statistics and hunting-history section.
- **The end holds.** About 17% stayed through the last three minutes.

What to do with this:
- Open on a real story or the most dramatic moment.
- Put a true human story every 2–3 minutes.
- Turn statistics into a story or cut them.
- Aim for about 8 minutes.

## The rules

### 1. Packaging and hook (0:00–0:30)
- The first 5 seconds show the title's promise: the animal, the danger, the viewer in the scene. No logos, no slow scene-setting, no title card before the action.
- The question the title asks is spoken by 15 seconds.
- Then three on-screen promises, each a question the video answers later (open loops). The last one is answered near the end, so it carries people through.
- Flash-forwards: 1–2 second glimpses of the most dramatic later moments during the hook.

### 2. Pacing
- A visual change at least every 2 seconds, checked by `tools/check_beats.py --video=<name> 2`.
- Changes come from, in order of value: a new animated action or shot, live footage, a new element entering, a camera move, a caption change.
- Narration at a brisk documentary pace (about 175–180 words a minute). No silence longer than half a second between scenes.
- Every 2–3 minutes a "re-hook": a red "COMING UP" banner teasing something specific and dramatic still ahead.

### 3. Text on screen
- Word-by-word captions on every line, with one keyword per phrase in yellow. Many people watch muted or half-listening; captions also give the eye something new every second.
- Chapter cards at every section start.
- Big numbers count up rather than appearing still.

### 3b. Transitions and effects (researched 22 Nov 2026)
Professional YouTube editors keep energy with motivated transitions (whip pans, zoom transitions, match cuts), speed ramps and freeze-frames on key moments, text pops on single words, glitch hits for shocking lines, and film burns, light leaks and grain on archival material. Documentary audiences still expect clarity, so every effect is tied to a moment in the narration rather than applied at random. Our rules:
- **Every shot enters with a transition matched to its type:** whips and ripples into footage; claws, zooms and slashes into drawn animation; slashes, pushes and blinds into graphics; irises into maps; flashes into title cards; a glitch into myth stamps; film burns into history.
- **Danger lines get more:** a flash or glitch cut, letterbox bars, an RGB split, a freeze-frame with a camera-flash on footage, and a screen shake with an impact sound.
- **History** (1945, 1950s, 1985) gets an old-film grade: sepia, flicker, gate weave, scratches and dust.
- **Light grain over the whole video,** and a sound for every transition (whoosh, glitch, splash, impact).

Sources: [ShortGenius on transitions](https://shortgenius.com/blog/transitions-for-videos), [Inside Editors on transitions](https://insideeditors.com/video-editing-transitions/), [AIR on retention editing](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8), [Motion Array on Johnny Harris-style editing](https://motionarray.com/learn/premiere-pro/edit-documentary-in-premiere-pro/), [Gling on video effects](https://www.gling.ai/blog/master-video-editing-effects), [Remotion transitions](https://www.remotion.dev/docs/transitions/presentations).

### 3c. Restraint (owner, 22 Nov 2026)
Constant zooms, captions, sound hits and overlays create activity without meaning, and viewers tire before the information is complete. So:
- Every effect has a reason.
- Vary the transitions, because one repeated type becomes a pattern viewers tune out.
- Light leaks and glitches only at section changes.
- Every transition gets a synced sound effect.
- Get the audio right before adding more effects.

### 4. Sound
- Continuous music bed under the voice, about 15 dB below it.
- A whoosh on every scene cut, a soft tick on every new visual element, an impact with a screen shake and red flash on danger words (bite, strike, attack, kill), splashes on water moments, a riser into every "coming up".

### 5. Structure
- Escalate: start with the encounter, end with the most dramatic and most useful material.
- Pay off every promise made in the hook, and pay off the last one late.
- Keep the end card short (6 seconds). Viewers leaving on a long end screen still count against the percentage.

### 6. After every upload
- Open YouTube Studio → the video → Analytics → Engagement → Audience retention, and the "Key moments" panel.
- Screenshot the graph and send it. Every dip shows a moment to fix in the next video.

## Sources
- YouTube Help, "Measure key moments for audience retention": https://support.google.com/youtube/answer/9314415
- vidIQ, "YouTube Audience Retention: What's a Good Rate": https://vidiq.com/blog/post/increase-audience-retention-youtube/
- Flintzy, audience retention benchmarks: https://www.flintzy.com/blog/audience-retention-in-youtube-studio-the-one-metric-that-actually-predicts-channel-growth/
- GIGAZINE on the MrBeast production document: https://gigazine.net/gsc_news/en/20240917-mrbeast-youtube-production/
- Creator Handbook on the same document: https://www.creatorhandbook.net/leaked-document-allegedly-reveals-mrbeasts-secrets-to-youtube-success-the-key-takeaways/
- Pixflow, retention editing: https://pixflow.net/blog/youtube-video-retention-editing/
- Creatune, retention editing for YouTube: https://www.creatuneagency.com/en/blog/retention-editing-for-youtube/
- Mark Studios, video editing and YouTube growth guide: https://www.markstudios.com/guide
