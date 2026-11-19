import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FPS } from "../kit/theme";
import { Hud } from "./common";
import shotsJson from "./shots.json";
import { SHOTS } from "./shotlist";

type ShotRow = { scene: string; t0: number; t1: number; text: string };
const ROWS = shotsJson as ShotRow[];
const TICKS = ["pop4", "click3", "click2"];
// The viewer's pulse on the instruments, by scene: it climbs as the danger rises.
const PULSE: Record<string, number> = { "01": 96, "02": 102, "03": 96, "04": 106, "05": 110, "06": 118, "07": 122, "08": 126, "09": 108, "10": 116, "11": 100, "12": 104, "13": 98, "14": 94, "15": 120, "16": 108, "17": 88 };

// Shots longer than two seconds cut in tighter halfway through, like a second camera angle.
const Reframe: React.FC<{ seed: number; children: React.ReactNode }> = ({ seed, children }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const cut = dur > 2 * FPS ? Math.floor(dur / 2) : Infinity;
  const on = f >= cut ? Math.min(1, (f - cut + 1) / 2) : 0;
  const dx = seed % 2 ? 50 : -50;
  const dy = seed % 3 ? -25 : 25;
  return <AbsoluteFill style={{ transform: `scale(${1 + 0.14 * on}) translate(${dx * on}px, ${dy * on}px)` }}>{children}</AbsoluteFill>;
};

// Plays one scene as a run of two-second shots, each its own visual.
export const ShotScene: React.FC<{ sceneKey: string; dur: number; start: number; lead: number }> = ({ sceneKey, dur, start, lead }) => {
  const mine = ROWS.map((r, i) => ({ ...r, i })).filter((r) => r.scene === sceneKey);
  const starts = mine.map((r, j) => (j === 0 ? 0 : lead + Math.round(r.t0 * FPS)));
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {mine.map((r, j) => {
        const from = starts[j];
        const to = j + 1 < mine.length ? starts[j + 1] : dur;
        return (
          <Sequence key={r.i} from={from} durationInFrames={Math.max(1, to - from)} name={`Shot ${r.i}`}>
            <Reframe seed={r.i}>{SHOTS[r.i] ?? <AbsoluteFill style={{ background: "#300" }} />}</Reframe>
            {j > 0 ? <Audio src={staticFile(`sfx/${TICKS[r.i % TICKS.length]}.mp3`)} volume={0.12} /> : null}
          </Sequence>
        );
      })}
      <Hud start={start} dur={dur} pulse={PULSE[sceneKey] ?? 100} />
    </AbsoluteFill>
  );
};

export const SHOT_COUNT = ROWS.length;
