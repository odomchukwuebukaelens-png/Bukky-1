// Shot library: every shot fills the frame, moves for its whole length, and lasts about two seconds.
// Shots are placed by the shot engine (video/src/croc/ShotScene.tsx) inside a Sequence, so
// useCurrentFrame() starts at 0 for each shot and useVideoConfig().durationInFrames is the shot length.
import React from "react";
import { AbsoluteFill, Img, interpolate, OffthreadVideo, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CrocSide, CrocTop, Person } from "./devices";
import { HUD, MONO } from "./hud";
import { CrocHead, Deep, Shore } from "./sets";
import { C } from "./theme";
import { FONT } from "./ui";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const useShot = () => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  return { f, dur, k: Math.min(1, f / Math.max(1, dur)) };
};
const ease = (t: number) => {
  const x = Math.min(1, Math.max(0, t));
  return x * x * (3 - 2 * x);
};
const pop = (f: number, at = 0, len = 8) => {
  const t = Math.min(1, Math.max(0, (f - at) / len));
  return 1 - Math.pow(1 - t, 3);
};
const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";
const Svg: React.FC<{ children: React.ReactNode; opacity?: number }> = ({ children, opacity = 1 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, opacity, overflow: "visible" }} width={1920} height={1080}>
    {children}
  </svg>
);

// ---------- Text that sits on top of a shot ----------

export const Kicker: React.FC<{ text: string; color?: string; size?: number; y?: number; x?: number; align?: "left" | "center" | "right"; width?: number }> = ({
  text,
  color = C.white,
  size = 96,
  y = 200,
  x = 130,
  align = "left",
  width = 1660,
}) => {
  const { f } = useShot();
  const p = pop(f, 1, 7);
  return (
    <div style={{ position: "absolute", left: x, top: y, width, textAlign: align, opacity: p, transform: `translateY(${(1 - p) * 30}px) scale(${0.92 + 0.08 * p})`, transformOrigin: align === "center" ? "center top" : "left top" }}>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1.03, color, whiteSpace: "pre-line", textShadow: SHADOW, WebkitTextStroke: "2px rgba(0,0,0,0.5)" }}>{text}</div>
    </div>
  );
};

export const Label: React.FC<{ text: string; x: number; y: number; color?: string; size?: number }> = ({ text, x, y, color = HUD, size = 34 }) => {
  const { f } = useShot();
  const typed = text.slice(0, Math.max(0, Math.floor((f - 3) * 2)));
  return <div style={{ position: "absolute", left: x, top: y, fontFamily: MONO, fontWeight: 700, fontSize: size, letterSpacing: 2, color, textShadow: SHADOW, whiteSpace: "nowrap" }}>{typed}</div>;
};

// ---------- Backgrounds ----------

const BG: Record<string, string> = {
  deep: "radial-gradient(ellipse at 50% 35%, #12505e 0%, #062530 55%, #01090c 100%)",
  dusk: "linear-gradient(#2b2a4c 0%, #7a4a5e 45%, #e08a50 100%)",
  red: "radial-gradient(ellipse at 50% 45%, #6e1a12 0%, #2a0806 60%, #0c0202 100%)",
  night: "radial-gradient(ellipse at 50% 30%, #0f2433 0%, #04090d 70%)",
  mud: "radial-gradient(ellipse at 50% 40%, #5a4a2a 0%, #2a2214 60%, #100c06 100%)",
  gold: "radial-gradient(ellipse at 50% 40%, #6a5418 0%, #2a2008 60%, #0c0902 100%)",
  sea: "linear-gradient(#0e4a66 0%, #0a2f45 50%, #04131e 100%)",
  paper: "radial-gradient(ellipse at 50% 40%, #e9dfc4 0%, #cdbf98 70%, #a8986e 100%)",
};

export const Backdrop: React.FC<{ v?: keyof typeof BG | string; children?: React.ReactNode; specks?: boolean }> = ({ v = "deep", children, specks = true }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: BG[v] ?? v }}>
      {specks
        ? Array.from({ length: 34 }, (_, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: (random(`bx${i}`) * 1920 + f * (0.4 + random(`bv${i}`))) % 1920,
                top: (random(`by${i}`) * 1080 - f * (0.3 + random(`bw${i}`) * 0.6) + 1080) % 1080,
                width: 4 + random(`bs${i}`) * 6,
                height: 4 + random(`bs${i}`) * 6,
                borderRadius: 6,
                background: "#e8f4f6",
                opacity: 0.08 + random(`bo${i}`) * 0.16,
              }}
            />
          ))
        : null}
      {children}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.6) 100%)" }} />
    </AbsoluteFill>
  );
};

// ---------- Real footage and photos ----------

const RELATED: Record<string, string> = {
  "11138": "NILE CROCODILE · A CLOSE RELATIVE",
  "11184": "NILE CROCODILE · A CLOSE RELATIVE",
  "11262": "NILE CROCODILE · A CLOSE RELATIVE",
  "11271": "NILE CROCODILE · A CLOSE RELATIVE",
  "21932": "NILE CROCODILE · A CLOSE RELATIVE",
  "27364": "NILE CROCODILE · A CLOSE RELATIVE",
  "9433": "CROCODILE · A CLOSE RELATIVE",
  "4120": "CROCODILE · A CLOSE RELATIVE",
  "22158": "NILE CROCODILES · CLOSE RELATIVES",
  "22159": "NILE CROCODILE · A CLOSE RELATIVE",
  "22160": "NILE CROCODILE · A CLOSE RELATIVE",
  "22161": "NILE CROCODILES · CLOSE RELATIVES",
  "26031": "NILE CROCODILE · A CLOSE RELATIVE",
  "26032": "YOUNG CROCODILES · A CLOSE RELATIVE",
  "26036": "YOUNG CROCODILES · A CLOSE RELATIVE",
  "13991": "CROCODILE SKIN · A CLOSE RELATIVE",
  "14385": "CROCODILE SKIN · A CLOSE RELATIVE",
  "30706": "AMERICAN ALLIGATOR · A RELATIVE",
  "32703": "AMERICAN ALLIGATOR · A RELATIVE",
  "32704": "AMERICAN ALLIGATOR · A RELATIVE",
  "32706": "AMERICAN ALLIGATOR · A RELATIVE",
  "32707": "AMERICAN ALLIGATOR · A RELATIVE",
};

// A two-second piece of a free Mixkit clip, cut by tools/cut_footage.py to footage/croc2/v<id>_<t>.mp4.
export const V: React.FC<{ id: string; t?: number; dir?: number; zoom?: number; rate?: number }> = ({ id, t = 0, dir = 1, zoom = 1.06, rate = 1 }) => {
  const { k } = useShot();
  const s = zoom + 0.08 * k;
  const label = RELATED[id];
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <OffthreadVideo
        src={staticFile(`footage/croc2/v${id}_${t}.mp4`)}
        muted
        playbackRate={rate}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${s}) translateX(${dir * (k - 0.5) * 30}px)`, filter: "saturate(0.92) contrast(1.06)" }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(rgba(0,0,0,0.25), transparent 30%, transparent 70%, rgba(0,0,0,0.35))" }} />
      {label ? <div style={{ position: "absolute", right: 130, top: 160, fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 2, color: "rgba(255,255,255,0.75)", textShadow: SHADOW }}>{label}</div> : null}
    </AbsoluteFill>
  );
};

// A free-licence photo with a slow push or pan. Credit sits small in the corner.
export const P: React.FC<{ name: string; credit: string; ox?: string; oy?: string; from?: number; to?: number }> = ({ name, credit, ox = "50%", oy = "50%", from = 1.04, to = 1.16 }) => {
  const { k } = useShot();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Img src={staticFile(`footage/croc2/${name}.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: `${ox} ${oy}`, transform: `scale(${from + (to - from) * k})`, transformOrigin: `${ox} ${oy}` }} />
      <AbsoluteFill style={{ background: "linear-gradient(rgba(0,0,0,0.3), transparent 30%, transparent 70%, rgba(0,0,0,0.35))" }} />
      <div style={{ position: "absolute", right: 130, top: 160, fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 2, color: "rgba(255,255,255,0.75)", textShadow: SHADOW }}>PHOTO · {credit}</div>
    </AbsoluteFill>
  );
};

// ---------- Drawn scenes ----------

export const RiverPOV: React.FC<{ z0?: number; z1?: number; zx?: number; zy?: number; eyes?: boolean; sink?: boolean; rise?: boolean; glow?: boolean; night?: boolean; ripples?: boolean; legs?: boolean; children?: React.ReactNode }> = ({
  z0 = 1,
  z1 = 1.12,
  zx = 1150,
  zy = 470,
  eyes = true,
  sink = false,
  rise = false,
  glow = false,
  night = false,
  ripples = false,
  legs = false,
  children,
}) => {
  const { f, k } = useShot();
  const show = !eyes ? 0 : sink ? 1 - ease(k * 1.4) : rise ? ease(k * 1.4) : 1;
  const zoom = z0 + (z1 - z0) * ease(k);
  return (
    <AbsoluteFill style={{ background: "#0d0f0a" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - zx * zoom}px, ${540 - zy * zoom}px) scale(${zoom})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -500, top: -500, width: 2920, height: 900, background: night ? "linear-gradient(#05070f, #101828)" : "linear-gradient(#2a2a4a 0%, #6c4a6e 45%, #d98a52 85%, #f0b06a 100%)" }} />
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <path d={`M -500 400 ${Array.from({ length: 64 }, (_, i) => `L ${-500 + i * 46} ${360 - random(`rk${i}`) * 50 - (i % 7 === 0 ? 30 : 0)}`).join(" ")} L 2420 400 Z`} fill="#14180f" />
        </svg>
        <div style={{ position: "absolute", left: -500, top: 398, width: 2920, height: 1300, background: night ? "linear-gradient(#141c22, #05080a)" : "linear-gradient(#8a6a3a 0%, #5a4a28 14%, #3b3a20 40%, #1c1d11 100%)" }} />
        {Array.from({ length: 40 }, (_, i) => {
          const y = 410 + Math.pow(random(`ry${i}`), 1.7) * 680;
          return <div key={i} style={{ position: "absolute", left: ((random(`rx${i}`) * 2700 + f * (0.4 + ((y - 400) / 680) * 1.4)) % 2900) - 500, top: y, width: 60 + ((y - 400) / 680) * 300, height: 3 + ((y - 400) / 680) * 5, borderRadius: 4, background: night ? "#5d7380" : "#c9a465", opacity: 0.12 + random(`ro${i}`) * 0.14 }} />;
        })}
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          <g transform={`translate(1150 ${470 + (1 - show) * 30})`} opacity={Math.min(1, show * 1.5)}>
            <ellipse cx={-50} cy={0} rx={30} ry={20} fill="#14160d" />
            <ellipse cx={50} cy={0} rx={30} ry={20} fill="#14160d" />
            <ellipse cx={0} cy={48} rx={26} ry={12} fill="#14160d" />
            <ellipse cx={-50} cy={-5} rx={13} ry={8} fill={glow ? "#ff3b2a" : "#e9d98a"} />
            <ellipse cx={50} cy={-5} rx={13} ry={8} fill={glow ? "#ff3b2a" : "#e9d98a"} />
            <rect x={-53} y={-12} width={5} height={14} rx={2} fill="#111" />
            <rect x={47} y={-12} width={5} height={14} rx={2} fill="#111" />
          </g>
          {ripples || sink || rise
            ? [0, 1, 2].map((i) => {
                const t = ((f / 40 + i / 3) % 1 + 1) % 1;
                return <ellipse key={i} cx={1150} cy={480} rx={60 + t * 260} ry={14 + t * 50} fill="none" stroke="#e3c184" strokeWidth={3} opacity={0.6 * (1 - t)} />;
              })
            : null}
        </svg>
        {children}
      </AbsoluteFill>
      {legs ? (
        <Svg>
          <rect x={700} y={980} width={150} height={200} rx={60} fill="#1b2a33" />
          <rect x={1070} y={980} width={150} height={200} rx={60} fill="#1b2a33" />
        </Svg>
      ) : null}
    </AbsoluteFill>
  );
};

type Mover = { x0: number; x1: number; y?: number; s?: number; rot?: number; jaw?: number | "snap" | "open"; flip?: boolean; plates?: number };
const jawOf = (j: Mover["jaw"], f: number) => (j === "snap" ? Math.max(0, 30 * Math.sin(f * 0.5)) : j === "open" ? Math.min(30, f * 2.5) : j ?? 0);

export const ShoreShot: React.FC<{ croc?: Mover; person?: { x0: number; x1?: number; y?: number; s?: number; lean?: number; run?: boolean }; night?: boolean; z0?: number; z1?: number; zx?: number; zy?: number; over?: React.ReactNode; children?: React.ReactNode }> = ({
  croc,
  person,
  night = false,
  z0 = 1.05,
  z1 = 1.12,
  zx = 900,
  zy = 560,
  over,
  children,
}) => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <Shore
      night={night ? 1 : 0}
      zoom={z0 + (z1 - z0) * e}
      zx={zx}
      zy={zy}
      croc={croc ? { x: croc.x0 + (croc.x1 - croc.x0) * e, y: croc.y ?? 700, scale: croc.s ?? 0.6, rot: croc.rot ?? 0, jaw: jawOf(croc.jaw, f), flip: croc.flip, plates: croc.plates } : undefined}
      person={person ? { x: person.x0 + ((person.x1 ?? person.x0) - person.x0) * e, y: person.y ?? 522, scale: person.s ?? 1.3, lean: (person.lean ?? 0) + (person.run ? Math.sin(f * 0.8) * 8 : 0) } : null}
      over={over}
    >
      {children}
    </Shore>
  );
};

export const DeepShot: React.FC<{ croc?: Mover; tint?: string; legs?: number; children?: React.ReactNode }> = ({ croc, tint, legs, children }) => {
  const { f, k } = useShot();
  return (
    <Deep tint={tint} croc={croc ? { x: croc.x0 + (croc.x1 - croc.x0) * ease(k), y: (croc.y ?? 620) + Math.sin(f * 0.06) * 8, scale: croc.s ?? 1, rot: croc.rot ?? 0, jaw: jawOf(croc.jaw, f), flip: croc.flip, plates: croc.plates } : undefined}>
      {legs !== undefined ? (
        <Svg>
          <rect x={legs} y={-40} width={60} height={300 + Math.sin(f * 0.15) * 10} rx={28} fill="#1b2a33" />
          <rect x={legs + 90} y={-40} width={60} height={290 - Math.sin(f * 0.15) * 10} rx={28} fill="#1b2a33" />
        </Svg>
      ) : null}
      {children}
    </Deep>
  );
};

export const HeadShot: React.FC<{ jaw?: Mover["jaw"]; dots?: boolean; glow?: boolean; bg?: string; x?: number; y?: number; s0?: number; s1?: number; children?: React.ReactNode }> = ({
  jaw = 2,
  dots = false,
  glow = false,
  bg = "deep",
  x = 300,
  y = 640,
  s0 = 1.15,
  s1 = 1.3,
  children,
}) => {
  const { f, k } = useShot();
  return (
    <Backdrop v={bg}>
      <CrocHead x={x} y={y} scale={s0 + (s1 - s0) * k} jaw={jawOf(jaw, f)} dots={dots ? Math.min(1, f / 30) : 0} eyeGlow={glow ? 1 : 0}>
        {children}
      </CrocHead>
    </Backdrop>
  );
};

export const TopShot: React.FC<{ roll?: number; rot0?: number; rot1?: number; x0?: number; x1?: number; y?: number; s?: number; bg?: string; children?: React.ReactNode }> = ({
  roll = 0,
  rot0 = -8,
  rot1 = -8,
  x0 = 960,
  x1 = 960,
  y = 560,
  s = 0.95,
  bg = "mud",
  children,
}) => {
  const { f, k } = useShot();
  return (
    <Backdrop v={bg}>
      {roll
        ? [0, 1, 2].map((i) => {
            const t = ((f / 30 + i / 3) % 1 + 1) % 1;
            return <div key={i} style={{ position: "absolute", left: x0 - 260 - t * 400, top: y - 120 - t * 140, width: 520 + t * 800, height: 240 + t * 280, borderRadius: "50%", border: "4px solid rgba(240,220,170,0.5)", opacity: 1 - t }} />;
          })
        : null}
      <CrocTop x={x0 + (x1 - x0) * ease(k)} y={y} scale={s} rotate={rot0 + (rot1 - rot0) * k} roll={f * roll} />
      {children}
    </Backdrop>
  );
};

// ---------- Graphics ----------

export const NumShot: React.FC<{ to: number; from?: number; unit?: string; label: string; color?: string; bg?: string; decimals?: number; icon?: "croc" | "person" | "skull" | "egg" | null; prefix?: string }> = ({
  to,
  from = 0,
  unit = "",
  label,
  color = C.accent,
  bg = "deep",
  decimals = 0,
  icon = "croc",
  prefix = "",
}) => {
  const { f, dur } = useShot();
  const v = interpolate(f, [2, Math.max(3, dur * 0.7)], [from, to], clamp);
  // Years count up without a thousands comma.
  const year = Number.isInteger(to) && to >= 1800 && to <= 2100 && from >= 1000;
  const txt = v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: !year });
  const p = pop(f, 0, 6);
  return (
    <Backdrop v={bg}>
      {icon === "croc" ? <CrocSide x={160} y={860} scale={0.55 + 0.05 * p} opacity={0.35} /> : null}
      {icon === "person" ? <Person x={1500} y={900} scale={3.2} color="rgba(127,233,255,0.35)" /> : null}
      <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center", transform: `scale(${0.85 + 0.15 * p})` }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 250, lineHeight: 1, color, textShadow: SHADOW }}>
          {prefix}
          {txt}
          <span style={{ fontSize: 110 }}>{unit}</span>
        </div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 42, letterSpacing: 4, color: C.white, marginTop: 20, textShadow: SHADOW }}>{label}</div>
      </div>
    </Backdrop>
  );
};

export const BarsShot: React.FC<{ title: string; rows: { label: string; v: number; text: string; color?: string }[]; bg?: string }> = ({ title, rows, bg = "deep" }) => {
  const { f } = useShot();
  const max = Math.max(...rows.map((r) => r.v));
  return (
    <Backdrop v={bg}>
      <div style={{ position: "absolute", left: 200, top: 250 }}>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 38, letterSpacing: 3, color: HUD, marginBottom: 40, textShadow: SHADOW }}>{title}</div>
        {rows.map((r, i) => {
          const g = ease((f - 3 - i * 5) / 16);
          return (
            <div key={i} style={{ marginBottom: 36 }}>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 40, color: C.white, marginBottom: 10, textShadow: SHADOW }}>{r.label}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
                <div style={{ width: Math.max(10, (r.v / max) * 1250 * g), height: 64, borderRadius: 8, background: r.color ?? HUD }} />
                <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 60, color: r.color ?? HUD, opacity: g, textShadow: SHADOW }}>{r.text}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Backdrop>
  );
};

export const GaugeShot: React.FC<{ frac: number; text: string; label: string; color?: string; bg?: string }> = ({ frac, text, label, color = C.red, bg = "red" }) => {
  const { f } = useShot();
  const p = ease(f / 22) * frac;
  const r = 330;
  const cx = 960;
  const cy = 600;
  const ang = Math.PI * (1 - Math.min(1.08, p));
  const arc = (a0: number, a1: number) => `M ${cx + Math.cos(a0) * r} ${cy - Math.sin(a0) * r} A ${r} ${r} 0 0 1 ${cx + Math.cos(a1) * r} ${cy - Math.sin(a1) * r}`;
  return (
    <Backdrop v={bg}>
      <Svg>
        <path d={arc(Math.PI, 0)} stroke="rgba(255,255,255,0.18)" strokeWidth={40} fill="none" />
        <path d={arc(Math.PI, Math.max(0, ang))} stroke={color} strokeWidth={40} fill="none" />
        <line x1={cx} y1={cy} x2={cx + Math.cos(ang) * (r - 60)} y2={cy - Math.sin(ang) * (r - 60)} stroke="#fff" strokeWidth={10} />
        <circle cx={cx} cy={cy} r={20} fill="#fff" />
      </Svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 620, textAlign: "center" }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 100, color, textShadow: SHADOW }}>{text}</div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 36, letterSpacing: 3, color: "#fff", textShadow: SHADOW }}>{label}</div>
      </div>
    </Backdrop>
  );
};

export const StampShot: React.FC<{ under: string; stamp?: string; bg?: string; color?: string }> = ({ under, stamp = "MYTH", bg = "paper", color = C.red }) => {
  const { f } = useShot();
  const s = interpolate(f, [6, 12], [2.6, 1], clamp);
  return (
    <Backdrop v={bg} specks={false}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 100, color: bg === "paper" ? "#2a1d10" : "#fff", whiteSpace: "pre-line", lineHeight: 1.05 }}>{under}</div>
      {f >= 6 ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 400, textAlign: "center", transform: `rotate(-12deg) scale(${s})` }}>
          <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: 220, color, border: `16px solid ${color}`, borderRadius: 20, padding: "0 50px", letterSpacing: 10, background: "rgba(255,255,255,0.08)" }}>{stamp}</span>
        </div>
      ) : null}
    </Backdrop>
  );
};

export const ListShot: React.FC<{ items: string[]; title?: string; bg?: string; done?: number }> = ({ items, title, bg = "deep", done = -1 }) => {
  const { f, dur } = useShot();
  const step = Math.max(4, (dur * 0.6) / items.length);
  return (
    <Backdrop v={bg}>
      <div style={{ position: "absolute", left: 220, top: 230 }}>
        {title ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 38, letterSpacing: 3, color: HUD, marginBottom: 34, textShadow: SHADOW }}>{title}</div> : null}
        {items.map((t, i) => {
          const p = pop(f, i * step, 7);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 28, marginBottom: 30, opacity: p, transform: `translateX(${(1 - p) * -60}px)` }}>
              <div style={{ width: 70, height: 70, borderRadius: 14, background: i <= done ? C.accent : "rgba(255,255,255,0.1)", border: `4px solid ${C.accent}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT, fontWeight: 800, fontSize: 40, color: "#111" }}>
                {i <= done ? "✓" : ""}
              </div>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 74, color: C.white, textShadow: SHADOW }}>{t}</div>
            </div>
          );
        })}
      </div>
    </Backdrop>
  );
};

const Car: React.FC<{ x: number; y: number; s: number; color?: string }> = ({ x, y, s, color = HUD }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M 0 0 L 40 -60 Q 60 -100 120 -104 L 300 -104 Q 360 -100 400 -60 L 470 -50 Q 500 -44 500 0 Z" fill="none" stroke={color} strokeWidth={8} />
    <circle cx={110} cy={0} r={38} fill="#06100f" stroke={color} strokeWidth={8} />
    <circle cx={390} cy={0} r={38} fill="#06100f" stroke={color} strokeWidth={8} />
  </g>
);
const Bus: React.FC<{ x: number; y: number; w: number; color?: string }> = ({ x, y, w, color = HUD }) => (
  <g>
    <rect x={x} y={y - 330} width={w} height={300} rx={40} fill="none" stroke={color} strokeWidth={8} />
    {Array.from({ length: 6 }, (_, i) => <rect key={i} x={x + 40 + i * ((w - 80) / 6)} y={y - 290} width={(w - 80) / 6 - 20} height={90} rx={10} fill="none" stroke={color} strokeWidth={5} />)}
    <circle cx={x + 200} cy={y - 30} r={56} fill="#06100f" stroke={color} strokeWidth={8} />
    <circle cx={x + w - 200} cy={y - 30} r={56} fill="#06100f" stroke={color} strokeWidth={8} />
  </g>
);
const Horse: React.FC<{ x: number; y: number; s: number; color?: string }> = ({ x, y, s, color = HUD }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill={color}>
    <ellipse cx={0} cy={-150} rx={150} ry={70} />
    <path d="M 110 -190 L 190 -320 L 240 -300 L 170 -170 Z" />
    <ellipse cx={225} cy={-315} rx={50} ry={28} />
    {[-110, -60, 70, 120].map((lx) => <rect key={lx} x={lx} y={-100} width={24} height={100} rx={10} />)}
    <path d="M -150 -170 Q -210 -120 -190 -40 L -170 -40 Q -180 -110 -140 -150 Z" />
  </g>
);

// Crocodile silhouette compared against a familiar object.
export const ScaleShot: React.FC<{ vs: "person" | "car" | "bus" | "horse" | "none"; title: string; croc?: number }> = ({ vs, title, croc = 1 }) => {
  const { f } = useShot();
  const g = ease(f / 14);
  return (
    <Backdrop v="deep">
      <Svg>
        {vs === "car" ? <Car x={420} y={860} s={2.1} /> : null}
        {vs === "bus" ? <Bus x={300} y={880} w={1320} /> : null}
        {vs === "horse" ? <Horse x={1400} y={880} s={1.4} /> : null}
        <line x1={300} y1={930} x2={300 + 1320 * g * croc} y2={930} stroke={C.accent} strokeWidth={8} />
      </Svg>
      {vs === "person" ? <Person x={1560} y={880} scale={3.6} color={HUD} /> : null}
      <CrocSide x={300 - (1 - g) * 200} y={vs === "horse" ? 810 : 800} scale={1.32 * croc} opacity={0.95} />
      <Label text={title} x={300} y={960} color={C.accent} size={38} />
    </Backdrop>
  );
};

export const EcgShot: React.FC<{ bpm: number; label: string; color?: string }> = ({ bpm, label, color = HUD }) => {
  const { f } = useShot();
  const period = (60 / bpm) * 30;
  const pts: string[] = [];
  for (let i = 0; i <= 240; i++) {
    const x = 160 + (i / 240) * 1600;
    const t = (f * 1.5 - (240 - i) * 0.6 + 9000) % period;
    const u = t / Math.min(period, 12);
    pts.push(`${x},${560 + (u < 1 ? Math.sin(u * Math.PI) * (u < 0.5 ? -220 : 110) : 0)}`);
  }
  return (
    <Backdrop v="night">
      <Svg>
        <polyline points={pts.join(" ")} stroke={color} strokeWidth={8} fill="none" />
      </Svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 760, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 90, color, textShadow: SHADOW }}>{label}</div>
    </Backdrop>
  );
};

export const RadarShot: React.FC<{ lines: string[] }> = ({ lines }) => {
  const { f } = useShot();
  const a = f * 0.12;
  return (
    <Backdrop v="night" specks={false}>
      <Svg>
        {[120, 240, 360, 480].map((r) => <circle key={r} cx={960} cy={560} r={r} fill="none" stroke="rgba(127,233,255,0.3)" strokeWidth={3} />)}
        <line x1={960} y1={560} x2={960 + Math.cos(a) * 480} y2={560 + Math.sin(a) * 480} stroke={HUD} strokeWidth={6} />
        <circle cx={1180} cy={420} r={18 + Math.sin(f * 0.4) * 5} fill={C.red} />
        <rect x={1140} y={380} width={80} height={80} fill="none" stroke={C.accent} strokeWidth={4} opacity={f > 8 ? 1 : 0} />
      </Svg>
      <div style={{ position: "absolute", left: 1250, top: 380 }}>
        {lines.map((l, i) => <div key={i} style={{ fontFamily: MONO, fontWeight: 700, fontSize: 40, color: i === lines.length - 1 ? C.accent : HUD, opacity: pop(f, 4 + i * 6), textShadow: SHADOW }}>{l}</div>)}
      </div>
    </Backdrop>
  );
};

export const TimerShot: React.FC<{ rows: { label: string; frac: number; text: string; color?: string }[] }> = ({ rows }) => {
  const { f } = useShot();
  return (
    <Backdrop v="deep">
      <div style={{ position: "absolute", left: 200, top: 300 }}>
        {rows.map((r, i) => {
          const g = ease((f - i * 6) / 30);
          return (
            <div key={i} style={{ marginBottom: 60 }}>
              <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 40, letterSpacing: 3, color: C.white }}>{r.label}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 26, marginTop: 12 }}>
                <div style={{ width: Math.max(10, 1300 * r.frac * g), height: 80, borderRadius: 10, background: r.color ?? HUD }} />
                <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 90, color: r.color ?? HUD }}>{r.text}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Backdrop>
  );
};

export const GridShot: React.FC<{ n: number; keep: number; title: string; shape?: "dot" | "egg" | "croc"; fade?: boolean; color?: string }> = ({ n, keep, title, shape = "dot", fade = true, color = "#efe8cf" }) => {
  const { f, dur } = useShot();
  const cols = Math.ceil(Math.sqrt(n * 1.8));
  const g = fade ? ease(f / (dur * 0.8)) : 0;
  return (
    <Backdrop v="deep">
      <Svg>
        {Array.from({ length: n }, (_, i) => {
          const cx = 960 - (cols * 70) / 2 + (i % cols) * 70 + 35;
          const cy = 300 + Math.floor(i / cols) * 70;
          const alive = i === Math.floor(n * 0.37) || i < keep - 1 ? 1 : 1 - ease((g - random(`g${i}`) * 0.9) / 0.1);
          const hi = fade && g > 0.95 && alive > 0.5;
          return shape === "egg" ? (
            <ellipse key={i} cx={cx} cy={cy} rx={20} ry={27} fill={hi ? C.accent : color} opacity={alive} />
          ) : (
            <circle key={i} cx={cx} cy={cy} r={hi ? 26 : 22} fill={hi ? C.accent : color} opacity={alive} />
          );
        })}
      </Svg>
      <Label text={title} x={200} y={170} size={40} />
    </Backdrop>
  );
};

export const LineShot: React.FC<{ pts: [number, number][]; upto: number; marks?: { x: number; text: string }[]; title: string; color?: string }> = ({ pts, upto, marks = [], title, color = C.red }) => {
  const { f } = useShot();
  const X = (yr: number) => 240 + ((yr - 1945) / 80) * 1440;
  const Y = (v: number) => 860 - (v / 100) * 520;
  const u = interpolate(f, [0, 30], [pts[0][0], upto], clamp);
  const seg: string[] = [];
  for (let i = 0; i < pts.length; i++) {
    if (pts[i][0] <= u) seg.push(`${X(pts[i][0])},${Y(pts[i][1])}`);
    else {
      const [a, b] = [pts[i - 1], pts[i]];
      const t = (u - a[0]) / (b[0] - a[0]);
      seg.push(`${X(u)},${Y(a[1] + (b[1] - a[1]) * t)}`);
      break;
    }
  }
  return (
    <Backdrop v="night">
      <Svg>
        <line x1={240} y1={860} x2={1680} y2={860} stroke="#2f6a74" strokeWidth={5} />
        <line x1={240} y1={330} x2={240} y2={860} stroke="#2f6a74" strokeWidth={5} />
        {[1945, 1971, 2000, 2025].map((yr) => <text key={yr} x={X(yr)} y={910} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={32} textAnchor="middle">{yr}</text>)}
        <polyline points={seg.join(" ")} stroke={color} strokeWidth={12} fill="none" strokeLinejoin="round" strokeLinecap="round" />
        {marks.map((m) => <line key={m.x} x1={X(m.x)} y1={330} x2={X(m.x)} y2={860} stroke={C.accent} strokeWidth={5} strokeDasharray="14 10" />)}
      </Svg>
      <Label text={title} x={260} y={240} size={40} />
    </Backdrop>
  );
};

export const CalendarShot: React.FC<{ months: number }> = ({ months }) => {
  const { f, dur } = useShot();
  const shown = Math.min(months, Math.floor((f / dur) * (months + 1)));
  return (
    <Backdrop v="deep">
      {Array.from({ length: months }, (_, i) => (
        <div key={i} style={{ position: "absolute", left: 260 + (i % 4) * 360, top: 260 + Math.floor(i / 4) * 230, width: 320, height: 190, borderRadius: 16, background: i < shown ? "rgba(255,77,61,0.25)" : "rgba(255,255,255,0.06)", border: `5px solid ${i < shown ? C.red : "rgba(127,233,255,0.35)"}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, color: HUD }}>MONTH {i + 1}</div>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 44, color: i < shown ? C.red : "rgba(255,255,255,0.3)" }}>{i < shown ? "NO MEAL" : "…"}</div>
        </div>
      ))}
    </Backdrop>
  );
};

export const TitleShot: React.FC<{ top?: string; mid: string; big?: string; bg?: string }> = ({ top, mid, big, bg = "night" }) => {
  const { f } = useShot();
  return (
    <Backdrop v={bg}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 250, textAlign: "center" }}>
        {top ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: HUD, opacity: pop(f) }}>{top}</div> : null}
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, lineHeight: 1.05, color: "#fff", whiteSpace: "pre-line", opacity: pop(f, 3), marginTop: 18, textShadow: SHADOW }}>{mid}</div>
        {big ? <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 180, color: C.accent, marginTop: 10, transform: `scale(${0.8 + 0.2 * pop(f, 8, 8)})`, opacity: pop(f, 8), textShadow: SHADOW }}>{big}</div> : null}
      </div>
    </Backdrop>
  );
};

export const ChapterShot: React.FC<{ n: number; title: string; bg?: string }> = ({ n, title, bg = "deep" }) => {
  const { f } = useShot();
  const w = ease(f / 10);
  return (
    <Backdrop v={bg}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 360, textAlign: "center" }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 240, color: "transparent", WebkitTextStroke: `4px ${C.accent}`, lineHeight: 1, opacity: pop(f) }}>{String(n).padStart(2, "0")}</div>
        <div style={{ height: 8, width: 900 * w, background: C.accent, margin: "16px auto" }} />
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 96, color: "#fff", opacity: pop(f, 4), textShadow: SHADOW }}>{title}</div>
      </div>
    </Backdrop>
  );
};

export const Split: React.FC<{ left: React.ReactNode; right: React.ReactNode; lt?: string; rt?: string }> = ({ left, right, lt, rt }) => {
  const { f } = useShot();
  const w = ease(f / 8);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 958, height: 1080, overflow: "hidden", transform: `translateX(${(1 - w) * -200}px)` }}>
        <div style={{ position: "absolute", left: -480, top: 0, width: 1920, height: 1080 }}>{left}</div>
      </div>
      <div style={{ position: "absolute", left: 962, top: 0, width: 958, height: 1080, overflow: "hidden", transform: `translateX(${(1 - w) * 200}px)` }}>
        <div style={{ position: "absolute", left: -480, top: 0, width: 1920, height: 1080 }}>{right}</div>
      </div>
      <div style={{ position: "absolute", left: 956, top: 0, width: 8, height: 1080, background: C.accent }} />
      {lt ? <div style={{ position: "absolute", left: 0, width: 958, top: 190, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: "#fff", textShadow: SHADOW }}>{lt}</div> : null}
      {rt ? <div style={{ position: "absolute", left: 962, width: 958, top: 190, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.accent, textShadow: SHADOW }}>{rt}</div> : null}
    </AbsoluteFill>
  );
};

// ---------- Map ----------

const LAND: [number, number][][] = [
  [[68, 24], [72, 21], [73, 16], [77, 8], [80, 13], [82, 17], [87, 21], [89, 22], [92, 21], [94, 16], [98, 10], [99, 7], [101, 3], [104, 1.5], [103, 5], [101, 12], [105, 9], [109, 12], [108, 17], [106, 20], [110, 21], [117, 24], [122, 30], [60, 30], [60, 25]],
  [[95, 5.5], [98, 3.5], [103, -1], [106, -5.5], [104, -5.5], [100, -2], [96, 3]],
  [[109, 1.5], [113, 3], [117, 7], [119, 5], [117.5, 0], [116, -4], [111, -3]],
  [[105.5, -6.5], [110, -6.5], [114.5, -7.7], [114, -8.6], [108, -7.8]],
  [[119, -5], [120, 0], [124, 1], [121, -1], [123, -4], [121, -5]],
  [[120, 18], [122, 17], [124, 12], [126, 8], [125, 6], [122, 8], [121, 13]],
  [[131, -1], [135, -3], [141, -2.5], [146, -5.5], [150, -10], [145, -8], [141, -9], [137, -7], [133, -4]],
  [[114, -22], [122, -17], [126, -14], [130, -12], [132, -11], [136, -12], [137, -15.5], [141, -17], [142, -11], [145, -15], [150, -23], [153, -28], [153, -32], [114, -32]],
  [[80, 9.5], [81.5, 8], [81.5, 6.2], [80, 6], [79.8, 8]],
];
export const RANGE: [number, number][] = [[86, 20], [81, 7], [90, 22], [95, 16], [100, 5], [101, 0], [113, 2], [110, -7], [123, 10], [121, -2], [124, -15], [131, -12], [136, -13], [141, -15], [138, -5], [146, -7], [145, -15], [149, -21], [160, -9], [167, -16]];
const px = (lon: number) => 250 + (lon - 60) * 12.3;
const py = (lat: number) => 250 + (30 - lat) * 10.6;

export const MapShot: React.FC<{
  cx?: number;
  cy?: number;
  z0?: number;
  z1?: number;
  pins?: { lon: number; lat: number; label: string; color?: string }[];
  range?: [number, number];
  path?: [number, number][];
  arrows?: boolean;
}> = ({ cx = 110, cy = 0, z0 = 1, z1 = 1.1, pins = [], range, path, arrows = false }) => {
  const { f, k } = useShot();
  const z = z0 + (z1 - z0) * ease(k);
  const lit = range ? interpolate(f, [0, 30], [range[0], range[1]], clamp) : 0;
  const prog = path ? ease(f / 40) : 0;
  const pp = path ? path.slice(0, Math.max(1, Math.ceil(prog * path.length))) : [];
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #0f3a47 0%, #061a22 70%)" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - px(cx) * z}px, ${540 - py(cy) * z}px) scale(${z})`, transformOrigin: "0 0" }}>
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
          {Array.from({ length: 12 }, (_, i) => <line key={i} x1={px(60 + i * 10)} y1={py(30)} x2={px(60 + i * 10)} y2={py(-32)} stroke="rgba(127,233,255,0.08)" strokeWidth={2 / z} />)}
          {LAND.map((poly, i) => <polygon key={i} points={poly.map(([lo, la]) => `${px(lo)},${py(la)}`).join(" ")} fill="#1d4650" stroke="#3f8590" strokeWidth={2 / z} />)}
          {RANGE.map(([lo, la], i) => (i < lit ? <circle key={i} cx={px(lo)} cy={py(la)} r={14 / Math.sqrt(z)} fill={C.accent} opacity={0.85} /> : null))}
          {pp.length > 1 ? <polyline points={pp.map(([lo, la]) => `${px(lo)},${py(la)}`).join(" ")} stroke={C.red} strokeWidth={6 / z} fill="none" /> : null}
          {arrows
            ? [0, 1, 2, 3].map((i) => {
                const t = ((f / 25 + i / 4) % 1 + 1) % 1;
                return <path key={i} d={`M ${px(139 + i * 0.7)} ${py(-10 - t * 4)} l 0 ${16 / z + 6} l -4 -6 m 4 6 l 4 -6`} stroke={HUD} strokeWidth={2} fill="none" opacity={1 - t} />;
              })
            : null}
          {pins.map((p, i) => {
            const s = pop(f, 3 + i * 4, 8);
            return (
              <g key={i} transform={`translate(${px(p.lon)} ${py(p.lat)}) scale(${s / z})`}>
                <circle r={22} fill={p.color ?? C.red} />
                <circle r={22 + ((f * 1.5) % 40)} fill="none" stroke={p.color ?? C.red} strokeWidth={4} opacity={1 - ((f * 1.5) % 40) / 40} />
                <text x={34} y={12} fill="#fff" fontFamily={FONT} fontWeight={800} fontSize={44} stroke="#000" strokeWidth={6} paintOrder="stroke">{p.label}</text>
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export { Svg, ease, pop };
