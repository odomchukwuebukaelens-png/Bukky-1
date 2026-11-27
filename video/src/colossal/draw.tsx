// Drawn scenes for "The First Colossal Squid Ever Filmed Alive".
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
const Title: React.FC<{ text?: string; color?: string; size?: number; y?: number }> = ({ text, color = C.white, size = 62, y = 170 }) =>
  text ? <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: size, color, textShadow: SHADOW }}>{text}</div> : null;

const RED = "#9e2f25";
const RED_D = "#6e1d17";

// A squid from the side: mantle pointing right, head and eye in the middle, arms trailing left. About 900 px long at s = 1.
export const Squid: React.FC<{ x: number; y: number; s?: number; flip?: boolean; rot?: number; f?: number; glass?: boolean; giant?: boolean; hooks?: boolean; outline?: boolean; opacity?: number; eye?: number }> = ({
  x, y, s = 1, flip = false, rot = 0, f = 0, glass = false, giant = false, hooks = false, outline = false, opacity = 1, eye = 1,
}) => {
  const body = glass ? "rgba(220,240,255,0.22)" : giant ? "#b5523f" : RED;
  const dark = glass ? "rgba(220,240,255,0.5)" : giant ? "#86392c" : RED_D;
  const stroke = outline ? C.white : glass ? "rgba(230,250,255,0.8)" : "none";
  const fill = outline ? "none" : body;
  const armLen = giant ? 520 : 330;
  const mantleL = giant ? 300 : 420;
  const mantleH = giant ? 70 : 120;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s}) rotate(${rot})`} opacity={opacity}>
      {/* arms */}
      {Array.from({ length: 8 }, (_, i) => {
        const a = (i - 3.5) * 9;
        const wave = Math.sin(f * 0.08 + i) * 14;
        const L = armLen * (0.75 + (i % 3) * 0.08);
        return <path key={i} d={`M -40 ${a * 0.6} C ${-L * 0.35} ${a * 1.6 + wave} ${-L * 0.7} ${a * 2.2 - wave} ${-L} ${a * 2.6 + wave * 0.5}`} stroke={outline ? C.white : body} strokeWidth={giant ? 14 : 22} strokeLinecap="round" fill="none" />;
      })}
      {/* two long tentacles */}
      {[-1, 1].map((sgn) => {
        const L = armLen * (giant ? 2.1 : 1.35);
        const wave = Math.sin(f * 0.06 + sgn) * 20;
        return (
          <g key={sgn}>
            <path d={`M -40 ${sgn * 10} C ${-L * 0.4} ${sgn * 60 + wave} ${-L * 0.75} ${sgn * 40 - wave} ${-L} ${sgn * 70 + wave}`} stroke={outline ? C.white : body} strokeWidth={8} strokeLinecap="round" fill="none" />
            <ellipse cx={-L} cy={sgn * 70 + wave} rx={44} ry={16} fill={fill} stroke={stroke} strokeWidth={3} />
            {hooks ? [0, 1, 2, 3].map((h) => <path key={h} d={`M ${-L - 30 + h * 18} ${sgn * 70 + wave - 4} q 6 -14 12 0`} stroke={C.accent} strokeWidth={4} fill="none" />) : null}
          </g>
        );
      })}
      {/* head */}
      <ellipse cx={20} cy={0} rx={90} ry={mantleH * 0.75} fill={fill} stroke={stroke} strokeWidth={3} />
      {/* mantle */}
      <path d={`M 80 ${-mantleH} C ${80 + mantleL * 0.5} ${-mantleH * 1.05} ${80 + mantleL * 0.9} ${-mantleH * 0.6} ${80 + mantleL} 0 C ${80 + mantleL * 0.9} ${mantleH * 0.6} ${80 + mantleL * 0.5} ${mantleH * 1.05} 80 ${mantleH} Z`} fill={fill} stroke={stroke} strokeWidth={3} />
      {/* fins */}
      <path d={`M ${80 + mantleL * 0.7} ${-mantleH * 0.6} L ${80 + mantleL * 1.05} ${-mantleH * 1.4} L ${80 + mantleL} 0 L ${80 + mantleL * 1.05} ${mantleH * 1.4} L ${80 + mantleL * 0.7} ${mantleH * 0.6} Z`} fill={outline ? "none" : dark} stroke={stroke} strokeWidth={3} />
      {!outline && !glass ? Array.from({ length: 18 }, (_, i) => <circle key={i} cx={100 + random(`sq${i}`) * mantleL * 0.8} cy={(random(`sr${i}`) - 0.5) * mantleH * 1.4} r={4 + random(`ss${i}`) * 5} fill={dark} opacity={0.6} />) : null}
      {glass ? Array.from({ length: 10 }, (_, i) => <circle key={i} cx={100 + random(`gq${i}`) * mantleL * 0.8} cy={(random(`gr${i}`) - 0.5) * mantleH} r={3} fill="#e86a4a" />) : null}
      {glass ? <ellipse cx={200} cy={0} rx={70} ry={26} fill="rgba(255,190,120,0.55)" /> : null}
      {/* eye */}
      <circle cx={10} cy={-8} r={(giant ? 22 : 34) * eye} fill="#0b0d10" stroke={glass ? "rgba(255,255,255,0.6)" : "#d8d1c4"} strokeWidth={4} />
      <circle cx={2} cy={-16} r={(giant ? 6 : 9) * eye} fill="#ffffff" opacity={0.7} />
    </g>
  );
};

// Toothfish, simple.
const Toothfish: React.FC<{ x: number; y: number; s?: number; flip?: boolean }> = ({ x, y, s = 1, flip = false }) => (
  <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
    <path d="M -120 0 L -160 -36 L -150 0 L -160 36 Z" fill="#4a4f54" />
    <path d="M 120 6 C 110 -30 40 -46 -20 -40 C -80 -34 -110 -14 -125 0 C -110 14 -80 30 -20 34 C 40 40 110 30 120 6 Z" fill="#6b7177" />
    <circle cx={88} cy={-6} r={8} fill="#111" />
  </g>
);

// A sperm whale from the side, facing right.
export const SpermWhale: React.FC<{ x: number; y: number; s?: number; flip?: boolean; f?: number; glow?: boolean }> = ({ x, y, s = 1, flip = false, f = 0, glow = false }) => (
  <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
    {glow ? <ellipse cx={0} cy={0} rx={560} ry={160} fill={C.cyan} opacity={0.18} style={{ filter: "blur(30px)" }} /> : null}
    <g transform={`rotate(${Math.sin(f * 0.08) * 6} -420 0)`}>
      <path d="M -420 0 L -520 -70 L -490 0 L -520 70 Z" fill="#3c4249" />
    </g>
    <path d="M 420 -90 L 420 60 C 380 90 300 100 200 96 C 0 96 -200 70 -420 10 L -420 -10 C -200 -70 0 -110 200 -110 C 320 -110 410 -105 420 -90 Z" fill="#4e555c" />
    <path d="M 410 70 L 260 80" stroke="#2b2f33" strokeWidth={6} />
    <circle cx={250} cy={10} r={7} fill="#111" />
    <path d="M -120 -84 L -150 -110 L -190 -78 Z" fill="#4e555c" />
  </g>
);

export type QActor = { x0: number; y0: number; x1?: number; y1?: number; s?: number; s1?: number; flip?: boolean; rot?: number; glass?: boolean; giant?: boolean; hooks?: boolean; outline?: boolean; o0?: number; o1?: number; eye?: number };

// Deep, cold water. Optional ROV light cone, a sperm whale, toothfish.
export const Abyss: React.FC<{ squids?: QActor[]; rov?: boolean; whale?: { x0: number; x1?: number; y: number; s?: number; flip?: boolean; glow?: boolean }; fish?: { x0: number; x1?: number; y: number; s?: number; flip?: boolean }[]; depth?: string; children?: React.ReactNode }> = ({
  squids = [], rov = false, whale, fish = [], depth, children,
}) => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #0b2a38 0%, #01070a 80%)", overflow: "hidden" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 70 }, (_, i) => <circle key={i} cx={(random(`a${i}`) * 1920 + f * 0.3) % 1920} cy={(random(`b${i}`) * 1080 + f * 0.5) % 1080} r={1.5 + random(`c${i}`) * 2} fill="#dff6ff" opacity={0.35} />)}
        {rov ? (
          <g>
            <polygon points={`1920,120 1920,320 700,820 400,300`} fill="#e9fbff" opacity={0.08} />
            <rect x={1760} y={150} width={180} height={140} rx={12} fill="#e0b13a" />
            <circle cx={1770} cy={200} r={14} fill="#fffbe0" />
            <circle cx={1770} cy={250} r={14} fill="#fffbe0" />
          </g>
        ) : null}
        {whale ? <SpermWhale x={lerp(whale.x0, whale.x1, e)} y={whale.y} s={whale.s ?? 0.8} flip={whale.flip} f={f} glow={whale.glow} /> : null}
        {fish.map((fi, i) => <Toothfish key={i} x={lerp(fi.x0, fi.x1, e)} y={fi.y} s={fi.s ?? 0.8} flip={fi.flip} />)}
        {squids.map((a, i) => (
          <Squid key={i} x={lerp(a.x0, a.x1, e)} y={lerp(a.y0, a.y1, e)} s={lerp(a.s ?? 0.8, a.s1, e)} flip={a.flip} rot={a.rot} f={f + i * 11} glass={a.glass} giant={a.giant} hooks={a.hooks} outline={a.outline} opacity={lerp(a.o0 ?? 1, a.o1, e)} eye={a.eye} />
        ))}
      </svg>
      {depth ? <div style={{ position: "absolute", left: 0, right: 0, top: 60, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 56, color: C.cyan, textShadow: SHADOW }}>{depth}</div> : null}
      {children}
    </AbsoluteFill>
  );
};

// Giant squid and colossal squid compared.
export const VsGiant: React.FC<{ hi?: "giant" | "colossal" }> = ({ hi }) => {
  const { f } = useShot();
  return (
    <Abyss>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <g opacity={hi === "colossal" ? 0.4 : 1}><Squid x={1250} y={330} s={0.8} giant f={f} /></g>
        <g opacity={hi === "giant" ? 0.4 : 1}><Squid x={1150} y={720} s={0.8} f={f} hooks /></g>
        <text x={1620} y={250} fill={C.white} fontFamily={FONT} fontWeight={800} fontSize={40}>GIANT</text>
        <text x={1620} y={292} fill="rgba(255,255,255,0.7)" fontFamily={MONO} fontWeight={700} fontSize={22}>LONGER · ≈ 12 M</text>
        <text x={1620} y={640} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={40}>COLOSSAL</text>
        <text x={1620} y={682} fill="rgba(255,255,255,0.7)" fontFamily={MONO} fontWeight={700} fontSize={22}>HEAVIER · ≈ 500 KG</text>
      </svg>
    </Abyss>
  );
};

// Labelled body parts.
export const Parts: React.FC<{ hi?: "mantle" | "fins" | "arms" | "tentacles" | "eye" | "beak" }> = ({ hi }) => {
  const { f } = useShot();
  const lab = (x: number, y: number, tx: number, ty: number, t: string, on: boolean) => (
    <g opacity={on ? 1 : 0.35}>
      <line x1={x} y1={y} x2={tx} y2={ty} stroke={on ? C.accent : C.white} strokeWidth={3} />
      <text x={tx} y={ty - 10} textAnchor="middle" fill={on ? C.accent : C.white} fontFamily={FONT} fontWeight={800} fontSize={36}>{t}</text>
    </g>
  );
  return (
    <Abyss>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <Squid x={1000} y={560} s={1} f={f} hooks />
        {lab(1300, 520, 1350, 330, "MANTLE", !hi || hi === "mantle")}
        {lab(1500, 500, 1640, 380, "FINS", !hi || hi === "fins")}
        {lab(820, 600, 760, 780, "8 ARMS", !hi || hi === "arms")}
        {lab(500, 620, 400, 800, "2 TENTACLES", !hi || hi === "tentacles")}
        {lab(1010, 552, 1000, 330, "EYE", !hi || hi === "eye")}
        {lab(960, 560, 900, 420, "BEAK", hi === "beak")}
      </svg>
    </Abyss>
  );
};

// The eye compared with everyday things.
export const EyeSize: React.FC<{ big?: number }> = ({ big = 27 }) => {
  const { f } = useShot();
  const px = 12.5;
  const items = [["HUMAN EYE", 2.4], ["FOOTBALL", 22], ["DINNER PLATE", 26], [`COLOSSAL SQUID · ${big} CM`, big]] as const;
  let x = 200;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #12404e 0%, #020a0e 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {items.map(([t, d], i) => {
          const r = (d * px) / 2;
          const cx = x + r;
          x += r * 2 + 70;
          const last = i === items.length - 1;
          return (
            <g key={i} opacity={pop(f, i * 4)}>
              <circle cx={cx} cy={440} r={r} fill={last ? "#0b0d10" : i === 1 ? "#d9d9d9" : i === 2 ? "#f0ece2" : "#6b8fa0"} stroke={last ? C.accent : "none"} strokeWidth={6} />
              <text x={cx} y={440 + Math.max(r, 30) + 46} textAnchor="middle" fill={last ? C.accent : C.white} fontFamily={FONT} fontWeight={800} fontSize={last ? 34 : 26}>{t}</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// An arm with suckers and swivelling hooks.
export const Hooks: React.FC<{ text?: string; grab?: boolean }> = ({ text, grab = false }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #2a1210 0%, #070202 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <path d="M 100 600 C 600 520 1200 520 1820 560 L 1820 700 C 1200 680 600 680 100 760 Z" fill={RED} />
        {Array.from({ length: 10 }, (_, i) => {
          const x = 240 + i * 160;
          const r = Math.sin(f * 0.2 + i) * (grab ? 50 : 25);
          return (
            <g key={i} transform={`translate(${x} 600)`}>
              <circle r={26} fill="#d9a89c" />
              <g transform={`rotate(${r})`}>
                <path d="M 0 -6 L 0 -60 Q 0 -86 26 -80" stroke="#f4f0e4" strokeWidth={10} fill="none" strokeLinecap="round" />
              </g>
            </g>
          );
        })}
        {grab ? <g transform="translate(900 380)"><Toothfish x={0} y={0} s={1.4} /></g> : null}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// The beak opening and closing in the ring of arms, with the radula.
export const BeakShot: React.FC<{ radula?: boolean; text?: string }> = ({ radula = false, text }) => {
  const { f } = useShot();
  const open = (Math.sin(f * 0.25) + 1) / 2;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #2a1210 0%, #070202 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 8 }, (_, i) => { const a = (i / 8) * Math.PI * 2; return <ellipse key={i} cx={960 + Math.cos(a) * 300} cy={520 + Math.sin(a) * 300} rx={90} ry={150} transform={`rotate(${(a * 180) / Math.PI + 90} ${960 + Math.cos(a) * 300} ${520 + Math.sin(a) * 300})`} fill={RED} />; })}
        <circle cx={960} cy={520} r={190} fill={RED_D} />
        <path d={`M 880 ${520 - 20 - open * 40} Q 960 ${420 - open * 40} 1060 ${500 - open * 30} L 960 ${520 - open * 10} Z`} fill="#1a1410" />
        <path d={`M 880 ${540 + open * 40} Q 960 ${620 + open * 40} 1060 ${540 + open * 30} L 960 ${530 + open * 10} Z`} fill="#2a221c" />
        {radula ? Array.from({ length: 9 }, (_, i) => <path key={i} d={`M ${930 + i * 7} 525 l 3 -8 l 3 8 Z`} fill="#d8d1c4" />) : null}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// The doughnut brain with the oesophagus through it.
export const Brain: React.FC<{ food?: "small" | "big"; text?: string }> = ({ food, text }) => {
  const { f, k } = useShot();
  const fx = 300 + 1300 * ease(k);
  const big = food === "big";
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #2a1210 0%, #070202 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <rect x={100} y={500} width={1720} height={80} rx={40} fill="#c98a7a" opacity={0.8} />
        <ellipse cx={960} cy={540} rx={260} ry={200} fill="#e7c9a6" />
        <ellipse cx={960} cy={540} rx={90} ry={70} fill="#2a1210" />
        <rect x={100} y={512} width={1720} height={56} rx={28} fill="#c98a7a" />
        {food ? <circle cx={big ? Math.min(fx, 860) : fx} cy={540} r={big ? 90 : 22} fill="#f3d36b" /> : null}
        {big && fx > 760 ? <ellipse cx={960} cy={540} rx={270} ry={210} fill="none" stroke={C.red} strokeWidth={10} opacity={0.6 + 0.4 * Math.sin(f * 0.5)} /> : null}
        <text x={960} y={300} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={30}>BRAIN</text>
        <text x={1600} y={480} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={26}>OESOPHAGUS →</text>
      </svg>
      <Title text={text} y={120} />
    </AbsoluteFill>
  );
};

// Three hearts and blue blood.
export const Hearts: React.FC<{ text?: string }> = ({ text }) => {
  const { f } = useShot();
  const beat = (o: number) => 1 + 0.12 * Math.max(0, Math.sin(f * 0.3 + o));
  const heart = (x: number, y: number, s: number, label: string) => (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M 0 30 C -60 -20 -50 -70 0 -40 C 50 -70 60 -20 0 30 Z" fill="#c8564a" />
      <text y={80} textAnchor="middle" fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={20} transform={`scale(${1 / s})`}>{label}</text>
    </g>
  );
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #0b2a38 0%, #01070a 80%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 16 }, (_, i) => { const t = ((f / 60 + i / 16) % 1 + 1) % 1; const a = t * Math.PI * 2; return <circle key={i} cx={960 + Math.cos(a) * 420} cy={520 + Math.sin(a) * 240} r={12} fill="#3a7bd5" />; })}
        {heart(960, 520, 2.2 * beat(0), "BODY HEART")}
        {heart(620, 420, 1.4 * beat(1.5), "GILL HEART")}
        {heart(1300, 420, 1.4 * beat(1.5), "GILL HEART")}
      </svg>
      <Title text={text} />
    </AbsoluteFill>
  );
};

// A small glass squid growing into a red giant.
export const Grow: React.FC = () => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <Abyss>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <g opacity={1 - e}><Squid x={960} y={300 + 300 * e} s={0.25 + 0.5 * e} glass f={f} /></g>
        <g opacity={e}><Squid x={960} y={300 + 300 * e} s={0.25 + 0.5 * e} f={f} /></g>
      </svg>
    </Abyss>
  );
};
