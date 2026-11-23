// Drawn shots for the humpback whale video. Flat 2D, our own characters, deep-teal palette.
// Every shot fills the frame, moves for its whole length and is placed by the shot engine.
import React from "react";
import { AbsoluteFill, interpolate, random } from "remotion";
import { registerKind } from "../kit/edit-rules";
import { HUD, MONO } from "../kit/hud";
import { Backdrop, ease, Kicker, Label, pop, Svg, useShot } from "../kit/shots";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { useLang, useT } from "./lang";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";
const BODY = "#22313d";
const BELLY = "#c8d2d8";
const FIN = "#dde5ea";

// ---------- Characters ----------

export type WhaleP = { x: number; y: number; s?: number; flip?: boolean; rot?: number; jaw?: number; bulge?: number; f?: number; opacity?: number; color?: string; pleats?: boolean };

// Humpback, side view, facing right. jaw 0..1 opens the lower jaw; bulge 0..1 balloons the pleated throat.
export const Whale: React.FC<WhaleP> = ({ x, y, s = 1, flip = false, rot = 0, jaw = 0, bulge = 0, f = 0, opacity = 1, color = BODY, pleats = true }) => {
  const flap = Math.sin(f * 0.12) * 6;
  const beat = Math.sin(f * 0.15) * 10;
  const b = bulge;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`} opacity={opacity}>
      {/* tail */}
      <g transform={`rotate(${beat} -440 0)`}>
        <path d="M -430 -14 C -470 -20 -500 -30 -520 -40 C -560 -90 -600 -120 -660 -128 C -620 -70 -610 -30 -585 -4 C -610 22 -620 62 -660 120 C -600 112 -560 84 -520 40 C -500 30 -470 20 -430 14 Z" fill={color} />
      </g>
      {/* body and upper jaw */}
      <path
        d="M 480 -8 C 440 -42 330 -78 170 -94 C 60 -102 -60 -100 -120 -96 L -150 -128 C -170 -132 -185 -122 -190 -100 C -280 -82 -380 -44 -440 -16 L -440 16 C -360 48 -220 92 -60 108 L 60 106 L 230 14 Z"
        fill={color}
      />
      {[0, 1, 2, 3, 4, 5, 6].map((i) => <circle key={i} cx={270 + i * 30} cy={-46 + i * 5} r={7} fill="#34475a" />)}
      <circle cx={205} cy={22} r={7} fill="#0a0f14" />
      {/* lower jaw and pleated throat, hinged behind the eye */}
      <g transform={`rotate(${jaw * 38} 220 12)`}>
        <path d={`M 222 12 L 476 6 C 450 40 ${400} ${62 + b * 60} ${320} ${84 + b * 120} C 230 ${110 + b * 150} 120 ${118 + b * 120} 40 108 L 60 100 Z`} fill={BELLY} />
        {pleats
          ? [0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
              <path key={i} d={`M ${70 + i * 6} ${104 + i * 1} Q ${250} ${70 + i * 8 + b * (40 + i * 12)} ${440 - i * 18} ${18 + i * 5}`} stroke="#8e9ca5" strokeWidth={3} fill="none" />
            ))
          : null}
      </g>
      {/* long white flipper */}
      <g transform={`rotate(${flap} 150 60)`}>
        <path d="M 170 58 C 120 150 20 240 -190 290 C -170 270 -150 256 -130 246 C -40 196 40 140 110 48 Z" fill={FIN} />
        {[0, 1, 2, 3, 4].map((i) => <circle key={i} cx={130 - i * 70} cy={110 + i * 40} r={9} fill={FIN} />)}
      </g>
    </g>
  );
};

// Humpback seen from above (bubble nets, rescues). Mouth opens as a widening V.
export const WhaleTop: React.FC<{ x: number; y: number; s?: number; rot?: number; open?: number; f?: number; belly?: boolean }> = ({ x, y, s = 1, rot = 0, open = 0, f = 0, belly = false }) => {
  const w = Math.sin(f * 0.15) * 8;
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
      <path d={`M -360 0 C -420 ${-60 + w} -470 ${-90 + w} -500 ${-110 + w} L -470 0 L -500 ${110 + w} C -470 ${90 + w} -420 ${60 + w} -360 0 Z`} fill={BODY} />
      <path d="M 300 0 C 280 -70 120 -105 -40 -95 C -200 -80 -320 -40 -380 0 C -320 40 -200 80 -40 95 C 120 105 280 70 300 0 Z" fill={belly ? BELLY : BODY} />
      <path d={`M 60 -90 C 0 -200 -100 -290 -230 ${-330 + w}`} stroke={FIN} strokeWidth={40} strokeLinecap="round" fill="none" />
      <path d={`M 60 90 C 0 200 -100 290 -230 ${330 - w}`} stroke={FIN} strokeWidth={40} strokeLinecap="round" fill="none" />
      {open > 0 ? <path d={`M 300 0 L ${420 + open * 60} ${-open * 120} L ${420 + open * 60} ${open * 120} Z`} fill="#5a2730" /> : null}
    </g>
  );
};

export const Kayak: React.FC<{ x: number; y: number; s?: number; tilt?: number; f?: number; color?: string; person?: boolean; phone?: boolean; paddle?: boolean }> = ({ x, y, s = 1, tilt = 0, f = 0, color = "#ffcc1a", person = true, phone = false, paddle = true }) => {
  const p = Math.sin(f * 0.2) * 25;
  return (
    <g transform={`translate(${x} ${y}) rotate(${tilt}) scale(${s})`}>
      {person ? (
        <g>
          <rect x={-22} y={-110} width={44} height={86} rx={18} fill="#e0572b" />
          <circle cx={0} cy={-132} r={24} fill="#e9c3a0" />
          <path d="M -24 -142 Q 0 -168 24 -142 Z" fill="#2b2b2b" />
          {paddle ? (
            <g transform={`rotate(${p} 0 -80)`}>
              <line x1={-150} y1={-80} x2={150} y2={-80} stroke="#333" strokeWidth={8} />
              <ellipse cx={-160} cy={-80} rx={26} ry={12} fill="#333" />
              <ellipse cx={160} cy={-80} rx={26} ry={12} fill="#333" />
            </g>
          ) : null}
          {phone ? <rect x={26} y={-120} width={22} height={36} rx={4} fill="#111" stroke="#7fe9ff" strokeWidth={3} /> : null}
        </g>
      ) : null}
      <path d="M -230 -20 Q 0 -40 230 -20 Q 180 20 0 22 Q -180 20 -230 -20 Z" fill={color} stroke="#7a5a00" strokeWidth={4} />
    </g>
  );
};

export const Diver: React.FC<{ x: number; y: number; s?: number; rot?: number; f?: number; torch?: boolean; bag?: boolean }> = ({ x, y, s = 1, rot = 0, f = 0, torch = false, bag = false }) => {
  const kick = Math.sin(f * 0.25) * 14;
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
      <rect x={-120} y={-70} width={120} height={34} rx={16} fill="#8a96a0" />
      <rect x={-150} y={-40} width={190} height={56} rx={28} fill="#3d5566" stroke="#cfe6ee" strokeWidth={4} />
      <circle cx={70} cy={-14} r={34} fill="#3d5566" stroke="#cfe6ee" strokeWidth={4} />
      <rect x={70} y={-30} width={36} height={22} rx={8} fill="#7fe9ff" opacity={0.8} />
      <g transform={`rotate(${kick} -150 -10)`}>
        <rect x={-300} y={-28} width={160} height={24} rx={12} fill="#3d5566" stroke="#cfe6ee" strokeWidth={3} />
        <path d="M -300 -40 L -380 -70 L -380 30 L -300 0 Z" fill="#e8b300" />
      </g>
      <g transform={`rotate(${-kick} -150 10)`}>
        <rect x={-300} y={4} width={160} height={24} rx={12} fill="#3d5566" stroke="#cfe6ee" strokeWidth={3} />
      </g>
      {bag ? <rect x={10} y={20} width={60} height={70} rx={10} fill="#4a6b3a" /> : null}
      {torch ? <path d="M 110 -14 L 700 -200 L 700 180 Z" fill="rgba(255,240,200,0.12)" /> : null}
      {Array.from({ length: 5 }, (_, i) => {
        const t = ((f / 30 + i / 5) % 1 + 1) % 1;
        return <circle key={i} cx={90 + Math.sin(i + f * 0.1) * 10} cy={-60 - t * 260} r={6 + i * 2} fill="none" stroke="#bfefff" strokeWidth={3} opacity={1 - t} />;
      })}
    </g>
  );
};

export const Seal: React.FC<{ x: number; y: number; s?: number; rot?: number; f?: number }> = ({ x, y, s = 1, rot = 0, f = 0 }) => (
  <g transform={`translate(${x} ${y}) rotate(${rot + Math.sin(f * 0.1) * 2}) scale(${s})`}>
    <path d="M -150 10 C -140 -40 -40 -60 60 -50 C 120 -46 150 -20 150 6 C 150 30 100 40 40 40 C -40 44 -120 40 -150 10 Z" fill="#6d7a80" />
    <circle cx={140} cy={-14} r={34} fill="#6d7a80" />
    <circle cx={152} cy={-22} r={5} fill="#111" />
    <path d="M -150 10 L -200 -14 L -196 34 Z" fill="#5a666b" />
    {[0, 1, 2, 3, 4, 5].map((i) => <circle key={i} cx={-90 + i * 40} cy={-20 + (i % 2) * 18} r={6} fill="#4f5a5f" />)}
  </g>
);

export const Orca: React.FC<{ x: number; y: number; s?: number; flip?: boolean; f?: number; rot?: number }> = ({ x, y, s = 1, flip = false, f = 0, rot = 0 }) => (
  <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot + Math.sin(f * 0.15) * 3})`}>
    <path d="M 220 0 C 200 -50 100 -70 -40 -64 C -150 -58 -230 -30 -280 -6 L -340 -50 L -320 0 L -340 50 L -280 6 C -230 30 -120 56 0 56 C 120 56 210 40 220 0 Z" fill="#0b0e12" />
    <path d="M -10 -62 L -40 -200 L -90 -60 Z" fill="#0b0e12" />
    <ellipse cx={130} cy={-24} rx={34} ry={14} fill="#f2f5f7" />
    <path d="M 120 30 C 40 50 -60 46 -120 30 C -60 20 40 16 120 30 Z" fill="#f2f5f7" />
  </g>
);

export const Fish: React.FC<{ cx: number; cy: number; n?: number; r?: number; f?: number; color?: string; tight?: number; seed?: string; scatter?: number }> = ({ cx, cy, n = 60, r = 220, f = 0, color = "#cfe9ef", tight = 1, seed = "fs", scatter = 0 }) => (
  <g>
    {Array.from({ length: n }, (_, i) => {
      const a = random(`${seed}a${i}`) * Math.PI * 2 + f * 0.03 * (i % 2 ? 1 : -1);
      const d = Math.sqrt(random(`${seed}d${i}`)) * r * tight * (1 + scatter * random(`${seed}s${i}`) * 2);
      const px = cx + Math.cos(a) * d * 1.6;
      const py = cy + Math.sin(a) * d * 0.7;
      const dir = Math.cos(a + Math.PI / 2) > 0 ? 1 : -1;
      return <path key={i} d={`M ${px} ${py} l ${-22 * dir} -8 l 0 16 Z M ${px} ${py} l ${14 * dir} 0`} fill={color} stroke={color} strokeWidth={6} strokeLinecap="round" opacity={0.85} />;
    })}
  </g>
);

export const Krill: React.FC<{ cx: number; cy: number; n?: number; r?: number; f?: number }> = ({ cx, cy, n = 140, r = 260, f = 0 }) => (
  <g>
    {Array.from({ length: n }, (_, i) => {
      const a = random(`ka${i}`) * Math.PI * 2 + f * 0.01;
      const d = Math.sqrt(random(`kd${i}`)) * r;
      return <ellipse key={i} cx={cx + Math.cos(a) * d * 1.5 + Math.sin(f * 0.2 + i) * 4} cy={cy + Math.sin(a) * d * 0.8} rx={6} ry={3} fill="#ff8fa0" opacity={0.8} />;
    })}
  </g>
);

const Bird: React.FC<{ x: number; y: number; s?: number; dive?: boolean; f?: number }> = ({ x, y, s = 1, dive = false, f = 0 }) =>
  dive ? (
    // A gannet folding into a dive: body pointing down, wings swept back.
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M 0 30 L -7 -10 L 0 -24 L 7 -10 Z" fill="#f2f5f7" />
      <path d="M -6 -8 L -30 -38 M 6 -8 L 30 -38" stroke="#f2f5f7" strokeWidth={6} strokeLinecap="round" />
      <path d="M 0 30 L 0 40" stroke="#e8a33a" strokeWidth={4} />
    </g>
  ) : (
    <path d={`M ${x - 30 * s} ${y} Q ${x - 15 * s} ${y - (14 + Math.sin(f * 0.4) * 10) * s} ${x} ${y} Q ${x + 15 * s} ${y - (14 + Math.sin(f * 0.4) * 10) * s} ${x + 30 * s} ${y}`} stroke="#e9eef0" strokeWidth={5} fill="none" />
  );

const Mountains: React.FC<{ y?: number; color?: string; snow?: boolean }> = ({ y = 470, color = "#55677a", snow = true }) => (
  <g>
    <path d={`M -100 ${y} ${Array.from({ length: 22 }, (_, i) => `L ${-100 + i * 105} ${y - 60 - random(`mt${i}`) * 170}`).join(" ")} L 2100 ${y} Z`} fill={color} />
    {snow ? Array.from({ length: 22 }, (_, i) => {
      const px = -100 + i * 105;
      const py = y - 60 - random(`mt${i}`) * 170;
      return py < y - 150 ? <path key={i} d={`M ${px - 22} ${py + 26} L ${px} ${py} L ${px + 22} ${py + 26} Z`} fill="#e8eef2" /> : null;
    }) : null}
    <path d={`M -100 ${y} ${Array.from({ length: 30 }, (_, i) => `L ${-100 + i * 75} ${y - 20 - random(`mh${i}`) * 60}`).join(" ")} L 2100 ${y} Z`} fill="#3a4a58" />
  </g>
);

// ---------- Scenes ----------

type Sky = "grey" | "day" | "dusk" | "polar";
const SKY: Record<Sky, string> = {
  grey: "linear-gradient(#7f8c97 0%, #a9b4bc 70%, #c4cbd0 100%)",
  day: "linear-gradient(#4f8fb8 0%, #9cc8df 75%, #cfe4ee 100%)",
  dusk: "linear-gradient(#2b2a4c 0%, #7a4a5e 50%, #e08a50 100%)",
  polar: "linear-gradient(#9fb6c8 0%, #d8e3ea 80%, #eef3f6 100%)",
};

// At the surface: the water line across the middle, the viewer's eye just above it.
export const SurfaceShot: React.FC<{
  sky?: Sky;
  kayak?: { x0: number; x1?: number; tilt?: number; s?: number };
  father?: boolean;
  dark?: number;
  engulf?: "open" | "close" | "release";
  birds?: boolean | "dive";
  ring?: boolean;
  boil?: boolean;
  swirl?: boolean;
  fluke?: boolean;
  head?: string;
  boat?: boolean;
  buoy?: boolean;
  surfacer?: number;
  whaleFar?: boolean;
  z0?: number;
  z1?: number;
  zx?: number;
  zy?: number;
  children?: React.ReactNode;
}> = ({ sky = "grey", kayak, father = false, dark = 0, engulf, birds = false, ring = false, boil = false, swirl = false, fluke = false, boat = false, buoy = false, surfacer, whaleFar = false, z0 = 1, z1 = 1.08, zx = 960, zy = 560, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const zoom = z0 + (z1 - z0) * e;
  const WL = 560;
  const kx = kayak ? lerp(kayak.x0, kayak.x1 ?? kayak.x0, e) : 0;
  // The mouth rising round the kayak: two jaws come up, then close.
  const up = engulf === "open" ? ease(k * 1.3) : engulf === "close" ? 1 : engulf === "release" ? 1 - ease(k * 1.5) : 0;
  const shut = engulf === "close" ? ease(k * 1.6) : engulf === "release" ? 1 - ease(k * 1.2) : 0;
  const kayakGone = engulf === "close" && shut > 0.6;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - zx * zoom}px, ${540 - zy * zoom}px) scale(${zoom})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -400, top: -400, width: 2720, height: WL + 400, background: SKY[sky] }} />
        <Svg>
          {sky !== "day" ? <Mountains y={WL} color={sky === "polar" ? "#c9d6df" : "#56687a"} /> : null}
          <rect x={-400} y={WL} width={2720} height={1000} fill={sky === "dusk" ? "#2b3346" : "#3c5566"} />
          {Array.from({ length: 46 }, (_, i) => {
            const y = WL + 8 + Math.pow(random(`sw${i}`), 1.6) * 560;
            const d = (y - WL) / 560;
            return <rect key={i} x={((random(`sx${i}`) * 2700 + f * (0.5 + d * 2)) % 2900) - 400} y={y} width={60 + d * 280} height={3 + d * 6} rx={3} fill="#b8cad4" opacity={0.12 + random(`so${i}`) * 0.16} />;
          })}
          {dark > 0 ? <ellipse cx={kx || 1000} cy={WL + 120} rx={420} ry={90} fill="#0c1820" opacity={dark * (0.5 + 0.4 * e)} /> : null}
          {swirl
            ? [0, 1, 2, 3].map((i) => {
                const t = ((f / 36 + i / 4) % 1 + 1) % 1;
                return <ellipse key={i} cx={kx || 1000} cy={WL + 40} rx={60 + t * 360} ry={12 + t * 60} fill="none" stroke="#e1ecf1" strokeWidth={4} opacity={0.7 * (1 - t)} />;
              })
            : null}
          {ring
            ? Array.from({ length: 70 }, (_, i) => {
                const a = (i / 70) * Math.PI * 2;
                const g = Math.min(1, f / 30);
                return i / 70 < g ? <circle key={i} cx={1000 + Math.cos(a) * 420} cy={WL + 90 + Math.sin(a) * 70} r={6 + random(`rb${i}`) * 8} fill="#eef6f8" opacity={0.8} /> : null;
              })
            : null}
          {boil
            ? Array.from({ length: 16 }, (_, i) => {
                const t = ((f / 18 + random(`bj${i}`)) % 1 + 1) % 1;
                return <path key={i} d={`M ${800 + random(`bx${i}`) * 400} ${WL + 30 - Math.sin(t * Math.PI) * 90} l -18 -6 l 0 12 Z`} fill="#dfeff3" opacity={0.9} />;
              })
            : null}
          {whaleFar ? <path d={`M 1300 ${WL + 4} Q 1420 ${WL - 40 - Math.sin(f * 0.05) * 6} 1560 ${WL + 4} Z`} fill={BODY} /> : null}
          {boat ? (
            <g transform={`translate(400 ${WL + 10 + Math.sin(f * 0.1) * 4})`}>
              <path d="M -200 -60 L 220 -60 L 180 10 L -170 10 Z" fill="#e9edf0" stroke="#2b3a46" strokeWidth={5} />
              <rect x={-60} y={-140} width={120} height={80} fill="#c9d0d6" stroke="#2b3a46" strokeWidth={5} />
            </g>
          ) : null}
          {buoy ? (
            <g transform={`translate(1200 ${WL + Math.sin(f * 0.15) * 6})`}>
              <rect x={-30} y={-40} width={60} height={60} rx={10} fill="#ff6a00" />
              <line x1={0} y1={-40} x2={0} y2={-160} stroke="#222" strokeWidth={6} />
              <path d="M 0 -160 L 100 -140 L 0 -110 Z" fill="#e02020" />
              <line x1={0} y1={-158} x2={80} y2={-122} stroke="#fff" strokeWidth={8} />
            </g>
          ) : null}
          {engulf ? (
            <g transform={`translate(${kx} ${WL + 30 - up * 160})`}>
              <path d={`M -330 140 C -300 -60 -150 ${-210 + shut * 120} 40 ${-230 + shut * 140} C 120 ${-230 + shut * 140} 180 -150 200 140 Z`} fill={BODY} />
              {[0, 1, 2, 3, 4, 5].map((i) => <circle key={i} cx={-180 + i * 60} cy={-120 + shut * 90 + Math.abs(i - 2.5) * 18} r={9} fill="#34475a" />)}
              <path d={`M 320 160 C 300 ${20 + shut * 40} 200 ${-20 + shut * 30} 60 ${-30 + shut * 60} C -40 ${-30 + shut * 60} -60 60 -60 160 Z`} fill={BELLY} opacity={0.95} />
            </g>
          ) : null}
          {kayak && !kayakGone ? <Kayak x={kx} y={WL + 6 + Math.sin(f * 0.12) * 4 - (engulf ? up * 40 : 0)} s={kayak.s ?? 1} tilt={(kayak.tilt ?? 0) + (engulf ? up * 25 : Math.sin(f * 0.1) * 2)} f={f} /> : null}
          {engulf && up > 0.4
            ? Array.from({ length: 30 }, (_, i) => {
                const t = Math.min(1, k * 1.5);
                return <circle key={i} cx={kx + (random(`sp${i}`) - 0.5) * 700 * t} cy={WL - random(`sq${i}`) * 300 * Math.sin(t * Math.PI)} r={6 + random(`sr${i}`) * 10} fill="#e6f2f6" opacity={0.85 * (1 - t * 0.6)} />;
              })
            : null}
          {father ? <Kayak x={220} y={WL + 60} s={1.25} f={f + 20} color="#ff8a1a" phone /> : null}
          {surfacer !== undefined ? (
            <g transform={`translate(${surfacer} ${WL + 20 - ease(k * 2) * 30})`}>
              <circle cx={0} cy={-30} r={30} fill="#e9c3a0" />
              <path d="M -30 -38 Q 0 -70 30 -38 Z" fill="#2b2b2b" />
              <rect x={-36} y={-4} width={72} height={60} rx={18} fill="#e0572b" />
              {[0, 1, 2].map((i) => {
                const t = ((f / 24 + i / 3) % 1 + 1) % 1;
                return <ellipse key={i} cx={0} cy={20} rx={50 + t * 200} ry={10 + t * 30} fill="none" stroke="#e1ecf1" strokeWidth={3} opacity={1 - t} />;
              })}
            </g>
          ) : null}
          {fluke ? (
            <g transform={`translate(1000 ${WL + 40 - Math.sin(Math.min(1, k * 1.2) * Math.PI) * 300})`}>
              <path d="M 0 60 C -10 0 -60 -40 -230 -70 C -150 -10 -60 10 -20 40 Z M 0 60 C 10 0 60 -40 230 -70 C 150 -10 60 10 20 40 Z" fill={BODY} />
              <path d="M -14 60 L 14 60 L 10 200 L -10 200 Z" fill={BODY} />
              {Array.from({ length: 10 }, (_, i) => <circle key={i} cx={-200 + i * 44} cy={-60 + Math.abs(i - 4.5) * -2 + 10} r={4} fill="#d8e3ea" opacity={0.8} />)}
            </g>
          ) : null}
          {birds
            ? Array.from({ length: 9 }, (_, i) => {
                const dv = birds === "dive" && i % 2 === 0;
                const t = ((f / 40 + random(`bd${i}`)) % 1 + 1) % 1;
                return <Bird key={i} x={700 + random(`bb${i}`) * 600 + (dv ? 0 : f * 2)} y={dv ? 200 + t * (WL - 200) : 150 + random(`bc${i}`) * 220} s={1.2} dive={dv} f={f + i * 7} />;
              })
            : null}
        </Svg>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Under the water, side on. Light from above, the surface line at the top.
export const UnderShot: React.FC<{
  whale?: Omit<WhaleP, "x" | "y" | "f"> & { x0: number; x1?: number; y0: number; y1?: number; jaw0?: number; jaw1?: number; b0?: number; b1?: number };
  fish?: { x: number; y: number; n?: number; r?: number; tight0?: number; tight1?: number; scatter?: boolean };
  krill?: { x: number; y: number };
  diver?: { x0: number; x1?: number; y: number; s?: number; bag?: boolean };
  hull?: number;
  deep?: number;
  rays?: boolean;
  shock?: { x: number; y: number };
  calf?: boolean;
  z0?: number;
  z1?: number;
  zx?: number;
  zy?: number;
  children?: React.ReactNode;
}> = ({ whale, fish, krill, diver, hull, deep = 0, rays = true, shock, calf = false, z0 = 1, z1 = 1.07, zx = 960, zy = 540, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const zoom = z0 + (z1 - z0) * e;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - zx * zoom}px, ${540 - zy * zoom}px) scale(${zoom})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -400, top: -400, width: 2720, height: 1900, background: `linear-gradient(#2f7f9a 0%, #135066 ${30 - deep * 20}%, #06222e ${70 - deep * 30}%, #01080c 100%)` }} />
        <Svg>
          <rect x={-400} y={-400} width={2720} height={440} fill="#5fa9c2" opacity={0.35} />
          {rays
            ? Array.from({ length: 7 }, (_, i) => (
                <path key={i} d={`M ${200 + i * 260 + Math.sin(f * 0.03 + i) * 40} 30 L ${120 + i * 260} 1100 L ${260 + i * 260} 1100 Z`} fill="#cdeef7" opacity={0.05 + 0.03 * Math.sin(f * 0.05 + i)} />
              ))
            : null}
          {Array.from({ length: 40 }, (_, i) => (
            <circle key={i} cx={(random(`ux${i}`) * 2200 + f * 0.6) % 2200 - 140} cy={(random(`uy${i}`) * 1100 - f * (0.3 + random(`uv${i}`)) + 1100) % 1100} r={2 + random(`ur${i}`) * 4} fill="#e8f4f6" opacity={0.15} />
          ))}
          {hull !== undefined ? <path d={`M ${hull - 230} 40 Q ${hull} 80 ${hull + 230} 40 Z`} fill="#3a2e10" opacity={0.85} /> : null}
          {krill ? <Krill cx={krill.x} cy={krill.y} f={f} /> : null}
          {fish ? <Fish cx={fish.x} cy={fish.y} n={fish.n ?? 70} r={fish.r ?? 200} f={f} tight={lerp(fish.tight0 ?? 1, fish.tight1 ?? fish.tight0 ?? 1, e)} scatter={fish.scatter ? e : 0} /> : null}
          {diver ? <Diver x={lerp(diver.x0, diver.x1 ?? diver.x0, e)} y={diver.y} s={diver.s ?? 1} f={f} bag={diver.bag} /> : null}
          {whale ? (
            <Whale
              {...whale}
              x={lerp(whale.x0, whale.x1 ?? whale.x0, e)}
              y={lerp(whale.y0, whale.y1 ?? whale.y0, e) + Math.sin(f * 0.05) * 6}
              jaw={lerp(whale.jaw0 ?? whale.jaw ?? 0, whale.jaw1 ?? whale.jaw0 ?? whale.jaw ?? 0, e)}
              bulge={lerp(whale.b0 ?? whale.bulge ?? 0, whale.b1 ?? whale.b0 ?? whale.bulge ?? 0, e)}
              f={f}
            />
          ) : null}
          {calf && whale ? <Whale x={lerp(whale.x0, whale.x1 ?? whale.x0, e) + 120} y={lerp(whale.y0, whale.y1 ?? whale.y0, e) + 230} s={(whale.s ?? 1) * 0.38} f={f + 10} flip={whale.flip} /> : null}
          {shock
            ? [0, 1, 2].map((i) => {
                const t = Math.min(1, (f / 14 + i * 0.25) % 1.2);
                return <circle key={i} cx={shock.x} cy={shock.y} r={40 + t * 420} fill="none" stroke="#fff" strokeWidth={10 * (1 - t)} opacity={1 - t} />;
              })
            : null}
        </Svg>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Inside the closed mouth: dark, soft walls, the baleen fringe, a torch beam. light 0..1 floods in as it opens.
export const MouthPOV: React.FC<{ light?: "none" | "in" | "flood"; squeeze?: boolean; torch?: boolean; text?: string }> = ({ light = "none", squeeze = false, torch = true, text }) => {
  const { f, k } = useShot();
  const sq = squeeze ? Math.sin(f * 0.25) * 30 : 0;
  const L = light === "in" ? ease(k) * 0.6 : light === "flood" ? 0.6 + ease(k) * 0.4 : 0;
  const shake = Math.sin(f * 0.9) * 6;
  return (
    <AbsoluteFill style={{ background: "#0a0204", transform: `translate(${shake}px, ${-shake * 0.6}px)` }}>
      <Svg>
        <path d={`M -100 ${-20 + sq} Q 960 ${260 + sq} 2020 ${-20 + sq} L 2020 -100 L -100 -100 Z`} fill="#3b1218" />
        <path d={`M -100 ${1100 - sq} Q 960 ${760 - sq} 2020 ${1100 - sq} L 2020 1200 L -100 1200 Z`} fill="#4a1820" />
        {Array.from({ length: 48 }, (_, i) => (
          <line key={i} x1={-60 + i * 44} y1={40 + Math.sin(i * 0.4) * 40 + sq} x2={-60 + i * 44 + Math.sin(f * 0.1 + i) * 8} y2={210 + Math.sin(i * 0.4) * 40 + sq} stroke="#2a1a10" strokeWidth={10} opacity={0.85} />
        ))}
        {torch ? <path d={`M 960 1080 L ${700 + Math.sin(f * 0.07) * 120} 360 L ${1240 + Math.sin(f * 0.07) * 120} 360 Z`} fill="rgba(255,236,200,0.16)" /> : null}
        {Array.from({ length: 14 }, (_, i) => {
          const t = ((f / 30 + i / 14) % 1 + 1) % 1;
          return <circle key={i} cx={900 + Math.sin(i * 2.1) * 160} cy={760 - t * 500} r={5 + (i % 4) * 3} fill="none" stroke="#e6b8b8" strokeWidth={3} opacity={(1 - t) * 0.6} />;
        })}
      </Svg>
      {L > 0 ? <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 50%, rgba(220,240,250,${L}) 0%, rgba(120,190,210,${L * 0.7}) ${20 + L * 50}%, transparent ${40 + L * 60}%)` }} /> : null}
      {text ? <Kicker text={text} y={430} align="center" x={0} width={1920} size={80} /> : null}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.85) 100%)" }} />
    </AbsoluteFill>
  );
};

// A cutaway of the head, drawn like a field guide on a blueprint.
export const CutawayShot: React.FC<{
  mode: "baleen" | "gulp" | "filter" | "throat" | "fist" | "stretch" | "person" | "plates" | "hairs" | "teeth" | "birds";
  title?: string;
  note?: string;
}> = ({ mode, title, note }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const jaw = mode === "gulp" ? e : mode === "baleen" || mode === "filter" || mode === "plates" ? 0.55 : 0.2;
  const bulge = mode === "gulp" ? e : mode === "filter" ? 1 - e : 0;
  const tube = mode === "throat" || mode === "fist" || mode === "stretch" || mode === "person" || mode === "birds";
  const tw = mode === "stretch" ? lerp(20, 44, e) : 20;
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 40%, #0f3a4a 0%, #04161e 75%)" specks={false}>
      <Svg>
        {Array.from({ length: 25 }, (_, i) => <line key={i} x1={i * 80} y1={0} x2={i * 80} y2={1080} stroke="rgba(127,233,255,0.06)" strokeWidth={2} />)}
        {Array.from({ length: 14 }, (_, i) => <line key={i} x1={0} y1={i * 80} x2={1920} y2={i * 80} stroke="rgba(127,233,255,0.06)" strokeWidth={2} />)}
        <g opacity={tube ? 0.55 : 1}>
          <Whale x={900} y={500} s={1.45} jaw={jaw} bulge={bulge} f={f} />
        </g>
        {mode === "gulp" ? <Krill cx={1650 - e * 500} cy={560} f={f} r={180} /> : null}
        {mode === "filter"
          ? Array.from({ length: 12 }, (_, i) => {
              const t = ((f / 20 + i / 12) % 1 + 1) % 1;
              return <path key={i} d={`M ${1250 + t * 260} ${520 + i * 14} l 36 0 l -12 -8 m 12 8 l -12 8`} stroke="#7fe9ff" strokeWidth={5} fill="none" opacity={1 - t} />;
            })
          : null}
        {mode === "baleen" || mode === "plates" || mode === "filter"
          ? Array.from({ length: 26 }, (_, i) => {
              const g = mode === "filter" ? 1 : ease((f - i * 0.8) / 10);
              return <line key={i} x1={1110 + i * 15} y1={498 - i * 1.2} x2={1110 + i * 15} y2={498 - i * 1.2 + 120 * g} stroke="#c9a46a" strokeWidth={7} />;
            })
          : null}
        {mode === "hairs"
          ? [0, 1, 2, 3, 4, 5, 6].map((i) => {
              const p = pop(f, i * 3, 8);
              return (
                <g key={i}>
                  <circle cx={900 + (270 + i * 30) * 1.45} cy={500 + (-46 + i * 5) * 1.45} r={18 * p} fill="none" stroke={C.accent} strokeWidth={5} />
                  <line x1={900 + (270 + i * 30) * 1.45} y1={500 + (-46 + i * 5) * 1.45 - 10} x2={900 + (270 + i * 30) * 1.45 + 6} y2={500 + (-46 + i * 5) * 1.45 - 10 - 50 * p} stroke="#fff" strokeWidth={4} />
                </g>
              );
            })
          : null}
        {mode === "teeth" ? (
          <g>
            <path d={`M 1150 520 l 30 40 l 30 -40 l 30 40 l 30 -40 l 30 40 l 30 -40`} stroke={C.red} strokeWidth={10} fill="none" opacity={1 - e * 0.3} />
            <line x1={1120} y1={460} x2={1380} y2={620} stroke={C.red} strokeWidth={16} opacity={pop(f, 8)} />
            <line x1={1380} y1={460} x2={1120} y2={620} stroke={C.red} strokeWidth={16} opacity={pop(f, 8)} />
          </g>
        ) : null}
        {tube ? (
          <g>
            <path d={`M 1240 530 C 1100 560 900 580 700 600`} stroke={C.red} strokeWidth={tw * 2} fill="none" strokeLinecap="round" opacity={0.9} />
            <ellipse cx={640} cy={610} rx={90} ry={70} fill={C.red} opacity={0.7} />
          </g>
        ) : null}
        {mode === "fist" ? (
          <g transform={`translate(${1520 - (1 - pop(f, 3, 10)) * 300} 300)`}>
            <rect x={-60} y={-50} width={120} height={100} rx={40} fill="#e9c3a0" />
            {[0, 1, 2, 3].map((i) => <rect key={i} x={-56 + i * 29} y={-66} width={26} height={40} rx={12} fill="#e2b48f" />)}
            <rect x={-40} y={46} width={80} height={120} rx={20} fill="#e9c3a0" />
          </g>
        ) : null}
        {mode === "person" ? (
          <g transform={`translate(${1400 - e * 160} 560)`}>
            <circle cx={0} cy={-150} r={36} fill={HUD} />
            <rect x={-70} y={-110} width={140} height={200} rx={50} fill={HUD} />
            <line x1={-120} y1={-40} x2={-260 + e * 40} y2={-40} stroke={C.red} strokeWidth={10} />
            <line x1={120} y1={-40} x2={260} y2={-40} stroke={C.red} strokeWidth={10} opacity={0.6} />
          </g>
        ) : null}
        {mode === "birds"
          ? [0, 1, 2].map((i) => {
              const t = ((f / 40 + i / 3) % 1 + 1) % 1;
              return <Bird key={i} x={lerp(1240, 680, t)} y={lerp(530, 605, t)} s={0.8} dive f={f} />;
            })
          : null}
      </Svg>
      {title ? <Label text={title} x={150} y={150} size={40} color={C.accent} /> : null}
      {note ? <div style={{ position: "absolute", left: 0, right: 0, top: 150, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 70, color: "#fff", textShadow: SHADOW, opacity: pop(f, 4) }}>{note}</div> : null}
    </Backdrop>
  );
};

// Bubble net from above: one whale spirals out a curtain of bubbles, fish pack in, mouths break the middle.
export const NetShot: React.FC<{ stage: "spiral" | "tighten" | "lunge" | "ring" | "kayak"; label?: string }> = ({ stage, label }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const R = stage === "tighten" ? lerp(380, 220, e) : stage === "lunge" ? 220 : 380;
  const g = stage === "spiral" ? Math.min(1, k * 1.1) : 1;
  const pts = Array.from({ length: 120 }, (_, i) => i / 120).filter((t) => t <= g);
  const wa = g * Math.PI * 2 * 1.1;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, #1d6d86 0%, #0a3a4c 60%, #041a24 100%)" }}>
      <Svg>
        {Array.from({ length: 30 }, (_, i) => (
          <path key={i} d={`M ${(random(`nw${i}`) * 2200 + f * 1.2) % 2200 - 140} ${random(`nh${i}`) * 1080} l 120 0`} stroke="#9fd2e0" strokeWidth={3} opacity={0.15} />
        ))}
        <Fish cx={960} cy={540} n={90} r={R * 0.55} f={f} color="#e4f2f5" seed="net" />
        {pts.map((t, i) => {
          const a = t * Math.PI * 2 * 1.1;
          const r = R + (1 - t) * 40;
          return <circle key={i} cx={960 + Math.cos(a) * r} cy={540 + Math.sin(a) * r * 0.85} r={7 + random(`nb${i}`) * 9 + Math.sin(f * 0.3 + i) * 2} fill="#f4fbfc" opacity={0.85} />;
        })}
        {stage === "spiral" ? <WhaleTop x={960 + Math.cos(wa) * (R + 60)} y={540 + Math.sin(wa) * (R + 60) * 0.85} s={0.32} rot={(wa * 180) / Math.PI + 90} f={f} /> : null}
        {stage === "lunge"
          ? [0, 1, 2, 3].map((i) => {
              const p = ease((k - i * 0.08) * 2.2);
              return (
                <g key={i} transform={`translate(${900 + (i % 2) * 140} ${480 + Math.floor(i / 2) * 140}) scale(${0.3 + p * 0.5})`} opacity={p}>
                  <path d="M -70 120 C -80 0 -40 -110 0 -140 C 40 -110 80 0 70 120 Z" fill={BODY} />
                  <path d="M -50 120 C -40 30 -10 -40 0 -60 C 10 -40 40 30 50 120 Z" fill="#7a2e3a" />
                </g>
              );
            })
          : null}
        {stage === "kayak" ? (
          <g transform={`translate(960 ${540 + Math.sin(f * 0.1) * 6}) rotate(-20) scale(0.6)`}>
            <path d="M -230 0 Q 0 -60 230 0 Q 0 60 -230 0 Z" fill="#ffcc1a" stroke="#7a5a00" strokeWidth={5} />
            <circle cx={0} cy={0} r={34} fill="#e0572b" />
          </g>
        ) : null}
      </Svg>
      {label ? <Label text={label} x={150} y={150} size={40} /> : null}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.6) 100%)" }} />
    </AbsoluteFill>
  );
};

// Antarctic floe: orcas, the wave, the humpback lifting the seal onto its chest.
export const IceShot: React.FC<{ stage: "floe" | "orcas" | "wave" | "arrive" | "slide" | "chest" | "nudge" | "away" | "boat"; children?: React.ReactNode }> = ({ stage, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const WL = 600;
  const sealOnFloe = stage === "floe" || stage === "orcas" || stage === "wave" || stage === "boat";
  const humpback = stage === "arrive" || stage === "slide" || stage === "chest" || stage === "nudge";
  return (
    <AbsoluteFill style={{ background: SKY.polar }}>
      <Svg>
        <Mountains y={WL} color="#c9d6df" snow />
        <rect x={0} y={WL} width={1920} height={480} fill="#2e5466" />
        {Array.from({ length: 30 }, (_, i) => (
          <rect key={i} x={((random(`iw${i}`) * 2200 + f) % 2200) - 140} y={WL + 10 + random(`ih${i}`) * 460} width={90} height={4} fill="#cfe2ea" opacity={0.2} />
        ))}
        {stage !== "away" ? (
          <g transform={`translate(${stage === "wave" ? 1100 + Math.sin(f * 0.3) * 20 : 1100} ${WL - 4 + (stage === "wave" ? Math.sin(f * 0.25) * 18 : 0)}) rotate(${stage === "wave" ? Math.sin(f * 0.25) * 6 : 0})`}>
            <path d="M -260 0 L -230 -40 L 220 -46 L 260 0 Z" fill="#f2f7fa" stroke="#9fb6c4" strokeWidth={4} />
            {sealOnFloe ? <Seal x={0} y={-80} s={0.9} f={f} rot={stage === "wave" ? e * 18 : 0} /> : null}
          </g>
        ) : (
          <g>
            <path d="M 1200 600 L 1230 560 L 1680 554 L 1720 600 Z" fill="#f2f7fa" stroke="#9fb6c4" strokeWidth={4} />
            <Seal x={lerp(1000, 1450, e)} y={lerp(640, 520, e)} s={0.9} f={f} />
          </g>
        )}
        {stage === "orcas" || stage === "wave" || stage === "boat"
          ? [0, 1, 2].map((i) => (
              <g key={i} transform={`translate(${lerp(500 + i * 160, 760 + i * 140, e)} ${WL + 6})`}>
                <path d={`M 0 0 L -26 ${-110 - i * 10} L -70 0 Z`} fill="#0b0e12" />
              </g>
            ))
          : null}
        {stage === "wave" ? <path d={`M 500 ${WL} C 700 ${WL - 160 * Math.sin(e * Math.PI)} 900 ${WL - 120 * Math.sin(e * Math.PI)} 1100 ${WL}`} fill="#3f6f84" /> : null}
        {stage === "boat" ? (
          <g transform={`translate(300 ${WL - 4})`}>
            <path d="M -160 -40 L 170 -40 L 140 10 L -140 10 Z" fill="#ff7a1a" />
            <circle cx={20} cy={-80} r={20} fill="#e9c3a0" />
            <rect x={-6} y={-60} width={50} height={22} rx={6} fill="#222" />
            <rect x={40} y={-58} width={60} height={14} rx={6} fill="#111" />
          </g>
        ) : null}
        {humpback ? (
          <g transform={`translate(${stage === "arrive" ? lerp(1800, 1100, e) : 1100} ${stage === "arrive" ? WL + 120 : WL + 90})`}>
            {stage === "arrive" ? (
              <Whale x={0} y={0} s={0.55} f={f} flip />
            ) : (
              <g>
                <path d="M -360 40 C -300 -30 -120 -60 60 -56 C 240 -52 360 -10 380 40 Z" fill={BELLY} />
                {Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${-200 + i * 50} -40 L ${-180 + i * 50} 30`} stroke="#8e9ca5" strokeWidth={4} />)}
                <path d={`M -120 -40 C -260 ${-140 - (stage === "nudge" ? Math.sin(f * 0.3) * 30 : 0)} -340 -120 -420 -60`} stroke={FIN} strokeWidth={46} strokeLinecap="round" fill="none" />
                <path d="M 120 -40 C 260 -140 340 -120 420 -60" stroke={FIN} strokeWidth={46} strokeLinecap="round" fill="none" />
                <Seal x={stage === "slide" ? lerp(-60, -120, e) : 0} y={stage === "slide" ? lerp(40, -70, e) : -96 + (stage === "nudge" ? Math.sin(f * 0.3) * 10 : 0)} s={0.8} f={f} rot={stage === "nudge" ? Math.sin(f * 0.3) * 8 : 0} />
              </g>
            )}
          </g>
        ) : null}
      </Svg>
      {children}
    </AbsoluteFill>
  );
};

// Old whaling: a sailing ship, a boat being smashed, a harpoon cannon, a whale on the slipway.
export const ShipShot: React.FC<{ mode: "sail" | "boat" | "smash" | "harpoon" | "cannon" | "slipway" | "deck"; label?: string }> = ({ mode, label }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const WL = 640;
  const roll = Math.sin(f * 0.08) * 3;
  return (
    <AbsoluteFill style={{ background: SKY.grey }}>
      <Svg>
        <rect x={0} y={WL} width={1920} height={440} fill="#3b4e5a" />
        {Array.from({ length: 34 }, (_, i) => (
          <path key={i} d={`M ${((random(`hw${i}`) * 2200 + f * 1.5) % 2200) - 140} ${WL + 10 + random(`hh${i}`) * 420} q 30 -12 60 0`} stroke="#c3d0d6" strokeWidth={4} fill="none" opacity={0.3} />
        ))}
        {mode === "sail" || mode === "harpoon" || mode === "deck" ? (
          <g transform={`translate(${mode === "sail" ? lerp(700, 1000, e) : 900} ${WL}) rotate(${roll})`}>
            <path d="M -360 -20 L 380 -20 L 300 70 L -300 70 Z" fill="#3a2614" />
            {[-180, 40, 240].map((mx, i) => (
              <g key={i}>
                <line x1={mx} y1={-20} x2={mx} y2={-460 + i * 40} stroke="#2a1a0c" strokeWidth={12} />
                <path d={`M ${mx - 120} ${-420 + i * 40} Q ${mx + 20} ${-380 + i * 40} ${mx + 120} ${-420 + i * 40} L ${mx + 110} ${-200 + i * 30} Q ${mx} ${-170 + i * 30} ${mx - 110} ${-200 + i * 30} Z`} fill="#e8dcc0" />
              </g>
            ))}
            {mode === "harpoon" ? <line x1={360} y1={-30} x2={lerp(380, 1000, e)} y2={lerp(-40, 40, e)} stroke="#222" strokeWidth={5} /> : null}
          </g>
        ) : null}
        {mode === "boat" || mode === "smash" ? (
          <g>
            <g transform={`translate(${mode === "smash" ? 900 + e * 120 : 900} ${WL - (mode === "smash" ? Math.sin(e * Math.PI) * 220 : 0)}) rotate(${mode === "smash" ? e * 70 : roll})`}>
              <path d="M -200 -10 Q 0 30 200 -10 L 170 30 Q 0 60 -170 30 Z" fill="#5a3a1c" />
              {[-120, -40, 40, 120].map((px) => <rect key={px} x={px - 12} y={-60} width={24} height={50} rx={10} fill="#2a2a2a" />)}
            </g>
            {mode === "smash" ? (
              <g transform={`translate(860 ${WL + 60})`}>
                <path d="M 0 60 C -10 0 -60 -40 -230 -70 C -150 -10 -60 10 -20 40 Z M 0 60 C 10 0 60 -40 230 -70 C 150 -10 60 10 20 40 Z" fill={BODY} transform={`translate(0 ${-e * 140})`} />
              </g>
            ) : (
              <path d={`M 1300 ${WL + 4} Q 1440 ${WL - 50} 1600 ${WL + 4} Z`} fill={BODY} />
            )}
          </g>
        ) : null}
        {mode === "cannon" ? (
          <g transform={`translate(400 ${WL - 60})`}>
            <path d="M -300 60 L 300 60 L 260 140 L -260 140 Z" fill="#2a2e33" />
            <g transform={`rotate(${-8 - Math.min(1, f / 8) * 4} 120 0)`}>
              <rect x={60} y={-30} width={300} height={60} rx={20} fill="#1b1f24" />
            </g>
            {f > 8 ? <circle cx={420} cy={-40} r={40 + (f - 8) * 10} fill="#d8dcdf" opacity={Math.max(0, 1 - (f - 8) / 20)} /> : null}
            <line x1={360} y1={-40} x2={360 + Math.min(1, f / 14) * 1100} y2={-40 + Math.min(1, f / 14) * 80} stroke="#111" strokeWidth={6} />
          </g>
        ) : null}
        {mode === "slipway" ? (
          <g>
            <path d={`M 200 ${WL} L 1700 ${WL - 260} L 1920 ${WL - 260} L 1920 1080 L 200 1080 Z`} fill="#5b5248" />
            <g transform={`translate(${lerp(500, 900, e)} ${lerp(WL - 30, WL - 110, e)}) rotate(-10)`}>
              <Whale x={0} y={0} s={0.7} f={0} />
            </g>
            <line x1={1600} y1={WL - 300} x2={lerp(820, 1220, e)} y2={lerp(WL - 60, WL - 150, e)} stroke="#222" strokeWidth={8} />
          </g>
        ) : null}
      </Svg>
      {label ? <Label text={label} x={150} y={150} size={40} color="#2a1d10" /> : null}
    </AbsoluteFill>
  );
};

// A 19th-century newspaper page with a headline and the year counting up.
export const NewsShot: React.FC<{ head: string; year?: number; sub?: string }> = ({ head, year, sub }) => {
  const { f, dur } = useShot();
  const y = year ? Math.round(interpolate(f, [0, dur * 0.6], [year - 40, year], clamp)) : null;
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 40%, #3a2c1c 0%, #140d06 80%)" specks={false}>
      <div style={{ position: "absolute", left: 320, right: 320, top: 110, bottom: 250, background: "#efe6cc", boxShadow: "0 20px 60px rgba(0,0,0,0.5)", transform: `rotate(-2deg) scale(${1 + 0.05 * ease(f / dur)})`, padding: 50 }}>
        <div style={{ fontFamily: "Georgia, serif", fontWeight: 700, fontSize: 40, color: "#2a1d10", textAlign: "center", borderBottom: "4px solid #2a1d10", paddingBottom: 10 }}>{y ?? ""}</div>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 82, color: "#1d140a", textAlign: "center", marginTop: 30, lineHeight: 1.05, whiteSpace: "pre-line", opacity: pop(f, 3) }}>{head}</div>
        {sub ? <div style={{ fontFamily: "Georgia, serif", fontSize: 40, color: "#3a2a18", textAlign: "center", marginTop: 26, opacity: pop(f, 8) }}>{sub}</div> : null}
        {Array.from({ length: 4 }, (_, i) => <div key={i} style={{ height: 12, background: "rgba(42,29,16,0.25)", marginTop: 22, width: `${70 + random(`nl${i}`) * 30}%` }} />)}
      </div>
    </Backdrop>
  );
};

// A singing male hanging head-down, with the song as a scrolling line.
export const SongShot: React.FC<{ mode: "hang" | "wave" | "repeat"; label?: string }> = ({ mode, label }) => {
  const { f } = useShot();
  const pts: string[] = [];
  for (let i = 0; i <= 200; i++) {
    const x = 120 + i * 8.4;
    const t = i * 0.2 + f * 0.25;
    pts.push(`${x},${860 + Math.sin(t) * 40 * Math.sin(t * 0.13) + Math.sin(t * 2.7) * 14}`);
  }
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#1f6b86 0%, #0b3546 50%, #031118 100%)" }}>
      <Svg>
        {mode !== "wave" ? <Whale x={960} y={440} s={0.62} rot={-80} f={f * 0.3} /> : null}
        {mode === "wave"
          ? [0, 1, 2, 3, 4].map((i) => {
              const t = ((f / 40 + i / 5) % 1 + 1) % 1;
              return <circle key={i} cx={960} cy={540} r={60 + t * 700} fill="none" stroke={HUD} strokeWidth={6} opacity={1 - t} />;
            })
          : null}
        <polyline points={pts.join(" ")} stroke={C.accent} strokeWidth={6} fill="none" />
        {mode === "repeat"
          ? [0, 1, 2].map((i) => <rect key={i} x={200 + i * 520} y={790} width={480} height={140} rx={16} fill="none" stroke={HUD} strokeWidth={4} opacity={pop(f, i * 6)} />)
          : null}
      </Svg>
      {label ? <Label text={label} x={150} y={150} size={40} /> : null}
    </AbsoluteFill>
  );
};

// ---------- Maps of the Americas, the Pacific and Antarctica ----------

const SA: [number, number][] = [[-80, 10], [-75, 11], [-62, 10.5], [-52, 5], [-50, 0], [-35, -5], [-35, -9], [-39, -15], [-41, -22], [-48, -26], [-53, -34], [-58, -38], [-62, -40], [-65, -45], [-68, -50], [-69, -52.5], [-71, -54], [-74, -52], [-75, -47], [-73.5, -40], [-71.5, -30], [-70.3, -18], [-75, -15], [-81, -6], [-80, -2], [-77, 4], [-78, 8]];
const NA: [number, number][] = [[-78, 8], [-80, 7.5], [-83, 8.5], [-86, 12], [-88, 13.5], [-92, 14.5], [-95, 16], [-100, 17], [-105, 20], [-110, 23], [-112, 29], [-117, 32.5], [-121, 35], [-124, 40], [-124, 48], [-128, 51], [-133, 56], [-140, 60], [-150, 60], [-158, 57], [-165, 60], [-166, 68], [-156, 71], [-141, 70], [-125, 70], [-110, 68], [-95, 69], [-90, 68], [-82, 66], [-94, 59], [-82, 55], [-78, 62], [-64, 60], [-56, 52], [-60, 46], [-66, 45], [-70, 43.5], [-70.5, 42], [-70, 41.6], [-74, 40.5], [-76, 35], [-81, 31], [-80, 27], [-81, 25], [-82, 28], [-84, 30], [-90, 29.5], [-97, 26], [-97, 20], [-91, 19], [-87, 21], [-88, 16], [-84, 15], [-83, 11], [-80, 9]];
const AU: [number, number][] = [[114, -22], [122, -17], [126, -14], [130, -12], [136, -12], [137, -15.5], [141, -17], [142, -11], [145, -15], [150, -23], [153, -28], [153, -32], [151, -34], [150, -37], [146, -39], [141, -38], [138, -35], [135, -35], [131, -31.5], [124, -34], [118, -35], [115, -34], [115, -30], [113, -26]];
const NZ: [number, number][][] = [
  [[172, -34.5], [178, -37.5], [177, -39.5], [174.5, -41.5], [172.5, -40.5], [174.5, -38.5]],
  [[172.5, -41], [174, -41.5], [171, -44], [168, -46.5], [166.5, -46], [169, -43.5]],
];
const FALK: [number, number][] = [[-61.3, -51.3], [-58, -51.3], [-57.8, -52], [-61, -52.2]];
const ANT: [number, number][] = [
  ...Array.from({ length: 25 }, (_, i) => [-180 + i * 4.5, -72 - Math.sin(i) * 2] as [number, number]),
  [-72, -70], [-66, -67], [-62, -64.5], [-57, -63.3], [-58, -64.5], [-62, -68], [-61, -72], [-60, -76],
  ...Array.from({ length: 50 }, (_, i) => [-50 + i * 4.6, -70 + Math.sin(i * 0.7) * 3 + (i > 20 && i < 40 ? 3.5 : 0)] as [number, number]),
  [180, -72], [180, -90], [-180, -90],
];
const ISLANDS: [number, number][] = [[165.5, -21.5], [-175.2, -21.2], [-170.7, -14.3], [-159.8, -21.2], [-149.5, -17.6], [-91, -0.5], [-157.9, 21.3], [-155.5, 19.6]];

// pacific: longitudes run 0..360 so the Pacific is in one piece.
export const WorldMap: React.FC<{
  lon: number;
  lat: number;
  z0?: number;
  z1?: number;
  pacific?: boolean;
  pins?: { lon: number; lat: number; label: string; color?: string }[];
  path?: [number, number][];
  waves?: [number, number][];
  label?: string;
  counter?: { to: number; unit: string };
}> = ({ lon, lat, z0 = 1, z1 = 1.12, pacific = false, pins = [], path, waves, label, counter }) => {
  const lang = useLang();
  const { f, k, dur } = useShot();
  const z = (z0 + (z1 - z0) * ease(k)) * 9;
  const L = (lo: number) => (pacific && lo < 0 ? lo + 360 : lo);
  const X = (lo: number) => 960 + (L(lo) - L(lon)) * z;
  const Y = (la: number) => 540 - (la - lat) * z * 1.1;
  const poly = (p: [number, number][]) => p.map(([a, b]) => `${X(a)},${Y(b)}`).join(" ");
  const shapes = [SA, NA, AU, ...NZ, FALK];
  const prog = path ? ease(f / (dur * 0.8)) : 0;
  const pp = path ? path.slice(0, Math.max(1, Math.ceil(prog * path.length))) : [];
  const wv = waves ? Math.min(waves.length, Math.floor((f / (dur * 0.8)) * waves.length) + 1) : 0;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #0f3a47 0%, #061a22 70%)" }}>
      <Svg>
        {Array.from({ length: 37 }, (_, i) => <line key={`a${i}`} x1={X(-180 + i * 10 + (pacific ? 180 : 0))} y1={0} x2={X(-180 + i * 10 + (pacific ? 180 : 0))} y2={1080} stroke="rgba(127,233,255,0.07)" strokeWidth={2} />)}
        {Array.from({ length: 19 }, (_, i) => <line key={`b${i}`} x1={0} y1={Y(-90 + i * 10)} x2={1920} y2={Y(-90 + i * 10)} stroke="rgba(127,233,255,0.07)" strokeWidth={2} />)}
        {shapes.map((p, i) => <polygon key={i} points={poly(p)} fill="#1d4650" stroke="#3f8590" strokeWidth={3} />)}
        <polygon points={poly(ANT.map(([a, b]) => [pacific && a < 0 ? a : a, b]))} fill="#3a6470" stroke="#6fa3b2" strokeWidth={3} opacity={0.9} />
        {pacific ? <polygon points={poly(ANT.map(([a, b]) => [a + 360, b] as [number, number]))} fill="#3a6470" stroke="#6fa3b2" strokeWidth={3} opacity={0.9} /> : null}
        {ISLANDS.map(([a, b], i) => <circle key={i} cx={X(a)} cy={Y(b)} r={6} fill="#3f8590" />)}
        {pp.length > 1 ? <polyline points={pp.map(([a, b]) => `${X(a)},${Y(b)}`).join(" ")} stroke={C.red} strokeWidth={8} fill="none" strokeLinecap="round" strokeDasharray="2 16" /> : null}
        {pp.length > 0 ? <circle cx={X(pp[pp.length - 1][0])} cy={Y(pp[pp.length - 1][1])} r={14} fill={C.accent} /> : null}
        {waves
          ? waves.slice(0, wv).map(([a, b], i) => {
              const t = ((f / 24 + i / 4) % 1 + 1) % 1;
              return <circle key={i} cx={X(a)} cy={Y(b)} r={20 + t * 70} fill="none" stroke={[C.accent, HUD, C.red, "#9cff8a", "#ff9cf0", "#fff"][i % 6]} strokeWidth={6} opacity={1 - t} />;
            })
          : null}
        {pins.map((p, i) => {
          const s = pop(f, 3 + i * 4, 8);
          return (
            <g key={i} transform={`translate(${X(p.lon)} ${Y(p.lat)}) scale(${s})`}>
              <circle r={18} fill={p.color ?? C.red} />
              <circle r={18 + ((f * 1.5) % 40)} fill="none" stroke={p.color ?? C.red} strokeWidth={4} opacity={1 - ((f * 1.5) % 40) / 40} />
              <text x={30} y={12} fill="#fff" fontFamily={FONT} fontWeight={800} fontSize={44} stroke="#000" strokeWidth={6} paintOrder="stroke">{p.label}</text>
            </g>
          );
        })}
      </Svg>
      {label ? <Label text={label} x={150} y={150} size={40} /> : null}
      {counter ? (
        <div style={{ position: "absolute", right: 150, bottom: 200, fontFamily: FONT, fontWeight: 800, fontSize: 110, color: C.accent, textShadow: SHADOW }}>
          {Math.round(counter.to * ease(f / (dur * 0.8))).toLocaleString(lang === "en" ? "en-US" : "uk-UA")}
          <span style={{ fontSize: 50 }}> {counter.unit}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// Whale against things you know: a person, one bus, two buses, elephants.
export const WhaleScale: React.FC<{ vs: "person" | "bus" | "bus2" | "elephants" | "flipper"; title: string; count?: number }> = ({ vs, title, count = 6 }) => {
  const { f } = useShot();
  const g = ease(f / 14);
  const Bus = ({ x }: { x: number }) => (
    <g>
      <rect x={x} y={560} width={560} height={240} rx={34} fill="none" stroke={HUD} strokeWidth={7} />
      {Array.from({ length: 5 }, (_, i) => <rect key={i} x={x + 30 + i * 104} y={590} width={84} height={80} rx={10} fill="none" stroke={HUD} strokeWidth={5} />)}
      <circle cx={x + 120} cy={800} r={44} fill="#06100f" stroke={HUD} strokeWidth={7} />
      <circle cx={x + 440} cy={800} r={44} fill="#06100f" stroke={HUD} strokeWidth={7} />
    </g>
  );
  return (
    <Backdrop v="deep">
      <Svg>
        {vs === "bus" ? <Bus x={560} /> : null}
        {vs === "bus2" ? (
          <g>
            <Bus x={260} />
            <Bus x={860} />
          </g>
        ) : null}
        {vs === "elephants"
          ? Array.from({ length: count }, (_, i) => {
              const p = pop(f, i * 3, 8);
              return (
                <g key={i} transform={`translate(${260 + i * 240} 830) scale(${0.9 * p})`} fill={HUD}>
                  <ellipse cx={0} cy={-120} rx={100} ry={70} />
                  <circle cx={90} cy={-150} r={50} />
                  <path d="M 130 -140 Q 170 -60 140 0 L 120 0 Q 140 -60 110 -120 Z" />
                  {[-60, -20, 30, 60].map((lx) => <rect key={lx} x={lx - 14} y={-70} width={28} height={70} rx={10} />)}
                </g>
              );
            })
          : null}
        {vs === "person" ? (
          <g transform="translate(1600 860)" fill={HUD}>
            <circle cx={0} cy={-210} r={32} />
            <rect x={-36} y={-176} width={72} height={176} rx={28} />
          </g>
        ) : null}
        <g opacity={vs === "elephants" ? 0.5 : 0.95}>
          <Whale x={960 - (1 - g) * 200} y={vs === "elephants" ? 450 : vs === "flipper" ? 440 : 420} s={vs === "flipper" ? 1.3 : 1.25} f={f} />
        </g>
        {vs === "flipper" ? <path d={`M ${960 + 170 * 1.3} ${440 + 58 * 1.3} L ${960 - 190 * 1.3} ${440 + 290 * 1.3}`} stroke={C.accent} strokeWidth={8} strokeDasharray="20 12" opacity={g} /> : null}
        <line x1={160} y1={960} x2={160 + 1600 * g} y2={960} stroke={C.accent} strokeWidth={8} />
      </Svg>
      <Label text={title} x={160} y={990} color={C.accent} size={38} />
    </Backdrop>
  );
};

// A population line falling and recovering, with an optional "protected" marker.
export const PopShot: React.FC<{ stage: "fall" | "protect" | "rise"; label: string; mark: string }> = ({ stage, label, mark }) => {
  const { f, dur } = useShot();
  const pts: [number, number][] = [[1900, 100], [1920, 92], [1940, 60], [1960, 20], [1970, 8], [1985, 5], [2000, 20], [2025, 70]];
  const upto = stage === "fall" ? interpolate(f, [0, dur * 0.8], [1900, 1985], clamp) : stage === "protect" ? 1985 : interpolate(f, [0, dur * 0.8], [1985, 2025], clamp);
  const X = (yr: number) => 240 + ((yr - 1900) / 125) * 1440;
  const Y = (v: number) => 860 - (v / 100) * 520;
  const seg: string[] = [];
  for (let i = 0; i < pts.length; i++) {
    if (pts[i][0] <= upto) seg.push(`${X(pts[i][0])},${Y(pts[i][1])}`);
    else {
      const [a, b] = [pts[i - 1], pts[i]];
      const t = (upto - a[0]) / (b[0] - a[0]);
      seg.push(`${X(upto)},${Y(a[1] + (b[1] - a[1]) * t)}`);
      break;
    }
  }
  return (
    <Backdrop v="night">
      <Svg>
        <line x1={240} y1={860} x2={1680} y2={860} stroke="#2f6a74" strokeWidth={5} />
        <line x1={240} y1={330} x2={240} y2={860} stroke="#2f6a74" strokeWidth={5} />
        {[1900, 1950, 1985, 2025].map((yr) => <text key={yr} x={X(yr)} y={910} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={32} textAnchor="middle">{yr}</text>)}
        <polyline points={seg.join(" ")} stroke={stage === "rise" ? HUD : C.red} strokeWidth={12} fill="none" strokeLinejoin="round" strokeLinecap="round" />
        {stage !== "fall" ? <line x1={X(1985)} y1={330} x2={X(1985)} y2={860} stroke={C.accent} strokeWidth={6} strokeDasharray="14 10" /> : null}
        {stage === "protect" ? <text x={X(1985) + 20} y={420} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={60} opacity={pop(f, 3)}>{mark}</text> : null}
      </Svg>
      <Label text={label} x={260} y={240} size={40} />
    </Backdrop>
  );
};

// A row of the animals humpbacks were seen defending, filling in one at a time.
export const VictimsShot: React.FC<{ items: ("seal" | "lion" | "calf" | "fish" | "humpback")[]; title: string; count?: number }> = ({ items, title, count }) => {
  const { f, dur } = useShot();
  const n = count ? Math.round(count * ease(f / (dur * 0.7))) : 0;
  return (
    <Backdrop v="deep">
      <Svg>
        {items.map((it, i) => {
          const p = pop(f, 2 + i * 5, 8);
          const x = 960 + (i - (items.length - 1) / 2) * 400;
          return (
            <g key={i} opacity={p} transform={`translate(${x} 560) scale(${0.6 + 0.4 * p})`}>
              <rect x={-170} y={-170} width={340} height={340} rx={30} fill="rgba(127,233,255,0.08)" stroke={HUD} strokeWidth={4} />
              {it === "seal" || it === "lion" ? <Seal x={-20} y={20} s={it === "lion" ? 0.95 : 0.85} f={f} /> : null}
              {it === "calf" ? <Whale x={0} y={-10} s={0.22} f={f} /> : null}
              {it === "humpback" ? <Whale x={0} y={-10} s={0.25} f={f} /> : null}
              {it === "fish" ? (
                <g>
                  <ellipse cx={0} cy={0} rx={90} ry={110} fill="#9aa8ae" />
                  <path d="M -20 -110 L 0 -200 L 20 -110 Z M -20 110 L 0 200 L 20 110 Z" fill="#9aa8ae" />
                  <circle cx={50} cy={-30} r={10} fill="#111" />
                </g>
              ) : null}
            </g>
          );
        })}
      </Svg>
      <Label text={title} x={200} y={200} size={40} />
      {count ? <div style={{ position: "absolute", right: 200, top: 170, fontFamily: FONT, fontWeight: 800, fontSize: 120, color: C.accent, textShadow: SHADOW }}>{n}</div> : null}
    </Backdrop>
  );
};

// A humpback charging an orca pack, flippers swinging.
export const FightShot: React.FC<{ stage: "charge" | "swing" | "scatter" }> = ({ stage }) => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <UnderShot rays deep={0.3}>
      <Svg>
        {[0, 1, 2].map((i) => (
          <Orca key={i} x={stage === "scatter" ? 1300 + i * 120 + e * (300 + i * 140) : 1250 + i * 140} y={380 + i * 150 + (stage === "scatter" ? (i - 1) * e * 160 : 0)} s={0.65} f={f + i * 9} flip={stage !== "scatter"} />
        ))}
        <g transform={`translate(${stage === "charge" ? lerp(-200, 500, e) : 520} 560)`}>
          <Whale x={0} y={0} s={0.8} f={stage === "swing" ? f * 3 : f} />
        </g>
        {stage === "swing" ? <path d={`M 700 600 Q 900 ${400 + Math.sin(f * 0.4) * 80} 1100 600`} stroke="#fff" strokeWidth={6} fill="none" opacity={0.5} /> : null}
      </Svg>
    </UnderShot>
  );
};

// One line of the safety list with its own little drawing on the right.
export const TipShot: React.FC<{ n: number; text: string; pic: "birds" | "fish" | "ring" | "away" | "distance" | "buoy" | "calm" }> = ({ n, text, pic }) => {
  const tr = useT();
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <Backdrop v="deep">
      <div style={{ position: "absolute", left: 140, top: 300, width: 860 }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 170, color: "transparent", WebkitTextStroke: `4px ${C.accent}`, lineHeight: 1, opacity: pop(f) }}>{String(n).padStart(2, "0")}</div>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 68, color: "#fff", lineHeight: 1.08, marginTop: 20, textShadow: SHADOW, opacity: pop(f, 3), whiteSpace: "pre-line" }}>{text}</div>
      </div>
      <div style={{ position: "absolute", left: 1060, top: 210, width: 720, height: 660, borderRadius: 30, overflow: "hidden", border: `5px solid ${HUD}` }}>
        <div style={{ position: "absolute", left: -600, top: -210, width: 1920, height: 1080, transform: "scale(1)" }}>
          {pic === "birds" ? <SurfaceShot sky="day" birds="dive" /> : null}
          {pic === "fish" ? <SurfaceShot sky="day" boil /> : null}
          {pic === "ring" ? <SurfaceShot sky="day" ring /> : null}
          {pic === "away" ? <SurfaceShot sky="day" kayak={{ x0: 1100, x1: 1450 }} ring /> : null}
          {pic === "distance" ? (
            <SurfaceShot sky="day" boat whaleFar>
              <Svg>
                <line x1={640} y1={600} x2={640 + 600 * e} y2={600} stroke={C.accent} strokeWidth={8} strokeDasharray="20 10" />
                <text x={880} y={680} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={64} stroke="#000" strokeWidth={6} paintOrder="stroke">{tr("100 М", "100 M")}</text>
              </Svg>
            </SurfaceShot>
          ) : null}
          {pic === "buoy" ? <SurfaceShot sky="day" buoy /> : null}
          {pic === "calm" ? <MouthPOV light="in" torch={false} /> : null}
        </div>
      </div>
    </Backdrop>
  );
};

registerKind("drawn", SurfaceShot, UnderShot, MouthPOV, IceShot, ShipShot, SongShot, NetShot, FightShot);
registerKind("graphic", CutawayShot, WhaleScale, PopShot, VictimsShot, TipShot, NewsShot);
registerKind("map", WorldMap);

export { lerp, SHADOW };
