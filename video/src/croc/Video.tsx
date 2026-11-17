import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { LEAD } from "../kit/cues";
import { Head, Lines } from "../kit/devices";
import { HUD } from "../kit/hud";
import { C, FPS } from "../kit/theme";
import { ramp } from "../kit/ui";
import { cues, type SP } from "./common";
import * as A from "./scenesA";
import * as Bs from "./scenesB";
import * as Cs from "./scenesC";

const ALL: Record<string, React.FC<SP>> = { ...(A as unknown as Record<string, React.FC<SP>>), ...(Bs as unknown as Record<string, React.FC<SP>>), ...(Cs as unknown as Record<string, React.FC<SP>>) };
const sceneFor = (key: string) => ALL[`S${key}`];

const END_CARD = 10 * FPS;
const starts: number[] = [];
let cursor = 0;
for (const key of cues.keys) {
  starts.push(cursor);
  cursor += cues.frames(key);
}
export const CROC_FRAMES = cursor + END_CARD;

// Four music clips laid end to end with short crossfades, ducked well under the voice.
const MUSIC = ["croc-tense-1", "croc-tense-2", "croc-calm-1", "croc-calm-2"];
const MUSIC_LEN = [222.8, 214.8, 212.0, 204.4].map((s) => Math.floor(s * FPS));
const XF = 3 * FPS;

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#020b0e", opacity: Math.min(ramp(f, 0, 20), ramp(f, END_CARD - 20, END_CARD, 1, 0)) }}>
      <Sequence durationInFrames={END_CARD}>
        <Lines items={["DIVE LOG CLOSED"]} y={300} size={36} />
        <Head text="ABYSS THEORY" y={370} size={170} />
        <Head text={"SUBSCRIBE FOR THE NEXT ANIMAL\nYOU DO NOT WANT TO SURPRISE"} y={610} size={56} color={C.accent} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const CrocVideo: React.FC = () => {
  let m = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {MUSIC.map((name, i) => {
        const from = m;
        const len = MUSIC_LEN[i];
        m += len - XF;
        return (
          <Sequence key={name} from={from} durationInFrames={len}>
            <Audio
              src={staticFile(`audio/music/${name}.mp3`)}
              volume={(fr) => 0.2 * Math.min(interpolate(fr, [0, XF], [0, 1], { extrapolateRight: "clamp" }), interpolate(fr, [len - XF, len], [1, 0], { extrapolateLeft: "clamp" }))}
            />
          </Sequence>
        );
      })}
      {cues.keys.map((key, i) => {
        const Scene = sceneFor(key);
        const dur = cues.frames(key);
        return (
          <Sequence key={key} from={starts[i]} durationInFrames={dur} name={`Scene ${key}`}>
            {Scene ? <Scene dur={dur} start={starts[i] / FPS} /> : <AbsoluteFill style={{ background: "#111", color: HUD, fontSize: 80, alignItems: "center", justifyContent: "center" }}>scene {key}</AbsoluteFill>}
            <Sequence from={LEAD}>
              <Audio src={staticFile(`audio/croc/${key}.mp3`)} />
            </Sequence>
          </Sequence>
        );
      })}
      <Sequence from={cursor} durationInFrames={END_CARD} name="End card">
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};
