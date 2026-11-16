import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILY } from "../font";
import { C, H, W } from "./theme";

export const FONT = `${FONT_FAMILY}, Inter, 'DejaVu Sans', sans-serif`;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const ramp = (frame: number, from: number, to: number, a = 0, b = 1) =>
  interpolate(frame, [from, to], [a, b], clamp);

// 0 before `at`, springs to 1, and fades back to 0 by `out` if given.
export const usePop = (at: number, out?: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame: frame - at, fps, config: { damping: 15, mass: 0.7 } });
  const off = out === undefined ? 1 : ramp(frame, out - 12, out, 1, 0);
  return frame < at ? 0 : inn * off;
};

export const Pop: React.FC<{
  at: number;
  out?: number;
  x?: number;
  y?: number;
  children: React.ReactNode;
  origin?: string;
}> = ({ at, out, x = 0, y = 0, children, origin = "center" }) => {
  const p = usePop(at, out);
  if (p <= 0.001) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        opacity: Math.min(1, p),
        transform: `scale(${0.7 + 0.3 * p})`,
        transformOrigin: origin,
      }}
    >
      {children}
    </div>
  );
};

export const Fade: React.FC<{ at: number; out?: number; len?: number; children: React.ReactNode }> = ({
  at,
  out,
  len = 20,
  children,
}) => {
  const frame = useCurrentFrame();
  const o = ramp(frame, at, at + len) * (out === undefined ? 1 : ramp(frame, out - len, out, 1, 0));
  if (o <= 0.001) return null;
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

export const Callout: React.FC<{
  at: number;
  out?: number;
  text: string;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  width?: number;
  align?: "left" | "center" | "right";
}> = ({ at, out, text, x = 0, y = 90, size = 84, color = C.white, width = W, align = "center" }) => (
  <Pop at={at} out={out} x={x} y={y}>
    <div
      style={{
        width,
        textAlign: align,
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: size,
        lineHeight: 1.08,
        letterSpacing: 1.5,
        color,
        textShadow: "0 6px 28px rgba(0,0,0,0.75)",
        whiteSpace: "pre-line",
      }}
    >
      {text}
    </div>
  </Pop>
);

export const Stat: React.FC<{
  at: number;
  out?: number;
  value: string;
  label: string;
  x: number;
  y: number;
  color?: string;
  size?: number;
}> = ({ at, out, value, label, x, y, color = C.accent, size = 120 }) => (
  <Pop at={at} out={out} x={x} y={y} origin="left center">
    <div style={{ fontFamily: FONT, fontWeight: 800, textShadow: "0 6px 28px rgba(0,0,0,0.75)" }}>
      <div style={{ fontSize: size, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: size * 0.3, color: C.white, letterSpacing: 3, marginTop: 10, opacity: 0.9 }}>
        {label}
      </div>
    </div>
  </Pop>
);

export const Tag: React.FC<{ at: number; out?: number; text: string; x: number; y: number; color?: string; size?: number }> = ({
  at,
  out,
  text,
  x,
  y,
  color = C.cyan,
  size = 34,
}) => (
  <Pop at={at} out={out} x={x} y={y} origin="left center">
    <div
      style={{
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: size,
        letterSpacing: 3,
        color,
        padding: "8px 18px",
        border: `3px solid ${color}`,
        borderRadius: 10,
        background: "rgba(2,10,14,0.55)",
        whiteSpace: "nowrap",
      }}
    >
      {text}
    </div>
  </Pop>
);

export const Counter: React.FC<{
  from: number;
  to: number;
  start: number;
  end: number;
  x: number;
  y: number;
  label: string;
  suffix?: string;
  color?: string;
  size?: number;
  out?: number;
}> = ({ from, to, start, end, x, y, label, suffix = "", color = C.accent, size = 120, out }) => {
  const frame = useCurrentFrame();
  const v = Math.round(ramp(frame, start, end, from, to));
  return <Stat at={start} out={out} value={`${v.toLocaleString("en-US")}${suffix}`} label={label} x={x} y={y} color={color} size={size} />;
};

export const Ocean: React.FC<{ count?: number; tint?: string; night?: number; seed?: string }> = ({
  count = 60,
  tint,
  night = 0,
  seed = "o",
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 20%, ${C.bgTop} 0%, ${C.bgMid} 55%, ${C.bgDeep} 100%)`,
      }}
    >
      {tint ? <AbsoluteFill style={{ background: tint }} /> : null}
      {Array.from({ length: count }, (_, i) => {
        const size = 3 + random(`${seed}s${i}`) * 8;
        const speed = 0.12 + random(`${seed}v${i}`) * 0.4;
        const x = random(`${seed}x${i}`) * W + Math.sin(frame / 55 + i) * 16;
        const y = (((random(`${seed}y${i}`) * H - frame * speed) % H) + H) % H;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "#cfe9f2",
              opacity: 0.07 + random(`${seed}o${i}`) * 0.2,
            }}
          />
        );
      })}
      {night > 0 ? <AbsoluteFill style={{ background: "#010409", opacity: night * 0.6 }} /> : null}
    </AbsoluteFill>
  );
};

export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.7) 100%)",
      pointerEvents: "none",
    }}
  />
);

// Slow push-in so no scene ever sits completely still.
export const Drift: React.FC<{ dur: number; from?: number; to?: number; children: React.ReactNode }> = ({
  dur,
  from = 1,
  to = 1.07,
  children,
}) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [0, dur], [from, to], clamp);
  return <AbsoluteFill style={{ transform: `scale(${s})` }}>{children}</AbsoluteFill>;
};

export const SceneFade: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const frame = useCurrentFrame();
  const o = Math.min(ramp(frame, 0, 15), ramp(frame, dur - 15, dur, 1, 0));
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};
