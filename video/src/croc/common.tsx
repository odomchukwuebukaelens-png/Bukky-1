import React from "react";
import { AbsoluteFill, Audio, random, Sequence, staticFile, useCurrentFrame } from "remotion";
import { createCues } from "../kit/cues";
import { B } from "../kit/devices";
import { AirGauge, HUD, MONO, Readout } from "../kit/hud";
import { C, FPS } from "../kit/theme";
import { ramp } from "../kit/ui";
import edit from "./edit.json";
import timing from "./timing-fast.json";
import { usePunch } from "../kit/retention";

export const EDIT = edit;
export const cues = createCues(timing, { lead: Math.round(edit.lead * FPS), tail: Math.round(edit.tail * FPS) });
export type SP = { dur: number; start: number };

type BeatDef = [number, React.ReactNode] | [number, React.ReactNode, number];
// Each beat lasts until the next one starts, unless it gives its own end frame.
// Every beat also gets a quiet UI tick so each visual change is heard as well as seen.
const TICKS = ["pop4", "click3", "click2"];
export const beats = (list: BeatDef[], end: number) =>
  list.map((b, i) => (
    <React.Fragment key={i}>
      <B at={b[0]} to={b[2] ?? list[i + 1]?.[0] ?? end}>
        {b[1]}
      </B>
      <Sequence from={b[0]} durationInFrames={20}>
        <Audio src={staticFile(`sfx/${TICKS[i % TICKS.length]}.mp3`)} volume={0.14} />
      </Sequence>
    </React.Fragment>
  ));

export const CREDIT = {
  jump: "MATT FROM MELBOURNE · CC BY 2.0",
  sign: "DRONEPICR · CC BY 2.0",
};

// The instruments that stay on for the whole video. Pulse is the viewer's own heart rate.
export const Hud: React.FC<{ start: number; depth?: number; pulse?: number; dur: number }> = ({ start, depth = 0.9, pulse = 72, dur }) => {
  const f = useCurrentFrame();
  const sec = 1380 + start + f / FPS;
  const mm = Math.floor(sec / 60);
  const ss = Math.floor(sec % 60);
  const bpm = Math.round(pulse + Math.sin(f * 0.11) * 1.5);
  const beat = Math.max(0, Math.sin((f / FPS) * (pulse / 60) * Math.PI * 2));
  const p = usePunch();
  return (
    <AbsoluteFill style={{ transform: `scale(${1 / p.s}) translate(${-p.tx}px, ${-p.ty}px)` }}>
      <Readout label="DEPTH" value={`${Math.max(0, depth + Math.sin(f * 0.05) * 0.02).toFixed(1)} M`} x={120} y={84} on={1} />
      <AirGauge bar={196 - (start + f / FPS) * 0.11} on={1} />
      <Readout label="DIVE TIME" value={`${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`} x={120} y={900} on={1} />
      <div style={{ position: "absolute", right: 120, top: 900, textAlign: "right" }}>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 20, letterSpacing: 2, color: "rgba(127,233,255,0.65)" }}>YOUR PULSE</div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 46, letterSpacing: 2, color: pulse > 110 ? C.red : pulse > 90 ? C.accent : HUD, marginTop: 2, transform: `scale(${1 + beat * 0.06})`, transformOrigin: "right center" }}>
          {bpm} BPM
        </div>
      </div>
    </AbsoluteFill>
  );
};

// What you see standing in the river at dusk. `eye` places the two bumps; `show` 1 = up, 0 = sunk.
export const River: React.FC<{ ex?: number; ey?: number; es?: number; show?: number; dusk?: number; zoom?: number; zx?: number; zy?: number; glow?: number; night?: number }> = ({
  ex = 1180,
  ey = 392,
  es = 0.5,
  show = 1,
  dusk = 0,
  zoom = 1,
  zx = 960,
  zy = 540,
  glow = 0,
  night = 0,
}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#0d0f0a" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - zx * zoom}px, ${540 - zy * zoom}px) scale(${zoom})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -400, top: -400, width: 2720, height: 762, background: "linear-gradient(#2a2a4a 0%, #6c4a6e 45%, #d98a52 85%, #f0b06a 100%)" }} />
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <path
            d={`M -400 362 ${Array.from({ length: 60 }, (_, i) => `L ${-400 + i * 46} ${330 - random(`bk${i}`) * 46 - (i % 7 === 0 ? 30 : 0)}`).join(" ")} L 2320 362 Z`}
            fill="#14180f"
          />
        </svg>
        <div style={{ position: "absolute", left: -400, top: 360, width: 2720, height: 1200, background: "linear-gradient(#8a6a3a 0%, #5a4a28 14%, #3b3a20 40%, #1c1d11 100%)" }} />
        <div style={{ position: "absolute", left: 760, top: 360, width: 400, height: 500, background: "linear-gradient(rgba(240,176,106,0.5), transparent)", filter: "blur(30px)" }} />
        {Array.from({ length: 46 }, (_, i) => {
          const y = 372 + Math.pow(random(`wy${i}`), 1.7) * 700;
          const w = 60 + ((y - 360) / 700) * 320;
          const x = ((random(`wx${i}`) * 2600 + f * (0.25 + ((y - 360) / 700) * 1.1)) % 2700) - 400;
          return <div key={i} style={{ position: "absolute", left: x, top: y, width: w, height: 3 + ((y - 360) / 700) * 5, borderRadius: 4, background: "#c9a465", opacity: 0.1 + random(`wo${i}`) * 0.14 }} />;
        })}
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <g transform={`translate(${ex} ${ey + (1 - show) * 34 * es}) scale(${es})`} opacity={Math.min(1, show * 1.6)}>
            <ellipse cx={-52} cy={0} rx={34} ry={22} fill="#14160d" />
            <ellipse cx={52} cy={0} rx={34} ry={22} fill="#14160d" />
            <ellipse cx={0} cy={54} rx={30} ry={14} fill="#14160d" />
            <rect x={-200} y={2} width={400} height={80} fill="#4a4024" opacity={0} />
            {glow > 0 ? (
              <g opacity={glow}>
                <ellipse cx={-52} cy={-6} rx={15} ry={9} fill="#e9d98a" />
                <ellipse cx={52} cy={-6} rx={15} ry={9} fill="#e9d98a" />
                <rect x={-55} y={-14} width={6} height={16} rx={3} fill="#111" />
                <rect x={49} y={-14} width={6} height={16} rx={3} fill="#111" />
              </g>
            ) : null}
            <rect x={-120} y={12 - (1 - show) * 34} width={240} height={90} fill="#554624" opacity={0.0} />
          </g>
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "#07070c", opacity: dusk * 0.5 + night * 0.35 }} />
    </AbsoluteFill>
  );
};
