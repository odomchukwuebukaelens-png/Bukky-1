import React from "react";
import { AbsoluteFill, random } from "remotion";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";

// Leopard seal thumbnail: the proven formula (black field, a detailed monochrome animal, a tiny diver,
// an arrow, a short second-person line) drawn with our own artwork, our ice ceiling and our yellow accent.
// The seal rises from below toward the diver with its jaws open. Designed at 1920x1080.
const text: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 800,
  lineHeight: 0.95,
  letterSpacing: 1,
  textShadow: "0 8px 30px rgba(0,0,0,0.9)",
};

// Head in local coordinates, snout at the left (0,0), neck running off to the right.
const SKULL = "M -8 4 C 10 -40 70 -78 170 -100 C 300 -128 470 -134 640 -122 C 820 -110 1000 -80 1200 -40 L 1200 120 C 1000 100 800 80 640 70 C 560 66 480 60 430 52 C 300 64 140 52 10 24 Z";
const JAW = "M 430 52 C 480 60 560 66 640 70 C 800 80 1000 100 1200 120 L 1200 420 C 900 420 600 380 380 330 C 250 300 130 268 60 236 C 40 226 36 212 52 204 C 160 190 300 130 430 52 Z";
const MOUTH = "M 14 24 C 140 52 300 64 430 52 C 300 130 160 190 52 204 C 30 150 14 80 14 24 Z";

const Teeth: React.FC<{ pts: [number, number, number, number][] }> = ({ pts }) => (
  <>
    {pts.map(([x, y, h, w], i) => (
      <path key={i} d={`M ${x - w} ${y} L ${x} ${y + h} L ${x + w} ${y} Z`} fill="#efeae0" stroke="#111" strokeWidth={3} strokeLinejoin="round" />
    ))}
  </>
);

export const LeopardThumbnail: React.FC<{ lead?: string; accent?: string; size?: number }> = ({ lead = "IT CHOSE ", accent = "YOU..", size = 160 }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 62% 62%, #171a1c 0%, #060707 58%, #000 100%)" }}>
    <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
      <defs>
        <linearGradient id="lt-up" x1="0" y1="0" x2="0.6" y2="1">
          <stop offset="0" stopColor="#dcdcdc" />
          <stop offset="0.5" stopColor="#8d8d8d" />
          <stop offset="1" stopColor="#2b2b2b" />
        </linearGradient>
        <linearGradient id="lt-lo" x1="0" y1="0" x2="0.5" y2="1">
          <stop offset="0" stopColor="#f4f4f4" />
          <stop offset="0.55" stopColor="#b9b9b9" />
          <stop offset="1" stopColor="#404040" />
        </linearGradient>
        <linearGradient id="lt-ray" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="rgba(220,240,255,0.16)" />
          <stop offset="1" stopColor="rgba(220,240,255,0)" />
        </linearGradient>
        <pattern id="lt-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)">
          <line x1="0" y1="0" x2="0" y2="9" stroke="#000" strokeWidth="2.2" />
        </pattern>
        <filter id="lt-grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.1" />
          <feComposite in2="SourceGraphic" operator="in" />
        </filter>
        <clipPath id="lt-skull"><path d={SKULL} /></clipPath>
        <clipPath id="lt-jaw"><path d={JAW} /></clipPath>
      </defs>

      {/* light falling through a hole in the ice */}
      {[0, 1, 2].map((i) => (
        <path key={i} d={`M ${1180 + i * 120} 0 L ${1260 + i * 120} 0 L ${900 + i * 260} 1080 L ${760 + i * 230} 1080 Z`} fill="url(#lt-ray)" />
      ))}
      {/* the ice ceiling, engraved */}
      <path d="M 0 0 L 1920 0 L 1920 70 C 1700 96 1560 60 1420 86 L 1380 40 L 1150 40 L 1110 92 C 900 70 700 110 520 84 C 340 60 160 98 0 80 Z" fill="#6f7a80" />
      <path d="M 0 80 C 160 98 340 60 520 84 C 700 110 900 70 1110 92 M 1420 86 C 1560 60 1700 96 1920 70" stroke="#111" strokeWidth={5} fill="none" />
      <rect x={1150} y={0} width={230} height={40} fill="#e8f4ff" opacity={0.9} />
      {Array.from({ length: 70 }, (_, i) => (
        <line key={i} x1={i * 28} y1={10} x2={i * 28 - 14} y2={60 + random(`ic${i}`) * 20} stroke="#3a4247" strokeWidth={2} opacity={0.7} />
      ))}

      {/* drifting particles */}
      {Array.from({ length: 60 }, (_, i) => (
        <circle key={i} cx={random(`px${i}`) * 1920} cy={120 + random(`py${i}`) * 960} r={1 + random(`pr${i}`) * 2.5} fill="#cfd6da" opacity={0.25 + random(`po${i}`) * 0.3} />
      ))}

      {/* the seal: rising from the lower right toward the diver, jaws wide */}
      <g transform="translate(760 640) rotate(-24) scale(1.05)">
        <path d={MOUTH} fill="#1a0607" />
        <path d="M 60 190 C 150 170 280 120 400 62" stroke="#5a1418" strokeWidth={26} fill="none" opacity={0.8} />
        {/* cheek teeth (three-pointed) and big canines */}
        <Teeth pts={[[44, 22, 58, 12], [78, 30, 46, 10], [140, 40, 26, 9], [190, 46, 24, 9], [240, 50, 22, 9], [290, 53, 20, 8], [340, 54, 18, 8]]} />
        <Teeth pts={[[80, 200, -54, 12], [118, 192, -40, 10], [170, 176, -24, 9], [220, 158, -22, 9], [270, 138, -20, 8], [320, 114, -18, 8], [370, 88, -16, 7]]} />
        <path d={SKULL} fill="url(#lt-up)" />
        <path d={JAW} fill="url(#lt-lo)" />
        <g clipPath="url(#lt-skull)">
          <rect x={-50} y={-200} width={1300} height={400} fill="url(#lt-hatch)" opacity={0.3} />
          <rect x={-50} y={-200} width={1300} height={400} fill="#000" filter="url(#lt-grain)" opacity={0.35} />
          {Array.from({ length: 10 }, (_, i) => (
            <path key={i} d={`M ${120 + i * 40} ${-80 + i * 6} C ${400 + i * 30} ${-110 + i * 10} ${800} ${-90 + i * 12} ${1200} ${-40 + i * 14}`} stroke="#1a1a1a" strokeWidth={3} fill="none" opacity={0.55} />
          ))}
        </g>
        <g clipPath="url(#lt-jaw)">
          <rect x={-50} y={0} width={1300} height={450} fill="url(#lt-hatch)" opacity={0.2} />
          <rect x={-50} y={0} width={1300} height={450} fill="#000" filter="url(#lt-grain)" opacity={0.3} />
          {/* leopard spots on the throat */}
          {Array.from({ length: 46 }, (_, i) => (
            <ellipse key={i} cx={260 + random(`ts${i}`) * 900} cy={150 + random(`tt${i}`) * 260} rx={8 + random(`tr${i}`) * 14} ry={5 + random(`tq${i}`) * 8} fill="#1e1e1e" opacity={0.7} transform={`rotate(${random(`ta${i}`) * 40 - 20} ${260 + random(`ts${i}`) * 900} ${150 + random(`tt${i}`) * 260})`} />
          ))}
          {Array.from({ length: 9 }, (_, i) => (
            <path key={i} d={`M ${120 + i * 50} ${250 + i * 14} C ${500} ${330 + i * 12} ${900} ${360 + i * 10} ${1200} ${380 + i * 8}`} stroke="#2a2a2a" strokeWidth={3} fill="none" opacity={0.45} />
          ))}
        </g>
        <path d={SKULL} fill="none" stroke="#000" strokeWidth={5} />
        <path d={JAW} fill="none" stroke="#000" strokeWidth={5} />
        {/* nostrils, brow and the cold eye */}
        <ellipse cx={46} cy={-30} rx={16} ry={7} fill="#111" transform="rotate(-24 46 -30)" />
        <path d="M 250 -92 C 300 -110 360 -108 400 -90" stroke="#111" strokeWidth={6} fill="none" />
        <ellipse cx={330} cy={-60} rx={34} ry={26} fill="#050505" stroke="#bbb" strokeWidth={3} />
        <circle cx={320} cy={-68} r={8} fill="#fff" />
        {/* whiskers */}
        {[0, 1, 2, 3].map((i) => (
          <path key={i} d={`M ${90 + i * 14} ${10 + i * 6} C ${60 + i * 6} ${70 + i * 10} ${10} ${110 + i * 12} ${-40 - i * 10} ${130 + i * 14}`} stroke="#ddd" strokeWidth={2} fill="none" opacity={0.6} />
        ))}
      </g>

      {/* the diver, tiny, looking down at it */}
      <g transform="translate(380 640) rotate(28) scale(0.55)">
        <rect x={-120} y={-70} width={120} height={34} rx={16} fill="#9a9a9a" />
        <rect x={-150} y={-40} width={190} height={56} rx={28} fill="#e8e8e8" stroke="#111" strokeWidth={5} />
        <circle cx={70} cy={-14} r={34} fill="#e8e8e8" stroke="#111" strokeWidth={5} />
        <rect x={-300} y={-28} width={160} height={24} rx={12} fill="#e8e8e8" stroke="#111" strokeWidth={4} />
        <rect x={-300} y={4} width={160} height={24} rx={12} fill="#e8e8e8" stroke="#111" strokeWidth={4} />
        <path d="M -300 -40 L -380 -70 L -380 30 L -300 0 Z" fill="#cfcfcf" stroke="#111" strokeWidth={4} />
        <rect x={60} y={10} width={60} height={22} rx={8} fill="#fff" />
      </g>
      {/* bubbles from the diver */}
      {[0, 1, 2, 3, 4].map((i) => (
        <circle key={i} cx={430 + (i % 2) * 14} cy={600 - i * 52} r={6 + i * 2} fill="none" stroke="#dfe6ea" strokeWidth={3} opacity={0.7} />
      ))}

      {/* arrow to the diver, our yellow */}
      <path d="M 120 380 C 130 470 180 530 250 560" stroke={C.accent} strokeWidth={14} fill="none" strokeLinecap="round" />
      <path d="M 200 586 L 262 566 L 230 510" stroke={C.accent} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
    <div style={{ position: "absolute", left: 60, top: 120 }}>
      <span style={{ ...text, fontSize: size, color: "#fff" }}>{lead}</span>
      <span style={{ ...text, fontSize: size, color: C.accent }}>{accent}</span>
    </div>
  </AbsoluteFill>
);
