// VFX layer (owner, 25 Nov 2026): effects composited over real footage, real photos and animation.
// All CSS/SVG, rendered per frame, so they work on any machine without WebGL.
// Every component reads the shot's own frame through useShot(), so it moves for the whole shot.
import React from "react";
import { AbsoluteFill, Img, interpolate, OffthreadVideo, random, staticFile } from "remotion";
import { ease, pop, useShot } from "./shots";
import { C } from "./theme";
import { FONT } from "./ui";
import { MONO } from "./hud";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const SHADOW = "0 6px 24px rgba(0,0,0,0.9), 0 0 4px #000";

// ---------- Atmosphere ----------

// Marine snow: drifting specks in three depth layers; near ones are bigger, faster and soft.
export const Snow: React.FC<{ n?: number; opacity?: number; seed?: string }> = ({ n = 90, opacity = 1, seed = "sn" }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity }}>
      {Array.from({ length: n }, (_, i) => {
        const layer = i % 3;
        const sp = [0.25, 0.55, 1.1][layer];
        const size = [2.5, 4.5, 9][layer];
        const x = (random(`${seed}x${i}`) * 2100 + f * sp * (0.6 + random(`${seed}v${i}`)) + Math.sin(f * 0.03 + i) * 12) % 2100 - 90;
        const y = (random(`${seed}y${i}`) * 1200 + f * sp * 0.45) % 1200 - 60;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: size,
              background: "#e9f6f8",
              opacity: [0.35, 0.45, 0.3][layer],
              filter: layer === 2 ? "blur(2.5px)" : layer === 0 ? "blur(0.5px)" : undefined,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// Light rays from the surface, slowly swaying.
export const Rays: React.FC<{ strength?: number; from?: number }> = ({ strength = 1, from = 960 }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="rayg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#d8f4ff" stopOpacity={0.55 * strength} />
            <stop offset="1" stopColor="#d8f4ff" stopOpacity={0} />
          </linearGradient>
          <filter id="rayblur">
            <feGaussianBlur stdDeviation="14" />
          </filter>
        </defs>
        <g filter="url(#rayblur)">
          {Array.from({ length: 9 }, (_, i) => {
            const x = from - 900 + i * 230 + Math.sin(f * 0.02 + i * 1.7) * 60;
            const w = 50 + random(`rw${i}`) * 110;
            const o = 0.45 + 0.55 * Math.abs(Math.sin(f * 0.015 + i));
            return <path key={i} d={`M ${x} -20 L ${x + w} -20 L ${x + w * 2.6 + (i - 4) * 70} 1100 L ${x - w * 1.2 + (i - 4) * 70} 1100 Z`} fill="url(#rayg)" opacity={o} />;
          })}
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// Caustics: the rippling light net seen on surfaces near the top of the water.
export const Caustics: React.FC<{ opacity?: number; scale?: number }> = ({ opacity = 0.18, scale = 1 }) => {
  const { f } = useShot();
  const id = "cau";
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen", opacity }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <filter id={id} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency={`${0.008 / scale} ${0.012 / scale}`} numOctaves={2} seed={Math.floor(f / 3) % 40} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.85  0 0 0 0 0.97  0 0 0 0 1  0 0 0 9 -4.2" />
        </filter>
        <rect width={1920} height={1080} filter={`url(#${id})`} />
      </svg>
    </AbsoluteFill>
  );
};

// Bubbles rising in a few streams.
export const Bubbles: React.FC<{ streams?: number[]; n?: number; y0?: number }> = ({ streams = [400, 1500], n = 14, y0 = 1100 }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {streams.map((sx, s) =>
          Array.from({ length: n }, (_, i) => {
            const t = ((f / 70 + random(`bb${s}${i}`)) % 1 + 1) % 1;
            const r = 4 + random(`br${s}${i}`) * 12;
            return <circle key={`${s}${i}`} cx={sx + Math.sin(t * 9 + i) * 18} cy={y0 - t * (y0 + 40)} r={r} fill="rgba(220,245,255,0.08)" stroke="rgba(230,250,255,0.6)" strokeWidth={2} />;
          }),
        )}
      </svg>
    </AbsoluteFill>
  );
};

// Depth haze: the water closes in toward the bottom and edges.
export const Haze: React.FC<{ depth?: number; color?: string }> = ({ depth = 0.5, color = "4,28,40" }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `linear-gradient(rgba(${color},${0.05 + depth * 0.1}) 0%, rgba(${color},${0.25 + depth * 0.45}) 100%), radial-gradient(ellipse at 50% 40%, transparent 45%, rgba(${color},${0.35 + depth * 0.4}) 100%)`,
    }}
  />
);

// ---------- Camera and grade ----------

// One shared look for every real clip and photo: cool, slightly lifted blacks, a touch of teal.
export const Polar: React.FC<{ children: React.ReactNode; warm?: boolean }> = ({ children, warm = false }) => (
  <AbsoluteFill>
    <AbsoluteFill style={{ filter: warm ? "saturate(0.95) contrast(1.06) brightness(1.02)" : "saturate(0.82) contrast(1.1) brightness(0.98) hue-rotate(-6deg)" }}>{children}</AbsoluteFill>
    <AbsoluteFill style={{ background: warm ? "rgba(255,190,120,0.06)" : "rgba(40,120,150,0.12)", mixBlendMode: "soft-light", pointerEvents: "none" }} />
  </AbsoluteFill>
);

// Handheld underwater camera: slow drift and sway, and a focus pull at the start of the shot.
export const Drift: React.FC<{ children: React.ReactNode; amount?: number; focus?: boolean; seed?: number }> = ({ children, amount = 1, focus = true, seed = 0 }) => {
  const { f } = useShot();
  const dx = Math.sin(f * 0.031 + seed) * 14 * amount;
  const dy = Math.cos(f * 0.024 + seed * 2) * 9 * amount;
  const rot = Math.sin(f * 0.019 + seed) * 0.6 * amount;
  const blur = focus ? interpolate(f, [0, 9], [7, 0], clamp) : 0;
  return <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg) scale(${1.05 + 0.03 * amount})`, filter: blur > 0.1 ? `blur(${blur}px)` : undefined }}>{children}</AbsoluteFill>;
};

// ---------- Real media with VFX ----------

// A real clip with the shared grade, camera drift and an optional atmosphere layer.
export const FX: React.FC<{
  src: string;
  label?: string;
  under?: boolean;
  rays?: boolean;
  snow?: boolean;
  bubbles?: boolean;
  zoom?: number;
}> = ({ src, label, under = false, rays = false, snow = false, bubbles = false, zoom = 1 }) => {
  const { k } = useShot();
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Drift amount={under ? 1 : 0.5}>
        <Polar>
          <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom * (1.02 + 0.05 * k)})` }} />
        </Polar>
      </Drift>
      {under ? <Haze depth={0.3} /> : null}
      {rays ? <Rays strength={0.7} /> : null}
      {snow ? <Snow n={60} /> : null}
      {bubbles ? <Bubbles /> : null}
      {label ? <Tag text={label} /> : null}
    </AbsoluteFill>
  );
};

// 2.5D photo: the background drifts one way, the subject (an elliptical cut-out) the other, with snow between.
export const Parallax: React.FC<{ src: string; credit: string; sx?: number; sy?: number; sr?: number; dir?: number; under?: boolean; snow?: boolean }> = ({
  src,
  credit,
  sx = 50,
  sy = 55,
  sr = 30,
  dir = 1,
  under = false,
  snow = true,
}) => {
  const { k } = useShot();
  const e = ease(k);
  const mask = `radial-gradient(ellipse ${sr}% ${sr * 1.25}% at ${sx}% ${sy}%, #000 62%, transparent 100%)`;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Polar>
        <AbsoluteFill style={{ transform: `scale(${1.14 + 0.02 * e}) translateX(${-dir * 26 * e}px)`, filter: "blur(2.5px) brightness(0.88)" }}>
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
        {snow ? <Snow n={45} opacity={0.7} seed="ps" /> : null}
        <AbsoluteFill style={{ transform: `scale(${1.12 + 0.07 * e}) translateX(${dir * 24 * e}px)`, transformOrigin: `${sx}% ${sy}%`, WebkitMaskImage: mask, maskImage: mask }}>
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      </Polar>
      {under ? <Haze depth={0.25} /> : <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.45) 100%)" }} />}
      <Tag text={`PHOTO · ${credit}`} />
    </AbsoluteFill>
  );
};

// Small source or species note, bottom-centre above the captions (never in a corner).
export const Tag: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: 812, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 17, letterSpacing: 2, color: "rgba(255,255,255,0.7)", textShadow: SHADOW }}>{text}</div>
);

// ---------- Inserts of real people and places ----------

// A drawn head-and-shoulders portrait for people with no free-licence photo. Never presented as a photo.
export const Portrait: React.FC<{ hair?: string; skin?: string; coat?: string; hat?: boolean; beard?: boolean }> = ({ hair = "#3b2a1e", skin = "#e2b896", coat = "#2c4656", hat = false, beard = false }) => (
  <svg viewBox="0 0 200 200" width="100%" height="100%">
    <rect width={200} height={200} fill="#c9d8de" />
    <path d="M 20 200 C 30 140 70 128 100 128 C 130 128 170 140 180 200 Z" fill={coat} />
    <rect x={86} y={104} width={28} height={30} fill={skin} />
    <ellipse cx={100} cy={84} rx={34} ry={40} fill={skin} />
    {hat ? <path d="M 62 74 C 62 34 138 34 138 74 L 142 80 L 58 80 Z" fill="#7a2a2a" /> : <path d="M 66 76 C 60 40 140 36 134 76 C 128 58 76 56 66 76 Z" fill={hair} />}
    {beard ? <path d="M 70 92 C 72 128 128 128 130 92 C 120 112 80 112 70 92 Z" fill={hair} /> : null}
    <circle cx={88} cy={84} r={3} fill="#1a1a1a" />
    <circle cx={112} cy={84} r={3} fill="#1a1a1a" />
  </svg>
);

// Circular or rectangular insert over a shot: a real photo, or a drawn portrait marked as an illustration.
export const Insert: React.FC<{
  photo?: string;
  portrait?: React.ReactNode;
  name: string;
  credit?: string;
  shape?: "circle" | "rect";
  x?: number;
  y?: number;
  size?: number;
}> = ({ photo, portrait, name, credit, shape = "circle", x = 1380, y = 250, size = 330 }) => {
  const { f } = useShot();
  const p = pop(f, 2, 10);
  const w = shape === "rect" ? size * 1.35 : size;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, transform: `scale(${0.7 + 0.3 * p}) rotate(${(1 - p) * -6}deg)`, opacity: p, transformOrigin: "center" }}>
      <div style={{ width: w, height: size, borderRadius: shape === "circle" ? "50%" : 18, overflow: "hidden", border: `7px solid ${C.white}`, boxShadow: "0 18px 50px rgba(0,0,0,0.65)", background: "#111" }}>
        {photo ? <Img src={staticFile(photo)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.9) contrast(1.05)" }} /> : portrait}
      </div>
      <div style={{ marginTop: 14, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 34, color: C.white, textShadow: SHADOW, whiteSpace: "nowrap" }}>{name}</div>
      <div style={{ textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 14, letterSpacing: 2, color: "rgba(255,255,255,0.7)", textShadow: SHADOW, whiteSpace: "nowrap" }}>{photo ? credit : "ILLUSTRATION"}</div>
    </div>
  );
};

// A graphic placed on footage: a ring around a point with a label line.
export const Callout: React.FC<{ x: number; y: number; r?: number; text: string; side?: 1 | -1 }> = ({ x, y, r = 90, text, side = 1 }) => {
  const { f } = useShot();
  const p = ease(f / 10);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <circle cx={x} cy={y} r={r * (1.3 - 0.3 * p)} fill="none" stroke={C.accent} strokeWidth={5} opacity={p} strokeDasharray={`${p * 2 * Math.PI * r} 9999`} />
        <line x1={x + side * r * 0.8} y1={y - r * 0.6} x2={x + side * (r + 150) * p} y2={y - r - 80 * p} stroke={C.accent} strokeWidth={4} opacity={p} />
      </svg>
      <div style={{ position: "absolute", left: side > 0 ? x + r + 160 : undefined, right: side < 0 ? 1920 - (x - r - 160) : undefined, top: y - r - 120, fontFamily: FONT, fontWeight: 800, fontSize: 46, color: C.accent, textShadow: SHADOW, opacity: pop(f, 6) }}>{text}</div>
    </AbsoluteFill>
  );
};
