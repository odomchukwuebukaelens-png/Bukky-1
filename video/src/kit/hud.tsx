import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MONO_FAMILY } from "../font";
import { C } from "./theme";
import { FONT, ramp, usePop } from "./ui";

export const MONO = `${MONO_FAMILY}, 'DejaVu Sans Mono', monospace`;
export const HUD = "#7fe9ff";

const mono = (size: number, color = HUD): React.CSSProperties => ({
  fontFamily: MONO,
  fontWeight: 700,
  fontSize: size,
  color,
  letterSpacing: 2,
  whiteSpace: "nowrap",
  textShadow: "0 0 12px rgba(0,0,0,0.9)",
});

// The diver's mask: everything is seen through this window.
export const MaskFrame: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div
      style={{
        position: "absolute",
        left: 34,
        top: 30,
        right: 34,
        bottom: 30,
        borderRadius: 150,
        boxShadow: "0 0 0 400px #010506, inset 0 0 90px 30px rgba(1,5,6,0.85)",
        border: "5px solid #0c1d22",
      }}
    />
    <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
      <path d="M 790 1080 Q 960 880 1130 1080 Z" fill="#010506" />
    </svg>
  </AbsoluteFill>
);

// A value on the dive computer. `flash` (0..1) makes it pulse when the narration mentions it.
export const Readout: React.FC<{
  label: string;
  value: string;
  x: number;
  y: number;
  on: number;
  flash?: number;
  align?: "left" | "right";
  warn?: boolean;
}> = ({ label, value, x, y, on, flash = 0, align = "left", warn = false }) => {
  if (on <= 0) return null;
  const col = warn ? C.accent : HUD;
  return (
    <div
      style={{
        position: "absolute",
        [align]: x,
        top: y,
        opacity: on,
        textAlign: align,
        transform: `scale(${1 + flash * 0.35})`,
        transformOrigin: `${align} top`,
      }}
    >
      <div style={mono(20, "rgba(127,233,255,0.65)")}>{label}</div>
      <div style={{ ...mono(46, flash > 0.3 ? C.accent : col), marginTop: 2 }}>{value}</div>
    </div>
  );
};

export const AirGauge: React.FC<{ bar: number; on: number }> = ({ bar, on }) => (
  <div style={{ position: "absolute", right: 120, top: 84, opacity: on, textAlign: "right" }}>
    <div style={mono(20, "rgba(127,233,255,0.65)")}>AIR</div>
    <div style={{ ...mono(46), marginTop: 2 }}>{Math.round(bar)} BAR</div>
    <div style={{ width: 260, height: 10, background: "rgba(127,233,255,0.18)", marginTop: 8, marginLeft: "auto" }}>
      <div style={{ width: `${(bar / 200) * 100}%`, height: "100%", background: bar < 70 ? C.red : HUD }} />
    </div>
  </div>
);

// Corner brackets that lock on to something, with a typed-out label.
export const ScanBox: React.FC<{
  at: number;
  out?: number;
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  sub?: string;
  color?: string;
  labelBelow?: boolean;
}> = ({ at, out, x, y, w, h, label, sub, color = HUD, labelBelow = false }) => {
  const frame = useCurrentFrame();
  const p = usePop(at, out);
  if (p <= 0.001) return null;
  const grow = 1.5 - 0.5 * Math.min(1, p);
  const L = 34;
  const typed = label.slice(0, Math.max(0, Math.floor((frame - at) * 1.2)));
  const corners = [
    [0, 0, 1, 1],
    [w, 0, -1, 1],
    [0, h, 1, -1],
    [w, h, -1, -1],
  ];
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: Math.min(1, p) }}>
      <svg width={w} height={h} style={{ overflow: "visible", transform: `scale(${grow})`, transformOrigin: "center" }}>
        {corners.map(([cx, cy, sx, sy], i) => (
          <path key={i} d={`M ${cx + sx * L} ${cy} L ${cx} ${cy} L ${cx} ${cy + sy * L}`} stroke={color} strokeWidth={5} fill="none" />
        ))}
      </svg>
      <div style={{ position: "absolute", left: 0, top: labelBelow ? h + 14 : -96 }}>
        <div style={mono(38, color)}>{typed}</div>
        {sub ? <div style={{ ...mono(26, "rgba(255,255,255,0.85)"), marginTop: 4, opacity: ramp(frame, at + 18, at + 28) }}>{sub}</div> : null}
      </div>
    </div>
  );
};

export const Line: React.FC<{ at: number; out?: number; x: number; y: number; text: string; size?: number; color?: string; align?: "left" | "right" | "center"; width?: number }> = ({
  at,
  out,
  x,
  y,
  text,
  size = 30,
  color = HUD,
  align = "left",
  width,
}) => {
  const frame = useCurrentFrame();
  const p = usePop(at, out);
  if (p <= 0.001) return null;
  const typed = text.slice(0, Math.max(0, Math.floor((frame - at) * 1.5)));
  return (
    <div style={{ position: "absolute", left: x, top: y, width, textAlign: align, opacity: Math.min(1, p), ...mono(size, color) }}>{typed}</div>
  );
};

// LOGGED = measured and sourced, REPORTED = credible but single-source, MYTH = false.
export const Evidence: React.FC<{ at: number; out?: number; x: number; y: number; level: "LOGGED" | "REPORTED" | "MYTH"; source: string }> = ({
  at,
  out,
  x,
  y,
  level,
  source,
}) => {
  const p = usePop(at, out);
  if (p <= 0.001) return null;
  const col = level === "LOGGED" ? HUD : level === "REPORTED" ? C.accent : C.red;
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: Math.min(1, p), display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{ ...mono(28, "#02090c"), background: col, padding: "4px 14px", textShadow: "none" }}>{level}</div>
      <div style={mono(26, "rgba(255,255,255,0.85)")}>{source}</div>
    </div>
  );
};

export const Big: React.FC<{ at: number; out?: number; x: number; y: number; text: string; size?: number; color?: string; width?: number; align?: "left" | "center" }> = ({
  at,
  out,
  x,
  y,
  text,
  size = 120,
  color = C.white,
  width = 1920,
  align = "left",
}) => {
  const p = usePop(at, out);
  if (p <= 0.001) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width,
        textAlign: align,
        opacity: Math.min(1, p),
        transform: `translateY(${(1 - Math.min(1, p)) * 30}px)`,
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: size,
        lineHeight: 1.02,
        color,
        whiteSpace: "pre-line",
        textShadow: "0 8px 30px rgba(0,0,0,0.85)",
      }}
    >
      {text}
    </div>
  );
};

export const ScanLines: React.FC<{ on: number }> = ({ on }) => {
  const frame = useCurrentFrame();
  if (on <= 0) return null;
  return (
    <AbsoluteFill style={{ opacity: on, pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: "repeating-linear-gradient(0deg, rgba(127,233,255,0.07) 0px, rgba(127,233,255,0.07) 2px, transparent 2px, transparent 7px)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: ((frame * 9) % 1300) - 110, height: 110, background: "linear-gradient(transparent, rgba(127,233,255,0.22), transparent)" }} />
    </AbsoluteFill>
  );
};
