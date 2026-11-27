import React from "react";
import { AbsoluteFill, Audio, Freeze, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FreezeAccent, Grade, Letterbox, RgbSplit, TransitionIn } from "../kit/fx";
import { planAll } from "../kit/edit-rules";
import { FPS } from "../kit/theme";
import shotsJson from "./shots.json";
import { HISTORY, SHOTS } from "./shotlist";

type ShotRow = { scene: string; t0: number; t1: number; text: string };
const ROWS = shotsJson as ShotRow[];
const TR = 8; // transition length in frames
const PLANS = planAll(SHOTS, shotsJson as { scene: string; text: string }[], HISTORY);

// On a danger moment, footage freezes halfway with a flash, like a photo being taken.
const FreezeHalf: React.FC<{ on: boolean; children: React.ReactNode }> = ({ on, children }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const mid = Math.floor(dur * 0.55);
  if (!on || f < mid) return <AbsoluteFill>{children}</AbsoluteFill>;
  return (
    <AbsoluteFill style={{ transform: `scale(${1 + (f - mid) * 0.004})` }}>
      <Freeze frame={mid}>{children}</Freeze>
      <Sequence from={mid}>
        <FreezeAccent />
      </Sequence>
    </AbsoluteFill>
  );
};

// Shots longer than two seconds cut in tighter halfway through, like a second camera angle.
const Reframe: React.FC<{ seed: number; len: number; children: React.ReactNode }> = ({ seed, len, children }) => {
  const f = useCurrentFrame();
  const cut = len > 1.8 * FPS ? Math.floor(len / 2) : Infinity;
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
        // Each shot keeps playing for the length of the next shot's transition, underneath it.
        const extra = j + 1 < mine.length ? TR : 0;
        const plan = PLANS[r.i];
        return (
          <Sequence key={r.i} from={from} durationInFrames={Math.max(1, to - from + extra)} name={`Shot ${r.i} ${plan.transition}`}>
            <TransitionIn kind={plan.transition} len={TR}>
              <Grade kind={plan.grade}>
                <RgbSplit amount={plan.rgb}>
                  <FreezeHalf on={plan.freeze}>
                    <Reframe seed={r.i} len={to - from}>{SHOTS[r.i] ?? <AbsoluteFill style={{ background: "#300" }} />}</Reframe>
                  </FreezeHalf>
                </RgbSplit>
              </Grade>
              <Letterbox on={plan.letterbox} />
            </TransitionIn>
            {plan.sfx ? <Audio src={staticFile(`sfx/${plan.sfx}.mp3`)} volume={plan.sfxVol} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const SHOT_COUNT = ROWS.length;
