import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Head, Lines } from "../kit/devices";
import { Captions, ChapterChip, ImpactFx, RetentionScene, SceneSfx, Teaser, type SceneEvents } from "../kit/retention";
import { Grain } from "../kit/fx";
import { C, FPS } from "../kit/theme";
import { ramp } from "../kit/ui";
import captions from "./captions.json";
import { cues, EDIT } from "./common";
import { ShotScene } from "./ShotScene";
import { LangContext } from "../humpback/lang";

const EVENTS = captions as unknown as Record<string, SceneEvents>;
const TEASERS = EDIT.teasers as Record<string, string>;
const TEASER_LEN = Math.round(2.6 * FPS);

const END_CARD = 6 * FPS;
const starts: number[] = [];
let cursor = 0;
for (const key of cues.keys) {
  starts.push(cursor);
  cursor += cues.frames(key);
}
export const LEOPARD_FRAMES = cursor + END_CARD;

// Frames where the narrator is speaking, across the whole video, for ducking the music.
const SPEECH: [number, number][] = [];
cues.keys.forEach((key, i) => {
  for (const c of EVENTS[key].captions) SPEECH.push([starts[i] + cues.lead + Math.round(c.t0 * FPS), starts[i] + cues.lead + Math.round(c.t1 * FPS)]);
});
// Music sits low under the voice and rises gently in pauses and at section breaks.
const musicLevel = (frame: number) => {
  let d = Infinity;
  let lo = 0;
  let hi = SPEECH.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const [a, b] = SPEECH[mid];
    if (frame < a) {
      d = Math.min(d, a - frame);
      hi = mid - 1;
    } else if (frame > b) {
      d = Math.min(d, frame - b);
      lo = mid + 1;
    } else {
      d = 0;
      break;
    }
  }
  return 0.13 + 0.12 * Math.min(1, Math.max(0, (d - 4) / 12));
};

// The crocodile music, reused at the owner's request (25 Nov 2026): four clips laid end to end with short crossfades, ducked well under the voice.
const MUSIC = ["croc-tense-1", "croc-tense-2", "croc-calm-1", "croc-calm-2"];
const MUSIC_LEN = [222.8, 214.8, 212.0, 204.4].map((s) => Math.floor(s * FPS));
const XF = 3 * FPS;

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#020b0e", opacity: Math.min(ramp(f, 0, 10), ramp(f, END_CARD - 15, END_CARD, 1, 0)) }}>
      <Sequence durationInFrames={END_CARD}>
        <Lines items={["DIVE LOG CLOSED"]} y={300} size={36} />
        <Head text="ABYSS THEORY" y={370} size={170} />
        <Head text={"SUBSCRIBE FOR THE NEXT ANIMAL\nYOU DO NOT WANT TO SURPRISE"} y={610} size={56} color={C.accent} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const LeopardVideo: React.FC<{ only?: string[] }> = ({ only }) => {
  let m = 0;
  const lead = cues.lead;
  return (
    <LangContext.Provider value="en">
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {MUSIC.map((name, i) => {
        const from = m;
        const len = MUSIC_LEN[i];
        m += len - XF;
        return (
          <Sequence key={name} from={from} durationInFrames={len}>
            <Audio
              src={staticFile(`audio/music/${name}.mp3`)}
              volume={(fr) => musicLevel(from + fr) * Math.min(interpolate(fr, [0, XF], [0, 1], { extrapolateRight: "clamp" }), interpolate(fr, [len - XF, len], [1, 0], { extrapolateLeft: "clamp" }))}
            />
          </Sequence>
        );
      })}
      {cues.keys.map((key, i) => {
        if (only && !only.includes(key)) return null;
        const dur = cues.frames(key);
        const ev = EVENTS[key];
        const teaser = TEASERS[key];
        const teaserAt = teaser ? dur - TEASER_LEN : undefined;
        return (
          <Sequence key={key} from={starts[i]} durationInFrames={dur} name={`Scene ${key}`}>
            <RetentionScene ev={ev} lead={lead}>
              <ShotScene sceneKey={key} dur={dur} start={starts[i] / FPS} lead={lead} />
            </RetentionScene>
            <ImpactFx ev={ev} lead={lead} />
            <Captions ev={ev} lead={lead} />
            {i > 0 ? <ChapterChip n={i + 1} title={cues.title(key)} /> : null}
            {teaser && teaserAt !== undefined ? (
              <Sequence from={teaserAt} durationInFrames={TEASER_LEN}>
                <Teaser text={teaser} len={TEASER_LEN} />
              </Sequence>
            ) : null}
            <SceneSfx ev={ev} lead={lead} index={i} beatFrames={[]} teaserAt={teaserAt} />
            <Sequence from={lead}>
              <Audio src={staticFile(`${EDIT.voiceDir}/${key}.mp3`)} />
            </Sequence>
          </Sequence>
        );
      })}
      <Grain />
      {only ? null : <Sequence from={cursor} durationInFrames={END_CARD} name="End card">
        <EndCard />
      </Sequence>}
    </AbsoluteFill>
    </LangContext.Provider>
  );
};

// The VFX test: the cold open only.
export const LEOPARD_TEST_FRAMES = starts[1];
