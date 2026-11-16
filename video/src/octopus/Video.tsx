import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { LEAD, sceneFrames, sceneKeys } from "../kit/cues";
import { Octopus } from "../kit/shapes";
import { C, FPS } from "../kit/theme";
import { Callout, Ocean, ramp, SceneFade, Vignette } from "../kit/ui";
import { S01, S02, S03, S04, S05, type SP } from "./scenesA";
import { S06, S07, S08, S09, S10, S11, S12 } from "./scenesB";
import { S13, S14, S15, S16, S17, S18, S19 } from "./scenesC";

const SCENES: React.FC<SP>[] = [S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19];

const END_CARD = 10 * FPS;

const starts: number[] = [];
let cursor = 0;
for (const key of sceneKeys) {
  starts.push(cursor);
  cursor += sceneFrames(key);
}
export const OCTOPUS_FRAMES = cursor + END_CARD;

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: Math.min(ramp(f, 0, 20), ramp(f, END_CARD - 20, END_CARD, 1, 0)) }}>
      <Ocean seed="end" />
      <Octopus x={1480} y={640} frame={f} scale={1.05} />
      <Callout at={10} text="THANKS FOR WATCHING" x={90} y={250} width={1000} align="left" size={56} color={C.cyan} />
      <Callout at={25} text="ABYSS THEORY" x={90} y={340} width={1400} align="left" size={124} />
      <Callout at={55} text={"SUBSCRIBE FOR THE NEXT ANIMAL\nYOU DO NOT WANT TO SURPRISE"} x={90} y={540} width={1100} align="left" size={52} color={C.accent} />
      <Vignette />
    </AbsoluteFill>
  );
};

export const OctopusVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Audio src={staticFile("audio/ambience.mp3")} loop volume={0.5} />
    {sceneKeys.map((key, i) => {
      const Scene = SCENES[i];
      const dur = sceneFrames(key);
      return (
        <Sequence key={key} from={starts[i]} durationInFrames={dur} name={`Scene ${key}`}>
          <SceneFade dur={dur}>
            <Scene dur={dur} />
          </SceneFade>
          <Sequence from={LEAD}>
            <Audio src={staticFile(`audio/octopus/${key}.mp3`)} />
          </Sequence>
        </Sequence>
      );
    })}
    <Sequence from={cursor} durationInFrames={END_CARD} name="End card">
      <EndCard />
    </Sequence>
  </AbsoluteFill>
);
