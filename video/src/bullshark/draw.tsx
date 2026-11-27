// Drawn scenes for "What Happens When a Bull Shark Follows You Upriver".
import React from "react";
import { AbsoluteFill, random } from "remotion";
import { useShot } from "../kit/shots";
import { MONO } from "../kit/hud";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { BUILDS, Shark } from "../megalodon/draw";

BUILDS.bull = { len: 0.9, girth: 1.45, tail: 0.95, color: "#7d8a91", belly: "#eef1f2", blunt: true };
BUILDS.tigerS = { len: 1.05, girth: 1.2, tail: 1.05, color: "#7c7f74", belly: "#ecebe2" };
BUILDS.reef = { len: 1, girth: 1, tail: 1, color: "#8a9aa3", belly: "#f0f3f4" };

const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";
const ease = (t: number) => {
  const x = Math.min(1, Math.max(0, t));
  return x * x * (3 - 2 * x);
};
const pop = (f: number, at = 0, len = 8) => {
  const t = Math.min(1, Math.max(0, (f - at) / len));
  return 1 - Math.pow(1 - t, 3);
};
const lerp = (a: number, b: number | undefined, k: number) => (b === undefined ? a : a + (b - a) * k);

const Title: React.FC<{ text?: string; color?: string; size?: number; y?: number }> = ({ text, color = C.white, size = 62, y = 170 }) =>
  text ? <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: size, color, textShadow: SHADOW }}>{text}</div> : null;

export type BActor = { b?: string; x0: number; y0: number; x1?: number; y1?: number; s?: number; s1?: number; flip?: boolean; rot?: number; open?: number; o0?: number; o1?: number };

// A brown river in profile: bank and trees above, murky water below, you wading, the shark in the murk.
export const River: React.FC<{
  sharks?: BActor[];
  you?: { x: number; s?: number; swim?: boolean } | false;
  murk?: number;
  sky?: "day" | "dusk" | "rain";
  signals?: boolean;
  bump?: boolean;
  surf?: number;
  children?: React.ReactNode;
}> = ({ sharks = [], you = { x: 1150 }, murk = 0.55, sky = "day", signals = false, bump = false, surf = 420, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const SKY = { day: ["#8fb8c8", "#d8e6dc"], dusk: ["#3b3350", "#e09a62"], rain: ["#5d6a70", "#9aa6a8"] }[sky];
  const jolt = bump ? Math.max(0, 1 - Math.abs(k - 0.5) * 6) : 0;
  const yx = you ? you.x + jolt * 30 : 0;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="rsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={SKY[0]} /><stop offset="1" stopColor={SKY[1]} /></linearGradient>
          <linearGradient id="rwat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7a6a44" /><stop offset="1" stopColor="#2b2416" /></linearGradient>
        </defs>
        <rect x={0} y={0} width={1920} height={surf} fill="url(#rsky)" />
        <path d={`M 0 ${surf - 80} C 300 ${surf - 140} 500 ${surf - 60} 800 ${surf - 110} C 1100 ${surf - 160} 1400 ${surf - 70} 1920 ${surf - 120} L 1920 ${surf} L 0 ${surf} Z`} fill="#2f4a2c" />
        {Array.from({ length: 14 }, (_, i) => <ellipse key={i} cx={i * 150 + 40} cy={surf - 120 - random(`tr${i}`) * 60} rx={90} ry={70} fill="#3d5e36" />)}
        {sky === "rain" ? Array.from({ length: 60 }, (_, i) => { const x = (random(`rx${i}`) * 1920 + f * 3) % 1920; const y = (random(`ry${i}`) * surf + f * 22) % surf; return <line key={i} x1={x} y1={y} x2={x - 6} y2={y + 26} stroke="#dfe8ea" strokeWidth={2} opacity={0.6} />; }) : null}
        <rect x={0} y={surf} width={1920} height={1080 - surf} fill="url(#rwat)" />
        {sharks.map((a, i) => (
          <g key={i} opacity={lerp(a.o0 ?? 1, a.o1, e)}>
            <Shark b={(a.b ?? "bull") as never} x={lerp(a.x0, a.x1, e)} y={lerp(a.y0, a.y1, e)} s={lerp(a.s ?? 0.7, a.s1, e)} flip={a.flip} rot={a.rot} f={f + i * 9} open={a.open} />
          </g>
        ))}
        {you ? (
          <g transform={`translate(${yx} ${surf + 60}) scale(${you.s ?? 1})`}>
            <rect x={-30} y={-150} width={60} height={130} rx={18} fill="#2e5a7a" />
            <circle cx={0} cy={-180} r={26} fill="#c98f6b" />
            <path d="M -26 -24 L -30 120 L -10 120 L 0 10 L 10 120 L 30 120 L 26 -24 Z" fill="#3a3a3a" />
            <rect x={-34} y={120} width={30} height={14} rx={6} fill="#c98f6b" />
            <rect x={4} y={120} width={30} height={14} rx={6} fill="#c98f6b" />
          </g>
        ) : null}
        {/* murk in front of everything under water */}
        <rect x={0} y={surf} width={1920} height={1080 - surf} fill="#5c4d2c" opacity={murk} />
        {Array.from({ length: 70 }, (_, i) => <circle key={i} cx={(random(`m${i}`) * 1920 + f * 0.6) % 1920} cy={surf + random(`n${i}`) * (1080 - surf)} r={2 + random(`o${i}`) * 3} fill="#c9b27c" opacity={0.35} />)}
        {signals && you
          ? [0, 1, 2, 3].map((i) => {
              const t = ((f / 30 + i / 4) % 1 + 1) % 1;
              return <ellipse key={i} cx={yx} cy={surf + 150} rx={40 + t * 320} ry={20 + t * 160} fill="none" stroke={C.cyan} strokeWidth={4} opacity={(1 - t) * 0.9} />;
            })
          : null}
        <path d={`M 0 ${surf} ${Array.from({ length: 40 }, (_, i) => `L ${i * 50} ${surf + Math.sin(i + f * 0.12) * 4}`).join(" ")} L 1920 ${surf}`} stroke="#e8dcc0" strokeWidth={3} fill="none" opacity={0.7} />
      </svg>
      {children}
    </AbsoluteFill>
  );
};

// Salt and water: a shark cutaway in the sea (balanced), in a river (water floods in), and fixed (kidneys, rectal gland).
export const Salt: React.FC<{ mode: "sea" | "river" | "fix" | "balance"; text?: string }> = ({ mode, text }) => {
  const { f, k } = useShot();
  const river = mode !== "sea";
  const swell = mode === "river" ? 1 + 0.08 * ease(k) : 1;
  return (
    <AbsoluteFill style={{ background: river ? "linear-gradient(#7a6a44, #2b2416)" : "linear-gradient(#16708a, #06283a)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: river ? 12 : 90 }, (_, i) => <circle key={i} cx={random(`so${i}`) * 1920} cy={random(`sp${i}`) * 1080} r={6} fill="#ffffff" opacity={0.55} />)}
        <g transform={`translate(960 540) scale(${swell}) translate(-960 -540)`}>
          <Shark b={"bull" as never} x={960} y={540} s={2} outline />
          {Array.from({ length: 50 }, (_, i) => <circle key={i} cx={760 + random(`si${i}`) * 420} cy={480 + random(`sj${i}`) * 110} r={6} fill="#ffffff" opacity={0.85} />)}
        </g>
        {mode === "river" ? Array.from({ length: 10 }, (_, i) => {
          const t = ((f / 24 + i / 10) % 1 + 1) % 1;
          const a = (i / 10) * Math.PI * 2;
          return <line key={i} x1={960 + Math.cos(a) * (520 - 300 * t)} y1={540 + Math.sin(a) * (300 - 170 * t)} x2={960 + Math.cos(a) * (480 - 300 * t)} y2={540 + Math.sin(a) * (280 - 170 * t)} stroke={C.cyan} strokeWidth={8} opacity={1 - t} />;
        }) : null}
        {mode === "fix" ? (
          <g>
            <ellipse cx={1000} cy={560} rx={60} ry={22} fill="#c8564a" />
            <text x={1000} y={640} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={26}>KIDNEYS</text>
            {Array.from({ length: 8 }, (_, i) => { const t = ((f / 20 + i / 8) % 1 + 1) % 1; return <circle key={i} cx={760 - t * 300} cy={600 + t * 60} r={10} fill={C.cyan} opacity={1 - t} />; })}
            <ellipse cx={720} cy={560} rx={26} ry={12} fill="#9b7a3a" opacity={0.6} />
            <text x={720} y={520} textAnchor="middle" fill="rgba(255,255,255,0.8)" fontFamily={MONO} fontWeight={700} fontSize={22}>RECTAL GLAND · SLOWS</text>
          </g>
        ) : null}
        <text x={960} y={900} textAnchor="middle" fill="rgba(255,255,255,0.8)" fontFamily={MONO} fontWeight={700} fontSize={30} letterSpacing={3}>
          {mode === "sea" ? "SEA · SALTY INSIDE AND OUT" : mode === "river" ? "RIVER · WATER FLOODS IN" : mode === "fix" ? "MORE URINE OUT · SALT KEPT IN" : "IN BETWEEN"}
        </text>
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// The shark's senses: lateral line along the body, electric pores on the snout, nostrils.
export const Senses: React.FC<{ mode: "lateral" | "electric" | "smell"; text?: string }> = ({ mode, text }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#4a3f26, #1a160d)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <Shark b={"bull" as never} x={mode === "lateral" ? 960 : 640} y={560} s={mode === "lateral" ? 2.2 : 4.2} f={f} />
        {mode === "lateral" ? Array.from({ length: 40 }, (_, i) => <circle key={i} cx={460 + i * 22} cy={540 - Math.sin(i / 40 * Math.PI) * 30} r={5} fill={C.cyan} opacity={0.4 + 0.6 * Math.abs(Math.sin(i * 0.4 - f * 0.2))} />) : null}
        {mode === "electric" ? (
          <g>
            {Array.from({ length: 40 }, (_, i) => <circle key={i} cx={1520 + random(`e${i}`) * 230} cy={470 + random(`ey${i}`) * 140} r={5} fill={C.accent} opacity={0.5 + 0.5 * Math.abs(Math.sin(i + f * 0.3))} />)}
            {[0, 1, 2].map((i) => { const t = ((f / 30 + i / 3) % 1 + 1) % 1; return <circle key={i} cx={1840} cy={540} r={40 + t * 260} fill="none" stroke={C.accent} strokeWidth={4} opacity={1 - t} />; })}
          </g>
        ) : null}
        {mode === "smell" ? Array.from({ length: 30 }, (_, i) => { const t = ((f / 40 + i / 30) % 1 + 1) % 1; return <circle key={i} cx={1900 - t * 200 + Math.sin(i) * 30} cy={560 + Math.cos(i * 2) * 60 * t} r={6} fill="#c8564a" opacity={1 - t} />; }) : null}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// Upper and lower teeth: a knife and a fork.
export const Jaws: React.FC<{ text?: string }> = ({ text }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #3a2f1c 0%, #0c0a06 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <text x={960} y={300} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={30}>UPPER · WIDE, SERRATED · CUT</text>
        {Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${560 + i * 90} 340 L ${600 + i * 90} 470 L ${640 + i * 90} 340 Z`} fill="#f4f0e4" stroke="#b9b2a2" strokeWidth={3} opacity={pop(f, i, 6)} />)}
        {Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${582 + i * 90} 720 L ${600 + i * 90} 580 L ${618 + i * 90} 720 Z`} fill="#f4f0e4" stroke="#b9b2a2" strokeWidth={3} opacity={pop(f, 8 + i, 6)} />)}
        <text x={960} y={780} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={30}>LOWER · NARROW, POINTED · HOLD</text>
      </svg>
      <Title text={text} y={110} />
    </AbsoluteFill>
  );
};

