// Transitions, grades and finishing effects. All CSS/SVG, so they render the same on any machine.
import React from "react";
import { AbsoluteFill, random, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "./theme";

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const easeOut = (t: number) => 1 - Math.pow(1 - clamp01(t), 3);
const easeInOut = (t: number) => {
  const x = clamp01(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};

// ---------- Transitions ----------
// The incoming shot is drawn on top of the outgoing one; during its first `len` frames it is revealed
// with one of these. The outgoing shot keeps playing underneath for those frames.

export type TransitionKind =
  | "cut"
  | "whip"
  | "whipLeft"
  | "zoom"
  | "zoomOut"
  | "flash"
  | "glitch"
  | "iris"
  | "slash"
  | "claw"
  | "ripple"
  | "burn"
  | "leak"
  | "spin"
  | "push"
  | "blinds"
  | "split";

export const TransitionIn: React.FC<{ kind: TransitionKind; len?: number; children: React.ReactNode }> = ({ kind, len = 8, children }) => {
  const f = useCurrentFrame();
  const t = clamp01(f / len);
  if (kind === "cut" || t >= 1) return <AbsoluteFill>{children}</AbsoluteFill>;
  const e = easeOut(t);
  const ei = easeInOut(t);
  let style: React.CSSProperties = {};
  let over: React.ReactNode = null;
  switch (kind) {
    case "whip":
    case "whipLeft": {
      const d = kind === "whip" ? 1 : -1;
      style = { transform: `translateX(${d * (1 - e) * 1920}px)`, filter: `blur(${(1 - e) * 30}px)` };
      break;
    }
    case "zoom":
      style = { transform: `scale(${0.4 + 0.6 * e})`, filter: `blur(${(1 - e) * 24}px)`, opacity: clamp01(t * 2.5) };
      break;
    case "zoomOut":
      style = { transform: `scale(${2.2 - 1.2 * e})`, filter: `blur(${(1 - e) * 20}px)`, opacity: clamp01(t * 2.5) };
      break;
    case "flash":
      style = { opacity: t > 0.25 ? 1 : 0 };
      over = <AbsoluteFill style={{ background: "#fff", opacity: Math.max(0, 1 - Math.abs(t - 0.3) * 3) }} />;
      break;
    case "glitch": {
      const on = t > 0.35 ? 1 : 0;
      const j = Math.floor(f / 2);
      style = {
        opacity: on || random(`gl${j}`) > 0.5 ? 1 : 0,
        transform: `translate(${(random(`gx${j}`) - 0.5) * 80 * (1 - t)}px, ${(random(`gy${j}`) - 0.5) * 20 * (1 - t)}px)`,
        filter: `drop-shadow(${12 * (1 - t)}px 0 0 rgba(255,0,60,0.8)) drop-shadow(${-12 * (1 - t)}px 0 0 rgba(0,240,255,0.8))`,
        clipPath: `inset(${random(`gc${j}`) * 30 * (1 - t)}% 0 ${random(`gd${j}`) * 30 * (1 - t)}% 0)`,
      };
      break;
    }
    case "iris":
      style = { clipPath: `circle(${ei * 120}% at 50% 50%)` };
      over = <AbsoluteFill style={{ boxShadow: `inset 0 0 0 ${(1 - t) * 8}px ${C.accent}`, borderRadius: "50%", opacity: 0 }} />;
      break;
    case "slash": {
      const p = ei * 160 - 30;
      style = { clipPath: `polygon(0 0, ${p + 20}% 0, ${p}% 100%, 0 100%)` };
      over = (
        <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
          <line x1={((p + 20) / 100) * 1920} y1={0} x2={(p / 100) * 1920} y2={1080} stroke={C.accent} strokeWidth={14} />
        </svg>
      );
      break;
    }
    case "claw": {
      // Three diagonal tears open across the frame, like claw marks.
      const w = ei * 360;
      const bands = [330, 960, 1590];
      style = { clipPath: `path('${bands.map((b) => `M ${b - w + 160} 0 L ${b + w + 160} 0 L ${b + w - 160} 1080 L ${b - w - 160} 1080 Z`).join(" ")}')` };
      if (t > 0.9) style = {};
      over = (
        <svg style={{ position: "absolute", left: 0, top: 0, opacity: 1 - t }} width={1920} height={1080}>
          {bands.map((b) => (
            <line key={b} x1={b + 160} y1={0} x2={b - 160} y2={1080} stroke="#fff" strokeWidth={8} />
          ))}
        </svg>
      );
      break;
    }
    case "ripple": {
      const pts: string[] = [];
      const edge = ei * 125 - 10;
      for (let i = 0; i <= 24; i++) {
        const y = (i / 24) * 100;
        pts.push(`${edge + Math.sin(i * 0.9 + f * 0.6) * 4}% ${y}%`);
      }
      style = { clipPath: `polygon(0 0, ${pts.join(", ")}, 0 100%)`, filter: `blur(${(1 - e) * 6}px)` };
      break;
    }
    case "burn":
      style = { opacity: clamp01((t - 0.3) * 2) };
      over = (
        <AbsoluteFill
          style={{
            background: `radial-gradient(circle at ${30 + t * 40}% 60%, rgba(255,240,200,${1 - Math.abs(t - 0.45) * 2}) 0%, rgba(255,120,20,${0.9 - Math.abs(t - 0.45) * 1.6}) 30%, rgba(120,20,0,${0.6 - Math.abs(t - 0.45)}) 60%, transparent 80%)`,
            mixBlendMode: "screen",
          }}
        />
      );
      break;
    case "leak":
      style = { opacity: clamp01(t * 1.6) };
      over = (
        <AbsoluteFill
          style={{
            background: `linear-gradient(${110 + t * 40}deg, transparent ${t * 60 - 30}%, rgba(255,170,80,0.85) ${t * 60}%, rgba(255,80,40,0.6) ${t * 60 + 15}%, transparent ${t * 60 + 40}%)`,
            mixBlendMode: "screen",
          }}
        />
      );
      break;
    case "spin":
      style = { transform: `rotate(${(1 - e) * -25}deg) scale(${0.6 + 0.4 * e})`, filter: `blur(${(1 - e) * 18}px)`, opacity: clamp01(t * 2) };
      break;
    case "push":
      style = { transform: `translateY(${(1 - e) * 1080}px)` };
      break;
    case "blinds":
      style = { clipPath: `path('${Array.from({ length: 8 }, (_, i) => { const y0 = i * 135; const y1 = y0 + 135 * ei; return `M 0 ${y0} L 1920 ${y0} L 1920 ${y1} L 0 ${y1} Z`; }).join(" ")}')` };
      if (t > 0.92) style = {};
      break;
    case "split":
      style = { clipPath: `inset(${(1 - ei) * 50}% 0 ${(1 - ei) * 50}% 0)` };
      break;
  }
  return (
    <AbsoluteFill>
      <AbsoluteFill style={style}>{children}</AbsoluteFill>
      {over}
    </AbsoluteFill>
  );
};

// ---------- Grades ----------

export type GradeKind = "none" | "film" | "night" | "danger" | "cold" | "warm" | "mono";

// Old-film look for history: sepia, flicker, gate weave, scratches and dust.
const OldFilm: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  const j = Math.floor(f / 2);
  const flick = 0.9 + random(`fl${j}`) * 0.18;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ filter: `sepia(0.85) contrast(1.15) brightness(${flick})`, transform: `translate(${(random(`wx${j}`) - 0.5) * 6}px, ${(random(`wy${j}`) - 0.5) * 6}px)` }}>{children}</AbsoluteFill>
      <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
        {Array.from({ length: 3 }, (_, i) =>
          random(`sc${j}${i}`) > 0.5 ? <line key={i} x1={random(`sx${j}${i}`) * 1920} y1={0} x2={random(`sx${j}${i}`) * 1920 + 6} y2={1080} stroke="rgba(255,250,230,0.35)" strokeWidth={2} /> : null,
        )}
        {Array.from({ length: 10 }, (_, i) => (
          <circle key={`d${i}`} cx={random(`dx${j}${i}`) * 1920} cy={random(`dy${j}${i}`) * 1080} r={1 + random(`dr${j}${i}`) * 3} fill="rgba(20,10,0,0.6)" />
        ))}
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 50%, rgba(40,20,0,0.75) 100%)" }} />
    </AbsoluteFill>
  );
};

export const Grade: React.FC<{ kind: GradeKind; children: React.ReactNode }> = ({ kind, children }) => {
  switch (kind) {
    case "film":
      return <OldFilm>{children}</OldFilm>;
    case "night":
      return <AbsoluteFill style={{ filter: "saturate(0.6) brightness(0.8) hue-rotate(-10deg)" }}>{children}<AbsoluteFill style={{ background: "rgba(20,50,90,0.28)", mixBlendMode: "multiply" }} /></AbsoluteFill>;
    case "danger":
      return <AbsoluteFill style={{ filter: "contrast(1.15) saturate(1.2)" }}>{children}<AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 40%, rgba(180,10,0,0.45) 100%)" }} /></AbsoluteFill>;
    case "cold":
      return <AbsoluteFill style={{ filter: "saturate(0.85) hue-rotate(8deg) contrast(1.05)" }}>{children}</AbsoluteFill>;
    case "warm":
      return <AbsoluteFill style={{ filter: "saturate(1.15) sepia(0.15) contrast(1.05)" }}>{children}</AbsoluteFill>;
    case "mono":
      return <AbsoluteFill style={{ filter: "grayscale(1) contrast(1.3)" }}>{children}</AbsoluteFill>;
    default:
      return <AbsoluteFill>{children}</AbsoluteFill>;
  }
};

// ---------- Finishing layers for the whole video ----------

// Fine animated grain, refreshed every other frame.
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.07 }) => {
  const f = useCurrentFrame();
  const seed = Math.floor(f / 2) % 50;
  return (
    <AbsoluteFill style={{ opacity, mixBlendMode: "overlay", pointerEvents: "none" }}>
      <svg width={1920} height={1080}>
        <filter id={`g${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width={1920} height={1080} filter={`url(#g${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

// Cinematic bars that slide in for dramatic shots.
export const Letterbox: React.FC<{ on: boolean }> = ({ on }) => {
  const f = useCurrentFrame();
  if (!on) return null;
  const h = 110 * easeOut(f / 8);
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: h, background: "#000" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: h, background: "#000" }} />
    </>
  );
};

// A brief RGB split, for glitchy or shocking moments.
export const RgbSplit: React.FC<{ amount: number; children: React.ReactNode }> = ({ amount, children }) =>
  amount <= 0 ? (
    <AbsoluteFill>{children}</AbsoluteFill>
  ) : (
    <AbsoluteFill style={{ filter: `drop-shadow(${amount}px 0 0 rgba(255,0,60,0.7)) drop-shadow(${-amount}px 0 0 rgba(0,230,255,0.7))` }}>{children}</AbsoluteFill>
  );

// Big word that slams in from huge and shakes the frame.
export const Slam: React.FC<{ text: string; color?: string; size?: number; y?: number }> = ({ text, color = C.accent, size = 200, y = 380 }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const s = 3 - 2 * easeOut(f / 6);
  const shake = f < 10 ? (random(`sl${f}`) - 0.5) * 30 * (1 - f / 10) : 0;
  const vis = f > dur - 4 ? (dur - f) / 4 : 1;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", transform: `translate(${shake}px, ${shake * 0.5}px) scale(${s})`, opacity: vis }}>
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: size, color, letterSpacing: 4, WebkitTextStroke: "4px #000", textShadow: "0 12px 40px rgba(0,0,0,0.9)" }}>{text}</span>
    </div>
  );
};

// Freeze-frame accent: white flash and a thin frame line when a shot freezes.
export const FreezeAccent: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <AbsoluteFill style={{ background: "#fff", opacity: Math.max(0, 0.6 - f * 0.15) }} />
      <AbsoluteFill style={{ boxShadow: "inset 0 0 0 10px rgba(255,255,255,0.85)" }} />
    </>
  );
};

// A slow 3D tilt that gives photos and drawn frames some depth.
export const Tilt: React.FC<{ dir?: number; children: React.ReactNode }> = ({ dir = 1, children }) => {
  const f = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();
  const k = clamp01(f / dur);
  return (
    <AbsoluteFill style={{ perspective: 1400 }}>
      <AbsoluteFill style={{ transform: `rotateY(${dir * (6 - 12 * k)}deg) rotateX(${3 - 6 * k}deg) scale(1.12)` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
