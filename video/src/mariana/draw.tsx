// Drawn shots for the Mariana descent: one ocean whose colour, light and life change with depth,
// a depth counter (centred above the captions, never in a corner), and the hunters of each zone.
import React from "react";
import { AbsoluteFill, interpolate, random } from "remotion";
import { registerKind } from "../kit/edit-rules";
import { ease, pop, Svg, useShot } from "../kit/shots";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { MONO } from "../kit/hud";
import { Bubbles, Caustics, Drift, Haze, Rays, Snow } from "../kit/vfx";
import { Diver } from "../humpback/draw";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";

// ---------- depth → light ----------
const DEPTHS = [0, 200, 600, 1000, 4000, 11000];
const LIGHT = [1, 0.62, 0.28, 0.04, 0, 0];
export const lightAt = (d: number) => interpolate(d, DEPTHS, LIGHT, clamp);
export const zoneOf = (d: number) =>
  d < 200 ? "SUNLIT ZONE" : d < 1000 ? "TWILIGHT ZONE" : d < 4000 ? "MIDNIGHT ZONE" : d < 6000 ? "THE ABYSS" : "THE HADAL ZONE";
const mix = (a: number[], b: number[], t: number) => `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], t))).join(",")})`;
const waterTop = (l: number) => mix([2, 6, 10], [58, 160, 196], l);
const waterBot = (l: number) => mix([0, 2, 4], [10, 70, 100], l);

// ---------- the creatures (all face right at s = 1; flip to face left) ----------
type CP = { s?: number; f?: number; glow?: number };
const Whitetip: React.FC<CP> = ({ f = 0 }) => {
  const w = Math.sin(f * 0.18) * 10;
  return (
    <g>
      <path d={`M -330 0 L -420 ${-80 + w} L -395 0 L -430 ${70 + w} Z`} fill="#5d7180" />
      <path d="M 300 6 C 270 -40 150 -62 0 -60 C -150 -58 -280 -30 -340 0 C -280 34 -140 56 0 54 C 140 52 260 38 300 6 Z" fill="#6f8796" />
      <path d="M 300 6 C 260 30 140 52 0 54 C -140 56 -260 34 -330 4 C -220 20 -100 30 20 30 C 140 30 240 20 300 6 Z" fill="#c9d4da" />
      <path d="M -10 -58 C 20 -150 60 -170 90 -168 C 70 -120 70 -90 80 -50 Z" fill="#6f8796" />
      <path d="M 66 -150 C 76 -165 86 -168 90 -168 C 82 -150 80 -140 80 -130 Z" fill="#f4f8fa" />
      <path d={`M 60 30 C 0 ${130 + w} -110 ${190 + w} -170 ${200 + w} C -110 150 -40 90 0 40 Z`} fill="#6f8796" />
      <path d={`M -120 ${178 + w} C -150 ${195 + w} -165 ${200 + w} -170 ${200 + w} C -150 ${185 + w} -135 ${175 + w} -125 ${165 + w} Z`} fill="#f4f8fa" />
      <circle cx={232} cy={-10} r={7} fill="#0b1116" />
      {[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M ${170 - i * 16} -14 q -6 20 0 36`} stroke="#4d5e6a" strokeWidth={3} fill="none" />)}
    </g>
  );
};
const Swordfish: React.FC<CP> = ({ f = 0, glow = 0 }) => {
  const w = Math.sin(f * 0.22) * 12;
  return (
    <g>
      <path d={`M -300 0 L -380 ${-110 + w} L -350 0 L -380 ${110 + w} Z`} fill="#2f3f52" />
      <path d="M 260 -4 C 220 -50 100 -64 -60 -54 C -200 -44 -290 -16 -320 0 C -290 18 -200 44 -60 52 C 100 58 220 44 260 4 Z" fill="#41566d" />
      <path d="M 260 4 C 220 40 100 54 -60 50 C -180 44 -270 20 -310 4 C -200 18 -80 26 40 26 C 150 26 220 16 260 4 Z" fill="#b8c3cc" />
      <path d="M 250 -4 L 560 -2 L 250 6 Z" fill="#2f3f52" />
      <path d="M 40 -52 C 60 -150 90 -170 110 -168 C 100 -120 96 -90 110 -48 Z" fill="#2f3f52" />
      {glow > 0 ? <circle cx={175} cy={-14} r={60} fill="url(#heat)" opacity={glow} /> : null}
      <circle cx={196} cy={-12} r={16} fill="#0b1116" />
      <circle cx={192} cy={-16} r={5} fill="#cfe9ef" />
    </g>
  );
};
const Cookie: React.FC<CP> = ({ glow = 0, f = 0 }) => (
  <g>
    <path d={`M -160 0 L -210 ${-40 + Math.sin(f * 0.3) * 6} L -195 0 L -210 ${36 + Math.sin(f * 0.3) * 6} Z`} fill="#5b4636" />
    <path d="M 150 0 C 140 -28 60 -36 -20 -32 C -100 -28 -150 -14 -170 0 C -150 14 -100 28 -20 32 C 60 34 140 28 150 0 Z" fill="#6b5442" />
    {glow > 0 ? <path d="M 140 6 C 120 26 60 32 -20 30 C -100 28 -150 14 -168 4 C -100 10 -20 14 60 12 C 110 10 130 8 140 6 Z" fill="#8fe8ff" opacity={glow} filter="url(#soft)" /> : null}
    {glow > 0 ? <path d="M 70 4 L 100 4 L 104 30 L 72 32 Z" fill="#1a120c" opacity={glow} /> : null}
    <circle cx={110} cy={-8} r={9} fill="#d9f3ff" />
    <circle cx={112} cy={-8} r={4} fill="#0b1116" />
  </g>
);
const Squid: React.FC<CP> = ({ f = 0 }) => (
  <g>
    {/* mantle points left, arms trail right */}
    <path d="M -520 0 C -470 -60 -300 -86 -120 -70 C -40 -64 0 -40 10 0 C 0 40 -40 64 -120 70 C -300 86 -470 60 -520 0 Z" fill="#a33a2b" />
    <path d="M -520 0 L -600 -70 L -560 0 L -600 70 Z" fill="#8a2f22" />
    {Array.from({ length: 8 }, (_, i) => {
      const a = (i - 3.5) * 9;
      const wv = Math.sin(f * 0.12 + i) * 30;
      return <path key={i} d={`M 0 ${a} C 120 ${a * 2 + wv} 220 ${a * 3 - wv} ${330 + (i % 3) * 30} ${a * 3.6 + wv}`} stroke="#b54434" strokeWidth={22 - Math.abs(i - 3.5) * 2} fill="none" strokeLinecap="round" />;
    })}
    {[-1, 1].map((s) => (
      <path key={s} d={`M 0 ${s * 10} C 260 ${s * 60 + Math.sin(f * 0.08) * 40} 520 ${s * 30 - Math.sin(f * 0.08 + 1) * 50} 820 ${s * 80 + Math.sin(f * 0.07) * 60}`} stroke="#c2513f" strokeWidth={9} fill="none" strokeLinecap="round" />
    ))}
    <circle cx={-40} cy={-6} r={34} fill="#f4f0e8" />
    <circle cx={-36} cy={-6} r={22} fill="#0b0b0b" />
    <circle cx={-42} cy={-12} r={7} fill="#fff" />
  </g>
);
const SpermWhale: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M -560 0 L -680 ${-70 + Math.sin(f * 0.1) * 12} L -640 0 L -680 ${70 + Math.sin(f * 0.1) * 12} Z`} fill="#3a3f46" />
    <path d="M 420 -20 C 420 -110 330 -130 150 -128 C -40 -126 -300 -90 -560 -6 L -560 12 C -300 70 -40 104 150 110 C 330 114 420 90 420 30 Z" fill="#4a5058" />
    {Array.from({ length: 16 }, (_, i) => <path key={i} d={`M ${-420 + i * 40} ${-60 + random(`sw${i}`) * 30} q 10 30 0 60`} stroke="#3c4148" strokeWidth={3} fill="none" opacity={0.7} />)}
    <path d="M 380 60 L 140 70 C 160 86 300 92 380 76 Z" fill="#d9dde0" />
    <circle cx={150} cy={10} r={8} fill="#0b1116" />
    <path d="M -60 70 C -80 120 -130 150 -180 160 C -150 120 -120 90 -100 64 Z" fill="#3a3f46" />
  </g>
);
const Beaked: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M -360 0 L -440 ${-56 + Math.sin(f * 0.14) * 10} L -410 0 L -440 ${56 + Math.sin(f * 0.14) * 10} Z`} fill="#5b4c42" />
    <path d="M 300 6 C 260 -40 160 -66 0 -62 C -160 -58 -300 -26 -370 0 C -300 30 -160 60 0 60 C 160 60 260 44 300 6 Z" fill="#6e5d50" />
    <path d="M 300 6 L 370 10 L 300 16 Z" fill="#cdbfae" />
    <path d="M 300 6 C 260 -40 180 -62 120 -60 C 160 -30 170 30 120 58 C 200 56 270 40 300 6 Z" fill="#d8ccbc" />
    {Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${-200 + i * 45} ${-30 + random(`bk${i}`) * 50} l ${60 + random(`bl${i}`) * 50} ${random(`bm${i}`) * 16 - 8}`} stroke="#efe8dc" strokeWidth={3} opacity={0.7} />)}
    <circle cx={210} cy={-6} r={6} fill="#0b1116" />
  </g>
);
const Angler: React.FC<CP> = ({ f = 0, glow = 1 }) => {
  const lure = 0.6 + 0.4 * Math.sin(f * 0.25);
  return (
    <g>
      <path d="M -170 0 L -240 -50 L -230 0 L -240 50 Z" fill="#1a1414" />
      <path d="M 120 -30 C 110 -120 -20 -150 -110 -110 C -190 -70 -190 70 -110 110 C -10 150 110 120 130 50 Z" fill="#241b1b" />
      <path d="M 130 50 C 110 120 0 130 -40 90 L 120 -30 Z" fill="#100a0a" />
      {Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${130 - i * 18} ${-28 + i * 9} l -6 ${22 + (i % 2) * 10} l -8 -${20 + (i % 2) * 8} Z`} fill="#efe8dc" />)}
      <path d={`M 0 -130 C 60 -230 160 -240 ${200 + Math.sin(f * 0.1) * 10} -180`} stroke="#3b2c2c" strokeWidth={6} fill="none" />
      <circle cx={200 + Math.sin(f * 0.1) * 10} cy={-176} r={44} fill="url(#lure)" opacity={glow * lure} />
      <circle cx={200 + Math.sin(f * 0.1) * 10} cy={-176} r={12} fill="#d8fbff" opacity={glow} />
      <circle cx={40} cy={-60} r={8} fill="#cfe9ef" opacity={0.7} />
    </g>
  );
};
const Viper: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M -300 0 L -350 ${-34 + Math.sin(f * 0.2) * 6} L -340 0 L -350 ${34 + Math.sin(f * 0.2) * 6} Z`} fill="#16222a" />
    <path d="M 160 -10 C 120 -50 0 -48 -120 -30 C -220 -16 -280 -6 -310 0 C -280 8 -220 20 -120 30 C 0 44 120 40 160 10 Z" fill="#1c2c36" />
    <path d="M 160 -10 L 230 -40 L 160 10 Z" fill="#0d151a" />
    {[[200, -34, 70], [180, -26, 50], [170, 6, -64], [150, 4, -40]].map(([x, y, h], i) => <path key={i} d={`M ${x - 5} ${y} L ${x} ${y + h} L ${x + 5} ${y} Z`} fill="#e9f1f2" />)}
    {Array.from({ length: 14 }, (_, i) => <circle key={i} cx={120 - i * 28} cy={22} r={4} fill="#7fe9ff" opacity={0.5 + 0.5 * Math.sin(f * 0.2 + i)} />)}
    <circle cx={110} cy={-16} r={12} fill="#0b0b0b" stroke="#6aa" strokeWidth={2} />
  </g>
);
const Fangtooth: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M -150 0 L -210 ${-50 + Math.sin(f * 0.2) * 8} L -190 0 L -210 ${50 + Math.sin(f * 0.2) * 8} Z`} fill="#1e1a1a" />
    <path d="M 150 -20 C 140 -110 0 -130 -80 -90 C -160 -50 -170 40 -100 80 C -20 120 120 100 150 40 Z" fill="#2c2524" />
    <path d="M 150 -20 L 160 40 L 70 40 Z" fill="#0c0808" />
    {[[150, -20, 60], [120, -14, 46], [96, -8, 36], [140, 40, -64], [110, 40, -48]].map(([x, y, h], i) => <path key={i} d={`M ${x - 7} ${y} L ${x} ${y + h} L ${x + 7} ${y} Z`} fill="#efe8dc" />)}
    <circle cx={60} cy={-50} r={10} fill="#bcd" opacity={0.6} />
  </g>
);
const Loosejaw: React.FC<CP> = ({ f = 0, glow = 1 }) => (
  <g>
    <path d={`M -260 0 L -310 ${-30 + Math.sin(f * 0.2) * 6} L -300 0 L -310 ${30 + Math.sin(f * 0.2) * 6} Z`} fill="#0d0d10" />
    <path d="M 150 -6 C 110 -40 0 -42 -100 -28 C -190 -14 -250 -4 -270 0 C -250 6 -190 18 -100 28 C 0 40 110 36 150 6 Z" fill="#17171c" />
    <path d="M 150 6 L 220 40 L 120 24 Z" fill="#17171c" />
    <circle cx={100} cy={-12} r={10} fill="#1c1c22" stroke="#555" strokeWidth={2} />
    <ellipse cx={104} cy={10} rx={14} ry={8} fill="#ff3a2a" opacity={glow} />
    <ellipse cx={70} cy={-14} rx={7} ry={5} fill="#7fe9ff" opacity={0.8} />
  </g>
);
const Rattail: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M 140 -10 C 120 -60 40 -64 -20 -40 C -120 -20 -300 0 -460 ${Math.sin(f * 0.1) * 10} C -300 14 -120 30 -20 40 C 40 60 120 56 140 10 Z`} fill="#8c8a84" />
    <path d="M 140 -10 L 190 0 L 140 10 Z" fill="#7a7872" />
    <path d="M -20 -40 C 0 -90 30 -100 40 -100 C 30 -70 30 -60 40 -36 Z" fill="#7a7872" />
    <circle cx={90} cy={-14} r={20} fill="#1a1a1a" />
    <circle cx={86} cy={-18} r={6} fill="#cfe9ef" />
  </g>
);
const Amphipod: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d="M -60 10 C -60 -30 0 -46 50 -30 C 80 -20 90 0 80 20 C 40 30 -20 34 -60 10 Z" fill="#f1e6d6" />
    {Array.from({ length: 6 }, (_, i) => <path key={i} d={`M ${-40 + i * 20} -36 q 4 -8 0 -12`} stroke="#d9c8b0" strokeWidth={3} fill="none" />)}
    {Array.from({ length: 7 }, (_, i) => <path key={i} d={`M ${-50 + i * 18} 20 l ${-6 + Math.sin(f * 0.6 + i) * 4} 26`} stroke="#e2d2bc" strokeWidth={4} />)}
    <path d="M 80 0 q 30 -20 50 -40 M 80 4 q 34 -6 56 -22" stroke="#e2d2bc" strokeWidth={3} fill="none" />
    <circle cx={64} cy={-12} r={5} fill="#3a1010" />
  </g>
);
const Snailfish: React.FC<CP> = ({ f = 0 }) => {
  const w = Math.sin(f * 0.12);
  return (
    <g opacity={0.95}>
      <path d={`M 120 0 C 120 -70 40 -90 -20 -70 C -120 -40 -260 -20 -400 ${w * 20} C -260 30 -120 60 -20 70 C 40 90 120 70 120 0 Z`} fill="#f2c4c4" opacity={0.85} />
      <path d={`M -20 -64 C -150 -70 -300 -40 -400 ${w * 20} C -300 0 -150 -30 -20 -40 Z`} fill="#f7d9d9" opacity={0.6} />
      <path d={`M -20 64 C -150 70 -300 40 -400 ${w * 20} C -300 10 -150 36 -20 40 Z`} fill="#f7d9d9" opacity={0.6} />
      <path d="M 20 -10 C 0 -30 -30 -30 -60 -10 C -30 10 0 10 20 -10 Z" fill="#c98f8f" opacity={0.5} />
      <circle cx={70} cy={-18} r={11} fill="#2a1414" />
      <circle cx={67} cy={-21} r={3} fill="#fff" />
      <path d="M 120 10 q -20 12 -40 8" stroke="#c98f8f" strokeWidth={4} fill="none" />
    </g>
  );
};
const Lantern: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d="M 40 0 C 30 -16 0 -18 -30 -12 L -50 -20 L -46 0 L -50 20 L -30 12 C 0 18 30 16 40 0 Z" fill="#6f8aa0" />
    {[0, 1, 2, 3].map((i) => <circle key={i} cx={20 - i * 14} cy={8} r={3} fill="#9ff3ff" opacity={0.6 + 0.4 * Math.sin(f * 0.3 + i)} />)}
    <circle cx={26} cy={-4} r={5} fill="#0b0b0b" />
  </g>
);
const Sleeper: React.FC<CP> = ({ f = 0 }) => (
  <g>
    <path d={`M -360 0 L -430 ${-60 + Math.sin(f * 0.06) * 8} L -410 0 L -430 ${50 + Math.sin(f * 0.06) * 8} Z`} fill="#26292c" />
    <path d="M 300 6 C 280 -60 150 -90 0 -86 C -160 -82 -300 -40 -380 0 C -300 40 -160 84 0 86 C 150 88 280 70 300 6 Z" fill="#33373b" />
    <path d="M -40 -84 C -20 -120 10 -126 30 -124 C 20 -100 20 -94 30 -84 Z" fill="#26292c" />
    <circle cx={220} cy={-14} r={8} fill="#7a8a90" />
  </g>
);
const Hagfish: React.FC<CP> = ({ f = 0 }) => (
  <path d={`M 120 0 C 60 ${-20 + Math.sin(f * 0.3) * 10} 0 ${20 - Math.sin(f * 0.3) * 10} -60 ${Math.sin(f * 0.3 + 1) * 14} C -120 ${-20 + Math.sin(f * 0.3 + 2) * 10} -180 10 -220 0`} stroke="#d9a3a0" strokeWidth={22} fill="none" strokeLinecap="round" />
);
const Cucumber: React.FC<CP> = ({ f = 0 }) => (
  <g opacity={0.9}>
    <path d="M -110 0 C -110 -50 100 -60 120 -10 C 130 30 -100 40 -110 0 Z" fill="#e7a0b4" opacity={0.75} />
    {Array.from({ length: 7 }, (_, i) => <path key={i} d={`M 116 ${-20 + i * 5} q ${20 + Math.sin(f * 0.2 + i) * 6} -${10 - i * 3} 40 -${4 - i}`} stroke="#f2c2d0" strokeWidth={4} fill="none" />)}
    {Array.from({ length: 8 }, (_, i) => <path key={i} d={`M ${-90 + i * 26} -40 l 4 -24`} stroke="#f2c2d0" strokeWidth={4} />)}
  </g>
);
const Trieste: React.FC<CP> = () => (
  <g>
    <path d="M -300 -60 C -300 -130 300 -130 320 -60 C 320 -10 -300 -10 -300 -60 Z" fill="#cfd3d6" stroke="#2a3238" strokeWidth={5} />
    <rect x={-40} y={-150} width={80} height={40} rx={6} fill="#b8bec2" stroke="#2a3238" strokeWidth={5} />
    <rect x={-20} y={-12} width={40} height={30} fill="#9aa3a8" />
    <circle cx={0} cy={60} r={50} fill="#9aa3a8" stroke="#2a3238" strokeWidth={5} />
    <circle cx={20} cy={60} r={12} fill="#ffe7a0" />
  </g>
);
const Bag: React.FC<CP> = ({ f = 0 }) => (
  <g transform={`rotate(${Math.sin(f * 0.05) * 3})`}>
    <path d="M -120 40 C -140 -20 -100 -70 -40 -60 L -30 -110 L -10 -60 C 20 -70 30 -60 50 -62 L 70 -112 L 80 -56 C 140 -50 150 10 120 50 C 60 80 -60 80 -120 40 Z" fill="#e8ecee" opacity={0.85} />
    <path d="M -80 0 C -40 -20 20 20 80 -10 M -60 30 C -10 20 40 40 100 20" stroke="#b9c2c6" strokeWidth={4} fill="none" />
  </g>
);
const Sub: React.FC<CP> = () => (
  <g>
    <path d="M 420 0 C 420 -60 330 -70 -300 -60 C -380 -56 -420 -30 -420 0 C -420 30 -380 56 -300 60 C 330 70 420 60 420 0 Z" fill="#1c2329" />
    <path d="M 60 -60 L 80 -140 L 200 -140 L 210 -62 Z" fill="#1c2329" />
    <path d="M 420 0 C 420 -40 380 -56 330 -60 C 360 -30 360 30 330 60 C 380 56 420 40 420 0 Z" fill="#3a4650" />
    <path d="M -420 0 L -480 -60 L -470 0 L -480 60 Z" fill="#1c2329" />
  </g>
);
const Cruiser: React.FC<CP> = () => (
  <g>
    <path d="M -520 0 L 540 0 L 480 60 L -470 60 Z" fill="#59636b" />
    <path d="M -300 0 L -300 -50 L -150 -50 L -150 -110 L -60 -110 L -60 -170 L 0 -170 L 0 -60 L 120 -60 L 120 -120 L 160 -120 L 160 -60 L 280 -60 L 280 0 Z" fill="#6b757d" />
    <rect x={-20} y={-260} width={10} height={100} fill="#59636b" />
    {[-380, -240, 340, 420].map((x) => <rect key={x} x={x} y={-24} width={70} height={18} fill="#4b545b" />)}
  </g>
);
const Carcass: React.FC<CP> = () => (
  <g>
    <path d="M -400 0 C -300 -40 300 -50 420 0 Z" fill="#cbbfb0" opacity={0.9} />
    {Array.from({ length: 18 }, (_, i) => <path key={i} d={`M ${-320 + i * 38} -10 C ${-330 + i * 38} -70 ${-300 + i * 38} -90 ${-290 + i * 38} -96`} stroke="#e8e0d4" strokeWidth={9} fill="none" strokeLinecap="round" />)}
    <path d="M 300 -10 C 360 -60 440 -40 460 0 Z" fill="#e8e0d4" />
  </g>
);

const CAST: Record<string, React.FC<CP>> = {
  whitetip: Whitetip, swordfish: Swordfish, cookie: Cookie, squid: Squid, sperm: SpermWhale, beaked: Beaked, angler: Angler, viper: Viper,
  fangtooth: Fangtooth, loosejaw: Loosejaw, rattail: Rattail, amphipod: Amphipod, snailfish: Snailfish, lantern: Lantern, sleeper: Sleeper,
  hagfish: Hagfish, cucumber: Cucumber, trieste: Trieste, bag: Bag, sub: Sub, cruiser: Cruiser, carcass: Carcass,
};
export type Actor = { c: keyof typeof CAST; x0: number; x1?: number; y0: number; y1?: number; s0?: number; s1?: number; flip?: boolean; rot?: number; o0?: number; o1?: number; glow?: number; bob?: number };
export const Act: React.FC<{ a: Actor; e: number; f: number }> = ({ a, e, f }) => {
  const Comp = CAST[a.c];
  const s = lerp(a.s0 ?? 1, a.s1 ?? a.s0 ?? 1, e);
  const x = lerp(a.x0, a.x1 ?? a.x0, e);
  const y = lerp(a.y0, a.y1 ?? a.y0, e) + Math.sin(f * 0.07 + a.x0) * (a.bob ?? 6);
  return (
    <g transform={`translate(${x} ${y}) rotate(${a.rot ?? 0}) scale(${a.flip ? -s : s} ${s})`} opacity={lerp(a.o0 ?? 1, a.o1 ?? a.o0 ?? 1, e)}>
      <Comp f={f} glow={a.glow ?? 1} />
    </g>
  );
};
const Defs: React.FC = () => (
  <defs>
    <radialGradient id="lure">
      <stop offset="0" stopColor="#dffcff" stopOpacity={1} />
      <stop offset="0.35" stopColor="#7fe9ff" stopOpacity={0.7} />
      <stop offset="1" stopColor="#7fe9ff" stopOpacity={0} />
    </radialGradient>
    <radialGradient id="heat">
      <stop offset="0" stopColor="#ffb347" stopOpacity={1} />
      <stop offset="1" stopColor="#ff5a1f" stopOpacity={0} />
    </radialGradient>
    <filter id="soft"><feGaussianBlur stdDeviation="6" /></filter>
  </defs>
);

// ---------- the depth counter: centred above the captions ----------
export const Counter: React.FC<{ d: number; zone?: boolean }> = ({ d, zone = true }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: 690, textAlign: "center", textShadow: SHADOW }}>
    <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 66, color: C.cyan, letterSpacing: 2 }}>{`${Math.round(d).toLocaleString("en-US")} M`}</div>
    {zone ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 18, color: "rgba(255,255,255,0.75)", letterSpacing: 4, marginTop: 2 }}>{zoneOf(d)}</div> : null}
  </div>
);

// ---------- the ocean at a given depth ----------
export const Water: React.FC<{
  d0: number;
  d1?: number;
  count?: boolean;
  cast?: Actor[];
  diver?: { x0: number; x1?: number; y0: number; y1?: number; s?: number; rot?: number; torch?: boolean };
  floor?: number;
  walls?: boolean;
  surface?: boolean;
  specks?: number;
  migrate?: boolean;
  clicks?: { x: number; y: number; tx: number; ty: number };
  beam?: { x: number; y: number; len: number };
  z0?: number;
  z1?: number;
  shake?: boolean;
  children?: React.ReactNode;
}> = ({ d0, d1, count = false, cast = [], diver, floor, walls = false, surface = false, specks = 0, migrate = false, clicks, beam, z0 = 1, z1 = 1.04, shake = false, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const d = lerp(d0, d1 ?? d0, k);
  const l = lightAt(d);
  const sh = shake ? Math.sin(f * 1.7) * 7 * Math.max(0, 1 - f / 18) : 0;
  const z = lerp(z0, z1, e);
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Drift amount={0.7} focus={false} seed={d0 / 300}>
        <AbsoluteFill style={{ background: `linear-gradient(${waterTop(l)} 0%, ${waterBot(l)} 100%)`, transform: `scale(${z}) translate(${sh}px, ${-sh}px)` }}>
          <Svg>
            <Defs />
            {surface ? (
              <g>
                <path d={`M 0 0 L 1920 0 L 1920 ${60 + Math.sin(f * 0.1) * 6} ${Array.from({ length: 16 }, (_, i) => `Q ${1920 - i * 120 - 60} ${40 + Math.sin(f * 0.15 + i) * 14} ${1920 - (i + 1) * 120} ${60 + Math.sin(f * 0.1 + i) * 6}`).join(" ")} Z`} fill="#bfeaf6" opacity={0.55} />
              </g>
            ) : null}
            {Array.from({ length: specks }, (_, i) => {
              const on = 0.5 + 0.5 * Math.sin(f * (0.05 + random(`sp${i}`) * 0.1) + i);
              return <circle key={i} cx={random(`sx${i}`) * 1920} cy={random(`sy${i}`) * 1080} r={2 + random(`sr${i}`) * 3} fill={random(`sc${i}`) > 0.3 ? "#7fe9ff" : "#c9f7c9"} opacity={on * 0.8} />;
            })}
            {migrate
              ? Array.from({ length: 70 }, (_, i) => (
                  <g key={i} transform={`translate(${random(`mx${i}`) * 1920} ${((random(`my${i}`) * 1300 - f * (4 + random(`mv${i}`) * 4)) % 1300 + 1300) % 1300 - 100}) rotate(-70) scale(${0.5 + random(`ms${i}`) * 0.5})`}>
                    <Lantern f={f + i} />
                  </g>
                ))
              : null}
            {floor !== undefined ? (
              <g>
                <path d={`M 0 ${floor} C 400 ${floor - 20} 900 ${floor + 16} 1300 ${floor - 10} C 1600 ${floor - 24} 1800 ${floor + 6} 1920 ${floor} L 1920 1080 L 0 1080 Z`} fill={mix([30, 32, 34], [120, 112, 96], Math.max(l, 0.12))} />
                {Array.from({ length: 40 }, (_, i) => <circle key={i} cx={random(`fl${i}`) * 1920} cy={floor + 20 + random(`fm${i}`) * (1080 - floor)} r={2 + random(`fn${i}`) * 4} fill="#5a5650" opacity={0.6} />)}
              </g>
            ) : null}
            {walls ? (
              <g fill="#101315">
                <path d={`M 0 0 L 420 0 C 380 300 460 600 360 1080 L 0 1080 Z`} />
                <path d={`M 1920 0 L 1520 0 C 1560 300 1460 640 1580 1080 L 1920 1080 Z`} />
                {Array.from({ length: 12 }, (_, i) => <path key={i} d={`M ${300 + random(`wa${i}`) * 100} ${i * 90} l 60 30 l -50 30`} stroke="#22282b" strokeWidth={6} fill="none" />)}
              </g>
            ) : null}
            {beam ? <path d={`M ${beam.x} ${beam.y} L ${beam.x + beam.len} ${beam.y - 90} L ${beam.x + beam.len} ${beam.y + 90} Z`} fill="#ff3a2a" opacity={0.18} /> : null}
            {clicks
              ? Array.from({ length: 5 }, (_, i) => {
                  const p = ((f + i * 9) % 45) / 45;
                  const x = lerp(clicks.x, clicks.tx, p);
                  const y = lerp(clicks.y, clicks.ty, p);
                  return <path key={i} d={`M ${x} ${y - 70} q 34 70 0 140`} stroke={C.cyan} strokeWidth={6} fill="none" opacity={1 - p} />;
                })
              : null}
            {cast.map((a, i) => <Act key={i} a={a} e={e} f={f} />)}
            {diver ? <Diver x={lerp(diver.x0, diver.x1 ?? diver.x0, e)} y={lerp(diver.y0, diver.y1 ?? diver.y0, e)} s={diver.s ?? 0.7} rot={diver.rot ?? 0} f={f} torch={diver.torch} /> : null}
          </Svg>
          {children}
        </AbsoluteFill>
      </Drift>
      {l > 0.3 ? <Caustics opacity={0.12 * l} /> : null}
      {l > 0.05 ? <Rays strength={l} from={960} /> : null}
      <Snow n={d > 1000 ? 120 : 70} opacity={d > 200 ? 0.9 : 0.5} seed={`w${d0}`} />
      {diver?.torch ? <Bubbles streams={[lerp(diver.x0, diver.x1 ?? diver.x0, e)]} n={10} y0={lerp(diver.y0, diver.y1 ?? diver.y0, e)} /> : null}
      <Haze depth={1 - l} color="0,6,10" />
      {count ? <Counter d={d} /> : null}
    </AbsoluteFill>
  );
};
registerKind("drawn", Water);

// ---------- diagrams ----------
const ZONES: [string, number, number][] = [["SUNLIT", 0, 200], ["TWILIGHT", 200, 1000], ["MIDNIGHT", 1000, 4000], ["ABYSS", 4000, 6000], ["HADAL", 6000, 11000]];
const yOf = (d: number) => 80 + Math.sqrt(Math.max(0, d) / 11000) * 690;
// The whole column of ocean, surface to trench floor, with a marker sliding to a depth.
export const Column: React.FC<{ d0?: number; d1?: number; hi?: string; marks?: { d: number; text: string }[]; everest?: boolean }> = ({ d0 = 0, d1, hi, marks = [], everest = false }) => {
  const { f, k } = useShot();
  const d = lerp(d0, d1 ?? d0, ease(k));
  return (
    <AbsoluteFill style={{ background: "#020a0e" }}>
      <Svg>
        {ZONES.map(([name, a, b]) => {
          const l = lightAt((a + b) / 2);
          return (
            <g key={name} opacity={hi && hi !== name ? 0.45 : 1}>
              <rect x={640} y={yOf(a)} width={640} height={yOf(b) - yOf(a)} fill={mix([10, 24, 34], [40, 130, 170], l)} stroke={hi === name ? C.accent : "#0b2a36"} strokeWidth={hi === name ? 6 : 2} />
              <text x={600} y={(yOf(a) + yOf(b)) / 2 + 12} textAnchor="end" fontFamily={FONT} fontWeight={800} fontSize={34} fill={hi === name ? C.accent : C.white}>{name}</text>
              <text x={1310} y={yOf(a) + 26} fontFamily={MONO} fontWeight={700} fontSize={22} fill="rgba(255,255,255,0.7)">{`${a.toLocaleString("en-US")} M`}</text>
            </g>
          );
        })}
        <text x={1310} y={yOf(11000) - 6} fontFamily={MONO} fontWeight={700} fontSize={22} fill="rgba(255,255,255,0.7)">≈ 11,000 M</text>
        {everest ? (
          <g opacity={pop(f, 4, 14)}>
            <path d={`M 700 ${yOf(11000)} L 960 ${yOf(11000 - 8849)} L 1220 ${yOf(11000)} Z`} fill="#c7cdd1" />
            <path d={`M 910 ${yOf(11000 - 8849) + 60} L 960 ${yOf(11000 - 8849)} L 1010 ${yOf(11000 - 8849) + 60} L 980 ${yOf(11000 - 8849) + 50} L 960 ${yOf(11000 - 8849) + 70} Z`} fill="#fff" />
            <line x1={960} y1={yOf(0)} x2={960} y2={yOf(11000 - 8849)} stroke={C.accent} strokeWidth={5} strokeDasharray="14 10" />
            <text x={990} y={yOf(420)} fontFamily={FONT} fontWeight={800} fontSize={40} fill={C.accent}>2 KM OF WATER</text>
            <text x={990} y={yOf(420) + 40} fontFamily={MONO} fontWeight={700} fontSize={22} fill={C.white}>ABOVE THE SUMMIT OF EVEREST</text>
          </g>
        ) : null}
        {marks.map((m, i) => (
          <g key={i} opacity={pop(f, 3 + i * 3, 8)}>
            <line x1={640} y1={yOf(m.d)} x2={1280} y2={yOf(m.d)} stroke={C.accent} strokeWidth={3} strokeDasharray="10 8" />
            <text x={1300} y={yOf(m.d) + 10} fontFamily={FONT} fontWeight={800} fontSize={30} fill={C.accent}>{m.text}</text>
          </g>
        ))}
        <g transform={`translate(960 ${yOf(d)})`}>
          <circle r={18} fill={C.accent} />
          <circle r={18 + (f % 30)} fill="none" stroke={C.accent} strokeWidth={3} opacity={1 - (f % 30) / 30} />
        </g>
      </Svg>
    </AbsoluteFill>
  );
};
registerKind("graphic", Column);

// A close diagram of one animal on black with labelled parts.
export const Diagram: React.FC<{ c: Actor["c"]; s?: number; x?: number; y?: number; flip?: boolean; glow?: number; notes?: { x: number; y: number; tx: number; ty: number; text: string }[]; title?: string; bg?: string; children?: React.ReactNode }> = ({ c, s = 1.4, x = 960, y = 520, flip, glow, notes = [], title, bg = "#03141c", children }) => {
  const { f, k } = useShot();
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 50%, ${bg} 0%, #000 100%)` }}>
      <Svg>
        <Defs />
        <Act a={{ c, x0: x, y0: y, s0: s * 0.96, s1: s, flip, glow }} e={ease(k)} f={f} />
        {notes.map((n, i) => {
          const p = pop(f, 4 + i * 5, 8);
          return (
            <g key={i} opacity={p}>
              <circle cx={n.x} cy={n.y} r={14} fill="none" stroke={C.accent} strokeWidth={5} />
              <line x1={n.x} y1={n.y} x2={lerp(n.x, n.tx, p)} y2={lerp(n.y, n.ty, p)} stroke={C.accent} strokeWidth={4} />
              <text x={n.tx + (n.tx > n.x ? 14 : -14)} y={n.ty + 12} textAnchor={n.tx > n.x ? "start" : "end"} fontFamily={FONT} fontWeight={800} fontSize={38} fill={C.white} style={{ textShadow: SHADOW }}>{n.text}</text>
            </g>
          );
        })}
      </Svg>
      {children}
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{title}</div> : null}
    </AbsoluteFill>
  );
};
registerKind("graphic", Diagram);

// Seen from below against the faint light above: the glowing belly hides the shark; the dark collar looks like a small fish.
export const FromBelow: React.FC = () => {
  const { f } = useShot();
  const t = pop(f, 10, 14);
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#0c3a4e, #021017)" }}>
      <Svg>
        <Defs />
        <g transform="translate(960 420) scale(2.2)" opacity={1 - t * 0.85}>
          <Cookie glow={1} f={f} />
        </g>
        <g transform="translate(960 420) scale(2.2)">
          <path d="M 70 4 L 100 4 L 104 30 L 72 32 Z" fill="#081016" />
        </g>
        <g opacity={t}>
          <circle cx={1150} cy={460} r={70} fill="none" stroke={C.accent} strokeWidth={5} />
          <text x={1240} y={470} fontFamily={FONT} fontWeight={800} fontSize={42} fill={C.white}>LOOKS LIKE A SMALL FISH</text>
        </g>
      </Svg>
    </AbsoluteFill>
  );
};
registerKind("graphic", FromBelow);

// Size compare: two things side by side with labels.
export const SizeCompare: React.FC<{ a: React.ReactNode; b: React.ReactNode; la: string; lb: string; title?: string }> = ({ a, b, la, lb, title }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, #0a2430 0%, #000 100%)" }}>
      <Svg>
        <Defs />
        <g opacity={pop(f, 0, 8)} transform="translate(620 470)">{a}</g>
        <g opacity={pop(f, 6, 8)} transform="translate(1300 470)">{b}</g>
        <text x={620} y={760} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={40} fill={C.accent} opacity={pop(f, 3, 8)}>{la}</text>
        <text x={1300} y={760} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={40} fill={C.white} opacity={pop(f, 9, 8)}>{lb}</text>
      </Svg>
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 60, color: C.white, textShadow: SHADOW }}>{title}</div> : null}
    </AbsoluteFill>
  );
};
registerKind("graphic", SizeCompare);

// Weight on a fingertip: a small car balanced on one finger.
export const Fingertip: React.FC = () => {
  const { f } = useShot();
  const y = interpolate(f, [0, 12], [-300, 0], clamp);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 60%, #0a1c24 0%, #000 100%)" }}>
      <Svg>
        <path d="M 900 1080 L 900 640 C 900 600 1020 600 1020 640 L 1020 1080 Z" fill="#c89a7c" />
        <path d="M 920 640 C 920 615 1000 615 1000 640 L 1000 660 L 920 660 Z" fill="#e4c3ad" />
        <g transform={`translate(960 ${600 + y})`}>
          <path d="M -170 0 L -150 -60 L -80 -110 L 80 -110 L 140 -60 L 180 -50 L 190 0 Z" fill={C.red} />
          <rect x={-60} y={-100} width={110} height={40} rx={8} fill="#bfe3ef" />
          <circle cx={-100} cy={0} r={30} fill="#222" />
          <circle cx={110} cy={0} r={30} fill="#222" />
        </g>
        <text x={960} y={200} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={58} fill={C.white} opacity={pop(f, 10, 8)}>≈ 1 TONNE ON EVERY SQUARE CENTIMETRE</text>
      </Svg>
    </AbsoluteFill>
  );
};
registerKind("graphic", Fingertip);

// A fish body filling with a pressure-protecting molecule; past the limit, water floods in.
export const Tmao: React.FC<{ over?: boolean }> = ({ over = false }) => {
  const { f, k } = useShot();
  const n = Math.round(lerp(10, over ? 90 : 60, ease(k)));
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, #170a0f 0%, #000 100%)" }}>
      <Svg>
        <g transform="translate(980 500) scale(2.4)">
          <Snailfish f={f} />
          {Array.from({ length: n }, (_, i) => <circle key={i} cx={-300 + random(`tm${i}`) * 400} cy={-40 + random(`tn${i}`) * 80} r={4} fill={C.cyan} opacity={0.9} />)}
          {over ? Array.from({ length: 8 }, (_, i) => <path key={i} d={`M ${-280 + i * 50} ${-140 + ((f * 4 + i * 20) % 80)} l 0 30`} stroke="#7fd4ff" strokeWidth={4} opacity={0.8} />) : null}
        </g>
        <text x={960} y={180} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={60} fill={C.white}>{over ? "PAST ≈ 8,200–8,400 M: WATER FLOODS IN" : "TMAO PROTECTS THE BODY FROM PRESSURE"}</text>
      </Svg>
    </AbsoluteFill>
  );
};
registerKind("graphic", Tmao);

// A big caption card with a stencil feel: a year, a depth or a name on black.
export const Card: React.FC<{ big: string; sub?: string; color?: string }> = ({ big, sub, color = C.white }) => {
  const { f, k } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0b2430 0%, #000 90%)", alignItems: "center", justifyContent: "center" }}>
      <div style={{ transform: `scale(${1 + k * 0.05})`, textAlign: "center", opacity: pop(f, 0, 6) }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 190, color, textShadow: SHADOW, lineHeight: 1 }}>{big}</div>
        {sub ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 32, color: "rgba(255,255,255,0.8)", letterSpacing: 6, marginTop: 20 }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
registerKind("graphic", Card);
