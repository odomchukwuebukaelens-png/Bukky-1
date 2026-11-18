import React from "react";
import { AbsoluteFill } from "remotion";
import { Person } from "../kit/devices";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { River } from "./common";

const line: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 800,
  lineHeight: 0.95,
  letterSpacing: 2,
  textShadow: "0 10px 40px rgba(0,0,0,0.95), 0 0 8px rgba(0,0,0,0.95)",
};

// Designed at 1920x1080 and scaled down to 1280x720 for upload.
export const CrocThumbnail: React.FC = () => (
  <AbsoluteFill>
    <River ex={1300} ey={700} es={3.6} glow={1} dusk={0.15} />
    <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
      <ellipse cx={330} cy={905} rx={150} ry={22} fill="none" stroke="#f0c98a" strokeWidth={5} opacity={0.6} />
      <ellipse cx={330} cy={905} rx={230} ry={36} fill="none" stroke="#f0c98a" strokeWidth={4} opacity={0.35} />
    </svg>
    <Person x={330} y={900} scale={2.1} color="#0d0f0a" />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 62% 62%, transparent 45%, rgba(0,0,0,0.7) 100%)" }} />
    <div style={{ position: "absolute", left: 70, top: 50 }}>
      <div style={{ ...line, fontSize: 250, color: C.white }}>IT SAW</div>
      <div style={{ ...line, fontSize: 250, color: C.accent, marginTop: 8 }}>YOU FIRST</div>
    </div>
  </AbsoluteFill>
);
