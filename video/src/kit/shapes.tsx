import React from "react";
import { random } from "remotion";
import { C } from "./theme";

const mix = (a: string, b: string, t: number) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * Math.max(0, Math.min(1, t))));
  return `#${c.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
};
export { mix };

type Reach = { arm: number; tx: number; ty: number; p: number };

// One arm as a chain of shrinking circles, so it tapers and bends organically.
const armPoints = (
  k: number,
  frame: number,
  length: number,
  spread: number,
  curl: number,
  reach?: Reach,
) => {
  const n = 26;
  const pts: { x: number; y: number; r: number; a: number }[] = [];
  if (reach && reach.p > 0) {
    const ex = reach.tx * reach.p;
    const ey = reach.ty * reach.p;
    const len = Math.hypot(ex, ey) || 1;
    const nx = -ey / len;
    const ny = ex / len;
    for (let i = 0; i <= n; i++) {
      const u = i / n;
      const wob = Math.sin(u * 5 + frame * 0.06) * 26 * Math.sin(u * Math.PI) * (1.15 - reach.p * 0.6);
      pts.push({ x: ex * u + nx * wob, y: ey * u + ny * wob, r: 30 * (1 - u * 0.82), a: Math.atan2(ey, ex) });
    }
    return pts;
  }
  const base = (Math.PI * (90 - spread / 2 + (spread * k) / 7)) / 180;
  const dir = k < 4 ? -1 : 1;
  let x = 0;
  let y = 0;
  const seg = length / n;
  for (let i = 0; i <= n; i++) {
    const u = i / n;
    const a = base + dir * curl * Math.pow(u, 1.4) + Math.sin(frame * 0.045 + i * 0.38 + k * 1.7) * 0.55 * u;
    pts.push({ x, y, r: 30 * (1 - u * 0.82), a });
    x += Math.cos(a) * seg;
    y += Math.sin(a) * seg;
  }
  return pts;
};

export const Octopus: React.FC<{
  x: number;
  y: number;
  scale?: number;
  frame: number;
  mood?: number; // 0 calm rust, 1 dark red, -1 pale
  color?: string;
  length?: number;
  spread?: number;
  curl?: number;
  reach?: Reach;
  rotate?: number;
  squashX?: number;
  squashY?: number;
  eyes?: boolean;
  opacity?: number;
  nerves?: number; // 0..1, how far glowing nerve cords run down the arms
  brain?: number; // 0..1 glow of the central brain
  underside?: boolean; // view from below: no mantle, beak at the centre
}> = ({
  x,
  y,
  scale = 1,
  frame,
  mood = 0,
  color,
  length = 330,
  spread = 170,
  curl = 0.9,
  reach,
  rotate = 0,
  squashX = 1,
  squashY = 1,
  eyes = true,
  opacity = 1,
  nerves = 0,
  brain = 0,
  underside = false,
}) => {
  const body = color ?? (mood >= 0 ? mix(C.octo, C.octoDark, mood) : mix(C.octo, C.octoPale, -mood));
  const shade = mix(body, "#000000", 0.28);
  const sucker = mix(body, "#ffffff", 0.55);
  const breathe = 1 + Math.sin(frame * 0.07) * 0.035;
  return (
    <svg
      style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }}
      width={1}
      height={1}
    >
      <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${scale * squashX} ${scale * squashY})`}>
        {Array.from({ length: 8 }, (_, k) => {
          const pts = armPoints(k, frame, length * (0.86 + 0.14 * random(`len${k}`)), spread, curl, reach && reach.arm === k ? reach : undefined);
          return (
            <g key={k}>
              {pts.map((p, i) => (
                <circle key={i} cx={p.x} cy={p.y} r={p.r} fill={i % 2 ? body : shade} />
              ))}
              {pts.map((p, i) =>
                i % 2 === 0 && i > 1 ? (
                  <circle
                    key={`s${i}`}
                    cx={p.x - Math.sin(p.a) * p.r * 0.45}
                    cy={p.y + Math.cos(p.a) * p.r * 0.45}
                    r={p.r * 0.34}
                    fill={sucker}
                    opacity={0.75}
                  />
                ) : null,
              )}
              {nerves > 0
                ? pts.map((p, i) =>
                    i / pts.length <= nerves ? <circle key={`n${i}`} cx={p.x} cy={p.y} r={6} fill={C.accent} /> : null,
                  )
                : null}
            </g>
          );
        })}
        {underside ? (
          <g>
            <circle cx={0} cy={0} r={78} fill={shade} />
            <path d="M -34 -8 Q 0 -44 34 -8 Q 10 -4 0 14 Q -10 -4 -34 -8 Z" fill="#141414" />
            <path d="M -28 14 Q 0 2 28 14 Q 0 44 -28 14 Z" fill="#242424" />
          </g>
        ) : (
          <g>
        <ellipse cx={0} cy={-105} rx={92 * breathe} ry={120 * breathe} fill={body} />
        <ellipse cx={-28} cy={-140} rx={34} ry={50} fill={shade} opacity={0.35} />
        <circle cx={0} cy={-8} r={66} fill={body} />
        {[[-40, -150], [30, -175], [48, -110], [-55, -90], [8, -128]].map(([sx, sy], i) => (
          <circle key={i} cx={sx} cy={sy} r={7 + (i % 3) * 3} fill={shade} opacity={0.5} />
        ))}
        {eyes
          ? [-38, 38].map((ex) => (
              <g key={ex}>
                <ellipse cx={ex} cy={-22} rx={19} ry={15} fill="#f3e3b0" />
                <rect x={ex - 14} y={-26} width={28} height={8} rx={4} fill="#111" />
              </g>
            ))
          : null}
        {brain > 0 ? <circle cx={0} cy={-8} r={34} fill={C.accent} opacity={brain} /> : null}
          </g>
        )}
      </g>
    </svg>
  );
};

// A single large arm for close-ups.
export const BigArm: React.FC<{ frame: number; x: number; y: number; length?: number; color?: string; highlight?: number }> = ({
  frame,
  x,
  y,
  length = 1500,
  color = C.octo,
  highlight = -1,
}) => {
  const n = 34;
  const shade = mix(color, "#000000", 0.25);
  const pts = Array.from({ length: n + 1 }, (_, i) => {
    const u = i / n;
    return {
      x: u * length,
      y: Math.sin(u * 3.2 + frame * 0.03) * 70 * u + Math.sin(u * 7 + frame * 0.05) * 14,
      r: 120 * (1 - u * 0.8),
    };
  });
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <g transform={`translate(${x} ${y})`}>
        {pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={p.r} fill={i % 2 ? color : shade} />
        ))}
        {pts.map((p, i) =>
          i > 0 ? (
            <g key={`s${i}`}>
              {[-0.38, 0.38].map((o, j) => {
                const idx = i * 2 + j;
                const lit = idx <= highlight;
                return (
                  <g key={j}>
                    <circle cx={p.x + o * p.r * 0.2} cy={p.y + p.r * (0.42 + j * 0.0) + (j ? p.r * 0.38 : 0)} r={p.r * 0.26} fill={lit ? C.accent : "#f0c9b6"} />
                    <circle cx={p.x + o * p.r * 0.2} cy={p.y + p.r * 0.42 + (j ? p.r * 0.38 : 0)} r={p.r * 0.11} fill={shade} />
                  </g>
                );
              })}
            </g>
          ) : null,
        )}
      </g>
    </svg>
  );
};

export const Diver: React.FC<{ x: number; y: number; scale?: number; frame: number; flip?: boolean; torch?: boolean; rotate?: number }> = ({
  x,
  y,
  scale = 1,
  frame,
  flip = false,
  torch = true,
  rotate = 0,
}) => {
  const bob = Math.sin(frame * 0.05) * 8;
  const kick = Math.sin(frame * 0.12) * 12;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <g transform={`translate(${x} ${y + bob}) rotate(${rotate}) scale(${flip ? -scale : scale} ${scale})`}>
        {torch ? <polygon points="150,10 900,-170 900,210" fill="#fff6c9" opacity={0.1} /> : null}
        {/* fins and legs */}
        <g transform={`rotate(${kick} -150 20)`}>
          <rect x={-290} y={6} width={150} height={26} rx={13} fill={C.diver} />
          <polygon points="-290,0 -380,-22 -380,58 -290,38" fill="#27414d" />
        </g>
        <g transform={`rotate(${-kick} -150 30)`}>
          <rect x={-285} y={30} width={150} height={26} rx={13} fill="#14212a" />
          <polygon points="-285,24 -375,6 -375,84 -285,62" fill="#1f3640" />
        </g>
        {/* tank and torso */}
        <rect x={-150} y={-52} width={170} height={40} rx={20} fill="#8a959b" />
        <rect x={-160} y={-18} width={230} height={70} rx={35} fill={C.diver} />
        {/* arm reaching forward */}
        <rect x={40} y={10} width={120} height={22} rx={11} fill={C.diver} />
        <circle cx={166} cy={21} r={16} fill="#2c4551" />
        {/* head and mask */}
        <circle cx={92} cy={-22} r={40} fill="#22343d" />
        <rect x={92} y={-44} width={44} height={34} rx={8} fill={C.cyan} opacity={0.85} />
        <rect x={98} y={-6} width={34} height={14} rx={6} fill="#555f66" />
        <path d="M110 2 Q 60 40 -40 -30" stroke="#555f66" strokeWidth={7} fill="none" />
        {/* bubbles */}
        {Array.from({ length: 6 }, (_, i) => {
          const t = ((frame * 1.6 + i * 37) % 220) / 220;
          return (
            <circle
              key={i}
              cx={124 + Math.sin(t * 9 + i) * 14}
              cy={-30 - t * 330}
              r={4 + (i % 3) * 3}
              fill="none"
              stroke="#cfe9f2"
              strokeWidth={2.5}
              opacity={0.6 * (1 - t)}
            />
          );
        })}
      </g>
    </svg>
  );
};

export const Crab: React.FC<{ x: number; y: number; scale?: number; frame: number; color?: string; opacity?: number }> = ({
  x,
  y,
  scale = 1,
  frame,
  color = "#d8743a",
  opacity = 1,
}) => {
  const w = Math.sin(frame * 0.3) * 6;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
      <g transform={`translate(${x} ${y}) scale(${scale})`}>
        {[-1, 1].map((s) => (
          <g key={s}>
            {[0, 1, 2].map((i) => (
              <path key={i} d={`M ${s * 40} ${i * 8} Q ${s * (75 + i * 6)} ${-10 + i * 14 + w * s} ${s * (88 + i * 4)} ${26 + i * 8}`} stroke={color} strokeWidth={7} fill="none" strokeLinecap="round" />
            ))}
            <path d={`M ${s * 36} -14 Q ${s * 70} -50 ${s * 78} -62`} stroke={color} strokeWidth={9} fill="none" strokeLinecap="round" />
            <ellipse cx={s * 84} cy={-70} rx={17} ry={11} fill={color} transform={`rotate(${s * (-30 + w)} ${s * 84} -70)`} />
          </g>
        ))}
        <ellipse cx={0} cy={0} rx={52} ry={32} fill={color} />
        <circle cx={-14} cy={-30} r={5} fill="#111" />
        <circle cx={14} cy={-30} r={5} fill="#111" />
      </g>
    </svg>
  );
};

export const ShellPile: React.FC<{ x: number; y: number; scale?: number; n?: number }> = ({ x, y, scale = 1, n = 14 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) scale(${scale})`}>
      {Array.from({ length: n }, (_, i) => {
        const px = (random(`sx${i}`) - 0.5) * 220;
        const py = -random(`sy${i}`) * 60 * (1 - Math.abs(px) / 130);
        return (
          <ellipse
            key={i}
            cx={px}
            cy={py}
            rx={20 + random(`sr${i}`) * 14}
            ry={11 + random(`sq${i}`) * 6}
            fill={i % 3 ? "#cdb9a2" : "#a98d77"}
            transform={`rotate(${random(`sa${i}`) * 80 - 40} ${px} ${py})`}
          />
        );
      })}
    </g>
  </svg>
);

// Rock mass with a rough edge. `side` picks which half of the frame it fills.
export const RockWall: React.FC<{ x: number; width: number; side?: "left" | "right"; color?: string; seed?: string }> = ({
  x,
  width,
  side = "right",
  color = C.rock,
  seed = "r",
}) => {
  const steps = 14;
  const edge = Array.from({ length: steps + 1 }, (_, i) => {
    const y = (i / steps) * 1080;
    const jx = (random(`${seed}${i}`) - 0.5) * 90;
    return `${side === "right" ? x + jx : x + width + jx},${y}`;
  });
  const far = side === "right" ? x + width + 200 : x - 200;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <polygon points={`${edge.join(" ")} ${far},1080 ${far},0`} fill={color} />
      {Array.from({ length: 10 }, (_, i) => (
        <ellipse
          key={i}
          cx={(side === "right" ? x + 120 : x + width - 120) + (side === "right" ? 1 : -1) * random(`${seed}c${i}`) * (width - 150)}
          cy={random(`${seed}d${i}`) * 1080}
          rx={40 + random(`${seed}e${i}`) * 70}
          ry={20 + random(`${seed}f${i}`) * 30}
          fill={C.rockLight}
          opacity={0.45}
        />
      ))}
    </svg>
  );
};

export const Seabed: React.FC<{ y?: number; color?: string }> = ({ y = 900, color = C.rock }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <path d={`M -50 ${y} Q 300 ${y - 50} 700 ${y - 10} T 1400 ${y - 20} T 2000 ${y - 5} L 2000 1200 L -50 1200 Z`} fill={color} />
  </svg>
);

export const Seal: React.FC<{ x: number; y: number; scale?: number; rotate?: number; flip?: boolean }> = ({ x, y, scale = 1, rotate = 0, flip }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${flip ? -scale : scale} ${scale})`}>
      <path d="M -260 10 C -200 -70 20 -95 170 -60 C 240 -45 280 -10 285 15 C 280 45 230 62 170 60 C 20 70 -150 60 -260 10 Z" fill="#6f7b82" />
      <path d="M -250 12 L -350 -40 L -320 15 L -355 62 Z" fill="#5c676d" />
      <path d="M 20 50 L -30 120 L 70 70 Z" fill="#5c676d" />
      <circle cx={215} cy={-12} r={9} fill="#0c1114" />
      <circle cx={282} cy={14} r={7} fill="#0c1114" />
      {[0, 1, 2].map((i) => (
        <line key={i} x1={262} y1={22 + i * 5} x2={310} y2={30 + i * 12} stroke="#cfd6da" strokeWidth={2} />
      ))}
    </g>
  </svg>
);

export const Shark: React.FC<{ x: number; y: number; scale?: number; flip?: boolean; frame: number; opacity?: number; rotate?: number }> = ({
  x,
  y,
  scale = 1,
  flip,
  frame,
  opacity = 1,
  rotate = 0,
}) => {
  const sway = Math.sin(frame * 0.15) * 8;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
      <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${flip ? -scale : scale} ${scale})`}>
        <path d="M -200 0 C -120 -45 60 -50 200 -8 C 220 -2 220 8 200 12 C 60 45 -120 35 -200 0 Z" fill="#7f8b92" />
        <path d={`M -195 0 L -270 ${-55 + sway} L -240 0 L -265 ${40 + sway} Z`} fill="#6b767c" />
        <path d="M -20 -40 L 10 -95 L 50 -38 Z" fill="#6b767c" />
        <path d="M 40 30 L 20 80 L 90 32 Z" fill="#6b767c" />
        <circle cx={160} cy={-8} r={6} fill="#0c1114" />
      </g>
    </svg>
  );
};

export const Gull: React.FC<{ x: number; y: number; scale?: number; opacity?: number; rotate?: number }> = ({ x, y, scale = 1, opacity = 1, rotate = 0 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${scale})`}>
      <ellipse cx={0} cy={0} rx={60} ry={34} fill="#eef2f4" />
      <path d="M -50 -8 L -110 -22 L -60 14 Z" fill="#9aa5ab" />
      <path d="M -30 -20 Q 10 -50 44 -14 Q 5 -6 -30 -20 Z" fill="#9aa5ab" />
      <circle cx={52} cy={-30} r={24} fill="#eef2f4" />
      <polygon points="72,-34 108,-26 72,-20" fill="#f0b93a" />
      <circle cx={58} cy={-35} r={4} fill="#111" />
      <line x1={-8} y1={30} x2={-8} y2={62} stroke="#f0b93a" strokeWidth={6} />
      <line x1={14} y1={30} x2={14} y2={62} stroke="#f0b93a" strokeWidth={6} />
    </g>
  </svg>
);

export const Person: React.FC<{ x: number; y: number; scale?: number; shirt?: string; item?: "food" | "stick" | null; itemP?: number }> = ({
  x,
  y,
  scale = 1,
  shirt = "#2f7fb8",
  item = null,
  itemP = 1,
}) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <g transform={`translate(${x} ${y}) scale(${scale})`}>
      <rect x={-48} y={150} width={40} height={190} rx={18} fill="#1f2a33" />
      <rect x={8} y={150} width={40} height={190} rx={18} fill="#1f2a33" />
      <rect x={-70} y={-40} width={140} height={220} rx={46} fill={shirt} />
      <circle cx={0} cy={-98} r={52} fill="#d9a67e" />
      <rect x={52} y={-10} width={130 * itemP + 30} height={30} rx={15} fill={shirt} transform="rotate(18 52 5)" />
      {item === "food" ? <ellipse cx={190 * itemP + 30} cy={64 * itemP + 10} rx={28} ry={16} fill="#d8743a" /> : null}
      {item === "stick" ? (
        <g transform={`translate(${170 * itemP + 20} ${56 * itemP + 8}) rotate(28)`}>
          <rect x={0} y={-5} width={170} height={10} rx={5} fill="#8b6a45" />
          {[0, 1, 2, 3, 4].map((i) => (
            <line key={i} x1={130 + i * 9} y1={-18} x2={130 + i * 9} y2={18} stroke="#d8c7a8" strokeWidth={3} />
          ))}
        </g>
      ) : null}
    </g>
  </svg>
);

export const Heart: React.FC<{ x: number; y: number; scale?: number; color?: string }> = ({ x, y, scale = 1, color = C.red }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <path
      transform={`translate(${x} ${y}) scale(${scale})`}
      d="M 0 30 C -60 -10 -50 -70 -5 -50 C 0 -48 0 -46 0 -40 C 0 -46 0 -48 5 -50 C 50 -70 60 -10 0 30 Z"
      fill={color}
    />
  </svg>
);

// An arm that grows from one point toward another as `p` goes 0 → 1.
export const Tentacle: React.FC<{
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  p: number;
  frame: number;
  thick?: number;
  color?: string;
}> = ({ x0, y0, x1, y1, p, frame, thick = 34, color = C.octo }) => {
  if (p <= 0) return null;
  const n = 30;
  const dx = (x1 - x0) * p;
  const dy = (y1 - y0) * p;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const shade = mix(color, "#000000", 0.28);
  const pts = Array.from({ length: n + 1 }, (_, i) => {
    const u = i / n;
    const wob = Math.sin(u * 6 + frame * 0.07) * 34 * Math.sin(u * Math.PI) * (1.2 - p * 0.7);
    return { x: x0 + dx * u + nx * wob, y: y0 + dy * u + ny * wob, r: thick * (1 - u * 0.78) };
  });
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      {pts.map((q, i) => (
        <circle key={i} cx={q.x} cy={q.y} r={q.r} fill={i % 2 ? color : shade} />
      ))}
      {pts.map((q, i) =>
        i % 2 === 0 ? <circle key={`s${i}`} cx={q.x + nx * q.r * 0.4} cy={q.y + ny * q.r * 0.4} r={q.r * 0.32} fill="#f0c9b6" opacity={0.8} /> : null,
      )}
    </svg>
  );
};

export const Svg: React.FC<{ children: React.ReactNode; opacity?: number }> = ({ children, opacity = 1 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
    {children}
  </svg>
);
