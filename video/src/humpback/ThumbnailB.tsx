import React from "react";
import { AbsoluteFill, random } from "remotion";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";

// Thumbnail B: the proven formula (black field, a detailed monochrome animal, a tiny diver with a torch,
// an arrow, a short second-person line), drawn with our own artwork and our yellow accent.
// Designed at 1920x1080, exported at 1280x720.
const text: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 800,
  lineHeight: 0.95,
  letterSpacing: 1,
  textShadow: "0 8px 30px rgba(0,0,0,0.9)",
};

const UPPER = "M 760 520 C 900 430 1200 330 1500 290 C 1700 265 1850 258 1920 262 L 1920 560 C 1700 520 1300 500 1000 520 C 900 526 820 532 760 520 Z";
const INSIDE = "M 1000 520 C 1300 500 1700 520 1920 560 L 1920 770 C 1600 708 1200 655 860 640 C 840 600 900 540 1000 520 Z";
const LOWER = "M 790 612 C 900 640 1300 664 1920 770 L 1920 1080 L 1120 1080 C 960 900 840 760 790 612 Z";

export const HumpbackThumbnailB: React.FC<{ lead?: string; accent?: string; size?: number }> = ({ lead = "ТИ В ЙОГО ", accent = "ПАЩІ..", size = 150 }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 70% 55%, #161616 0%, #050505 60%, #000 100%)" }}>
    <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
      <defs>
        <linearGradient id="up" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#d9d9d9" />
          <stop offset="0.45" stopColor="#8a8a8a" />
          <stop offset="1" stopColor="#2a2a2a" />
        </linearGradient>
        <linearGradient id="lo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f2f2f2" />
          <stop offset="0.5" stopColor="#b5b5b5" />
          <stop offset="1" stopColor="#3a3a3a" />
        </linearGradient>
        <pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)">
          <line x1="0" y1="0" x2="0" y2="9" stroke="#000" strokeWidth="2.2" />
        </pattern>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.1" />
          <feComposite in2="SourceGraphic" operator="in" />
        </filter>
        <clipPath id="body">
          <path d={UPPER} />
          <path d={LOWER} />
        </clipPath>
      </defs>
      {/* torch beam from the diver into the mouth */}
      <path d="M 420 742 L 1060 540 L 1120 760 Z" fill="rgba(255,255,255,0.10)" />
      <path d="M 420 742 L 1000 600 L 1030 700 Z" fill="rgba(255,255,255,0.10)" />
      {/* the head */}
      <path d={INSIDE} fill="#0d0405" />
      {Array.from({ length: 46 }, (_, i) => {
        const x = 1010 + i * 20;
        const y = 518 - Math.sin(i / 14) * 8 + i * 0.9;
        return <line key={i} x1={x} y1={y} x2={x - 6 + random(`bl${i}`) * 6} y2={y + 70 + random(`bm${i}`) * 50} stroke="#6b6152" strokeWidth={5} opacity={0.9} />;
      })}
      <path d={UPPER} fill="url(#up)" />
      <path d={LOWER} fill="url(#lo)" />
      {/* engraving: hatching and grain over the shading */}
      <g clipPath="url(#body)">
        <rect x={700} y={200} width={1300} height={900} fill="url(#hatch)" opacity={0.28} />
        <rect x={700} y={200} width={1300} height={900} fill="#000" filter="url(#grain)" opacity={0.35} />
        {Array.from({ length: 14 }, (_, i) => (
          <path key={i} d={`M ${830 + i * 22} ${650 + i * 18} C ${1150 + i * 10} ${700 + i * 20} ${1500} ${760 + i * 22} ${1920} ${800 + i * 24}`} stroke="#1a1a1a" strokeWidth={4} fill="none" opacity={0.75} />
        ))}
        {Array.from({ length: 40 }, (_, i) => (
          <circle key={i} cx={1250 + random(`sc${i}`) * 650} cy={330 + random(`sd${i}`) * 160} r={2 + random(`se${i}`) * 4} fill="#111" opacity={0.6} />
        ))}
      </g>
      {/* knobbly bumps along the top of the head */}
      {Array.from({ length: 13 }, (_, i) => {
        const x = 800 + i * 62;
        const y = 505 - i * 15 + (i > 7 ? (i - 7) * 6 : 0);
        return (
          <g key={i}>
            <circle cx={x} cy={y} r={13} fill="#e6e6e6" />
            <circle cx={x + 3} cy={y + 3} r={13} fill="none" stroke="#222" strokeWidth={3} />
          </g>
        );
      })}
      <path d={UPPER} fill="none" stroke="#000" strokeWidth={5} />
      <path d={LOWER} fill="none" stroke="#000" strokeWidth={5} />
      {/* the diver, tiny, torch on */}
      <g transform="translate(380 760) rotate(-12) scale(0.55)">
        <rect x={-120} y={-70} width={120} height={34} rx={16} fill="#9a9a9a" />
        <rect x={-150} y={-40} width={190} height={56} rx={28} fill="#e8e8e8" stroke="#111" strokeWidth={5} />
        <circle cx={70} cy={-14} r={34} fill="#e8e8e8" stroke="#111" strokeWidth={5} />
        <rect x={-300} y={-28} width={160} height={24} rx={12} fill="#e8e8e8" stroke="#111" strokeWidth={4} />
        <rect x={-300} y={4} width={160} height={24} rx={12} fill="#e8e8e8" stroke="#111" strokeWidth={4} />
        <path d="M -300 -40 L -380 -70 L -380 30 L -300 0 Z" fill="#cfcfcf" stroke="#111" strokeWidth={4} />
        <rect x={60} y={10} width={60} height={22} rx={8} fill="#fff" />
      </g>
      {/* arrow to the diver */}
      <path d="M 470 470 C 380 560 360 640 396 712" stroke="#e3231b" strokeWidth={14} fill="none" strokeLinecap="round" />
      <path d="M 360 690 L 400 735 L 430 680" stroke="#e3231b" strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
    <div style={{ position: "absolute", left: 60, top: 50 }}>
      <span style={{ ...text, fontSize: size, color: "#fff" }}>{lead}</span>
      <span style={{ ...text, fontSize: size, color: C.accent }}>{accent}</span>
    </div>
  </AbsoluteFill>
);
