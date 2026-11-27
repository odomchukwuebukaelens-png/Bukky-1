// Drawn scenes for "Megalodon Didn't Look Like a Giant Great White".
// One shark drawing that can be stocky (great white) or long and slender (the 2024–25 megalodon),
// plus the fossil evidence: teeth, the vertebral column, growth rings, the family tree and the 3D model.
import React from "react";
import { AbsoluteFill, random } from "remotion";
import { useShot } from "../kit/shots";
import { MONO } from "../kit/hud";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { Whale } from "../humpback/draw";

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

// ---------- The shark ----------

export type Build = { len: number; girth: number; tail: number; color: string; belly: string };
export const BUILDS: Record<string, Build> = {
  gw: { len: 1, girth: 1.28, tail: 1, color: "#6f7d87", belly: "#e9edef" },
  megOld: { len: 1, girth: 1.28, tail: 1, color: "#56636c", belly: "#d9dfe2" },
  megNew: { len: 1.42, girth: 0.95, tail: 1.2, color: "#4f5d66", belly: "#d3dade" },
  mako: { len: 1, girth: 1.05, tail: 1.05, color: "#2f5f9a", belly: "#f1f4f6" },
  lemon: { len: 1.12, girth: 0.86, tail: 1.1, color: "#a99a62", belly: "#efe8cf" },
};

// A shark in profile, facing right, 600 px long at s = 1 and len = 1. `open` opens the mouth (0–1); `glow` adds a warm core.
export const Shark: React.FC<{ x: number; y: number; s?: number; b?: Build | keyof typeof BUILDS; flip?: boolean; rot?: number; f?: number; open?: number; glow?: number; outline?: boolean; wire?: boolean; opacity?: number }> = ({
  x, y, s = 1, b = "megNew", flip = false, rot = 0, f = 0, open = 0, glow = 0, outline = false, wire = false, opacity = 1,
}) => {
  const B = typeof b === "string" ? BUILDS[b] : b;
  const L = 300 * B.len;
  const H = 70 * B.girth;
  const T = -0.8 * L;
  const tl = B.tail;
  const body = `M ${L} 0 C ${L * 0.85} ${-H * 0.75} ${L * 0.5} ${-H} ${L * 0.2} ${-H} C ${-L * 0.2} ${-H} ${-L * 0.6} ${-H * 0.45} ${T} ${-H * 0.18} L ${T} ${H * 0.18} C ${-L * 0.55} ${H * 0.5} ${-L * 0.1} ${H * 0.95} ${L * 0.25} ${H * 0.85} C ${L * 0.6} ${H * 0.75} ${L * 0.9} ${H * 0.4} ${L} 0 Z`;
  const belly = `M ${L * 0.98} ${H * 0.12} C ${L * 0.5} ${H * 0.32} ${-L * 0.3} ${H * 0.36} ${T} ${H * 0.15} L ${T} ${H * 0.18} C ${-L * 0.55} ${H * 0.5} ${-L * 0.1} ${H * 0.95} ${L * 0.25} ${H * 0.85} C ${L * 0.6} ${H * 0.75} ${L * 0.9} ${H * 0.4} ${L} 0 Z`;
  const tail = `M ${T + 6} ${-H * 0.2} L ${T - 75 * tl} ${-H * 1.75 - 40 * (tl - 1)} L ${T - 28} 0 L ${T - 62 * tl} ${H * 1.35} L ${T + 6} ${H * 0.2} Z`;
  const dorsal = `M ${L * 0.16} ${-H * 0.95} C ${L * 0.06} ${-H * 1.6} ${-L * 0.04} ${-H * 1.9} ${-L * 0.14} ${-H * 2.05} C ${-L * 0.1} ${-H * 1.5} ${-L * 0.08} ${-H * 1.2} ${-L * 0.12} ${-H * 0.85} Z`;
  const pect = `M ${L * 0.32} ${H * 0.62} L ${L * 0.06} ${H * 1.95} L ${L * 0.14} ${H * 0.72} Z`;
  const small = `M ${-L * 0.6} ${-H * 0.5} L ${-L * 0.66} ${-H * 0.85} L ${-L * 0.7} ${-H * 0.4} Z M ${-L * 0.58} ${H * 0.55} L ${-L * 0.66} ${H * 0.9} L ${-L * 0.68} ${H * 0.45} Z`;
  const beat = Math.sin(f * 0.18) * 7;
  const stroke = outline || wire ? (wire ? C.cyan : C.white) : "none";
  const fill = outline || wire ? "none" : B.color;
  const sw = (outline ? 5 : 3) / s;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`} opacity={opacity}>
      <g transform={`rotate(${beat} ${T} 0)`}>
        <path d={tail} fill={fill} stroke={stroke} strokeWidth={sw} />
      </g>
      <path d={dorsal} fill={fill} stroke={stroke} strokeWidth={sw} />
      <path d={small} fill={fill} stroke={stroke} strokeWidth={sw} />
      <path d={body} fill={fill} stroke={stroke} strokeWidth={sw} />
      {!outline && !wire ? <path d={belly} fill={B.belly} /> : null}
      {wire
        ? Array.from({ length: 9 }, (_, i) => {
            const xx = L * 0.9 - i * (L * 1.7) / 8;
            return <line key={i} x1={xx} y1={-H} x2={xx} y2={H * 0.9} stroke={C.cyan} strokeWidth={1.5 / s} opacity={0.5} />;
          })
        : null}
      {glow > 0 ? <ellipse cx={0} cy={0} rx={L * 0.7} ry={H * 0.6} fill="#ff9a3c" opacity={0.45 * glow} style={{ filter: "blur(18px)" }} /> : null}
      <path d={pect} fill={outline || wire ? "none" : B.color} stroke={stroke} strokeWidth={sw} />
      {!outline && !wire ? (
        <>
          {[0, 1, 2, 3, 4].map((i) => <line key={i} x1={L * (0.52 - i * 0.035)} y1={-H * 0.2} x2={L * (0.5 - i * 0.035)} y2={H * 0.3} stroke="#2a343a" strokeWidth={2 / s + 1} opacity={0.6} />)}
          <circle cx={L * 0.8} cy={-H * 0.22} r={Math.max(5, H * 0.08)} fill="#0b0f12" />
          {open > 0 ? (
            <g>
              <path d={`M ${L * 0.92} ${H * 0.2} L ${L * 0.55} ${H * 0.45} L ${L * 0.9} ${H * (0.45 + 0.7 * open)} Z`} fill="#4a1414" />
              {Array.from({ length: 7 }, (_, i) => <path key={i} d={`M ${L * (0.88 - i * 0.045)} ${H * (0.24 + i * 0.03)} l -6 12 l -6 -12 Z`} fill="#f4f1e8" />)}
            </g>
          ) : (
            <path d={`M ${L * 0.88} ${H * 0.38} L ${L * 0.6} ${H * 0.5}`} stroke="#2a343a" strokeWidth={3} />
          )}
        </>
      ) : null}
    </g>
  );
};

// ---------- Underwater set ----------

export type SharkActor = { b?: keyof typeof BUILDS; x0: number; y0: number; x1?: number; y1?: number; s?: number; s1?: number; flip?: boolean; rot?: number; open?: number; glow?: number; outline?: boolean; wire?: boolean; o0?: number; o1?: number };

export const Deep: React.FC<{
  sharks?: SharkActor[];
  whale?: { x0: number; y0: number; x1?: number; s?: number; flip?: boolean };
  bus?: { x: number; y: number; n?: number; s?: number };
  person?: { x: number; y: number; s?: number };
  ruler?: { x: number; y: number; px: number; label: string };
  warm?: boolean;
  dark?: boolean;
  children?: React.ReactNode;
}> = ({ sharks = [], whale, bus, person, ruler, warm = false, dark = false, children }) => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <AbsoluteFill style={{ background: dark ? "linear-gradient(#0b2a38, #020a0e)" : warm ? "linear-gradient(#1f8fa6, #0b3e52)" : "linear-gradient(#16708a, #06283a)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {[0, 1, 2, 3, 4].map((i) => <polygon key={i} points={`${260 + i * 360 + Math.sin(f * 0.03 + i) * 30},0 ${380 + i * 360},0 ${200 + i * 330},1080 ${80 + i * 330},1080`} fill="#c9f6ff" opacity={dark ? 0.02 : 0.05} />)}
        {Array.from({ length: 40 }, (_, i) => <circle key={i} cx={(random(`p${i}`) * 1920 + f * 0.4) % 1920} cy={random(`q${i}`) * 1080} r={1.5 + random(`r${i}`) * 2} fill="#e6fbff" opacity={0.25} />)}
        {whale ? <Whale x={lerp(whale.x0, whale.x1, e)} y={whale.y0} s={whale.s ?? 0.6} flip={whale.flip} f={f} /> : null}
        {bus ? (
          <g transform={`translate(${bus.x} ${bus.y}) scale(${bus.s ?? 1})`}>
            {Array.from({ length: bus.n ?? 1 }, (_, i) => (
              <g key={i} transform={`translate(${i * 410} 0)`}>
                <rect x={0} y={-120} width={400} height={120} rx={14} fill={C.accent} />
                {[0, 1, 2, 3, 4].map((j) => <rect key={j} x={20 + j * 74} y={-104} width={60} height={46} rx={6} fill="#24343c" />)}
                <circle cx={80} cy={0} r={22} fill="#111" />
                <circle cx={320} cy={0} r={22} fill="#111" />
              </g>
            ))}
          </g>
        ) : null}
        {person ? (
          <g transform={`translate(${person.x} ${person.y}) scale(${person.s ?? 1})`} fill={C.white}>
            <circle cx={0} cy={-170} r={18} />
            <path d="M -18 -148 L 18 -148 L 22 -70 L 14 0 L 4 0 L 0 -60 L -4 0 L -14 0 L -22 -70 Z" />
          </g>
        ) : null}
        {sharks.map((a, i) => (
          <Shark key={i} b={a.b} x={lerp(a.x0, a.x1, e)} y={lerp(a.y0, a.y1, e)} s={lerp(a.s ?? 1, a.s1, e)} flip={a.flip} rot={a.rot} f={f + i * 13} open={a.open} glow={a.glow} outline={a.outline} wire={a.wire} opacity={lerp(a.o0 ?? 1, a.o1, e)} />
        ))}
        {ruler ? (
          <g transform={`translate(0 ${170 - ruler.y})`}>
            <line x1={ruler.x} y1={ruler.y} x2={ruler.x + ruler.px * ease(f / 14)} y2={ruler.y} stroke={C.accent} strokeWidth={6} />
            <line x1={ruler.x} y1={ruler.y - 18} x2={ruler.x} y2={ruler.y + 18} stroke={C.accent} strokeWidth={6} />
            <line x1={ruler.x + ruler.px * ease(f / 14)} y1={ruler.y - 18} x2={ruler.x + ruler.px * ease(f / 14)} y2={ruler.y + 18} stroke={C.accent} strokeWidth={6} />
            <text x={ruler.x + ruler.px / 2} y={ruler.y - 30} textAnchor="middle" fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={52} stroke="#000" strokeWidth={6} paintOrder="stroke" opacity={pop(f, 8)}>{ruler.label}</text>
          </g>
        ) : null}
      </svg>
      {children}
    </AbsoluteFill>
  );
};

// ---------- Fossil evidence ----------

const toothPath = (w: number, h: number) => `M ${-w / 2} 0 C ${-w * 0.45} ${-h * 0.4} ${-w * 0.15} ${-h * 0.8} 0 ${-h} C ${w * 0.15} ${-h * 0.8} ${w * 0.45} ${-h * 0.4} ${w / 2} 0 C ${w * 0.3} ${h * 0.18} ${-w * 0.3} ${h * 0.18} ${-w / 2} 0 Z`;

// A drawn tooth with a serrated edge; megalodon or great white.
export const Tooth: React.FC<{ x: number; y: number; h: number; meg?: boolean; label?: string; delay?: number }> = ({ x, y, h, meg = true, label, delay = 0 }) => {
  const { f } = useShot();
  const p = pop(f, delay, 10);
  const w = h * (meg ? 0.95 : 0.8);
  return (
    <g transform={`translate(${x} ${y}) scale(${p})`}>
      <path d={`M ${-w / 2} 6 L ${w / 2} 6 L ${w * 0.42} ${h * 0.22} L ${-w * 0.42} ${h * 0.22} Z`} fill={meg ? "#5a4a38" : "#d8d2c4"} />
      <path d={toothPath(w, h)} fill={meg ? "#7c8b93" : "#f2efe6"} stroke={meg ? "#3d4a50" : "#b9b2a2"} strokeWidth={3} />
      {Array.from({ length: 14 }, (_, i) => {
        const t = (i + 1) / 15;
        return (
          <React.Fragment key={i}>
            <circle cx={-w / 2 + (w / 2) * t} cy={-h * t * 0.98} r={1.8} fill={meg ? "#3d4a50" : "#b9b2a2"} />
            <circle cx={w / 2 - (w / 2) * t} cy={-h * t * 0.98} r={1.8} fill={meg ? "#3d4a50" : "#b9b2a2"} />
          </React.Fragment>
        );
      })}
      {label ? <text x={0} y={h * 0.22 + 60} textAnchor="middle" fill={C.white} fontFamily={FONT} fontWeight={800} fontSize={36}>{label}</text> : null}
    </g>
  );
};

export const TeethCompare: React.FC<{ hand?: boolean; triangle?: boolean; title?: string }> = ({ hand = true, triangle = false, title }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #1d3b45 0%, #071419 80%)" }}>
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      <Tooth x={720} y={640} h={420} meg label="MEGALODON ≈ 18 CM" />
      <Tooth x={1260} y={640} h={150} meg={false} label="GREAT WHITE" delay={8} />
      {triangle ? <path d="M 520 640 L 720 220 L 920 640 Z M 1190 640 L 1260 490 L 1330 640 Z" fill="none" stroke={C.accent} strokeWidth={6} strokeDasharray="18 10" /> : null}
      {hand ? <path d="M 1500 700 C 1500 600 1520 560 1560 560 L 1560 470 C 1560 440 1600 440 1600 470 L 1600 540 L 1600 440 C 1600 410 1640 410 1640 440 L 1640 540 L 1640 450 C 1640 420 1680 420 1680 450 L 1680 560 L 1680 490 C 1680 465 1715 465 1715 490 L 1715 640 C 1715 700 1680 740 1620 740 Z" fill="#d9b48f" opacity={0.85} /> : null}
    </svg>
    {title ? <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{title}</div> : null}
  </AbsoluteFill>
);

// A shark skeleton of cartilage that rots away, leaving teeth (and a few vertebrae).
export const Cartilage: React.FC<{ stage: "whole" | "rot" | "teeth" }> = ({ stage }) => {
  const { f, k } = useShot();
  const fade = stage === "whole" ? 1 : stage === "rot" ? 1 - ease(k * 1.2) : 0;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#0e4a5c, #041a22)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <rect x={0} y={760} width={1920} height={320} fill="#b39a6c" opacity={0.7} />
        <g opacity={fade}>
          <Shark x={960} y={560} s={1.6} b="gw" outline />
          {Array.from({ length: 40 }, (_, i) => <rect key={i} x={600 + i * 15} y={548} width={11} height={24} rx={3} fill="#d9e4e8" opacity={0.8} />)}
        </g>
        {Array.from({ length: 16 }, (_, i) => {
          const x = 1250 + (i % 8) * 18 - Math.floor(i / 8) * 10;
          const y = 640 + Math.floor(i / 8) * 26;
          const drop = stage === "whole" ? 0 : ease(k * 1.3) * (790 - y);
          return <path key={i} d={toothPath(14, 24)} transform={`translate(${x + (stage === "teeth" ? random(`t${i}`) * 200 - 100 : 0)} ${y + (stage === "teeth" ? 790 - y : drop)}) rotate(${stage === "whole" ? 0 : random(`r${i}`) * 120 - 60})`} fill="#f2efe6" />;
        })}
        {stage !== "whole" ? [0, 1, 2].map((i) => <circle key={i} cx={760 + i * 70} cy={790} r={12} fill="#d9e4e8" opacity={stage === "teeth" ? 1 : ease(k)} />) : null}
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: stage === "teeth" ? C.accent : C.white, textShadow: SHADOW }}>
        {stage === "whole" ? "CARTILAGE, NOT BONE" : stage === "rot" ? "IT ROTS AWAY" : "ONLY THE TEETH REMAIN"}
      </div>
    </AbsoluteFill>
  );
};

// A great white scaled up step by step: the old way of drawing megalodon.
export const ScaleUp: React.FC<{ crack?: boolean; label?: string }> = ({ crack = false, label }) => {
  const { f, k } = useShot();
  const s = 0.45 + 1.4 * ease(k);
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#16708a, #06283a)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <Shark x={960} y={540} s={s} b="megOld" f={f} />
        {crack ? (
          <g opacity={ease(k * 2 - 0.6)}>
            {[[960, 540, 600, 300], [960, 540, 1400, 260], [960, 540, 1500, 800], [960, 540, 500, 820], [960, 540, 980, 100]].map(([a, b, c, d], i) => <line key={i} x1={a} y1={b} x2={a + (c - a) * ease(k * 2 - 0.6)} y2={b + (d - b) * ease(k * 2 - 0.6)} stroke="#fff" strokeWidth={6} />)}
          </g>
        ) : null}
      </svg>
      {label ? <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.accent, textShadow: SHADOW }}>{label}</div> : null}
    </AbsoluteFill>
  );
};

// A family tree: megalodon's line (Otodus) and the great white's line (mako-like).
export const Tree: React.FC<{ stage?: 1 | 2 | 3; hi?: "meg" | "gw" | "both" }> = ({ stage = 3, hi = "both" }) => {
  const { f } = useShot();
  const draw = (at: number) => ease((f - at) / 14);
  const node = (x: number, y: number, t: string, sub: string, on: boolean, at: number) => (
    <g opacity={pop(f, at, 8)}>
      <rect x={x - 200} y={y - 50} width={400} height={100} rx={16} fill={on ? "rgba(255,210,63,0.16)" : "rgba(255,255,255,0.06)"} stroke={on ? C.accent : "rgba(255,255,255,0.3)"} strokeWidth={3} />
      <text x={x} y={y - 2} textAnchor="middle" fill={C.white} fontFamily={FONT} fontWeight={800} fontSize={34}>{t}</text>
      <text x={x} y={y + 32} textAnchor="middle" fill="rgba(255,255,255,0.7)" fontFamily={MONO} fontWeight={700} fontSize={20}>{sub}</text>
    </g>
  );
  const m = hi === "meg" || hi === "both";
  const g = hi === "gw" || hi === "both";
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #12404e 0%, #04161d 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <text x={60} y={140} fill="rgba(255,255,255,0.5)" fontFamily={MONO} fontWeight={700} fontSize={20}>55 MILLION YEARS AGO</text>
        <text x={60} y={760} fill="rgba(255,255,255,0.5)" fontFamily={MONO} fontWeight={700} fontSize={22}>NOW</text>
        {node(620, 230, "OTODUS OBLIQUUS", "≈ 55 MILLION YEARS AGO", m, 0)}
        <line x1={620} y1={280} x2={620} y2={280 + 300 * draw(6)} stroke={m ? C.accent : "#7f9aa3"} strokeWidth={8} />
        {node(620, 640, "MEGALODON", "OTODUS · EXTINCT", m, 18)}
        {stage >= 2 ? (
          <>
            {node(1300, 380, "MAKO-LIKE ANCESTOR", "SMALLER, SMOOTH TEETH", g, 22)}
            <line x1={1300} y1={430} x2={1300} y2={430 + 160 * draw(28)} stroke={g ? C.accent : "#7f9aa3"} strokeWidth={8} />
            {node(1300, 640, "GREAT WHITE", "CARCHARODON · ALIVE", g, 38)}
          </>
        ) : null}
        {stage >= 3 ? <text x={960} y={850} textAnchor="middle" fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={60} opacity={pop(f, 30)}>COUSINS, NOT GRANDPARENTS</text> : null}
      </svg>
    </AbsoluteFill>
  );
};

// The 141-disc vertebral column from Brussels lining up, optionally laid against shark outlines.
export const Spine: React.FC<{ n?: number; over?: "none" | "gw" | "slim"; label?: string; ct?: boolean }> = ({ n = 141, over = "none", label, ct = false }) => {
  const { f, k } = useShot();
  const shown = Math.min(n, Math.floor(f * 6));
  const x0 = 300;
  const w = 1320 / 141;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #1d3b45 0%, #071419 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {over === "gw" ? <Shark x={960 - 120} y={540} s={1.9} b="gw" outline opacity={ease(k * 2)} /> : null}
        {over === "slim" ? <Shark x={960 + 40} y={540} s={1.85} b="megNew" outline opacity={ease(k * 2)} /> : null}
        {Array.from({ length: shown }, (_, i) => {
          const hgt = 70 - Math.abs(i - 50) * 0.35;
          return <rect key={i} x={x0 + i * w} y={540 - hgt / 2} width={w - 1.5} height={Math.max(20, hgt)} rx={2} fill="#d8cdb3" stroke="#8a7c5c" strokeWidth={1} />;
        })}
        {ct ? <rect x={x0 + (1320 * ((f * 0.02) % 1))} y={430} width={8} height={220} fill={C.cyan} opacity={0.8} /> : null}
        <text x={960} y={680} textAnchor="middle" fill="rgba(255,255,255,0.75)" fontFamily={MONO} fontWeight={700} fontSize={30} letterSpacing={4}>{shown} VERTEBRAE</text>
      </svg>
      {label ? <div style={{ position: "absolute", left: 0, right: 0, top: 110, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.accent, textShadow: SHADOW }}>{label}</div> : null}
    </AbsoluteFill>
  );
};

// A vertebra cut through, its growth bands appearing like tree rings.
export const Rings: React.FC<{ to?: number; text?: string }> = ({ to = 46, text }) => {
  const { f } = useShot();
  const shown = Math.min(to, Math.floor(f * 2.2));
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #1d3b45 0%, #071419 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <circle cx={760} cy={520} r={330} fill="#d8cdb3" />
        {Array.from({ length: shown }, (_, i) => <circle key={i} cx={760} cy={520} r={20 + (i / to) * 300} fill="none" stroke="#8a6f45" strokeWidth={2.5} opacity={0.8} />)}
        <circle cx={760} cy={520} r={18} fill="#3a2e1c" />
        <text x={1260} y={560} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={180}>{shown}</text>
        <text x={1264} y={620} fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={30} letterSpacing={4}>GROWTH BANDS</text>
      </svg>
      {text ? <div style={{ position: "absolute", left: 0, right: 0, top: 70, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 60, color: C.white, textShadow: SHADOW }}>{text}</div> : null}
    </AbsoluteFill>
  );
};

// A newborn megalodon next to an adult human, and eggs inside the mother.
export const Newborn: React.FC<{ womb?: boolean }> = ({ womb = false }) => {
  const { f } = useShot();
  return (
    <Deep person={womb ? undefined : { x: 1300, y: 760, s: 1.25 }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {womb ? (
          <>
            <Shark x={960} y={540} s={2.2} b="megNew" outline />
            <ellipse cx={980} cy={590} rx={330} ry={90} fill="rgba(255,210,63,0.08)" stroke={C.accent} strokeWidth={3} strokeDasharray="10 8" />
            <Shark x={940 + Math.sin(f * 0.1) * 10} y={590} s={0.5} b="megNew" f={f} />
            {Array.from({ length: 7 }, (_, i) => <circle key={i} cx={1150 + (i % 4) * 30} cy={560 + Math.floor(i / 4) * 34} r={12} fill="#f3e2a1" opacity={i < 7 - Math.floor(f / 8) ? 1 : 0} />)}
          </>
        ) : (
          <>
            <Shark x={760} y={600} s={0.62} b="megNew" f={f} />
            <line x1={760 - 300 * 1.42 * 0.62 - 60} y1={170} x2={760 + 300 * 1.42 * 0.62} y2={170} stroke={C.accent} strokeWidth={6} />
            <text x={700} y={140} textAnchor="middle" fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={48}>≈ 2 M AT BIRTH</text>
          </>
        )}
      </svg>
    </Deep>
  );
};

// The 2022 3D model being built: column, then teeth, then great-white "flesh".
export const Build3D: React.FC<{ stage: "column" | "teeth" | "flesh" | "done" }> = ({ stage }) => {
  const { f, k } = useShot();
  const rot = Math.sin(f * 0.03) * 6;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0f2f3a 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 20 }, (_, i) => <line key={i} x1={0} y1={700 + i * 20} x2={1920} y2={700 + i * 20} stroke="rgba(127,212,255,0.08)" />)}
        <g transform={`translate(960 520) skewY(${rot}) translate(-960 -520)`}>
          {Array.from({ length: 141 }, (_, i) => <rect key={i} x={520 + i * 6.4} y={520 - 16} width={5} height={32} fill="#d8cdb3" opacity={0.9} />)}
          {stage !== "column" ? <g opacity={stage === "teeth" ? ease(k * 2) : 1}>{Array.from({ length: 12 }, (_, i) => <path key={i} d={toothPath(16, 26)} transform={`translate(${1460 + i * 10} ${560 - (i % 2) * 6}) rotate(180)`} fill="#f2efe6" />)}</g> : null}
          {stage === "flesh" || stage === "done" ? <Shark x={1000} y={520} s={1.7} b="megOld" wire={stage === "flesh"} opacity={stage === "flesh" ? ease(k * 1.5) : 0.95} f={f} /> : null}
        </g>
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 90, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: C.cyan }}>
        {stage === "column" ? "STEP 1 · THE SPINE" : stage === "teeth" ? "STEP 2 · THE TEETH" : stage === "flesh" ? "STEP 3 · A GREAT WHITE'S BODY" : "3D MODEL · 2022"}
      </div>
    </AbsoluteFill>
  );
};

// Three reconstructions side by side.
export const Three: React.FC<{ hi?: number; q?: boolean }> = ({ hi = -1, q = true }) => {
  const { f } = useShot();
  const items: { b: keyof typeof BUILDS; s: number; t: string }[] = [
    { b: "megOld", s: 0.75, t: "1909" },
    { b: "megOld", s: 0.62, t: "2022" },
    { b: "megNew", s: 0.62, t: "2025" },
  ];
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #04161d 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {items.map((it, i) => (
          <g key={i} opacity={pop(f, i * 5)}>
            <Shark x={360 + i * 600} y={480} s={it.s} b={it.b} outline={i !== hi} f={f} />
            <text x={360 + i * 600} y={700} textAnchor="middle" fill={i === hi ? C.accent : C.white} fontFamily={FONT} fontWeight={800} fontSize={56}>{it.t}</text>
            {q ? <text x={360 + i * 600} y={330} textAnchor="middle" fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={90} opacity={pop(f, 12 + i * 4)}>?</text> : null}
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
};

// The world cooling: ice growing at the poles, warm coastal seas shrinking.
export const Cooling: React.FC<{ text?: string }> = ({ text }) => {
  const { f, k } = useShot();
  const ice = 60 + 140 * ease(k);
  return (
    <AbsoluteFill style={{ background: "#04161d" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <defs>
          <clipPath id="globe"><circle cx={960} cy={540} r={380} /></clipPath>
        </defs>
        <circle cx={960} cy={540} r={380} fill="#1b6f88" />
        <g clipPath="url(#globe)">
          <path d="M 700 300 C 760 260 860 280 900 340 C 940 420 880 520 820 560 C 760 600 700 560 680 480 Z M 1000 360 C 1080 320 1200 360 1220 440 C 1240 540 1160 640 1080 660 C 1020 640 990 520 1000 360 Z" fill="#3f7a58" />
          <rect x={560} y={160} width={800} height={ice} fill="#eef6f8" />
          <rect x={560} y={920 - ice} width={800} height={ice} fill="#eef6f8" />
          <rect x={560} y={160 + ice} width={800} height={760 - ice * 2} fill="#ff8a4c" opacity={0.25 * (1 - ease(k))} />
        </g>
        <circle cx={960} cy={540} r={380} fill="none" stroke="#7fd4ff" strokeWidth={3} />
        <text x={960} y={1000} textAnchor="middle" fill={C.cyan} fontFamily={MONO} fontWeight={700} fontSize={30} letterSpacing={4} opacity={0.8}>{Math.round(24 - 6 * ease(k))} °C AVERAGE SEA SURFACE (ILLUSTRATIVE)</text>
      </svg>
      {text ? <div style={{ position: "absolute", left: 0, right: 0, top: 60, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white, textShadow: SHADOW }}>{text}</div> : null}
    </AbsoluteFill>
  );
};

// Drawers of "tongue stones" in an old cabinet of curiosities.
export const Cabinet: React.FC<{ text?: string }> = ({ text }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "#2a1b10" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 3 }, (_, r) =>
          Array.from({ length: 4 }, (_, c) => (
            <g key={`${r}-${c}`} transform={`translate(${260 + c * 360} ${180 + r * 230})`} opacity={pop(f, (r * 4 + c) * 1.5)}>
              <rect width={330} height={200} rx={8} fill="#5b3b22" stroke="#8a6040" strokeWidth={6} />
              <rect x={14} y={14} width={302} height={172} fill="#e9dfc8" />
              {Array.from({ length: 3 }, (_, i) => <path key={i} d={toothPath(48, 70)} transform={`translate(${80 + i * 85} ${150}) rotate(${(random(`${r}${c}${i}`) - 0.5) * 30})`} fill={["#7c8b93", "#5a4a38", "#9a8a70"][i]} />)}
            </g>
          ))
        )}
      </svg>
      {text ? <div style={{ position: "absolute", left: 0, right: 0, top: 70, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: "#f3e7c9", textShadow: SHADOW }}>{text}</div> : null}
    </AbsoluteFill>
  );
};
