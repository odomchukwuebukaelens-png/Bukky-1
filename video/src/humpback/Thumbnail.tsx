import React from "react";
import { AbsoluteFill, random } from "remotion";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";

const line: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 800,
  lineHeight: 0.95,
  letterSpacing: 2,
  textShadow: "0 10px 40px rgba(0,0,0,0.95), 0 0 8px rgba(0,0,0,0.95)",
};

// Designed at 1920x1080 and scaled down to 1280x720 for upload.
// The moment the mouth closes: a humpback's head out of the water, a yellow kayak half inside.
export const HumpbackThumbnail: React.FC = () => (
  <AbsoluteFill style={{ background: "linear-gradient(#6f7c87 0%, #a9b4bc 55%, #c4cbd0 62%)" }}>
    <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
      <path d={`M 0 640 ${Array.from({ length: 20 }, (_, i) => `L ${i * 105} ${640 - 60 - random(`tm${i}`) * 170}`).join(" ")} L 1920 640 Z`} fill="#56687a" />
      <rect x={0} y={640} width={1920} height={440} fill="#34495a" />
      {Array.from({ length: 40 }, (_, i) => <rect key={i} x={random(`tx${i}`) * 1920} y={650 + random(`ty${i}`) * 420} width={80 + random(`tw${i}`) * 200} height={5} fill="#b8cad4" opacity={0.18} />)}
      {/* upper jaw, dark, with the knobbly bumps */}
      <path d="M 860 700 C 900 430 1140 220 1460 190 C 1700 170 1880 220 1920 260 L 1920 430 C 1700 440 1350 470 1080 560 C 980 600 900 650 860 700 Z" fill="#1f2e3a" />
      {Array.from({ length: 9 }, (_, i) => <circle key={i} cx={1080 + i * 90} cy={300 - Math.sin(i / 2.8) * 70 + i * 4} r={16} fill="#3a4e60" />)}
      {/* inside the mouth */}
      <path d="M 1080 560 C 1350 470 1700 440 1920 430 L 1920 600 C 1650 600 1350 620 1100 660 Z" fill="#5a1f28" />
      {Array.from({ length: 34 }, (_, i) => <line key={i} x1={1100 + i * 24} y1={556 - i * 3.6} x2={1104 + i * 24} y2={610 - i * 2.4} stroke="#c9a46a" strokeWidth={7} />)}
      {/* lower jaw and pleated throat */}
      <path d="M 860 720 C 920 680 1000 660 1100 660 C 1350 620 1650 600 1920 600 L 1920 800 L 860 800 Z" fill="#c8d2d8" />
      {Array.from({ length: 6 }, (_, i) => <path key={i} d={`M ${960 + i * 30} ${700 + i * 14} Q ${1400} ${650 + i * 22} ${1920} ${630 + i * 26}`} stroke="#8e9ca5" strokeWidth={5} fill="none" />)}
      <circle cx={1060} cy={500} r={14} fill="#0a0f14" />
      {/* the yellow kayak, caught across the mouth, nose sticking out */}
      <g transform="translate(1330 590) rotate(-8) scale(0.88)">
        <path d="M -420 -34 Q 0 -74 420 -34 Q 330 34 0 40 Q -330 34 -420 -34 Z" fill="#ffcc1a" stroke="#6a4a00" strokeWidth={7} />
        <ellipse cx={-40} cy={-40} rx={70} ry={20} fill="#3a2a00" />
        <line x1={-360} y1={-160} x2={200} y2={60} stroke="#1a1a1a" strokeWidth={14} />
        <ellipse cx={-380} cy={-168} rx={50} ry={20} fill="#1a1a1a" transform="rotate(22 -380 -168)" />
      </g>
      {/* spray at the waterline */}
      {Array.from({ length: 30 }, (_, i) => <circle key={i} cx={820 + random(`sx${i}`) * 1100} cy={760 - random(`sy${i}`) * 140} r={6 + random(`sr${i}`) * 14} fill="#eef6f8" opacity={0.8} />)}
      {Array.from({ length: 14 }, (_, i) => <circle key={`u${i}`} cx={1000 + random(`ux${i}`) * 900} cy={140 + random(`uy${i}`) * 120} r={6 + random(`ur${i}`) * 10} fill="#eef6f8" opacity={0.7} />)}
      <path d="M 820 780 Q 1400 730 1920 790 L 1920 830 Q 1400 770 820 820 Z" fill="#e6f2f6" opacity={0.9} />
    </svg>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 66% 45%, transparent 40%, rgba(0,0,0,0.65) 100%)" }} />
    <div style={{ position: "absolute", left: 70, top: 60 }}>
      <div style={{ ...line, fontSize: 210, color: C.white }}>ВІН</div>
      <div style={{ ...line, fontSize: 210, color: C.white, marginTop: 6 }}>ЗАКРИВ</div>
      <div style={{ ...line, fontSize: 250, color: C.accent, marginTop: 6 }}>ПАЩУ</div>
    </div>
  </AbsoluteFill>
);
