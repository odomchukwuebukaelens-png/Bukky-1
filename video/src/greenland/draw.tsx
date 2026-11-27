// Drawn scenes for "The Shark That Might Be 400 Years Old" (Greenland shark).
import React from "react";
import { AbsoluteFill, random } from "remotion";
import { useShot } from "../kit/shots";
import { MONO } from "../kit/hud";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";

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
const BODY = "#5d5650";
const BELLY = "#8a8178";

// A Greenland shark from the side, facing right, about 640 px long at s = 1.
export const GShark: React.FC<{ x: number; y: number; s?: number; flip?: boolean; rot?: number; f?: number; parasite?: boolean; timeline?: number; glow?: number; outline?: boolean; opacity?: number }> = ({
  x, y, s = 1, flip = false, rot = 0, f = 0, parasite = false, timeline = 0, glow = 0, outline = false, opacity = 1,
}) => {
  const beat = Math.sin(f * 0.09) * 6; // slow: about one beat every 2–3 s of animation
  const fill = outline ? "none" : BODY;
  const stroke = outline ? C.white : "none";
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`} opacity={opacity}>
      <g transform={`rotate(${beat} -250 0)`}>
        <path d="M -250 -14 L -350 -92 C -340 -50 -330 -20 -318 0 L -340 46 L -250 14 Z" fill={fill} stroke={stroke} strokeWidth={4} />
      </g>
      <path d="M 320 4 C 318 -50 260 -86 160 -90 C 40 -94 -120 -70 -200 -40 C -230 -28 -250 -18 -252 -10 L -252 10 C -230 30 -120 72 20 78 C 160 84 290 60 320 4 Z" fill={fill} stroke={stroke} strokeWidth={4} />
      {!outline ? <path d="M 316 14 C 290 54 160 80 20 76 C -100 72 -200 40 -250 10 C -150 30 0 40 316 14 Z" fill={BELLY} /> : null}
      <path d="M -30 -84 L -62 -130 L -96 -74 Z M -160 -54 L -186 -92 L -210 -40 Z" fill={fill} stroke={stroke} strokeWidth={4} />
      <path d="M 170 56 L 120 120 L 110 60 Z" fill={fill} stroke={stroke} strokeWidth={4} />
      {!outline ? (
        <>
          {[0, 1, 2, 3, 4].map((i) => <line key={i} x1={200 - i * 12} y1={-14} x2={196 - i * 12} y2={26} stroke="#3b3632" strokeWidth={3} />)}
          <circle cx={262} cy={-22} r={7} fill="#0c0f12" />
          <path d="M 300 30 L 240 40" stroke="#3b3632" strokeWidth={4} />
          {Array.from({ length: 30 }, (_, i) => <circle key={i} cx={-200 + random(`gs${i}`) * 440} cy={-60 + random(`gt${i}`) * 100} r={3 + random(`gr${i}`) * 4} fill="#4a443f" opacity={0.6} />)}
          {parasite ? <path d={`M 262 -18 C 266 6 ${262 + Math.sin(f * 0.1) * 6} 28 ${258 + Math.sin(f * 0.1) * 8} 44`} stroke="#efe2d0" strokeWidth={7} strokeLinecap="round" fill="none" /> : null}
          {glow > 0 ? <ellipse cx={30} cy={0} rx={260} ry={60} fill={C.cyan} opacity={0.25 * glow} style={{ filter: "blur(16px)" }} /> : null}
        </>
      ) : null}
      {timeline > 0 ? (
        <g>
          <line x1={-240} y1={-4} x2={-240 + 540 * timeline} y2={-4} stroke={C.accent} strokeWidth={6} />
          {[["1620", 0], ["1776", 0.38], ["1900", 0.69], ["TODAY", 1]].map(([t, p], i) =>
            timeline >= (p as number) ? (
              <g key={i} transform={`translate(${-240 + 540 * (p as number)} -4)`}>
                <circle r={9} fill={C.accent} />
                <text y={-18} textAnchor="middle" fill={C.white} fontFamily={FONT} fontWeight={800} fontSize={26} stroke="#000" strokeWidth={5} paintOrder="stroke">{t}</text>
              </g>
            ) : null
          )}
        </g>
      ) : null}
    </g>
  );
};

// A ringed seal asleep, hanging upright in the water.
const SleepSeal: React.FC<{ x: number; y: number; s?: number; f?: number }> = ({ x, y, s = 1, f = 0 }) => (
  <g transform={`translate(${x} ${y + Math.sin(f * 0.06) * 6}) scale(${s}) rotate(80)`}>
    <path d="M -110 10 C -100 -30 -20 -46 60 -40 C 110 -36 130 -14 130 6 C 130 26 90 34 40 34 C -30 38 -90 34 -110 10 Z" fill="#8c8f8c" />
    <circle cx={120} cy={-8} r={26} fill="#8c8f8c" />
    <path d="M -110 10 L -150 -10 L -146 30 Z" fill="#767976" />
    {[0, 1, 2, 3, 4, 5].map((i) => <ellipse key={i} cx={-70 + i * 30} cy={-10 + (i % 2) * 16} rx={9} ry={6} fill="none" stroke="#5f625f" strokeWidth={3} />)}
    <path d="M 126 -14 q 6 4 12 0" stroke="#222" strokeWidth={3} fill="none" />
  </g>
);

export type GActor = { x0: number; y0: number; x1?: number; y1?: number; s?: number; s1?: number; flip?: boolean; rot?: number; parasite?: boolean; timeline?: [number, number]; glow?: number; o0?: number; o1?: number; outline?: boolean };

// Under the Arctic ice: an ice ceiling, dark cold water, specks.
export const Under: React.FC<{ sharks?: GActor[]; ice?: boolean; seal?: { x: number; y: number; s?: number }; person?: { x: number; y: number; s?: number; walk?: boolean }; car?: { x: number; y: number }; deep?: boolean; children?: React.ReactNode; light?: boolean }> = ({
  sharks = [], ice = true, seal, person, car, deep = false, children, light = false,
}) => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <AbsoluteFill style={{ background: deep ? "linear-gradient(#0a2630, #01080b)" : light ? "linear-gradient(#2b7a90, #0b3644)" : "linear-gradient(#1b5566, #041820)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {!deep ? [0, 1, 2, 3].map((i) => <polygon key={i} points={`${380 + i * 420},0 ${470 + i * 420},0 ${300 + i * 400},1080 ${210 + i * 400},1080`} fill="#d8f6ff" opacity={0.04} />) : null}
        {ice ? (
          <path d={`M -10 -10 L 1930 -10 L 1930 ${90} ${Array.from({ length: 26 }, (_, i) => `L ${1920 - i * 77} ${70 + random(`ic${i}`) * 70}`).join(" ")} L -10 100 Z`} fill="#e9f4f7" opacity={0.92} />
        ) : null}
        {Array.from({ length: 50 }, (_, i) => <circle key={i} cx={(random(`s${i}`) * 1920 + f * 0.3) % 1920} cy={(random(`t${i}`) * 1080 + f * 0.4) % 1080} r={1.5 + random(`u${i}`) * 2} fill="#e6fbff" opacity={0.3} />)}
        {seal ? <SleepSeal x={seal.x} y={seal.y} s={seal.s ?? 1} f={f} /> : null}
        {car ? (
          <g transform={`translate(${car.x} ${car.y})`}>
            <path d="M -200 0 L -200 -60 L -120 -60 L -70 -110 L 80 -110 L 130 -60 L 200 -55 L 200 0 Z" fill={C.accent} />
            <circle cx={-120} cy={0} r={30} fill="#111" />
            <circle cx={120} cy={0} r={30} fill="#111" />
          </g>
        ) : null}
        {person ? (
          <g transform={`translate(${person.walk ? person.x + 260 * e : person.x} ${person.y}) scale(${person.s ?? 1})`} fill={C.white}>
            <circle cx={0} cy={-170} r={18} />
            <path d={`M -18 -148 L 18 -148 L 22 -70 L ${14 + (person.walk ? Math.sin(f * 0.25) * 10 : 0)} 0 L 4 0 L 0 -60 L -4 0 L ${-14 - (person.walk ? Math.sin(f * 0.25) * 10 : 0)} 0 L -22 -70 Z`} />
          </g>
        ) : null}
        {sharks.map((a, i) => (
          <GShark key={i} x={lerp(a.x0, a.x1, e)} y={lerp(a.y0, a.y1, e)} s={lerp(a.s ?? 1, a.s1, e)} flip={a.flip} rot={a.rot} f={f + i * 17} parasite={a.parasite} timeline={a.timeline ? lerp(a.timeline[0], a.timeline[1], e) : 0} glow={a.glow} opacity={lerp(a.o0 ?? 1, a.o1, e)} outline={a.outline} />
        ))}
      </svg>
      {children}
    </AbsoluteFill>
  );
};

const Title: React.FC<{ text?: string; color?: string; size?: number; y?: number }> = ({ text, color = C.white, size = 64, y = 170 }) =>
  text ? <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: size, color, textShadow: SHADOW }}>{text}</div> : null;

// The eye lens in layers; the nucleus at the centre formed before birth.
export const Lens: React.FC<{ stage?: "layers" | "nucleus" | "date"; text?: string }> = ({ stage = "layers", text }) => {
  const { f } = useShot();
  const n = Math.min(14, Math.floor(f * 0.9));
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: n }, (_, i) => <circle key={i} cx={960} cy={520} r={380 - i * 24} fill={`rgba(200,230,240,${0.05 + i * 0.012})`} stroke="rgba(220,245,255,0.5)" strokeWidth={2} />)}
        {stage !== "layers" ? <circle cx={960} cy={520} r={50 + Math.sin(f * 0.2) * 4} fill={C.accent} opacity={0.9} /> : null}
        {stage !== "layers" ? <text x={960} y={620} textAnchor="middle" fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={38} stroke="#000" strokeWidth={6} paintOrder="stroke">NUCLEUS · MADE BEFORE BIRTH</text> : null}
        {stage === "date" ? <text x={960} y={300} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={44} opacity={pop(f, 8)}>¹⁴C → BIRTH YEAR</text> : null}
        {stage === "layers" ? <text x={960 + 380} y={170} textAnchor="end" fill="rgba(255,255,255,0.7)" fontFamily={MONO} fontWeight={700} fontSize={26}>NEW LAYERS ADDED ON THE OUTSIDE</text> : null}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// Atmospheric carbon-14: the bomb pulse of the early 1960s.
export const Bomb: React.FC<{ mark?: number; text?: string }> = ({ mark, text }) => {
  const { f } = useShot();
  const X = (yr: number) => 260 + ((yr - 1930) / 90) * 1400;
  const Yv = (v: number) => 820 - v * 520;
  const val = (yr: number) => (yr < 1955 ? 0.02 : yr < 1964 ? 0.02 + ((yr - 1955) / 9) * 0.95 : 0.97 * Math.exp(-(yr - 1964) / 16) + 0.04);
  const upto = 1930 + Math.min(90, f * 2.2);
  const pts = Array.from({ length: 91 }, (_, i) => 1930 + i).filter((y) => y <= upto).map((y) => `${X(y)},${Yv(val(y))}`).join(" ");
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <line x1={260} y1={820} x2={1680} y2={820} stroke="rgba(255,255,255,0.5)" strokeWidth={3} />
        {[1940, 1960, 1980, 2000, 2020].map((y) => <text key={y} x={X(y)} y={870} textAnchor="middle" fill="rgba(255,255,255,0.7)" fontFamily={MONO} fontWeight={700} fontSize={26}>{y}</text>)}
        <text x={260} y={260} fill={C.cyan} fontFamily={MONO} fontWeight={700} fontSize={28}>CARBON-14 IN THE AIR</text>
        <polyline points={pts} stroke={C.accent} strokeWidth={8} fill="none" />
        {mark ? <line x1={X(mark)} y1={300} x2={X(mark)} y2={820} stroke={C.red} strokeWidth={5} strokeDasharray="14 10" opacity={pop(f, 10)} /> : null}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// The 28 sharks of the 2016 study lined up by length, the biggest highlighted.
export const LineUp: React.FC<{ hi?: boolean; bomb?: boolean; text?: string }> = ({ hi = false, bomb = false, text }) => {
  const { f } = useShot();
  const lens = Array.from({ length: 28 }, (_, i) => 81 + (i / 27) * (502 - 81) + (random(`l${i}`) - 0.5) * 20);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {lens.slice().reverse().map((L, j) => {
          const i = 27 - j;
          const col = i % 4;
          const row = Math.floor(i / 4);
          const isBig = i === 27;
          const young = L <= 220;
          return (
            <g key={i} opacity={pop(f, i * 0.6, 6)}>
              <GShark x={240 + col * 460} y={230 + row * 92} s={(L / 502) * 0.55} outline={!(hi && isBig) && !(bomb && young)} />
              {bomb && young ? <circle cx={240 + col * 460 + 180} cy={230 + row * 92 - 30} r={10} fill={C.red} /> : null}
            </g>
          );
        })}
      </svg>
      <Title text={text} y={110} size={52} color={C.accent} />
    </AbsoluteFill>
  );
};

// Tail beats counted against a walking person.
export const TailBeat: React.FC<{ text?: string }> = ({ text }) => {
  const { f } = useShot();
  return (
    <Under ice={false} sharks={[{ x0: 600, y0: 520, x1: 900, s: 1.1 }]} person={{ x: 1250, y: 760, s: 1, walk: true }}>
      <Title text={text ?? `1 TAIL BEAT ≈ EVERY 7 SECONDS`} color={C.accent} size={56} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 160, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 34, color: C.white }}>{`0.34 M/S · ${(f / 30).toFixed(1)} S`}</div>
    </Under>
  );
};

// Genome size and jumping genes.
export const Genome: React.FC<{ stage?: "size" | "jump" | "repair"; text?: string }> = ({ stage = "size", text }) => {
  const { f, k } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {stage === "size" ? (
          <>
            <text x={200} y={420} fill={C.white} fontFamily={FONT} fontWeight={800} fontSize={40}>HUMAN · ≈ 3.1 BILLION</text>
            <rect x={200} y={440} width={700 * ease(f / 14)} height={50} rx={10} fill="#7fd4ff" />
            <text x={200} y={620} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={40}>GREENLAND SHARK · ≈ 6.5 BILLION</text>
            <rect x={200} y={640} width={1470 * ease((f - 6) / 16)} height={50} rx={10} fill={C.accent} />
          </>
        ) : (
          <>
            {Array.from({ length: 60 }, (_, i) => {
              const x = 160 + i * 27;
              const y1 = 540 + Math.sin(i * 0.45 + f * 0.08) * 120;
              const y2 = 540 - Math.sin(i * 0.45 + f * 0.08) * 120;
              const jump = stage === "jump" && i % 7 === 0;
              return (
                <g key={i}>
                  <line x1={x} y1={y1} x2={x} y2={y2} stroke={jump ? C.red : "rgba(255,255,255,0.35)"} strokeWidth={jump ? 6 : 3} />
                  <circle cx={x} cy={y1} r={7} fill={C.cyan} />
                  <circle cx={x} cy={y2} r={7} fill={C.accent} />
                </g>
              );
            })}
            {stage === "repair"
              ? [0, 1, 2].map((i) => {
                  const x = 400 + i * 500;
                  return <g key={i} opacity={ease(k * 3 - i * 0.6)}><circle cx={x} cy={540} r={60} fill="none" stroke="#7dff9a" strokeWidth={6} /><text x={x} y={650} textAnchor="middle" fill="#7dff9a" fontFamily={MONO} fontWeight={700} fontSize={26}>REPAIRED</text></g>;
                })
              : null}
            {stage === "jump" ? <text x={960} y={820} textAnchor="middle" fill={C.red} fontFamily={MONO} fontWeight={700} fontSize={34}>{`> 70% "JUMPING GENES"`}</text> : null}
          </>
        )}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// A simple chart of the North Atlantic, Arctic and Caribbean.
const NA_LAND: [number, number][][] = [
  [[-55, 60], [-44, 60], [-40, 65], [-22, 70], [-20, 76], [-18, 81], [-35, 83], [-60, 82], [-72, 78], [-68, 76], [-58, 75], [-54, 70], [-52, 66]],
  [[-24, 65.5], [-18, 66.5], [-13.5, 65.5], [-15, 64], [-19, 63.4], [-22.7, 64]],
  [[5, 58], [5, 62], [10, 64], [14, 68], [20, 70], [28, 71], [30, 70], [30, 60], [12, 56], [8, 58]],
  [[-10, 36], [-9, 43], [-2, 44], [-5, 48], [2, 51], [8, 54], [12, 56], [30, 56], [30, 36]],
  [[-6, 50], [-5, 58.6], [-3, 58.6], [0, 52], [1.5, 51]],
  [[-100, 15], [-97, 26], [-90, 29], [-82, 30], [-81, 25], [-80, 32], [-76, 35], [-75, 39], [-70, 42], [-66, 44], [-60, 46], [-53, 47], [-56, 52], [-62, 58], [-65, 60], [-78, 62], [-90, 64], [-100, 70], [-100, 15]],
  [[-100, 15], [-88, 13], [-83, 10], [-79, 9], [-77, 8], [-78, 15], [-84, 16], [-88, 18], [-87, 21], [-90, 21], [-97, 18]],
];
export const NAMap: React.FC<{ cx?: number; cy?: number; z0?: number; z1?: number; pins?: { lon: number; lat: number; label: string; color?: string }[]; route?: [number, number][]; range?: boolean; text?: string }> = ({ cx = -35, cy = 55, z0 = 1, z1 = 1.06, pins = [], route, range = false, text }) => {
  const { f, k } = useShot();
  const z = lerp(z0, z1, ease(k));
  const K = 10.5 * z;
  const X = (lon: number) => 960 + (lon - cx) * K * 0.7;
  const Y = (lat: number) => 540 - (lat - cy) * K;
  const poly = (p: [number, number][]) => p.map(([lo, la]) => `${X(lo)},${Y(la)}`).join(" ");
  const prog = ease(f / 40);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0f4050 0%, #06202a 75%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {range ? <path d={`M ${X(-70)} ${Y(80)} L ${X(20)} ${Y(80)} L ${X(20)} ${Y(60)} L ${X(-5)} ${Y(55)} L ${X(-40)} ${Y(42)} L ${X(-70)} ${Y(40)} Z`} fill={C.accent} opacity={0.12} /> : null}
        {NA_LAND.map((p, i) => <polygon key={i} points={poly(p)} fill="#2a4f4a" stroke="#5f9a8c" strokeWidth={3} />)}
        {route ? <polyline points={route.slice(0, Math.max(1, Math.ceil(prog * route.length))).map(([lo, la]) => `${X(lo)},${Y(la)}`).join(" ")} stroke={C.accent} strokeWidth={7} strokeDasharray="18 10" fill="none" /> : null}
        {pins.map((p, i) => {
          const s = pop(f, 3 + i * 5, 8);
          return (
            <g key={i} transform={`translate(${X(p.lon)} ${Y(p.lat)}) scale(${s})`}>
              <circle r={14} fill={p.color ?? C.red} />
              <circle r={14 + ((f * 1.5) % 34)} fill="none" stroke={p.color ?? C.red} strokeWidth={4} opacity={1 - ((f * 1.5) % 34) / 34} />
              <text x={26} y={12} fill="#fff" fontFamily={FONT} fontWeight={800} fontSize={38} stroke="#000" strokeWidth={7} paintOrder="stroke">{p.label}</text>
            </g>
          );
        })}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// Warm surface water over cold deep water on a reef slope, the shark in the cold layer.
export const Layers: React.FC<{ text?: string }> = ({ text }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#25a6c4 0%, #1a7f9b 30%, #0d3a4c 34%, #041820 100%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <path d="M 0 200 L 260 230 L 420 420 L 600 700 L 760 1080 L 0 1080 Z" fill="#3a3a32" />
        <path d="M 0 200 L 260 230 L 300 260 L 0 250 Z" fill="#e8c46a" opacity={0.6} />
        <text x={1500} y={160} fill="#fff4c9" fontFamily={MONO} fontWeight={700} fontSize={34}>WARM · ≈ 28 °C</text>
        <text x={1500} y={760} fill={C.cyan} fontFamily={MONO} fontWeight={700} fontSize={34}>COLD · A FEW °C</text>
        <GShark x={1150 + Math.sin(f * 0.02) * 40} y={640} s={0.8} f={f} />
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// An eye with the parasite, then the healthy rod-only retina.
export const EyeParasite: React.FC<{ retina?: boolean; text?: string }> = ({ retina = false, text }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: retina ? "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" : "radial-gradient(ellipse at 50% 45%, #3c3632 0%, #0c0a09 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {retina ? (
          <g>
            {Array.from({ length: 70 }, (_, i) => <rect key={i} x={240 + i * 21} y={380 + Math.sin(i) * 4} width={10} height={260} rx={5} fill={C.cyan} opacity={0.4 + 0.4 * Math.abs(Math.sin(i * 0.7 + f * 0.1))} />)}
            <text x={960} y={330} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={32}>RODS ONLY · NO CONES · STILL WORKING</text>
          </g>
        ) : (
          <g>
            <ellipse cx={960} cy={480} rx={300} ry={190} fill="#1c1a18" />
            <circle cx={960} cy={480} r={150} fill="#2a3a40" />
            <circle cx={960} cy={480} r={70} fill="#070909" />
            {[0, 1, 2, 3].map((i) => <line key={i} x1={880 + i * 30} y1={400} x2={920 + i * 25} y2={560} stroke="#8d9ba0" strokeWidth={3} opacity={0.6} />)}
            <path d={`M 990 470 C 1010 600 ${990 + Math.sin(f * 0.08) * 20} 700 ${980 + Math.sin(f * 0.08) * 30} 820`} stroke="#efe2d0" strokeWidth={22} strokeLinecap="round" fill="none" />
            <text x={1300} y={780} fill="#efe2d0" fontFamily={MONO} fontWeight={700} fontSize={28}>OMMATOKOITA · ≈ 3 CM</text>
          </g>
        )}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};
