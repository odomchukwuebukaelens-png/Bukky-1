// Drawn scenes for "The Orcas That Started Sinking Boats": a sailing yacht with its keel and rudder,
// orcas, the Strait of Gibraltar map, the tuna chase, research ID cards and the story's props.
// Our own flat style: deep teal water, yellow accent, white hulls.
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
const BLACK = "#0a0d11";
const WHITE = "#eef3f5";
const SADDLE = "#8d979e";

// ---------- Animals ----------

// An orca from the side, facing right, about 700 px long at s = 1. f drives the tail beat.
export const Orca: React.FC<{ x: number; y: number; s?: number; flip?: boolean; rot?: number; f?: number; fin?: number; open?: number }> = ({ x, y, s = 1, flip = false, rot = 0, f = 0, fin = 1, open = 0 }) => {
  const beat = Math.sin(f * 0.22) * 9;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`}>
      <g transform={`rotate(${beat} -340 0)`}>
        <path d="M -330 0 C -370 -14 -410 -50 -450 -62 C -430 -30 -420 -10 -410 0 C -420 10 -430 30 -450 62 C -410 50 -370 14 -330 0 Z" fill={BLACK} />
      </g>
      <path d={`M -10 -82 C -16 ${-82 - 70 * fin} -36 ${-82 - 120 * fin} -64 ${-82 - 150 * fin} C -36 ${-82 - 148 * fin} -2 ${-82 - 110 * fin} 34 ${-82 - 64 * fin} C 50 -110 66 -92 80 -80 Z`} fill={BLACK} />
      <path d={`M 262 ${open * 6} C 258 -40 200 -72 120 -80 C 20 -90 -120 -82 -220 -50 C -280 -32 -310 -14 -340 -6 L -340 6 C -310 14 -270 32 -210 46 C -100 72 60 72 160 58 C 220 48 258 ${30 + open * 10} 262 ${open * 6} Z`} fill={BLACK} />
      {open > 0 ? <path d={`M 262 0 L 150 ${8 + open * 4} L 262 ${open * 22} Z`} fill="#5a1d1d" /> : null}
      <ellipse cx={-60} cy={-74} rx={80} ry={13} fill={SADDLE} opacity={0.75} />
      <ellipse cx={152} cy={-36} rx={38} ry={13} transform="rotate(-8 152 -36)" fill={WHITE} />
      <path d="M 236 24 C 180 54 60 64 -40 54 C -110 48 -170 44 -200 48 C -150 30 -60 32 20 30 C 100 28 170 24 236 24 Z" fill={WHITE} />
      <path d="M -110 44 C -140 4 -196 -8 -240 2 C -206 24 -160 44 -110 44 Z" fill={WHITE} />
      <ellipse cx={96} cy={48} rx={44} ry={17} transform="rotate(28 96 48)" fill={BLACK} />
    </g>
  );
};

// An orca from above, pointing along its heading (degrees, 0 = right).
export const OrcaTop: React.FC<{ x: number; y: number; s?: number; h?: number; f?: number }> = ({ x, y, s = 1, h = 0, f = 0 }) => (
  <g transform={`translate(${x} ${y}) rotate(${h}) scale(${s})`}>
    <g transform={`rotate(${Math.sin(f * 0.22) * 10} -150 0)`}>
      <path d="M -150 0 L -210 -46 C -200 -20 -196 -8 -190 0 C -196 8 -200 20 -210 46 Z" fill={BLACK} />
    </g>
    <ellipse cx={0} cy={0} rx={160} ry={40} fill={BLACK} />
    <path d="M 40 -34 L 90 -80 L 70 -30 Z M 40 34 L 90 80 L 70 30 Z" fill={BLACK} />
    <ellipse cx={-30} cy={0} rx={40} ry={16} fill={SADDLE} opacity={0.8} />
    <line x1={-10} y1={0} x2={30} y2={0} stroke="#000" strokeWidth={6} />
  </g>
);

// Atlantic bluefin tuna, facing right, about 360 px long at s = 1.
export const Tuna: React.FC<{ x: number; y: number; s?: number; flip?: boolean; rot?: number; f?: number }> = ({ x, y, s = 1, flip = false, rot = 0, f = 0 }) => (
  <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`}>
    <g transform={`rotate(${Math.sin(f * 0.5) * 12} -150 0)`}>
      <path d="M -150 0 L -200 -70 L -180 0 L -200 70 Z" fill="#26364a" />
    </g>
    <path d="M 180 4 C 170 -40 90 -64 0 -64 C -80 -62 -130 -30 -160 0 C -130 30 -80 56 0 58 C 90 58 170 40 180 4 Z" fill="#9fb4c4" />
    <path d="M 180 4 C 170 -40 90 -64 0 -64 C -80 -62 -130 -30 -160 0 C -100 -8 0 -12 176 -2 Z" fill="#1f3550" />
    <path d="M 10 -62 L -30 -110 L -50 -58 Z" fill="#1f3550" />
    {[0, 1, 2, 3, 4, 5].map((i) => <path key={i} d={`M ${-60 - i * 16} -44 l -8 -14 l -6 16 Z M ${-60 - i * 16} 42 l -8 14 l -6 -16 Z`} fill="#e8c23a" />)}
    <circle cx={140} cy={-10} r={9} fill="#111" />
    <circle cx={142} cy={-12} r={3} fill="#fff" />
  </g>
);

// ---------- Boats ----------

export type BoatProps = {
  x: number;
  y: number;
  s?: number;
  rot?: number;
  rud?: number; // rudder angle in degrees
  damage?: "none" | "holes" | "split" | "gone";
  engine?: boolean;
  f?: number;
  kind?: "yacht" | "schooner";
  flipY?: number; // 1 upright, -1 upside down
  sails?: boolean;
};

// A 12-metre sailing yacht in profile, bow to the right, waterline at y = 0 (local). Keel, spade rudder and propeller below.
export const Yacht: React.FC<BoatProps> = ({ x, y, s = 1, rot = 0, rud = 0, damage = "none", engine = false, f = 0, kind = "yacht", flipY = 1, sails = true }) => {
  const wood = kind === "schooner";
  const hull = wood ? "#7a4a2a" : "#f2f5f7";
  const cos = Math.max(0.12, Math.abs(Math.cos((rud * Math.PI) / 180)));
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s} ${s * flipY})`}>
      {/* mast and sails */}
      {wood ? (
        <>
          <line x1={110} y1={-60} x2={110} y2={-470} stroke="#4a3020" strokeWidth={9} />
          <line x1={-80} y1={-56} x2={-80} y2={-520} stroke="#4a3020" strokeWidth={10} />
          {sails ? (
            <>
              <path d="M 106 -450 L 106 -90 L -40 -90 L 20 -420 Z" fill="#e8dcc0" />
              <path d="M -84 -500 L -84 -90 L -220 -90 L -150 -470 Z" fill="#e8dcc0" />
              <path d="M 114 -440 L 250 -66 L 120 -80 Z" fill="#efe6cf" />
            </>
          ) : null}
        </>
      ) : (
        <>
          <line x1={40} y1={-60} x2={40} y2={-560} stroke="#9aa6ad" strokeWidth={8} />
          <line x1={40} y1={-110} x2={-200} y2={-104} stroke="#9aa6ad" strokeWidth={7} />
          {sails ? (
            <>
              <path d="M 34 -545 L 34 -114 L -196 -110 Z" fill="#f7f9fa" stroke="#c9d3d8" strokeWidth={2} />
              <path d="M 46 -520 L 246 -64 L 60 -84 Z" fill="#eef2f4" stroke="#c9d3d8" strokeWidth={2} />
            </>
          ) : null}
          <path d="M -70 -56 L -60 -90 L 120 -94 L 140 -60 Z" fill="#dfe6ea" />
          {[0, 1, 2].map((i) => <rect key={i} x={-30 + i * 50} y={-84} width={30} height={12} rx={4} fill="#26343c" />)}
        </>
      )}
      {/* hull */}
      <path d="M -240 -44 L 252 -60 C 244 -20 200 22 120 30 L -196 28 C -228 22 -240 0 -240 -44 Z" fill={hull} />
      <path d={`M -240 -30 L 250 -46`} stroke={wood ? "#3c2414" : C.accent} strokeWidth={wood ? 6 : 8} />
      <path d="M -238 -6 C -236 14 -222 24 -196 28 L 120 30 C 190 24 232 -4 246 -30 L -238 -6 Z" fill={wood ? "#5c3820" : "#25323a"} opacity={0.9} />
      {/* keel */}
      {wood ? <path d="M -180 26 L 160 28 L 120 64 L -160 62 Z" fill="#4a2d18" /> : (
        <>
          <path d="M 40 28 L 0 28 L -18 170 L 30 170 Z" fill="#2c3a42" />
          <ellipse cx={6} cy={172} rx={46} ry={13} fill="#2c3a42" />
        </>
      )}
      {/* propeller */}
      {!wood ? (
        <g transform="translate(-120 46)">
          <line x1={0} y1={-18} x2={0} y2={0} stroke="#56646c" strokeWidth={6} />
          <g transform={`scale(1 ${engine ? Math.cos(f * 1.4) : 1})`}>
            <ellipse cx={0} cy={0} rx={5} ry={20} fill="#b08a3c" />
          </g>
        </g>
      ) : null}
      {/* spade rudder */}
      {!wood && damage !== "gone" ? (
        <g transform={`translate(-188 28) scale(${cos} 1)`}>
          <rect x={-3} y={-6} width={6} height={14} fill="#56646c" />
          <path d={damage === "split" ? "M -10 4 L 22 4 L 18 54 L 6 62 L -4 50 L -14 58 Z" : "M -10 4 L 22 4 L 16 120 L -24 120 Z"} fill="#e9edef" stroke="#aab5bb" strokeWidth={2} />
          {damage === "holes" ? (
            <>
              <circle cx={2} cy={40} r={7} fill="#0b1c24" />
              <circle cx={-4} cy={78} r={8} fill="#0b1c24" />
            </>
          ) : null}
        </g>
      ) : null}
      {wood ? <path d="M -238 0 L -262 4 L -258 60 L -230 56 Z" fill="#4a2d18" /> : null}
    </g>
  );
};

// A tanker or cargo ship in profile, bow right, waterline at y = 0.
export const Ship: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M -600 -60 L 600 -60 L 560 30 L -580 30 Z" fill="#7d2b2b" />
    <rect x={-600} y={-80} width={1200} height={22} fill="#2f3b44" />
    <rect x={-560} y={-200} width={140} height={120} fill="#e9edef" />
    <rect x={-540} y={-240} width={60} height={40} fill="#c64633" />
    {[0, 1, 2, 3, 4].map((i) => <rect key={i} x={-380 + i * 190} y={-120} width={160} height={40} fill={["#3a6ea5", "#c98b2b", "#5a8a4a", "#b23b3b", "#3a6ea5"][i]} />)}
  </g>
);

// ---------- The sea in profile: sky above, water below ----------

export type Mover = { x0: number; y0: number; x1?: number; y1?: number; s?: number; s1?: number; flip?: boolean; rot?: number; rot1?: number; o0?: number; o1?: number; fin?: number; open?: number };

export const Sea: React.FC<{
  surf?: number;
  sky?: "day" | "dusk" | "night" | "grey";
  boat?: Partial<BoatProps> & { x0?: number; x1?: number; y0?: number; y1?: number; rot1?: number; rud1?: number; wobble?: number; flip1?: number };
  orcas?: Mover[];
  tuna?: Mover[];
  ship?: { x: number; s?: number };
  cam?: { x: number; y: number; z0: number; z1?: number };
  shake?: boolean;
  bubbles?: { x: number; y: number }[];
  flash?: { x: number; y: number; at?: number };
  line?: { x: number; y1: number; tuna?: boolean };
  dinghy?: { x: number; people?: number };
  children?: React.ReactNode;
}> = ({ surf = 470, sky = "day", boat, orcas = [], tuna = [], ship, cam, shake = false, bubbles = [], flash, line, dinghy, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const SKY = { day: ["#5fa8d3", "#bfe0ee"], dusk: ["#2b2a4a", "#d9845a"], night: ["#05080f", "#1a2638"], grey: ["#6f7f8a", "#b7c2c8"] }[sky];
  const z = cam ? lerp(cam.z0, cam.z1, e) : 1;
  const cx = cam ? cam.x : 960;
  const cy = cam ? cam.y : 540;
  const jit = shake ? Math.sin(f * 2.1) * 10 * Math.max(0, 1 - Math.abs(k - 0.4) * 3) : 0;
  const wob = boat?.wobble ?? 0;
  const bx = lerp(boat?.x0 ?? 960, boat?.x1, e) + (boat?.x0 === undefined ? 0 : 0);
  const by = lerp(boat?.y0 ?? surf, boat?.y1, e);
  const brot = lerp(boat?.rot ?? 0, boat?.rot1, e) + Math.sin(f * 0.12) * 1.2 + Math.sin(f * 1.3) * wob;
  const brud = lerp(boat?.rud ?? 0, boat?.rud1, e) + Math.sin(f * 0.9) * wob * 6;
  const bflip = lerp(boat?.flipY ?? 1, boat?.flip1, ease((k - 0.3) / 0.6));
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={SKY[0]} />
            <stop offset="1" stopColor={SKY[1]} />
          </linearGradient>
          <linearGradient id="seag" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={sky === "night" ? "#0a2a3a" : "#1d7f9a"} />
            <stop offset="0.5" stopColor={sky === "night" ? "#051620" : "#0d4b62"} />
            <stop offset="1" stopColor="#031822" />
          </linearGradient>
        </defs>
        <g transform={`translate(${960 + jit} ${540}) scale(${z}) translate(${-cx} ${-cy})`}>
          <rect x={-3000} y={-3000} width={8000} height={3000 + surf} fill="url(#skyg)" />
          {sky === "dusk" ? <circle cx={1500} cy={surf - 60} r={70} fill="#ffcf7a" opacity={0.85} /> : null}
          <rect x={-3000} y={surf} width={8000} height={6000} fill="url(#seag)" />
          {[0, 1, 2, 3, 4].map((i) => (
            <polygon key={i} points={`${300 + i * 330 + Math.sin(f * 0.03 + i) * 40},${surf} ${420 + i * 330},${surf} ${200 + i * 300},${surf + 900} ${80 + i * 300},${surf + 900}`} fill="#bff3ff" opacity={sky === "night" ? 0.02 : 0.06} />
          ))}
          {ship ? <Ship x={ship.x - 400 * e * 0.3} y={surf} s={ship.s ?? 0.6} /> : null}
          {line ? (
            <g>
              <line x1={line.x} y1={surf - 40} x2={line.x} y2={line.y1} stroke="#e8eef0" strokeWidth={2} />
              {line.tuna ? <Tuna x={line.x + 10} y={line.y1 + 30} s={0.5} rot={80} f={f} /> : null}
              <path d={`M ${line.x - 120} ${surf - 10} L ${line.x + 140} ${surf - 14} L ${line.x + 110} ${surf + 30} L ${line.x - 100} ${surf + 30} Z`} fill="#3d78a8" />
              <rect x={line.x - 30} y={surf - 70} width={70} height={60} fill="#e9edef" />
            </g>
          ) : null}
          {boat ? <Yacht x={bx} y={by} s={boat.s ?? 1} rot={brot} rud={brud} damage={boat.damage} engine={boat.engine} f={f} kind={boat.kind} flipY={bflip} sails={boat.sails} /> : null}
          {dinghy ? (
            <g transform={`translate(${dinghy.x} ${surf + Math.sin(f * 0.1) * 4}) scale(2.2)`}>
              {Array.from({ length: dinghy.people ?? 6 }, (_, i) => <circle key={i} cx={-60 + i * 24} cy={-34} r={11} fill="#2a2a2a" />)}
              <path d="M -90 -20 L 90 -20 L 70 10 L -74 10 Z" fill="#d8c9a6" />
            </g>
          ) : null}
          {tuna.map((m, i) => (
            <Tuna key={i} x={lerp(m.x0, m.x1, e)} y={lerp(m.y0, m.y1, e)} s={lerp(m.s ?? 1, m.s1, e)} flip={m.flip} rot={lerp(m.rot ?? 0, m.rot1, e)} f={f + i * 7} />
          ))}
          {orcas.map((m, i) => (
            <g key={i} opacity={lerp(m.o0 ?? 1, m.o1, e)}>
              <Orca x={lerp(m.x0, m.x1, e)} y={lerp(m.y0, m.y1, e)} s={lerp(m.s ?? 0.6, m.s1, e)} flip={m.flip} rot={lerp(m.rot ?? 0, m.rot1, e)} f={f + i * 11} fin={m.fin} open={m.open} />
            </g>
          ))}
          {/* water in front: tints what is under the surface */}
          <rect x={-3000} y={surf} width={8000} height={6000} fill="#06455c" opacity={0.28} />
          <path d={`M -3000 ${surf} ${Array.from({ length: 60 }, (_, i) => `L ${-3000 + i * 140} ${surf + Math.sin(i * 1.3 + f * 0.15) * 5}`).join(" ")} L 5000 ${surf}`} stroke="#d9f4ff" strokeWidth={4} fill="none" opacity={0.8} />
          {bubbles.map((b, i) =>
            Array.from({ length: 8 }, (_, j) => {
              const t = ((f * 0.03 + j / 8 + i * 0.37) % 1 + 1) % 1;
              return <circle key={`${i}-${j}`} cx={b.x + Math.sin(j * 3 + f * 0.1) * 14} cy={b.y - t * (b.y - surf)} r={4 + (j % 3) * 3} fill="none" stroke="#d9f4ff" strokeWidth={2} opacity={1 - t} />;
            })
          )}
          {flash ? (() => {
            const t = (f - (flash.at ?? 10)) / 14;
            if (t < 0 || t > 1) return null;
            return (
              <g opacity={1 - t}>
                <circle cx={flash.x} cy={flash.y} r={30 + 160 * t} fill="#fff6c0" opacity={0.7} />
                {Array.from({ length: 10 }, (_, j) => (
                  <line key={j} x1={flash.x} y1={flash.y} x2={flash.x + Math.cos(j * 0.63) * 200 * t} y2={flash.y + Math.sin(j * 0.63) * 200 * t} stroke="#ffd23f" strokeWidth={5} />
                ))}
              </g>
            );
          })() : null}
        </g>
      </svg>
      {children}
    </AbsoluteFill>
  );
};

// ---------- From above ----------

export const TopView: React.FC<{ h0?: number; h1?: number; orcas?: { r: number; a0: number; a1?: number; s?: number }[]; wake?: boolean; spin?: boolean; children?: React.ReactNode; z?: number }> = ({ h0 = -10, h1, orcas = [], wake = true, spin = false, children, z = 1 }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const h = spin ? h0 + 300 * e : lerp(h0, h1, e);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #1a7a95 0%, #0b4357 60%, #062a38 100%)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 40 }, (_, i) => {
          const x = (random(`w${i}`) * 2200 - 140 + f * 1.2) % 2100;
          const y = random(`v${i}`) * 1080;
          return <path key={i} d={`M ${x} ${y} q 30 -10 60 0`} stroke="#bfefff" strokeWidth={3} fill="none" opacity={0.25} />;
        })}
        <g transform={`translate(960 520) scale(${z})`}>
          {wake && !spin ? <path d={`M -200 0 L -900 -140 L -900 140 Z`} transform={`rotate(${h})`} fill="#e9fbff" opacity={0.18} /> : null}
          {spin ? <circle r={300} fill="none" stroke="#e9fbff" strokeWidth={14} opacity={0.18} strokeDasharray="60 40" /> : null}
          {orcas.map((o, i) => {
            const a = lerp(o.a0, o.a1, e) + h;
            const rad = (a * Math.PI) / 180;
            return <OrcaTop key={i} x={Math.cos(rad) * o.r} y={Math.sin(rad) * o.r} h={a + 90} s={o.s ?? 0.6} f={f + i * 9} />;
          })}
          <g transform={`rotate(${h})`}>
            <path d="M 250 0 C 200 -70 40 -90 -200 -80 L -230 -70 L -230 70 L -200 80 C 40 90 200 70 250 0 Z" fill="#f2f5f7" stroke="#c9d3d8" strokeWidth={4} />
            <path d="M -60 -50 L 110 -40 C 140 -20 140 20 110 40 L -60 50 Z" fill="#dfe6ea" />
            <line x1={40} y1={0} x2={-220} y2={0} stroke="#9aa6ad" strokeWidth={8} />
            <circle cx={40} cy={0} r={12} fill="#9aa6ad" />
            <circle cx={-170} cy={0} r={26} fill="none" stroke="#56646c" strokeWidth={6} />
          </g>
        </g>
      </svg>
      {children}
    </AbsoluteFill>
  );
};

// ---------- Close-up under the stern: the rudder and an orca ----------

export const Rudder: React.FC<{ mode: "push" | "bite" | "marks" | "split" | "gone" | "holes" | "still"; orca?: boolean; label?: string }> = ({ mode, orca = true, label }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const ang = mode === "push" || mode === "bite" ? Math.sin(f * 0.35) * 55 : mode === "still" ? 0 : 20;
  const cos = Math.max(0.1, Math.abs(Math.cos((ang * Math.PI) / 180)));
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#11617a, #062a38)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {[0, 1, 2, 3].map((i) => <polygon key={i} points={`${400 + i * 380},0 ${520 + i * 380},0 ${300 + i * 380},1080 ${180 + i * 380},1080`} fill="#bff3ff" opacity={0.05} />)}
        <path d="M -100 0 L 2100 0 L 2100 170 C 1400 230 600 230 -100 190 Z" fill="#25323a" />
        <g transform={`translate(1060 200) scale(${cos * 2.4} 2.4)`}>
          <rect x={-5} y={-30} width={10} height={36} fill="#56646c" />
          {mode !== "gone" ? (
            <path d={mode === "split" ? "M -24 4 L 40 4 L 34 120 L 10 136 L -4 116 L -26 132 Z" : "M -24 4 L 40 4 L 30 250 L -46 250 Z"} fill="#e9edef" stroke="#aab5bb" strokeWidth={2} />
          ) : (
            <path d="M -8 4 L 8 4 L 6 30 L -2 22 L -8 34 Z" fill="#56646c" />
          )}
          {mode === "marks" || mode === "split" ? [0, 1, 2, 3, 4].map((i) => <line key={i} x1={-20 + i * 2} y1={60 + i * 14} x2={30 - i * 3} y2={50 + i * 16} stroke="#7d8a90" strokeWidth={2.5} opacity={ease(k * 3 - i * 0.3)} />) : null}
          {mode === "holes" ? (
            <>
              <circle cx={4} cy={80} r={11 * pop(f, 6)} fill="#06202a" />
              <circle cx={-6} cy={160} r={12 * pop(f, 14)} fill="#06202a" />
            </>
          ) : null}
        </g>
        {orca ? (
          <Orca
            x={mode === "bite" ? 860 + 30 * Math.sin(f * 0.35) : mode === "gone" ? 700 - 500 * e : 700 + Math.sin(f * 0.35) * 60}
            y={mode === "gone" ? 760 : 640}
            s={1.15}
            rot={mode === "bite" ? -22 : -14}
            f={f}
            open={mode === "bite" ? 1 : 0}
          />
        ) : null}
        {mode === "gone" ? <g transform={`translate(${720 - 500 * e} ${560}) rotate(${-30 + 40 * e}) scale(1.6)`}><path d="M -24 4 L 40 4 L 30 150 L -46 150 Z" fill="#e9edef" /></g> : null}
      </svg>
      {label ? <div style={{ position: "absolute", left: 0, right: 0, top: 120, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.accent, textShadow: SHADOW }}>{label}</div> : null}
    </AbsoluteFill>
  );
};

// The cockpit wheel turning on its own.
export const Helm: React.FC<{ rot0?: number; rot1?: number; jerk?: boolean; text?: string }> = ({ rot0 = 0, rot1 = 140, jerk = true, text }) => {
  const { f, k } = useShot();
  const r = lerp(rot0, rot1, ease(k)) + (jerk ? Math.sin(f * 0.9) * 12 : 0);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #6fa9c6 0%, #2b5a70 70%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <rect x={0} y={760} width={1920} height={320} fill="#c9b48a" />
        {Array.from({ length: 16 }, (_, i) => <line key={i} x1={i * 130} y1={760} x2={i * 130 - 200} y2={1080} stroke="#a89064" strokeWidth={4} />)}
        <rect x={930} y={560} width={60} height={240} fill="#56646c" />
        <g transform={`translate(960 470) rotate(${r})`}>
          <circle r={300} fill="none" stroke="#2c3a42" strokeWidth={34} />
          <circle r={300} fill="none" stroke="#7d8a90" strokeWidth={8} />
          {[0, 1, 2, 3, 4, 5].map((i) => <line key={i} x1={0} y1={0} x2={Math.cos((i * Math.PI) / 3) * 300} y2={Math.sin((i * Math.PI) / 3) * 300} stroke="#2c3a42" strokeWidth={16} />)}
          <circle r={50} fill="#2c3a42" />
          <rect x={-10} y={-318} width={20} height={36} fill={C.red} />
        </g>
      </svg>
      {text ? <div style={{ position: "absolute", left: 0, right: 0, top: 70, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{text}</div> : null}
    </AbsoluteFill>
  );
};

// ---------- The Strait of Gibraltar map ----------

const IBERIA: [number, number][] = [
  [-5.35, 36.14], [-5.6, 36.01], [-5.92, 36.19], [-6.3, 36.53], [-6.43, 36.8], [-6.95, 37.18], [-7.42, 37.18], [-7.9, 37.0], [-8.6, 37.1], [-8.99, 37.02],
  [-8.8, 37.5], [-8.87, 37.95], [-8.82, 38.3], [-9.2, 38.42], [-9.2, 38.6], [-9.42, 38.69], [-9.5, 38.78], [-9.4, 39.05], [-9.38, 39.36], [-9.0, 39.75],
  [-8.85, 40.2], [-8.67, 41.15], [-8.83, 41.69], [-8.87, 41.87], [-8.9, 42.1], [-9.05, 42.55], [-9.27, 42.88], [-9.2, 43.2], [-8.4, 43.38], [-7.7, 43.75],
  [-7.0, 43.55], [-5.8, 43.6], [-4.0, 43.45], [-3.0, 43.42], [-1.8, 43.38], [-1.4, 44.2], [-1.2, 46.5], [8, 46.5], [8, 43.6], [6, 43.1], [4.5, 43.45],
  [3.1, 43.1], [3.2, 42.4], [3.2, 41.9], [2.2, 41.4], [0.9, 41.0], [0.0, 39.9], [-0.3, 39.4], [0.2, 38.8], [-0.5, 38.3], [-0.98, 37.6], [-1.7, 37.2],
  [-2.1, 36.73], [-2.9, 36.75], [-4.4, 36.72], [-5.0, 36.45],
];
const AFRICA: [number, number][] = [
  [-11, 28], [-9.8, 30.5], [-9.8, 31.5], [-9.25, 32.3], [-8.5, 33.3], [-7.6, 33.6], [-6.8, 34.05], [-6.2, 35.1], [-5.92, 35.79], [-5.8, 35.78],
  [-5.5, 35.9], [-5.32, 35.9], [-5.3, 35.6], [-4.9, 35.3], [-4.0, 35.2], [-3.0, 35.25], [-2.0, 35.1], [-1.2, 35.5], [0, 35.9], [1.0, 36.5], [3, 36.8], [8, 37], [8, 28],
];
const ISLANDS: [number, number][][] = [
  [[2.35, 39.6], [3.2, 39.95], [3.45, 39.55], [2.8, 39.3]],
  [[3.8, 40.0], [4.3, 39.95], [4.1, 39.82]],
  [[1.2, 38.9], [1.6, 39.1], [1.6, 38.85]],
];

export type Pin = { lon: number; lat: number; label: string; color?: string; at?: number; side?: 1 | -1 };

export const StraitMap: React.FC<{
  cx?: number;
  cy?: number;
  z0?: number;
  z1?: number;
  pins?: Pin[];
  route?: [number, number][];
  ships?: boolean;
  labels?: boolean;
  title?: string;
  arrow?: { from: [number, number]; to: [number, number]; color?: string };
  width?: boolean;
}> = ({ cx = -6, cy = 38.5, z0 = 1, z1 = 1.08, pins = [], route, ships = false, labels = true, title, arrow, width = false }) => {
  const { f, k } = useShot();
  const z = lerp(z0, z1, ease(k));
  const K = 150 * z;
  const X = (lon: number) => 960 + (lon - cx) * K * 0.82;
  const Y = (lat: number) => 540 - (lat - cy) * K;
  const poly = (pts: [number, number][]) => pts.map(([lo, la]) => `${X(lo)},${Y(la)}`).join(" ");
  const prog = ease(f / 40);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0f4050 0%, #06202a 75%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 30 }, (_, i) => <line key={i} x1={X(-16 + i)} y1={0} x2={X(-16 + i)} y2={1080} stroke="rgba(127,233,255,0.06)" strokeWidth={2} />)}
        {Array.from({ length: 20 }, (_, i) => <line key={i} x1={0} y1={Y(28 + i)} x2={1920} y2={Y(28 + i)} stroke="rgba(127,233,255,0.06)" strokeWidth={2} />)}
        <polygon points={poly(AFRICA)} fill="#2a4f4a" stroke="#5f9a8c" strokeWidth={3} />
        <polygon points={poly(IBERIA)} fill="#2a4f4a" stroke="#5f9a8c" strokeWidth={3} />
        {ISLANDS.map((p, i) => <polygon key={i} points={poly(p)} fill="#2a4f4a" stroke="#5f9a8c" strokeWidth={2} />)}
        {labels ? (
          <>
            <text x={X(-4.2)} y={Y(40)} fill="rgba(255,255,255,0.45)" fontFamily={FONT} fontWeight={800} fontSize={Math.min(90, 30 * z)} letterSpacing={6}>SPAIN</text>
            <text x={X(-8.3)} y={Y(39.9)} fill="rgba(255,255,255,0.45)" fontFamily={FONT} fontWeight={800} fontSize={Math.min(70, 22 * z)} letterSpacing={4}>PORTUGAL</text>
            <text x={X(-6.4)} y={Y(34.2)} fill="rgba(255,255,255,0.45)" fontFamily={FONT} fontWeight={800} fontSize={Math.min(90, 30 * z)} letterSpacing={6}>MOROCCO</text>
            <text x={X(-14)} y={Y(37.3)} fill="rgba(127,233,255,0.5)" fontFamily={FONT} fontWeight={800} fontSize={Math.min(60, 22 * z)} letterSpacing={4}>ATLANTIC</text>
            <text x={X(-0.5)} y={Y(37.5)} fill="rgba(127,233,255,0.5)" fontFamily={FONT} fontWeight={800} fontSize={Math.min(60, 20 * z)} letterSpacing={4}>MEDITERRANEAN</text>
          </>
        ) : null}
        {width ? (
          <g>
            <line x1={X(-5.6)} y1={Y(36.01)} x2={X(-5.55)} y2={Y(35.9)} stroke={C.accent} strokeWidth={6} strokeDasharray="14 8" />
            <text x={X(-5.5)} y={Y(35.96)} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={48} stroke="#000" strokeWidth={6} paintOrder="stroke">≈ 14 KM</text>
          </g>
        ) : null}
        {ships
          ? Array.from({ length: 10 }, (_, i) => {
              const t = ((f * 0.006 + i / 10) % 1 + 1) % 1;
              const lon = i % 2 ? -8 + t * 6 : -2 - t * 6;
              const lat = 35.95 + (i % 3) * 0.03;
              return <circle key={i} cx={X(lon)} cy={Y(lat)} r={7} fill={i % 3 ? C.white : C.accent} opacity={0.9} />;
            })
          : null}
        {route ? <polyline points={route.slice(0, Math.max(1, Math.ceil(prog * route.length))).map(([lo, la]) => `${X(lo)},${Y(la)}`).join(" ")} stroke={C.accent} strokeWidth={8} strokeDasharray="20 12" fill="none" /> : null}
        {arrow ? (() => {
          const [x1, y1] = [X(arrow.from[0]), Y(arrow.from[1])];
          const [x2, y2] = [X(arrow.to[0]), Y(arrow.to[1])];
          const p = prog;
          const xe = x1 + (x2 - x1) * p, ye = y1 + (y2 - y1) * p;
          const a = Math.atan2(y2 - y1, x2 - x1);
          return (
            <g>
              <line x1={x1} y1={y1} x2={xe} y2={ye} stroke={arrow.color ?? C.accent} strokeWidth={12} />
              <path d={`M ${xe} ${ye} l ${-40 * Math.cos(a - 0.5)} ${-40 * Math.sin(a - 0.5)} M ${xe} ${ye} l ${-40 * Math.cos(a + 0.5)} ${-40 * Math.sin(a + 0.5)}`} stroke={arrow.color ?? C.accent} strokeWidth={12} />
            </g>
          );
        })() : null}
        {pins.map((p, i) => {
          const s = pop(f, p.at ?? 3 + i * 5, 8);
          const side = p.side ?? 1;
          return (
            <g key={i} transform={`translate(${X(p.lon)} ${Y(p.lat)}) scale(${s})`}>
              <circle r={16} fill={p.color ?? C.red} />
              <circle r={16 + ((f * 1.5) % 36)} fill="none" stroke={p.color ?? C.red} strokeWidth={4} opacity={1 - ((f * 1.5) % 36) / 36} />
              <text x={side * 30} y={12} textAnchor={side > 0 ? "start" : "end"} fill="#fff" fontFamily={FONT} fontWeight={800} fontSize={40} stroke="#000" strokeWidth={7} paintOrder="stroke">{p.label}</text>
            </g>
          );
        })}
      </svg>
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 70, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{title}</div> : null}
    </AbsoluteFill>
  );
};

// ---------- Population, ID cards, headlines ----------

// 39 orcas in five family groups. `fade` greys out the last n; `hi` lights one group.
export const Census: React.FC<{ fade?: number; hi?: number; title?: string; count?: boolean }> = ({ fade = 0, hi = -1, title, count = true }) => {
  const { f } = useShot();
  const groups = [9, 8, 8, 7, 7];
  let n = 0;
  const shown = Math.min(39, Math.floor(f * 1.6));
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #0f4050 0%, #04161d 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {groups.map((g, gi) => {
          const gx = 260 + gi * 350;
          return (
            <g key={gi}>
              <rect x={gx - 150} y={260} width={300} height={430} rx={28} fill={gi === hi ? "rgba(255,210,63,0.16)" : "rgba(255,255,255,0.04)"} stroke={gi === hi ? C.accent : "rgba(255,255,255,0.12)"} strokeWidth={3} />
              {Array.from({ length: g }, (_, j) => {
                const idx = n++;
                const vis = idx < shown;
                const dead = idx >= 39 - fade;
                return (
                  <g key={j} opacity={vis ? (dead ? 0.15 : 1) : 0}>
                    <Orca x={gx - 62 + (j % 2) * 128} y={318 + Math.floor(j / 2) * 84} s={0.155} f={f + idx * 5} />
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
      {count ? <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 120, color: C.accent, textShadow: SHADOW }}>{Math.max(0, shown - fade)}</div> : null}
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 720, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 30, letterSpacing: 4, color: C.white }}>{title}</div> : null}
    </AbsoluteFill>
  );
};

// Research photo-ID cards: a drawn dorsal fin and saddle patch per orca, with its name.
const finPath = (seed: string) => {
  const h = 150 + random(seed) * 60;
  const lean = 30 + random(seed + "l") * 40;
  const nick = random(seed + "n");
  const ny = 0.35 + nick * 0.4;
  const nx = -lean * ny;
  return `M -70 0 C -60 ${-h * 0.5} ${-lean - 10} ${-h * 0.9} ${-lean} ${-h} C ${-lean + 20} ${-h * 0.92} 10 ${-h * 0.6} ${nx + 26} ${-h * ny} L ${nx + 14} ${-h * ny + 8} L ${nx + 30} ${-h * ny + 14} C 50 ${-h * 0.2} 60 -10 80 0 Z`;
};
export const IdCards: React.FC<{ names: string[]; sub?: string[]; hi?: number; title?: string }> = ({ names, sub = [], hi = -1, title }) => {
  const { f } = useShot();
  const n = names.length;
  const w = Math.min(420, 1700 / n - 30);
  return (
    <AbsoluteFill style={{ background: "#e9e4d8" }}>
      <AbsoluteFill style={{ background: "repeating-linear-gradient(0deg, transparent 0 39px, rgba(0,0,0,0.05) 39px 40px)" }} />
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 80, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: "#3a3a3a" }}>{title}</div> : null}
      {names.map((name, i) => {
        const p = pop(f, 2 + i * 4, 10);
        const x = 960 - (n * (w + 30)) / 2 + i * (w + 30);
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 230, width: w, height: 470, background: "#fbfaf6", borderRadius: 12, boxShadow: i === hi ? `0 0 0 8px ${C.accent}, 0 14px 40px rgba(0,0,0,0.3)` : "0 14px 40px rgba(0,0,0,0.25)", opacity: p, transform: `translateY(${(1 - p) * 60}px) rotate(${(i % 2 ? 1 : -1) * 1.5}deg)` }}>
            <svg width={w} height={300} style={{ position: "absolute", top: 20 }}>
              <rect x={14} y={0} width={w - 28} height={290} fill="#5c7f92" />
              <g transform={`translate(${w / 2} 240) scale(${Math.min(1.4, w / 260)})`}>
                <path d="M -200 0 C -100 -30 100 -30 200 0 L 200 60 L -200 60 Z" fill={BLACK} />
                <ellipse cx={-10} cy={-6} rx={110} ry={16} fill={SADDLE} opacity={0.85} />
                <path d={finPath(name)} fill={BLACK} />
              </g>
            </svg>
            <div style={{ position: "absolute", top: 340, left: 0, right: 0, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: Math.min(44, w / 7), color: "#1d2a30" }}>{name}</div>
            {sub[i] ? <div style={{ position: "absolute", top: 400, left: 0, right: 0, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 20, letterSpacing: 2, color: "#6a6a6a" }}>{sub[i]}</div> : null}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Headlines and posts stacking up on screen.
export const Headlines: React.FC<{ items: string[] }> = ({ items }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "#14181c" }}>
      {items.map((t, i) => {
        const p = pop(f, i * 6, 8);
        return (
          <div key={i} style={{ position: "absolute", left: 220 + (i % 2) * 560 + (i % 3) * 60, top: 120 + i * 150, width: 920, padding: "26px 34px", background: i % 2 ? "#f4f1e8" : "#ffffff", borderLeft: `14px solid ${i % 2 ? C.red : "#111"}`, boxShadow: "0 18px 40px rgba(0,0,0,0.5)", opacity: p, transform: `scale(${0.8 + 0.2 * p}) rotate(${(i % 2 ? 2 : -2) * p}deg)`, fontFamily: FONT, fontWeight: 800, fontSize: 50, color: "#111", lineHeight: 1.05 }}>
            {t}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// A big dorsal fin at the surface, with impact marks appearing.
export const FinHoles: React.FC<{ holes?: number; ring?: boolean; text?: string }> = ({ holes = 0, ring = false, text }) => {
  const { f } = useShot();
  const pts: [number, number][] = [[-40, -230], [-58, -205], [-30, -190], [-70, -175], [-45, -160], [-15, -150], [-60, -140], [-35, -125], [0, -110], [-50, -105]];
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#7fb2c9 0%, #cfe3ea 59%, #1b6f88 59%, #08384a 100%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <g transform={`translate(960 ${640 + Math.sin(f * 0.08) * 6}) scale(1.35)`}>
          <path d="M -150 0 C -120 -150 -80 -260 -130 -330 C -60 -300 20 -200 60 -110 C 80 -60 110 -20 150 0 Z" fill={BLACK} />
          {pts.slice(0, holes).map(([x, y], i) => <circle key={i} cx={x} cy={y} r={4.5 * pop(f, 2 + i * 2, 5)} fill="#cfd6da" />)}
          {ring ? <ellipse cx={-38} cy={-168} rx={80} ry={100} fill="none" stroke={C.accent} strokeWidth={5} strokeDasharray={`${ease(f / 12) * 900} 9999`} /> : null}
        </g>
        <rect x={0} y={636} width={1920} height={444} fill="#0b4a60" opacity={0.35} />
      </svg>
      {text ? <div style={{ position: "absolute", left: 0, right: 0, top: 60, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{text}</div> : null}
    </AbsoluteFill>
  );
};

// An orca at the surface wearing a dead salmon on its head (the 1987 fad), drawn.
export const SalmonHat: React.FC<{ n?: number }> = ({ n = 1 }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#6f8fa0 0%, #b9cdd6 45%, #2b6b80 45%, #0b3442 100%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: n }, (_, i) => {
          const x = n === 1 ? 960 : 520 + i * 440;
          const y = 520 + Math.sin(f * 0.1 + i) * 8;
          return (
            <g key={i} transform={`translate(${x} ${y})`}>
              <Orca x={0} y={60} s={0.75} rot={-6} f={f + i * 10} />
              <g transform="translate(178 4) rotate(-10) scale(0.62)">
                <path d="M -90 0 C -60 -26 40 -30 90 -6 L 120 -24 L 112 4 L 122 26 L 90 10 C 40 26 -60 24 -90 0 Z" fill="#c76a5a" />
                <circle cx={-70} cy={-4} r={5} fill="#222" />
              </g>
            </g>
          );
        })}
        <rect x={0} y={486} width={1920} height={594} fill="#0b4a60" opacity={0.3} />
      </svg>
    </AbsoluteFill>
  );
};

// A countdown-free big date or number on a paper card.
export const DateCard: React.FC<{ top?: string; big: string; sub?: string; color?: string; dark?: boolean }> = ({ top, big, sub, color, dark = false }) => {
  const { f, k } = useShot();
  const p = pop(f, 0, 10);
  return (
    <AbsoluteFill style={{ background: dark ? "radial-gradient(ellipse at 50% 45%, #0f3a47 0%, #04161d 80%)" : "#ece6d8", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center", transform: `scale(${(0.9 + 0.1 * p) * (1 + 0.04 * k)})`, opacity: p }}>
        {top ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 36, letterSpacing: 8, color: dark ? C.cyan : "#5a5a5a" }}>{top}</div> : null}
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 190, lineHeight: 1.05, color: color ?? (dark ? C.white : "#16232a") }}>{big}</div>
        {sub ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 5, color: dark ? "rgba(255,255,255,0.75)" : "#5a5a5a", marginTop: 8 }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
