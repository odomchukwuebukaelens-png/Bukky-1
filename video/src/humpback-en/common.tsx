import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { createCues } from "../kit/cues";
import { AirGauge, HUD, MONO, Readout } from "../kit/hud";
import { usePunch } from "../kit/retention";
import { C, FPS } from "../kit/theme";
import edit from "./edit.json";
import timing from "./timing-fast.json";

export const EDIT = edit;
export const cues = createCues(timing, { lead: Math.round(edit.lead * FPS), tail: Math.round(edit.tail * FPS) });

// The same corner instruments as every Abyss Theory video, labelled in English.
export const Hud: React.FC<{ start: number; depth: number; pulse: number; dur: number }> = ({ start, depth, pulse }) => {
  const f = useCurrentFrame();
  const sec = 1380 + start + f / FPS;
  const mm = Math.floor(sec / 60);
  const ss = Math.floor(sec % 60);
  const bpm = Math.round(pulse + Math.sin(f * 0.11) * 1.5);
  const beat = Math.max(0, Math.sin((f / FPS) * (pulse / 60) * Math.PI * 2));
  const p = usePunch();
  return (
    <AbsoluteFill style={{ transform: `scale(${1 / p.s}) translate(${-p.tx}px, ${-p.ty}px)` }}>
      <Readout label="DEPTH" value={`${Math.max(0, depth + Math.sin(f * 0.05) * 0.05).toFixed(1)} M`} x={120} y={84} on={1} />
      <AirGauge bar={196 - (start + f / FPS) * 0.11} on={1} label="AIR" unit="BAR" />
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
