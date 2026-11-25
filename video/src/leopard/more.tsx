// More drawn shots for the leopard seal video: close-ups, diagrams and rule cards.
import React from "react";
import { AbsoluteFill, interpolate, random } from "remotion";
import { registerKind } from "../kit/edit-rules";
import { HUD, MONO } from "../kit/hud";
import { Backdrop, ease, Label, pop, Svg, useShot } from "../kit/shots";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { Drift, Snow } from "../kit/vfx";
import { Seal } from "./draw";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";
const Title: React.FC<{ text: string; y?: number; color?: string }> = ({ text, y = 150, color = C.white }) => {
  const { f } = useShot();
  return <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 72, color, textShadow: SHADOW, opacity: pop(f, 2) }}>{text}</div>;
};

// The head, big. mode: plain, jaw (opening), eye (highlight), curve (traces the upturned mouth), lines (long, flat).
export const HeadClose: React.FC<{ mode?: "plain" | "jaw" | "eye" | "curve" | "lines" | "hinge"; dark?: boolean; label?: string }> = ({ mode = "plain", dark = false, label }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const jaw = mode === "jaw" ? e : mode === "hinge" ? 0.35 : 0.04;
  // The head of a seal at scale 3.1, placed so the head fills the frame.
  const S = 3.1;
  const X = -40;
  const Y = 560;
  const px = (x: number) => X + x * S;
  const py = (y: number) => Y + y * S;
  return (
    <AbsoluteFill style={{ background: dark ? "radial-gradient(ellipse at 60% 45%, #0b2a36 0%, #01070a 80%)" : "radial-gradient(ellipse at 60% 45%, #1a5a70 0%, #04161e 80%)", overflow: "hidden" }}>
      <Drift amount={0.4} focus={false}>
        <Svg>
          <Seal x={X} y={Y} s={S} jaw={jaw} f={f * 0.3} />
          {mode === "eye" ? <circle cx={px(386)} cy={py(-34)} r={60 + Math.sin(f * 0.3) * 6} fill="none" stroke={C.accent} strokeWidth={6} opacity={e} /> : null}
          {mode === "curve" ? <path d={`M ${px(466)} ${py(6)} C ${px(420)} ${py(10)} ${px(360)} ${py(14)} ${px(322)} ${py(12)} C ${px(312)} ${py(10)} ${px(306)} ${py(2)} ${px(302)} ${py(-8)}`} stroke={C.accent} strokeWidth={10} fill="none" strokeDasharray={`${e * 900} 9999`} strokeLinecap="round" /> : null}
          {mode === "lines" ? (
            <g opacity={e}>
              <line x1={px(300)} y1={py(-80)} x2={px(475)} y2={py(-80)} stroke={C.accent} strokeWidth={6} />
              <line x1={px(300)} y1={py(-90)} x2={px(300)} y2={py(-70)} stroke={C.accent} strokeWidth={6} />
              <line x1={px(475)} y1={py(-90)} x2={px(475)} y2={py(-70)} stroke={C.accent} strokeWidth={6} />
            </g>
          ) : null}
          {mode === "hinge" ? <circle cx={px(318)} cy={py(14)} r={34} fill="none" stroke={C.accent} strokeWidth={6} opacity={e} /> : null}
        </Svg>
      </Drift>
      <Snow n={40} opacity={0.6} seed="hc" />
      {label ? <Title text={label} /> : null}
    </AbsoluteFill>
  );
};

// Teeth diagram. canine: the long front teeth; trident: one three-pointed cheek tooth; lock: rows interlocking;
// comb: next to a comb; suck: water drawn in; filter: water out between the teeth; trapped: krill stay inside.
export const TeethShot: React.FC<{ mode: "canine" | "trident" | "lock" | "comb" | "suck" | "filter" | "trapped"; label?: string }> = ({ mode, label }) => {
  const { f, k } = useShot();
  const e = ease(k);
  const tooth = (x: number, y: number, s: number, down: boolean, key: string | number) => (
    <path key={key} transform={`translate(${x} ${y}) scale(${s} ${down ? s : -s})`} d="M -40 0 L -30 -40 L -18 -14 L 0 -70 L 18 -14 L 30 -40 L 40 0 Z" fill="#f1ede2" stroke="#b9b2a0" strokeWidth={3} />
  );
  const row = (y: number, down: boolean, off: number) => Array.from({ length: 6 }, (_, i) => tooth(420 + i * 190 + off, y, 1.2, down, `${down}${i}`));
  const gap = mode === "lock" ? lerp(80, 0, e) : 0;
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 45%, #4a1820 0%, #14050a 80%)" specks={false}>
      <Svg>
        {mode === "canine" ? (
          <g>
            <path d="M 300 380 Q 960 300 1620 380 L 1620 300 L 300 300 Z" fill="#7a2a34" />
            {[560, 1360].map((x, i) => <path key={i} d={`M ${x - 40} 360 L ${x} ${360 + 220 * (0.4 + 0.6 * e)} L ${x + 40} 360 Z`} fill="#f4f0e6" stroke="#b9b2a0" strokeWidth={4} />)}
            {[700, 820, 940, 1060, 1180].map((x) => <path key={x} d={`M ${x - 20} 360 L ${x} 420 L ${x + 20} 360 Z`} fill="#f4f0e6" />)}
          </g>
        ) : null}
        {mode === "trident" ? tooth(960, 700, 5 * (0.6 + 0.4 * pop(f, 0, 10)), true, "t") : null}
        {mode === "trident" ? [[760, 400], [960, 360], [1160, 400]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={40} fill="none" stroke={C.accent} strokeWidth={6} opacity={pop(f, 6 + i * 4)} />) : null}
        {mode === "lock" || mode === "comb" || mode === "suck" || mode === "filter" || mode === "trapped" ? (
          <g>
            <g transform={`translate(0 ${-gap})`}>{row(540, true, 0)}</g>
            <g transform={`translate(0 ${gap})`}>{row(540, false, 95)}</g>
          </g>
        ) : null}
        {mode === "comb" ? (
          <g transform={`translate(${lerp(1900, 960, pop(f, 4, 12))} 860)`}>
            <rect x={-420} y={-40} width={840} height={40} rx={10} fill={C.accent} />
            {Array.from({ length: 40 }, (_, i) => <rect key={i} x={-410 + i * 21} y={0} width={10} height={90} fill={C.accent} />)}
          </g>
        ) : null}
        {mode === "suck"
          ? Array.from({ length: 10 }, (_, i) => {
              const t = ((f / 20 + i / 10) % 1 + 1) % 1;
              return <path key={i} d={`M ${1900 - t * 1400} ${300 + i * 50} l -50 0 l 14 -10 m -14 10 l 14 10`} stroke="#7fe9ff" strokeWidth={6} fill="none" opacity={1 - t} />;
            })
          : null}
        {mode === "filter"
          ? Array.from({ length: 10 }, (_, i) => {
              const t = ((f / 20 + i / 10) % 1 + 1) % 1;
              return <path key={i} d={`M ${500 + (i % 6) * 190} ${560 - 40 + t * 380} l 0 40 l -10 -14 m 10 14 l 10 -14`} stroke="#7fe9ff" strokeWidth={6} fill="none" opacity={1 - t} />;
            })
          : null}
        {mode === "trapped" || mode === "suck"
          ? Array.from({ length: 30 }, (_, i) => <ellipse key={i} cx={460 + random(`kt${i}`) * 1000} cy={260 + random(`ku${i}`) * 200 + Math.sin(f * 0.2 + i) * 6} rx={14} ry={6} fill="#ff8fa0" opacity={mode === "suck" ? e : 1} />)
          : null}
      </Svg>
      {label ? <Label text={label} x={160} y={150} size={40} color={C.accent} /> : null}
    </Backdrop>
  );
};

// Tiny krill beside a paperclip, or a whole seal: the range of prey one mouth handles.
export const SmallBig: React.FC<{ big?: boolean }> = ({ big = false }) => {
  const { f } = useShot();
  return (
    <Backdrop v="deep">
      <Svg>
        <g opacity={big ? 0.35 : 1}>
          <ellipse cx={420} cy={560} rx={60} ry={22} fill="#ff8fa0" />
          <path d="M 520 520 L 700 520 Q 740 520 740 560 Q 740 600 700 600 L 540 600 Q 520 600 520 580 L 520 540 Q 520 530 540 530 L 690 530" stroke="#cfd8dc" strokeWidth={8} fill="none" transform="scale(0.8) translate(140 120)" />
        </g>
        <g opacity={big ? 1 : 0.35}>
          <Seal x={1300} y={560} s={0.75} f={f} />
        </g>
      </Svg>
      <div style={{ position: "absolute", left: 220, top: 700, fontFamily: FONT, fontWeight: 800, fontSize: 56, color: big ? "rgba(255,255,255,0.4)" : C.accent, textShadow: SHADOW }}>KRILL</div>
      <div style={{ position: "absolute", left: 1150, top: 760, fontFamily: FONT, fontWeight: 800, fontSize: 56, color: big ? C.accent : "rgba(255,255,255,0.4)", textShadow: SHADOW }}>A SEAL</div>
    </Backdrop>
  );
};

// The coat, with one part pointed out: back, throat or spots.
export const CoatShot: React.FC<{ part: "back" | "throat" | "spots" }> = ({ part }) => {
  const { f } = useShot();
  const p = pop(f, 3, 10);
  const pts = { back: [860, 380, "DARK GREY BACK"], throat: [1300, 620, "PALE THROAT AND SIDES"], spots: [760, 520, "DARK SPOTS"] } as const;
  const [x, y, t] = pts[part];
  return (
    <Backdrop v="deep">
      <Svg>
        <Seal x={900} y={540} s={1.8} f={f * 0.4} />
        <circle cx={x} cy={y} r={110 * (0.6 + 0.4 * p)} fill="none" stroke={C.accent} strokeWidth={6} opacity={p} />
      </Svg>
      <Label text={t} x={x - 100} y={y - 190} size={42} color={C.accent} />
    </Backdrop>
  );
};

// Seal spots beside leopard rosettes.
export const SpotsCompare: React.FC = () => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 958, height: 1080, background: "#a9b4ba" }}>
        <Svg>
          {Array.from({ length: 60 }, (_, i) => <ellipse key={i} cx={random(`a${i}`) * 958} cy={random(`b${i}`) * 1080} rx={14 + random(`c${i}`) * 16} ry={9 + random(`d${i}`) * 9} fill="#2b3238" opacity={pop(f, i % 10)} />)}
        </Svg>
      </div>
      <div style={{ position: "absolute", left: 962, top: 0, width: 958, height: 1080, background: "#d9a85a" }}>
        <svg width={958} height={1080} style={{ position: "absolute" }}>
          {Array.from({ length: 40 }, (_, i) => (
            <g key={i} transform={`translate(${random(`e${i}`) * 958} ${random(`g${i}`) * 1080})`} opacity={pop(f, 4 + (i % 10))}>
              <circle r={26} fill="none" stroke="#2a1a0a" strokeWidth={9} strokeDasharray="22 10" />
              <circle r={14} fill="#a8742e" />
            </g>
          ))}
        </svg>
      </div>
      <div style={{ position: "absolute", left: 956, top: 0, width: 8, height: 1080, background: C.accent }} />
      <div style={{ position: "absolute", left: 0, width: 958, top: 150, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: "#fff", textShadow: SHADOW }}>LEOPARD SEAL</div>
      <div style={{ position: "absolute", left: 962, width: 958, top: 150, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: "#fff", textShadow: SHADOW }}>LEOPARD</div>
    </AbsoluteFill>
  );
};

// Female beside male: the female is the bigger one.
export const SexScale: React.FC = () => {
  const { f } = useShot();
  const g = ease(f / 14);
  return (
    <Backdrop v="deep">
      <Svg>
        <Seal x={900} y={400} s={0.95 * (0.8 + 0.2 * g)} f={f} />
        <Seal x={800} y={760} s={0.66 * (0.8 + 0.2 * g)} f={f + 9} />
      </Svg>
      <Label text="FEMALE" x={260} y={250} size={46} color={C.accent} />
      <Label text="MALE" x={300} y={640} size={46} />
    </Backdrop>
  );
};

// A penguin being whipped at the surface: shown as motion and spray, not gore.
export const Thrash: React.FC<{ z?: number }> = ({ z = 1 }) => {
  const { f } = useShot();
  const a = Math.sin(f * 0.6) * 70;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#8fa9bb 0%, #cddbe3 52%, #1f4d60 52%, #0c2c3a 100%)", overflow: "hidden" }}>
      <Svg>
        <g transform={`translate(960 600) scale(${z}) translate(-960 -600)`}>
          <g transform={`translate(960 600) rotate(-70)`}>
            <Seal x={0} y={0} s={0.6} jaw={0.3} f={f} />
          </g>
          <g transform={`translate(960 ${380 + Math.abs(Math.sin(f * 0.6)) * 40}) rotate(${a})`}>
            <ellipse cx={0} cy={-120} rx={18} ry={36} fill="#16191c" />
            <ellipse cx={4} cy={-116} rx={10} ry={26} fill="#f2f4f5" />
          </g>
          {Array.from({ length: 26 }, (_, i) => {
            const t = ((f / 14 + random(`th${i}`)) % 1 + 1) % 1;
            return <circle key={i} cx={960 + (random(`ti${i}`) - 0.5) * 600 * t} cy={560 - Math.sin(t * Math.PI) * 260 * random(`tj${i}`)} r={5 + random(`tk${i}`) * 10} fill="#eef7fa" opacity={0.85 * (1 - t)} />;
          })}
        </g>
      </Svg>
      <Snow n={30} opacity={0.5} seed="th" />
    </AbsoluteFill>
  );
};

// A climbing boot with crampon spikes, kicking.
export const Crampon: React.FC<{ label?: boolean }> = ({ label = false }) => {
  const { f } = useShot();
  const kick = Math.max(0, Math.sin(f * 0.5)) * 60;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#cddbe3 0%, #e8eff3 60%, #1f4d60 60%)", overflow: "hidden" }}>
      <Svg>
        <g transform={`translate(${700 + kick * 3} 520) rotate(${-10 + kick * 0.3})`}>
          <rect x={-60} y={-360} width={120} height={300} rx={30} fill="#3a3f46" />
          <path d="M -80 -80 L 160 -80 Q 220 -80 220 -30 L 220 0 L -80 0 Z" fill="#7a2a20" />
          {Array.from({ length: 8 }, (_, i) => <path key={i} d={`M ${-60 + i * 36} 0 l 12 50 l 12 -50 Z`} fill="#c9d2d8" stroke="#555" strokeWidth={2} />)}
          <path d="M 220 -20 l 60 20 l -60 10 Z" fill="#c9d2d8" />
        </g>
        <g transform="translate(1380 700) rotate(-70)">
          <Seal x={0} y={0} s={0.7} jaw={0.4} f={f} />
        </g>
        {kick > 50 ? <circle cx={1250} cy={560} r={60} fill="none" stroke="#fff" strokeWidth={8} opacity={0.8} /> : null}
      </Svg>
      {label ? <Label text="CRAMPONS · STEEL SPIKES" x={160} y={150} size={42} color={C.accent} /> : null}
    </AbsoluteFill>
  );
};

// A timeline of known encounters from 1916 to today. red marks the one death.
export const Timeline: React.FC<{ marks: number[]; red?: number; title?: string }> = ({ marks, red, title }) => {
  const { f } = useShot();
  const X = (y: number) => 200 + ((y - 1910) / 120) * 1520;
  const g = ease(f / 18);
  return (
    <Backdrop v="night">
      <Svg>
        <line x1={200} y1={560} x2={200 + 1520 * g} y2={560} stroke="#2f6a74" strokeWidth={8} />
        {[1916, 1950, 1985, 2003, 2026].map((y) => <text key={y} x={X(y)} y={640} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={32} textAnchor="middle" opacity={g}>{y}</text>)}
        {marks.map((y, i) => <circle key={y} cx={X(y)} cy={560} r={22 * pop(f, 4 + i * 4)} fill={C.accent} />)}
        {red ? <circle cx={X(red)} cy={560} r={30 * pop(f, 10)} fill={C.red} stroke="#fff" strokeWidth={5} /> : null}
      </Svg>
      {title ? <Label text={title} x={200} y={380} size={42} /> : null}
    </Backdrop>
  );
};

// Three things it can decide. hi: which one is lit.
export const Choices: React.FC<{ hi?: number; all?: boolean }> = ({ hi = -1, all = false }) => {
  const { f } = useShot();
  const items = ["NOT FOOD · IT LEAVES", "CURIOUS · IT FOLLOWS", "PREY"];
  return (
    <Backdrop v="deep">
      <Svg>
        <Seal x={420} y={560} s={0.55} f={f} />
        {items.map((_, i) => <path key={i} d={`M 700 560 C 900 560 950 ${300 + i * 260} 1150 ${300 + i * 260}`} stroke={i === hi ? (i === 2 ? C.red : C.accent) : "rgba(127,233,255,0.4)"} strokeWidth={i === hi ? 10 : 5} fill="none" strokeDasharray={`${ease((f - i * 3) / 12) * 700} 9999`} />)}
      </Svg>
      {items.map((t, i) => (
        <div key={i} style={{ position: "absolute", left: 1180, top: 270 + i * 260, fontFamily: FONT, fontWeight: 800, fontSize: 52, color: all ? "#fff" : i === hi ? (i === 2 ? C.red : C.accent) : "rgba(255,255,255,0.45)", textShadow: SHADOW, opacity: pop(f, 4 + i * 3) }}>{t}</div>
      ))}
    </Backdrop>
  );
};

// What it eats, one icon at a time.
export const PreyRow: React.FC<{ n: number; hi?: number }> = ({ n, hi = -1 }) => {
  const { f } = useShot();
  const names = ["KRILL", "FISH", "SQUID", "PENGUINS", "SEALS"];
  const icon = (i: number) =>
    i === 0 ? <ellipse cx={0} cy={0} rx={50} ry={18} fill="#ff8fa0" /> :
    i === 1 ? <path d="M -70 0 Q 0 -45 60 0 Q 0 45 -70 0 Z M 60 0 L 95 -28 L 95 28 Z" fill="#9fc3cf" /> :
    i === 2 ? <path d="M 0 -70 L 30 0 L 22 60 L 8 20 L 0 70 L -8 20 L -22 60 L -30 0 Z" fill="#e0a6b6" /> :
    i === 3 ? <g><ellipse cx={0} cy={0} rx={26} ry={52} fill="#16191c" /><ellipse cx={4} cy={6} rx={16} ry={40} fill="#f2f4f5" /><circle cx={0} cy={-46} r={18} fill="#16191c" /></g> :
    <g transform="scale(0.24)"><Seal x={0} y={0} f={f} /></g>;
  return (
    <Backdrop v="deep">
      <Svg>
        {names.slice(0, n).map((_, i) => (
          <g key={i} transform={`translate(${260 + i * 350} 520) scale(${0.6 + 0.4 * pop(f, i === n - 1 ? 2 : 0, 8)})`}>
            <rect x={-140} y={-140} width={280} height={280} rx={28} fill={i === hi ? "rgba(255,210,63,0.15)" : "rgba(127,233,255,0.08)"} stroke={i === hi ? C.accent : HUD} strokeWidth={5} />
            {icon(i)}
          </g>
        ))}
      </Svg>
      {names.slice(0, n).map((t, i) => <div key={i} style={{ position: "absolute", left: 260 + i * 350 - 140, width: 280, top: 700, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 40, color: i === hi ? C.accent : "#fff", textShadow: SHADOW }}>{t}</div>)}
    </Backdrop>
  );
};

// A pale crabeater seal with parallel scars drawing in.
export const Scars: React.FC<{ z?: number }> = ({ z = 1 }) => {
  const { f, k } = useShot();
  const e = ease(k * 1.4);
  return (
    <Backdrop v="deep">
      <Svg>
        <g transform={`translate(960 540) scale(${z}) translate(-960 -540)`}>
          <g transform="translate(960 560) scale(1.5)">
            <path d="M 300 0 C 280 -50 180 -70 40 -66 C -120 -62 -260 -40 -330 -8 L -330 12 C -240 44 -100 64 40 64 C 180 64 280 46 300 0 Z" fill="#cfc6b4" />
            <circle cx={240} cy={-20} r={6} fill="#222" />
            {[0, 1, 2].map((i) => <path key={i} d={`M ${-60 + i * 26} -50 C ${-20 + i * 26} -10 ${20 + i * 26} 20 ${60 + i * 26} 50`} stroke="#8a4a3a" strokeWidth={6} fill="none" strokeDasharray={`${e * 160} 999`} strokeLinecap="round" />)}
          </g>
        </g>
      </Svg>
      <Label text="CRABEATER SEAL · SCARS" x={160} y={150} size={40} color={C.accent} />
    </Backdrop>
  );
};

// One safety rule with its own small drawing.
export const Rule: React.FC<{ n: number; text: string; pic: "water" | "distance" | "between" | "feed" | "dog" | "edge" | "calm" | "splash" }> = ({ n, text, pic }) => {
  const { f } = useShot();
  const e = ease(f / 16);
  return (
    <Backdrop v="deep">
      <div style={{ position: "absolute", left: 140, top: 300, width: 860 }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 170, color: "transparent", WebkitTextStroke: `4px ${C.accent}`, lineHeight: 1, opacity: pop(f) }}>{String(n).padStart(2, "0")}</div>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 66, color: "#fff", lineHeight: 1.08, marginTop: 20, textShadow: SHADOW, opacity: pop(f, 3), whiteSpace: "pre-line" }}>{text}</div>
      </div>
      <Svg>
        <g transform="translate(1420 560)">
          <rect x={-330} y={-280} width={660} height={560} rx={30} fill="rgba(127,233,255,0.06)" stroke={HUD} strokeWidth={4} />
          {pic === "water" ? <g><rect x={-330} y={0} width={660} height={280} fill="#1f4d60" /><g transform="scale(0.35)"><Seal x={0} y={420} f={f} /></g><line x1={-200} y1={-200} x2={200} y2={200} stroke={C.red} strokeWidth={14} /></g> : null}
          {pic === "distance" ? <g><g transform="translate(120 60) scale(0.35)"><Seal x={0} y={0} f={f} /></g><circle cx={-240} cy={-20} r={24} fill={HUD} /><rect x={-264} y={4} width={48} height={90} rx={16} fill={HUD} /><line x1={-200} y1={140} x2={-200 + 300 * e} y2={140} stroke={C.accent} strokeWidth={8} strokeDasharray="20 10" /><text x={-60} y={210} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={60}>20 M</text></g> : null}
          {pic === "between" ? <g><rect x={-330} y={80} width={260} height={200} fill="#1f4d60" /><g transform="translate(160 40) scale(0.32)"><Seal x={0} y={0} f={f} flip /></g><circle cx={-20} cy={-40} r={24} fill={C.red} /><rect x={-44} y={-16} width={48} height={90} rx={16} fill={C.red} /><path d="M 80 60 L -200 160" stroke={C.accent} strokeWidth={6} strokeDasharray="14 8" /></g> : null}
          {pic === "feed" ? <g><g transform="scale(0.4)"><Seal x={0} y={0} f={f} /></g><path d="M -200 -120 l 30 0 l -15 -40 Z" fill="#9fc3cf" /><line x1={-220} y1={-220} x2={220} y2={220} stroke={C.red} strokeWidth={14} /></g> : null}
          {pic === "dog" ? <g><ellipse cx={-120} cy={60} rx={70} ry={36} fill="#b88a5a" /><circle cx={-50} cy={20} r={30} fill="#b88a5a" /><g transform="translate(150 80) scale(0.3)"><Seal x={0} y={0} f={f} flip /></g><line x1={-220} y1={-220} x2={220} y2={220} stroke={C.red} strokeWidth={14} /></g> : null}
          {pic === "edge" ? <g><rect x={-330} y={40} width={660} height={240} fill="#1f4d60" /><rect x={-330} y={0} width={360} height={40} fill="#f4fafc" /><g transform="translate(120 80) rotate(-60) scale(0.3)"><Seal x={0} y={0} f={f} /></g></g> : null}
          {pic === "calm" || pic === "splash" ? <g><rect x={-330} y={-60} width={660} height={340} fill="#1f4d60" />{Array.from({ length: pic === "splash" ? 14 : 3 }, (_, i) => <circle key={i} cx={-100 + (i % 5) * 50} cy={-60 - (i % 3) * 30 * (pic === "splash" ? Math.abs(Math.sin(f * 0.4 + i)) : 0)} r={10} fill="#eef7fa" />)}{pic === "splash" ? <line x1={-220} y1={-220} x2={220} y2={220} stroke={C.red} strokeWidth={14} /> : null}</g> : null}
        </g>
      </Svg>
    </Backdrop>
  );
};

registerKind("drawn", HeadClose, Thrash, Crampon);
registerKind("graphic", TeethShot, SmallBig, CoatShot, SpotsCompare, SexScale, Timeline, Choices, PreyRow, Scars, Rule);

export { lerp, clamp, interpolate };
