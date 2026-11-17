import React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CrocSide, Person } from "./devices";
import { HUD, MONO } from "./hud";
import { C } from "./theme";
import { ramp } from "./ui";

// Live footage beat: muted, lightly graded, with a small source label.
export const Clip: React.FC<{ src: string; label: string; from?: number; cont?: boolean; hold?: boolean; zoom?: number }> = ({ src, label, from = 0, cont = false, hold = false, zoom = 1.04 }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const vis = Math.min(cont ? 1 : ramp(f, 0, 7), hold ? 1 : ramp(f, dur - 6, dur, 1, 0));
  return (
    <AbsoluteFill style={{ opacity: vis, background: "#020b0e" }}>
      <OffthreadVideo src={staticFile(src)} startFrom={from} muted style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom + f * 0.0004})`, filter: "saturate(0.85) contrast(1.06) brightness(0.9)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(rgba(2,14,18,0.25), rgba(2,14,18,0.45))" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 40, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 2, color: "rgba(255,255,255,0.7)" }}>{label}</div>
    </AbsoluteFill>
  );
};

type CrocState = { x: number; y: number; scale?: number; rot?: number; jaw?: number; tail?: number; flip?: boolean; show?: boolean; plates?: number };

// Side-on cut through a riverbank: land on the left, water on the right. Most of the action is staged here.
export const Shore: React.FC<{
  croc?: CrocState;
  person?: { x: number; y?: number; scale?: number; lean?: number; color?: string } | null;
  night?: number;
  zoom?: number;
  zx?: number;
  zy?: number;
  children?: React.ReactNode; // extra props drawn in scene space, under the water tint
  over?: React.ReactNode; // drawn above the water
}> = ({ croc, person = null, night = 0, zoom = 1, zx = 960, zy = 540, children, over }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#0a0f10" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - zx * zoom}px, ${540 - zy * zoom}px) scale(${zoom})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -600, top: -500, width: 3200, height: 1100, background: "linear-gradient(#232847 0%, #6c4a6e 50%, #d98a52 88%, #f0b06a 100%)" }} />
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <path d={`M -600 600 ${Array.from({ length: 70 }, (_, i) => `L ${-600 + i * 46} ${560 - random(`sh${i}`) * 60 - (i % 6 === 0 ? 36 : 0)}`).join(" ")} L 2600 600 Z`} fill="#182016" />
          <rect x={-600} y={598} width={3200} height={900} fill="#5d4d2a" />
          <path d="M -600 520 L 560 520 Q 700 530 800 640 Q 960 860 1300 930 L 2600 980 L 2600 1500 L -600 1500 Z" fill="#33291a" />
          <path d="M -600 520 L 560 520 Q 640 524 700 560" stroke="#4d6a35" strokeWidth={14} fill="none" />
        </svg>
        {children}
        {croc && croc.show !== false ? <CrocSide x={croc.x} y={croc.y} scale={croc.scale ?? 0.6} rotate={croc.rot ?? 0} tail={croc.tail ?? Math.sin(f * 0.16) * 14} flip={croc.flip} jaw={croc.jaw ?? 0} plates={croc.plates ?? 0} /> : null}
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <path d="M 700 600 L 2600 600 L 2600 1500 L 1300 1500 L 1300 930 Q 960 860 800 640 Z" fill="#3d3a1e" opacity={0.5} />
          {Array.from({ length: 16 }, (_, i) => {
            const x = ((random(`sr${i}`) * 2000 + f * (0.5 + random(`sv${i}`))) % 1900) + 720;
            return <rect key={i} x={x} y={596 + (i % 3) * 3} width={60 + random(`sw${i}`) * 110} height={4} rx={2} fill="#e3c184" opacity={0.35} />;
          })}
        </svg>
        {person ? <Person x={person.x} y={person.y ?? 522} scale={person.scale ?? 1.3} color={person.color ?? "#f1ead8"} lean={person.lean ?? 0} /> : null}
        {over}
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "#05060c", opacity: night * 0.55 }} />
    </AbsoluteFill>
  );
};

// Under the surface, seen from the side.
export const Deep: React.FC<{ croc?: CrocState; children?: React.ReactNode; tint?: string; bed?: boolean; surface?: boolean }> = ({ croc, children, tint = "#12261f", bed = true, surface = true }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: `linear-gradient(#3f4a2a 0%, ${tint} 45%, #060d0b 100%)` }}>
      {surface ? <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 150, background: "linear-gradient(rgba(240,200,130,0.35), transparent)" }} /> : null}
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{ position: "absolute", left: 200 + i * 430 + Math.sin(f * 0.01 + i) * 40, top: -100, width: 150, height: 900, background: "linear-gradient(rgba(255,230,170,0.1), transparent)", transform: "skewX(-14deg)" }} />
      ))}
      {Array.from({ length: 40 }, (_, i) => (
        <div key={i} style={{ position: "absolute", left: (random(`dx${i}`) * 1920 + f * 0.3) % 1920, top: (random(`dy${i}`) * 1080 + Math.sin(f * 0.02 + i) * 20) % 1080, width: 5, height: 5, borderRadius: 3, background: "#d8e2c0", opacity: 0.12 + random(`do${i}`) * 0.2 }} />
      ))}
      {bed ? (
        <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
          <path d="M 0 930 Q 480 890 960 920 T 1920 900 L 1920 1080 L 0 1080 Z" fill="#231d12" />
        </svg>
      ) : null}
      {children}
      {croc && croc.show !== false ? <CrocSide x={croc.x} y={croc.y} scale={croc.scale ?? 0.9} rotate={croc.rot ?? 0} tail={croc.tail ?? Math.sin(f * 0.16) * 20} flip={croc.flip} jaw={croc.jaw ?? 0} plates={croc.plates ?? 0} /> : null}
    </AbsoluteFill>
  );
};

// Large head in profile with a working jaw. `jaw` is the opening in degrees.
export const CrocHead: React.FC<{ x?: number; y?: number; scale?: number; jaw?: number; dots?: number; eyeGlow?: number; color?: string; children?: React.ReactNode }> = ({ x = 330, y = 600, scale = 1.25, jaw = 0, dots = 0, eyeGlow = 0, color = "#56613f", children }) => {
  const f = useCurrentFrame();
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <g transform={`translate(${x} ${y}) scale(${scale})`}>
        <g transform={`rotate(${-jaw} 900 44)`}>
          <path d="M 22 34 L 700 44 L 1900 52 L 1900 230 L 1000 170 Q 600 190 300 130 L 30 66 Z" fill="#48522f" />
          <path d="M 30 62 Q 300 120 600 150 L 1000 140" stroke="#c9c39c" strokeWidth={5} fill="none" opacity={0.35} />
          {Array.from({ length: 22 }, (_, i) => (
            <path key={i} d={`M ${40 + i * 27} ${36 + i * 0.4} l 9 -${22 + (i % 3) * 6} l 9 ${22 + (i % 3) * 6} Z`} fill="#f2ecd2" />
          ))}
        </g>
        <path d="M 0 4 Q 18 -40 70 -44 L 520 -70 Q 600 -132 690 -130 L 780 -112 Q 900 -152 1000 -142 L 1900 -190 L 1900 60 L 1000 46 L 700 34 L 0 22 Z" fill={color} />
        {Array.from({ length: 24 }, (_, i) => (
          <path key={i} d={`M ${28 + i * 25} ${20 + i * 0.5} l 9 ${22 + (i % 3) * 7} l 9 -${22 + (i % 3) * 7} Z`} fill="#f2ecd2" />
        ))}
        {Array.from({ length: 34 }, (_, i) => (
          <circle key={i} cx={720 + random(`hs${i}`) * 270} cy={-110 + random(`ht${i}`) * 140} r={9 + random(`hr${i}`) * 9} fill="#3e4730" opacity={0.55} />
        ))}
        <ellipse cx={650} cy={-96} rx={30} ry={22} fill="#e9d98a" />
        <rect x={644} y={-116} width={11} height={40} rx={5} fill="#111" />
        {eyeGlow > 0 ? <circle cx={650} cy={-96} r={34 + Math.sin(f * 0.3) * 5} fill="#ff3b2a" opacity={eyeGlow} /> : null}
        <ellipse cx={44} cy={-34} rx={15} ry={8} fill="#2c331f" />
        <ellipse cx={820} cy={-108} rx={34} ry={10} fill="#2c331f" />
        {dots > 0
          ? Array.from({ length: 150 }, (_, i) => {
              const px = 40 + random(`jd${i}`) * 640;
              const top = random(`je${i}`) < 0.5;
              const py = top ? -30 + random(`jf${i}`) * 44 - px * 0.03 : 60 + random(`jf${i}`) * 50 + px * 0.05;
              return i / 150 < dots ? <circle key={`d${i}`} cx={px} cy={py} r={4.5} fill={C.accent} opacity={0.6 + 0.4 * Math.sin(f * 0.2 + i)} /> : null;
            })
          : null}
        {children}
      </g>
    </svg>
  );
};

// A label with a thin leader line, for pointing at parts of an animated scene.
export const Tag: React.FC<{ x: number; y: number; tx: number; ty: number; text: string; color?: string }> = ({ x, y, tx, ty, text, color = HUD }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const vis = Math.min(ramp(f, 0, 6), ramp(f, dur - 5, dur, 1, 0));
  return (
    <AbsoluteFill style={{ opacity: vis }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <line x1={x} y1={y} x2={x + (tx - x) * ramp(f, 0, 8)} y2={y + (ty - y) * ramp(f, 0, 8)} stroke={color} strokeWidth={4} />
        <circle cx={x} cy={y} r={9} fill={color} />
      </svg>
      <div style={{ position: "absolute", left: tx + 14, top: ty - 24, fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 2, color, textShadow: "0 3px 14px #000", whiteSpace: "nowrap", opacity: ramp(f, 6, 12) }}>{text}</div>
    </AbsoluteFill>
  );
};

export const lerp = (f: number, a: number, b: number, v0: number, v1: number) => interpolate(f, [a, b], [v0, v1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
