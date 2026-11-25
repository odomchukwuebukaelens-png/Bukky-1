// Drawn shots for the leopard seal video: our own seal, the under-ice world and the ice edge,
// with the VFX layer (rays, snow, caustics, haze, drift) built in.
import React from "react";
import { AbsoluteFill, interpolate, random } from "remotion";
import { registerKind } from "../kit/edit-rules";
import { Backdrop, ease, Kicker, Label, pop, Svg, useShot } from "../kit/shots";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { MONO } from "../kit/hud";
import { Bubbles, Caustics, Drift, Haze, Rays, Snow } from "../kit/vfx";
import { Diver } from "../humpback/draw";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const BACK = "#4a545e";
const BELLY = "#c7ced2";
const SPOT = "#262d33";

// Leopard seal, side view, facing right. jaw 0..1 opens the mouth; the mouth corner curves up (the "smile").
export const Seal: React.FC<{ x: number; y: number; s?: number; flip?: boolean; rot?: number; jaw?: number; f?: number; opacity?: number; teeth?: boolean }> = ({
  x,
  y,
  s = 1,
  flip = false,
  rot = 0,
  jaw = 0,
  f = 0,
  opacity = 1,
  teeth = true,
}) => {
  const wave = Math.sin(f * 0.16) * 8;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`} opacity={opacity}>
      {/* rear flippers sweep side to side */}
      <g transform={`rotate(${wave} -460 0)`}>
        <path d="M -455 -12 C -500 -30 -540 -60 -575 -70 C -560 -35 -560 -10 -575 8 C -545 4 -505 2 -455 10 Z" fill={BACK} />
      </g>
      {/* body: long, slim, with the big reptilian head */}
      <path d="M 470 -6 C 452 -44 392 -66 318 -66 C 262 -66 222 -58 186 -66 C 80 -92 -140 -88 -300 -54 C -380 -38 -430 -22 -462 -8 L -462 12 C -400 42 -210 78 0 82 C 120 84 214 64 296 44 L 470 6 Z" fill={BACK} />
      <path d="M 296 44 C 214 64 120 84 0 82 C -210 78 -380 40 -440 14 C -330 30 -150 50 0 52 C 130 54 230 36 300 22 Z" fill={BELLY} />
      {Array.from({ length: 34 }, (_, i) => (
        <ellipse key={i} cx={-380 + random(`sx${i}`) * 640} cy={-40 + random(`sy${i}`) * 90} rx={5 + random(`sr${i}`) * 7} ry={3 + random(`sq${i}`) * 4} fill={SPOT} opacity={0.75} />
      ))}
      {/* fore flipper */}
      <g transform={`rotate(${Math.sin(f * 0.12) * 10} 170 40)`}>
        <path d="M 180 36 C 150 90 110 130 52 150 C 80 120 112 84 138 34 Z" fill={BACK} />
      </g>
      {/* mouth: corner curves up into the "smile"; lower jaw drops on a hinge */}
      <g transform={`rotate(${jaw * 34} 318 14)`}>
        <path d="M 318 14 L 466 8 C 456 30 420 42 330 40 Z" fill={BACK} />
        {teeth && jaw > 0.15 ? [350, 382, 414, 446].map((tx, i) => <path key={i} d={`M ${tx} 10 l 8 ${i === 3 ? -20 : -12} l 8 ${i === 3 ? 20 : 12} Z`} fill="#f2efe6" />) : null}
      </g>
      {jaw > 0.15 ? <path d={`M 318 12 L 466 6 C 440 ${10 + jaw * 30} 380 ${14 + jaw * 60} 330 ${16 + jaw * 40} Z`} fill="#5a1f28" /> : null}
      {teeth && jaw > 0.15 ? [356, 388, 420, 452].map((tx, i) => <path key={i} d={`M ${tx} 6 l 8 ${i === 3 ? 22 : 13} l 8 ${i === 3 ? -22 : -13} Z`} fill="#f2efe6" />) : null}
      <path d="M 466 6 C 420 10 360 14 322 12 C 312 10 306 2 302 -8" stroke="#14191d" strokeWidth={5} fill="none" strokeLinecap="round" />
      <ellipse cx={386} cy={-34} rx={10} ry={8} fill="#0c0f12" />
      <circle cx={389} cy={-37} r={2.5} fill="#cfd8dc" />
      <circle cx={460} cy={-14} r={3} fill="#0c0f12" />
    </g>
  );
};

const Penguin: React.FC<{ x: number; y: number; s?: number; f?: number; swim?: boolean }> = ({ x, y, s = 1, f = 0, swim = false }) => (
  <g transform={`translate(${x} ${y}) scale(${s}) rotate(${swim ? 80 : Math.sin(f * 0.2 + x) * 3})`}>
    <ellipse cx={0} cy={0} rx={22} ry={44} fill="#16191c" />
    <ellipse cx={4} cy={6} rx={14} ry={34} fill="#f2f4f5" />
    <circle cx={0} cy={-38} r={15} fill="#16191c" />
    <circle cx={6} cy={-41} r={3} fill="#fff" />
    <path d="M 12 -38 l 14 4 l -14 4 Z" fill="#e8742a" />
  </g>
);

// Under the ice: a jagged ice ceiling with an opening, rays, snow and caustics, and whatever is in the water.
export const UnderIce: React.FC<{
  seal?: { x0: number; x1?: number; y0: number; y1?: number; s0?: number; s1?: number; jaw0?: number; jaw1?: number; flip?: boolean; rot?: number; o0?: number; o1?: number };
  diver?: { x0: number; x1?: number; y0: number; y1?: number; s?: number; rot?: number; camera?: boolean };
  penguin?: { x0: number; x1?: number; y: number; dead?: boolean };
  prey?: { x0: number; x1?: number; y: number; s?: number };
  sealBubbles?: boolean;
  dark0?: number;
  dark1?: number;
  hole?: number;
  shake?: boolean;
  children?: React.ReactNode;
}> = ({ seal, diver, penguin, prey, sealBubbles = false, dark0 = 0.2, dark1, hole = 960, shake = false, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const dark = lerp(dark0, dark1 ?? dark0, e);
  const sh = shake ? Math.sin(f * 1.7) * 6 * Math.max(0, 1 - f / 18) : 0;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Drift amount={0.8} focus={false} seed={hole / 100}>
        <AbsoluteFill style={{ background: `linear-gradient(#2a7f99 0%, #0f4c62 ${32 - dark * 20}%, #052230 ${68 - dark * 30}%, #01080c 100%)`, transform: `translate(${sh}px, ${-sh}px)` }}>
          <Svg>
            {/* ice ceiling with an opening where the light comes in */}
            <path d={`M -50 -10 L 1970 -10 L 1970 ${120 + Math.sin(1) * 20} ${Array.from({ length: 30 }, (_, i) => `L ${1970 - i * 70} ${110 + random(`ic${i}`) * 90}`).join(" ")} L -50 150 Z`} fill="#b9dbe6" opacity={0.92} />
            <path d={`M ${hole - 150} -10 C ${hole - 120} 90 ${hole + 120} 90 ${hole + 150} -10 Z`} fill="#eaf9ff" />
            {Array.from({ length: 30 }, (_, i) => <path key={i} d={`M ${1970 - i * 70} ${110 + random(`ic${i}`) * 90} l -20 ${30 + random(`id${i}`) * 50} l -30 -40 Z`} fill="#9cc8d6" opacity={0.8} />)}
            {penguin ? <g transform={penguin.dead ? `rotate(25 ${lerp(penguin.x0, penguin.x1 ?? penguin.x0, e)} ${penguin.y})` : undefined}><Penguin x={lerp(penguin.x0, penguin.x1 ?? penguin.x0, e)} y={penguin.y} s={1.4} swim={!penguin.dead} f={f} /></g> : null}
            {prey ? <g opacity={0.95}><Seal x={lerp(prey.x0, prey.x1 ?? prey.x0, e)} y={prey.y + Math.sin(f * 0.1) * 6} s={prey.s ?? 0.45} f={f + 7} teeth={false} /></g> : null}
            {diver ? (
              <g>
                <Diver x={lerp(diver.x0, diver.x1 ?? diver.x0, e)} y={lerp(diver.y0, diver.y1 ?? diver.y0, e)} s={diver.s ?? 0.8} rot={diver.rot ?? 0} f={f} />
                {diver.camera ? <rect x={lerp(diver.x0, diver.x1 ?? diver.x0, e) + 70 * (diver.s ?? 0.8)} y={lerp(diver.y0, diver.y1 ?? diver.y0, e) - 40 * (diver.s ?? 0.8)} width={60 * (diver.s ?? 0.8)} height={40 * (diver.s ?? 0.8)} rx={6} fill="#222" stroke="#9ab" strokeWidth={3} /> : null}
              </g>
            ) : null}
            {seal ? (
              <Seal
                x={lerp(seal.x0, seal.x1 ?? seal.x0, e)}
                y={lerp(seal.y0, seal.y1 ?? seal.y0, e) + Math.sin(f * 0.07) * 6}
                s={lerp(seal.s0 ?? 1, seal.s1 ?? seal.s0 ?? 1, e)}
                jaw={lerp(seal.jaw0 ?? 0, seal.jaw1 ?? seal.jaw0 ?? 0, e)}
                flip={seal.flip}
                rot={seal.rot ?? 0}
                opacity={lerp(seal.o0 ?? 1, seal.o1 ?? seal.o0 ?? 1, e)}
                f={f}
              />
            ) : null}
          </Svg>
          {children}
        </AbsoluteFill>
      </Drift>
      {sealBubbles && seal ? <Bubbles streams={[lerp(seal.x0, seal.x1 ?? seal.x0, e) + (seal.flip ? -1 : 1) * 420 * lerp(seal.s0 ?? 1, seal.s1 ?? seal.s0 ?? 1, e)]} n={18} y0={lerp(seal.y0, seal.y1 ?? seal.y0, e)} /> : null}
      <Caustics opacity={0.1 * (1 - dark)} />
      <Rays strength={0.9 * (1 - dark)} from={hole} />
      <Snow n={80} />
      <Haze depth={dark} />
    </AbsoluteFill>
  );
};

// Above the water at the ice edge: the floe, penguins, and the seal's head breaking the surface.
export const IceEdge: React.FC<{ penguins?: number; head?: boolean; strike?: boolean; man?: boolean; manX?: [number, number]; chase?: boolean; sink?: boolean; flash?: boolean; z0?: number; z1?: number; zx?: number; zy?: number; children?: React.ReactNode }> = ({
  penguins = 4,
  head = false,
  strike = false,
  man = false,
  manX = [300, 700],
  chase = false,
  sink = false,
  flash = false,
  z0 = 1,
  z1 = 1.06,
  zx = 960,
  zy = 560,
  children,
}) => {
  const { f, k } = useShot();
  const e = ease(k);
  const z = lerp(z0, z1, e);
  const WL = 600;
  const up = strike ? Math.sin(Math.min(1, k * 1.4) * Math.PI) : sink ? 1 - Math.min(1, k * 1.5) : head ? Math.min(1, k * 2) : 0;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Drift amount={0.4} focus={false}>
        <AbsoluteFill style={{ transform: `translate(${960 - zx * z}px, ${540 - zy * z}px) scale(${z})`, transformOrigin: "0 0" }}>
          <div style={{ position: "absolute", left: -300, top: -300, width: 2520, height: WL + 300, background: "linear-gradient(#8fa9bb 0%, #cddbe3 80%, #e8eff3 100%)" }} />
          <Svg>
            <rect x={-300} y={WL} width={2520} height={800} fill="#1f4d60" />
            {Array.from({ length: 30 }, (_, i) => <rect key={i} x={((random(`ew${i}`) * 2400 + f * 0.8) % 2500) - 300} y={WL + 10 + random(`eh${i}`) * 460} width={80 + random(`el${i}`) * 140} height={4} fill="#d2e6ee" opacity={0.18} />)}
            <path d={`M -300 ${WL + 6} L 900 ${WL + 6} L 980 ${WL - 10} L 1000 ${WL + 40} L -300 ${WL + 40} Z`} fill="#f4fafc" />
            <path d={`M -300 ${WL - 70} L 860 ${WL - 74} L 960 ${WL - 12} L 900 ${WL + 8} L -300 ${WL + 8} Z`} fill="#e4f1f6" />
            {Array.from({ length: penguins }, (_, i) => <Penguin key={i} x={560 + i * 90} y={WL - 120 + (i % 2) * 6} f={f + i * 5} />)}
            {chase ? <g transform={`translate(${lerp(manX[0] - 420, manX[1] - 260, e)} ${WL - 40})`}><Seal x={0} y={0} s={0.42} f={f * 2} /></g> : null}
            {head || strike || sink ? (
              <g transform={`translate(1180 ${WL + 40 - up * 170}) rotate(-62)`}>
                <Seal x={0} y={0} s={0.55} jaw={strike ? up * 0.9 : 0.05} f={f} />
              </g>
            ) : null}
            {man ? (
              <g transform={`translate(${lerp(manX[0], manX[1], e)} ${WL - 70})`}>
                <circle cx={0} cy={-150} r={22} fill="#2b2b2b" />
                <rect x={-24} y={-128} width={48} height={90} rx={14} fill="#5a4630" />
                <rect x={-20} y={-40} width={16} height={60} fill="#3a2e20" />
                <rect x={4} y={-40} width={16} height={60} fill="#3a2e20" />
              </g>
            ) : null}
            {Array.from({ length: 16 }, (_, i) => {
              const t = ((f / 40 + i / 16) % 1 + 1) % 1;
              return up > 0.3 ? <circle key={i} cx={1150 + (random(`sp${i}`) - 0.5) * 300 * t} cy={WL - random(`sq${i}`) * 200 * Math.sin(t * Math.PI)} r={5 + random(`ss${i}`) * 8} fill="#eef7fa" opacity={0.8} /> : null;
            })}
          </Svg>
          {children}
        </AbsoluteFill>
      </Drift>
      <Snow n={40} opacity={0.6} seed="ie" />
      {flash ? <AbsoluteFill style={{ background: "#fff", opacity: Math.max(0, 1 - Math.abs(f - 12) / 5) }} /> : null}
    </AbsoluteFill>
  );
};

// The seal beside familiar things: a diver, or a horse, with a measured line.
export const SealScale: React.FC<{ vs: "diver" | "horse"; title: string }> = ({ vs, title }) => {
  const { f } = useShot();
  const g = ease(f / 14);
  return (
    <Backdrop v="deep">
      <Svg>
        {vs === "horse" ? (
          <g transform="translate(1450 820) scale(1.25)" fill="rgba(127,233,255,0.85)">
            <ellipse cx={0} cy={-150} rx={150} ry={70} />
            <path d="M 110 -190 L 190 -320 L 240 -300 L 170 -170 Z" />
            <ellipse cx={225} cy={-315} rx={50} ry={28} />
            {[-110, -60, 70, 120].map((lx) => <rect key={lx} x={lx} y={-100} width={24} height={100} rx={10} />)}
          </g>
        ) : (
          <Diver x={1450} y={560} s={0.9} f={f} />
        )}
        <Seal x={700 - (1 - g) * 200} y={vs === "horse" ? 700 : 560} s={1.05} f={f} />
        <line x1={190} y1={vs === "horse" ? 880 : 700} x2={190 + 1100 * g} y2={vs === "horse" ? 880 : 700} stroke={C.accent} strokeWidth={8} />
      </Svg>
      <Label text={title} x={190} y={vs === "horse" ? 900 : 720} size={40} color={C.accent} />
    </Backdrop>
  );
};

// Close-up of the jaws closing around a camera.
export const JawsCam: React.FC = () => {
  const { f, k } = useShot();
  const jaw = interpolate(k, [0, 0.45, 1], [0.95, 1, 0.25], clamp);
  return (
    <UnderIce dark0={0.45} shake>
      <Svg>
        <g transform="translate(860 560)">
          <Seal x={0} y={0} s={2.4} jaw={jaw} f={f} />
        </g>
        <rect x={1720 + Math.sin(f * 0.4) * 6} y={560} width={150} height={100} rx={12} fill="#1b1f22" stroke="#9ab" strokeWidth={5} />
        <circle cx={1750} cy={610} r={30} fill="#0a0d10" stroke="#7fe9ff" strokeWidth={5} />
      </Svg>
    </UnderIce>
  );
};

// A big line of text over darkness, for the date cards in the cold open.
export const Dateline: React.FC<{ text: string; sub?: string }> = ({ text, sub }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0c3343 0%, #02090d 75%)" }}>
      <Snow n={50} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 380, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 170, color: C.white, opacity: pop(f, 1, 8), letterSpacing: 6, textShadow: "0 10px 40px rgba(0,0,0,0.9)" }}>{text}</div>
      {sub ? <div style={{ position: "absolute", left: 0, right: 0, top: 580, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 36, color: "rgba(127,233,255,0.85)", letterSpacing: 6, opacity: pop(f, 6) }}>{sub}</div> : null}
    </AbsoluteFill>
  );
};

registerKind("drawn", UnderIce, IceEdge, JawsCam);
registerKind("graphic", SealScale);
registerKind("title", Dateline);

export { Kicker, Bubbles, lerp };
