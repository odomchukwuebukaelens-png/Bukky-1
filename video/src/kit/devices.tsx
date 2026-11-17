import React from "react";
import { AbsoluteFill, Img, interpolate, random, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { MONO_FAMILY } from "../font";
import { HUD, MONO } from "./hud";
import { C } from "./theme";
import { FONT, ramp } from "./ui";

// One visual beat: children see local frames starting at 0 and fade themselves in and out.
export const B: React.FC<{ at: number; to: number; children: React.ReactNode }> = ({ at, to, children }) => (
  <Sequence from={at} durationInFrames={Math.max(1, to - at)}>
    {children}
  </Sequence>
);

export const useBeat = (fadeIn = 7, fadeOut = 6) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  return { f, dur, vis: Math.min(ramp(f, 0, fadeIn), ramp(f, dur - fadeOut, dur, 1, 0)) };
};

const shadow = "0 6px 26px rgba(0,0,0,0.9), 0 0 4px rgba(0,0,0,0.9)";
const typed = (text: string, f: number, speed = 1.6) => text.slice(0, Math.max(0, Math.floor(f * speed)));

// Real photograph with a slow move, cooled and darkened so the instruments stay readable.
export const Photo: React.FC<{
  src: string;
  credit: string;
  from?: number;
  to?: number;
  ox?: string;
  oy?: string;
  dim?: number;
  invert?: boolean;
  fit?: "cover" | "contain";
  cont?: boolean; // continues the previous shot of the same photo: no fade in
  hold?: boolean; // the next beat continues this shot: no fade out
}> = ({ src, credit, from = 1.04, to = 1.16, ox = "50%", oy = "50%", dim = 0.3, invert = false, fit = "cover", cont = false, hold = false }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const vis = Math.min(cont ? 1 : ramp(f, 0, 8), hold ? 1 : ramp(f, dur - 6, dur, 1, 0));
  const z = interpolate(f, [0, dur], [from, to]);
  return (
    <AbsoluteFill style={{ opacity: vis, background: "#020b0e" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: fit,
          objectPosition: `${ox} ${oy}`,
          transform: `scale(${z})`,
          transformOrigin: `${ox} ${oy}`,
          filter: invert ? "invert(1) hue-rotate(180deg) brightness(0.9) contrast(1.2)" : "saturate(0.8) contrast(1.08) brightness(0.86)",
        }}
      />
      <AbsoluteFill style={{ background: `linear-gradient(rgba(2,14,18,${dim}), rgba(2,14,18,${dim + 0.25}))` }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 62, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 2, color: "rgba(255,255,255,0.6)" }}>
        PHOTO · {credit}
      </div>
    </AbsoluteFill>
  );
};

export const ScanBg: React.FC<{ tint?: string }> = ({ tint = "#020b0e" }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: tint }}>
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(127,233,255,0.07) 2px, transparent 2px), linear-gradient(90deg, rgba(127,233,255,0.07) 2px, transparent 2px)",
          backgroundSize: "80px 80px",
          transform: `translateY(${(f * 0.35) % 80}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

export const Head: React.FC<{
  text: string;
  sub?: string;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  align?: "left" | "center" | "right";
  width?: number;
}> = ({ text, sub, x = 130, y = 260, size = 110, color = C.white, align = "left", width = 1660 }) => {
  const { f, vis } = useBeat();
  return (
    <div style={{ position: "absolute", left: x, top: y, width, textAlign: align, opacity: vis, transform: `translateY(${(1 - ramp(f, 0, 8)) * 26}px)` }}>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1.03, color, whiteSpace: "pre-line", textShadow: shadow }}>{text}</div>
      {sub ? (
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: Math.max(28, size * 0.3), letterSpacing: 2, color: HUD, marginTop: 16, textShadow: shadow }}>{typed(sub, f - 6)}</div>
      ) : null}
    </div>
  );
};

export const Num: React.FC<{
  value: number;
  from?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  label?: string;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  count?: number;
  align?: "left" | "center";
  width?: number;
}> = ({ value, from = 0, decimals = 0, prefix = "", suffix = "", label, x = 130, y = 250, size = 210, color = HUD, count = 26, align = "left", width = 1660 }) => {
  const { f, vis } = useBeat();
  const v = interpolate(f, [0, count], [from, value], { extrapolateRight: "clamp" });
  const txt = v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return (
    <div style={{ position: "absolute", left: x, top: y, width, textAlign: align, opacity: vis }}>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1, color, textShadow: shadow, whiteSpace: "nowrap" }}>
        {prefix}
        {txt}
        <span style={{ fontSize: size * 0.45 }}>{suffix}</span>
      </div>
      {label ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 2, color: C.white, marginTop: 14, textShadow: shadow }}>{typed(label, f - 4)}</div> : null}
    </div>
  );
};

export const Lines: React.FC<{ items: string[]; x?: number; y?: number; size?: number; color?: string; gap?: number; highlight?: number }> = ({
  items,
  x = 130,
  y = 280,
  size = 44,
  color = HUD,
  gap = 14,
  highlight = -1,
}) => {
  const { f, vis } = useBeat();
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: vis }}>
      {items.map((t, i) => (
        <div key={i} style={{ fontFamily: MONO, fontWeight: 700, fontSize: size, letterSpacing: 2, color: i === highlight ? C.accent : color, marginBottom: size * 0.42, textShadow: shadow, whiteSpace: "nowrap" }}>
          {typed(t, f - i * gap)}
        </div>
      ))}
    </div>
  );
};

export const Bars: React.FC<{ rows: { label: string; value: number; text: string; color?: string }[]; max: number; x?: number; y?: number; w?: number; title?: string }> = ({
  rows,
  max,
  x = 130,
  y = 300,
  w = 1100,
  title,
}) => {
  const { f, vis } = useBeat();
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: vis }}>
      {title ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, letterSpacing: 2, color: HUD, marginBottom: 26, textShadow: shadow }}>{title}</div> : null}
      {rows.map((r, i) => {
        const g = ramp(f, 4 + i * 10, 26 + i * 10);
        return (
          <div key={i} style={{ marginBottom: 30 }}>
            <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, letterSpacing: 2, color: C.white, marginBottom: 8, textShadow: shadow }}>{r.label}</div>
            <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
              <div style={{ width: Math.max(6, (r.value / max) * w * g), height: 44, background: r.color ?? HUD }} />
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 44, color: r.color ?? HUD, opacity: g, textShadow: shadow, whiteSpace: "nowrap" }}>{r.text}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export const Gauge: React.FC<{ value: number; max: number; label: string; text: string; x?: number; y?: number; r?: number; color?: string }> = ({
  value,
  max,
  label,
  text,
  x = 960,
  y = 640,
  r = 300,
  color = C.accent,
}) => {
  const { f, vis } = useBeat();
  const p = ramp(f, 4, 40) * Math.min(1, value / max);
  const ang = Math.PI * (1 - p);
  const arc = (a0: number, a1: number) => {
    const p0 = [x + Math.cos(a0) * r, y - Math.sin(a0) * r];
    const p1 = [x + Math.cos(a1) * r, y - Math.sin(a1) * r];
    return `M ${p0[0]} ${p0[1]} A ${r} ${r} 0 0 1 ${p1[0]} ${p1[1]}`;
  };
  return (
    <AbsoluteFill style={{ opacity: vis }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <path d={arc(Math.PI, 0)} stroke="rgba(127,233,255,0.25)" strokeWidth={34} fill="none" />
        {p > 0.002 ? <path d={arc(Math.PI, ang)} stroke={color} strokeWidth={34} fill="none" /> : null}
        <line x1={x} y1={y} x2={x + Math.cos(ang) * (r - 50)} y2={y - Math.sin(ang) * (r - 50)} stroke={C.white} strokeWidth={8} />
        <circle cx={x} cy={y} r={16} fill={C.white} />
      </svg>
      <div style={{ position: "absolute", left: x - 500, top: y + 30, width: 1000, textAlign: "center" }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 110, color, textShadow: shadow }}>{text}</div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 2, color: C.white, textShadow: shadow }}>{label}</div>
      </div>
    </AbsoluteFill>
  );
};

export const Stamp: React.FC<{ text: string; color?: string; x?: number; y?: number; size?: number; rotate?: number }> = ({ text, color = C.red, x = 960, y = 540, size = 200, rotate = -12 }) => {
  const { f, vis } = useBeat(3, 6);
  const s = interpolate(f, [0, 6], [2.4, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: x - 700, top: y - size * 0.75, width: 1400, textAlign: "center", opacity: vis, transform: `rotate(${rotate}deg) scale(${s})` }}>
      <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, color, border: `${size * 0.08}px solid ${color}`, padding: `0 ${size * 0.25}px`, borderRadius: 18, letterSpacing: 8, background: "rgba(2,11,14,0.55)" }}>{text}</span>
    </div>
  );
};

export const Chip: React.FC<{ level: "LOGGED" | "REPORTED" | "MYTH"; source: string; x?: number; y?: number }> = ({ level, source, x = 420, y = 912 }) => {
  const { vis } = useBeat();
  const col = level === "LOGGED" ? HUD : level === "REPORTED" ? C.accent : C.red;
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: vis, display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 28, letterSpacing: 2, color: "#02090c", background: col, padding: "4px 14px" }}>{level}</div>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 24, letterSpacing: 1.5, color: "rgba(255,255,255,0.9)", textShadow: shadow, whiteSpace: "nowrap" }}>{source}</div>
    </div>
  );
};

export const Box: React.FC<{ x: number; y: number; w: number; h: number; label: string; sub?: string; color?: string; below?: boolean }> = ({ x, y, w, h, label, sub, color = HUD, below = false }) => {
  const { f, vis } = useBeat();
  const grow = 1.5 - 0.5 * ramp(f, 0, 8);
  const L = 34;
  const corners = [
    [0, 0, 1, 1],
    [w, 0, -1, 1],
    [0, h, 1, -1],
    [w, h, -1, -1],
  ];
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: vis }}>
      <svg width={w} height={h} style={{ overflow: "visible", transform: `scale(${grow})` }}>
        {corners.map(([cx, cy, sx, sy], i) => (
          <path key={i} d={`M ${cx + sx * L} ${cy} L ${cx} ${cy} L ${cx} ${cy + sy * L}`} stroke={color} strokeWidth={5} fill="none" />
        ))}
      </svg>
      <div style={{ position: "absolute", left: 0, top: below ? h + 14 : -96, whiteSpace: "nowrap" }}>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 38, letterSpacing: 2, color, textShadow: shadow }}>{typed(label, f)}</div>
        {sub ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 26, letterSpacing: 2, color: "rgba(255,255,255,0.88)", textShadow: shadow, opacity: ramp(f, 12, 20) }}>{sub}</div> : null}
      </div>
    </div>
  );
};

export const Ecg: React.FC<{ bpm: number; x?: number; y?: number; w?: number; color?: string; label?: string }> = ({ bpm, x = 130, y = 520, w = 1100, color = HUD, label }) => {
  const { f, vis } = useBeat();
  const period = (60 / bpm) * 30; // frames per beat
  const pts: string[] = [];
  for (let i = 0; i <= 220; i++) {
    const px = (i / 220) * w;
    const t = (f - (220 - i) * 0.9 + 9000) % period;
    const u = t / Math.min(period, 14);
    const spike = u < 1 ? Math.sin(u * Math.PI) * (u < 0.5 ? -120 : 60) : 0;
    pts.push(`${x + px},${y + spike}`);
  }
  return (
    <AbsoluteFill style={{ opacity: vis }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <polyline points={pts.join(" ")} stroke={color} strokeWidth={6} fill="none" />
      </svg>
      {label ? <div style={{ position: "absolute", left: x, top: y + 90, fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 2, color: C.white, textShadow: shadow }}>{label}</div> : null}
    </AbsoluteFill>
  );
};

// Side-view crocodile silhouette, 1000 units long, snout at the left.
export const CrocSide: React.FC<{ x: number; y: number; scale?: number; flip?: boolean; color?: string; rotate?: number; opacity?: number; plates?: number; tail?: number }> = ({
  x,
  y,
  scale = 1,
  flip = false,
  color = "#56613f",
  rotate = 0,
  opacity = 1,
  plates = 0,
  tail = 0,
}) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${flip ? -scale : scale} ${scale})`}>
      <path d="M 390 20 L 432 20 L 452 70 L 484 74 L 484 86 L 410 86 L 394 58 Z" fill="#3e4730" />
      <path d="M 630 22 L 690 18 L 706 68 L 742 72 L 742 86 L 660 86 L 640 56 Z" fill="#3e4730" />
      <path
        d={`M 0 -18 Q 12 -36 34 -34 L 160 -40 Q 210 -64 250 -62 L 300 -58 Q 330 -68 360 -66 Q 440 -92 520 -86 Q 590 -84 640 -74 L 720 -60 Q 800 ${-48 + tail * 0.4} 880 ${-30 + tail} L 1000 ${-8 + tail * 1.6} L 1000 ${tail * 1.6} Q 900 ${4 + tail} 860 ${6 + tail * 0.8} L 720 20 Q 660 34 600 34 L 420 34 Q 350 32 300 22 L 160 6 L 10 -4 Z`}
        fill={color}
      />
      <path d="M 6 -11 L 258 -8" stroke="#2c331f" strokeWidth={4} />
      {Array.from({ length: 16 }, (_, i) => (
        <path key={i} d={`M ${18 + i * 15} -10 l 5 9 l 5 -9 Z`} fill="#efe8cf" />
      ))}
      {Array.from({ length: 24 }, (_, i) => {
        const px = 340 + i * 26;
        const py = px < 520 ? -66 - ((px - 340) / 180) * 20 : px < 720 ? -86 + ((px - 520) / 200) * 26 : -60 + ((px - 720) / 280) * 52 + tail * ((px - 720) / 280);
        return <path key={i} d={`M ${px} ${py} l 11 -17 l 11 17 Z`} fill={plates > i / 24 ? C.accent : "#3e4730"} />;
      })}
      <ellipse cx={236} cy={-52} rx={11} ry={8} fill="#e9d98a" />
      <rect x={233} y={-59} width={5} height={14} rx={2} fill="#111" />
      <ellipse cx={26} cy={-33} rx={6} ry={4} fill="#2c331f" />
    </g>
  </svg>
);

// Seen from above: used for approach paths and the death roll.
export const CrocTop: React.FC<{ x: number; y: number; scale?: number; rotate?: number; color?: string; opacity?: number; roll?: number }> = ({ x, y, scale = 1, rotate = 0, color = "#56613f", opacity = 1, roll = 0 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${scale} ${scale * (0.35 + 0.65 * Math.abs(Math.cos(roll)))})`}>
      <path d="M -500 0 Q -430 -26 -330 -34 Q -250 -60 -160 -66 Q 0 -84 140 -62 Q 300 -40 500 0 Q 300 40 140 62 Q 0 84 -160 66 Q -250 60 -330 34 Q -430 26 -500 0 Z" fill={Math.cos(roll) < 0 ? "#cfc9a4" : color} />
      {[-230, 60].map((lx) => (
        <g key={lx}>
          <path d={`M ${lx} -60 l -30 -70 l 44 -10 l 30 70 Z`} fill="#3e4730" />
          <path d={`M ${lx} 60 l -30 70 l 44 10 l 30 -70 Z`} fill="#3e4730" />
        </g>
      ))}
      {Math.cos(roll) >= 0 ? (
        <g>
          <circle cx={-330} cy={-20} r={9} fill="#e9d98a" />
          <circle cx={-330} cy={20} r={9} fill="#e9d98a" />
        </g>
      ) : null}
    </g>
  </svg>
);

export const Person: React.FC<{ x: number; y: number; scale?: number; color?: string; lean?: number }> = ({ x, y, scale = 1, color = HUD, lean = 0 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) scale(${scale}) rotate(${lean})`}>
      <circle cx={0} cy={-150} r={22} fill={color} />
      <rect x={-22} y={-124} width={44} height={74} rx={16} fill={color} />
      <rect x={-20} y={-56} width={17} height={58} rx={8} fill={color} />
      <rect x={3} y={-56} width={17} height={58} rx={8} fill={color} />
    </g>
  </svg>
);

export const Fog: React.FC<{ level: number; color?: string }> = ({ level, color = "#1c2a1c" }) => (
  <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 62%, transparent ${Math.max(4, 46 - level * 34)}%, ${color} ${Math.max(18, 82 - level * 40)}%)`, opacity: Math.min(1, 0.55 + level * 0.45) }} />
);

export { typed, shadow, random, MONO_FAMILY };
